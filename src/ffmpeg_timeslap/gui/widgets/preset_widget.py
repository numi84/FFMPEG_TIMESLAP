"""Widget for preset selection and management."""

from PyQt5.QtWidgets import (
    QGroupBox, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal

from ...presets.preset_manager import PresetManager


class PresetWidget(QGroupBox):
    """Widget for selecting and managing presets."""

    # Signals
    preset_loaded = pyqtSignal(str)  # Preset name
    preset_saved = pyqtSignal(str)  # Preset name
    preset_deleted = pyqtSignal(str)  # Preset name

    def __init__(self, preset_manager: PresetManager, parent=None):
        """
        Initialize widget.

        Args:
            preset_manager: PresetManager instance
            parent: Parent widget
        """
        super().__init__("Presets", parent)
        self.preset_manager = preset_manager
        self.setup_ui()
        self.load_presets()

    def setup_ui(self):
        """Setup user interface."""
        layout = QHBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(8, 4, 8, 4)
        self.setLayout(layout)
        self.setMaximumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        # Label
        layout.addWidget(QLabel("Preset:"))

        # Preset dropdown
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(200)
        self.preset_combo.currentTextChanged.connect(self.on_preset_selected)
        layout.addWidget(self.preset_combo)

        # Description label
        self.description_label = QLabel("")
        self.description_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.description_label, 1)  # Stretch factor 1

        # Buttons
        self.load_btn = QPushButton("Laden")
        self.load_btn.clicked.connect(self.load_selected_preset)
        layout.addWidget(self.load_btn)

        self.save_btn = QPushButton("Speichern als...")
        self.save_btn.clicked.connect(self.save_current_preset)
        layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Löschen")
        self.delete_btn.clicked.connect(self.delete_selected_preset)
        layout.addWidget(self.delete_btn)

    def load_presets(self):
        """Load all available presets into dropdown."""
        self.preset_combo.clear()
        self.preset_combo.addItem("-- Kein Preset --", None)

        # Get all presets
        presets = self.preset_manager.get_all_presets()

        for preset_name in presets:
            # Mark default presets
            if self.preset_manager.is_default_preset(preset_name):
                display_name = f"{preset_name} ⭐"
            else:
                display_name = preset_name

            self.preset_combo.addItem(display_name, preset_name)

    def on_preset_selected(self, text: str):
        """
        Handle preset selection change.

        Args:
            text: Selected preset display name
        """
        # Get actual preset name from combo data
        preset_name = self.preset_combo.currentData()

        if preset_name:
            # Load description
            description = self.preset_manager.get_preset_description(preset_name)
            self.description_label.setText(description or "")

            # Enable/disable delete button
            is_default = self.preset_manager.is_default_preset(preset_name)
            self.delete_btn.setEnabled(not is_default)
        else:
            self.description_label.setText("")
            self.delete_btn.setEnabled(False)

    def load_selected_preset(self):
        """Load selected preset and emit signal."""
        preset_name = self.preset_combo.currentData()

        if preset_name:
            self.preset_loaded.emit(preset_name)
            QMessageBox.information(
                self,
                "Preset geladen",
                f"Preset '{preset_name}' wurde geladen."
            )
        else:
            QMessageBox.warning(
                self,
                "Kein Preset gewählt",
                "Bitte wählen Sie ein Preset aus der Liste."
            )

    def save_current_preset(self):
        """Save current configuration as preset (shows dialog)."""
        # This will be handled by main window with a dialog
        # For now, just emit signal
        self.preset_saved.emit("")

    def delete_selected_preset(self):
        """Delete selected user preset."""
        preset_name = self.preset_combo.currentData()

        if not preset_name:
            QMessageBox.warning(
                self,
                "Kein Preset gewählt",
                "Bitte wählen Sie ein Preset zum Löschen."
            )
            return

        if self.preset_manager.is_default_preset(preset_name):
            QMessageBox.warning(
                self,
                "Standard-Preset",
                "Standard-Presets können nicht gelöscht werden."
            )
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Preset löschen",
            f"Möchten Sie das Preset '{preset_name}' wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.preset_manager.delete_preset(preset_name)

            if success:
                self.load_presets()  # Refresh list
                self.preset_deleted.emit(preset_name)
                QMessageBox.information(
                    self,
                    "Preset gelöscht",
                    f"Preset '{preset_name}' wurde gelöscht."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    f"Preset '{preset_name}' konnte nicht gelöscht werden."
                )

    def get_selected_preset(self) -> str:
        """
        Get currently selected preset name.

        Returns:
            Preset name or empty string if none selected
        """
        preset_name = self.preset_combo.currentData()
        return preset_name or ""

    def refresh_presets(self):
        """Refresh preset list."""
        current_preset = self.get_selected_preset()
        self.load_presets()

        # Try to reselect previous preset
        if current_preset:
            index = self.preset_combo.findData(current_preset)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
