from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from cybercam.config.settings import SettingsManager
from cybercam.core.camera import CameraManager


class SettingsView(QWidget):
    # Live зміни — тільки поточний сеанс.
    session_settings_changed = Signal(dict)

    # SAVE — записали на диск.
    settings_saved = Signal()
    camera_device_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._settings = SettingsManager()
        self._loading = False

        self._build_ui()
        self._load_settings()
        self._connect_live_controls()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("pageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("pageContent")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        # ── HEADER ─────────────────────────────

        title = QLabel("SETTINGS")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "Changes are applied live. "
            "Press SAVE SETTINGS to keep them after restart."
        )
        description.setObjectName("sectionDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        # ── CAMERA DEVICE ──────────────────────

        camera_panel = QFrame()
        camera_panel.setObjectName("gesturePanel")

        camera_layout = QVBoxLayout(camera_panel)
        camera_layout.setContentsMargins(20, 20, 20, 20)
        camera_layout.setSpacing(12)

        camera_title = QLabel("CAMERA DEVICE")
        camera_title.setObjectName("tableHeader")

        camera_description = QLabel(
            "Select which camera CyberGesture should use."
        )
        camera_description.setObjectName("sectionDescription")
        camera_description.setWordWrap(True)

        self._camera_combo = QComboBox()

        current_camera_index = int(
            self._settings.get(
                "camera.device_index",
                0,
            )
        )

        available_cameras = (
            CameraManager.find_available_cameras(
                current_index=current_camera_index,
            )
        )

        camera_names = CameraManager.get_camera_names()

        for position, camera_index in enumerate(
            available_cameras
        ):
            if position < len(camera_names):
                camera_name = camera_names[position]
            else:
                camera_name = (
                    f"CAMERA {camera_index + 1}"
                )

            self._camera_combo.addItem(
                camera_name,
                camera_index,
            )

        camera_layout.addWidget(camera_title)
        camera_layout.addWidget(self._camera_combo)
        camera_layout.addWidget(camera_description)

        layout.addWidget(camera_panel)

        # ── SYSTEM ─────────────────────────────

        system_panel = QFrame()
        system_panel.setObjectName("gesturePanel")

        system_layout = QVBoxLayout(system_panel)
        system_layout.setContentsMargins(18, 16, 18, 16)
        system_layout.setSpacing(10)

        system_title = QLabel("SYSTEM")
        system_title.setObjectName("panelTitle")

        self._minimize_to_tray_checkbox = QCheckBox(
            "MINIMIZE TO TRAY WHEN CLOSING"
        )

        system_layout.addWidget(system_title)
        system_layout.addWidget(
            self._minimize_to_tray_checkbox
        )

        layout.addWidget(system_panel)

        # ── VISUALIZATION ──────────────────────

        visualization_panel = QFrame()
        visualization_panel.setObjectName("gesturePanel")

        visualization_layout = QVBoxLayout(
            visualization_panel
        )
        visualization_layout.setContentsMargins(
            20, 20, 20, 20
        )
        visualization_layout.setSpacing(12)

        visualization_title = QLabel("VISUALIZATION")
        visualization_title.setObjectName("tableHeader")

        self._show_zone_checkbox = QCheckBox(
            "SHOW ACTIVATION ZONE"
        )

        visualization_description = QLabel(
            "Show the activation area and hand size "
            "debug information on the camera."
        )
        visualization_description.setObjectName(
            "sectionDescription"
        )
        visualization_description.setWordWrap(True)

        visualization_layout.addWidget(
            visualization_title
        )
        visualization_layout.addWidget(
            self._show_zone_checkbox
        )
        visualization_layout.addWidget(
            visualization_description
        )

        layout.addWidget(visualization_panel)

        # ── ACTIVATION ZONE ────────────────────

        zone_panel = QFrame()
        zone_panel.setObjectName("gesturePanel")

        zone_layout = QVBoxLayout(zone_panel)
        zone_layout.setContentsMargins(20, 20, 20, 20)
        zone_layout.setSpacing(14)

        zone_title = QLabel("ACTIVATION ZONE")
        zone_title.setObjectName("tableHeader")

        zone_description = QLabel(
            "Move and resize the area where the center "
            "of the detected hand must be."
        )
        zone_description.setObjectName(
            "sectionDescription"
        )
        zone_description.setWordWrap(True)

        zone_layout.addWidget(zone_title)
        zone_layout.addWidget(zone_description)

        (
            self._zone_x_slider,
            self._zone_x_value,
        ) = self._create_slider(
            zone_layout,
            "HORIZONTAL POSITION",
            5,
            95,
        )

        (
            self._zone_y_slider,
            self._zone_y_value,
        ) = self._create_slider(
            zone_layout,
            "VERTICAL POSITION",
            5,
            95,
        )

        (
            self._zone_width_slider,
            self._zone_width_value,
        ) = self._create_slider(
            zone_layout,
            "ZONE WIDTH",
            10,
            100,
        )

        (
            self._zone_height_slider,
            self._zone_height_value,
        ) = self._create_slider(
            zone_layout,
            "ZONE HEIGHT",
            10,
            100,
        )

        layout.addWidget(zone_panel)

        # ── ACTIVATION DISTANCE / SIZE ─────────

        size_panel = QFrame()
        size_panel.setObjectName("gesturePanel")

        size_layout = QVBoxLayout(size_panel)
        size_layout.setContentsMargins(20, 20, 20, 20)
        size_layout.setSpacing(14)

        size_title = QLabel("HAND ACTIVATION SIZE")
        size_title.setObjectName("tableHeader")

        size_description = QLabel(
            "Higher values require the hand to appear "
            "larger in the camera before control becomes active."
        )
        size_description.setObjectName(
            "sectionDescription"
        )
        size_description.setWordWrap(True)

        size_layout.addWidget(size_title)
        size_layout.addWidget(size_description)

        (
            self._hand_size_slider,
            self._hand_size_value,
        ) = self._create_slider(
            size_layout,
            "NORMAL HAND",
            5,
            70,
        )

        (
            self._fist_size_slider,
            self._fist_size_value,
        ) = self._create_slider(
            size_layout,
            "FIST",
            5,
            70,
        )

        layout.addWidget(size_panel)

        # ── GESTURE CONTROL ────────────────────

        control_panel = QFrame()
        control_panel.setObjectName("gesturePanel")

        control_layout = QGridLayout(control_panel)
        control_layout.setContentsMargins(
            20, 20, 20, 20
        )
        control_layout.setHorizontalSpacing(20)
        control_layout.setVerticalSpacing(14)

        control_title = QLabel("GESTURE CONTROL")
        control_title.setObjectName("tableHeader")

        control_layout.addWidget(
            control_title,
            0,
            0,
            1,
            2,
        )

        stability_label = QLabel("STABILITY")
        stability_label.setObjectName("gestureName")

        self._stability_spin = QSpinBox()
        self._stability_spin.setRange(100, 2000)
        self._stability_spin.setSingleStep(50)
        self._stability_spin.setSuffix(" ms")

        control_layout.addWidget(
            stability_label,
            1,
            0,
        )
        control_layout.addWidget(
            self._stability_spin,
            1,
            1,
        )

        stability_description = QLabel(
            "How long a gesture must remain stable "
            "before activation."
        )
        stability_description.setObjectName(
            "sectionDescription"
        )
        stability_description.setWordWrap(True)

        control_layout.addWidget(
            stability_description,
            2,
            0,
            1,
            2,
        )

        cooldown_label = QLabel("COOLDOWN")
        cooldown_label.setObjectName("gestureName")

        self._cooldown_spin = QSpinBox()
        self._cooldown_spin.setRange(100, 5000)
        self._cooldown_spin.setSingleStep(100)
        self._cooldown_spin.setSuffix(" ms")

        control_layout.addWidget(
            cooldown_label,
            3,
            0,
        )
        control_layout.addWidget(
            self._cooldown_spin,
            3,
            1,
        )

        cooldown_description = QLabel(
            "Minimum delay between triggered actions."
        )
        cooldown_description.setObjectName(
            "sectionDescription"
        )
        cooldown_description.setWordWrap(True)

        control_layout.addWidget(
            cooldown_description,
            4,
            0,
            1,
            2,
        )

        control_layout.setColumnStretch(0, 1)

        layout.addWidget(control_panel)

        # ── FACE CONTROL ────────────────────────

        face_panel = QFrame()
        face_panel.setObjectName("gesturePanel")

        face_layout = QVBoxLayout(face_panel)
        face_layout.setContentsMargins(20, 20, 20, 20)
        face_layout.setSpacing(14)

        face_title = QLabel("FACE CONTROL")
        face_title.setObjectName("tableHeader")

        face_description = QLabel(
            "Tune facial gesture timing and sensitivity. "
            "Higher sensitivity values require a stronger expression."
        )
        face_description.setObjectName("sectionDescription")
        face_description.setWordWrap(True)

        face_layout.addWidget(face_title)
        face_layout.addWidget(face_description)

        face_timing = QGridLayout()
        face_timing.setHorizontalSpacing(20)
        face_timing.setVerticalSpacing(14)

        face_stability_label = QLabel("FACE STABILITY")
        face_stability_label.setObjectName("gestureName")

        self._face_stability_spin = QSpinBox()
        self._face_stability_spin.setRange(100, 2000)
        self._face_stability_spin.setSingleStep(50)
        self._face_stability_spin.setSuffix(" ms")

        face_timing.addWidget(face_stability_label, 0, 0)
        face_timing.addWidget(self._face_stability_spin, 0, 1)

        face_cooldown_label = QLabel("FACE COOLDOWN")
        face_cooldown_label.setObjectName("gestureName")

        self._face_cooldown_spin = QSpinBox()
        self._face_cooldown_spin.setRange(100, 5000)
        self._face_cooldown_spin.setSingleStep(100)
        self._face_cooldown_spin.setSuffix(" ms")

        face_timing.addWidget(face_cooldown_label, 1, 0)
        face_timing.addWidget(self._face_cooldown_spin, 1, 1)
        face_timing.setColumnStretch(0, 1)

        face_layout.addLayout(face_timing)

        (
            self._smile_threshold_slider,
            self._smile_threshold_value,
        ) = self._create_slider(
            face_layout,
            "SMILE SENSITIVITY",
            10,
            95,
        )

        (
            self._mouth_threshold_slider,
            self._mouth_threshold_value,
        ) = self._create_slider(
            face_layout,
            "MOUTH OPEN SENSITIVITY",
            10,
            95,
        )

        (
            self._eyebrows_threshold_slider,
            self._eyebrows_threshold_value,
        ) = self._create_slider(
            face_layout,
            "EYEBROWS SENSITIVITY",
            10,
            95,
        )

        layout.addWidget(face_panel)

        # ── END OF SCROLLABLE CONTENT ──────────

        layout.addStretch()
        
        scroll.setWidget(content)
        root_layout.addWidget(scroll, 1)
        
        # ── FIXED SAVE BAR ─────────────────────
        
        save_bar = QFrame()
        save_bar.setObjectName("settingsSaveBar")
        
        save_layout = QHBoxLayout(save_bar)
        save_layout.setContentsMargins(20, 12, 20, 12)
        save_layout.setSpacing(16)
        
        self._status_label = QLabel("")
        self._status_label.setObjectName("saveStatus")
        
        self._save_button = QPushButton(
            "SAVE CHANGES"
        )
        self._save_button.setObjectName("saveButton")
        
        self._save_button.clicked.connect(
            self._save_settings
        )
        
        save_layout.addWidget(
            self._status_label,
            1,
        )
        
        save_layout.addWidget(
            self._save_button,
        )
        
        root_layout.addWidget(save_bar)

    def _create_slider(
        self,
        parent_layout,
        title: str,
        minimum: int,
        maximum: int,
    ):
        header = QHBoxLayout()

        label = QLabel(title)
        label.setObjectName("gestureName")

        value_label = QLabel("0%")
        value_label.setObjectName("sliderValue")

        header.addWidget(label)
        header.addStretch()
        header.addWidget(value_label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)

        parent_layout.addLayout(header)
        parent_layout.addWidget(slider)

        return slider, value_label

    def _on_camera_changed(self, index: int):
        if self._loading:
            return

        camera_index = self._camera_combo.itemData(index)

        if camera_index is None:
            return

        self.camera_device_changed.emit(
            int(camera_index)
        )

        self._status_label.setText(
            "● SESSION CHANGES — NOT SAVED"
        )

    def _connect_live_controls(self):
        self._show_zone_checkbox.toggled.connect(
            self._apply_session_settings
        )

        self._camera_combo.currentIndexChanged.connect(
            self._on_camera_changed
        )

        sliders = (
            self._zone_x_slider,
            self._zone_y_slider,
            self._zone_width_slider,
            self._zone_height_slider,
            self._hand_size_slider,
            self._fist_size_slider,
            self._smile_threshold_slider,
            self._mouth_threshold_slider,
            self._eyebrows_threshold_slider,
        )

        for slider in sliders:
            slider.valueChanged.connect(
                self._apply_session_settings
            )

        self._stability_spin.valueChanged.connect(
            self._apply_session_settings
        )

        self._cooldown_spin.valueChanged.connect(
            self._apply_session_settings
        )

        self._face_stability_spin.valueChanged.connect(
            self._apply_session_settings
        )

        self._face_cooldown_spin.valueChanged.connect(
            self._apply_session_settings
        )

    def _load_settings(self):
        self._loading = True

        camera_index = int(
            self._settings.get(
                "camera.device_index",
                0,
            )
        )

        combo_index = self._camera_combo.findData(
            camera_index
        )

        if combo_index >= 0:
            self._camera_combo.setCurrentIndex(
                combo_index
            )

        self._minimize_to_tray_checkbox.setChecked(
            bool(
                self._settings.get(
                    "app.minimize_to_tray",
                    False,
                )
            )
        )

        self._settings.load()

        self._show_zone_checkbox.setChecked(
            self._settings.get(
                "gesture_control.show_activation_zone",
                False,
            )
        )

        min_x = self._settings.get(
            "gesture_control.activation_zone.min_x",
            0.30,
        )
        max_x = self._settings.get(
            "gesture_control.activation_zone.max_x",
            0.70,
        )
        min_y = self._settings.get(
            "gesture_control.activation_zone.min_y",
            0.25,
        )
        max_y = self._settings.get(
            "gesture_control.activation_zone.max_y",
            0.75,
        )

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        zone_width = max_x - min_x
        zone_height = max_y - min_y

        self._zone_x_slider.setValue(
            round(center_x * 100)
        )
        self._zone_y_slider.setValue(
            round(center_y * 100)
        )
        self._zone_width_slider.setValue(
            round(zone_width * 100)
        )
        self._zone_height_slider.setValue(
            round(zone_height * 100)
        )

        hand_width = self._settings.get(
            "gesture_control.activation_zone.min_hand_width",
            0.25,
        )

        fist_width = self._settings.get(
            "gesture_control.activation_zone.min_fist_width",
            0.18,
        )

        self._hand_size_slider.setValue(
            round(hand_width * 100)
        )

        self._fist_size_slider.setValue(
            round(fist_width * 100)
        )

        self._stability_spin.setValue(
            self._settings.get(
                "gesture_control.stability_ms",
                350,
            )
        )

        self._cooldown_spin.setValue(
            self._settings.get(
                "gesture_control.cooldown_ms",
                1000,
            )
        )

        self._face_stability_spin.setValue(
            self._settings.get(
                "face_control.stability_ms",
                400,
            )
        )

        self._face_cooldown_spin.setValue(
            self._settings.get(
                "face_control.cooldown_ms",
                1000,
            )
        )

        self._smile_threshold_slider.setValue(
            round(
                self._settings.get(
                    "face_control.smile_threshold",
                    0.60,
                ) * 100
            )
        )

        self._mouth_threshold_slider.setValue(
            round(
                self._settings.get(
                    "face_control.mouth_open_threshold",
                    0.50,
                ) * 100
            )
        )

        self._eyebrows_threshold_slider.setValue(
            round(
                self._settings.get(
                    "face_control.eyebrows_up_threshold",
                    0.65,
                ) * 100
            )
        )

        self._update_value_labels()

        self._loading = False

    def _calculate_zone(self):
        center_x = (
            self._zone_x_slider.value() / 100.0
        )

        center_y = (
            self._zone_y_slider.value() / 100.0
        )

        zone_width = (
            self._zone_width_slider.value() / 100.0
        )

        zone_height = (
            self._zone_height_slider.value() / 100.0
        )

        half_width = zone_width / 2
        half_height = zone_height / 2

        center_x = max(
            half_width,
            min(1.0 - half_width, center_x),
        )

        center_y = max(
            half_height,
            min(1.0 - half_height, center_y),
        )

        min_x = center_x - half_width
        max_x = center_x + half_width

        min_y = center_y - half_height
        max_y = center_y + half_height

        return min_x, max_x, min_y, max_y

    def _build_session_settings(self) -> dict:
        min_x, max_x, min_y, max_y = (
            self._calculate_zone()
        )

        hand_width = (
            self._hand_size_slider.value() / 100.0
        )

        fist_width = (
            self._fist_size_slider.value() / 100.0
        )

        # Зберігаємо співвідношення поточних
        # width/height threshold.
        hand_height = min(
            1.0,
            hand_width * 1.68,
        )

        fist_height = min(
            1.0,
            fist_width * 1.39,
        )

        return {
            "show_activation_zone":
                self._show_zone_checkbox.isChecked(),

            "stability_ms":
                self._stability_spin.value(),

            "cooldown_ms":
                self._cooldown_spin.value(),

            "face_control": {
                "stability_ms":
                    self._face_stability_spin.value(),

                "cooldown_ms":
                    self._face_cooldown_spin.value(),

                "smile_threshold":
                    round(
                        self._smile_threshold_slider.value()
                        / 100.0,
                        2,
                    ),

                "mouth_open_threshold":
                    round(
                        self._mouth_threshold_slider.value()
                        / 100.0,
                        2,
                    ),

                "eyebrows_up_threshold":
                    round(
                        self._eyebrows_threshold_slider.value()
                        / 100.0,
                        2,
                    ),
            },

            "activation_zone": {
                "min_x": round(min_x, 3),
                "max_x": round(max_x, 3),
                "min_y": round(min_y, 3),
                "max_y": round(max_y, 3),

                "min_hand_width":
                    round(hand_width, 3),

                "min_hand_height":
                    round(hand_height, 3),

                "min_fist_width":
                    round(fist_width, 3),

                "min_fist_height":
                    round(fist_height, 3),
            },
        }

    def _apply_session_settings(self, *args):
        if self._loading:
            return

        self._update_value_labels()

        session_settings = (
            self._build_session_settings()
        )

        # НІЧОГО НЕ ЗАПИСУЄМО НА ДИСК.
        self.session_settings_changed.emit(
            session_settings
        )

        self._status_label.setText(
            "● SESSION CHANGES — NOT SAVED"
        )

    def _update_value_labels(self):
        self._zone_x_value.setText(
            f"{self._zone_x_slider.value()}%"
        )

        self._zone_y_value.setText(
            f"{self._zone_y_slider.value()}%"
        )

        self._zone_width_value.setText(
            f"{self._zone_width_slider.value()}%"
        )

        self._zone_height_value.setText(
            f"{self._zone_height_slider.value()}%"
        )

        self._hand_size_value.setText(
            f"{self._hand_size_slider.value()}%"
        )

        self._fist_size_value.setText(
            f"{self._fist_size_slider.value()}%"
        )

        self._smile_threshold_value.setText(
            f"{self._smile_threshold_slider.value()}%"
        )

        self._mouth_threshold_value.setText(
            f"{self._mouth_threshold_slider.value()}%"
        )

        self._eyebrows_threshold_value.setText(
            f"{self._eyebrows_threshold_slider.value()}%"
        )

    def _save_settings(self):
        session = self._build_session_settings()

        self._settings.set(
            "app.minimize_to_tray",
            self._minimize_to_tray_checkbox.isChecked(),
        )

        self._settings.set(
            "camera.device_index",
            self._camera_combo.currentData(),
        )

        self._settings.set(
            "gesture_control.show_activation_zone",
            session["show_activation_zone"],
        )

        self._settings.set(
            "gesture_control.stability_ms",
            session["stability_ms"],
        )

        self._settings.set(
            "gesture_control.cooldown_ms",
            session["cooldown_ms"],
        )

        face_control = session["face_control"]

        for key, value in face_control.items():
            self._settings.set(
                f"face_control.{key}",
                value,
            )

        zone = session["activation_zone"]

        for key, value in zone.items():
            self._settings.set(
                f"gesture_control.activation_zone.{key}",
                value,
            )

        # ТІЛЬКИ ТУТ записуємо settings.json.
        self._settings.save()

        self._status_label.setText(
            "✓ SETTINGS SAVED"
        )

        self.settings_saved.emit()