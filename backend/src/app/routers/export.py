from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session

from app.db import get_session
from app.models.collection import Collection
from app.services.exporters import export_csv, export_json

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/collections/{collection_id}/export")
def export_collection(
    collection_id: int,
    format: str = "csv",
    session: Session = Depends(get_session),
) -> PlainTextResponse:
    """Export collection results as CSV or JSON."""
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
    else:
        raise HTTPException(status_code=400, detail="format must be 'csv' or 'json'")

    return PlainTextResponse(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
