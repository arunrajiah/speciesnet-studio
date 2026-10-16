"""WDX (Wildlife Detection Exchange) export, and sending reviewed results to WildNetwork.

One WDX event per image: the reviewer's decision when there is one, otherwise the top
prediction. Blank, human and
vehicle images are never exported. Coordinates are rounded before they leave Studio. Spec:
https://github.com/arunrajiah/wildlife-detection-exchange
"""

import hashlib
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models.collection import Collection
from app.models.item import Item
from app.models.prediction import Prediction
from app.models.review import ReviewRecord, ReviewStatus

SOURCE = "speciesnet-studio"
STUDIO_VERSION = "0.5"
_SKIP_COMMON = frozenset({"blank", "human", "vehicle", "no_cv_result", "animal"})
BATCH = 1000

# Review decisions in WDX terms. An override is a human identification, so it counts as confirmed.
_REVIEW = {
    ReviewStatus.confirmed: "confirmed",
    ReviewStatus.overridden: "confirmed",
    ReviewStatus.flagged: "uncertain",
    ReviewStatus.unreviewed: "unreviewed",
}


@dataclass
class WdxOptions:
    latitude: float | None = None  # used when an image has no GPS in its EXIF
    longitude: float | None = None
    round_coords: int = 2  # 2 decimals is about 1 km
    utc_offset: str | None = (
        None  # camera clock offset such as "+05:30"; default: this machine's offset
    )
    min_confidence: float = 0.0
    reviewed_only: bool = True
    license: str = "CC-BY-4.0"


def parse_label(label: str) -> dict[str, str] | None:
    """A SpeciesNet label (uuid;class;order;family;genus;species;common) or a plain name, as WDX.

    Returns None for labels that must not be exported (blank, human, vehicle, unidentified animal).
    """
    label = (label or "").strip()
    if not label:
        return None
    if ";" in label:
        parts = (label.split(";") + [""] * 7)[:7]
        _uuid, cls, order, family, genus, species, common = (p.strip() for p in parts)
        if common.lower() in _SKIP_COMMON:
            return None
        out: dict[str, str] = {}
        if genus and species:
            out = {
                "scientificName": f"{genus.capitalize()} {species.lower()}",
                "taxonRank": "species",
            }
        elif genus:
            out = {"scientificName": genus.capitalize(), "taxonRank": "genus"}
        elif family:
            out = {"scientificName": family.capitalize(), "taxonRank": "family"}
        elif cls:
            out = {"scientificName": cls.capitalize(), "taxonRank": "class"}
        else:
            return None
        if common:
            out["vernacularName"] = common
        return out
    if label.lower() in _SKIP_COMMON:
        return None
    words = label.split()
    # A reviewer's free-text override: a binomial is a scientific name, anything else a common name.
    if len(words) == 2 and words[0][:1].isupper() and words[1].islower():
        return {"scientificName": label, "taxonRank": "species"}
    return {"vernacularName": label, "taxonRank": "unranked"}


def _offset(opt: WdxOptions) -> timezone:
    if opt.utc_offset:
        sign = -1 if opt.utc_offset.startswith("-") else 1
        hh, _, mm = opt.utc_offset.lstrip("+-").partition(":")
        return timezone(sign * timedelta(hours=int(hh), minutes=int(mm or 0)))
    local = datetime.now().astimezone().tzinfo
    return local if isinstance(local, timezone) else UTC


