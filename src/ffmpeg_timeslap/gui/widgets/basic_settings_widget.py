"""Widget for basic encoding settings."""

from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QSpinBox, QSlider,
    QLabel, QHBoxLayout, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal

from ...utils.constants import (
    CODECS, FRAMERATES, ENCODING_PRESETS, CRF_PRESETS,
    RESOLUTIONS, DEFAULT_FRAMERATE, DEFAULT_CODEC,
    DEFAULT_PRESET, DEFAULT_CRF, DEFAULT_RESOLUTION
)
from ...utils.ffmpeg_locator import find_ffmpeg, check_codec_available


class BasicSettingsWidget(QWidget):
    """Widget for basic encoding settings."""

    # Signals
    settings_changed = pyqtSignal()
    framerate_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        layout = QFormLayout()
        self.setLayout(layout)

        # Framerate
        framerate_layout = QHBoxLayout()

        self.framerate_combo = QComboBox()
        for fps in FRAMERATES:
            self.framerate_combo.addItem(f"{fps} fps", fps)
        self.framerate_combo.setCurrentText(f"{DEFAULT_FRAMERATE} fps")
        self.framerate_combo.currentIndexChanged.connect(self.on_framerate_changed)
        framerate_layout.addWidget(self.framerate_combo)

        # Custom framerate spinbox
        self.framerate_spin = QSpinBox()
        self.framerate_spin.setRange(1, 240)
        self.framerate_spin.setValue(DEFAULT_FRAMERATE)
        self.framerate_spin.setSuffix(" fps")
        self.framerate_spin.valueChanged.connect(self.on_framerate_spin_changed)
        framerate_layout.addWidget(QLabel("oder Custom:"))
        framerate_layout.addWidget(self.framerate_spin)

        layout.addRow("Framerate:", framerate_layout)

        # Codec
        self.codec_combo = QComboBox()
        self._populate_codec_list()
        self.codec_combo.currentIndexChanged.connect(self.on_settings_changed)
        layout.addRow("Codec:", self.codec_combo)

        # CRF Quality
        crf_layout = QHBoxLayout()

        self.crf_slider = QSlider(Qt.Horizontal)
        self.crf_slider.setRange(0, 51)
        self.crf_slider.setValue(DEFAULT_CRF)
        self.crf_slider.setTickPosition(QSlider.TicksBelow)
        self.crf_slider.setTickInterval(5)
        self.crf_slider.valueChanged.connect(self.on_crf_changed)
        crf_layout.addWidget(self.crf_slider, 1)

        self.crf_value_label = QLabel(str(DEFAULT_CRF))
        self.crf_value_label.setMinimumWidth(30)
        self.crf_value_label.setStyleSheet("font-weight: bold;")
        crf_layout.addWidget(self.crf_value_label)

        layout.addRow("Qualität (CRF):", crf_layout)

        # CRF Preset buttons
        preset_layout = QHBoxLayout()
        for preset_name, crf_value in CRF_PRESETS.items():
            btn = QPushButton(preset_name)
            btn.setProperty("crf_value", crf_value)
            btn.clicked.connect(lambda checked, v=crf_value: self.set_crf(v))
            preset_layout.addWidget(btn)

        layout.addRow("", preset_layout)

        # Encoding Preset
        self.preset_combo = QComboBox()
        for preset in ENCODING_PRESETS:
            self.preset_combo.addItem(preset)
        self.preset_combo.setCurrentText(DEFAULT_PRESET)
        self.preset_combo.currentIndexChanged.connect(self.on_settings_changed)
        layout.addRow("Encoding Preset:", self.preset_combo)

        # Output Resolution
        resolution_layout = QHBoxLayout()

        self.resolution_combo = QComboBox()
        for res_id, res_name in RESOLUTIONS:
            self.resolution_combo.addItem(res_name, res_id)
        self.resolution_combo.setCurrentText(
            next(name for rid, name in RESOLUTIONS if rid == DEFAULT_RESOLUTION)
        )
        self.resolution_combo.currentIndexChanged.connect(self.on_resolution_changed)
        resolution_layout.addWidget(self.resolution_combo)

        # Custom resolution inputs
        self.custom_width_edit = QLineEdit()
        self.custom_width_edit.setPlaceholderText("Breite")
        self.custom_width_edit.setMaximumWidth(80)
        self.custom_width_edit.setEnabled(False)
        resolution_layout.addWidget(self.custom_width_edit)

        resolution_layout.addWidget(QLabel("x"))

        self.custom_height_edit = QLineEdit()
        self.custom_height_edit.setPlaceholderText("Höhe")
        self.custom_height_edit.setMaximumWidth(80)
        self.custom_height_edit.setEnabled(False)
        resolution_layout.addWidget(self.custom_height_edit)

        layout.addRow("Auflösung:", resolution_layout)

    def on_framerate_changed(self):
        """Handle framerate combo change."""
        fps = self.framerate_combo.currentData()
        if fps:
            self.framerate_spin.blockSignals(True)
            self.framerate_spin.setValue(fps)
            self.framerate_spin.blockSignals(False)
            self.framerate_changed.emit(fps)
            self.settings_changed.emit()

    def on_framerate_spin_changed(self, value: int):
        """Handle custom framerate spinbox change."""
        # Update combo to show custom value
        self.framerate_combo.blockSignals(True)
        index = self.framerate_combo.findData(value)
        if index >= 0:
            self.framerate_combo.setCurrentIndex(index)
        self.framerate_combo.blockSignals(False)
        self.framerate_changed.emit(value)
        self.settings_changed.emit()

    def on_crf_changed(self, value: int):
        """Handle CRF slider change."""
        self.crf_value_label.setText(str(value))
        self.settings_changed.emit()

    def set_crf(self, value: int):
        """Set CRF value from preset button."""
        self.crf_slider.setValue(value)

    def on_resolution_changed(self):
        """Handle resolution combo change."""
        resolution = self.resolution_combo.currentData()

        # Enable/disable custom inputs
        is_custom = (resolution == "custom")
        self.custom_width_edit.setEnabled(is_custom)
        self.custom_height_edit.setEnabled(is_custom)

        if not is_custom:
            self.custom_width_edit.clear()
            self.custom_height_edit.clear()

        self.settings_changed.emit()

    def on_settings_changed(self):
        """Handle any setting change."""
        self.settings_changed.emit()

    def _populate_codec_list(self):
        """Populate codec combo box with availability check."""
        try:
            ffmpeg_path = find_ffmpeg()

            for codec_id, codec_name in CODECS:
                is_available = check_codec_available(ffmpeg_path, codec_id)

                if is_available:
                    # Codec is available
                    self.codec_combo.addItem(f"{codec_name}", codec_id)
                else:
                    # Codec not available - show with warning
                    self.codec_combo.addItem(f"{codec_name} ⚠️ (nicht verfügbar)", codec_id)

            # Set default codec
            default_index = self.codec_combo.findData(DEFAULT_CODEC)
            if default_index >= 0:
                self.codec_combo.setCurrentIndex(default_index)

        except Exception:
            # If we can't check availability, just show all codecs
            for codec_id, codec_name in CODECS:
                self.codec_combo.addItem(codec_name, codec_id)

            default_index = self.codec_combo.findData(DEFAULT_CODEC)
            if default_index >= 0:
                self.codec_combo.setCurrentIndex(default_index)

    # Getters
    def get_framerate(self) -> int:
        """Get framerate value."""
        return self.framerate_spin.value()

    def get_codec(self) -> str:
        """Get codec ID."""
        return self.codec_combo.currentData()

    def get_crf(self) -> int:
        """Get CRF value."""
        return self.crf_slider.value()

    def get_preset(self) -> str:
        """Get encoding preset."""
        return self.preset_combo.currentText()

    def get_resolution(self) -> str:
        """Get resolution preset ID."""
        return self.resolution_combo.currentData()

    def get_custom_resolution(self) -> str:
        """Get custom resolution string."""
        if self.resolution_combo.currentData() == "custom":
            width = self.custom_width_edit.text()
            height = self.custom_height_edit.text()
            if width and height:
                return f"{width}x{height}"
        return ""

    # Setters
    def set_framerate(self, fps: int):
        """Set framerate."""
        self.framerate_spin.setValue(fps)

    def set_codec(self, codec: str):
        """Set codec."""
        index = self.codec_combo.findData(codec)
        if index >= 0:
            self.codec_combo.setCurrentIndex(index)

    def set_crf_value(self, crf: int):
        """Set CRF value."""
        self.crf_slider.setValue(crf)

    def set_encoding_preset(self, preset: str):
        """Set encoding preset."""
        index = self.preset_combo.findText(preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)

    def set_resolution(self, resolution: str, custom_resolution: str = ""):
        """Set resolution."""
        index = self.resolution_combo.findData(resolution)
        if index >= 0:
            self.resolution_combo.setCurrentIndex(index)

        if resolution == "custom" and custom_resolution:
            if 'x' in custom_resolution:
                width, height = custom_resolution.split('x')
                self.custom_width_edit.setText(width)
                self.custom_height_edit.setText(height)
