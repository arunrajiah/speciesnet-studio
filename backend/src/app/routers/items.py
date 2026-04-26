import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.db import get_session
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus
from app.repositories.reviews import upsert_review

router = APIRouter(prefix="/api", tags=["items"])

_IMAGES_DIR = Path(os.environ.get("IMAGES_DIR", "./data/images")).resolve()
_THUMBS_DIR = Path(os.environ.get("THUMBS_DIR", "./data/thumbs")).resolve()


def _image_url(path: str) -> str:
    """Return a URL for a full-res image, preserving subdirectory structure."""
    try:
        rel = Path(path).resolve().relative_to(_IMAGES_DIR)
        return f"/images/{rel.as_posix()}"
    except ValueError:
        return f"/images/{os.path.basename(path)}"


def _thumb_url(path: str) -> str:
    """Return a URL for a thumbnail image."""
    try:
        rel = Path(path).resolve().relative_to(_THUMBS_DIR)
        return f"/thumbs/{rel.as_posix()}"
    except ValueError:
        return f"/thumbs/{os.path.basename(path)}"


# ── list items ────────────────────────────────────────────────────────────────


@router.get("/collections/{collection_id}/items")
def list_items(
    collection_id: int,
    label: str | None = None,
    min_conf: float | None = None,
    max_conf: float | None = None,
    status: str | None = None,
    q: str | None = None,
    session: Session = Depends(get_session),
) -> list[dict[str, object]]:
    """Return items for a collection with optional filters."""
    if min_conf is not None and not (0.0 <= min_conf <= 1.0):
        raise HTTPException(status_code=422, detail="min_conf must be between 0 and 1")
    if max_conf is not None and not (0.0 <= max_conf <= 1.0):
        raise HTTPException(status_code=422, detail="max_conf must be between 0 and 1")
    if min_conf is not None and max_conf is not None and min_conf > max_conf:
        raise HTTPException(status_code=422, detail="min_conf must not exceed max_conf")
    if status is not None:
        valid_statuses = [s.value for s in ReviewStatus]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=422,
                detail=f"status must be one of: {', '.join(valid_statuses)}",
            )

    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())
    if not items:
        return []

    item_ids = [i.id for i in items if i.id is not None]

    # Batch-load all predictions and reviews in two queries instead of 2N.
    all_preds = list(
        session.exec(
            select(Prediction)
            .where(col(Prediction.item_id).in_(item_ids))
            .order_by(Prediction.confidence.desc())  # type: ignore[attr-defined]
        ).all()
    )
    all_reviews = list(
        session.exec(select(ReviewRecord).where(col(ReviewRecord.item_id).in_(item_ids))).all()
    )

    top_pred_by_item: dict[int, Prediction] = {}
    for pred in all_preds:
        if pred.item_id not in top_pred_by_item:
            top_pred_by_item[pred.item_id] = pred

    review_by_item: dict[int, ReviewRecord] = {r.item_id: r for r in all_reviews}

    result: list[dict[str, object]] = []
    for item in items:
        top_pred = top_pred_by_item.get(item.id)  # type: ignore[arg-type]
        review = review_by_item.get(item.id)  # type: ignore[arg-type]
        review_status = review.status if review else ReviewStatus.unreviewed

        top_label = top_pred.label if top_pred else None
        top_confidence = top_pred.confidence if top_pred else None

        if label and top_label != label:
            continue
        if min_conf is not None and (top_confidence is None or top_confidence < min_conf):
            continue
        if max_conf is not None and (top_confidence is None or top_confidence > max_conf):
            continue
        if status and review_status != status:
            continue
        if q and q.lower() not in item.filename.lower():
            continue

        result.append(
            {
                "id": item.id,
                "filename": item.filename,
                "thumbnail_url": _thumb_url(item.thumbnail_path) if item.thumbnail_path else None,
                "top_label": top_label,
                "top_confidence": top_confidence,
                "review_status": review_status,
                "latitude": item.latitude,
                "longitude": item.longitude,
            }
        )

    return result


# ── single item ───────────────────────────────────────────────────────────────


