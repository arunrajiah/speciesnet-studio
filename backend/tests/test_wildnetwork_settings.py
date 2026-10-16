"""Saved WildNetwork settings and automatic sending after a review."""

import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from test_wdx import _seed

from app.db import get_session
from app.main import create_app
from app.models.review import ReviewStatus
from app.repositories.reviews import upsert_review
from app.services import settings as saved
from app.services import wdx


@pytest.fixture()
def client_and_session() -> Iterator[tuple[TestClient, Session]]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    app = create_app()

    def override() -> Iterator[Session]:
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override
    with Session(engine) as s:
        yield TestClient(app), s


def test_key_is_saved_but_never_returned(client_and_session: tuple[TestClient, Session]) -> None:
    c, _ = client_and_session
    assert c.get("/api/settings/wildnetwork").json()["has_api_key"] is False
    res = c.put(
        "/api/settings/wildnetwork",
        json={"api_key": "wn_secret", "latitude": 11.6, "longitude": 76.5, "auto_send": True},
    ).json()
    assert res["has_api_key"] is True and res["auto_send"] is True and res["latitude"] == 11.6
    body = c.get("/api/settings/wildnetwork").text
    assert "wn_secret" not in body and json.loads(body)["has_api_key"] is True
    # A partial update keeps the rest; an empty key forgets it.
    c.put("/api/settings/wildnetwork", json={"utc_offset": "+05:30"})
    assert c.get("/api/settings/wildnetwork").json()["latitude"] == 11.6
    assert c.put("/api/settings/wildnetwork", json={"api_key": ""}).json()["has_api_key"] is False
    assert c.put("/api/settings/wildnetwork", json={"latitude": 123}).status_code == 400
    assert c.put("/api/settings/wildnetwork", json={"utc_offset": "noon"}).status_code == 400


def test_send_uses_saved_key_and_location(
    monkeypatch: pytest.MonkeyPatch, client_and_session: tuple[TestClient, Session]
) -> None:
    c, s = client_and_session
    col_id = _seed(s)
    sent: list[tuple[int, str, str]] = []

    def fake_send(events: list[dict[str, object]], endpoint: str, key: str) -> dict[str, int]:
        sent.append((len(events), endpoint, key))
        return {"received": len(events), "inserted": len(events), "updated": 0, "rejected": 0}

    monkeypatch.setattr("app.routers.export.send", fake_send)
    no_key = c.post(f"/api/collections/{col_id}/send-wdx", json={})
    assert no_key.status_code == 400 and "API key" in no_key.json()["detail"]
    c.put(
        "/api/settings/wildnetwork",
        json={"api_key": "wn_saved", "latitude": 11.6, "longitude": 76.5},
    )
    res = c.post(f"/api/collections/{col_id}/send-wdx", json={}).json()
    assert res["sent"] == 3 and sent[-1] == (3, saved.DEFAULT_ENDPOINT, "wn_saved")


def test_auto_send_after_review(
    monkeypatch: pytest.MonkeyPatch, client_and_session: tuple[TestClient, Session]
) -> None:
    _, s = client_and_session
    _seed(s)
    calls: list[list[str]] = []

    def fake_send(events: list[dict[str, object]], endpoint: str, key: str) -> dict[str, int]:
        calls.append([str(e["media"]["fileName"]) for e in events])  # type: ignore[index]
        return {"received": len(events)}

    monkeypatch.setattr(wdx, "send", fake_send)
    # Off by default: nothing is sent.
    assert wdx.auto_send_items(s, [1, 2]) is None and calls == []

    saved.save(
        s,
        saved.WildNetworkSettings(api_key="wn_k", latitude=11.6, longitude=76.5, auto_send=True),
    )
    # The never-reviewed image d.jpg is reviewed now: only that one goes out.
    d_id = 4
    upsert_review(s, d_id, ReviewStatus.confirmed, reviewer_name="Ranger B")
    assert wdx.auto_send_items(s, [d_id]) == {"received": 1}
    assert calls == [["d.jpg"]]
    cfg = saved.load(s)
    assert cfg.last_send_result == "sent 1, accepted 1" and cfg.last_send_at

    # A human or blank image produces nothing to send.
    calls.clear()
    wdx.auto_send_items(s, [5, 6])
    assert calls == []
