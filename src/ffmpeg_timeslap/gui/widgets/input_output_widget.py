"""Widget for input/output folder selection."""

from PyQt5.QtWidgets import (
    QGroupBox, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog
)
from PyQt5.QtCore import pyqtSignal
from pathlib import Path


class InputOutputWidget(QGroupBox):
    """Widget for selecting input and output folders."""

    # Signals
    input_folder_changed = pyqtSignal(Path)
    output_folder_changed = pyqtSignal(Path)
    output_filename_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize widget."""
        super().__init__("Input / Output", parent)

        self.setup_ui()

    def setup_ui(self):
        """Setup user interface."""
        layout = QGridLayout()
        self.setLayout(layout)

        # Input folder
        layout.addWidget(QLabel("Input Ordner:"), 0, 0)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Wählen Sie einen Ordner mit Bildern...")
        self.input_edit.textChanged.connect(self.on_input_changed)
        layout.addWidget(self.input_edit, 0, 1)

        self.input_browse_btn = QPushButton("Durchsuchen...")
        self.input_browse_btn.clicked.connect(self.browse_input)
        layout.addWidget(self.input_browse_btn, 0, 2)

        # Output folder
        layout.addWidget(QLabel("Output Ordner:"), 1, 0)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Wählen Sie einen Ausgabe-Ordner...")
        self.output_edit.textChanged.connect(self.on_output_changed)
        layout.addWidget(self.output_edit, 1, 1)

        self.output_browse_btn = QPushButton("Durchsuchen...")
        self.output_browse_btn.clicked.connect(self.browse_output)
        layout.addWidget(self.output_browse_btn, 1, 2)

        # Output filename
        layout.addWidget(QLabel("Dateiname:"), 2, 0)

        self.filename_edit = QLineEdit("timelapse.mp4")
        self.filename_edit.textChanged.connect(self.on_filename_changed)
        layout.addWidget(self.filename_edit, 2, 1, 1, 2)

        # Set column stretch
        layout.setColumnStretch(1, 1)

    def browse_input(self):
        """Browse for input folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Input Ordner wählen",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )

        if folder:
            self.input_edit.setText(folder)

    def browse_output(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Output Ordner wählen",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )

        if folder:
            self.output_edit.setText(folder)

    def on_input_changed(self):
        """Handle input folder change."""
        text = self.input_edit.text()
        if text:
            self.input_folder_changed.emit(Path(text))

    def on_output_changed(self):
        """Handle output folder change."""
        text = self.output_edit.text()
        if text:
            self.output_folder_changed.emit(Path(text))

    def on_filename_changed(self):
        """Handle filename change."""
        text = self.filename_edit.text()
        if text:
            self.output_filename_changed.emit(text)

    def get_input_folder(self) -> Path:
        """Get input folder path."""
        return Path(self.input_edit.text()) if self.input_edit.text() else Path.home()

    def get_output_folder(self) -> Path:
        """Get output folder path."""
        return Path(self.output_edit.text()) if self.output_edit.text() else Path.home()

    def get_output_filename(self) -> str:
        """Get output filename."""
        return self.filename_edit.text() or "timelapse.mp4"

    def set_input_folder(self, path: Path):
        """Set input folder."""
        self.input_edit.setText(str(path))

    def set_output_folder(self, path: Path):
        """Set output folder."""
        self.output_edit.setText(str(path))

    def set_output_filename(self, filename: str):
        """Set output filename."""
        self.filename_edit.setText(filename)
