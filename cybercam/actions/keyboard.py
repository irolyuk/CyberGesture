from __future__ import annotations

import ctypes

from cybercam.core.action_engine import (
    Action,
    ActionEngine,
    ActionType,
)


KEYEVENTF_KEYUP = 0x0002

VK_CODES = {
    "CTRL": 0x11,
    "SHIFT": 0x10,
    "ALT": 0x12,
    "WIN": 0x5B,

    "A": 0x41,
    "B": 0x42,
    "C": 0x43,
    "D": 0x44,
    "E": 0x45,
    "F": 0x46,
    "G": 0x47,
    "H": 0x48,
    "I": 0x49,
    "J": 0x4A,
    "K": 0x4B,
    "L": 0x4C,
    "M": 0x4D,
    "N": 0x4E,
    "O": 0x4F,
    "P": 0x50,
    "Q": 0x51,
    "R": 0x52,
    "S": 0x53,
    "T": 0x54,
    "U": 0x55,
    "V": 0x56,
    "W": 0x57,
    "X": 0x58,
    "Y": 0x59,
    "Z": 0x5A,

    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,

    "SPACE": 0x20,
    "ENTER": 0x0D,
    "ESC": 0x1B,
    "TAB": 0x09,
}


def _key_down(key_code: int) -> None:
    ctypes.windll.user32.keybd_event(
        key_code,
        0,
        0,
        0,
    )


def _key_up(key_code: int) -> None:
    ctypes.windll.user32.keybd_event(
        key_code,
        0,
        KEYEVENTF_KEYUP,
        0,
    )


def _execute_hotkey(action: Action) -> None:
    if not action.value:
        return

    key_names = [
        key.strip().upper()
        for key in action.value.split("+")
        if key.strip()
    ]

    key_codes = []

    for key_name in key_names:
        key_code = VK_CODES.get(key_name)

        if key_code is None:
            raise ValueError(
                f"Unsupported key: {key_name}"
            )

        key_codes.append(key_code)

    for key_code in key_codes:
        _key_down(key_code)

    for key_code in reversed(key_codes):
        _key_up(key_code)


def register_keyboard_actions(
    engine: ActionEngine,
) -> None:
    engine.register_handler(
        ActionType.HOTKEY,
        _execute_hotkey,
    )