from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class ActionType(str, Enum):
    NONE = "NONE"

    MEDIA_PLAY_PAUSE = "MEDIA_PLAY_PAUSE"
    MEDIA_NEXT = "MEDIA_NEXT"
    MEDIA_PREVIOUS = "MEDIA_PREVIOUS"

    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    VOLUME_MUTE = "VOLUME_MUTE"

    HOTKEY = "HOTKEY"
    LAUNCH_PROGRAM = "LAUNCH_PROGRAM"


@dataclass
class Action:
    type: ActionType
    value: str | None = None


class ActionEngine:
    def __init__(self):
        self._handlers: dict[
            ActionType,
            Callable[[Action], None]
        ] = {}

    def register_handler(
        self,
        action_type: ActionType,
        handler: Callable[[Action], None],
    ) -> None:
        self._handlers[action_type] = handler

    def execute(self, action: Action) -> bool:
        if action.type == ActionType.NONE:
            return False

        handler = self._handlers.get(action.type)

        if handler is None:
            print(
                f"[ActionEngine] No handler registered "
                f"for {action.type.value}"
            )
            return False

        try:
            handler(action)
            return True

        except Exception as error:
            print(
                f"[ActionEngine] Failed to execute "
                f"{action.type.value}: {error}"
            )
            return False