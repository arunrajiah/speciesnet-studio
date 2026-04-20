import json
import logging
import os
from dataclasses import dataclass, field

from sqlmodel import Session, select

from app.models.item import Item
from app.models.prediction import Prediction

logger = logging.getLogger(__name__)


@dataclass
class ParsedPrediction:
    """Normalised prediction for a single image."""

    filepath: str
    label: str
    confidence: float
    bbox: list[float] | None
    model_version: str | None
    raw: dict[str, object] = field(default_factory=dict)


def parse_predictions_json(path: str) -> list[ParsedPrediction]:
    """Load *path* and return a flat list of ParsedPrediction objects.

    Accepts the SpeciesNet schema:
    ``{"predictions": [{"filepath": ..., "classifications": {...},
      "detections": [...], "prediction": ..., "prediction_score": ...,
      "model_version": ...}]}``
    """
    with open(path) as fh:
        data: dict[str, object] = json.load(fh)

    results: list[ParsedPrediction] = []
    predictions = data.get("predictions", [])
    if not isinstance(predictions, list):
        return results

    for entry in predictions:
        if not isinstance(entry, dict):
            continue
        filepath = str(entry.get("filepath", ""))
        model_version = entry.get("model_version")
        label = str(entry.get("prediction", "unknown"))
        score = float(entry.get("prediction_score", 0.0))

        # Bounding box from first detection, normalised to [x, y, w, h] in [0,1]
        bbox: list[float] | None = None
        detections = entry.get("detections")
        if isinstance(detections, list) and detections:
            first = detections[0]
            if isinstance(first, dict) and "bbox" in first:
                raw_bbox = first["bbox"]
                if isinstance(raw_bbox, list) and len(raw_bbox) == 4:
                    bbox = [float(v) for v in raw_bbox]

        results.append(
            ParsedPrediction(
                filepath=filepath,
                label=label,
                confidence=score,
                bbox=bbox,
                model_version=str(model_version) if model_version is not None else None,
                raw=dict(entry),
            )
        )

    return results


def persist_predictions(
    session: Session,
    collection_id: int,
    parsed: list[ParsedPrediction],
) -> None:
    """Match ParsedPredictions to Item rows by filename and insert Prediction rows."""
    items = list(session.exec(select(Item).where(Item.collection_id == collection_id)).all())
    filename_to_item: dict[str, Item] = {os.path.basename(item.path): item for item in items}

    inserted = 0
    for pp in parsed:
        filename = os.path.basename(pp.filepath)
        item = filename_to_item.get(filename)
        if item is None:
            logger.warning("No Item found for filepath %s — skipping", pp.filepath)
            continue

        prediction = Prediction(
            item_id=item.id,
            label=pp.label,
            confidence=pp.confidence,
            bbox_json=json.dumps(pp.bbox) if pp.bbox else None,
            model_version=pp.model_version,
            raw_json=json.dumps(pp.raw),
        )
        session.add(prediction)
        inserted += 1

    session.commit()
    logger.info("Persisted %d predictions for collection %d", inserted, collection_id)
