import asyncio
import json
import logging
import os
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, WebSocket
from sqlmodel import Session

from app.adapters.speciesnet_adapter import SpeciesNetAdapter
from app.adapters.subprocess_adapter import SubprocessAdapter
from app.config import load_config
from app.db import engine, get_session
from app.repositories.collections import get_collection
from app.services.jobs import create_job, get_job, update_job
from app.services.results_parser import parse_predictions_json, persist_predictions

PREDICTIONS_DIR = os.environ.get("PREDICTIONS_DIR", "./data/predictions")

logger = logging.getLogger(__name__)

router = APIRouter(tags=["inference"])


def _run_inference_task(job_id: str, collection_id: int, folder: str) -> None:
    """Background task: run adapter, parse results, persist predictions."""
    update_job(job_id, status="running", stage="starting")
    os.makedirs(PREDICTIONS_DIR, exist_ok=True)
    output_json = os.path.join(PREDICTIONS_DIR, f"job_{job_id}.json")

    config = load_config()
    if config.get("adapter") == "speciesnet":
        adapter: SubprocessAdapter | SpeciesNetAdapter = SpeciesNetAdapter(
            model_name=config.get("speciesnet_model"),
            country=config.get("speciesnet_country"),
            geofence=bool(config.get("speciesnet_geofence", True)),
        )
    else:
        adapter = SubprocessAdapter(config.get("adapter_command", ["echo", "no-op"]))

    def on_progress(progress: dict[str, object]) -> None:
        update_job(
            job_id,
            stage="inferring",
            current=progress.get("current", 0),
            total=progress.get("total", 0),
        )

    try:
        # Write an empty predictions file so the parser has something to read
        # even if the adapter doesn't write one (e.g. the placeholder echo command)
        if not os.path.exists(output_json):
            with open(output_json, "w") as fh:
                json.dump({"predictions": []}, fh)

        adapter.run(folder, output_json, on_progress)

        update_job(job_id, stage="parsing")
        parsed = parse_predictions_json(output_json)

        update_job(job_id, stage="persisting")
        with Session(engine) as session:
            persist_predictions(session, collection_id, parsed)

        update_job(
            job_id,
            status="completed",
            stage="done",
            finished_at=datetime.now(UTC).isoformat(),
        )
    except Exception as exc:
        logger.exception("Inference job %s failed", job_id)
        update_job(
            job_id,
            status="failed",
            error=str(exc),
            finished_at=datetime.now(UTC).isoformat(),
        )


@router.post("/api/collections/{collection_id}/inference")
def start_inference(
    collection_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """Kick off an inference job for a collection."""
    col = get_collection(session, collection_id)
    if col is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    job_id = create_job()
    background_tasks.add_task(_run_inference_task, job_id, collection_id, col.source_folder)
    return {"job_id": job_id}


@router.get("/api/jobs/{job_id}")
def get_job_status(job_id: str) -> dict[str, object]:
    """Return the current state of a job."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.websocket("/ws/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str) -> None:
    """Stream job state over WebSocket until the job reaches a terminal state."""
    await websocket.accept()
    try:
        while True:
            job = get_job(job_id)
            if job is None:
                await websocket.send_json({"error": "job not found"})
                break
            await websocket.send_json(job)
            if job.get("status") in ("completed", "failed"):
                break
            await asyncio.sleep(1)
    except Exception:
        logger.exception("WebSocket error for job %s", job_id)
    finally:
        await websocket.close()
