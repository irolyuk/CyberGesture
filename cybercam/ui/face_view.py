from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from cybercam.config.settings import SettingsManager


class FaceView(QWidget):
    settings_saved = Signal()

    ACTIONS = {
        "NONE": "None",
        "MEDIA_PLAY_PAUSE": "Play / Pause",
        "MEDIA_NEXT": "Next Track",
        "MEDIA_PREVIOUS": "Previous Track",
        "VOLUME_UP": "Volume Up",
        "VOLUME_DOWN": "Volume Down",
        "VOLUME_MUTE": "Mute",
    }

    GESTURES = {
        "SMILE": "SMILE",
        "MOUTH_OPEN": "MOUTH OPEN",
        "EYEBROWS_UP": "EYEBROWS UP",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._settings = SettingsManager()

        self._combos: dict[
            str,
            QComboBox,
        ] = {}

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        scroll = QScrollArea()
        scroll.setObjectName("pageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        content = QWidget()
        content.setObjectName("pageContent")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )
        layout.setSpacing(18)

        title = QLabel(
            "FACE CONTROL"
        )
        title.setObjectName(
            "sectionTitle"
        )

        description = QLabel(
            "Configure the action executed "
            "by each detected facial gesture."
        )
        description.setObjectName(
            "sectionDescription"
        )
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        panel = QFrame()
        panel.setObjectName(
            "gesturePanel"
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        grid = QGridLayout(panel)

        grid.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)

        gesture_header = QLabel(
            "FACE GESTURE"
        )
        gesture_header.setObjectName(
            "tableHeader"
        )

        action_header = QLabel(
            "ACTION"
        )
        action_header.setObjectName(
            "tableHeader"
        )

        grid.addWidget(
            gesture_header,
            0,
            0,
        )

        grid.addWidget(
            action_header,
            0,
            1,
        )

        # Action column receives available width.
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        for row, (
            gesture_key,
            gesture_name,
        ) in enumerate(
            self.GESTURES.items(),
            start=1,
        ):
            gesture_label = QLabel(
                gesture_name
            )
            gesture_label.setObjectName(
                "gestureName"
            )

            combo = QComboBox()

            combo.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )

            for (
                action_key,
                action_name,
            ) in self.ACTIONS.items():
                combo.addItem(
                    action_name,
                    action_key,
                )

            self._combos[
                gesture_key
            ] = combo

            grid.addWidget(
                gesture_label,
                row,
                0,
            )

            grid.addWidget(
                combo,
                row,
                1,
            )

        layout.addWidget(panel)

        layout.addStretch()

        self._status_label = QLabel("")
        self._status_label.setObjectName(
            "saveStatus"
        )
        self._status_label.setWordWrap(True)

        self._save_button = QPushButton(
            "SAVE CHANGES"
        )
        self._save_button.setObjectName(
            "saveButton"
        )

        self._save_button.clicked.connect(
            self._save_settings
        )

        layout.addWidget(
            self._status_label
        )

        layout.addWidget(
            self._save_button
        )

        scroll.setWidget(content)

        root_layout.addWidget(scroll)

    def _load_settings(self):
        custom_actions = self._settings.get(
            "custom_actions",
            {},
        )

        for (
            gesture,
            combo,
        ) in self._combos.items():

            while (
                combo.count()
                > len(self.ACTIONS)
            ):
                combo.removeItem(
                    combo.count() - 1
                )

            for (
                action_id,
                action_data,
            ) in custom_actions.items():

                name = action_data.get(
                    "name",
                    action_id,
                )

                combo.addItem(
                    name,
                    f"CUSTOM:{action_id}",
                )

            selected_action = (
                self._settings.get(
                    f"face_gestures.{gesture}",
                    "NONE",
                )
            )

            index = combo.findData(
                selected_action
            )

            if index >= 0:
                combo.setCurrentIndex(
                    index
                )

    def _save_settings(self):
        for (
            gesture,
            combo,
        ) in self._combos.items():

            action = (
                combo.currentData()
            )

            self._settings.set(
                f"face_gestures.{gesture}",
                action,
            )

        self._settings.save()

        self._status_label.setText(
            "✓ SETTINGS SAVED"
        )

        self.settings_saved.emit()

    def reload_settings(self):
        self._settings.load()
        self._load_settings()