"""Widget for displaying image sequence information."""

from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel
from PyQt5.QtCore import Qt
from typing import Optional

from ...core.models import SequenceInfo
from ...core.sequence_detector import get_estimated_duration, format_duration


class SequenceInfoWidget(QGroupBox):
    """Widget for displaying detected sequence information (read-only)."""

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__("Bildsequenz-Informationen", parent)

        self.setup_ui()
        self.clear()

    def setup_ui(self):
        """Setup user interface."""
        layout = QFormLayout()
        self.setLayout(layout)

        # Pattern
        self.pattern_label = QLabel("-")
        layout.addRow("Muster:", self.pattern_label)

        # Count
        self.count_label = QLabel("-")
        layout.addRow("Anzahl Bilder:", self.count_label)

        # Range
        self.range_label = QLabel("-")
        layout.addRow("Nummerierungsbereich:", self.range_label)

        # Dimensions
        self.dimensions_label = QLabel("-")
        layout.addRow("Bildgröße:", self.dimensions_label)

        # Estimated duration
        self.duration_label = QLabel("-")
        layout.addRow("Geschätzte Länge:", self.duration_label)

        # Warnings/Status
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: orange; font-weight: bold;")
        self.warning_label.setWordWrap(True)
        layout.addRow("", self.warning_label)

    def update_info(self, sequence_info: SequenceInfo, framerate: int = 25):
        """
        Update displayed information.

        Args:
            sequence_info: SequenceInfo object with detected sequence
            framerate: Framerate for duration estimation
        """
        if not sequence_info:
            self.clear()
            return

        # Pattern
        self.pattern_label.setText(sequence_info.pattern)

        # Count
        self.count_label.setText(f"{sequence_info.count} Bilder")

        # Range
        range_text = f"{sequence_info.start_number} - {sequence_info.end_number}"
        self.range_label.setText(range_text)

        # Dimensions
        dim_text = sequence_info.dimensions_str
        if sequence_info.needs_padding:
            dim_text += " (ungerade - Padding wird angewendet)"
        self.dimensions_label.setText(dim_text)

        # Estimated duration
        duration = get_estimated_duration(sequence_info.count, framerate)
        duration_text = format_duration(duration)
        duration_text += f" @ {framerate} fps"
        self.duration_label.setText(duration_text)

        # Warnings
        warnings = []

        if sequence_info.has_gaps:
            gap_count = len(sequence_info.gaps)
            warnings.append(
                f"⚠ {gap_count} fehlende Bilder erkannt (Nummern: {', '.join(map(str, sequence_info.gaps[:5]))}"
                f"{', ...' if gap_count > 5 else ''}). "
                "Concat-Modus wird verwendet."
            )

        if sequence_info.needs_padding:
            warnings.append(
                "⚠ Bildgröße hat ungerade Dimensionen. "
                "Padding-Filter wird automatisch angewendet."
            )

        if warnings:
            self.warning_label.setText("\n".join(warnings))
            self.warning_label.show()
        else:
            self.warning_label.hide()

    def clear(self):
        """Clear all information."""
        self.pattern_label.setText("-")
        self.count_label.setText("-")
        self.range_label.setText("-")
        self.dimensions_label.setText("-")
        self.duration_label.setText("-")
        self.warning_label.clear()
        self.warning_label.hide()

    def set_framerate_for_duration(self, framerate: int, sequence_info: Optional[SequenceInfo]):
        """
        Update duration display with new framerate.

        Args:
            framerate: New framerate
            sequence_info: Current sequence info
        """
        if sequence_info:
            duration = get_estimated_duration(sequence_info.count, framerate)
            duration_text = format_duration(duration)
            duration_text += f" @ {framerate} fps"
            self.duration_label.setText(duration_text)
