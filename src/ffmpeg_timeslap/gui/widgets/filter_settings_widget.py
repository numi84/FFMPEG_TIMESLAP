"""Widget for filter settings."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QFormLayout,
    QComboBox, QSlider, QLabel, QSpinBox, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal

from ...utils.constants import (
    DEFLICKER_MODES, ROTATE_ANGLES,
    DEFAULT_DEFLICKER_MODE, DEFAULT_DEFLICKER_SIZE, DEFAULT_ROTATE_ANGLE
)
from .interactive_crop_widget import InteractiveCropWidget


class FilterSettingsWidget(QWidget):
    """Widget for filter settings (Deflicker, Crop, Rotate)."""

    # Signals
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__(parent)
        self.image_preview = None  # Will be set by main window
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left side: Filter controls
        left_widget = QWidget()
        layout = QVBoxLayout()
        left_widget.setLayout(layout)
        main_layout.addWidget(left_widget, 1)

        # Right side: Interactive crop preview
        self.preview_widget = InteractiveCropWidget()
        self.preview_widget.refresh_requested.connect(self.on_preview_refresh)
        self.preview_widget.crop_changed.connect(self.on_crop_changed_from_preview)
        self.preview_widget.image_changed.connect(self.on_preview_image_changed)
        main_layout.addWidget(self.preview_widget, 1)

        # Deflicker filter
        self.deflicker_group = QGroupBox("Deflicker")
        self.deflicker_group.setCheckable(True)
        self.deflicker_group.setChecked(False)
        self.deflicker_group.toggled.connect(self.on_settings_changed)
        layout.addWidget(self.deflicker_group)

        deflicker_layout = QFormLayout()
        self.deflicker_group.setLayout(deflicker_layout)

        # Deflicker mode
        self.deflicker_mode_combo = QComboBox()
        for mode in DEFLICKER_MODES:
            self.deflicker_mode_combo.addItem(mode)
        self.deflicker_mode_combo.setCurrentText(DEFAULT_DEFLICKER_MODE)
        self.deflicker_mode_combo.currentIndexChanged.connect(self.on_settings_changed)
        deflicker_layout.addRow("Modus:", self.deflicker_mode_combo)

        # Deflicker size
        size_layout = QHBoxLayout()

        self.deflicker_size_slider = QSlider(Qt.Horizontal)
        self.deflicker_size_slider.setRange(5, 20)
        self.deflicker_size_slider.setValue(DEFAULT_DEFLICKER_SIZE)
        self.deflicker_size_slider.setTickPosition(QSlider.TicksBelow)
        self.deflicker_size_slider.setTickInterval(5)
        self.deflicker_size_slider.valueChanged.connect(self.on_deflicker_size_changed)
        size_layout.addWidget(self.deflicker_size_slider, 1)

        self.deflicker_size_label = QLabel(str(DEFAULT_DEFLICKER_SIZE))
        self.deflicker_size_label.setMinimumWidth(30)
        size_layout.addWidget(self.deflicker_size_label)

        deflicker_layout.addRow("Größe:", size_layout)

        # Crop filter
        self.crop_group = QGroupBox("Crop (Zuschneiden)")
        self.crop_group.setCheckable(True)
        self.crop_group.setChecked(False)
        self.crop_group.toggled.connect(self.on_settings_changed)
        layout.addWidget(self.crop_group)

        crop_layout = QFormLayout()
        self.crop_group.setLayout(crop_layout)

        # Crop X
        self.crop_x_spin = QSpinBox()
        self.crop_x_spin.setRange(0, 9999)
        self.crop_x_spin.setSuffix(" px")
        self.crop_x_spin.setSingleStep(2)  # Step by 2 for even pixels
        self.crop_x_spin.valueChanged.connect(self.on_crop_value_changed)
        crop_layout.addRow("X Position:", self.crop_x_spin)

        # Crop Y
        self.crop_y_spin = QSpinBox()
        self.crop_y_spin.setRange(0, 9999)
        self.crop_y_spin.setSuffix(" px")
        self.crop_y_spin.setSingleStep(2)  # Step by 2 for even pixels
        self.crop_y_spin.valueChanged.connect(self.on_crop_value_changed)
        crop_layout.addRow("Y Position:", self.crop_y_spin)

        # Crop Width
        self.crop_w_spin = QSpinBox()
        self.crop_w_spin.setRange(32, 9999)  # Minimum 32px
        self.crop_w_spin.setValue(1920)
        self.crop_w_spin.setSuffix(" px")
        self.crop_w_spin.setSingleStep(2)  # Step by 2 for even pixels
        self.crop_w_spin.valueChanged.connect(self.on_crop_value_changed)
        crop_layout.addRow("Breite:", self.crop_w_spin)

        # Crop Height
        self.crop_h_spin = QSpinBox()
        self.crop_h_spin.setRange(32, 9999)  # Minimum 32px
        self.crop_h_spin.setValue(1080)
        self.crop_h_spin.setSuffix(" px")
        self.crop_h_spin.setSingleStep(2)  # Step by 2 for even pixels
        self.crop_h_spin.valueChanged.connect(self.on_crop_value_changed)
        crop_layout.addRow("Höhe:", self.crop_h_spin)

        # Store image dimensions for validation
        self.image_width = 0
        self.image_height = 0

        # Rotate filter
        self.rotate_group = QGroupBox("Rotate (Drehen)")
        self.rotate_group.setCheckable(True)
        self.rotate_group.setChecked(False)
        self.rotate_group.toggled.connect(self.on_settings_changed)
        layout.addWidget(self.rotate_group)

        rotate_layout = QFormLayout()
        self.rotate_group.setLayout(rotate_layout)

        # Rotate angle slider
        angle_layout = QHBoxLayout()

        self.rotate_slider = QSlider(Qt.Horizontal)
        self.rotate_slider.setRange(0, 359)
        self.rotate_slider.setValue(0)
        self.rotate_slider.setTickPosition(QSlider.TicksBelow)
        self.rotate_slider.setTickInterval(45)
        self.rotate_slider.valueChanged.connect(self.on_rotate_angle_changed)
        angle_layout.addWidget(self.rotate_slider, 1)

        self.rotate_angle_label = QLabel("0°")
        self.rotate_angle_label.setMinimumWidth(40)
        angle_layout.addWidget(self.rotate_angle_label)

        rotate_layout.addRow("Winkel:", angle_layout)

        # Quick rotate buttons
        quick_rotate_layout = QHBoxLayout()

        btn_90 = QPushButton("90°")
        btn_90.clicked.connect(lambda: self.rotate_slider.setValue(90))
        quick_rotate_layout.addWidget(btn_90)

        btn_180 = QPushButton("180°")
        btn_180.clicked.connect(lambda: self.rotate_slider.setValue(180))
        quick_rotate_layout.addWidget(btn_180)

        btn_270 = QPushButton("270°")
        btn_270.clicked.connect(lambda: self.rotate_slider.setValue(270))
        quick_rotate_layout.addWidget(btn_270)

        btn_reset = QPushButton("0°")
        btn_reset.clicked.connect(lambda: self.rotate_slider.setValue(0))
        quick_rotate_layout.addWidget(btn_reset)

        rotate_layout.addRow("Schnellwahl:", quick_rotate_layout)

        # Flip/Mirror filter
        self.flip_group = QGroupBox("Flip/Spiegeln")
        self.flip_group.setCheckable(True)
        self.flip_group.setChecked(False)
        self.flip_group.toggled.connect(self.on_settings_changed)
        layout.addWidget(self.flip_group)

        flip_layout = QVBoxLayout()
        self.flip_group.setLayout(flip_layout)

        # Horizontal flip
        self.flip_horizontal_check = QCheckBox("Horizontal spiegeln (links/rechts)")
        self.flip_horizontal_check.toggled.connect(self.on_settings_changed)
        flip_layout.addWidget(self.flip_horizontal_check)

        # Vertical flip
        self.flip_vertical_check = QCheckBox("Vertikal spiegeln (oben/unten)")
        self.flip_vertical_check.toggled.connect(self.on_settings_changed)
        flip_layout.addWidget(self.flip_vertical_check)

        # Stretch
        layout.addStretch()

    def on_deflicker_size_changed(self, value: int):
        """Handle deflicker size change."""
        self.deflicker_size_label.setText(str(value))
        self.settings_changed.emit()

    def on_rotate_angle_changed(self, value: int):
        """Handle rotate angle change."""
        self.rotate_angle_label.setText(f"{value}°")
        self.update_preview()
        self.settings_changed.emit()

    def on_crop_value_changed(self):
        """Handle crop value change with validation."""
        if self.image_width > 0 and self.image_height > 0:
            # Validate crop boundaries
            x = self.crop_x_spin.value()
            y = self.crop_y_spin.value()
            w = self.crop_w_spin.value()
            h = self.crop_h_spin.value()

            # Ensure crop doesn't exceed image boundaries
            if x + w > self.image_width:
                # Adjust width to fit
                new_w = self.image_width - x
                # Round down to even
                new_w = (new_w // 2) * 2
                if new_w < 32:
                    # If width too small, adjust x instead
                    x = self.image_width - w
                    x = max(0, (x // 2) * 2)
                    self.crop_x_spin.blockSignals(True)
                    self.crop_x_spin.setValue(x)
                    self.crop_x_spin.blockSignals(False)
                else:
                    self.crop_w_spin.blockSignals(True)
                    self.crop_w_spin.setValue(new_w)
                    self.crop_w_spin.blockSignals(False)

            if y + h > self.image_height:
                # Adjust height to fit
                new_h = self.image_height - y
                # Round down to even
                new_h = (new_h // 2) * 2
                if new_h < 32:
                    # If height too small, adjust y instead
                    y = self.image_height - h
                    y = max(0, (y // 2) * 2)
                    self.crop_y_spin.blockSignals(True)
                    self.crop_y_spin.setValue(y)
                    self.crop_y_spin.blockSignals(False)
                else:
                    self.crop_h_spin.blockSignals(True)
                    self.crop_h_spin.setValue(new_h)
                    self.crop_h_spin.blockSignals(False)

        self.on_settings_changed()

    def on_crop_changed_from_preview(self, x: int, y: int, w: int, h: int):
        """Handle crop change from interactive preview."""
        # Update spin boxes without triggering another update
        self.crop_x_spin.blockSignals(True)
        self.crop_y_spin.blockSignals(True)
        self.crop_w_spin.blockSignals(True)
        self.crop_h_spin.blockSignals(True)

        self.crop_x_spin.setValue(x)
        self.crop_y_spin.setValue(y)
        self.crop_w_spin.setValue(w)
        self.crop_h_spin.setValue(h)

        self.crop_x_spin.blockSignals(False)
        self.crop_y_spin.blockSignals(False)
        self.crop_w_spin.blockSignals(False)
        self.crop_h_spin.blockSignals(False)

        self.settings_changed.emit()

    def on_settings_changed(self):
        """Handle any setting change."""
        self.update_preview()
        self.settings_changed.emit()

    def on_preview_refresh(self):
        """Handle preview refresh request."""
        # Will be connected by main window to load first image from sequence
        pass

    def on_preview_image_changed(self, image_path):
        """Handle image change from slider navigation."""
        from PIL import Image

        # Update image dimensions when navigating through images
        try:
            with Image.open(image_path) as img:
                self.image_width = img.width
                self.image_height = img.height

                # Update crop spinbox maximums
                self.crop_x_spin.setMaximum(self.image_width - 32)
                self.crop_y_spin.setMaximum(self.image_height - 32)
                self.crop_w_spin.setMaximum(self.image_width)
                self.crop_h_spin.setMaximum(self.image_height)

        except Exception as e:
            print(f"Error loading image dimensions: {e}")

    def update_preview(self):
        """Update preview with current filter settings."""
        # Update crop settings in preview
        if self.is_crop_enabled():
            self.preview_widget.set_crop(
                self.get_crop_x(),
                self.get_crop_y(),
                self.get_crop_width(),
                self.get_crop_height()
            )

        # Update rotation and flip transforms
        rotate_angle = self.get_rotate_angle() if self.is_rotate_enabled() else 0
        flip_h = self.is_flip_horizontal() if self.is_flip_enabled() else False
        flip_v = self.is_flip_vertical() if self.is_flip_enabled() else False

        # Pass transforms to preview widget
        if hasattr(self.preview_widget, 'crop_label'):
            self.preview_widget.crop_label.set_transforms(rotate_angle, flip_h, flip_v)

    def load_preview_image(self, image_path, image_files=None):
        """
        Load an image into the preview.

        Args:
            image_path: Path to image file
            image_files: Optional list of all image files in sequence
        """
        from pathlib import Path
        from PIL import Image

        # Load image to get dimensions
        try:
            with Image.open(image_path) as img:
                self.image_width = img.width
                self.image_height = img.height

                # Update crop spinbox maximums
                self.crop_x_spin.setMaximum(self.image_width - 32)
                self.crop_y_spin.setMaximum(self.image_height - 32)
                self.crop_w_spin.setMaximum(self.image_width)
                self.crop_h_spin.setMaximum(self.image_height)

                # Set initial crop to full image if not set
                if self.crop_w_spin.value() == 1920 and self.crop_h_spin.value() == 1080:
                    self.crop_w_spin.setValue(self.image_width)
                    self.crop_h_spin.setValue(self.image_height)

        except Exception as e:
            print(f"Error loading image dimensions: {e}")

        # If image sequence provided, use it for slider navigation
        if image_files:
            self.preview_widget.set_image_sequence([Path(f) for f in image_files])
        else:
            self.preview_widget.load_image(Path(image_path))

        self.update_preview()

    # Getters
    def is_deflicker_enabled(self) -> bool:
        """Check if deflicker is enabled."""
        return self.deflicker_group.isChecked()

    def get_deflicker_mode(self) -> str:
        """Get deflicker mode."""
        return self.deflicker_mode_combo.currentText()

    def get_deflicker_size(self) -> int:
        """Get deflicker size."""
        return self.deflicker_size_slider.value()

    def is_crop_enabled(self) -> bool:
        """Check if crop is enabled."""
        return self.crop_group.isChecked()

    def get_crop_x(self) -> int:
        """Get crop X position."""
        return self.crop_x_spin.value()

    def get_crop_y(self) -> int:
        """Get crop Y position."""
        return self.crop_y_spin.value()

    def get_crop_width(self) -> int:
        """Get crop width."""
        return self.crop_w_spin.value()

    def get_crop_height(self) -> int:
        """Get crop height."""
        return self.crop_h_spin.value()

    def is_rotate_enabled(self) -> bool:
        """Check if rotate is enabled."""
        return self.rotate_group.isChecked()

    def get_rotate_angle(self) -> float:
        """Get rotate angle."""
        return float(self.rotate_slider.value())

    def is_flip_enabled(self) -> bool:
        """Check if flip is enabled."""
        return self.flip_group.isChecked()

    def is_flip_horizontal(self) -> bool:
        """Check if horizontal flip is enabled."""
        return self.flip_horizontal_check.isChecked()

    def is_flip_vertical(self) -> bool:
        """Check if vertical flip is enabled."""
        return self.flip_vertical_check.isChecked()

    # Setters
    def set_deflicker_enabled(self, enabled: bool):
        """Set deflicker enabled."""
        self.deflicker_group.setChecked(enabled)

    def set_deflicker_mode(self, mode: str):
        """Set deflicker mode."""
        index = self.deflicker_mode_combo.findText(mode)
        if index >= 0:
            self.deflicker_mode_combo.setCurrentIndex(index)

    def set_deflicker_size(self, size: int):
        """Set deflicker size."""
        self.deflicker_size_slider.setValue(size)

    def set_crop_enabled(self, enabled: bool):
        """Set crop enabled."""
        self.crop_group.setChecked(enabled)

    def set_crop_values(self, x: int, y: int, width: int, height: int):
        """Set crop values."""
        self.crop_x_spin.setValue(x)
        self.crop_y_spin.setValue(y)
        self.crop_w_spin.setValue(width)
        self.crop_h_spin.setValue(height)

    def set_rotate_enabled(self, enabled: bool):
        """Set rotate enabled."""
        self.rotate_group.setChecked(enabled)

    def set_rotate_angle(self, angle: float):
        """Set rotate angle."""
        self.rotate_slider.setValue(int(angle))

    def set_flip_enabled(self, enabled: bool):
        """Set flip enabled."""
        self.flip_group.setChecked(enabled)

    def set_flip_horizontal(self, enabled: bool):
        """Set horizontal flip."""
        self.flip_horizontal_check.setChecked(enabled)

    def set_flip_vertical(self, enabled: bool):
        """Set vertical flip."""
        self.flip_vertical_check.setChecked(enabled)
