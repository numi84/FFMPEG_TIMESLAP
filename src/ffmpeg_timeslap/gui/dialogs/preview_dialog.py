"""Dialog for previewing FFMPEG command."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QApplication
)
from PyQt5.QtCore import Qt


class PreviewDialog(QDialog):
    """Dialog for previewing and copying FFMPEG command."""

    def __init__(self, command_string: str, parent=None):
        """
        Initialize dialog.

        Args:
            command_string: FFMPEG command string to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.command_string = command_string
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        self.setWindowTitle("FFMPEG Command Vorschau")
        self.setMinimumSize(700, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Info label
        info_label = QLabel(
            "Dies ist der FFMPEG-Befehl, der ausgeführt wird. "
            "Sie können ihn kopieren und manuell in der Kommandozeile ausführen."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Command text
        self.command_text = QTextEdit()
        self.command_text.setPlainText(self.command_string)
        self.command_text.setReadOnly(True)
        self.command_text.setFont(self.command_text.font())
        # Monospace font for better readability
        font = self.command_text.font()
        font.setFamily("Courier New")
        self.command_text.setFont(font)
        layout.addWidget(self.command_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.copy_btn = QPushButton("In Zwischenablage kopieren")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)

        button_layout.addStretch()

        self.close_btn = QPushButton("Schließen")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def copy_to_clipboard(self):
        """Copy command to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.command_string)

        # Temporarily change button text
        original_text = self.copy_btn.text()
        self.copy_btn.setText("✓ Kopiert!")
        self.copy_btn.setEnabled(False)

        # Reset after 2 seconds
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.reset_copy_button(original_text))

    def reset_copy_button(self, original_text: str):
        """Reset copy button to original state."""
        self.copy_btn.setText(original_text)
        self.copy_btn.setEnabled(True)
