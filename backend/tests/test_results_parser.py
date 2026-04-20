import json
import os
import tempfile

from app.services.results_parser import parse_predictions_json

_FIXTURE: dict[str, object] = {
    "predictions": [
        {
            "filepath": "/data/img_01.jpg",
            "prediction": "panthera_leo",
            "prediction_score": 0.92,
            "model_version": "v1.0",
            "classifications": {"classes": ["panthera_leo"], "scores": [0.92]},
            "detections": [{"label": "animal", "conf": 0.95, "bbox": [0.1, 0.2, 0.3, 0.4]}],
        },
        {
            "filepath": "/data/img_02.jpg",
            "prediction": "blank",
            "prediction_score": 0.99,
            "model_version": "v1.0",
            "detections": [],
        },
    ]
}


def test_parse_returns_correct_count() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(_FIXTURE, fh)
        path = fh.name
    try:
        results = parse_predictions_json(path)
        assert len(results) == 2
    finally:
        os.unlink(path)


def test_parse_extracts_label_and_confidence() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(_FIXTURE, fh)
        path = fh.name
    try:
        results = parse_predictions_json(path)
        lion = results[0]
        assert lion.label == "panthera_leo"
        assert abs(lion.confidence - 0.92) < 1e-6
        assert lion.model_version == "v1.0"
    finally:
        os.unlink(path)


def test_parse_normalises_bbox() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(_FIXTURE, fh)
        path = fh.name
    try:
        results = parse_predictions_json(path)
        lion = results[0]
        assert lion.bbox == [0.1, 0.2, 0.3, 0.4]
    finally:
        os.unlink(path)


def test_parse_blank_has_no_bbox() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(_FIXTURE, fh)
        path = fh.name
    try:
        results = parse_predictions_json(path)
        blank = results[1]
        assert blank.bbox is None
    finally:
        os.unlink(path)