def build_events(
    session: Session, collection_id: int, opt: WdxOptions, item_ids: list[int] | None = None
) -> tuple[list[dict[str, object]], dict[str, int]]:
    """WDX events for a collection, plus counts of what was skipped and why."""
    col = session.get(Collection, collection_id)
    query = select(Item).where(Item.collection_id == collection_id)
    if item_ids is not None:
        query = query.where(Item.id.in_(item_ids))  # type: ignore[union-attr]
    items = list(session.exec(query).all())
    skipped = {
        "no_prediction": 0,
        "not_wildlife": 0,
        "unreviewed": 0,
        "low_confidence": 0,
        "no_location": 0,
        "no_time": 0,
    }
    if col is None or not items:
        return [], skipped
    ids = [i.id for i in items if i.id is not None]
    top: dict[int, Prediction] = {}
    for p in session.exec(
        select(Prediction).where(Prediction.item_id.in_(ids)).order_by(Prediction.confidence.desc())  # type: ignore[attr-defined]
    ).all():
        top.setdefault(p.item_id, p)
    in_ids = ReviewRecord.item_id.in_(ids)  # type: ignore[attr-defined]
    reviews = {r.item_id: r for r in session.exec(select(ReviewRecord).where(in_ids)).all()}
    tz = _offset(opt)
    deployment_id = "collection-" + hashlib.sha256(col.source_folder.encode()).hexdigest()[:12]

    events: list[dict[str, object]] = []
    for item in items:
        pred = top.get(item.id)  # type: ignore[arg-type]
        if pred is None:
            skipped["no_prediction"] += 1
            continue
        review = reviews.get(item.id)  # type: ignore[arg-type]
        status = review.status if review else ReviewStatus.unreviewed
        if opt.reviewed_only and status == ReviewStatus.unreviewed:
            skipped["unreviewed"] += 1
            continue
        label = (
            review.override_label
            if review and status == ReviewStatus.overridden and review.override_label
            else pred.label
        )
        taxon = parse_label(label)
        if taxon is None:
            skipped["not_wildlife"] += 1
            continue
        if status == ReviewStatus.unreviewed and pred.confidence < opt.min_confidence:
            skipped["low_confidence"] += 1
            continue
        lat = item.latitude if item.latitude is not None else opt.latitude
        lon = item.longitude if item.longitude is not None else opt.longitude
        if lat is None or lon is None:
            skipped["no_location"] += 1
            continue
        if item.captured_at is None:
            skipped["no_time"] += 1
            continue
        start = item.captured_at if item.captured_at.tzinfo else item.captured_at.replace(tzinfo=tz)
        # Stable across re-ingesting the same folder: a second send updates, not duplicates.
        rid = hashlib.sha256(f"{item.path}|{item.captured_at.isoformat()}".encode()).hexdigest()[
            :20
        ]
        model = pred.model_version or "unknown"
        detection: dict[str, object] = {
            **taxon,
            "confidence": round(float(pred.confidence), 4),
            "classifier": {"name": "SpeciesNet", "version": model},
            "pipeline": [
                {"role": "detector", "name": "MegaDetector", "version": "5a"},
                {"role": "classifier", "name": "SpeciesNet", "version": model},
            ],
        }
        media: dict[str, object] = {"mediaType": "image", "fileName": item.filename}
        if pred.bbox_json:
            try:
                box = [float(v) for v in json.loads(pred.bbox_json)]
                if len(box) == 4:
                    media["region"] = {"type": "box", "coordinates": box, "units": "normalized"}
            except (ValueError, TypeError):
                pass
        rev: dict[str, object] = {"status": _REVIEW[status]}
        if review and status != ReviewStatus.unreviewed:
            if review.reviewer_name:
                rev["reviewedBy"] = review.reviewer_name
            when = (
                review.updated_at
                if review.updated_at.tzinfo
                else review.updated_at.replace(tzinfo=UTC)
            )
            rev["reviewedAt"] = when.isoformat(timespec="seconds")
        events.append(
            {
                "wdx": "0.2",
                "eventId": f"{SOURCE}:{rid}",
                "eventStart": start.isoformat(timespec="seconds"),
                "deployment": {
                    "deploymentId": deployment_id,
                    "name": col.name,
                    "latitude": round(lat, opt.round_coords),
                    "longitude": round(lon, opt.round_coords),
                    "coordinateUncertaintyMeters": max(1, int(111_000 / (10**opt.round_coords))),
                    "sensorType": "camera-trap",
                },
                "detection": detection,
                "media": media,
                "review": rev,
                "source": {
                    "system": SOURCE,
                    "systemVersion": STUDIO_VERSION,
                    "sourceRecordId": rid,
                },
                "license": opt.license,
            }
        )
    return events, skipped


def to_ndjson(events: list[dict[str, object]]) -> str:
    return "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in events)


def send(
    events: list[dict[str, object]], endpoint: str, api_key: str, timeout: float = 60
) -> dict[str, object]:
    """POST events in batches to a WDX endpoint, e.g. WildNetwork's /api/v1/events."""
    counts = {"received": 0, "inserted": 0, "updated": 0, "rejected": 0}
    details: list[object] = []
    for i in range(0, len(events), BATCH):
        req = urllib.request.Request(
            endpoint,
            data=to_ndjson(events[i : i + BATCH]).encode(),
            method="POST",
            headers={
                "authorization": f"Bearer {api_key}",
                "content-type": "application/x-ndjson",
                "user-agent": f"speciesnet-studio/{STUDIO_VERSION}",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (endpoint is chosen by the user)
            res = json.loads(r.read())
        for k in counts:
            counts[k] += int(res.get(k, 0))
        details.extend(res.get("rejectedDetails", [])[: max(0, 20 - len(details))])
    return {**counts, "rejectedDetails": details}


def auto_send_items(session: Session, item_ids: list[int]) -> dict[str, object] | None:
    """Send just-reviewed items with the saved settings, when automatic sending is on.

    Returns None when it is off or not set up. The outcome is saved for the Export dialog.
    """
    from app.services import settings as saved

    cfg = saved.load(session)
    if not (cfg.auto_send and cfg.api_key) or not item_ids:
        return None
    opt = WdxOptions(
        latitude=cfg.latitude,
        longitude=cfg.longitude,
        round_coords=cfg.round_coords,
        utc_offset=cfg.utc_offset,
        reviewed_only=True,
    )
    by_collection: dict[int, list[int]] = {}
    for item in session.exec(select(Item).where(Item.id.in_(item_ids))).all():  # type: ignore[union-attr]
        by_collection.setdefault(item.collection_id, []).append(item.id)  # type: ignore[arg-type]
    events: list[dict[str, object]] = []
    for collection_id, ids in by_collection.items():
        events += build_events(session, collection_id, opt, ids)[0]
    try:
        result: dict[str, object] = (
            send(events, cfg.endpoint, cfg.api_key) if events else {"received": 0}
        )
        cfg.last_send_result = f"sent {len(events)}, accepted {result.get('received', 0)}"
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        result = {"error": str(e)}
        cfg.last_send_result = f"failed: {e}"[:200]
    cfg.last_send_at = datetime.now(UTC).isoformat(timespec="seconds")
    saved.save(session, cfg)
    return result


def schedule_auto_send(session: Session, item_ids: list[int]) -> None:
    """After a review is saved: send in a background thread, so reviewing never waits."""
    from app.services import settings as saved

    cfg = saved.load(session)
    if not (cfg.auto_send and cfg.api_key) or not item_ids:
        return
    import threading

    from app.db import engine

    def run() -> None:
        with Session(engine) as s:
            auto_send_items(s, item_ids)

    threading.Thread(target=run, daemon=True).start()
