"""Saved Wildlife Network settings, so sending needs no typing each time.

Studio is self-hosted, so the key is kept in the local database next to the reviews.
It is never returned by the
API; the frontend only learns whether one is saved.
"""

import json
from dataclasses import asdict, dataclass

from sqlmodel import Session

from app.models.setting import AppSetting

KEY = "wildnetwork"
DEFAULT_ENDPOINT = "https://wlnw.org/api/v1/events"
# Wildlife Network moved from this host on 2026-10-23. It still accepts uploads,
# but saved settings move to the new one.
OLD_ENDPOINT = "https://wildnetwork.arunrajiah.com/api/v1/events"


@dataclass
class WildNetworkSettings:
    api_key: str | None = None
    endpoint: str = DEFAULT_ENDPOINT
    latitude: float | None = None
    longitude: float | None = None
    utc_offset: str | None = None
    round_coords: int = 2
    auto_send: bool = False  # send each review decision as it is made
    last_send_at: str | None = None
    last_send_result: str | None = None


def load(session: Session) -> WildNetworkSettings:
    row = session.get(AppSetting, KEY)
    if row is None:
        return WildNetworkSettings()
    data = json.loads(row.value)
    known = WildNetworkSettings.__dataclass_fields__
    cfg = WildNetworkSettings(**{k: v for k, v in data.items() if k in known})
    if cfg.endpoint == OLD_ENDPOINT:
        cfg.endpoint = DEFAULT_ENDPOINT
    return cfg


def save(session: Session, s: WildNetworkSettings) -> None:
    row = session.get(AppSetting, KEY)
    value = json.dumps(asdict(s))
    if row is None:
        session.add(AppSetting(key=KEY, value=value))
    else:
        row.value = value
        session.add(row)
    session.commit()


def public(s: WildNetworkSettings) -> dict[str, object]:
    """Everything except the key itself."""
    d: dict[str, object] = asdict(s)
    d.pop("api_key")
    d["has_api_key"] = bool(s.api_key)
    return d
