from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import time


class Gesture(str, Enum):
    OPEN_PALM = "OPEN_PALM"
    FIST = "FIST"
    VICTORY = "VICTORY"
    POINT = "POINT"
    HEART = "HEART"
    UNKNOWN = "UNKNOWN"


@dataclass
class GestureResult:
    detected: Gesture
    stable: Gesture
    stable_for_ms: int
    triggered: bool


class GestureEngine:
    def __init__(
        self,
        stability_ms: int = 350,
        cooldown_ms: int = 1000,
    ):
        self._stability_ms = stability_ms
        self._cooldown_ms = cooldown_ms

        self._candidate = Gesture.UNKNOWN
        self._candidate_since = time.monotonic()

        self._stable = Gesture.UNKNOWN
        self._last_trigger_time = 0.0

    def process(self, hands) -> GestureResult:
        now = time.monotonic()

        detected = self._classify_hands(hands)

        # Якщо побачили інший жест —
        # починаємо відлік стабільності заново.
        if detected != self._candidate:
            self._candidate = detected
            self._candidate_since = now

        stable_for_ms = int(
            (now - self._candidate_since) * 1000
        )

        triggered = False

        if (
            detected != Gesture.UNKNOWN
            and stable_for_ms >= self._stability_ms
        ):
            if detected != self._stable:
                self._stable = detected

                time_since_last_trigger = (
                    now - self._last_trigger_time
                ) * 1000

                if time_since_last_trigger >= self._cooldown_ms:
                    triggered = True
                    self._last_trigger_time = now

        if detected == Gesture.UNKNOWN:
            self._stable = Gesture.UNKNOWN

        return GestureResult(
            detected=detected,
            stable=self._stable,
            stable_for_ms=stable_for_ms,
            triggered=triggered,
        )

    def reset(self) -> None:
        self._candidate = Gesture.UNKNOWN
        self._stable = Gesture.UNKNOWN
        self._candidate_since = time.monotonic()

    def _classify_hands(self, hands) -> Gesture:
        if not hands:
            return Gesture.UNKNOWN
    
        # Дві руки — спочатку перевіряємо HEART.
        if len(hands) >= 2:
            if self._is_heart(
                hands[0],
                hands[1],
            ):
                return Gesture.HEART
    
            # Якщо дві руки є, але HEART нема —
            # лишаємо стару логіку для першої руки.
            return self._classify(hands[0])
    
        # Одна рука — стара логіка без змін.
        return self._classify(hands[0])
    
    @staticmethod
    def _is_heart(left_hand, right_hand) -> bool:
        if (
            left_hand is None
            or right_hand is None
            or len(left_hand) != 21
            or len(right_hand) != 21
        ):
            return False
    
        # MediaPipe landmarks:
        # 4 = thumb tip
        # 8 = index tip
        # 0 = wrist
        # 9 = middle finger MCP
    
        thumb_a = left_hand[4]
        thumb_b = right_hand[4]
    
        index_a = left_hand[8]
        index_b = right_hand[8]
    
        wrist_a = left_hand[0]
        wrist_b = right_hand[0]
    
        middle_a = left_hand[9]
        middle_b = right_hand[9]
    
        def distance(a, b):
            return (
                (a.x - b.x) ** 2
                + (a.y - b.y) ** 2
            ) ** 0.5
    
        # Розмір кожної долоні.
        palm_a = distance(
            wrist_a,
            middle_a,
        )
    
        palm_b = distance(
            wrist_b,
            middle_b,
        )
    
        average_palm = (
            palm_a + palm_b
        ) / 2
    
        if average_palm <= 0:
            return False
    
        # Нормалізовані відстані.
        thumb_distance = (
            distance(
                thumb_a,
                thumb_b,
            )
            / average_palm
        )
    
        index_distance = (
            distance(
                index_a,
                index_b,
            )
            / average_palm
        )
    
        wrist_distance = (
            distance(
                wrist_a,
                wrist_b,
            )
            / average_palm
        )
    
        # У серці кінчики вказівних мають
        # бути вище кінчиків великих пальців.
        index_center_y = (
            index_a.y + index_b.y
        ) / 2
    
        thumb_center_y = (
            thumb_a.y + thumb_b.y
        ) / 2
    
        index_above_thumbs = (
            index_center_y
            < thumb_center_y
        )
    
        # Кінчики повинні бути достатньо близько,
        # а самі руки — знаходитися поруч.
        return (
            thumb_distance < 0.75
            and index_distance < 0.95
            and wrist_distance < 4.5
            and index_above_thumbs
        )

    def _classify(self, landmarks) -> Gesture:
        if landmarks is None or len(landmarks) != 21:
            return Gesture.UNKNOWN

        fingers = self._get_finger_states(landmarks)

        index = fingers["index"]
        middle = fingers["middle"]
        ring = fingers["ring"]
        pinky = fingers["pinky"]

        # ✋
        if index and middle and ring and pinky:
            return Gesture.OPEN_PALM

        # ✊
        if not index and not middle and not ring and not pinky:
            return Gesture.FIST

        # ✌
        if (
            index
            and middle
            and not ring
            and not pinky
        ):
            return Gesture.VICTORY

        # ☝
        if (
            index
            and not middle
            and not ring
            and not pinky
        ):
            return Gesture.POINT

        return Gesture.UNKNOWN

    @staticmethod
    def _get_finger_states(landmarks) -> dict[str, bool]:
        """
        Для чотирьох пальців визначаємо, чи вони випрямлені.

        MediaPipe:
        менше Y = точка вище на зображенні.
        """

        finger_indices = {
            "index": (6, 8),
            "middle": (10, 12),
            "ring": (14, 16),
            "pinky": (18, 20),
        }

        states = {}

        for name, (pip_index, tip_index) in finger_indices.items():
            pip = landmarks[pip_index]
            tip = landmarks[tip_index]

            states[name] = tip.y < pip.y

        return states

    def update_settings(
        self,
        stability_ms: int,
        cooldown_ms: int,
    ) -> None:
        self._stability_ms = stability_ms
        self._cooldown_ms = cooldown_ms