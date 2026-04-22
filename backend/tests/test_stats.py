"""Tests for GET /api/collections/{collection_id}/stats."""

from sqlmodel import Session, SQLModel, create_engine

from app.models.collection import Collection
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus

# ── helpers ───────────────────────────────────────────────────────────────────


def _make_engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _seed(session: Session) -> int:
    """Create a collection with 4 items, predictions, and mixed review states."""
    col = Collection(name="stats-test", source_folder="/tmp")
    session.add(col)
    session.commit()
    session.refresh(col)
    assert col.id is not None
    col_id: int = col.id

    species = [
        ("lion", 0.95),
        ("elephant", 0.80),
        ("zebra", 0.70),
        ("lion", 0.60),
    ]
    statuses = [ReviewStatus.confirmed, ReviewStatus.overridden, ReviewStatus.flagged, None]

    for i, ((label, conf), status) in enumerate(zip(species, statuses, strict=True)):
        item = Item(collection_id=col_id, filename=f"img{i}.jpg", path=f"/tmp/img{i}.jpg")
        session.add(item)
        session.commit()
        session.refresh(item)
        assert item.id is not None

        pred = Prediction(item_id=item.id, label=label, confidence=conf)
        session.add(pred)

        if status is not None:
            review = ReviewRecord(item_id=item.id, status=status)
            session.add(review)

    session.commit()
    return col_id


# ── unit tests against the service layer ─────────────────────────────────────


def test_stats_counts(session: Session) -> None:
    """status counts are correct for a mixed collection."""
    from app.routers.stats import get_collection_stats

    col_id = _seed(session)
    # Patch the dependency manually — call the function with our test session.
    result = get_collection_stats(collection_id=col_id, session=session)

    assert result["total"] == 4
    assert result["confirmed"] == 1
    assert result["overridden"] == 1
    assert result["flagged"] == 1
    assert result["unreviewed"] == 1  # item with no ReviewRecord
    assert result["reviewed"] == 3


def test_stats_avg_confidence(session: Session) -> None:
    """avg_confidence is mean of per-item top prediction confidence."""
    from app.routers.stats import get_collection_stats

    col_id = _seed(session)
    result = get_collection_stats(collection_id=col_id, session=session)

    # Items have confidences 0.95, 0.80, 0.70, 0.60  →  mean = 0.7625
    avg = result["avg_confidence"]
    assert avg is not None
    assert abs(float(avg) - 0.7625) < 1e-6


def test_stats_top_labels(session: Session) -> None:
    """top_labels ranks lion first (appears twice)."""
    from app.routers.stats import get_collection_stats

    col_id = _seed(session)
    result = get_collection_stats(collection_id=col_id, session=session)

    top = result["top_labels"]
    assert isinstance(top, list)
    assert len(top) >= 1
    assert top[0]["label"] == "lion"
    assert top[0]["count"] == 2


def test_stats_empty_collection(session: Session) -> None:
    """An empty collection returns all-zero counts and no avg_confidence."""
    from app.routers.stats import get_collection_stats

    col = Collection(name="empty", source_folder="/tmp")
    session.add(col)
    session.commit()
    session.refresh(col)
    assert col.id is not None

    result = get_collection_stats(collection_id=col.id, session=session)

    assert result["total"] == 0
    assert result["reviewed"] == 0
    assert result["unreviewed"] == 0
    assert result["avg_confidence"] is None
    assert result["top_labels"] == []

