from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, col, func, select

from app.db import get_session
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/collections/{collection_id}/stats")
def get_collection_stats(
    collection_id: int,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Return review and prediction statistics for a collection.

    Two queries are issued:
    1. Item + ReviewRecord join for status counts.
    2. Item + Prediction join for confidence averages and top-label counts.
    """
    # ── query 1: status counts ────────────────────────────────────────────────
    # Left-outer-join so items with no review record are counted as unreviewed.
    status_rows = session.exec(
        select(ReviewRecord.status, func.count(col(Item.id)).label("cnt"))
        .select_from(Item)
        .outerjoin(ReviewRecord, col(ReviewRecord.item_id) == col(Item.id))
        .where(col(Item.collection_id) == collection_id)
        .group_by(ReviewRecord.status)
    ).all()

    total = 0
    status_counts: dict[str | None, int] = {}
    for row in status_rows:
        status_counts[row[0]] = row[1]
        total += row[1]

    # Items with no review record have status == None in the outer join.
    null_count = status_counts.pop(None, 0)
    confirmed = status_counts.get(ReviewStatus.confirmed, 0)
    overridden = status_counts.get(ReviewStatus.overridden, 0)
    flagged = status_counts.get(ReviewStatus.flagged, 0)
    unreviewed_explicit = status_counts.get(ReviewStatus.unreviewed, 0)
    unreviewed = null_count + unreviewed_explicit
    reviewed = total - unreviewed

    # ── query 2: per-item max confidence + label ──────────────────────────────
    # Subquery: highest confidence prediction per item.
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

    # Join back to get the label for the max-confidence prediction.
    # Where multiple predictions share the exact max confidence, take any one.
    top_pred_rows = session.exec(
        select(Prediction.label, Prediction.confidence)
        .join(
            max_conf_sub,
            (col(Prediction.item_id) == max_conf_sub.c.item_id)
            & (col(Prediction.confidence) == max_conf_sub.c.max_conf),
        )
        .join(Item, col(Prediction.item_id) == col(Item.id))
        .where(col(Item.collection_id) == collection_id)
        .distinct()
    ).all()

    # avg_confidence = mean of per-item max confidence values.
    if top_pred_rows:
        avg_confidence: float | None = sum(r[1] for r in top_pred_rows) / len(top_pred_rows)
    else:
        avg_confidence = None

    # top_labels: count of items where that label is the top prediction.
    label_counts: dict[str, int] = {}
    for label, _conf in top_pred_rows:
        label_counts[label] = label_counts.get(label, 0) + 1

    top_labels = [
        {"label": lbl, "count": cnt}
        for lbl, cnt in sorted(label_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    ]

    # ── query 3: review count per reviewer ───────────────────────────────────
    reviewer_rows = session.exec(
        select(ReviewRecord.reviewer_name, func.count(col(ReviewRecord.id)).label("cnt"))
        .join(Item, col(ReviewRecord.item_id) == col(Item.id))
        .where(col(Item.collection_id) == collection_id)
        .where(col(ReviewRecord.status) != ReviewStatus.unreviewed)
        .where(col(ReviewRecord.reviewer_name).is_not(None))
        .group_by(ReviewRecord.reviewer_name)
        .order_by(func.count(col(ReviewRecord.id)).desc())
    ).all()

    reviewers = [{"name": name, "count": cnt} for name, cnt in reviewer_rows if name]

    return {
        "total": total,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "confirmed": confirmed,
        "overridden": overridden,
        "flagged": flagged,
        "avg_confidence": avg_confidence,
        "top_labels": top_labels,
        "reviewers": reviewers,
    }
