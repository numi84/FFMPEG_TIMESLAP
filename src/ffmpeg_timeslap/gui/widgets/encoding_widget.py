"""Widget for encoding controls and progress."""

from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QProgressBar, QTextEdit, QLabel
)
from PyQt5.QtCore import pyqtSignal


class EncodingWidget(QGroupBox):
    """Widget for encoding controls and progress display."""

    # Signals
    preview_requested = pyqtSignal()
    start_requested = pyqtSignal()
    cancel_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__("Encoding", parent)
        self.is_encoding = False
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.preview_btn = QPushButton("Vorschau")
        self.preview_btn.setToolTip("FFMPEG-Befehl anzeigen ohne zu starten")
        self.preview_btn.clicked.connect(self.on_preview_clicked)
        button_layout.addWidget(self.preview_btn)

        button_layout.addStretch()

        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("QPushButton { font-weight: bold; min-height: 30px; }")
        self.start_btn.clicked.connect(self.on_start_clicked)
        button_layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Progress section
        self.progress_label = QLabel("Bereit")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # FFMPEG Output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)
        self.output_text.setPlaceholderText("FFMPEG-Output wird hier angezeigt...")
        layout.addWidget(self.output_text)

    def on_preview_clicked(self):
        """Handle preview button click."""
        self.preview_requested.emit()

    def on_start_clicked(self):
        """Handle start button click."""
        if not self.is_encoding:
            self.start_requested.emit()

    def on_cancel_clicked(self):
        """Handle cancel button click."""
        if self.is_encoding:
            self.cancel_requested.emit()

    def set_encoding_state(self, encoding: bool):
        """
        Set encoding state (enable/disable controls).

        Args:
            encoding: True if encoding is in progress
        """
        self.is_encoding = encoding

        self.preview_btn.setEnabled(not encoding)
        self.start_btn.setEnabled(not encoding)
        self.cancel_btn.setEnabled(encoding)

        if encoding:
            self.start_btn.setText("Läuft...")
            self.progress_label.setText("Encoding läuft...")
        else:
            self.start_btn.setText("Start")
            self.progress_label.setText("Bereit")

    def update_progress(self, percentage: int):
        """
        Update progress bar.

        Args:
            percentage: Progress percentage (0-100)
        """
        self.progress_bar.setValue(percentage)

    def append_output(self, text: str):
        """
        Append text to output display.

        Args:
            text: Text to append
        """
        # Use insertPlainText instead of append to avoid QTextCursor threading issues
        self.output_text.moveCursor(self.output_text.textCursor().End)
        self.output_text.insertPlainText(text.rstrip() + '\n')
        # Auto-scroll to bottom
        self.output_text.ensureCursorVisible()

    def clear_output(self):
        """Clear output display."""
        self.output_text.clear()

    def reset_progress(self):
        """Reset progress bar to 0."""
        self.progress_bar.setValue(0)
        self.progress_label.setText("Bereit")

    def set_status_message(self, message: str):
        """
        Set status message.

        Args:
            message: Status message
        """
        self.progress_label.setText(message)

    def show_completion_message(self, success: bool, message: str):
        """
        Show completion message.

        Args:
            success: True if encoding succeeded
            message: Completion message
        """
        if success:
            self.progress_label.setText(f"✓ {message}")
            self.progress_bar.setValue(100)
        else:
            self.progress_label.setText(f"✗ {message}")

        self.set_encoding_state(False)
