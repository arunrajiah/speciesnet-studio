import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.adapters.speciesnet_adapter import SpeciesNetAdapter


def _make_images(tmp_path: Path, n: int = 3) -> str:
    folder = tmp_path / "images"
    folder.mkdir()
    for i in range(n):
        (folder / f"img{i}.jpg").write_bytes(b"")
    return str(folder)


def _fake_predict(instances_dict, run_mode, progress_bars, predictions_json):  # type: ignore[no-untyped-def]
    Path(predictions_json).write_text(json.dumps({"predictions": []}))


def test_adapter_reports_progress_and_writes_json(tmp_path: Path) -> None:
    folder = _make_images(tmp_path, n=4)
    output_json = str(tmp_path / "out.json")

    mock_model_instance = MagicMock()
    mock_model_instance.predict.side_effect = _fake_predict

    mock_speciesnet = MagicMock()
    mock_speciesnet.SpeciesNet.return_value = mock_model_instance
    mock_speciesnet.DEFAULT_MODEL = "test-model"

    mock_utils = MagicMock()
    mock_utils.prepare_instances_dict.return_value = {}

    progress_calls: list[dict] = []

    with patch.dict(
        "sys.modules",
        {"speciesnet": mock_speciesnet, "speciesnet.utils": mock_utils},
    ):
        SpeciesNetAdapter().run(folder, output_json, progress_calls.append)

    assert len(progress_calls) == 2
    assert progress_calls[0] == {"current": 0, "total": 4}
    assert progress_calls[1] == {"current": 4, "total": 4}
    assert os.path.exists(output_json)


def test_adapter_raises_when_speciesnet_not_installed(tmp_path: Path) -> None:
    folder = _make_images(tmp_path, n=1)
    output_json = str(tmp_path / "out.json")

    with patch.dict("sys.modules", {"speciesnet": None}):
        with pytest.raises(RuntimeError, match="speciesnet is not installed"):
            SpeciesNetAdapter().run(folder, output_json, lambda _: None)
