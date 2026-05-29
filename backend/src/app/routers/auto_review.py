from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlmodel import Session, col, select

from app.db import get_session
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus
from app.repositories.collections import get_collection
from app.repositories.reviews import upsert_review
from app.services.results_parser import parse_predictions_json, persist_predictions

router = APIRouter(prefix="/api", tags=["auto-review"])

# Labels SpeciesNet assigns to non-wildlife frames — kept as a frozenset for O(1) lookup
BLANK_LABELS: frozenset[str] = frozenset({"blank", "human", "vehicle", "no_cv_result"})

# ---------------------------------------------------------------------------
# Feature 1 – Import predictions
# ---------------------------------------------------------------------------


class ImportPredictionsBody(BaseModel):
    predictions_path: str


class ImportPredictionsResponse(BaseModel):
    imported: int
    warnings: list[str]


@router.post(
    "/collections/{collection_id}/import-predictions",
    response_model=ImportPredictionsResponse,
)
def import_predictions(
    collection_id: int,
    body: ImportPredictionsBody,
    session: Session = Depends(get_session),
) -> ImportPredictionsResponse:
    """Parse a SpeciesNet predictions JSON file and persist results for the collection."""
    collection = get_collection(session, collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    warnings: list[str] = []
    try:
        parsed = parse_predictions_json(body.predictions_path)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=422, detail=f"Predictions file not found: {body.predictions_path}"
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422, detail=f"Failed to parse predictions file: {exc}"
        ) from exc

    if not parsed:
        warnings.append("No predictions found in the provided file.")
        return ImportPredictionsResponse(imported=0, warnings=warnings)

    persist_predictions(session, collection_id, parsed)
    return ImportPredictionsResponse(imported=len(parsed), warnings=warnings)


# ---------------------------------------------------------------------------
# Feature 2 – Auto-review by confidence / label
# ---------------------------------------------------------------------------


class AutoReviewBody(BaseModel):
    status: ReviewStatus
    min_confidence: float | None = None
    labels: list[str] | None = None
    only_unreviewed: bool = True
    # When True, approve ALL blank/human/vehicle frames regardless of confidence
    include_blank_labels: bool = False
    reviewer_name: str | None = None

    @field_validator("min_confidence")
    @classmethod
    def validate_min_confidence(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("min_confidence must be between 0.0 and 1.0")
        return v


class AutoReviewPreviewResponse(BaseModel):
    count: int


class AutoReviewResponse(BaseModel):
    reviewed: int


def _top_predictions_by_item(session: Session, collection_id: int) -> dict[int, tuple[str, float]]:
    """Return a mapping of item_id -> (label, confidence) for the highest-confidence
    prediction per item in the given collection.
    """
    from sqlalchemy import func

    max_conf_sub = (
        select(
            col(Prediction.item_id).label("item_id"),
            func.max(Prediction.confidence).label("max_conf"),
        )
        .join(Item, col(Prediction.item_id) == col(Item.id))
        .where(col(Item.collection_id) == collection_id)
        .group_by(col(Prediction.item_id))
        .subquery()
    )

    rows = session.exec(
        select(Prediction.item_id, Prediction.label, Prediction.confidence)
        .join(
            max_conf_sub,
            (col(Prediction.item_id) == max_conf_sub.c.item_id)
            & (col(Prediction.confidence) == max_conf_sub.c.max_conf),
        )
        .distinct()
    ).all()

    result: dict[int, tuple[str, float]] = {}
    for item_id, label, confidence in rows:
        if item_id not in result:
            result[item_id] = (label, confidence)
    return result


def _candidate_item_ids(
    session: Session,
    collection_id: int,
    min_confidence: float | None,
    labels: list[str] | None,
    only_unreviewed: bool,
    include_blank_labels: bool = False,
) -> list[int]:
    """Return item IDs that satisfy all filter criteria.

    When *include_blank_labels* is True, items whose top label is one of the
    BLANK_LABELS set are always included regardless of the confidence threshold.
    This lets callers sweep high-confidence wildlife AND clear all obvious
    blank/human/vehicle frames in a single operation.
    """
    item_ids: list[int] = [
        row
        for row in session.exec(
            select(col(Item.id)).where(col(Item.collection_id) == collection_id)
        ).all()
        if row is not None
    ]

    if not item_ids:
        return []

    top_preds = _top_predictions_by_item(session, collection_id)

    reviewed_item_ids: set[int] = set()
    if only_unreviewed:
        review_rows = session.exec(
            select(col(ReviewRecord.item_id), col(ReviewRecord.status)).where(
                col(ReviewRecord.item_id).in_(item_ids)
            )
        ).all()
        reviewed_item_ids = {
            iid for iid, status in review_rows if status != ReviewStatus.unreviewed
        }

    candidates: list[int] = []
    for item_id in item_ids:
        if only_unreviewed and item_id in reviewed_item_ids:
            continue

        pred = top_preds.get(item_id)
        label = pred[0] if pred else None
        confidence = pred[1] if pred else None
        is_blank = label in BLANK_LABELS if label else False

        # Blank-label items are always included when the flag is set
        if include_blank_labels and is_blank:
            candidates.append(item_id)
            continue

        # Confidence filter
        if min_confidence is not None:
            if confidence is None or confidence < min_confidence:
                continue

        # Label allow-list filter (explicit labels param, independent of blank logic)
        if labels is not None:
            if label is None or label not in labels:
                continue

        candidates.append(item_id)

    return candidates


@router.get(
    "/collections/{collection_id}/auto-review/preview",
    response_model=AutoReviewPreviewResponse,
)
def auto_review_preview(
    collection_id: int,
    min_confidence: float | None = None,
    labels: str | None = None,
    only_unreviewed: bool = True,
    include_blank_labels: bool = False,
    session: Session = Depends(get_session),
) -> AutoReviewPreviewResponse:
    """Return the count of items that would be affected by an auto-review operation."""
    if min_confidence is not None and not (0.0 <= min_confidence <= 1.0):
        raise HTTPException(status_code=422, detail="min_confidence must be between 0.0 and 1.0")

    collection = get_collection(session, collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    parsed_labels: list[str] | None = (
        [lbl.strip() for lbl in labels.split(",") if lbl.strip()] if labels else None
    )

    candidate_ids = _candidate_item_ids(
        session,
        collection_id,
        min_confidence=min_confidence,
        labels=parsed_labels,
        only_unreviewed=only_unreviewed,
        include_blank_labels=include_blank_labels,
    )
    return AutoReviewPreviewResponse(count=len(candidate_ids))


@router.post(
    "/collections/{collection_id}/auto-review",
    response_model=AutoReviewResponse,
)
def auto_review(
    collection_id: int,
    body: AutoReviewBody,
    session: Session = Depends(get_session),
) -> AutoReviewResponse:
    """Apply a review status to all items matching the confidence/label criteria."""
    collection = get_collection(session, collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    candidate_ids = _candidate_item_ids(
        session,
        collection_id,
        min_confidence=body.min_confidence,
        labels=body.labels,
        only_unreviewed=body.only_unreviewed,
        include_blank_labels=body.include_blank_labels,
    )

    for item_id in candidate_ids:
        upsert_review(session, item_id, body.status, reviewer_name=body.reviewer_name)

    return AutoReviewResponse(reviewed=len(candidate_ids))
