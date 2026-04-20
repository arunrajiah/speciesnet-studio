import csv
import io
import json

from sqlmodel import Session, select

from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus


def _build_rows(session: Session, collection_id: int) -> list[dict[str, object]]:
    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())
    rows: list[dict[str, object]] = []

    for item in items:
        top_pred = session.exec(
            select(Prediction)
            .where(Prediction.item_id == item.id)
            .order_by(Prediction.confidence.desc())  # type: ignore[attr-defined]
        ).first()

        review = session.exec(
            select(ReviewRecord).where(ReviewRecord.item_id == item.id)
        ).first()

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
