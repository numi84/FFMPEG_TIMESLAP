"""Widget for filter settings."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QFormLayout,
    QComboBox, QSlider, QLabel, QSpinBox, QPushButton, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from ...utils.constants import (
    DEFLICKER_MODES, ROTATE_ANGLES,
    DEFAULT_DEFLICKER_MODE, DEFAULT_DEFLICKER_SIZE, DEFAULT_ROTATE_ANGLE
)


class FilterSettingsWidget(QWidget):
    """Widget for filter settings (Deflicker, Crop, Rotate)."""

    # Signals
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__(parent)
        self.image_preview = None  # Will be set by main window
        self.preview_widget = None  # Will be set by main window

        # Debounce timers for smooth input
        self.rotate_update_timer = QTimer()
        self.rotate_update_timer.setSingleShot(True)
        self.rotate_update_timer.timeout.connect(self._apply_rotation_update)

        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        # Single column layout - preview is now in main window
        layout = QVBoxLayout()
        self.setLayout(layout)

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
        self.rotate_group.toggled.connect(self.on_rotate_toggled)
        layout.addWidget(self.rotate_group)

        rotate_layout = QFormLayout()
        self.rotate_group.setLayout(rotate_layout)

        # Rotate angle slider and input
        angle_layout = QHBoxLayout()

        self.rotate_slider = QSlider(Qt.Horizontal)
        self.rotate_slider.setRange(0, 359)
        self.rotate_slider.setValue(0)
        self.rotate_slider.setTickPosition(QSlider.TicksBelow)
        self.rotate_slider.setTickInterval(45)
        self.rotate_slider.valueChanged.connect(self.on_rotate_slider_changed)
        angle_layout.addWidget(self.rotate_slider, 1)

        # Direct angle input
        self.rotate_angle_spinbox = QDoubleSpinBox()
        self.rotate_angle_spinbox.setRange(0.0, 359.99)
        self.rotate_angle_spinbox.setDecimals(1)
        self.rotate_angle_spinbox.setSuffix("°")
        self.rotate_angle_spinbox.setValue(0.0)
        self.rotate_angle_spinbox.setMinimumWidth(80)
        self.rotate_angle_spinbox.valueChanged.connect(self.on_rotate_spinbox_changed)
        angle_layout.addWidget(self.rotate_angle_spinbox)

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

    def on_rotate_slider_changed(self, value: int):
        """Handle rotate slider change."""
        # Update spinbox without triggering its signal
        self.rotate_angle_spinbox.blockSignals(True)
        self.rotate_angle_spinbox.setValue(float(value))
        self.rotate_angle_spinbox.blockSignals(False)

        # Debounce: wait 200ms before updating preview
        self.rotate_update_timer.stop()
        self.rotate_update_timer.start(200)

    def on_rotate_spinbox_changed(self, value: float):
        """Handle rotate spinbox change."""
        # Update slider without triggering its signal
        self.rotate_slider.blockSignals(True)
        self.rotate_slider.setValue(int(value))
        self.rotate_slider.blockSignals(False)

        # Debounce: wait 200ms before updating preview
        self.rotate_update_timer.stop()
        self.rotate_update_timer.start(200)

    def _apply_rotation_update(self):
        """Apply rotation update after debounce delay."""
        # Update spinbox maximums based on transformed dimensions
        self.update_spinbox_maximums()

        self.update_preview()
        self.settings_changed.emit()

    def on_rotate_toggled(self, enabled: bool):
        """Handle rotation enable/disable."""
        # Update spinbox maximums when rotation is enabled/disabled
        self.update_spinbox_maximums()
        self.on_settings_changed()

    def update_spinbox_maximums(self):
        """Update crop spinbox maximum values based on transformed image dimensions."""
        if self.image_width == 0 or self.image_height == 0:
            return

        # Get dimensions after rotation/flip transforms
        transformed_width, transformed_height = self.get_transformed_dimensions()

        # Update spinbox maximums
        self.crop_x_spin.setMaximum(max(0, transformed_width - 32))
        self.crop_y_spin.setMaximum(max(0, transformed_height - 32))
        self.crop_w_spin.setMaximum(transformed_width)
        self.crop_h_spin.setMaximum(transformed_height)

        # Also validate current crop values against new bounds
        self.validate_crop_against_bounds()

    def validate_crop_against_bounds(self):
        """Validate and adjust crop values to fit within transformed image bounds."""
        transformed_width, transformed_height = self.get_transformed_dimensions()

        if transformed_width == 0 or transformed_height == 0:
            return

        # Block signals to prevent recursive updates
        self.crop_x_spin.blockSignals(True)
        self.crop_y_spin.blockSignals(True)
        self.crop_w_spin.blockSignals(True)
        self.crop_h_spin.blockSignals(True)

        # Get current values
        x = self.crop_x_spin.value()
        y = self.crop_y_spin.value()
        w = self.crop_w_spin.value()
        h = self.crop_h_spin.value()

        # Constrain to transformed bounds
        if x >= transformed_width:
            x = max(0, transformed_width - 32)
        if y >= transformed_height:
            y = max(0, transformed_height - 32)

        if x + w > transformed_width:
            w = max(32, transformed_width - x)
            w = (w // 2) * 2  # Round to even

        if y + h > transformed_height:
            h = max(32, transformed_height - y)
            h = (h // 2) * 2  # Round to even

        # Update values
        self.crop_x_spin.setValue(x)
        self.crop_y_spin.setValue(y)
        self.crop_w_spin.setValue(w)
        self.crop_h_spin.setValue(h)

        # Restore signals
        self.crop_x_spin.blockSignals(False)
        self.crop_y_spin.blockSignals(False)
        self.crop_w_spin.blockSignals(False)
        self.crop_h_spin.blockSignals(False)

    def on_crop_value_changed(self):
        """Handle crop value change with validation."""
        # Use transformed dimensions instead of original
        transformed_width, transformed_height = self.get_transformed_dimensions()

        if transformed_width > 0 and transformed_height > 0:
            # Validate crop boundaries
            x = self.crop_x_spin.value()
            y = self.crop_y_spin.value()
            w = self.crop_w_spin.value()
            h = self.crop_h_spin.value()

            # Ensure crop doesn't exceed transformed image boundaries
            if x + w > transformed_width:
                # Adjust width to fit
                new_w = transformed_width - x
                # Round down to even
                new_w = (new_w // 2) * 2
                if new_w < 32:
                    # If width too small, adjust x instead
                    x = transformed_width - w
                    x = max(0, (x // 2) * 2)
                    self.crop_x_spin.blockSignals(True)
                    self.crop_x_spin.setValue(x)
                    self.crop_x_spin.blockSignals(False)
                else:
                    self.crop_w_spin.blockSignals(True)
                    self.crop_w_spin.setValue(new_w)
                    self.crop_w_spin.blockSignals(False)

            if y + h > transformed_height:
                # Adjust height to fit
                new_h = transformed_height - y
                # Round down to even
                new_h = (new_h // 2) * 2
                if new_h < 32:
                    # If height too small, adjust y instead
                    y = transformed_height - h
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

    def on_preview_image_changed(self, image_path):
        """Handle image change from slider navigation."""
        from PIL import Image

        # Update image dimensions when navigating through images
        try:
            with Image.open(image_path) as img:
                self.image_width = img.width
                self.image_height = img.height

                # Update crop spinbox maximums based on current transforms
                self.update_spinbox_maximums()

        except Exception as e:
            print(f"Error loading image dimensions: {e}")

    def get_transformed_dimensions(self) -> tuple[int, int]:
        """
        Get image dimensions after rotation/flip transforms are applied.
        This mirrors the logic in InteractiveCropLabel._get_transformed_size()
        """
        width = self.image_width
        height = self.image_height

        if width == 0 or height == 0:
            return (width, height)

        # Get rotation angle if enabled
        if self.is_rotate_enabled():
            angle = self.get_rotate_angle() % 360

            if angle in [90, 270]:
                width, height = height, width
            elif angle in [0, 180]:
                pass  # No dimension change
            else:
                # Calculate bounding box for arbitrary angles
                import math
                rad = math.radians(angle)
                cos_a = abs(math.cos(rad))
                sin_a = abs(math.sin(rad))

                new_width = int(self.image_width * cos_a + self.image_height * sin_a)
                new_height = int(self.image_width * sin_a + self.image_height * cos_a)

                width, height = new_width, new_height

        return (width, height)

    def update_preview(self):
        """Update preview with current filter settings."""
        if not self.preview_widget:
            return

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
        if not self.preview_widget:
            return

        from pathlib import Path
        from PIL import Image

        # Load image to get dimensions
        try:
            with Image.open(image_path) as img:
                self.image_width = img.width
                self.image_height = img.height

                # Update crop spinbox maximums based on current transforms
                self.update_spinbox_maximums()

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
        return self.rotate_angle_spinbox.value()

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
        self.rotate_angle_spinbox.setValue(angle)
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
