from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus
from app.repositories.reviews import upsert_review

router = APIRouter(prefix="/api", tags=["items"])


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
    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())

    result: list[dict[str, object]] = []
    for item in items:
        top_pred = session.exec(
            select(Prediction)
            .where(Prediction.item_id == item.id)
            .order_by(Prediction.confidence.desc())  # type: ignore[attr-defined]
        ).first()

        review = session.exec(
            select(ReviewRecord).where(ReviewRecord.item_id == item.id)
        ).first()
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
                "thumbnail_url": f"/thumbs/{item.thumbnail_path.split('/')[-1]}"
                if item.thumbnail_path
                else None,
                "top_label": top_label,
                "top_confidence": top_confidence,
                "review_status": review_status,
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

    review = session.exec(
        select(ReviewRecord).where(ReviewRecord.item_id == item_id)
    ).first()

    return {
        "id": item.id,
        "filename": item.filename,
        "full_image_url": f"/images/{item.filename}",
        "thumbnail_url": f"/thumbs/{item.thumbnail_path.split('/')[-1]}"
        if item.thumbnail_path
        else None,
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
        }
        if review
        else None,
    }


# ── labels ────────────────────────────────────────────────────────────────────


@router.get("/collections/{collection_id}/labels")
def list_labels(
    collection_id: int, session: Session = Depends(get_session)
) -> list[str]:
    """Return distinct prediction labels for a collection."""
    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())
    item_ids = [i.id for i in items if i.id is not None]
    if not item_ids:
        return []
    preds = list(session.exec(select(Prediction).where(Prediction.item_id.in_(item_ids))).all())  # type: ignore[attr-defined]
    return sorted({p.label for p in preds})


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

    status_val = str(body.get("status", "confirmed"))
    override_label = body.get("override_label")
    reviewer_note = body.get("reviewer_note")

    record = upsert_review(
        session,
        item_id,
        status=ReviewStatus(status_val),
        override_label=str(override_label) if override_label else None,
        reviewer_note=str(reviewer_note) if reviewer_note else None,
    )
    return {
        "id": record.id,
        "item_id": record.item_id,
        "status": record.status,
        "override_label": record.override_label,
        "reviewer_note": record.reviewer_note,
        "updated_at": record.updated_at.isoformat(),
    }
