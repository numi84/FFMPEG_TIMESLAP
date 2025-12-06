"""Interactive crop widget with mouse selection."""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QSpinBox, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QCursor, QMouseEvent
from pathlib import Path
from typing import Optional


class InteractiveCropLabel(QLabel):
    """Label that allows interactive crop selection with mouse."""

    crop_changed = pyqtSignal(int, int, int, int)  # x, y, w, h

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__(parent)

        self.original_pixmap: Optional[QPixmap] = None
        self.display_scale = 1.0
        self.display_offset = QPoint(0, 0)  # Offset for centered image

        # Crop rectangle in transformed image coordinates
        self.crop_rect = QRect(0, 0, 100, 100)
        self.is_dragging = False
        self.is_resizing = False
        self.resize_handle = None  # 'tl', 'tr', 'bl', 'br', 'l', 'r', 't', 'b'
        self.drag_start_pos = QPoint()
        self.drag_start_rect = QRect()

        # Transform settings
        self.rotate_angle = 0.0
        self.flip_horizontal = False
        self.flip_vertical = False

        # Aspect ratio constraint
        self.aspect_ratio_locked = False
        self.aspect_ratio_w = 16
        self.aspect_ratio_h = 9

        # Handle size for resize corners/edges
        self.handle_size = 10

        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(600, 450)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("border: 1px solid #ccc; background: #222;")

    def sizeHint(self):
        """Provide proper size hint for layout."""
        return QSize(800, 600)

    def set_image(self, pixmap: QPixmap):
        """Set the image to display."""
        self.original_pixmap = pixmap
        # Reset transformations when loading new image
        self.rotate_angle = 0.0
        self.flip_horizontal = False
        self.flip_vertical = False
        # Set crop to full image (ensure even dimensions for FFMPEG)
        width = self._round_to_even(pixmap.width())
        height = self._round_to_even(pixmap.height())
        self.crop_rect = QRect(0, 0, width, height)
        # Force widget to calculate proper size before first display
        self.updateGeometry()
        self.update_display()

    def set_crop_rect(self, x: int, y: int, w: int, h: int):
        """Set crop rectangle from external source."""
        if self.original_pixmap:
            # Ensure even values for FFMPEG compatibility
            x = self._round_to_even(x)
            y = self._round_to_even(y)
            w = self._round_to_even(w)
            h = self._round_to_even(h)
            self.crop_rect = QRect(x, y, w, h)
            self.update_display()

    def set_transforms(self, rotate: float, flip_h: bool, flip_v: bool):
        """Set rotation and flip transforms."""
        old_transforms = (self.rotate_angle, self.flip_horizontal, self.flip_vertical)
        new_transforms = (rotate, flip_h, flip_v)

        # If transforms changed, update them but preserve crop if possible
        if old_transforms != new_transforms:
            self.rotate_angle = rotate
            self.flip_horizontal = flip_h
            self.flip_vertical = flip_v

            # Validate and adjust crop to fit within new transformed bounds
            if self.original_pixmap:
                transformed_width, transformed_height = self._get_transformed_size()

                # Constrain existing crop to new bounds
                if self.crop_rect.right() > transformed_width or self.crop_rect.bottom() > transformed_height:
                    # Crop doesn't fit, adjust it
                    x = min(self.crop_rect.x(), max(0, transformed_width - 32))
                    y = min(self.crop_rect.y(), max(0, transformed_height - 32))
                    w = min(self.crop_rect.width(), transformed_width - x)
                    h = min(self.crop_rect.height(), transformed_height - y)

                    # Ensure minimum size and even values
                    w = max(32, self._round_to_even(w))
                    h = max(32, self._round_to_even(h))
                    x = self._round_to_even(x)
                    y = self._round_to_even(y)

                    self.crop_rect = QRect(x, y, w, h)

        self.update_display()

    def set_aspect_ratio(self, locked: bool, ratio_w: int, ratio_h: int):
        """Set aspect ratio constraint."""
        self.aspect_ratio_locked = locked
        self.aspect_ratio_w = ratio_w
        self.aspect_ratio_h = ratio_h

    def update_display(self):
        """Update the displayed image with crop overlay."""
        if not self.original_pixmap:
            return

        # Start with original image
        working_pixmap = self.original_pixmap.copy()

        # FIRST: Apply transformations to the image (rotate/flip)
        from PyQt5.QtGui import QTransform

        # Apply rotation first
        if self.rotate_angle != 0:
            transform = QTransform()
            transform.rotate(self.rotate_angle)
            working_pixmap = working_pixmap.transformed(transform, Qt.SmoothTransformation)

        # Apply flip second
        if self.flip_horizontal or self.flip_vertical:
            transform = QTransform()
            if self.flip_horizontal:
                transform.scale(-1, 1)
            if self.flip_vertical:
                transform.scale(1, -1)
            working_pixmap = working_pixmap.transformed(transform, Qt.SmoothTransformation)

        # Calculate scale factor based on TRANSFORMED image size
        # Make sure widget has a valid size (avoid division by zero)
        widget_size = self.size()
        if widget_size.width() <= 0 or widget_size.height() <= 0:
            widget_size = self.minimumSize()

        transformed_size = working_pixmap.size()
        if transformed_size.width() <= 0 or transformed_size.height() <= 0:
            return

        scale_w = widget_size.width() / transformed_size.width()
        scale_h = widget_size.height() / transformed_size.height()
        self.display_scale = min(scale_w, scale_h, 1.0)  # Don't scale up

        # Scale transformed image to display size
        display_size = transformed_size * self.display_scale
        display_pixmap = working_pixmap.scaled(
            int(display_size.width()),
            int(display_size.height()),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Calculate offset for centering (image might be smaller than widget)
        self.display_offset = QPoint(
            (widget_size.width() - display_pixmap.width()) // 2,
            (widget_size.height() - display_pixmap.height()) // 2
        )

        # SECOND: Draw crop overlay on TRANSFORMED image
        result = QPixmap(display_pixmap.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.drawPixmap(0, 0, display_pixmap)

        # Draw darkened area outside crop
        painter.fillRect(result.rect(), QColor(0, 0, 0, 120))

        # Draw clear crop area
        scaled_crop = self._scale_rect_to_display(self.crop_rect)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(scaled_crop, display_pixmap, scaled_crop)

        # Draw crop border
        pen = QPen(QColor(255, 255, 0), 2)
        painter.setPen(pen)
        painter.drawRect(scaled_crop)

        # Draw resize handles
        self._draw_handles(painter, scaled_crop)

        painter.end()

        self.setPixmap(result)

    def _scale_rect_to_display(self, rect: QRect) -> QRect:
        """Scale a rectangle from original coordinates to display coordinates."""
        return QRect(
            int(rect.x() * self.display_scale),
            int(rect.y() * self.display_scale),
            int(rect.width() * self.display_scale),
            int(rect.height() * self.display_scale)
        )

    def _scale_point_to_original(self, point: QPoint) -> QPoint:
        """Scale a point from display coordinates to original coordinates."""
        if self.display_scale == 0:
            return point
        return QPoint(
            int(point.x() / self.display_scale),
            int(point.y() / self.display_scale)
        )

    def _draw_handles(self, painter: QPainter, rect: QRect):
        """Draw resize handles on crop rectangle."""
        handle_brush = QBrush(QColor(255, 255, 0))
        painter.setBrush(handle_brush)
        painter.setPen(QPen(QColor(0, 0, 0), 1))

        h = self.handle_size

        # Corner handles
        painter.drawRect(rect.left() - h//2, rect.top() - h//2, h, h)  # TL
        painter.drawRect(rect.right() - h//2, rect.top() - h//2, h, h)  # TR
        painter.drawRect(rect.left() - h//2, rect.bottom() - h//2, h, h)  # BL
        painter.drawRect(rect.right() - h//2, rect.bottom() - h//2, h, h)  # BR

        # Edge handles
        painter.drawRect(rect.center().x() - h//2, rect.top() - h//2, h, h)  # T
        painter.drawRect(rect.center().x() - h//2, rect.bottom() - h//2, h, h)  # B
        painter.drawRect(rect.left() - h//2, rect.center().y() - h//2, h, h)  # L
        painter.drawRect(rect.right() - h//2, rect.center().y() - h//2, h, h)  # R

    def _widget_pos_to_pixmap_pos(self, widget_pos: QPoint) -> QPoint:
        """Convert widget coordinates to pixmap coordinates (accounting for centering offset)."""
        # The pixmap is displayed centered in the widget via QLabel's alignment
        # We need to account for this offset
        pixmap = self.pixmap()
        if not pixmap:
            return widget_pos

        # Calculate the actual position of the pixmap within the widget
        widget_rect = self.rect()
        pixmap_rect = pixmap.rect()

        # Calculate offset based on alignment (we use Qt.AlignCenter)
        offset_x = (widget_rect.width() - pixmap_rect.width()) // 2
        offset_y = (widget_rect.height() - pixmap_rect.height()) // 2

        # Subtract offset to get position relative to pixmap
        return QPoint(widget_pos.x() - offset_x, widget_pos.y() - offset_y)

    def _get_handle_at_pos(self, pos: QPoint) -> Optional[str]:
        """Get which resize handle is at the given position."""
        if not self.original_pixmap:
            return None

        # Convert widget position to pixmap position
        pixmap_pos = self._widget_pos_to_pixmap_pos(pos)

        scaled_crop = self._scale_rect_to_display(self.crop_rect)
        h = self.handle_size

        # Check corner handles
        if QRect(scaled_crop.left() - h, scaled_crop.top() - h, h*2, h*2).contains(pixmap_pos):
            return 'tl'
        if QRect(scaled_crop.right() - h, scaled_crop.top() - h, h*2, h*2).contains(pixmap_pos):
            return 'tr'
        if QRect(scaled_crop.left() - h, scaled_crop.bottom() - h, h*2, h*2).contains(pixmap_pos):
            return 'bl'
        if QRect(scaled_crop.right() - h, scaled_crop.bottom() - h, h*2, h*2).contains(pixmap_pos):
            return 'br'

        # Check edge handles
        if QRect(scaled_crop.center().x() - h, scaled_crop.top() - h, h*2, h*2).contains(pixmap_pos):
            return 't'
        if QRect(scaled_crop.center().x() - h, scaled_crop.bottom() - h, h*2, h*2).contains(pixmap_pos):
            return 'b'
        if QRect(scaled_crop.left() - h, scaled_crop.center().y() - h, h*2, h*2).contains(pixmap_pos):
            return 'l'
        if QRect(scaled_crop.right() - h, scaled_crop.center().y() - h, h*2, h*2).contains(pixmap_pos):
            return 'r'

        # Check if inside crop rect (for dragging)
        if scaled_crop.contains(pixmap_pos):
            return 'move'

        return None

    def _resize_with_aspect_ratio(self, rect: QRect, delta: QPoint, handle: str) -> QRect:
        """
        Resize rectangle while maintaining aspect ratio.

        Args:
            rect: Starting rectangle
            delta: Mouse movement delta
            handle: Resize handle identifier

        Returns:
            New rectangle with aspect ratio maintained

        Strategy:
            - Corner handles: Resize both dimensions proportionally
            - Edge handles: Only allow movement on appropriate dimension,
                           adjust other dimension to maintain ratio
        """
        from ...utils.aspect_ratio import (
            calculate_height_from_width,
            calculate_width_from_height
        )

        new_rect = QRect(rect)

        # Determine which dimension to use as "primary" based on handle
        if handle in ['tl', 'br']:
            # Top-left or bottom-right: Use diagonal, width determines height
            if handle == 'tl':
                new_rect.setLeft(rect.left() + delta.x())
                new_rect.setTop(rect.top() + delta.y())
            else:  # br
                new_rect.setRight(rect.right() + delta.x())
                new_rect.setBottom(rect.bottom() + delta.y())

            # Recalculate height based on width
            width = new_rect.width()
            height = calculate_height_from_width(
                width, self.aspect_ratio_w, self.aspect_ratio_h
            )

            # Adjust based on which corner
            if handle == 'tl':
                new_rect.setTop(new_rect.bottom() - height)
            else:
                new_rect.setHeight(height)

        elif handle in ['tr', 'bl']:
            # Top-right or bottom-left: Use diagonal, width determines height
            if handle == 'tr':
                new_rect.setRight(rect.right() + delta.x())
                new_rect.setTop(rect.top() + delta.y())
            else:  # bl
                new_rect.setLeft(rect.left() + delta.x())
                new_rect.setBottom(rect.bottom() + delta.y())

            # Recalculate height based on width
            width = new_rect.width()
            height = calculate_height_from_width(
                width, self.aspect_ratio_w, self.aspect_ratio_h
            )

            # Adjust based on which corner
            if handle == 'tr':
                new_rect.setTop(new_rect.bottom() - height)
            else:
                new_rect.setHeight(height)

        elif handle in ['l', 'r']:
            # Left or right edge: Adjust width, recalculate height
            if handle == 'l':
                new_rect.setLeft(rect.left() + delta.x())
            else:
                new_rect.setRight(rect.right() + delta.x())

            width = new_rect.width()
            height = calculate_height_from_width(
                width, self.aspect_ratio_w, self.aspect_ratio_h
            )

            # Center the height adjustment
            center_y = new_rect.center().y()
            new_rect.setHeight(height)
            new_rect.moveCenter(QPoint(new_rect.center().x(), center_y))

        elif handle in ['t', 'b']:
            # Top or bottom edge: Adjust height, recalculate width
            if handle == 't':
                new_rect.setTop(rect.top() + delta.y())
            else:
                new_rect.setBottom(rect.bottom() + delta.y())

            height = new_rect.height()
            width = calculate_width_from_height(
                height, self.aspect_ratio_w, self.aspect_ratio_h
            )

            # Center the width adjustment
            center_x = new_rect.center().x()
            new_rect.setWidth(width)
            new_rect.moveCenter(QPoint(center_x, new_rect.center().y()))

        return new_rect

    def _round_to_even(self, value: int) -> int:
        """Round value to nearest even number."""
        return (value // 2) * 2

    def _get_transformed_size(self) -> tuple[int, int]:
        """Get the size of the image after transformations are applied."""
        if not self.original_pixmap:
            return (0, 0)

        # Calculate transformed dimensions
        width = self.original_pixmap.width()
        height = self.original_pixmap.height()

        # Normalize angle to 0-359 range
        angle = self.rotate_angle % 360

        # Handle common angles
        if angle in [90, 270]:
            # Rotation by 90° or 270° swaps width and height
            width, height = height, width
        elif angle in [0, 180]:
            # No dimension change for 0° or 180°
            pass
        else:
            # For arbitrary angles, calculate bounding box
            # This matches Qt's QPixmap.transformed() behavior
            import math
            rad = math.radians(angle)
            cos_a = abs(math.cos(rad))
            sin_a = abs(math.sin(rad))

            new_width = int(width * cos_a + height * sin_a)
            new_height = int(width * sin_a + height * cos_a)

            width, height = new_width, new_height

        return (width, height)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press."""
        if event.button() != Qt.LeftButton or not self.original_pixmap:
            return

        handle = self._get_handle_at_pos(event.pos())

        if handle:
            if handle == 'move':
                self.is_dragging = True
            else:
                self.is_resizing = True
                self.resize_handle = handle

            self.drag_start_pos = event.pos()
            self.drag_start_rect = QRect(self.crop_rect)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move."""
        if not self.original_pixmap:
            return

        if self.is_dragging:
            # Move crop rectangle
            # Convert both positions to pixmap space
            current_pixmap_pos = self._widget_pos_to_pixmap_pos(event.pos())
            start_pixmap_pos = self._widget_pos_to_pixmap_pos(self.drag_start_pos)
            delta_display = current_pixmap_pos - start_pixmap_pos

            # Convert delta to original coordinates
            delta_original = self._scale_point_to_original(delta_display) - self._scale_point_to_original(QPoint(0, 0))

            new_rect = QRect(self.drag_start_rect)
            new_rect.translate(delta_original)

            # Constrain to transformed image bounds
            transformed_width, transformed_height = self._get_transformed_size()
            if new_rect.left() < 0:
                new_rect.moveLeft(0)
            if new_rect.top() < 0:
                new_rect.moveTop(0)
            if new_rect.right() > transformed_width:
                new_rect.moveRight(transformed_width)
            if new_rect.bottom() > transformed_height:
                new_rect.moveBottom(transformed_height)

            # Round to even pixels (all values to ensure FFMPEG compatibility)
            new_rect.setX(self._round_to_even(new_rect.x()))
            new_rect.setY(self._round_to_even(new_rect.y()))
            new_rect.setWidth(self._round_to_even(new_rect.width()))
            new_rect.setHeight(self._round_to_even(new_rect.height()))

            self.crop_rect = new_rect
            self.update_display()
            self.crop_changed.emit(self.crop_rect.x(), self.crop_rect.y(),
                                   self.crop_rect.width(), self.crop_rect.height())

        elif self.is_resizing:
            # Resize crop rectangle
            # Convert both positions to pixmap space
            current_pixmap_pos = self._widget_pos_to_pixmap_pos(event.pos())
            start_pixmap_pos = self._widget_pos_to_pixmap_pos(self.drag_start_pos)
            delta_display = current_pixmap_pos - start_pixmap_pos

            # Convert delta to original coordinates
            delta_original = self._scale_point_to_original(delta_display) - self._scale_point_to_original(QPoint(0, 0))

            new_rect = QRect(self.drag_start_rect)

            if self.aspect_ratio_locked:
                # Aspect ratio constrained resize
                new_rect = self._resize_with_aspect_ratio(
                    new_rect, delta_original, self.resize_handle
                )
            else:
                # Free resize (current behavior)
                # Apply resize based on handle
                # Left edge
                if self.resize_handle in ['l', 'tl', 'bl']:
                    new_rect.setLeft(self.drag_start_rect.left() + delta_original.x())
                # Right edge
                if self.resize_handle in ['r', 'tr', 'br']:
                    new_rect.setRight(self.drag_start_rect.right() + delta_original.x())
                # Top edge
                if self.resize_handle in ['t', 'tl', 'tr']:
                    new_rect.setTop(self.drag_start_rect.top() + delta_original.y())
                # Bottom edge
                if self.resize_handle in ['b', 'bl', 'br']:
                    new_rect.setBottom(self.drag_start_rect.bottom() + delta_original.y())

            # Constrain to transformed image bounds
            transformed_width, transformed_height = self._get_transformed_size()
            if new_rect.left() < 0:
                new_rect.setLeft(0)
            if new_rect.top() < 0:
                new_rect.setTop(0)
            if new_rect.right() > transformed_width:
                new_rect.setRight(transformed_width)
            if new_rect.bottom() > transformed_height:
                new_rect.setBottom(transformed_height)

            # Ensure minimum size
            if new_rect.width() < 32:
                if self.resize_handle in ['l', 'tl', 'bl']:
                    new_rect.setLeft(new_rect.right() - 32)
                else:
                    new_rect.setWidth(32)
            if new_rect.height() < 32:
                if self.resize_handle in ['t', 'tl', 'tr']:
                    new_rect.setTop(new_rect.bottom() - 32)
                else:
                    new_rect.setHeight(32)

            # Round to even pixels
            new_rect = new_rect.normalized()
            new_rect.setX(self._round_to_even(new_rect.x()))
            new_rect.setY(self._round_to_even(new_rect.y()))
            new_rect.setWidth(self._round_to_even(new_rect.width()))
            new_rect.setHeight(self._round_to_even(new_rect.height()))

            self.crop_rect = new_rect
            self.update_display()
            self.crop_changed.emit(self.crop_rect.x(), self.crop_rect.y(),
                                   self.crop_rect.width(), self.crop_rect.height())

        else:
            # Update cursor based on hover
            handle = self._get_handle_at_pos(event.pos())
            if handle == 'move':
                self.setCursor(QCursor(Qt.SizeAllCursor))
            elif handle in ['tl', 'br']:
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
            elif handle in ['tr', 'bl']:
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
            elif handle in ['t', 'b']:
                self.setCursor(QCursor(Qt.SizeVerCursor))
            elif handle in ['l', 'r']:
                self.setCursor(QCursor(Qt.SizeHorCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.is_resizing = False
            self.resize_handle = None


class InteractiveCropWidget(QWidget):
    """Widget for interactive crop selection."""

    crop_changed = pyqtSignal(int, int, int, int)
    refresh_requested = pyqtSignal()
    image_changed = pyqtSignal(Path)  # Signal when a different image is loaded

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__(parent)
        self.image_files = []  # List of all image files in sequence
        self.current_image_index = 0
        self.pending_image_index = 0  # Index to load after debounce

        # Debounce timer for image loading
        self.image_load_timer = QTimer()
        self.image_load_timer.setSingleShot(True)
        self.image_load_timer.timeout.connect(self._load_pending_image)

        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Image navigation slider at top
        nav_layout = QHBoxLayout()

        nav_label = QLabel("Bild:")
        nav_layout.addWidget(nav_label)

        self.image_slider = QSlider(Qt.Horizontal)
        self.image_slider.setMinimum(0)
        self.image_slider.setMaximum(0)
        self.image_slider.setValue(0)
        self.image_slider.setEnabled(False)
        self.image_slider.valueChanged.connect(self.on_image_slider_changed)
        nav_layout.addWidget(self.image_slider, 1)

        # Direct image number input
        self.image_spinbox = QSpinBox()
        self.image_spinbox.setMinimum(1)
        self.image_spinbox.setMaximum(1)
        self.image_spinbox.setValue(1)
        self.image_spinbox.setEnabled(False)
        self.image_spinbox.setPrefix("Nr. ")
        self.image_spinbox.setMinimumWidth(80)
        self.image_spinbox.valueChanged.connect(self.on_image_spinbox_changed)
        nav_layout.addWidget(self.image_spinbox)

        self.image_counter_label = QLabel("/ 0")
        self.image_counter_label.setMinimumWidth(50)
        self.image_counter_label.setAlignment(Qt.AlignLeft)
        nav_layout.addWidget(self.image_counter_label)

        layout.addLayout(nav_layout)

        # Interactive crop label
        self.crop_label = InteractiveCropLabel()
        self.crop_label.crop_changed.connect(self.crop_changed.emit)
        layout.addWidget(self.crop_label)

        # Info label
        self.info_label = QLabel("Kein Bild geladen")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.load_btn = QPushButton("Beispielbild laden")
        self.load_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(self.load_btn)

        self.reset_btn = QPushButton("Vollbild")
        self.reset_btn.clicked.connect(self.reset_crop)
        button_layout.addWidget(self.reset_btn)

        layout.addLayout(button_layout)

    def set_image_sequence(self, image_files: list):
        """Set the list of images in the sequence."""
        self.image_files = image_files
        if image_files:
            self.current_image_index = 0
            self.image_slider.setMaximum(len(image_files) - 1)
            self.image_slider.setValue(0)
            self.image_slider.setEnabled(True)
            self.image_spinbox.setMaximum(len(image_files))
            self.image_spinbox.setValue(1)
            self.image_spinbox.setEnabled(True)
            self.update_image_counter()
            self.load_image(image_files[0])
        else:
            self.image_slider.setEnabled(False)
            self.image_spinbox.setEnabled(False)
            self.image_counter_label.setText("/ 0")

    def on_image_slider_changed(self, value: int):
        """Handle image slider value change."""
        if 0 <= value < len(self.image_files):
            # Update spinbox without triggering its signal
            self.image_spinbox.blockSignals(True)
            self.image_spinbox.setValue(value + 1)
            self.image_spinbox.blockSignals(False)
            self.update_image_counter_display(value)

            # Debounce: wait 200ms before loading image
            self.pending_image_index = value
            self.image_load_timer.stop()
            self.image_load_timer.start(200)

    def on_image_spinbox_changed(self, value: int):
        """Handle image spinbox value change (1-based)."""
        # Convert 1-based to 0-based index
        index = value - 1
        if 0 <= index < len(self.image_files):
            # Update slider without triggering its signal
            self.image_slider.blockSignals(True)
            self.image_slider.setValue(index)
            self.image_slider.blockSignals(False)
            self.update_image_counter_display(index)

            # Debounce: wait 200ms before loading image
            self.pending_image_index = index
            self.image_load_timer.stop()
            self.image_load_timer.start(200)

    def _load_pending_image(self):
        """Load the pending image after debounce delay."""
        if 0 <= self.pending_image_index < len(self.image_files):
            self.current_image_index = self.pending_image_index
            self.load_image(self.image_files[self.pending_image_index])

    def update_image_counter(self):
        """Update the image counter label."""
        if self.image_files:
            self.image_counter_label.setText(f"/ {len(self.image_files)}")

    def update_image_counter_display(self, index: int):
        """Update image counter display without loading image."""
        # Just update the display, actual image loading is debounced
        pass  # Counter is now part of spinbox, no separate update needed

    def load_image(self, image_path: Path):
        """Load an image for crop selection."""
        if not image_path.exists():
            self.info_label.setText("Bild nicht gefunden")
            return

        pixmap = QPixmap(str(image_path))

        if pixmap.isNull():
            self.info_label.setText("Fehler beim Laden des Bildes")
            return

        # Save current crop settings and transformations before loading new image
        saved_crop = None
        saved_transforms = None
        if self.crop_label.original_pixmap:
            saved_crop = QRect(self.crop_label.crop_rect)
            saved_transforms = (
                self.crop_label.rotate_angle,
                self.crop_label.flip_horizontal,
                self.crop_label.flip_vertical
            )

        self.crop_label.set_image(pixmap)

        # Restore transformations BEFORE restoring crop (transforms affect dimensions)
        if saved_transforms is not None:
            rotate, flip_h, flip_v = saved_transforms
            # Manually set transforms without resetting crop
            self.crop_label.rotate_angle = rotate
            self.crop_label.flip_horizontal = flip_h
            self.crop_label.flip_vertical = flip_v

        # Restore crop settings if they exist and are valid for new image
        if saved_crop is not None:
            # Get transformed dimensions to check bounds
            transformed_width, transformed_height = self.crop_label._get_transformed_size()

            # Check if saved crop fits within transformed image dimensions
            if (saved_crop.right() <= transformed_width and
                saved_crop.bottom() <= transformed_height):
                self.crop_label.set_crop_rect(
                    saved_crop.x(), saved_crop.y(),
                    saved_crop.width(), saved_crop.height()
                )
            else:
                # Adjust crop to fit within new bounds
                x = min(saved_crop.x(), max(0, transformed_width - 32))
                y = min(saved_crop.y(), max(0, transformed_height - 32))
                w = min(saved_crop.width(), transformed_width - x)
                h = min(saved_crop.height(), transformed_height - y)

                # Ensure even values
                w = max(32, self.crop_label._round_to_even(w))
                h = max(32, self.crop_label._round_to_even(h))
                x = self.crop_label._round_to_even(x)
                y = self.crop_label._round_to_even(y)

                self.crop_label.set_crop_rect(x, y, w, h)

        # Update display with current transforms
        self.crop_label.update_display()

        # Force layout recalculation to prevent resize after load
        self.updateGeometry()
        self.crop_label.updateGeometry()

        # Show current image info
        info_text = f"Bild: {pixmap.width()}x{pixmap.height()}"
        if len(self.image_files) > 1:
            info_text += f" | {image_path.name}"
        info_text += " | Ziehen Sie das gelbe Rechteck"

        self.info_label.setText(info_text)

        # Emit signal that image changed
        self.image_changed.emit(image_path)

    def set_crop(self, x: int, y: int, w: int, h: int):
        """Set crop rectangle from external source."""
        self.crop_label.set_crop_rect(x, y, w, h)

    def reset_crop(self):
        """Reset crop to full image."""
        if self.crop_label.original_pixmap:
            pixmap = self.crop_label.original_pixmap
            # Ensure even dimensions for FFMPEG compatibility
            width = self.crop_label._round_to_even(pixmap.width())
            height = self.crop_label._round_to_even(pixmap.height())
            self.crop_label.set_crop_rect(0, 0, width, height)
            self.crop_changed.emit(0, 0, width, height)

    def clear(self):
        """Clear the widget."""
        self.crop_label.original_pixmap = None
        self.crop_label.clear()
        self.info_label.setText("Kein Bild geladen")
