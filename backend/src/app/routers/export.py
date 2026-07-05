from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session

from app.db import get_session
from app.models.collection import Collection
from app.services.exporters import export_csv, export_json, export_wildlife_insights

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/collections/{collection_id}/export")
def export_collection(
    collection_id: int,
    format: str = "csv",
    session: Session = Depends(get_session),
) -> PlainTextResponse:
    """Export collection results.

    Supported formats:
    - ``csv`` — all fields, spreadsheet-compatible
    - ``json`` — same fields as CSV, as a JSON array
    - ``wi-csv`` — Wildlife Insights-compatible CSV
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
    else:
        raise HTTPException(status_code=400, detail="format must be 'csv', 'json', or 'wi-csv'")

    return PlainTextResponse(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
