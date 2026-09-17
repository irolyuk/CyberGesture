from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum


class FaceGesture(str, Enum):
    SMILE = "SMILE"
    MOUTH_OPEN = "MOUTH_OPEN"
    EYEBROWS_UP = "EYEBROWS_UP"
    UNKNOWN = "UNKNOWN"


@dataclass
class FaceGestureResult:
    detected: FaceGesture
    stable: FaceGesture
    stable_for_ms: int
    triggered: bool


class FaceGestureEngine:
    def __init__(
        self,
        stability_ms: int = 400,
        cooldown_ms: int = 1000,
        smile_threshold: float = 0.60,
        mouth_open_threshold: float = 0.50,
        eyebrows_up_threshold: float = 0.65,
    ):
        self._stability_ms = stability_ms
        self._cooldown_ms = cooldown_ms

        self._smile_threshold = smile_threshold
        self._mouth_open_threshold = mouth_open_threshold
        self._eyebrows_up_threshold = eyebrows_up_threshold

        self._candidate = FaceGesture.UNKNOWN
        self._candidate_since = time.monotonic()

        self._stable = FaceGesture.UNKNOWN
        self._last_trigger_time = 0.0

    def process(
        self,
        face_blendshapes,
    ) -> FaceGestureResult:
        now = time.monotonic()

        detected = self._classify(
            face_blendshapes
        )

        if detected != self._candidate:
            self._candidate = detected
            self._candidate_since = now

        stable_for_ms = int(
            (now - self._candidate_since) * 1000
        )

        triggered = False

        if (
            detected != FaceGesture.UNKNOWN
            and stable_for_ms >= self._stability_ms
        ):
            if detected != self._stable:
                self._stable = detected

                time_since_last_trigger = (
                    now - self._last_trigger_time
                ) * 1000

                if (
                    time_since_last_trigger
                    >= self._cooldown_ms
                ):
                    triggered = True
                    self._last_trigger_time = now

        if detected == FaceGesture.UNKNOWN:
            self._stable = FaceGesture.UNKNOWN

        return FaceGestureResult(
            detected=detected,
            stable=self._stable,
            stable_for_ms=stable_for_ms,
            triggered=triggered,
        )

    def reset(self) -> None:
        self._candidate = FaceGesture.UNKNOWN
        self._stable = FaceGesture.UNKNOWN
        self._candidate_since = time.monotonic()

    def update_settings(
        self,
        stability_ms: int | None = None,
        cooldown_ms: int | None = None,
        smile_threshold: float | None = None,
        mouth_open_threshold: float | None = None,
        eyebrows_up_threshold: float | None = None,
    ) -> None:
        if stability_ms is not None:
            self._stability_ms = max(
                0,
                int(stability_ms),
            )

        if cooldown_ms is not None:
            self._cooldown_ms = max(
                0,
                int(cooldown_ms),
            )

        if smile_threshold is not None:
            self._smile_threshold = float(
                smile_threshold
            )

        if mouth_open_threshold is not None:
            self._mouth_open_threshold = float(
                mouth_open_threshold
            )

        if eyebrows_up_threshold is not None:
            self._eyebrows_up_threshold = float(
                eyebrows_up_threshold
            )

    def _classify(
        self,
        face_blendshapes,
    ) -> FaceGesture:
        if not face_blendshapes:
            return FaceGesture.UNKNOWN

        scores = self._get_scores(
            face_blendshapes
        )

        smile = (
            scores.get(
                "mouthSmileLeft",
                0.0,
            )
            + scores.get(
                "mouthSmileRight",
                0.0,
            )
        ) / 2.0

        mouth_open = scores.get(
            "jawOpen",
            0.0,
        )

        eyebrows_up = max(
            scores.get(
                "browInnerUp",
                0.0,
            ),
            scores.get(
                "browOuterUpLeft",
                0.0,
            ),
            scores.get(
                "browOuterUpRight",
                0.0,
            ),
        )

        # Priority matters when several expressions
        # happen at the same time.
        if (
            mouth_open
            >= self._mouth_open_threshold
        ):
            return FaceGesture.MOUTH_OPEN

        if (
            smile
            >= self._smile_threshold
        ):
            return FaceGesture.SMILE

        # Suppress eyebrow recognition while the mouth is noticeably open.
        # This prevents jaw movement from being misread as EYEBROWS_UP when
        # jawOpen briefly falls just below the MOUTH_OPEN threshold.
        eyebrow_mouth_guard = (
            self._mouth_open_threshold * 0.70
        )

        if (
            mouth_open < eyebrow_mouth_guard
            and eyebrows_up >= self._eyebrows_up_threshold
        ):
            return FaceGesture.EYEBROWS_UP

        return FaceGesture.UNKNOWN

    @staticmethod
    def _get_scores(
        face_blendshapes,
    ) -> dict[str, float]:
        scores = {}

        for category in face_blendshapes:
            name = category.category_name

            if not name:
                continue

            scores[name] = float(
                category.score
            )

        return scores