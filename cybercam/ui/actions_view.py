from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from cybercam.config.settings import SettingsManager


class ActionsView(QWidget):
    action_added = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._settings = SettingsManager()

        self._build_ui()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # ── SCROLL AREA ────────────────────────

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

        title = QLabel("CUSTOM ACTIONS")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "Create custom actions that can be assigned to gestures."
        )
        description.setObjectName("sectionDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        # ── CREATE ACTION ──────────────────────

        panel = QFrame()
        panel.setObjectName("gesturePanel")
        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )
        panel_layout.setSpacing(10)

        name_label = QLabel("ACTION NAME")
        name_label.setObjectName("tableHeader")

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText(
            "Example: Show Desktop"
        )

        type_label = QLabel("ACTION TYPE")
        type_label.setObjectName("tableHeader")

        self._type_combo = QComboBox()
        self._type_combo.addItem(
            "Keyboard Hotkey",
            "HOTKEY",
        )

        self._type_combo.addItem(
            "Open File / Program",
            "LAUNCH_PROGRAM",
        )

        self._type_combo.currentIndexChanged.connect(
            self._update_action_type
        )

        self._value_label = QLabel(
            "HOTKEY"
        )
        self._value_label.setObjectName(
            "tableHeader"
        )

        self._value_input = QLineEdit()
        self._value_input.setPlaceholderText(
            "Example: WIN+D"
        )

        self._browse_button = QPushButton(
            "BROWSE FILE"
        )
        self._browse_button.setObjectName(
            "browseButton"
        )
        self._browse_button.clicked.connect(
            self._browse_program
        )
        self._browse_button.hide()

        self._browse_folder_button = QPushButton(
            "BROWSE FOLDER"
        )
        self._browse_folder_button.setObjectName(
            "browseButton"
        )
        self._browse_folder_button.clicked.connect(
            self._browse_folder
        )
        self._browse_folder_button.hide()

        browse_layout = QHBoxLayout()
        browse_layout.setSpacing(8)
        browse_layout.addWidget(self._browse_button)
        browse_layout.addWidget(
            self._browse_folder_button
        )

        self._add_button = QPushButton(
            "ADD ACTION"
        )
        self._add_button.setObjectName(
            "saveButton"
        )

        self._status_label = QLabel("")
        self._status_label.setObjectName(
            "saveStatus"
        )
        self._status_label.setWordWrap(True)

        self._add_button.clicked.connect(
            self._add_action
        )

        panel_layout.addWidget(name_label)
        panel_layout.addWidget(self._name_input)

        panel_layout.addWidget(type_label)
        panel_layout.addWidget(self._type_combo)

        panel_layout.addWidget(self._value_label)
        panel_layout.addWidget(self._value_input)
        panel_layout.addLayout(browse_layout)
        panel_layout.addSpacing(4)
        panel_layout.addWidget(self._add_button)
        panel_layout.addWidget(self._status_label)

        layout.addWidget(panel)

        # ── SAVED ACTIONS ──────────────────────

        saved_header = QHBoxLayout()

        saved_title = QLabel("SAVED ACTIONS")
        saved_title.setObjectName("tableHeader")

        self._actions_count = QLabel("0")
        self._actions_count.setObjectName(
            "actionsCount"
        )

        saved_header.addWidget(saved_title)
        saved_header.addStretch()
        saved_header.addWidget(
            self._actions_count
        )

        layout.addLayout(saved_header)

        self._actions_container = QWidget()

        self._actions_list = QVBoxLayout(
            self._actions_container
        )

        self._actions_list.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self._actions_list.setSpacing(8)

        layout.addWidget(
            self._actions_container
        )

        layout.addStretch()

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

        self._refresh_actions()

    def _update_action_type(self):
        action_type = (
            self._type_combo.currentData()
        )

        if action_type == "HOTKEY":
            self._value_label.setText(
                "HOTKEY"
            )

            self._value_input.setPlaceholderText(
                "Example: WIN+D"
            )

            self._browse_button.hide()
            self._browse_folder_button.hide()

        elif action_type == "LAUNCH_PROGRAM":
            self._value_label.setText(
                "FILE / PROGRAM / FOLDER"
            )

            self._value_input.setPlaceholderText(
                "Select a file, program, or folder..."
            )

            self._browse_button.show()
            self._browse_folder_button.show()


    def _browse_program(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select file or program",
            "",
            "All Files (*)",
        )

        if file_path:
            self._value_input.setText(
                file_path
            )

    def _browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select folder",
            "",
        )
    
        if folder_path:
            self._value_input.setText(folder_path)

    def _refresh_actions(self):
        while self._actions_list.count():
            item = self._actions_list.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        custom_actions = self._settings.get(
            "custom_actions",
            {},
        )

        self._actions_count.setText(
            str(len(custom_actions))
        )

        if not custom_actions:
            empty_label = QLabel(
                "NO CUSTOM ACTIONS"
            )
            empty_label.setObjectName(
                "sectionDescription"
            )

            self._actions_list.addWidget(
                empty_label
            )
            return

        for action_id, action_data in custom_actions.items():
            row = QFrame()
            row.setObjectName("actionRow")

            row.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(
                14,
                12,
                14,
                12,
            )
            row_layout.setSpacing(12)

            # ── ACTION INFO ────────────────────

            info_layout = QVBoxLayout()
            info_layout.setSpacing(3)

            name = action_data.get(
                "name",
                action_id,
            )

            action_type = action_data.get(
                "type",
                "UNKNOWN",
            )

            value = action_data.get(
                "value",
                "",
            )

            name_label = QLabel(name)
            name_label.setObjectName(
                "actionName"
            )
            name_label.setWordWrap(True)

            details_label = QLabel(
                f"{action_type}  ·  {value}"
            )
            details_label.setObjectName(
                "actionDetails"
            )
            details_label.setWordWrap(True)

            info_layout.addWidget(
                name_label
            )
            info_layout.addWidget(
                details_label
            )

            # ── DELETE ─────────────────────────

            delete_button = QPushButton(
                "DELETE"
            )
            delete_button.setObjectName(
                "deleteButton"
            )

            delete_button.setSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed,
            )

            delete_button.clicked.connect(
                lambda checked=False,
                current_id=action_id:
                self._delete_action(
                    current_id
                )
            )

            row_layout.addLayout(
                info_layout,
                1,
            )

            row_layout.addWidget(
                delete_button,
                0,
                Qt.AlignmentFlag.AlignVCenter,
            )

            self._actions_list.addWidget(row)

    def _delete_action(
        self,
        action_id: str,
    ):
        custom_actions = self._settings.get(
            "custom_actions",
            {},
        )

        if action_id not in custom_actions:
            return

        del custom_actions[action_id]

        self._settings.set(
            "custom_actions",
            custom_actions,
        )

        gestures = self._settings.get(
            "gestures",
            {},
        )

        binding_name = (
            f"CUSTOM:{action_id}"
        )

        for gesture_name, action_name in gestures.items():
            if action_name == binding_name:
                self._settings.set(
                    f"gestures.{gesture_name}",
                    "NONE",
                )

        self._settings.save()

        self._status_label.setText(
            "✓ ACTION DELETED"
        )

        self._refresh_actions()

        self.action_added.emit(
            "",
            "",
            "",
        )

    def _add_action(self):
        name = self._name_input.text().strip()

        action_type = (
            self._type_combo.currentData()
        )

        value = (
            self._value_input.text().strip()
        )

        if not name:
            self._status_label.setText(
                "⚠ ACTION NAME REQUIRED"
            )
            return

        if not value:
            if action_type == "LAUNCH_PROGRAM":
                message = "⚠ FILE / PROGRAM / FOLDER REQUIRED"
            else:
                message = "⚠ HOTKEY REQUIRED"

            self._status_label.setText(
                message
            )
            return

        action_id = (
            name.upper()
            .replace(" ", "_")
            .replace("-", "_")
        )

        self._settings.set(
            f"custom_actions.{action_id}",
            {
                "name": name,
                "type": action_type,
                "value": value,
            },
        )

        self._settings.save()

        self.action_added.emit(
            name,
            action_type,
            value,
        )

        self._status_label.setText(
            f"✓ {name} CREATED"
        )

        self._name_input.clear()
        self._value_input.clear()

        self._refresh_actions()