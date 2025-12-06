"""Widget for filter settings."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QFormLayout,
    QComboBox, QSlider, QLabel, QSpinBox, QPushButton, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from ...utils.constants import (
    DEFLICKER_MODES, ROTATE_ANGLES,
    DEFAULT_DEFLICKER_MODE, DEFAULT_DEFLICKER_SIZE, DEFAULT_ROTATE_ANGLE,
    ASPECT_RATIOS, DEFAULT_ASPECT_RATIO
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

        # Aspect Ratio controls
        aspect_ratio_layout = QVBoxLayout()

        # First row: Preset dropdown + Lock checkbox
        preset_lock_layout = QHBoxLayout()

        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItems(ASPECT_RATIOS)
        self.aspect_ratio_combo.setCurrentText(DEFAULT_ASPECT_RATIO)
        self.aspect_ratio_combo.currentTextChanged.connect(self.on_aspect_ratio_preset_changed)
        preset_lock_layout.addWidget(QLabel("Seitenverhältnis:"))
        preset_lock_layout.addWidget(self.aspect_ratio_combo, 1)

        self.aspect_ratio_lock_check = QCheckBox("Sperren")
        self.aspect_ratio_lock_check.setChecked(False)
        self.aspect_ratio_lock_check.toggled.connect(self.on_aspect_ratio_lock_toggled)
        preset_lock_layout.addWidget(self.aspect_ratio_lock_check)

        aspect_ratio_layout.addLayout(preset_lock_layout)

        # Second row: Custom ratio inputs (hidden by default)
        custom_ratio_layout = QHBoxLayout()

        self.custom_ratio_w_spin = QSpinBox()
        self.custom_ratio_w_spin.setRange(1, 99)
        self.custom_ratio_w_spin.setValue(16)
        self.custom_ratio_w_spin.setPrefix("W: ")
        self.custom_ratio_w_spin.valueChanged.connect(self.on_custom_ratio_changed)
        custom_ratio_layout.addWidget(self.custom_ratio_w_spin)

        custom_ratio_layout.addWidget(QLabel(":"))

        self.custom_ratio_h_spin = QSpinBox()
        self.custom_ratio_h_spin.setRange(1, 99)
        self.custom_ratio_h_spin.setValue(9)
        self.custom_ratio_h_spin.setPrefix("H: ")
        self.custom_ratio_h_spin.valueChanged.connect(self.on_custom_ratio_changed)
        custom_ratio_layout.addWidget(self.custom_ratio_h_spin)

        self.custom_ratio_widget = QWidget()
        self.custom_ratio_widget.setLayout(custom_ratio_layout)
        self.custom_ratio_widget.setVisible(False)  # Hidden initially

        aspect_ratio_layout.addWidget(self.custom_ratio_widget)

        # Third row: Swap button + Current ratio display
        swap_display_layout = QHBoxLayout()

        self.aspect_ratio_swap_btn = QPushButton("↔ Tauschen")
        self.aspect_ratio_swap_btn.setToolTip("Breite und Höhe tauschen (Hochformat ↔ Querformat)")
        self.aspect_ratio_swap_btn.clicked.connect(self.on_swap_aspect_ratio)
        swap_display_layout.addWidget(self.aspect_ratio_swap_btn)

        self.current_ratio_label = QLabel("Aktuell: --")
        self.current_ratio_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        swap_display_layout.addWidget(self.current_ratio_label, 1)

        aspect_ratio_layout.addLayout(swap_display_layout)

        crop_layout.addRow(aspect_ratio_layout)

        # Store image dimensions for validation
        self.image_width = 0
        self.image_height = 0

        # Track aspect ratio editing state
        self.last_edited_dimension = "width"  # Track which was edited last
        self.ignore_spinbox_updates = False   # Prevent circular updates

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
        """Handle crop value change with validation and aspect ratio enforcement."""
        # Ignore updates if we're programmatically updating
        if self.ignore_spinbox_updates:
            return

        # Use transformed dimensions instead of original
        transformed_width, transformed_height = self.get_transformed_dimensions()

        if transformed_width > 0 and transformed_height > 0:
            x = self.crop_x_spin.value()
            y = self.crop_y_spin.value()
            w = self.crop_w_spin.value()
            h = self.crop_h_spin.value()

            # If aspect ratio is locked, adjust based on which dimension changed
            if self.aspect_ratio_lock_check.isChecked():
                sender = self.sender()

                # Determine which dimension was edited
                if sender == self.crop_w_spin:
                    self.last_edited_dimension = "width"
                elif sender == self.crop_h_spin:
                    self.last_edited_dimension = "height"

                # Get current ratio
                ratio_w, ratio_h = self.get_current_aspect_ratio()

                # Auto-adjust based on last edited dimension
                if self.last_edited_dimension == "width":
                    # Width changed, calculate new height
                    from ...utils.aspect_ratio import calculate_height_from_width
                    new_h = calculate_height_from_width(w, ratio_w, ratio_h)

                    # Check if new height fits
                    if y + new_h > transformed_height:
                        # Doesn't fit, adjust both to fit
                        new_h = min(new_h, transformed_height - y)
                        new_h = max(32, (new_h // 2) * 2)

                        from ...utils.aspect_ratio import calculate_width_from_height
                        w = calculate_width_from_height(new_h, ratio_w, ratio_h)

                    # Update height spinbox
                    self.ignore_spinbox_updates = True
                    self.crop_h_spin.setValue(new_h)
                    self.ignore_spinbox_updates = False
                    h = new_h

                else:  # height edited
                    # Height changed, calculate new width
                    from ...utils.aspect_ratio import calculate_width_from_height
                    new_w = calculate_width_from_height(h, ratio_w, ratio_h)

                    # Check if new width fits
                    if x + new_w > transformed_width:
                        # Doesn't fit, adjust both to fit
                        new_w = min(new_w, transformed_width - x)
                        new_w = max(32, (new_w // 2) * 2)

                        from ...utils.aspect_ratio import calculate_height_from_width
                        h = calculate_height_from_width(new_w, ratio_w, ratio_h)

                    # Update width spinbox
                    self.ignore_spinbox_updates = True
                    self.crop_w_spin.setValue(new_w)
                    self.ignore_spinbox_updates = False
                    w = new_w

            # Standard boundary validation
            if x + w > transformed_width:
                new_w = transformed_width - x
                new_w = (new_w // 2) * 2
                if new_w < 32:
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
                new_h = transformed_height - y
                new_h = (new_h // 2) * 2
                if new_h < 32:
                    y = transformed_height - h
                    y = max(0, (y // 2) * 2)
                    self.crop_y_spin.blockSignals(True)
                    self.crop_y_spin.setValue(y)
                    self.crop_y_spin.blockSignals(False)
                else:
                    self.crop_h_spin.blockSignals(True)
                    self.crop_h_spin.setValue(new_h)
                    self.crop_h_spin.blockSignals(False)

        # Update current ratio display
        self.update_current_ratio_display()

        # Update preview and emit signal
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

        # Update current ratio display
        self.update_current_ratio_display()

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

    # Aspect Ratio Methods
    def get_current_aspect_ratio(self) -> tuple:
        """
        Get current aspect ratio components.

        Returns:
            Tuple of (width_ratio, height_ratio)
        """
        from ...utils.aspect_ratio import parse_ratio_string

        preset = self.aspect_ratio_combo.currentText()

        if preset in ["Free", "Default"]:
            # No constraint, return current dimensions ratio
            return (self.crop_w_spin.value(), self.crop_h_spin.value())
        elif preset == "Custom":
            return (self.custom_ratio_w_spin.value(), self.custom_ratio_h_spin.value())
        else:
            try:
                return parse_ratio_string(preset)
            except ValueError:
                return (16, 9)  # Fallback

    def on_aspect_ratio_preset_changed(self, preset: str):
        """Handle aspect ratio preset selection change."""
        # Show/hide custom ratio inputs
        if preset == "Custom":
            self.custom_ratio_widget.setVisible(True)
        else:
            self.custom_ratio_widget.setVisible(False)

        # "Default" preset is always locked, auto-enable lock
        if preset == "Default":
            self.aspect_ratio_lock_check.setChecked(True)
            self.aspect_ratio_lock_check.setEnabled(False)  # Disable lock checkbox
        else:
            self.aspect_ratio_lock_check.setEnabled(True)   # Enable lock checkbox

        # If locked, apply new ratio to current crop
        if self.aspect_ratio_lock_check.isChecked() and preset not in ["Free", "Default"]:
            self.apply_aspect_ratio_to_crop()

        # Update display
        self.update_current_ratio_display()

        # Update preview widget aspect ratio
        self.update_preview_aspect_ratio()

    def on_aspect_ratio_lock_toggled(self, locked: bool):
        """Handle aspect ratio lock toggle."""
        if locked:
            preset = self.aspect_ratio_combo.currentText()

            # Auto-detect if "Free" or "Default" selected
            if preset in ["Free", "Default"]:
                self.auto_detect_aspect_ratio()
            else:
                # Apply selected ratio to current crop
                self.apply_aspect_ratio_to_crop()

        # Update preview widget
        self.update_preview_aspect_ratio()

        # Update display
        self.update_current_ratio_display()

    def on_custom_ratio_changed(self):
        """Handle custom aspect ratio value change."""
        if self.aspect_ratio_combo.currentText() == "Custom":
            # IMPORTANT: Update preview widget with new custom ratio values
            self.update_preview_aspect_ratio()

            if self.aspect_ratio_lock_check.isChecked():
                self.apply_aspect_ratio_to_crop()
            self.update_current_ratio_display()

    def on_swap_aspect_ratio(self):
        """Swap width and height of crop (portrait <-> landscape)."""
        # If aspect ratio is locked, update the aspect ratio settings FIRST
        preset = self.aspect_ratio_combo.currentText()

        if self.aspect_ratio_lock_check.isChecked():
            if preset == "Custom":
                # Swap custom ratio values BEFORE swapping crop dimensions
                custom_w = self.custom_ratio_w_spin.value()
                custom_h = self.custom_ratio_h_spin.value()

                self.custom_ratio_w_spin.blockSignals(True)
                self.custom_ratio_h_spin.blockSignals(True)
                self.custom_ratio_w_spin.setValue(custom_h)
                self.custom_ratio_h_spin.setValue(custom_w)
                self.custom_ratio_w_spin.blockSignals(False)
                self.custom_ratio_h_spin.blockSignals(False)

            elif preset not in ["Free", "Default"]:
                # Try to find matching swapped preset (e.g., 16:9 -> 9:16)
                from ...utils.aspect_ratio import parse_ratio_string
                try:
                    ratio_w, ratio_h = parse_ratio_string(preset)
                    swapped_preset = f"{ratio_h}:{ratio_w}"

                    # Check if swapped version exists in presets
                    if swapped_preset in ASPECT_RATIOS:
                        self.aspect_ratio_combo.blockSignals(True)
                        self.aspect_ratio_combo.setCurrentText(swapped_preset)
                        self.aspect_ratio_combo.blockSignals(False)
                except ValueError:
                    pass  # Keep current preset if can't swap

        # IMPORTANT: Update preview widget with new aspect ratio BEFORE swapping crop
        self.update_preview_aspect_ratio()

        # Now swap the crop dimensions
        current_w = self.crop_w_spin.value()
        current_h = self.crop_h_spin.value()

        self.ignore_spinbox_updates = True
        self.crop_w_spin.setValue(current_h)
        self.crop_h_spin.setValue(current_w)
        self.ignore_spinbox_updates = False

        # Validate against bounds
        self.validate_crop_against_bounds()

        # Update preview
        self.on_settings_changed()

        # Update display
        self.update_current_ratio_display()

    def apply_aspect_ratio_to_crop(self):
        """Apply current aspect ratio to crop dimensions."""
        from ...utils.aspect_ratio import constrain_rect_to_ratio

        ratio_w, ratio_h = self.get_current_aspect_ratio()
        transformed_width, transformed_height = self.get_transformed_dimensions()

        if transformed_width == 0 or transformed_height == 0:
            return

        # Get current crop
        x = self.crop_x_spin.value()
        y = self.crop_y_spin.value()
        w = self.crop_w_spin.value()
        h = self.crop_h_spin.value()

        # Constrain to ratio
        new_x, new_y, new_w, new_h = constrain_rect_to_ratio(
            x, y, w, h, ratio_w, ratio_h,
            transformed_width, transformed_height,
            anchor="center"
        )

        # Update spinboxes
        self.ignore_spinbox_updates = True
        self.crop_x_spin.setValue(new_x)
        self.crop_y_spin.setValue(new_y)
        self.crop_w_spin.setValue(new_w)
        self.crop_h_spin.setValue(new_h)
        self.ignore_spinbox_updates = False

        # Update preview
        self.update_preview()

    def auto_detect_aspect_ratio(self):
        """Auto-detect aspect ratio from current crop or image dimensions."""
        from ...utils.aspect_ratio import simplify_ratio, find_closest_preset_ratio

        # Use current crop dimensions
        w = self.crop_w_spin.value()
        h = self.crop_h_spin.value()

        # Simplify ratio
        ratio_w, ratio_h = simplify_ratio(w, h)

        # Get list of presets (exclude "Free" and "Custom")
        presets = [r for r in ASPECT_RATIOS if r not in ["Free", "Custom"]]

        # Find closest preset
        closest = find_closest_preset_ratio(w, h, presets)

        if closest:
            # Select the preset
            self.aspect_ratio_combo.blockSignals(True)
            self.aspect_ratio_combo.setCurrentText(closest)
            self.aspect_ratio_combo.blockSignals(False)
        else:
            # Use custom
            self.aspect_ratio_combo.blockSignals(True)
            self.aspect_ratio_combo.setCurrentText("Custom")
            self.aspect_ratio_combo.blockSignals(False)

            self.custom_ratio_w_spin.setValue(ratio_w)
            self.custom_ratio_h_spin.setValue(ratio_h)
            self.custom_ratio_widget.setVisible(True)

        self.update_current_ratio_display()

    def update_current_ratio_display(self):
        """Update the current aspect ratio display label."""
        w = self.crop_w_spin.value()
        h = self.crop_h_spin.value()

        if w == 0 or h == 0:
            self.current_ratio_label.setText("Aktuell: --")
            return

        from ...utils.aspect_ratio import simplify_ratio
        ratio_w, ratio_h = simplify_ratio(w, h)

        # Also show decimal ratio
        decimal_ratio = w / h

        self.current_ratio_label.setText(
            f"Aktuell: {ratio_w}:{ratio_h} ({decimal_ratio:.2f}:1)"
        )

    def update_preview_aspect_ratio(self):
        """Update aspect ratio constraint in preview widget."""
        if not self.preview_widget:
            return

        locked = self.aspect_ratio_lock_check.isChecked()
        ratio_w, ratio_h = self.get_current_aspect_ratio()

        if hasattr(self.preview_widget, 'crop_label'):
            self.preview_widget.crop_label.set_aspect_ratio(locked, ratio_w, ratio_h)

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

    def is_aspect_ratio_locked(self) -> bool:
        """Check if aspect ratio is locked."""
        return self.aspect_ratio_lock_check.isChecked()

    def get_aspect_ratio_preset(self) -> str:
        """Get aspect ratio preset."""
        return self.aspect_ratio_combo.currentText()

    def get_aspect_ratio_custom_w(self) -> int:
        """Get custom aspect ratio width."""
        return self.custom_ratio_w_spin.value()

    def get_aspect_ratio_custom_h(self) -> int:
        """Get custom aspect ratio height."""
        return self.custom_ratio_h_spin.value()

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

    def set_aspect_ratio_locked(self, locked: bool):
        """Set aspect ratio locked."""
        self.aspect_ratio_lock_check.setChecked(locked)

    def set_aspect_ratio_preset(self, preset: str):
        """Set aspect ratio preset."""
        index = self.aspect_ratio_combo.findText(preset)
        if index >= 0:
            self.aspect_ratio_combo.setCurrentIndex(index)

    def set_aspect_ratio_custom(self, w: int, h: int):
        """Set custom aspect ratio values."""
        self.custom_ratio_w_spin.setValue(w)
        self.custom_ratio_h_spin.setValue(h)

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
