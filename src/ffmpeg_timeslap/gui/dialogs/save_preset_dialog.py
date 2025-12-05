"""Dialog for saving encoding presets."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from typing import Tuple, Optional


class SavePresetDialog(QDialog):
    """Dialog for saving a new encoding preset."""

    def __init__(self, parent=None):
        """Initialize dialog."""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        self.setWindowTitle("Preset speichern")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form
        form_layout = QFormLayout()

        # Preset name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("z.B. Mein YouTube Preset")
        form_layout.addRow("Name:*", self.name_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "Optional: Beschreibung des Presets..."
        )
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Beschreibung:", self.description_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Speichern")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.on_save_clicked)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def on_save_clicked(self):
        """Handle save button click."""
        name = self.name_edit.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Name erforderlich",
                "Bitte geben Sie einen Namen für das Preset ein."
            )
            self.name_edit.setFocus()
            return

        # Validate name (no special characters in filename)
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in name for char in invalid_chars):
            QMessageBox.warning(
                self,
                "Ungültiger Name",
                f"Der Name darf keine dieser Zeichen enthalten: {' '.join(invalid_chars)}"
            )
            self.name_edit.setFocus()
            return

        self.accept()

    def get_preset_data(self) -> Tuple[str, str]:
        """
        Get preset name and description.

        Returns:
            Tuple of (name, description)
        """
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        return (name, description)


def show_save_preset_dialog(parent=None) -> Optional[Tuple[str, str]]:
    """
    Show save preset dialog and return data.

    Args:
        parent: Parent widget

    Returns:
        Tuple of (name, description) or None if cancelled
    """
    dialog = SavePresetDialog(parent)

    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_preset_data()

    return None
