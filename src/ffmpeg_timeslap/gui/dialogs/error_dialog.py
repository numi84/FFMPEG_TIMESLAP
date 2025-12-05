"""Dialog for displaying errors."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt

from ...core.models import ErrorInfo


class ErrorDialog(QDialog):
    """Dialog for displaying error information."""

    def __init__(self, error_info: ErrorInfo, parent=None):
        """
        Initialize dialog.

        Args:
            error_info: ErrorInfo object with error details
            parent: Parent widget
        """
        super().__init__(parent)
        self.error_info = error_info
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        self.setWindowTitle("Fehler")
        self.setMinimumSize(500, 350)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Error icon and message
        message_label = QLabel(f"❌ {self.error_info.user_message}")
        message_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d32f2f;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Recoverable hint
        if self.error_info.recoverable:
            hint_label = QLabel(
                "💡 Dieser Fehler kann möglicherweise durch Anpassen der Einstellungen behoben werden."
            )
            hint_label.setStyleSheet("color: #f57c00;")
            hint_label.setWordWrap(True)
            layout.addWidget(hint_label)

        # Technical details
        details_label = QLabel("Technische Details:")
        details_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(details_label)

        self.details_text = QTextEdit()
        self.details_text.setPlainText(self.error_info.technical_details)
        self.details_text.setReadOnly(True)
        # Monospace font
        font = self.details_text.font()
        font.setFamily("Courier New")
        font.setPointSize(9)
        self.details_text.setFont(font)
        layout.addWidget(self.details_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_btn = QPushButton("Schließen")
        self.close_btn.setDefault(True)
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)


def show_error_dialog(error_info: ErrorInfo, parent=None):
    """
    Show error dialog.

    Args:
        error_info: ErrorInfo object
        parent: Parent widget
    """
    dialog = ErrorDialog(error_info, parent)
    dialog.exec_()
