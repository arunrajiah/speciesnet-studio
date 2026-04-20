import logging
import os
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

SAMPLE_IMAGES = [
    {
        "filename": "lion.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lion_waiting_in_Namibia.jpg/320px-Lion_waiting_in_Namibia.jpg",
    },
    {
        "filename": "elephant.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/African_Bush_Elephant.jpg/320px-African_Bush_Elephant.jpg",
    },
    {
        "filename": "zebra.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Plains_Zebra_Equus_quagga.jpg/320px-Plains_Zebra_Equus_quagga.jpg",
    },
    {
        "filename": "giraffe.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Giraffe_Mikumi_National_Park.jpg/240px-Giraffe_Mikumi_National_Park.jpg",
    },
    {
        "filename": "cheetah.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/TheCheethcat.jpg/320px-TheCheethcat.jpg",
    },
]

SAMPLE_DIR = os.environ.get("SAMPLE_DIR", "./data/images/sample")


def ensure_sample_images() -> str:
    """Download sample images if not present. Returns the sample folder path."""
    dest = Path(SAMPLE_DIR)
    dest.mkdir(parents=True, exist_ok=True)

    for img in SAMPLE_IMAGES:
        out = dest / img["filename"]
        if out.exists():
            continue
        try:
            req = urllib.request.Request(img["url"], headers={"User-Agent": "SpeciesNetStudio/0.1"})
            with urllib.request.urlopen(req, timeout=15) as resp, open(out, "wb") as f:
                f.write(resp.read())
            logger.info("Downloaded sample image: %s", img["filename"])
        except Exception as exc:
            logger.warning("Could not download %s: %s", img["filename"], exc)

    return str(dest.resolve())
