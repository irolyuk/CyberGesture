from __future__ import annotations

import ctypes

from cybercam.core.action_engine import (
    Action,
    ActionEngine,
    ActionType,
)


KEYEVENTF_KEYUP = 0x0002

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3


def _press_media_key(key_code: int) -> None:
    user32 = ctypes.windll.user32

    user32.keybd_event(
        key_code,
        0,
        0,
        0,
    )

    user32.keybd_event(
        key_code,
        0,
        KEYEVENTF_KEYUP,
        0,
    )


def _play_pause(action: Action) -> None:
    _press_media_key(VK_MEDIA_PLAY_PAUSE)


def _next_track(action: Action) -> None:
    _press_media_key(VK_MEDIA_NEXT_TRACK)


def _previous_track(action: Action) -> None:
    _press_media_key(VK_MEDIA_PREV_TRACK)


def _volume_up(action: Action) -> None:
    _press_media_key(VK_VOLUME_UP)


def _volume_down(action: Action) -> None:
    _press_media_key(VK_VOLUME_DOWN)


def _volume_mute(action: Action) -> None:
    _press_media_key(VK_VOLUME_MUTE)


def register_media_actions(
    engine: ActionEngine,
) -> None:
    engine.register_handler(
        ActionType.MEDIA_PLAY_PAUSE,
        _play_pause,
    )

    engine.register_handler(
        ActionType.MEDIA_NEXT,
        _next_track,
    )

    engine.register_handler(
        ActionType.MEDIA_PREVIOUS,
        _previous_track,
    )

    engine.register_handler(
        ActionType.VOLUME_UP,
        _volume_up,
    )

    engine.register_handler(
        ActionType.VOLUME_DOWN,
        _volume_down,
    )

    engine.register_handler(
        ActionType.VOLUME_MUTE,
        _volume_mute,
    )