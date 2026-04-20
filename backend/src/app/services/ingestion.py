import logging
import os
from datetime import UTC, datetime
from typing import Any

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
from sqlmodel import Session

from app.db import engine
from app.models.item import Item

logger = logging.getLogger(__name__)

_SUPPORTED = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

# In-memory progress keyed by collection_id
_progress: dict[int, dict[str, Any]] = {}


def get_progress(collection_id: int) -> dict[str, Any]:
    """Return ingestion progress for a collection."""
    return _progress.get(collection_id, {"processed": 0, "total": 0, "stage": "idle"})


def _collect_paths(folder: str) -> list[str]:
    paths: list[str] = []
    for root, _, files in os.walk(folder):
        for fname in files:
            if os.path.splitext(fname)[1].lower() in _SUPPORTED:
                paths.append(os.path.join(root, fname))
    return sorted(paths)


def _parse_exif(img: Image.Image) -> dict[str, Any]:
    data: dict[str, Any] = {}
    try:
        raw = img._getexif()  # type: ignore[attr-defined]
        if not raw:
            return data
        exif: dict[str, Any] = {TAGS.get(k, k): v for k, v in raw.items()}

        # Datetime
        for tag in ("DateTimeOriginal", "DateTime"):
            if tag in exif:
                try:
                    data["captured_at"] = datetime.strptime(
                        str(exif[tag]), "%Y:%m:%d %H:%M:%S"
                    ).replace(tzinfo=UTC)
                    break
                except ValueError:
                    logger.debug("Could not parse EXIF datetime tag %s: %r", tag, exif[tag])

        # GPS
        gps_info = exif.get("GPSInfo")
        if gps_info and isinstance(gps_info, dict):
            gps: dict[str, Any] = {GPSTAGS.get(k, k): v for k, v in gps_info.items()}
            lat = _dms_to_decimal(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
            lon = _dms_to_decimal(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
            if lat is not None:
                data["latitude"] = lat
            if lon is not None:
                data["longitude"] = lon
    except Exception:
        pass
    return data


def _dms_to_decimal(dms: Any, ref: Any) -> float | None:
    if not dms or len(dms) != 3:
        return None
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        decimal = degrees + minutes / 60 + seconds / 3600
        if ref in ("S", "W"):
            decimal = -decimal
        return decimal
    except (TypeError, ValueError):
        return None


def _make_thumbnail(src_path: str, thumb_dir: str, filename: str) -> str | None:
    try:
        os.makedirs(thumb_dir, exist_ok=True)
        thumb_name = os.path.splitext(filename)[0] + "_thumb.jpg"
        thumb_path = os.path.join(thumb_dir, thumb_name)
        with Image.open(src_path) as img:
            img.thumbnail((300, 300))
            img.convert("RGB").save(thumb_path, "JPEG", quality=85)
        return thumb_path
    except Exception as exc:
        logger.warning("Thumbnail failed for %s: %s", src_path, exc)
        return None


def walk_folder(collection_id: int, folder: str, thumb_dir: str) -> None:
    """Walk a folder, extract EXIF, generate thumbnails, and persist Item rows."""
    paths = _collect_paths(folder)
    total = len(paths)
    _progress[collection_id] = {"processed": 0, "total": total, "stage": "scanning"}

    with Session(engine) as session:
        for idx, path in enumerate(paths, 1):
            filename = os.path.basename(path)
            exif_data: dict[str, Any] = {}
            width = height = None
            thumb_path = None

            try:
                with Image.open(path) as img:
                    width, height = img.size
                    exif_data = _parse_exif(img)
                thumb_path = _make_thumbnail(path, thumb_dir, filename)
            except Exception as exc:
                logger.warning("Could not open %s: %s", path, exc)

            item = Item(
                collection_id=collection_id,
                filename=filename,
                path=path,
                captured_at=exif_data.get("captured_at"),
                latitude=exif_data.get("latitude"),
                longitude=exif_data.get("longitude"),
                width=width,
                height=height,
                thumbnail_path=thumb_path,
            )
            session.add(item)
            session.commit()

            _progress[collection_id] = {
                "processed": idx,
                "total": total,
                "stage": "ingesting",
            }

    _progress[collection_id] = {"processed": total, "total": total, "stage": "done"}
