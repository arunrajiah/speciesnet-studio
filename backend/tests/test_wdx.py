import json
from datetime import datetime

from sqlmodel import Session

from app.models.collection import Collection
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus
from app.services import wdx
from app.services.wdx import WdxOptions, build_events, parse_label

LEOPARD = "a1b2;mammalia;carnivora;felidae;panthera;pardus;leopard"
CHITAL = "c3d4;mammalia;cetartiodactyla;cervidae;axis;axis;chital"
HUMAN = "f1f2;;;;;;human"
BLANK = "f3f4;;;;;;blank"


def _seed(session: Session) -> int:
    col = Collection(name="Kabini cam 07", source_folder="/data/cam07")
    session.add(col)
    session.commit()
    session.refresh(col)
    assert col.id is not None
    rows = [
        # (filename, label, confidence, review status, override, gps)
        ("a.jpg", LEOPARD, 0.93, ReviewStatus.confirmed, None, (11.58123, 76.54321)),
        ("b.jpg", LEOPARD, 0.61, ReviewStatus.overridden, CHITAL, None),
        ("c.jpg", CHITAL, 0.88, ReviewStatus.flagged, None, None),
        ("d.jpg", CHITAL, 0.97, None, None, None),  # never reviewed
        ("e.jpg", HUMAN, 0.99, ReviewStatus.confirmed, None, None),
        ("f.jpg", BLANK, 0.99, ReviewStatus.confirmed, None, None),
    ]
    for i, (name, label, conf, status, override, gps) in enumerate(rows):
        item = Item(
            collection_id=col.id,
            filename=name,
            path=f"/data/cam07/{name}",
            captured_at=datetime(2026, 9, 14, 5, 40 + i),
            latitude=gps[0] if gps else None,
            longitude=gps[1] if gps else None,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        session.add(
            Prediction(
                item_id=item.id,
                label=label,
                confidence=conf,
                bbox_json="[0.41, 0.33, 0.22, 0.29]",
                model_version="4.0.1a",
            )
        )
        if status is not None:
            session.add(
                ReviewRecord(
                    item_id=item.id,
                    status=status,
                    override_label=override,
                    reviewer_name="Ranger A",
                )
            )
        session.commit()
    return col.id


def test_parse_label() -> None:
    assert parse_label(LEOPARD) == {
        "scientificName": "Panthera pardus",
        "taxonRank": "species",
        "vernacularName": "leopard",
    }
    assert parse_label("x;mammalia;carnivora;felidae;panthera;;") == {
        "scientificName": "Panthera",
        "taxonRank": "genus",
    }
    assert parse_label(HUMAN) is None
    assert parse_label(BLANK) is None
    assert parse_label("Panthera tigris") == {
        "scientificName": "Panthera tigris",
        "taxonRank": "species",
    }
    assert parse_label("sloth bear") == {"vernacularName": "sloth bear", "taxonRank": "unranked"}


def test_reviewed_events(session: Session) -> None:
    col_id = _seed(session)
    events, skipped = build_events(
        session, col_id, WdxOptions(latitude=11.6, longitude=76.5, utc_offset="+05:30")
    )
    by_file = {e["media"]["fileName"]: e for e in events}  # type: ignore[index]
    # Humans and blanks are never exported; the unreviewed image is left out by default.
    assert sorted(by_file) == ["a.jpg", "b.jpg", "c.jpg"]
    assert skipped["not_wildlife"] == 2 and skipped["unreviewed"] == 1

    a = by_file["a.jpg"]
    assert a["wdx"] == "0.2" and str(a["eventId"]).startswith("speciesnet-studio:")
    assert a["eventStart"] == "2026-09-14T05:40:00+05:30"
    assert a["deployment"]["latitude"] == 11.58 and a["deployment"]["longitude"] == 76.54  # type: ignore[index]
    assert a["detection"]["scientificName"] == "Panthera pardus"  # type: ignore[index]
    assert [s["role"] for s in a["detection"]["pipeline"]] == ["detector", "classifier"]  # type: ignore[index]
    assert a["media"]["region"] == {
        "type": "box",
        "coordinates": [0.41, 0.33, 0.22, 0.29],
        "units": "normalized",
    }  # type: ignore[index]
    assert a["review"]["status"] == "confirmed" and a["review"]["reviewedBy"] == "Ranger A"  # type: ignore[index]
    assert a["source"]["system"] == "speciesnet-studio"  # type: ignore[index]

    # An override replaces the model's label and counts as a confirmed identification.
    b = by_file["b.jpg"]
    assert b["detection"]["scientificName"] == "Axis axis" and b["review"]["status"] == "confirmed"  # type: ignore[index]
    assert (
        b["deployment"]["latitude"] == 11.6
    )  # no GPS in the image: the collection's location  # type: ignore[index]
    assert by_file["c.jpg"]["review"]["status"] == "uncertain"  # type: ignore[index]


def test_ids_are_stable_and_unreviewed_optional(session: Session) -> None:
    col_id = _seed(session)
    opt = WdxOptions(latitude=11.6, longitude=76.5, reviewed_only=False)
    first, _ = build_events(session, col_id, opt)
    again, _ = build_events(session, col_id, opt)
    assert [e["eventId"] for e in first] == [e["eventId"] for e in again]
    d = next(e for e in first if e["media"]["fileName"] == "d.jpg")  # type: ignore[index]
    assert d["review"] == {"status": "unreviewed"}


def test_without_location_nothing_is_sent(session: Session) -> None:
    col_id = _seed(session)
    events, skipped = build_events(session, col_id, WdxOptions())
    assert [e["media"]["fileName"] for e in events] == ["a.jpg"]  # type: ignore[index]
    assert skipped["no_location"] == 2


def test_send_batches_and_sums(monkeypatch, session: Session) -> None:  # type: ignore[no-untyped-def]
    col_id = _seed(session)
    events, _ = build_events(session, col_id, WdxOptions(latitude=11.6, longitude=76.5))
    calls: list[tuple[str, str, int]] = []

    class Resp:
        def __init__(self, n: int) -> None:
            self.n = n

        def __enter__(self) -> "Resp":
            return self

        def __exit__(self, *a: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(
                {"received": self.n, "inserted": self.n, "updated": 0, "rejected": 0}
            ).encode()

    def fake_urlopen(req, timeout=0):  # type: ignore[no-untyped-def]
        lines = req.data.decode().strip().splitlines()
        calls.append((req.full_url, req.headers["Authorization"], len(lines)))
        assert all(json.loads(line)["wdx"] == "0.2" for line in lines)
        return Resp(len(lines))

    monkeypatch.setattr(wdx.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(wdx, "BATCH", 2)
    res = wdx.send(events, "https://example.org/api/v1/events", "wn_test")
    assert res["received"] == 3 and res["inserted"] == 3
    assert [c[2] for c in calls] == [2, 1] and calls[0][1] == "Bearer wn_test"
