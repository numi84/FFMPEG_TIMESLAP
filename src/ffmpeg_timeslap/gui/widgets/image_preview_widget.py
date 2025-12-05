"""Image preview widget for crop and rotate visualization."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QTransform
from pathlib import Path
from typing import Optional


class ImagePreviewWidget(QWidget):
    """Widget to preview crop and rotate effects on an image."""

    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__(parent)
        self.original_pixmap: Optional[QPixmap] = None
        self.displayed_pixmap: Optional[QPixmap] = None

        # Transform settings
        self.crop_enabled = False
        self.crop_x = 0
        self.crop_y = 0
        self.crop_w = 0
        self.crop_h = 0
        self.rotate_angle = 0

        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background: #222;")
        self.image_label.setScaledContents(False)
        layout.addWidget(self.image_label)

        # Info label
        self.info_label = QLabel("Kein Bild geladen")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.load_btn = QPushButton("Beispielbild laden")
        self.load_btn.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(self.load_btn)

        self.reset_btn = QPushButton("Ansicht zurücksetzen")
        self.reset_btn.clicked.connect(self.reset_view)
        button_layout.addWidget(self.reset_btn)

        layout.addLayout(button_layout)

    def load_image(self, image_path: Path):
        """
        Load an image for preview.

        Args:
            image_path: Path to image file
        """
        if not image_path.exists():
            self.info_label.setText("Bild nicht gefunden")
            return

        self.original_pixmap = QPixmap(str(image_path))

        if self.original_pixmap.isNull():
            self.info_label.setText("Fehler beim Laden des Bildes")
            return

        self.info_label.setText(
            f"Original: {self.original_pixmap.width()}x{self.original_pixmap.height()}"
        )

        self.update_preview()

    def set_crop(self, enabled: bool, x: int, y: int, w: int, h: int):
        """
        Set crop settings.

        Args:
            enabled: Whether crop is enabled
            x: Crop x position
            y: Crop y position
            w: Crop width
            h: Crop height
        """
        self.crop_enabled = enabled
        self.crop_x = x
        self.crop_y = y
        self.crop_w = w
        self.crop_h = h
        self.update_preview()

    def set_rotate(self, angle: int):
        """
        Set rotation angle.

        Args:
            angle: Rotation angle (0, 90, 180, 270)
        """
        self.rotate_angle = angle
        self.update_preview()

    def update_preview(self):
        """Update the preview with current transform settings."""
        if not self.original_pixmap:
            return

        # Start with original
        pixmap = self.original_pixmap.copy()

        # Apply rotation first (before crop)
        if self.rotate_angle != 0:
            transform = QTransform()
            transform.rotate(self.rotate_angle)
            pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

        # Apply crop after rotation
        if self.crop_enabled and self.crop_w > 0 and self.crop_h > 0:
            crop_rect = QRect(self.crop_x, self.crop_y, self.crop_w, self.crop_h)

            # Validate crop rect against transformed image size
            if (crop_rect.right() <= pixmap.width() and
                crop_rect.bottom() <= pixmap.height()):
                pixmap = pixmap.copy(crop_rect)
            else:
                self.info_label.setText("Crop-Bereich außerhalb des Bildes!")
                return

        self.displayed_pixmap = pixmap

        # Scale to fit label while maintaining aspect ratio
        scaled = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled)

        # Update info
        info_parts = [f"Vorschau: {pixmap.width()}x{pixmap.height()}"]

        if self.crop_enabled:
            info_parts.append(f"Crop: {self.crop_w}x{self.crop_h} @ ({self.crop_x},{self.crop_y})")

        if self.rotate_angle != 0:
            info_parts.append(f"Rotation: {self.rotate_angle}°")

        self.info_label.setText(" | ".join(info_parts))

    def draw_crop_overlay(self):
        """Draw crop rectangle overlay on original image."""
        if not self.original_pixmap or not self.crop_enabled:
            return

        # Create a copy to draw on
        pixmap = self.original_pixmap.copy()
        painter = QPainter(pixmap)

        # Draw semi-transparent overlay
        overlay_color = QColor(0, 0, 0, 128)
        painter.fillRect(pixmap.rect(), overlay_color)

        # Draw clear crop area
        crop_rect = QRect(self.crop_x, self.crop_y, self.crop_w, self.crop_h)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(crop_rect, Qt.transparent)

        # Draw crop border
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawRect(crop_rect)

        painter.end()

        # Display with crop overlay
        scaled = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

    def reset_view(self):
        """Reset to original image view."""
        if self.original_pixmap:
            self.update_preview()

    def clear(self):
        """Clear the preview."""
        self.original_pixmap = None
        self.displayed_pixmap = None
        self.image_label.clear()
        self.info_label.setText("Kein Bild geladen")
