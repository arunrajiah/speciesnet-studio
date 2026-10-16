import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.services import settings as saved

router = APIRouter(prefix="/api/settings", tags=["settings"])


class WildNetworkUpdate(BaseModel):
    """Fields left out are kept. Send ``api_key: ""`` to forget the saved key."""

    api_key: str | None = None
    endpoint: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    utc_offset: str | None = None
    round_coords: int | None = None
    auto_send: bool | None = None


@router.get("/wildnetwork")
def get_wildnetwork(session: Session = Depends(get_session)) -> dict[str, object]:
    """Saved WildNetwork settings without the key itself (``has_api_key`` says if one is saved)."""
    return saved.public(saved.load(session))


@router.put("/wildnetwork")
def put_wildnetwork(
    body: WildNetworkUpdate, session: Session = Depends(get_session)
) -> dict[str, object]:
    cfg = saved.load(session)
    fields = body.model_fields_set
    if "api_key" in fields:
        cfg.api_key = (body.api_key or "").strip() or None
    if "endpoint" in fields and body.endpoint:
        if not body.endpoint.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            raise HTTPException(status_code=400, detail="endpoint must be https")
        cfg.endpoint = body.endpoint
    if "latitude" in fields:
        if body.latitude is not None and not -90 <= body.latitude <= 90:
            raise HTTPException(status_code=400, detail="latitude out of range")
        cfg.latitude = body.latitude
    if "longitude" in fields:
        if body.longitude is not None and not -180 <= body.longitude <= 180:
            raise HTTPException(status_code=400, detail="longitude out of range")
        cfg.longitude = body.longitude
    if "utc_offset" in fields:
        if body.utc_offset and not re.fullmatch(r"[+-]\d{1,2}(:\d{2})?", body.utc_offset):
            raise HTTPException(status_code=400, detail="utc_offset must look like +05:30")
        cfg.utc_offset = body.utc_offset or None
    if "round_coords" in fields and body.round_coords is not None:
        if not 0 <= body.round_coords <= 5:
            raise HTTPException(status_code=400, detail="round_coords must be 0 to 5")
        cfg.round_coords = body.round_coords
    if "auto_send" in fields and body.auto_send is not None:
        cfg.auto_send = body.auto_send
    saved.save(session, cfg)
    return saved.public(cfg)
