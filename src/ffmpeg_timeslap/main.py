"""Main entry point for FFMPEG Timeslap application."""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from .gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("FFMPEG Timeslap")
    app.setOrganizationName("Christian Neumayer")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
