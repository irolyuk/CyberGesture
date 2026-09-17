from __future__ import annotations

import os
from pathlib import Path

from cybercam.core.action_engine import (
    Action,
    ActionEngine,
    ActionType,
)


def _launch_program(action: Action) -> None:
    if not action.value:
        raise ValueError(
            "File, program, or folder path is empty."
        )

    target_path = Path(
        action.value
    ).expanduser()

    if not target_path.exists():
        raise FileNotFoundError(
            f"Path not found: {target_path}"
        )

    os.startfile(
        str(target_path)
    )


def register_launcher_actions(
    engine: ActionEngine,
) -> None:
    engine.register_handler(
        ActionType.LAUNCH_PROGRAM,
        _launch_program,
    )