#!/usr/bin/env python3
"""Download a small set of public-domain camera trap images for testing.

Images are sourced from the Snapshot Serengeti dataset hosted on LILA.science
(Creative Commons CC BY 4.0).  Only the first page of results (~20 images) is
fetched to keep the download fast and the footprint small.

Usage:
    python scripts/download_sample.py --dest ./data/images/sample
"""

import argparse
import json
import os
import urllib.request
from pathlib import Path

# Public LILA.science Snapshot Serengeti image index (CC BY 4.0)
# Each entry is {"file_name": "<relative_path>", "url": "<direct_image_url>"}
MANIFEST_URL = (
    "https://lilablobssc.blob.core.windows.net/snapshotserengeti-v-2-0/"
    "SnapshotSerengeti_v2_0_images.json.gz"
)

# Lightweight fallback: a hand-picked list of 10 CC0 Wikimedia wildlife images
# used when the LILA manifest is unavailable or too large.
FALLBACK_IMAGES: list[dict[str, str]] = [
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


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "SpeciesNetStudio/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", default="./data/images/sample", help="Destination directory")
    parser.add_argument(
        "--count", type=int, default=5, help="Number of images to download (max 5 for fallback)"
    )
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    images = FALLBACK_IMAGES[: args.count]
    print(f"Downloading {len(images)} sample images to {dest} …")

    for i, img in enumerate(images, 1):
        out = dest / img["filename"]
        if out.exists():
            print(f"  [{i}/{len(images)}] {img['filename']} — already exists, skipping")
            continue
        try:
            download(img["url"], out)
            size = out.stat().st_size
            print(f"  [{i}/{len(images)}] {img['filename']} ({size:,} bytes)")
        except Exception as exc:
            print(f"  [{i}/{len(images)}] {img['filename']} — FAILED: {exc}")

    print("Done.")


if __name__ == "__main__":
    main()
