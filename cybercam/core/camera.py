from __future__ import annotations

import cv2
import json
import subprocess


class CameraError(Exception):
    """Помилка, пов'язана з роботою камери."""


class CameraManager:
    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
    ):
        self._camera_index = camera_index
        self._width = width
        self._height = height
        self._fps = fps

        self._capture: cv2.VideoCapture | None = None

    @property
    def is_running(self) -> bool:
        return self._capture is not None and self._capture.isOpened()

    @staticmethod
    def find_available_cameras(
        current_index: int = 0,
        max_devices: int = 10,
    ) -> list[int]:
        available = [current_index]

        for camera_index in range(max_devices):
            if camera_index == current_index:
                continue

            capture = cv2.VideoCapture(
                camera_index,
                cv2.CAP_MSMF,
            )

            try:
                if capture.isOpened():
                    available.append(camera_index)
            finally:
                capture.release()

        return sorted(set(available))

    @staticmethod
    def get_camera_names() -> list[str]:
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-CimInstance Win32_PnPEntity | "
                "Where-Object { "
                "$_.PNPClass -eq 'Camera' -or "
                "$_.PNPClass -eq 'Image' "
                "} | "
                "Select-Object -ExpandProperty Name | "
                "ConvertTo-Json -Compress"
            ),
        ]
    
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
    
            if result.returncode != 0:
                return []
    
            output = result.stdout.strip()
    
            if not output:
                return []
    
            data = json.loads(output)
    
            if isinstance(data, str):
                return [data]
    
            if isinstance(data, list):
                return [
                    str(name)
                    for name in data
                    if name
                ]
    
        except (
            subprocess.SubprocessError,
            json.JSONDecodeError,
            OSError,
        ):
            pass
        
        return []

    def start(self) -> None:
        if self.is_running:
            return

        capture = cv2.VideoCapture(
            self._camera_index,
            cv2.CAP_MSMF,
        )

        if not capture.isOpened():
            capture.release()
            raise CameraError(
                f"Не вдалося відкрити камеру #{self._camera_index}"
            )

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        capture.set(cv2.CAP_PROP_FPS, self._fps)

        self._capture = capture

    def read_frame(self):
        if not self.is_running:
            raise CameraError("Камера не запущена.")

        success, frame = self._capture.read()

        if not success or frame is None:
            raise CameraError("Не вдалося отримати кадр із камери.")

        return frame

    def stop(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> "CameraManager":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()