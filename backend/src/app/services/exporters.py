import csv
import io
import json
import os

from sqlmodel import Session, select

from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus

# Labels treated as non-wildlife by SpeciesNet
_BLANK_LABELS = frozenset({"blank", "human", "vehicle", "no_cv_result"})


def _build_rows(session: Session, collection_id: int) -> list[dict[str, object]]:
    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())
    if not items:
        return []

    item_ids = [i.id for i in items if i.id is not None]

    # Batch-load all predictions and reviews in two queries instead of 2N.
    all_preds = list(
        session.exec(
            select(Prediction)
            .where(Prediction.item_id.in_(item_ids))  # type: ignore[attr-defined]
            .order_by(Prediction.confidence.desc())  # type: ignore[attr-defined]
        ).all()
    )
    all_reviews = list(
        session.exec(select(ReviewRecord).where(ReviewRecord.item_id.in_(item_ids))).all()  # type: ignore[attr-defined]
    )

    top_pred_by_item: dict[int, Prediction] = {}
    for pred in all_preds:
        if pred.item_id not in top_pred_by_item:
            top_pred_by_item[pred.item_id] = pred

    review_by_item: dict[int, ReviewRecord] = {r.item_id: r for r in all_reviews}

    rows: list[dict[str, object]] = []
    for item in items:
        top_pred = top_pred_by_item.get(item.id)  # type: ignore[arg-type]
        review = review_by_item.get(item.id)  # type: ignore[arg-type]
        rows.append(
            {
                "id": item.id,
                "filename": item.filename,
                "captured_at": item.captured_at.isoformat() if item.captured_at else None,
                "latitude": item.latitude,
                "longitude": item.longitude,
                "top_label": top_pred.label if top_pred else None,
                "top_confidence": top_pred.confidence if top_pred else None,
                "model_version": top_pred.model_version if top_pred else None,
                "review_status": review.status if review else ReviewStatus.unreviewed,
                "override_label": review.override_label if review else None,
                "reviewer_note": review.reviewer_note if review else None,
                "reviewer_name": review.reviewer_name if review else None,
            }
        )

    return rows


def export_csv(session: Session, collection_id: int) -> str:
    rows = _build_rows(session, collection_id)
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def export_json(session: Session, collection_id: int) -> str:
    return json.dumps(_build_rows(session, collection_id), indent=2, default=str)


# Wildlife Insights column order (required fields first, then optional)
_WI_FIELDS = [
    "project_id",
    "subproject_id",
    "camera_id",
    "deployment_id",
    "image_id",
    "image_sequence",
    "filename",
    "timestamp",
    "image_is_blank",
    "human_in_image",
    "number_of_objects",
    "common_name",
    "notes",
    "latitude",
    "longitude",
    "review_status",
    "reviewer_name",
]


def export_wildlife_insights(session: Session, collection_id: int, project_name: str) -> str:
    """Export in a Wildlife Insights-compatible CSV format.

    Columns that require human annotation (age, sex, individual ID, etc.) are left
    blank — reviewers can fill those in after import to WI.
    """
    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())
    if not items:
        return ""

    item_ids = [i.id for i in items if i.id is not None]

    all_preds = list(
        session.exec(
            select(Prediction)
            .where(Prediction.item_id.in_(item_ids))  # type: ignore[attr-defined]
            .order_by(Prediction.confidence.desc())  # type: ignore[attr-defined]
        ).all()
    )
    all_reviews = list(
        session.exec(select(ReviewRecord).where(ReviewRecord.item_id.in_(item_ids))).all()  # type: ignore[attr-defined]
    )

    top_pred_by_item: dict[int, Prediction] = {}
    for pred in all_preds:
        if pred.item_id not in top_pred_by_item:
            top_pred_by_item[pred.item_id] = pred

    review_by_item: dict[int, ReviewRecord] = {r.item_id: r for r in all_reviews}

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_WI_FIELDS, extrasaction="ignore")
    writer.writeheader()

    for item in items:
        if item.id is None:
            continue
        top_pred = top_pred_by_item.get(item.id)
        review = review_by_item.get(item.id)

        label = top_pred.label if top_pred else None
        # Use override label if the reviewer corrected it
        effective_label = (review.override_label if review and review.override_label else label)

        is_blank = effective_label in _BLANK_LABELS if effective_label else True
        is_human = effective_label == "human" if effective_label else False

        # Derive camera_id from the immediate parent directory of the file
        camera_id = os.path.basename(os.path.dirname(item.path)) if item.path else ""
        deployment_id = f"{project_name}-{camera_id}" if camera_id else project_name

        writer.writerow(
            {
                "project_id": project_name,
                "subproject_id": "",
                "camera_id": camera_id,
                "deployment_id": deployment_id,
                "image_id": item.id,
                "image_sequence": "",
                "filename": item.filename,
                "timestamp": item.captured_at.isoformat() if item.captured_at else "",
                "image_is_blank": "TRUE" if effective_label == "blank" else "FALSE",
                "human_in_image": "TRUE" if is_human else "FALSE",
                "number_of_objects": 0 if is_blank else 1,
                "common_name": effective_label if not is_blank else "",
                "notes": review.reviewer_note if review and review.reviewer_note else "",
                "latitude": item.latitude if item.latitude is not None else "",
                "longitude": item.longitude if item.longitude is not None else "",
                "review_status": review.status if review else ReviewStatus.unreviewed,
                "reviewer_name": review.reviewer_name if review and review.reviewer_name else "",
            }
        )

    return buf.getvalue()
