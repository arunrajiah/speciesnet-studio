import re
import urllib.error

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models.collection import Collection
from app.services import settings as saved
from app.services.exporters import export_csv, export_json, export_wildlife_insights
from app.services.wdx import WdxOptions, build_events, send, to_ndjson

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/collections/{collection_id}/export")
def export_collection(
    collection_id: int,
    format: str = "csv",
    latitude: float | None = None,
    longitude: float | None = None,
    round_coords: int = 2,
    utc_offset: str | None = None,
    reviewed_only: bool = True,
    session: Session = Depends(get_session),
) -> PlainTextResponse:
    """Export collection results.

    Supported formats:
    - ``csv`` — all fields, spreadsheet-compatible
    - ``json`` — same fields as CSV, as a JSON array
    - ``wi-csv`` — Wildlife Insights-compatible CSV
    - ``wdx`` — WDX 0.2 events as NDJSON, for Wildlife Network or any WDX endpoint.
      ``latitude``/``longitude`` are used for images without GPS; ``reviewed_only``
      (default true) leaves out images nobody has reviewed.
    """
    collection = session.get(Collection, collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    if format == "json":
        content = export_json(session, collection_id)
        media_type = "application/json"
        filename = f"collection_{collection_id}.json"
    elif format == "csv":
        content = export_csv(session, collection_id)
        media_type = "text/csv"
        filename = f"collection_{collection_id}.csv"
    elif format == "wi-csv":
        content = export_wildlife_insights(session, collection_id, project_name=collection.name)
        media_type = "text/csv"
        filename = f"collection_{collection_id}_wildlife_insights.csv"
    elif format == "wdx":
        opt = _options(latitude, longitude, round_coords, utc_offset, reviewed_only)
        events, _ = build_events(session, collection_id, opt)
        content = to_ndjson(events)
        media_type = "application/x-ndjson"
        filename = f"collection_{collection_id}.wdx.ndjson"
    else:
        raise HTTPException(
            status_code=400, detail="format must be 'csv', 'json', 'wi-csv' or 'wdx'"
        )

    return PlainTextResponse(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _options(
    latitude: float | None,
    longitude: float | None,
    round_coords: int,
    utc_offset: str | None,
    reviewed_only: bool,
) -> WdxOptions:
    if (
        latitude is not None
        and not -90 <= latitude <= 90
        or longitude is not None
        and not -180 <= longitude <= 180
    ):
        raise HTTPException(status_code=400, detail="latitude or longitude out of range")
    if not 0 <= round_coords <= 5:
        raise HTTPException(status_code=400, detail="round_coords must be 0 to 5")
    if utc_offset is not None:
        if not re.fullmatch(r"[+-]\d{1,2}(:\d{2})?", utc_offset):
            raise HTTPException(status_code=400, detail="utc_offset must look like +05:30")
    return WdxOptions(
        latitude=latitude,
        longitude=longitude,
        round_coords=round_coords,
        utc_offset=utc_offset,
        reviewed_only=reviewed_only,
    )


class SendRequest(BaseModel):
    """Fields left out use the saved Wildlife Network settings (Settings > Wildlife Network)."""

    api_key: str | None = None
    endpoint: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    round_coords: int | None = None
    utc_offset: str | None = None
    reviewed_only: bool = True


@router.post("/collections/{collection_id}/send-wdx")
def send_collection(
    collection_id: int, body: SendRequest, session: Session = Depends(get_session)
) -> dict[str, object]:
    """Send a collection's results to Wildlife Network (or another WDX endpoint) as WDX events.

    Sending again updates the same events (stable ids), so a later review round replaces
    earlier decisions.
    """
    if session.get(Collection, collection_id) is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    cfg = saved.load(session)
    api_key = (body.api_key or "").strip() or cfg.api_key
    endpoint = body.endpoint or cfg.endpoint
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="No Wildlife Network API key: add one in the Wildlife Network tab",
        )
    if not endpoint.startswith(("https://", "http://localhost", "http://127.0.0.1")):
        raise HTTPException(status_code=400, detail="endpoint must be https")
    opt = _options(
        body.latitude if body.latitude is not None else cfg.latitude,
        body.longitude if body.longitude is not None else cfg.longitude,
        body.round_coords if body.round_coords is not None else cfg.round_coords,
        body.utc_offset or cfg.utc_offset,
        body.reviewed_only,
    )
    events, skipped = build_events(session, collection_id, opt)
    if not events:
        return {"sent": 0, "skipped": skipped, "result": None}
    try:
        result = send(events, endpoint, api_key)
    except urllib.error.HTTPError as e:
        detail = (
            "Wildlife Network did not accept the API key"
            if e.code == 401
            else f"endpoint answered HTTP {e.code}"
        )
        raise HTTPException(status_code=502, detail=detail) from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise HTTPException(status_code=502, detail=f"could not reach the endpoint: {e}") from e
    return {"sent": len(events), "skipped": skipped, "result": result}
