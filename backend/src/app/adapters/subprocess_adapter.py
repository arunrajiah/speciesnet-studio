import json
import logging
import re
import subprocess
from collections.abc import Callable

logger = logging.getLogger(__name__)

# Lines that look like {"current": 3, "total": 10, ...} or "3/10"
_JSON_PROGRESS = re.compile(r"^\s*\{.*\}\s*$")
_SLASH_PROGRESS = re.compile(r"(\d+)\s*/\s*(\d+)")


class SubprocessAdapter:
    """Run an external command and stream progress from its stdout."""

    def __init__(self, command_template: list[str]) -> None:
        self._template = command_template

    def run(
        self,
        folder: str,
        output_json: str,
        on_progress: Callable[[dict[str, object]], None],
    ) -> None:
        """Format the command, execute it, and call *on_progress* per output line."""
        cmd = [
            part.replace("{folder}", folder).replace("{output_json}", output_json)
            for part in self._template
        ]
        logger.info("Running adapter: %s", cmd)

        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        ) as proc:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                progress = _parse_progress(line)
                if progress:
                    on_progress(progress)
                else:
                    logger.debug("adapter: %s", line)

        if proc.returncode != 0:
            raise RuntimeError(
                f"Adapter exited with code {proc.returncode}. Check logs for details."
            )


def _parse_progress(line: str) -> dict[str, object] | None:
    """Try to extract a progress dict from a stdout line."""
    if _JSON_PROGRESS.match(line):
        try:
            data = json.loads(line)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    m = _SLASH_PROGRESS.search(line)
    if m:
        current, total = int(m.group(1)), int(m.group(2))
        return {"current": current, "total": total}

    return None
