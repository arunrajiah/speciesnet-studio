import json
import os
import sys
import tempfile

import pytest

from app.adapters.subprocess_adapter import SubprocessAdapter


def test_adapter_calls_on_progress_for_slash_lines() -> None:
    """Adapter parses X/Y progress lines from stdout and calls on_progress."""
    script = "import sys\nprint('1/3')\nprint('2/3')\nprint('3/3')\n"
    progress_calls: list[dict[str, object]] = []
    adapter = SubprocessAdapter([sys.executable, "-c", script])
    adapter.run(".", "/dev/null", lambda p: progress_calls.append(p))

    assert len(progress_calls) == 3
    assert progress_calls[0] == {"current": 1, "total": 3}
    assert progress_calls[2] == {"current": 3, "total": 3}


def test_adapter_writes_output_json() -> None:
    """Adapter runs command that writes a JSON file; file exists afterwards."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "preds.json")
        script = f"import json; json.dump({{'predictions':[]}}, open({out!r},'w'))"
        adapter = SubprocessAdapter([sys.executable, "-c", script])
        adapter.run(".", out, lambda _: None)
        assert os.path.exists(out)
        data = json.loads(open(out).read())
        assert data == {"predictions": []}


def test_adapter_raises_on_nonzero_exit() -> None:
    """Adapter raises RuntimeError if the command exits with a non-zero code."""
    adapter = SubprocessAdapter([sys.executable, "-c", "raise SystemExit(1)"])
    with pytest.raises(RuntimeError, match="Adapter exited with code 1"):
        adapter.run(".", "/dev/null", lambda _: None)
