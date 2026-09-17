from __future__ import annotations

import sys
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class FaceTrackerError(RuntimeError):
    pass


class FaceTracker:
    def __init__(
        self,
        model_path: str,
        max_faces: int = 1,
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
        self._timestamp_ms = 0
        self._landmarker = None

        if not self._model_path.exists():
            raise FaceTrackerError(
                f"Face model not found: "
                f"{self._model_path}"
            )

        try:
            base_options = python.BaseOptions(
                model_asset_path=str(
                    self._model_path
                )
            )

            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_faces=max_faces,

                # Нам це знадобиться для міміки.
                output_face_blendshapes=True,

                # 3D transformation matrices
                # зараз не потрібні.
                output_facial_transformation_matrixes=False,
            )

            self._landmarker = (
                vision.FaceLandmarker.create_from_options(
                    options
                )
            )

        except Exception as error:
            raise FaceTrackerError(
                f"Failed to initialize "
                f"FaceTracker: {error}"
            ) from error

    def process(self, frame):
        if self._landmarker is None:
            raise FaceTrackerError(
                "FaceTracker is not initialized."
            )

        if frame is None:
            raise FaceTrackerError(
                "Cannot process an empty frame."
            )

        try:
            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame,
            )

            self._timestamp_ms += 1

            return self._landmarker.detect_for_video(
                mp_image,
                self._timestamp_ms,
            )

        except Exception as error:
            raise FaceTrackerError(
                f"Face tracking failed: {error}"
            ) from error

    def close(self) -> None:
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()