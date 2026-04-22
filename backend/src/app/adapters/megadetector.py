"""MegaDetector adapter — runs Microsoft's MegaDetector via ``run_detector_batch.py``.

Output JSON shape produced by MegaDetector (different from SpeciesNet)::

    {
        "images": [
            {
                "file": "path/to/image.jpg",
                "detections": [
                    {
                        "category": "1",   # "1"=animal, "2"=person, "3"=vehicle
                        "conf": 0.95,
                        "bbox": [x, y, w, h]  # normalised, COCO-style
                    }
                ],
                "max_detection_conf": 0.95
            }
        ],
        "info": {"detector": "...", "detection_completion_time": "..."}
    }

Note: ``results_parser.py`` currently expects the SpeciesNet prediction format and would
need updating to ingest MegaDetector output.  That is a future task — this adapter is
responsible only for running the process correctly.
"""

from __future__ import annotations

import logging
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)

_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


class MegaDetectorAdapter:
    """Run MegaDetector inference via ``run_detector_batch.py``.

    Args:
        model_path: Absolute path to the MegaDetector model weights file.
        threshold:  Detection confidence threshold (default 0.1).
        python:     Python executable used to invoke the script (default ``"python"``).
    """

    def __init__(
        self,
        model_path: str,
        threshold: float = 0.1,
        python: str = "python",
    ) -> None:
        self._model_path = model_path
        self._threshold = threshold
        self._python = python

    def run(
        self,
        folder: str,
        output_json: str,
        on_progress: Callable[[dict[str, object]], None],
    ) -> None:
        """Run MegaDetector on all jpg/jpeg/png images under *folder*.

        Writes the standard MegaDetector JSON to *output_json*.  Calls
        *on_progress* with ``{"stage": "running", "message": <line>}`` for
        every non-empty line emitted to stdout/stderr.  Raises
        ``RuntimeError`` on a non-zero exit code.
        """
        image_paths = [str(p) for p in Path(folder).rglob("*") if p.suffix.lower() in _IMAGE_EXTS]
        logger.info("MegaDetector: found %d images in %s", len(image_paths), folder)

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp.write("\n".join(image_paths))
            image_list_path = tmp.name

        cmd = [
            self._python,
            "run_detector_batch.py",
            "--model_file",
            self._model_path,
            "--image_file_list",
            image_list_path,
            "--output_file",
            output_json,
            "--threshold",
            str(self._threshold),
        ]
        logger.info("MegaDetector command: %s", cmd)

        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        ) as proc:
            if proc.stdout is None:
                raise RuntimeError("subprocess stdout is None — PIPE not opened")
            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                on_progress({"stage": "running", "message": line})
                logger.debug("megadetector: %s", line)

        if proc.returncode != 0:
            raise RuntimeError(
                f"MegaDetector exited with code {proc.returncode}. Check logs for details."
            )

        logger.info("MegaDetector inference complete: %s", output_json)
