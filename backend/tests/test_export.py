import json

from sqlmodel import Session

from app.models.collection import Collection
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus
from app.services.exporters import export_csv, export_json


def _seed(session: Session) -> int:
    col = Collection(name="export-test", source_folder="/tmp")
    session.add(col)
    session.commit()
    session.refresh(col)

    item = Item(collection_id=col.id, filename="a.jpg", path="/tmp/a.jpg")
    session.add(item)
    session.commit()
    session.refresh(item)

    pred = Prediction(item_id=item.id, label="lion", confidence=0.91)
    session.add(pred)

    review = ReviewRecord(item_id=item.id, status=ReviewStatus.confirmed)
    session.add(review)
    session.commit()

    assert col.id is not None
    return col.id


def test_export_csv_contains_header_and_row(session: Session) -> None:
    col_id = _seed(session)
    csv_text = export_csv(session, col_id)
    lines = csv_text.strip().splitlines()
    assert lines[0].startswith("id,filename")
    assert "a.jpg" in lines[1]
    assert "lion" in lines[1]
    assert "confirmed" in lines[1]


def test_export_json_is_valid_list(session: Session) -> None:
    col_id = _seed(session)
    data = json.loads(export_json(session, col_id))
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["top_label"] == "lion"
    assert data[0]["review_status"] == "confirmed"


def test_export_csv_empty_collection(session: Session) -> None:
    col = Collection(name="empty", source_folder="/tmp")
    session.add(col)
    session.commit()
    session.refresh(col)
    assert col.id is not None
    assert export_csv(session, col.id) == ""
