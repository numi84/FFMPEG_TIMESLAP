"""Main application window."""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QAction, QStatusBar, QMessageBox, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from pathlib import Path
import threading

from ..core.models import EncodingConfig
from ..core.sequence_detector import detect_sequence
from ..core.command_builder import FFmpegCommandBuilder
from ..core.encoder import FFmpegEncoder
from ..presets.preset_manager import PresetManager
from ..utils.constants import APP_NAME, APP_VERSION
from ..utils.ffmpeg_locator import check_ffmpeg_available, find_ffmpeg
from ..utils.validators import validate_encoding_config

from .widgets.preset_widget import PresetWidget
from .widgets.input_output_widget import InputOutputWidget
from .widgets.sequence_info_widget import SequenceInfoWidget
from .widgets.basic_settings_widget import BasicSettingsWidget
from .widgets.advanced_settings_widget import AdvancedSettingsWidget
from .widgets.filter_settings_widget import FilterSettingsWidget
from .widgets.encoding_widget import EncodingWidget
from .widgets.interactive_crop_widget import InteractiveCropWidget

from .dialogs.preview_dialog import PreviewDialog
from .dialogs.save_preset_dialog import show_save_preset_dialog
from .dialogs.error_dialog import show_error_dialog, ErrorInfo


class EncodingSignals(QObject):
    """Signals for thread-safe encoding updates."""
    progress = pyqtSignal(int)
    output = pyqtSignal(str)
    finished = pyqtSignal(bool, str)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()

        # Configuration
        # Debug defaults for faster testing
        debug_input = Path("E:/Projekte/Tests")
        debug_output = Path("E:/Projekte")

        self.config = EncodingConfig(
            input_folder=debug_input if debug_input.exists() else Path.home(),
            output_folder=debug_output if debug_output.exists() else Path.home()
        )

        # Preset manager
        self.preset_manager = PresetManager()

        # Encoder
        self.encoder = None
        self.encoding_thread = None
        self.encoding_signals = EncodingSignals()

        # Connect encoding signals
        self.encoding_signals.progress.connect(self.on_encoding_progress)
        self.encoding_signals.output.connect(self.on_encoding_output)
        self.encoding_signals.finished.connect(self.on_encoding_finished)

        # Setup UI
        self.setup_ui()

        # Check FFMPEG availability
        self.check_ffmpeg()

    def setup_ui(self):
        """Setup user interface."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1920, 1080)  # Full-HD minimum

        # Create menu bar
        self.create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # ==== TOP ROW: Presets, Input/Output, Sequenz-Info ====
        top_row = QHBoxLayout()

        # Left side: Presets + Input/Output
        left_top = QVBoxLayout()

        self.preset_widget = PresetWidget(self.preset_manager)
        self.preset_widget.preset_loaded.connect(self.on_preset_loaded)
        self.preset_widget.preset_saved.connect(self.on_save_preset)
        left_top.addWidget(self.preset_widget)

        self.input_output_widget = InputOutputWidget()
        self.input_output_widget.input_folder_changed.connect(self.on_input_folder_changed)
        self.input_output_widget.output_folder_changed.connect(self.on_output_folder_changed)
        self.input_output_widget.output_filename_changed.connect(self.on_output_filename_changed)
        left_top.addWidget(self.input_output_widget)

        # Right side: Sequenz-Info
        right_top = QVBoxLayout()
        self.sequence_info_widget = SequenceInfoWidget()
        right_top.addWidget(self.sequence_info_widget)
        right_top.addStretch()  # Push to top

        # Combine top left and right (2:1 ratio)
        top_row.addLayout(left_top, 2)
        top_row.addLayout(right_top, 1)

        main_layout.addLayout(top_row)

        # ==== MIDDLE ROW: Tabs + Preview ====
        # Use QSplitter for resizable divider between tabs and preview
        middle_splitter = QSplitter(Qt.Horizontal)

        # Left: Settings tabs
        self.settings_tabs = QTabWidget()

        self.basic_settings = BasicSettingsWidget()
        self.basic_settings.framerate_changed.connect(self.on_framerate_changed)
        self.settings_tabs.addTab(self.basic_settings, "Basis")

        self.advanced_settings = AdvancedSettingsWidget()
        self.settings_tabs.addTab(self.advanced_settings, "Erweitert")

        self.filter_settings = FilterSettingsWidget()
        self.settings_tabs.addTab(self.filter_settings, "Filter")

        middle_splitter.addWidget(self.settings_tabs)

        # Right: Preview widget (always visible)
        self.preview_widget = InteractiveCropWidget()
        self.preview_widget.refresh_requested.connect(self._load_preview_image)
        self.preview_widget.crop_changed.connect(self.on_crop_changed_from_preview)
        self.preview_widget.image_changed.connect(self.filter_settings.on_preview_image_changed)
        middle_splitter.addWidget(self.preview_widget)

        # Set initial sizes: 35% for tabs, 65% for preview
        # Calculate based on Full-HD width (1920px)
        middle_splitter.setSizes([672, 1248])  # 35% and 65% of 1920px
        middle_splitter.setStretchFactor(0, 35)
        middle_splitter.setStretchFactor(1, 65)

        main_layout.addWidget(middle_splitter, 1)  # Middle row stretches to fill

        # ==== BOTTOM ROW: Encoding ====
        self.encoding_widget = EncodingWidget()
        self.encoding_widget.preview_requested.connect(self.on_preview_requested)
        self.encoding_widget.start_requested.connect(self.on_start_requested)
        self.encoding_widget.cancel_requested.connect(self.on_cancel_requested)
        main_layout.addWidget(self.encoding_widget)

        # Connect preview widget to filter settings
        self.filter_settings.preview_widget = self.preview_widget

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bereit")

    def create_menu_bar(self):
        """Create menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&Datei")

        open_action = QAction("Ordner öffnen...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open_folder)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Presets menu
        presets_menu = menu_bar.addMenu("&Presets")

        save_preset_action = QAction("Preset speichern...", self)
        save_preset_action.setShortcut("Ctrl+S")
        save_preset_action.triggered.connect(self.on_save_preset)
        presets_menu.addAction(save_preset_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Hilfe")

        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        ffmpeg_info_action = QAction("FFMPEG Info", self)
        ffmpeg_info_action.triggered.connect(self.show_ffmpeg_info)
        help_menu.addAction(ffmpeg_info_action)

    def check_ffmpeg(self):
        """Check if FFMPEG is available."""
        available, path, version = check_ffmpeg_available()

        if available:
            self.status_bar.showMessage(f"FFMPEG gefunden: {path}")
        else:
            QMessageBox.warning(
                self,
                "FFMPEG nicht gefunden",
                "FFMPEG wurde nicht gefunden.\n\n"
                "Bitte installieren Sie FFMPEG oder konfigurieren Sie "
                "den Pfad in den Einstellungen.\n\n"
                "Download: https://ffmpeg.org/download.html"
            )

    def on_open_folder(self):
        """Handle open folder action."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Input Ordner wählen",
            str(self.config.input_folder),
        )

        if folder:
            self.input_output_widget.set_input_folder(Path(folder))

    def on_input_folder_changed(self, folder: Path):
        """Handle input folder change."""
        self.config.input_folder = folder
        self.status_bar.showMessage(f"Analysiere Bildsequenz in: {folder}")

        # Detect sequence
        sequence_info = detect_sequence(folder)

        if sequence_info:
            # Generate concat file if needed
            if sequence_info.use_concat and sequence_info.concat_file is None:
                from ..core.sequence_detector import get_image_files, generate_concat_file
                image_files = get_image_files(folder)
                concat_file = generate_concat_file(image_files, folder)
                sequence_info.concat_file = concat_file

            self.config.sequence_info = sequence_info
            self.config.start_number = sequence_info.start_number
            self.sequence_info_widget.update_info(
                sequence_info,
                self.basic_settings.get_framerate()
            )

            # Update status message with gap info
            if sequence_info.has_gaps:
                gap_count = len(sequence_info.gaps)
                self.status_bar.showMessage(
                    f"✓ {sequence_info.count} Bilder erkannt in: {folder} (Concat-Modus: {gap_count} Lücken)"
                )
            else:
                self.status_bar.showMessage(
                    f"✓ {sequence_info.count} Bilder erkannt in: {folder}"
                )

            # Load first image into preview
            self._load_preview_image()
        else:
            self.config.sequence_info = None
            self.sequence_info_widget.clear()
            self.status_bar.showMessage("✗ Keine gültige Bildsequenz gefunden")
            QMessageBox.warning(
                self,
                "Keine Bildsequenz gefunden",
                f"Im Ordner '{folder}' wurde keine gültige Bildsequenz gefunden.\n\n"
                "Stellen Sie sicher, dass:\n"
                "- Die Bilder nummeriert sind (z.B. IMG_0001.jpg)\n"
                "- Unterstützte Formate verwendet werden (JPG, PNG, TIFF)"
            )

    def on_output_folder_changed(self, folder: Path):
        """Handle output folder change."""
        self.config.output_folder = folder

    def on_output_filename_changed(self, filename: str):
        """Handle output filename change."""
        self.config.output_filename = filename

    def on_framerate_changed(self, framerate: int):
        """Handle framerate change."""
        # Update duration display in sequence info
        if self.config.sequence_info:
            self.sequence_info_widget.set_framerate_for_duration(
                framerate,
                self.config.sequence_info
            )

    def on_preset_loaded(self, preset_name: str):
        """Handle preset loaded."""
        success = self.preset_manager.apply_preset_to_config(preset_name, self.config)

        if success:
            # Update UI from config
            self.apply_config_to_ui()
            self.status_bar.showMessage(f"Preset '{preset_name}' geladen")
        else:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Preset '{preset_name}' konnte nicht geladen werden."
            )

    def on_save_preset(self):
        """Handle save preset action."""
        # Update config from UI
        self.update_config_from_ui()

        # Show dialog
        result = show_save_preset_dialog(self)

        if result:
            name, description = result
            success = self.preset_manager.save_preset(name, self.config, description)

            if success:
                self.preset_widget.refresh_presets()
                QMessageBox.information(
                    self,
                    "Preset gespeichert",
                    f"Preset '{name}' wurde erfolgreich gespeichert."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    f"Preset '{name}' konnte nicht gespeichert werden."
                )

    def on_preview_requested(self):
        """Handle preview request."""
        # Update config from UI
        self.update_config_from_ui()

        # Validate
        validation = validate_encoding_config(self.config)

        if not validation.valid:
            error_msg = "\n".join(validation.errors)
            QMessageBox.warning(
                self,
                "Validierungsfehler",
                f"Bitte beheben Sie folgende Fehler:\n\n{error_msg}"
            )
            return

        # Build command
        try:
            ffmpeg_path = find_ffmpeg()
            builder = FFmpegCommandBuilder(self.config, ffmpeg_path)
            command_string = builder.build_as_string()

            # Show preview dialog
            dialog = PreviewDialog(command_string, self)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Erstellen des Befehls:\n\n{str(e)}"
            )

    def on_start_requested(self):
        """Handle start encoding request."""
        # Update config from UI
        self.update_config_from_ui()

        # Check if output file exists
        if self.config.output_path.exists():
            reply = QMessageBox.question(
                self,
                "Datei überschreiben?",
                f"Die Datei existiert bereits:\n\n{self.config.output_path}\n\n"
                "Möchten Sie sie überschreiben?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        # Validate
        validation = validate_encoding_config(self.config)

        if not validation.valid:
            error_msg = "\n".join(validation.errors)
            QMessageBox.warning(
                self,
                "Validierungsfehler",
                f"Bitte beheben Sie folgende Fehler:\n\n{error_msg}"
            )
            return

        # Show warnings if any
        if validation.warnings:
            warning_msg = "\n".join(validation.warnings)
            reply = QMessageBox.question(
                self,
                "Warnungen",
                f"Folgende Warnungen wurden gefunden:\n\n{warning_msg}\n\n"
                "Möchten Sie trotzdem fortfahren?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        # Start encoding in thread
        self.start_encoding()

    def on_cancel_requested(self):
        """Handle cancel encoding request."""
        if self.encoder:
            self.encoder.cancel_encoding()
            self.status_bar.showMessage("Encoding abgebrochen")

    def start_encoding(self):
        """Start encoding in background thread."""
        try:
            # Create encoder
            self.encoder = FFmpegEncoder(self.config)

            # Setup callbacks with signals for thread-safety
            self.encoder.on_progress = lambda p: self.encoding_signals.progress.emit(p)
            self.encoder.on_output = lambda o: self.encoding_signals.output.emit(o)
            self.encoder.on_finished = lambda s, m: self.encoding_signals.finished.emit(s, m)

            # Update UI
            self.encoding_widget.set_encoding_state(True)
            self.encoding_widget.clear_output()
            self.encoding_widget.reset_progress()

            # Start encoding
            success = self.encoder.start_encoding()

            if success:
                # Run in thread
                self.encoding_thread = threading.Thread(
                    target=self.encoder.wait_for_completion,
                    daemon=True
                )
                self.encoding_thread.start()
            else:
                self.encoding_widget.set_encoding_state(False)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Starten des Encodings:\n\n{str(e)}"
            )
            self.encoding_widget.set_encoding_state(False)

    def on_encoding_progress(self, percentage: int):
        """Handle encoding progress update."""
        self.encoding_widget.update_progress(percentage)

    def on_encoding_output(self, text: str):
        """Handle encoding output."""
        self.encoding_widget.append_output(text)

    def on_encoding_finished(self, success: bool, message: str):
        """Handle encoding finished."""
        self.encoding_widget.show_completion_message(success, message)

        if success:
            self.status_bar.showMessage(f"✓ {message}")
            QMessageBox.information(
                self,
                "Encoding abgeschlossen",
                f"Video erfolgreich erstellt:\n\n{self.config.output_path}"
            )
        else:
            self.status_bar.showMessage(f"✗ {message}")
            # Show error dialog if available
            # For now, just a message box
            QMessageBox.critical(
                self,
                "Encoding fehlgeschlagen",
                f"Encoding fehlgeschlagen:\n\n{message}"
            )

    def update_config_from_ui(self):
        """Update configuration from all widgets."""
        # Basic settings
        self.config.framerate = self.basic_settings.get_framerate()
        self.config.codec = self.basic_settings.get_codec()
        self.config.crf = self.basic_settings.get_crf()
        self.config.preset = self.basic_settings.get_preset()
        self.config.output_resolution = self.basic_settings.get_resolution()
        self.config.custom_resolution = self.basic_settings.get_custom_resolution()

        # Advanced settings
        self.config.profile = self.advanced_settings.get_profile()
        self.config.level = self.advanced_settings.get_level()
        self.config.pixel_format = self.advanced_settings.get_pixel_format()
        self.config.movflags_faststart = self.advanced_settings.get_movflags_faststart()
        self.config.custom_args = self.advanced_settings.get_custom_args()

        # Filter settings
        self.config.deflicker_enabled = self.filter_settings.is_deflicker_enabled()
        self.config.deflicker_mode = self.filter_settings.get_deflicker_mode()
        self.config.deflicker_size = self.filter_settings.get_deflicker_size()

        self.config.crop_enabled = self.filter_settings.is_crop_enabled()
        self.config.crop_x = self.filter_settings.get_crop_x()
        self.config.crop_y = self.filter_settings.get_crop_y()
        self.config.crop_w = self.filter_settings.get_crop_width()
        self.config.crop_h = self.filter_settings.get_crop_height()

        # Aspect ratio settings
        self.config.aspect_ratio_locked = self.filter_settings.is_aspect_ratio_locked()
        self.config.aspect_ratio_preset = self.filter_settings.get_aspect_ratio_preset()
        self.config.aspect_ratio_custom_w = self.filter_settings.get_aspect_ratio_custom_w()
        self.config.aspect_ratio_custom_h = self.filter_settings.get_aspect_ratio_custom_h()
        # Determine mode based on preset
        preset = self.config.aspect_ratio_preset
        if preset == "Free":
            self.config.aspect_ratio_mode = "free"
        elif preset == "Custom":
            self.config.aspect_ratio_mode = "custom"
        else:
            self.config.aspect_ratio_mode = "preset"

        self.config.rotate_enabled = self.filter_settings.is_rotate_enabled()
        self.config.rotate_angle = self.filter_settings.get_rotate_angle()

        self.config.flip_enabled = self.filter_settings.is_flip_enabled()
        self.config.flip_horizontal = self.filter_settings.is_flip_horizontal()
        self.config.flip_vertical = self.filter_settings.is_flip_vertical()

    def apply_config_to_ui(self):
        """Apply configuration to all widgets."""
        # Basic settings
        self.basic_settings.set_framerate(self.config.framerate)
        self.basic_settings.set_codec(self.config.codec)
        self.basic_settings.set_crf_value(self.config.crf)
        self.basic_settings.set_encoding_preset(self.config.preset)
        self.basic_settings.set_resolution(
            self.config.output_resolution,
            self.config.custom_resolution
        )

        # Advanced settings
        self.advanced_settings.set_profile(self.config.profile)
        self.advanced_settings.set_level(self.config.level)
        self.advanced_settings.set_pixel_format(self.config.pixel_format)
        self.advanced_settings.set_movflags_faststart(self.config.movflags_faststart)
        self.advanced_settings.set_custom_args(self.config.custom_args)

        # Filter settings
        self.filter_settings.set_deflicker_enabled(self.config.deflicker_enabled)
        self.filter_settings.set_deflicker_mode(self.config.deflicker_mode)
        self.filter_settings.set_deflicker_size(self.config.deflicker_size)

        self.filter_settings.set_crop_enabled(self.config.crop_enabled)
        self.filter_settings.set_crop_values(
            self.config.crop_x, self.config.crop_y,
            self.config.crop_w, self.config.crop_h
        )

        # Aspect ratio settings
        self.filter_settings.set_aspect_ratio_locked(self.config.aspect_ratio_locked)
        self.filter_settings.set_aspect_ratio_preset(self.config.aspect_ratio_preset)
        self.filter_settings.set_aspect_ratio_custom(
            self.config.aspect_ratio_custom_w,
            self.config.aspect_ratio_custom_h
        )

        self.filter_settings.set_rotate_enabled(self.config.rotate_enabled)
        self.filter_settings.set_rotate_angle(self.config.rotate_angle)

        self.filter_settings.set_flip_enabled(self.config.flip_enabled)
        self.filter_settings.set_flip_horizontal(self.config.flip_horizontal)
        self.filter_settings.set_flip_vertical(self.config.flip_vertical)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"Über {APP_NAME}",
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            f"<p>Eine benutzerfreundliche Anwendung zur Erstellung von "
            f"Timelapse-Videos aus Bildsequenzen.</p>"
            f"<p><b>Autor:</b> Christian Neumayer<br>"
            f"<b>Email:</b> numi@nech.at</p>"
            f"<p><b>FFMPEG:</b> Video encoding powered by FFMPEG<br>"
            f"<b>Lizenz:</b> MIT</p>"
        )

    def show_ffmpeg_info(self):
        """Show FFMPEG information."""
        available, path, version = check_ffmpeg_available()

        if available:
            info_text = f"<b>FFMPEG gefunden</b><br><br>"
            info_text += f"<b>Pfad:</b> {path}<br>"
            info_text += f"<b>Version:</b><br><pre>{version}</pre>"
        else:
            info_text = "<b>FFMPEG nicht gefunden</b><br><br>"
            info_text += "Bitte installieren Sie FFMPEG oder konfigurieren Sie den Pfad."

        QMessageBox.information(self, "FFMPEG Information", info_text)

    def on_crop_changed_from_preview(self, x: int, y: int, w: int, h: int):
        """Handle crop change from preview widget."""
        self.filter_settings.on_crop_changed_from_preview(x, y, w, h)

    def _load_preview_image(self):
        """Load the first image from sequence into preview."""
        if not self.config.sequence_info:
            return

        try:
            # Get all images from sequence
            from ..core.sequence_detector import get_image_files
            image_files = get_image_files(self.config.input_folder)

            if image_files:
                first_image = image_files[0]
                # Load image into preview widget with full sequence
                self.filter_settings.load_preview_image(first_image, image_files)

        except Exception as e:
            print(f"Failed to load preview image: {e}")
