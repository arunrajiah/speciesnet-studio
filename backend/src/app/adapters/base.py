from collections.abc import Callable
from typing import Protocol


class InferenceAdapter(Protocol):
    """Contract that every inference backend must satisfy."""

    def run(
        self,
        folder: str,
        output_json: str,
        on_progress: Callable[[dict[str, object]], None],
    ) -> None:
        """Run inference on *folder*, write results to *output_json*.

        Call *on_progress* with a progress dict whenever meaningful work
        has been completed.  Raise on non-zero exit or fatal error.
        """
        ...
