import logging
import os
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def _count_images(folder: str) -> int:
    return sum(1 for p in Path(folder).rglob("*") if p.suffix.lower() in _IMAGE_EXTS)


class SpeciesNetAdapter:
    """Run SpeciesNet inference via the Python API (requires `speciesnet` package).

    Calls ``model.predict()`` which writes the predictions JSON to *output_json*.
    Progress is reported as (0, total) → (total, total) since the Python API does
    not expose a per-image callback; use ``SubprocessAdapter`` if you need
    fine-grained live progress.
    """

    def __init__(
        self,
        model_name: str | None = None,
        country: str | None = None,
        geofence: bool = True,
    ) -> None:
        self._model_name = model_name
        self._country = country
        self._geofence = geofence

    def run(
        self,
        folder: str,
        output_json: str,
        on_progress: Callable[[dict[str, object]], None],
    ) -> None:
        """Run SpeciesNet on *folder* and write predictions to *output_json*."""
        try:
            from speciesnet import DEFAULT_MODEL, SpeciesNet
            from speciesnet.utils import prepare_instances_dict
        except ImportError as exc:
            raise RuntimeError(
                "speciesnet is not installed. Install it with: uv pip install 'speciesnet>=5.0.0'"
            ) from exc

        model_name = self._model_name or os.environ.get("SPECIESNET_MODEL") or DEFAULT_MODEL
        logger.info("Loading SpeciesNet model: %s", model_name)

        total = _count_images(folder)
        on_progress({"current": 0, "total": total})

        instances_dict = prepare_instances_dict(
            folders=[folder],
            country=self._country,
        )

        model = SpeciesNet(model_name, geofence=self._geofence)
        model.predict(
            instances_dict=instances_dict,
            run_mode="multi_thread",
            progress_bars=False,
            predictions_json=output_json,
        )

        on_progress({"current": total, "total": total})
        logger.info("SpeciesNet inference complete: %s", output_json)