@router.get("/items/{item_id}")
def get_item(item_id: int, session: Session = Depends(get_session)) -> dict[str, object]:
    """Return full detail for a single item."""
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    predictions = list(
        session.exec(
            select(Prediction)
            .where(Prediction.item_id == item_id)
            .order_by(Prediction.confidence.desc())  # type: ignore[attr-defined]
        ).all()
    )

    review = session.exec(select(ReviewRecord).where(ReviewRecord.item_id == item_id)).first()

    return {
        "id": item.id,
        "filename": item.filename,
        "full_image_url": _image_url(item.path),
        "thumbnail_url": _thumb_url(item.thumbnail_path) if item.thumbnail_path else None,
        "captured_at": item.captured_at.isoformat() if item.captured_at else None,
        "latitude": item.latitude,
        "longitude": item.longitude,
        "width": item.width,
        "height": item.height,
        "predictions": [
            {
                "label": p.label,
                "confidence": p.confidence,
                "bbox_json": p.bbox_json,
                "model_version": p.model_version,
            }
            for p in predictions
        ],
        "review": {
            "status": review.status,
            "override_label": review.override_label,
            "reviewer_note": review.reviewer_note,
            "reviewer_name": review.reviewer_name,
        }
        if review
        else None,
    }


# ── labels ────────────────────────────────────────────────────────────────────


@router.get("/collections/{collection_id}/labels")
def list_labels(collection_id: int, session: Session = Depends(get_session)) -> list[str]:
    """Return distinct prediction labels for a collection."""
    labels = list(
        session.exec(
            select(col(Prediction.label))
            .join(Item, col(Prediction.item_id) == col(Item.id))
            .where(col(Item.collection_id) == collection_id)
            .distinct()
        ).all()
    )
    return sorted(set(labels))


# ── batch review ─────────────────────────────────────────────────────────────


@router.post("/items/batch-review")
def batch_review(
    body: dict[str, object],
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Apply the same review decision to multiple items at once.

    Body fields:
    - ``item_ids`` (list[int], required): items to update.
    - ``status`` (str, required): one of the ReviewStatus values.
    - ``override_label`` (str | null, optional).
    - ``reviewer_note`` (str | null, optional).
    - ``reviewer_name`` (str | null, optional): name of the person reviewing.

    Returns ``{"updated": <count>}`` or 404 if any item_id is not found.
    """
    raw_ids = body.get("item_ids", [])
    if not isinstance(raw_ids, list):
        raise HTTPException(status_code=422, detail="item_ids must be a list")
    item_ids: list[int] = []
    for v in raw_ids:
        if not isinstance(v, int):
            raise HTTPException(status_code=422, detail="each item_id must be an integer")
        item_ids.append(v)

    raw_status = body.get("status", "confirmed")
    if not isinstance(raw_status, str):
        raise HTTPException(status_code=422, detail="status must be a string")
    try:
        review_status = ReviewStatus(raw_status)
    except ValueError:
        valid = ", ".join(s.value for s in ReviewStatus)
        raise HTTPException(status_code=422, detail=f"status must be one of: {valid}") from None

    raw_label = body.get("override_label")
    override_label = str(raw_label) if isinstance(raw_label, str) and raw_label else None

    raw_note = body.get("reviewer_note")
    reviewer_note = str(raw_note) if isinstance(raw_note, str) and raw_note else None

    raw_name = body.get("reviewer_name")
    reviewer_name = str(raw_name) if isinstance(raw_name, str) and raw_name else None

    for item_id in item_ids:
        if session.get(Item, item_id) is None:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    updated = 0
    for item_id in item_ids:
        upsert_review(
            session,
            item_id,
            status=review_status,
            override_label=override_label,
            reviewer_note=reviewer_note,
            reviewer_name=reviewer_name,
        )
        updated += 1

    return {"updated": updated}


# ── review ────────────────────────────────────────────────────────────────────


@router.put("/items/{item_id}/review")
def submit_review(
    item_id: int,
    body: dict[str, object],
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Upsert a review record for an item."""
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    raw_status = body.get("status", "confirmed")
    if not isinstance(raw_status, str):
        raise HTTPException(status_code=422, detail="status must be a string")
    status_val = raw_status

    raw_label = body.get("override_label")
    override_label = str(raw_label) if isinstance(raw_label, str) and raw_label else None

    raw_note = body.get("reviewer_note")
    reviewer_note = str(raw_note) if isinstance(raw_note, str) and raw_note else None

    raw_name = body.get("reviewer_name")
    reviewer_name = str(raw_name) if isinstance(raw_name, str) and raw_name else None

    try:
        review_status = ReviewStatus(status_val)
    except ValueError:
        valid = ", ".join(s.value for s in ReviewStatus)
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of: {valid}",
        ) from None

    record = upsert_review(
        session,
        item_id,
        status=review_status,
        override_label=override_label,
        reviewer_note=reviewer_note,
        reviewer_name=reviewer_name,
    )
    return {
        "id": record.id,
        "item_id": record.item_id,
        "status": record.status,
        "override_label": record.override_label,
        "reviewer_note": record.reviewer_note,
        "reviewer_name": record.reviewer_name,
        "updated_at": record.updated_at.isoformat(),
    }
