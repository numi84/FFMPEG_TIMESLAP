"""Widget for advanced encoding settings."""

from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QCheckBox, QLineEdit
)
from PyQt5.QtCore import pyqtSignal

from ...utils.constants import (
    PROFILES, LEVELS, PIXEL_FORMATS,
    DEFAULT_PROFILE, DEFAULT_LEVEL, DEFAULT_PIXEL_FORMAT
)


class AdvancedSettingsWidget(QWidget):
    """Widget for advanced encoding settings."""

    # Signals
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        layout = QFormLayout()
        self.setLayout(layout)

        # Profile
        self.profile_combo = QComboBox()
        for profile in PROFILES:
            self.profile_combo.addItem(profile)
        self.profile_combo.setCurrentText(DEFAULT_PROFILE)
        self.profile_combo.currentIndexChanged.connect(self.on_settings_changed)
        layout.addRow("Profil:", self.profile_combo)

        # Level
        self.level_combo = QComboBox()
        for level in LEVELS:
            self.level_combo.addItem(level)
        self.level_combo.setCurrentText(DEFAULT_LEVEL)
        self.level_combo.currentIndexChanged.connect(self.on_settings_changed)
        layout.addRow("Level:", self.level_combo)

        # Pixel Format
        self.pixel_format_combo = QComboBox()
        for pix_fmt in PIXEL_FORMATS:
            self.pixel_format_combo.addItem(pix_fmt)
        self.pixel_format_combo.setCurrentText(DEFAULT_PIXEL_FORMAT)
        self.pixel_format_combo.currentIndexChanged.connect(self.on_settings_changed)
        layout.addRow("Pixelformat:", self.pixel_format_combo)

        # movflags faststart
        self.movflags_checkbox = QCheckBox("Aktivieren")
        self.movflags_checkbox.setChecked(True)
        self.movflags_checkbox.setToolTip(
            "Optimiert MP4-Dateien für schnelleres Streaming im Web"
        )
        self.movflags_checkbox.stateChanged.connect(self.on_settings_changed)
        layout.addRow("movflags +faststart:", self.movflags_checkbox)

        # Custom FFMPEG Arguments
        self.custom_args_edit = QLineEdit()
        self.custom_args_edit.setPlaceholderText("z.B. -threads 4 -y")
        self.custom_args_edit.setToolTip(
            "Zusätzliche FFMPEG-Argumente für fortgeschrittene Benutzer"
        )
        self.custom_args_edit.textChanged.connect(self.on_settings_changed)
        layout.addRow("Custom Args:", self.custom_args_edit)

        # Info label
        info_label = QLineEdit()
        info_label.setReadOnly(True)
        info_label.setStyleSheet("background: transparent; border: none; color: gray;")
        info_label.setText(
            "⚠ Hinweis: Custom Args werden am Ende des FFMPEG-Befehls angehängt"
        )
        layout.addRow("", info_label)

    def on_settings_changed(self):
        """Handle any setting change."""
        self.settings_changed.emit()

    # Getters
    def get_profile(self) -> str:
        """Get profile."""
        return self.profile_combo.currentText()

    def get_level(self) -> str:
        """Get level."""
        return self.level_combo.currentText()

    def get_pixel_format(self) -> str:
        """Get pixel format."""
        return self.pixel_format_combo.currentText()

    def get_movflags_faststart(self) -> bool:
        """Get movflags faststart setting."""
        return self.movflags_checkbox.isChecked()

    def get_custom_args(self) -> str:
        """Get custom FFMPEG arguments."""
        return self.custom_args_edit.text().strip()

    # Setters
    def set_profile(self, profile: str):
        """Set profile."""
        index = self.profile_combo.findText(profile)
        if index >= 0:
            self.profile_combo.setCurrentIndex(index)

    def set_level(self, level: str):
        """Set level."""
        index = self.level_combo.findText(level)
        if index >= 0:
            self.level_combo.setCurrentIndex(index)

    def set_pixel_format(self, pixel_format: str):
        """Set pixel format."""
        index = self.pixel_format_combo.findText(pixel_format)
        if index >= 0:
            self.pixel_format_combo.setCurrentIndex(index)

    def set_movflags_faststart(self, enabled: bool):
        """Set movflags faststart."""
        self.movflags_checkbox.setChecked(enabled)

    def set_custom_args(self, args: str):
        """Set custom arguments."""
        self.custom_args_edit.setText(args)
