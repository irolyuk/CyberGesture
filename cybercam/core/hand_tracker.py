from __future__ import annotations

import sys
from pathlib import Path

import cv2
import mediapipe as mp

from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision



class HandTrackerError(Exception):
    """Помилка модуля відстеження рук."""


class HandTracker:
    def __init__(
        self,
        model_path: str | Path,
        max_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        model_path = Path(model_path)

        if model_path.is_absolute():
            self._model_path = model_path
        elif getattr(sys, "frozen", False):
            self._model_path = (
                Path(sys._MEIPASS)
                / model_path
            )
        else:
            project_root = (
                Path(__file__).resolve().parents[2]
            )
            self._model_path = (
                project_root
                / model_path
            )
        self._max_hands = max_hands

        if not self._model_path.exists():
            raise HandTrackerError(
                f"Hand Landmarker model not found: {self._model_path}"
            )

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(self._model_path)
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=self._max_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        try:
            self._landmarker = vision.HandLandmarker.create_from_options(
                options
            )
        except Exception as error:
            raise HandTrackerError(
                f"Failed to initialize Hand Landmarker: {error}"
            ) from error

        self._timestamp_ms = 0

    def process(self, frame):
        if frame is None:
            raise HandTrackerError("Frame is empty.")

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        self._timestamp_ms += 1

        try:
            return self._landmarker.detect_for_video(
                mp_image,
                self._timestamp_ms,
            )
        except Exception as error:
            raise HandTrackerError(
                f"Hand tracking failed: {error}"
            ) from error

    def close(self) -> None:
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None

    def __enter__(self) -> "HandTracker":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()