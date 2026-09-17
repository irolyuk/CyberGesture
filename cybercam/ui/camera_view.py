import cv2

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from cybercam.core.camera import CameraError, CameraManager
from cybercam.core.hand_tracker import HandTracker, HandTrackerError
from cybercam.core.face_tracker import FaceTracker, FaceTrackerError
from cybercam.core.action_engine import (
    Action,
    ActionEngine,
    ActionType,
)
from cybercam.core.gesture_engine import Gesture, GestureEngine
from cybercam.core.face_gesture_engine import (
    FaceGesture,
    FaceGestureEngine,
)
from cybercam.actions.media import register_media_actions
from cybercam.actions.keyboard import register_keyboard_actions
from cybercam.actions.launcher import register_launcher_actions

from cybercam.config.settings import SettingsManager

class CameraWorker(QThread):
    frame_ready = Signal(QImage)
    tracking_updated = Signal(int)
    gesture_updated = Signal(str)
    face_updated = Signal(str)
    control_state_updated = Signal(bool)

    camera_error = Signal(str)
    camera_started = Signal()
    camera_stopped = Signal()

    def __init__(
        self,
        camera_index: int = 0,
        model_path: str = "assets/models/hand_landmarker.task",
        face_model_path: str = "assets/models/face_landmarker.task",
        parent=None,
    ):
        super().__init__(parent)

        self._camera_index = camera_index
        self._model_path = model_path
        self._face_model_path = face_model_path
        self._running = False
        self._reload_settings_requested = False
        self._session_settings = None
        self._face_frame_counter = 0
        self._last_face_result = None

    def run(self):
        camera = CameraManager(
            camera_index=self._camera_index,
            width=1280,
            height=720,
            fps=30,
        )

        tracker = None
        face_tracker = None

        settings = SettingsManager()
        session_settings = None

        stability_ms = settings.get(
            "gesture_control.stability_ms",
            350,
        )

        cooldown_ms = settings.get(
            "gesture_control.cooldown_ms",
            1000,
        )

        gesture_engine = GestureEngine(
            stability_ms=stability_ms,
            cooldown_ms=cooldown_ms,
        )

        face_gesture_engine = FaceGestureEngine(
            stability_ms=settings.get(
                "face_control.stability_ms",
                400,
            ),
            cooldown_ms=settings.get(
                "face_control.cooldown_ms",
                1000,
            ),
            smile_threshold=settings.get(
                "face_control.smile_threshold",
                0.60,
            ),
            mouth_open_threshold=settings.get(
                "face_control.mouth_open_threshold",
                0.50,
            ),
            eyebrows_up_threshold=settings.get(
                "face_control.eyebrows_up_threshold",
                0.65,
            ),
        )

        action_engine = ActionEngine()

        register_media_actions(action_engine)
        register_keyboard_actions(action_engine)
        register_launcher_actions(action_engine)

        gesture_bindings = self._load_gesture_bindings(
            settings
        )

        face_gesture_bindings = self._load_face_gesture_bindings(
            settings
        )

        try:
            camera.start()

            tracker = HandTracker(
                model_path=self._model_path,
                max_hands=2,
            )

            face_tracker = FaceTracker(
                model_path=self._face_model_path,
                max_faces=1,
            )

            self._running = True
            self.camera_started.emit()

            while self._running:
                if self._reload_settings_requested:
                    settings.load()

                    gesture_engine.update_settings(
                        stability_ms=settings.get(
                            "gesture_control.stability_ms",
                            350,
                        ),
                        cooldown_ms=settings.get(
                            "gesture_control.cooldown_ms",
                            1000,
                        ),
                    )

                    face_gesture_engine.update_settings(
                        stability_ms=settings.get(
                            "face_control.stability_ms",
                            400,
                        ),
                        cooldown_ms=settings.get(
                            "face_control.cooldown_ms",
                            1000,
                        ),
                        smile_threshold=settings.get(
                            "face_control.smile_threshold",
                            0.60,
                        ),
                        mouth_open_threshold=settings.get(
                            "face_control.mouth_open_threshold",
                            0.50,
                        ),
                        eyebrows_up_threshold=settings.get(
                            "face_control.eyebrows_up_threshold",
                            0.65,
                        ),
                    )

                    gesture_bindings = self._load_gesture_bindings(
                        settings
                    )

                    face_gesture_bindings = (
                        self._load_face_gesture_bindings(
                            settings
                        )
                    )

                    self._reload_settings_requested = False

                session_settings = self._session_settings

                if session_settings is not None:
                    gesture_engine.update_settings(
                        stability_ms=session_settings.get(
                            "stability_ms",
                            350,
                        ),
                        cooldown_ms=session_settings.get(
                            "cooldown_ms",
                            1000,
                        ),
                    )

                    face_session = session_settings.get(
                        "face_control",
                        {},
                    )

                    face_gesture_engine.update_settings(
                        stability_ms=face_session.get(
                            "stability_ms",
                            400,
                        ),
                        cooldown_ms=face_session.get(
                            "cooldown_ms",
                            1000,
                        ),
                        smile_threshold=face_session.get(
                            "smile_threshold",
                            0.60,
                        ),
                        mouth_open_threshold=face_session.get(
                            "mouth_open_threshold",
                            0.50,
                        ),
                        eyebrows_up_threshold=face_session.get(
                            "eyebrows_up_threshold",
                            0.65,
                        ),
                    )

                frame = camera.read_frame()

                # ── FACE TRACKING ─────────────────
                # Run the heavier face model every second camera frame.
                # Reuse the latest result for drawing between detections.
                self._face_frame_counter += 1

                if (
                    self._last_face_result is None
                    or self._face_frame_counter % 2 == 0
                ):
                    self._last_face_result = face_tracker.process(
                        frame
                    )

                face_result = self._last_face_result

                # ── FACE GESTURE ENGINE ───────────
                if (
                    face_result is not None
                    and face_result.face_blendshapes
                ):
                    face_gesture_result = (
                        face_gesture_engine.process(
                            face_result.face_blendshapes[0]
                        )
                    )
                else:
                    face_gesture_engine.reset()
                    face_gesture_result = None

                if (
                    face_result is not None
                    and face_result.face_landmarks
                ):
                    if (
                        face_gesture_result is not None
                        and face_gesture_result.detected
                        != FaceGesture.UNKNOWN
                    ):
                        self.face_updated.emit(
                            face_gesture_result.detected.value
                        )
                    else:
                        self.face_updated.emit("TRACKED")

                    face_active = self._is_face_in_gesture_zone(
                        face_result.face_landmarks[0],
                        settings,
                        session_settings,
                    )

                    if not face_active:
                        face_gesture_engine.reset()

                    # FACE may still be recognized and shown in the HUD
                    # outside the zone, but actions are allowed only when
                    # the center of the face is inside the activation zone.
                    if (
                        face_active
                        and face_gesture_result is not None
                        and face_gesture_result.triggered
                    ):
                        action = face_gesture_bindings.get(
                            face_gesture_result.stable
                        )

                        if action is not None:
                            action_engine.execute(action)
                else:
                    self.face_updated.emit("NONE")

                # ── HAND TRACKING ─────────────────

                result = tracker.process(frame)

                hand_count = len(result.hand_landmarks)

                self.tracking_updated.emit(hand_count)

                if hand_count > 0:
                    landmarks = result.hand_landmarks[0]

                    gesture_result = gesture_engine.process(
                        result.hand_landmarks
                    )

                    self.gesture_updated.emit(
                        gesture_result.detected.value
                    )

                    # Чи знаходиться рука в активній зоні
                    if gesture_result.detected == Gesture.HEART:
                        hand_active = self._is_heart_in_gesture_zone(
                            result.hand_landmarks,
                            settings,
                            session_settings,
                        )
                    else:
                        hand_active = self._is_hand_in_gesture_zone(
                            landmarks,
                            gesture_result.detected,
                            settings,
                            session_settings,
                        )

                    self.control_state_updated.emit(
                        hand_active
                    )

                    # Виконуємо дію тільки якщо:
                    # 1. рука в активній зоні
                    # 2. жест стабільний
                    # 3. GestureEngine дозволив trigger
                    if (
                        hand_active
                        and gesture_result.triggered
                    ):
                        action = gesture_bindings.get(
                            gesture_result.stable
                        )

                        if action is not None:
                            action_engine.execute(action)

                else:
                    gesture_engine.reset()

                    self.gesture_updated.emit("NONE")
                    self.control_state_updated.emit(False)

                # ── DRAW FACE LANDMARKS ──────────

                self._draw_face_debug(
                    frame,
                    face_result,
                    face_gesture_result,
                )

                # ── DRAW HAND LANDMARKS ──────────

                self._draw_hand_landmarks(
                    frame,
                    result.hand_landmarks,
                )

                show_activation_zone = settings.get(
                    "gesture_control.show_activation_zone",
                    False,
                )

                if session_settings is not None:
                    show_activation_zone = (
                        session_settings.get(
                            "show_activation_zone",
                            show_activation_zone,
                        )
                    )

                if show_activation_zone:
                    self._draw_activation_zone(
                        frame,
                        settings,
                        result.hand_landmarks,
                        session_settings,
                    )

                # ── FRAME → QT IMAGE ─────────────

                frame_rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

                height, width, channels = frame_rgb.shape
                bytes_per_line = channels * width

                image = QImage(
                    frame_rgb.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                ).copy()

                self.frame_ready.emit(image)

        except (CameraError, HandTrackerError, FaceTrackerError) as error:
            self.camera_error.emit(str(error))

        except Exception as error:
            self.camera_error.emit(
                f"Unexpected camera error: {error}"
            )

        finally:
            self._running = False

            if tracker is not None:
                tracker.close()

            if face_tracker is not None:
                face_tracker.close()

            camera.stop()

            self.camera_stopped.emit()

    @staticmethod
    def _is_face_in_gesture_zone(
        landmarks,
        settings: SettingsManager,
        session_settings: dict | None = None,
    ) -> bool:
        if not landmarks:
            return False

        xs = [landmark.x for landmark in landmarks]
        ys = [landmark.y for landmark in landmarks]

        center_x = (min(xs) + max(xs)) / 2
        center_y = (min(ys) + max(ys)) / 2

        zone_min_x = settings.get(
            "gesture_control.activation_zone.min_x",
            0.30,
        )
        zone_max_x = settings.get(
            "gesture_control.activation_zone.max_x",
            0.70,
        )
        zone_min_y = settings.get(
            "gesture_control.activation_zone.min_y",
            0.25,
        )
        zone_max_y = settings.get(
            "gesture_control.activation_zone.max_y",
            0.75,
        )

        if session_settings is not None:
            zone = session_settings.get(
                "activation_zone",
                {},
            )
            zone_min_x = zone.get("min_x", zone_min_x)
            zone_max_x = zone.get("max_x", zone_max_x)
            zone_min_y = zone.get("min_y", zone_min_y)
            zone_max_y = zone.get("max_y", zone_max_y)

        return (
            zone_min_x <= center_x <= zone_max_x
            and zone_min_y <= center_y <= zone_max_y
        )

    @staticmethod
    def _is_heart_in_gesture_zone(
        hands,
        settings: SettingsManager,
        session_settings: dict | None = None,
    ) -> bool:
        if hands is None or len(hands) < 2:
            return False

        hand_a = hands[0]
        hand_b = hands[1]

        if len(hand_a) != 21 or len(hand_b) != 21:
            return False

        # Усі landmarks обох рук.
        all_landmarks = list(hand_a) + list(hand_b)

        xs = [
            landmark.x
            for landmark in all_landmarks
        ]

        ys = [
            landmark.y
            for landmark in all_landmarks
        ]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        heart_width = max_x - min_x
        heart_height = max_y - min_y

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # ── SAVED SETTINGS ─────────────────

        zone_min_x = settings.get(
            "gesture_control.activation_zone.min_x",
            0.30,
        )

        zone_max_x = settings.get(
            "gesture_control.activation_zone.max_x",
            0.70,
        )

        zone_min_y = settings.get(
            "gesture_control.activation_zone.min_y",
            0.25,
        )

        zone_max_y = settings.get(
            "gesture_control.activation_zone.max_y",
            0.75,
        )

        min_hand_width = settings.get(
            "gesture_control.activation_zone.min_hand_width",
            0.25,
        )

        min_hand_height = settings.get(
            "gesture_control.activation_zone.min_hand_height",
            0.42,
        )

        # ── SESSION OVERRIDE ────────────────

        if session_settings is not None:
            zone = session_settings.get(
                "activation_zone",
                {},
            )

            zone_min_x = zone.get(
                "min_x",
                zone_min_x,
            )

            zone_max_x = zone.get(
                "max_x",
                zone_max_x,
            )

            zone_min_y = zone.get(
                "min_y",
                zone_min_y,
            )

            zone_max_y = zone.get(
                "max_y",
                zone_max_y,
            )

            min_hand_width = zone.get(
                "min_hand_width",
                min_hand_width,
            )

            min_hand_height = zone.get(
                "min_hand_height",
                min_hand_height,
            )

        # Центр серця повинен бути всередині зони.
        inside_center = (
            zone_min_x <= center_x <= zone_max_x
            and zone_min_y <= center_y <= zone_max_y
        )

        # HEART складається з двох рук, тому його bounding box
        # природно ширший. Для distance використовуємо той самий
        # NORMAL HAND threshold.
        large_enough = (
            heart_width >= min_hand_width
            or heart_height >= min_hand_height
        )

        return inside_center and large_enough

    @staticmethod
    def _is_hand_in_gesture_zone(
        landmarks,
        gesture: Gesture,
        settings: SettingsManager,
        session_settings: dict | None = None,
    ) -> bool:
        if landmarks is None or len(landmarks) != 21:
            return False

        xs = [
            landmark.x
            for landmark in landmarks
        ]

        ys = [
            landmark.y
            for landmark in landmarks
        ]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        hand_width = max_x - min_x
        hand_height = max_y - min_y

        center_x = (
            min_x + max_x
        ) / 2

        center_y = (
            min_y + max_y
        ) / 2

        zone_min_x = settings.get(
            "gesture_control.activation_zone.min_x",
            0.30,
        )

        zone_max_x = settings.get(
            "gesture_control.activation_zone.max_x",
            0.70,
        )

        zone_min_y = settings.get(
            "gesture_control.activation_zone.min_y",
            0.25,
        )

        zone_max_y = settings.get(
            "gesture_control.activation_zone.max_y",
            0.75,
        )

        min_hand_width = settings.get(
            "gesture_control.activation_zone.min_hand_width",
            0.25,
        )

        min_hand_height = settings.get(
            "gesture_control.activation_zone.min_hand_height",
            0.42,
        )

        min_fist_width = settings.get(
            "gesture_control.activation_zone.min_fist_width",
            0.18,
        )

        min_fist_height = settings.get(
            "gesture_control.activation_zone.min_fist_height",
            0.25,
        )

        if session_settings is not None:
            zone = session_settings.get(
                "activation_zone",
                {},
            )

            zone_min_x = zone.get(
                "min_x",
                zone_min_x,
            )
            zone_max_x = zone.get(
                "max_x",
                zone_max_x,
            )
            zone_min_y = zone.get(
                "min_y",
                zone_min_y,
            )
            zone_max_y = zone.get(
                "max_y",
                zone_max_y,
            )

            min_hand_width = zone.get(
                "min_hand_width",
                min_hand_width,
            )
            min_hand_height = zone.get(
                "min_hand_height",
                min_hand_height,
            )

            min_fist_width = zone.get(
                "min_fist_width",
                min_fist_width,
            )
            min_fist_height = zone.get(
                "min_fist_height",
                min_fist_height,
            )

        # Рука повинна бути приблизно
        # в центральній частині кадру.
        inside_center = (
            zone_min_x <= center_x <= zone_max_x
            and zone_min_y <= center_y <= zone_max_y
        )

        if gesture == Gesture.FIST:
            large_enough = (
                hand_width >= min_fist_width
                or hand_height >= min_fist_height
            )
        else:
            large_enough = (
                hand_width >= min_hand_width
                or hand_height >= min_hand_height
            )

        return inside_center and large_enough

    @staticmethod
    def _draw_activation_zone(
        frame,
        settings: SettingsManager,
        hands,
        session_settings: dict | None = None,
    ):
        height, width, _ = frame.shape

        zone_min_x = settings.get(
            "gesture_control.activation_zone.min_x",
            0.30,
        )

        zone_max_x = settings.get(
            "gesture_control.activation_zone.max_x",
            0.70,
        )

        zone_min_y = settings.get(
            "gesture_control.activation_zone.min_y",
            0.25,
        )

        zone_max_y = settings.get(
            "gesture_control.activation_zone.max_y",
            0.75,
        )

        if session_settings is not None:
            zone = session_settings.get(
                "activation_zone",
                {},
            )

            zone_min_x = zone.get(
                "min_x",
                zone_min_x,
            )
            zone_max_x = zone.get(
                "max_x",
                zone_max_x,
            )
            zone_min_y = zone.get(
                "min_y",
                zone_min_y,
            )
            zone_max_y = zone.get(
                "max_y",
                zone_max_y,
            )

        # ── ACTIVATION AREA ───────────────────────

        x1 = int(zone_min_x * width)
        y1 = int(zone_min_y * height)

        x2 = int(zone_max_x * width)
        y2 = int(zone_max_y * height)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (70, 180, 100),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            "ACTIVATION ZONE",
            (x1 + 10, y1 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (110, 255, 145),
            1,
            cv2.LINE_AA,
        )

        if not hands:
            return

        # Поки action logic використовує першу руку,
        # debug overlay теж показує першу.
        landmarks = hands[0]

        if len(landmarks) != 21:
            return

        xs = [
            landmark.x
            for landmark in landmarks
        ]

        ys = [
            landmark.y
            for landmark in landmarks
        ]

        min_x = min(xs)
        max_x = max(xs)

        min_y = min(ys)
        max_y = max(ys)

        hand_width = max_x - min_x
        hand_height = max_y - min_y

        center_x = (
            min_x + max_x
        ) / 2

        center_y = (
            min_y + max_y
        ) / 2

        inside_position = (
            zone_min_x <= center_x <= zone_max_x
            and zone_min_y <= center_y <= zone_max_y
        )

        # ── HAND BOUNDING BOX ─────────────────────

        hand_x1 = int(min_x * width)
        hand_y1 = int(min_y * height)

        hand_x2 = int(max_x * width)
        hand_y2 = int(max_y * height)

        cv2.rectangle(
            frame,
            (hand_x1, hand_y1),
            (hand_x2, hand_y2),
            (80, 210, 255),
            1,
            cv2.LINE_AA,
        )

        # ── NORMAL HAND SIZE ──────────────────────

        min_hand_width = settings.get(
            "gesture_control.activation_zone.min_hand_width",
            0.25,
        )

        min_hand_height = settings.get(
            "gesture_control.activation_zone.min_hand_height",
            0.42,
        )

        normal_size_ok = (
            hand_width >= min_hand_width
            or hand_height >= min_hand_height
        )

        # ── FIST SIZE ─────────────────────────────

        min_fist_width = settings.get(
            "gesture_control.activation_zone.min_fist_width",
            0.18,
        )

        min_fist_height = settings.get(
            "gesture_control.activation_zone.min_fist_height",
            0.25,
        )

        if session_settings is not None:
            zone = session_settings.get(
                "activation_zone",
                {},
            )

            min_hand_width = zone.get(
                "min_hand_width",
                min_hand_width,
            )
            min_hand_height = zone.get(
                "min_hand_height",
                min_hand_height,
            )

            min_fist_width = zone.get(
                "min_fist_width",
                min_fist_width,
            )
            min_fist_height = zone.get(
                "min_fist_height",
                min_fist_height,
            )

        fist_size_ok = (
            hand_width >= min_fist_width
            or hand_height >= min_fist_height
        )

        position_text = (
            "OK"
            if inside_position
            else "OUTSIDE"
        )

        hand_text = (
            "OK"
            if normal_size_ok
            else "TOO SMALL"
        )

        fist_text = (
            "OK"
            if fist_size_ok
            else "TOO SMALL"
        )

        # ── DEBUG INFO ────────────────────────────

        text_x = 20
        text_y = 35

        # Dark transparent backing panel for hand debug.
        panel_x = text_x
        panel_y = text_y
        panel_width = 250
        panel_height = 85
        
        overlay = frame.copy()
        
        cv2.rectangle(
            overlay,
            (panel_x - 10, panel_y - 25),
            (
                panel_x - 10 + panel_width,
                panel_y - 25 + panel_height,
            ),
            (0, 0, 0),
            -1,
        )
        
        cv2.addWeighted(
            overlay,
            0.55,
            frame,
            0.45,
            0,
            frame,
        )

        cv2.putText(
            frame,
            f"POSITION: {position_text}",
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (110, 255, 145),
            1,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"HAND SIZE: {hand_text}",
            (text_x, text_y + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (110, 255, 145),
            1,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"FIST SIZE: {fist_text}",
            (text_x, text_y + 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (110, 255, 145),
            1,
            cv2.LINE_AA,
        )

    @staticmethod
    def _draw_face_debug(frame, face_result, face_gesture_result):
        if (
            face_result is None
            or not face_result.face_landmarks
        ):
            return

        height, width, _ = frame.shape
        face = face_result.face_landmarks[0]

        # ── FACE POINT CLOUD ──────────────────────
        for landmark in face:
            x = int(landmark.x * width)
            y = int(landmark.y * height)

            if 0 <= x < width and 0 <= y < height:
                cv2.circle(
                    frame,
                    (x, y),
                    1,
                    (110, 255, 145),
                    -1,
                    cv2.LINE_AA,
                )

        # ── BLENDSHAPE VALUES ─────────────────────
        scores = {}

        if face_result.face_blendshapes:
            for category in face_result.face_blendshapes[0]:
                name = category.category_name
                if name:
                    scores[name] = float(category.score)

        smile = (
            scores.get("mouthSmileLeft", 0.0)
            + scores.get("mouthSmileRight", 0.0)
        ) / 2.0

        jaw_open = scores.get(
            "jawOpen",
            0.0,
        )
        blink_left = scores.get(
            "eyeBlinkLeft",
            0.0,
        )
        blink_right = scores.get(
            "eyeBlinkRight",
            0.0,
        )

        brow_up = max(
            scores.get("browInnerUp", 0.0),
            scores.get("browOuterUpLeft", 0.0),
            scores.get("browOuterUpRight", 0.0),
        )

        panel_width = 280
        panel_y = 34
        line_height = 24

        # FACE HUD stays on the top-right so it never overlaps
        # the hand / activation-zone debug information on the left.
        panel_x = max(
            18,
            width - panel_width - 18,
        )

        if face_gesture_result is None:
            detected_name = "NONE"
            stable_name = "NONE"
            stable_ms = 0
        else:
            detected_name = (
                "NONE"
                if face_gesture_result.detected == FaceGesture.UNKNOWN
                else face_gesture_result.detected.value
            )
            stable_name = (
                "NONE"
                if face_gesture_result.stable == FaceGesture.UNKNOWN
                else face_gesture_result.stable.value
            )
            stable_ms = face_gesture_result.stable_for_ms

        lines = [
            "FACE: DETECTED",
            f"GESTURE: {detected_name}",
            f"STABLE:  {stable_name}",
            f"HOLD:    {stable_ms} ms",
            "",
            f"SMILE:   {smile:.2f}",
            f"JAW OPEN:{jaw_open:>6.2f}",
            f"BLINK L: {blink_left:.2f}",
            f"BLINK R: {blink_right:.2f}",
            f"BROW UP: {brow_up:.2f}",
        ]

        # Dark backing panel for readability.
        panel_height = (
            len(lines) * line_height + 18
        )

        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (panel_x - 10, panel_y - 25),
            (
                panel_x - 10 + panel_width,
                panel_y - 25 + panel_height,
            ),
            (0, 0, 0),
            -1,
        )
        cv2.addWeighted(
            overlay,
            0.55,
            frame,
            0.45,
            0,
            frame,
        )

        for index, text in enumerate(lines):
            y = panel_y + index * line_height

            if not text:
                continue

            cv2.putText(
                frame,
                text,
                (panel_x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (110, 255, 145),
                1,
                cv2.LINE_AA,
            )

    @staticmethod
    def _draw_hand_landmarks(frame, hands):
        height, width, _ = frame.shape

        connections = (
            # Thumb
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),

            # Index
            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),

            # Middle
            (5, 9),
            (9, 10),
            (10, 11),
            (11, 12),

            # Ring
            (9, 13),
            (13, 14),
            (14, 15),
            (15, 16),

            # Pinky
            (13, 17),
            (17, 18),
            (18, 19),
            (19, 20),

            # Palm
            (0, 17),
        )

        for hand in hands:
            points = []

            for landmark in hand:
                x = int(
                    landmark.x * width
                )

                y = int(
                    landmark.y * height
                )

                points.append(
                    (x, y)
                )

            # Connections
            for start, end in connections:
                cv2.line(
                    frame,
                    points[start],
                    points[end],
                    (70, 180, 100),
                    2,
                    cv2.LINE_AA,
                )

            # Landmarks
            for index, point in enumerate(points):
                radius = 5

                # Fingertips
                if index in (
                    4,
                    8,
                    12,
                    16,
                    20,
                ):
                    radius = 7

                cv2.circle(
                    frame,
                    point,
                    radius,
                    (110, 255, 145),
                    -1,
                    cv2.LINE_AA,
                )

                cv2.circle(
                    frame,
                    point,
                    radius + 2,
                    (20, 70, 35),
                    1,
                    cv2.LINE_AA,
                )

    @staticmethod
    def _load_gesture_bindings(
        settings: SettingsManager,
    ) -> dict[Gesture, Action]:
        bindings = {}

        gesture_settings = settings.get(
            "gestures",
            {},
        )

        custom_actions = settings.get(
            "custom_actions",
            {},
        )

        for gesture_name, action_name in gesture_settings.items():
            try:
                gesture = Gesture(
                    gesture_name
                )

                # ── CUSTOM ACTION ────────────────

                if action_name.startswith("CUSTOM:"):
                    action_id = action_name.split(
                        ":",
                        1,
                    )[1]

                    action_data = custom_actions.get(
                        action_id
                    )

                    if action_data is None:
                        print(
                            f"[Settings] Custom action "
                            f"not found: {action_id}"
                        )
                        continue

                    action_type = ActionType(
                        action_data["type"]
                    )

                    bindings[gesture] = Action(
                        type=action_type,
                        value=action_data.get("value"),
                    )

                # ── BUILT-IN ACTION ──────────────

                else:
                    action_type = ActionType(
                        action_name
                    )

                    bindings[gesture] = Action(
                        type=action_type
                    )

            except (ValueError, KeyError) as error:
                print(
                    f"[Settings] Invalid binding: "
                    f"{gesture_name} -> {action_name}: "
                    f"{error}"
                )

        return bindings

    @staticmethod
    def _load_face_gesture_bindings(
        settings: SettingsManager,
    ) -> dict[FaceGesture, Action]:
        bindings = {}

        face_settings = settings.get(
            "face_gestures",
            {},
        )

        custom_actions = settings.get(
            "custom_actions",
            {},
        )

        for gesture_name, action_name in face_settings.items():
            try:
                gesture = FaceGesture(
                    gesture_name
                )

                if action_name == "NONE":
                    continue

                # ── CUSTOM ACTION ────────────────
                if action_name.startswith("CUSTOM:"):
                    action_id = action_name.split(
                        ":",
                        1,
                    )[1]

                    action_data = custom_actions.get(
                        action_id
                    )

                    if action_data is None:
                        print(
                            f"[Settings] Custom face action "
                            f"not found: {action_id}"
                        )
                        continue

                    action_type = ActionType(
                        action_data["type"]
                    )

                    bindings[gesture] = Action(
                        type=action_type,
                        value=action_data.get("value"),
                    )

                # ── BUILT-IN ACTION ──────────────
                else:
                    action_type = ActionType(
                        action_name
                    )

                    bindings[gesture] = Action(
                        type=action_type
                    )

            except (ValueError, KeyError) as error:
                print(
                    f"[Settings] Invalid face binding: "
                    f"{gesture_name} -> {action_name}: "
                    f"{error}"
                )

        return bindings

    def apply_session_settings(
        self,
        session_settings: dict,
    ):
        self._session_settings = session_settings

    def reload_settings(self):
        self._reload_settings_requested = True

    def stop(self):
        self._running = False
        self.wait()