from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QMenu,
    QApplication,
    QSystemTrayIcon,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
)
from cybercam.ui.gestures_view import GesturesView
from cybercam.ui.face_view import FaceView
from cybercam.ui.camera_view import CameraWorker
from cybercam.ui.actions_view import ActionsView
from cybercam.ui.settings_window import SettingsView
from cybercam.config.settings import SettingsManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._camera_worker: CameraWorker | None = None

        self.setWindowTitle("CyberGesture")

        assets_dir = Path(__file__).resolve().parents[2] / "assets" / "icons"
        self._logo_path = assets_dir / "logo.png"
        self._icon_path = assets_dir / "icon.ico"

        if self._icon_path.exists():
            self.setWindowIcon(QIcon(str(self._icon_path)))
        self.resize(1280, 820)
        self.setMinimumSize(640, 480)

        self._build_ui()
        self._apply_style()
        self._force_exit = False
        self._setup_tray()
        self._start_camera()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # ── HEADER ─────────────────────────────

        header = QHBoxLayout()

        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(10)

        self._logo_label = QLabel()
        self._logo_label.setObjectName("appLogo")
        self._logo_label.setFixedSize(50, 50)
        self._logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self._logo_path.exists():
            logo_pixmap = QPixmap(str(self._logo_path))
            self._logo_label.setPixmap(
                logo_pixmap.scaled(
                    self._logo_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        title = QLabel("CYBERGESTURE")
        title.setObjectName("title")

        brand_layout.addWidget(self._logo_label)
        brand_layout.addWidget(title)

        self._status_label = QLabel("● INITIALIZING")
        self._status_label.setObjectName("status")

        header.addLayout(brand_layout)
        header.addStretch()
        header.addWidget(self._status_label)

        main_layout.addLayout(header)

        # ── CAMERA ─────────────────────────────

        self._camera_frame = QFrame()
        self._camera_frame.setObjectName("cameraFrame")

        camera_layout = QVBoxLayout(self._camera_frame)
        camera_layout.setContentsMargins(2, 2, 2, 2)

        self._camera_label = QLabel("WAITING FOR CAMERA...")
        self._camera_label.setObjectName("camera")
        self._camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._camera_label.setMinimumSize(
            0,
            0,
        )

        self._camera_label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Ignored,
        )

        camera_layout.addWidget(self._camera_label)

        self._gestures_view = GesturesView()
        self._face_view = FaceView()
        self._actions_view = ActionsView()
        self._settings_view = SettingsView()

        self._actions_view.action_added.connect(
            self._on_actions_changed
        )

        self._gestures_view.settings_saved.connect(
            self._reload_camera_settings
        )

        self._face_view.settings_saved.connect(
            self._reload_camera_settings
        )

        self._settings_view.camera_device_changed.connect(
            self._switch_camera
        )

        self._settings_view.settings_saved.connect(
            self._reload_camera_settings
        )

        self._settings_view.session_settings_changed.connect(
            self._apply_session_settings
        )

        self._pages = QStackedWidget()

        self._pages.addWidget(
            self._camera_frame
        )

        self._pages.addWidget(
            self._gestures_view
        )

        self._pages.addWidget(
            self._face_view
        )

        self._pages.addWidget(
            self._actions_view
        )

        self._pages.addWidget(
            self._settings_view
        )

        self._pages.setCurrentWidget(
            self._camera_frame
        )

        main_layout.addWidget(
            self._pages,
            1,
        )

        # ── INFO BAR ───────────────────────────

        info_layout = QGridLayout()

        info_layout.setHorizontalSpacing(12)
        info_layout.setVerticalSpacing(6)

        self._camera_info = QLabel(
            "CAMERA  01"
        )

        self._face_info = QLabel(
            "FACE  --"
        )

        self._hands_info = QLabel(
            "HANDS  --"
        )

        self._gesture_info = QLabel(
            "GESTURE  --"
        )

        self._control_info = QLabel(
            "HAND  ● PASSIVE"
        )

        info_layout.addWidget(
            self._camera_info,
            0,
            0,
        )

        info_layout.addWidget(
            self._face_info,
            0,
            1,
        )

        info_layout.addWidget(
            self._hands_info,
            0,
            2,
        )

        info_layout.addWidget(
            self._gesture_info,
            1,
            0,
            1,
            2,
        )

        info_layout.addWidget(
            self._control_info,
            1,
            2,
        )

        main_layout.addLayout(
            info_layout
        )

        # ── NAVIGATION ─────────────────────────

        nav_layout = QHBoxLayout()

        self._camera_button = QPushButton("CAMERA")
        self._gestures_button = QPushButton("GESTURES")
        self._face_button = QPushButton("FACE")
        self._actions_button = QPushButton("ACTIONS")
        self._settings_button = QPushButton("SETTINGS")

        self._camera_button.clicked.connect(
            self._show_camera
        )

        self._gestures_button.clicked.connect(
            self._show_gestures
        )

        self._face_button.clicked.connect(
            self._show_face
        )

        self._actions_button.clicked.connect(
            self._show_actions
        )

        self._settings_button.clicked.connect(
            self._show_settings
        )

        self._camera_button.setProperty("active", True)

        nav_layout.addWidget(
            self._camera_button,
            1,
        )

        nav_layout.addWidget(
            self._gestures_button,
            1,
        )

        nav_layout.addWidget(
            self._face_button,
            1,
        )

        nav_layout.addWidget(
            self._actions_button,
            1,
        )

        nav_layout.addWidget(
            self._settings_button,
            1,
        )

        main_layout.addLayout(nav_layout)

        footer = QLabel("Created by Ivan Roliuk")
        footer.setObjectName("footer")
        footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        main_layout.addWidget(footer)

    def _setup_tray(self):
        self._tray_icon = QSystemTrayIcon(self)

        if self._icon_path.exists():
            self._tray_icon.setIcon(
                QIcon(str(self._icon_path))
            )
        else:
            self._tray_icon.setIcon(
                self.windowIcon()
            )

        self._tray_icon.setToolTip("CyberGesture")

        tray_menu = QMenu(self)

        open_action = QAction(
            "Open CyberGesture",
            self,
        )
        open_action.triggered.connect(
            self._restore_from_tray
        )

        exit_action = QAction(
            "Exit",
            self,
        )
        exit_action.triggered.connect(
            self._exit_from_tray
        )

        tray_menu.addAction(open_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)

        self._tray_icon.setContextMenu(
            tray_menu
        )

        self._tray_icon.activated.connect(
            self._on_tray_activated
        )

        self._tray_icon.show()


    def _restore_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()


    def _on_tray_activated(
        self,
        reason: QSystemTrayIcon.ActivationReason,
    ):
        if (
            reason
            == QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            self._restore_from_tray()


    def _exit_from_tray(self):
        self._force_exit = True

        if self._camera_worker is not None:
            self._camera_worker.stop()
            self._camera_worker.wait()
            self._camera_worker = None

        if hasattr(self, "_tray_icon"):
            self._tray_icon.hide()

        self.close()

        QApplication.instance().quit()

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #080c0a;
            }

            QWidget {
                color: #9dffb0;
                font-family: Consolas;
                font-size: 14px;
            }

            QLabel#title {
                color: #72ff91;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 4px;
            }

            QLabel#status {
                color: #72ff91;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#appLogo {
                background-color: transparent;
                border: none;
            }

            QLabel#footer {
                color: #376e43;
                font-size: 10px;
                padding: 0px 2px;
            }

            QFrame#cameraFrame {
                background-color: #050806;
                border: 1px solid #244b2e;
            }

            QLabel#camera {
                background-color: #020403;
                color: #376e43;
                border: none;
            }

            QPushButton {
                background-color: #0c130e;
                color: #70c981;

                border: 1px solid #244b2e;
                padding: 10px 18px;

                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #132019;
                border-color: #55a866;
                color: #9dffb0;
            }

            QPushButton[active="true"] {
                background-color: #17301e;
                border-color: #72ff91;
                color: #72ff91;
            }

            QLabel#sectionTitle {
                color: #72ff91;
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 3px;
            }

            QLabel#sectionDescription {
                color: #579b66;
                font-size: 13px;
            }

            QFrame#gesturePanel {
                background-color: #070c09;
                border: 1px solid #244b2e;
            }

            QLabel#tableHeader {
                color: #4f8f5d;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#gestureName {
                color: #9dffb0;
                font-size: 15px;
                font-weight: bold;
            }

            QComboBox {
                background-color: #0c130e;
                color: #9dffb0;
                border: 1px solid #244b2e;
                padding: 8px 12px;                
            }

            QComboBox:hover {
                border-color: #55a866;
            }

            QComboBox::drop-down {
                border: none;
                width: 28px;
            }

            QComboBox QAbstractItemView {
                background-color: #0c130e;
                color: #9dffb0;
                selection-background-color: #17301e;
                selection-color: #72ff91;
                border: 1px solid #244b2e;
            }

            QPushButton#saveButton {
                background-color: #17301e;
                color: #72ff91;
                border: 1px solid #72ff91;
                padding: 12px 20px;
                font-weight: bold;
            }

            QPushButton#saveButton:hover {
                background-color: #21452b;
            }

            QLabel#saveStatus {
                color: #72ff91;
                font-size: 12px;
            }

            QFrame#actionRow {
                background-color: #0a100c;
                border: 1px solid #1c3823;
            }

            QPushButton#deleteButton {
                background-color: #160b0b;
                color: #ff7777;
                border: 1px solid #713333;
                padding: 6px 12px;
                font-weight: bold;
            }

            QPushButton#deleteButton:hover {
                background-color: #281010;
                border-color: #ff7777;
            }

            QScrollArea#pageScroll {
                background-color: transparent;
                border: none;
            }

            QScrollArea#pageScroll > QWidget > QWidget {
                background-color: #080c0a;
            }

            QWidget#pageContent {
                background-color: #080c0a;
            }

            QLineEdit {
                background-color: #0c130e;
                color: #9dffb0;
                border: 1px solid #244b2e;
                padding: 9px 10px;
            }

            QLineEdit:focus {
                border-color: #72ff91;
            }

            QLabel#actionName {
                color: #9dffb0;
                font-size: 14px;
                font-weight: bold;
            }

            QLabel#actionDetails {
                color: #579b66;
                font-size: 12px;
            }

            QLabel#actionsCount {
                color: #72ff91;
                font-size: 12px;
                font-weight: bold;
            }

            QScrollBar:vertical {
                background: #080c0a;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #244b2e;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background: #55a866;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QPushButton#browseButton {
                background-color: #0c130e;
                color: #70c981;
                border: 1px solid #244b2e;
                padding: 8px 12px;
            }

            QPushButton#browseButton:hover {
                background-color: #132019;
                border-color: #72ff91;
                color: #9dffb0;
            }

            QFrame#settingsSaveBar {
                background-color: #0a100c;
                border-top: 1px solid #244b2e;
                border-left: none;
                border-right: none;
                border-bottom: none;
            }

            QFrame#settingsSaveBar QPushButton#saveButton {
                min-width: 160px;
            }

            /* ── SETTINGS ───────────────────────── */

            QFrame#settingsSaveBar {
                background-color: #0a100c;
                border-top: 1px solid #244b2e;
                border-left: none;
                border-right: none;
                border-bottom: none;
            }
            
            QFrame#settingsSaveBar QPushButton#saveButton {
                min-width: 160px;
            }
            
            
            /* ── SETTINGS SLIDERS ───────────────── */
            
            QLabel#sliderValue {
                color: #72ff91;
                font-size: 12px;
                font-weight: bold;
            }
            
            QSlider::groove:horizontal {
                height: 4px;
                background-color: #16241a;
                border: 1px solid #244b2e;
            }
            
            QSlider::sub-page:horizontal {
                background-color: #376e43;
                border: 1px solid #55a866;
            }
            
            QSlider::add-page:horizontal {
                background-color: #101812;
                border: 1px solid #244b2e;
            }
            
            QSlider::handle:horizontal {
                background-color: #72ff91;
                border: 1px solid #9dffb0;
                width: 14px;
                margin: -6px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background-color: #9dffb0;
            }
            
            
            /* ── SETTINGS CHECKBOX ──────────────── */
            
            QCheckBox {
                color: #9dffb0;
                spacing: 10px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: #0c130e;
                border: 1px solid #376e43;
            }
            
            QCheckBox::indicator:unchecked:hover {
                border-color: #72ff91;
            }
            
            QCheckBox::indicator:checked {
                background-color: #72ff91;
                border: 1px solid #72ff91;
            }
            
            
            /* ── SETTINGS SPINBOX ───────────────── */
            
            QSpinBox {
                background-color: #0c130e;
                color: #9dffb0;
                border: 1px solid #244b2e;
                padding: 7px 10px;
                min-width: 100px;
            }
            
            QSpinBox:hover {
                border-color: #55a866;
            }
            
            QSpinBox:focus {
                border-color: #72ff91;
            }
            
            QSpinBox::up-button,
            QSpinBox::down-button {
                background-color: #132019;
                border-left: 1px solid #244b2e;
                width: 18px;
            }
            
            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover {
                background-color: #21452b;
            }
        """)

    def _show_camera(self):
        self._pages.setCurrentWidget(
            self._camera_frame
        )

        self._set_active_nav_button(
            self._camera_button
        )


    def _show_gestures(self):
        self._pages.setCurrentWidget(
            self._gestures_view
        )

        self._set_active_nav_button(
            self._gestures_button
        )

    def _show_face(self):
        self._pages.setCurrentWidget(
            self._face_view
        )

        self._set_active_nav_button(
            self._face_button
        )

    def _show_actions(self):
        self._pages.setCurrentWidget(
            self._actions_view
        )

        self._set_active_nav_button(
            self._actions_button
        )

    def _show_settings(self):
        self._pages.setCurrentWidget(
            self._settings_view
        )

        self._set_active_nav_button(
            self._settings_button
        )

    def _set_active_nav_button(
        self,
        active_button: QPushButton,
    ):
        buttons = (
            self._camera_button,
            self._gestures_button,
            self._face_button,
            self._actions_button,
            self._settings_button,
        )

        for button in buttons:
            button.setProperty(
                "active",
                button is active_button,
            )

            button.style().unpolish(button)
            button.style().polish(button)

    def _apply_session_settings(
        self,
        session_settings: dict,
    ):
        if self._camera_worker is not None:
            self._camera_worker.apply_session_settings(
                session_settings
            )

    def _reload_camera_settings(self):
        if self._camera_worker is not None:
            self._camera_worker.reload_settings()

    def _switch_camera(self, camera_index: int):
        camera_index = int(camera_index)

        # Спочатку повністю зупиняємо стару камеру.
        if self._camera_worker is not None:
            self._camera_worker.stop()
            self._camera_worker.wait()

            self._camera_worker = None

        # Тільки після повного завершення старого worker
        # запускаємо нову камеру.
        self._start_camera(camera_index)

    def _start_camera(
        self,
        camera_index: int | None = None,
    ):
        if camera_index is None:
            settings = SettingsManager()

            camera_index = int(
                settings.get(
                    "camera.device_index",
                    0,
                )
            )

        self._camera_worker = CameraWorker(
            camera_index=camera_index
        )

        self._camera_worker.frame_ready.connect(
            self._update_camera_frame
        )

        self._camera_worker.tracking_updated.connect(
            self._update_tracking
        )

        self._camera_worker.gesture_updated.connect(
            self._update_gesture
        )

        self._camera_worker.face_updated.connect(
            self._update_face
        )

        self._camera_worker.camera_started.connect(
            self._on_camera_started
        )

        self._camera_worker.camera_stopped.connect(
            self._on_camera_stopped
        )

        self._camera_worker.camera_error.connect(
            self._on_camera_error
        )

        self._camera_worker.control_state_updated.connect(
            self._update_control_state
        )

        self._camera_worker.start()

    def _update_camera_frame(self, image: QImage):
        pixmap = QPixmap.fromImage(image)

        pixmap = pixmap.scaled(
            self._camera_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self._camera_label.setPixmap(pixmap)

    def _update_tracking(self, hand_count: int):
        self._hands_info.setText(
            f"HANDS  {hand_count}"
        )

    def _update_gesture(self, gesture: str):
        self._gesture_info.setText(
            f"GESTURE  {gesture}"
        )

    def _update_face(self, face_state: str):
        if face_state == "NONE":
            self._face_info.setText(
                "FACE  -- NONE"
            )
        elif face_state == "TRACKED":
            self._face_info.setText(
                "FACE  ● TRACKED"
            )
        else:
            self._face_info.setText(
                f"FACE  ● {face_state}"
            )

    def _on_camera_started(self):
        self._status_label.setText("● TRACKING ACTIVE")

    def _on_camera_stopped(self):
        self._status_label.setText("● CAMERA OFFLINE")

    def _on_camera_error(self, message: str):
        self._status_label.setText("● CAMERA ERROR")
        self._camera_label.setText(message)

    def _update_control_state(self, active: bool):
        if active:
            self._control_info.setText(
                "HAND  ● ACTIVE"
            )
        else:
            self._control_info.setText(
                "HAND  ● PASSIVE"
            )

    def closeEvent(self, event):
        settings = SettingsManager()

        minimize_to_tray = bool(
            settings.get(
                "app.minimize_to_tray",
                False,
            )
        )

        if (
            minimize_to_tray
            and not self._force_exit
        ):
            event.ignore()
            self.hide()
            return

        if self._camera_worker is not None:
            self._camera_worker.stop()
            self._camera_worker.wait()
            self._camera_worker = None

        if hasattr(self, "_tray_icon"):
            self._tray_icon.hide()

        event.accept()

    def _on_actions_changed(
        self,
        name: str,
        action_type: str,
        value: str,
    ):
        self._gestures_view.reload_settings()
        self._face_view.reload_settings()

        if self._camera_worker is not None:
            self._camera_worker.reload_settings()