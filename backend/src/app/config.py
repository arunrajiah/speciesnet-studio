import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG: dict[str, Any] = {
    # Set adapter to "speciesnet" to use the Python package directly.
    # Any other value (or absence) falls back to SubprocessAdapter.
    "adapter": "subprocess",
    "adapter_command": ["echo", "configure me — see config/inference.yaml"],
    # Optional SpeciesNet-specific settings (only used when adapter = "speciesnet")
    "speciesnet_model": None,
    "speciesnet_country": None,
    "speciesnet_geofence": True,
}

_CONFIG_PATH = os.environ.get("STUDIO_CONFIG", "./config/inference.yaml")


def load_config() -> dict[str, Any]:
    """Load ./config/inference.yaml if it exists; fall back to defaults."""
    if not os.path.exists(_CONFIG_PATH):
        logger.warning("Config not found at %s — using defaults", _CONFIG_PATH)
        return dict(_DEFAULT_CONFIG)

    try:
        import yaml  # soft dependency — only needed at runtime

        with open(_CONFIG_PATH) as fh:
            data: dict[str, Any] = yaml.safe_load(fh) or {}
        return {**_DEFAULT_CONFIG, **data}
    except ImportError:
        logger.warning("PyYAML not installed — using default config")
        return dict(_DEFAULT_CONFIG)
    except Exception as exc:
        logger.error("Failed to load config from %s: %s", _CONFIG_PATH, exc)
        return dict(_DEFAULT_CONFIG)
