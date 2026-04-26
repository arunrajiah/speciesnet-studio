from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models.review import ReviewRecord, ReviewStatus


def upsert_review(
    session: Session,
    item_id: int,
    status: ReviewStatus,
    override_label: str | None = None,
    reviewer_note: str | None = None,
    reviewer_name: str | None = None,
) -> ReviewRecord:
    """Insert or update the review record for *item_id*."""
    existing = session.exec(select(ReviewRecord).where(ReviewRecord.item_id == item_id)).first()

    if existing:
        existing.status = status
        existing.override_label = override_label
        existing.reviewer_note = reviewer_note
        existing.reviewer_name = reviewer_name
        existing.updated_at = datetime.now(UTC)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    record = ReviewRecord(
        item_id=item_id,
        status=status,
        override_label=override_label,
        reviewer_note=reviewer_note,
        reviewer_name=reviewer_name,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_review(session: Session, item_id: int) -> ReviewRecord | None:
    """Return the review record for *item_id*, or None."""
    return session.exec(select(ReviewRecord).where(ReviewRecord.item_id == item_id)).first()
