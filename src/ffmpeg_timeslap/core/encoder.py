"""FFMPEG encoding process management."""

import subprocess
from typing import List, Optional, Callable
from pathlib import Path

from .models import EncodingConfig, ErrorInfo
from .command_builder import FFmpegCommandBuilder
from .progress_parser import ProgressParser
from ..utils.ffmpeg_locator import find_ffmpeg


class FFmpegEncoder:
    """Manages FFMPEG encoding process."""

    def __init__(self, config: EncodingConfig):
        """
        Initialize encoder.

        Args:
            config: EncodingConfig with all settings
        """
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.ffmpeg_path = find_ffmpeg()

        # Build command
        builder = FFmpegCommandBuilder(config, self.ffmpeg_path)
        self.command = builder.build()

        # Progress parser
        self.parser = ProgressParser()

        if config.sequence_info:
            self.parser.set_total_frames(config.sequence_info.count)

        # Callbacks
        self.on_progress: Optional[Callable[[int], None]] = None
        self.on_output: Optional[Callable[[str], None]] = None
        self.on_finished: Optional[Callable[[bool, str], None]] = None

    def get_command_string(self) -> str:
        """
        Get command as string for preview.

        Returns:
            Command string
        """
        builder = FFmpegCommandBuilder(self.config, self.ffmpeg_path)
        return builder.build_as_string()

    def start_encoding(self) -> bool:
        """
        Start encoding process.

        Returns:
            True if process started successfully
        """
        try:
            # Prepare concat file if needed
            if self.config.use_concat and self.config.sequence_info:
                from .sequence_detector import generate_concat_file, get_image_files

                image_files = get_image_files(self.config.input_folder)
                # Save concat file in input folder to keep paths simple
                concat_file = generate_concat_file(image_files, self.config.input_folder)
                self.config.sequence_info.concat_file = concat_file

                # Rebuild command with concat file
                builder = FFmpegCommandBuilder(self.config, self.ffmpeg_path)
                self.command = builder.build()

            # Start process
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr to stdout
                universal_newlines=True,
                bufsize=1
            )

            return True

        except Exception as e:
            if self.on_finished:
                self.on_finished(False, f"Failed to start encoding: {e}")
            return False

    def wait_for_completion(self) -> bool:
        """
        Wait for encoding to complete (blocking).

        Returns:
            True if encoding completed successfully
        """
        if not self.process:
            return False

        try:
            # Read output line by line
            for line in self.process.stdout:
                # Parse progress
                progress_info = self.parser.parse_output(line)

                # Notify progress callback
                if self.on_progress and progress_info.percentage is not None:
                    self.on_progress(progress_info.percentage)

                # Notify output callback
                if self.on_output:
                    self.on_output(line)

            # Wait for process to finish
            return_code = self.process.wait()

            # Check success
            success = (return_code == 0)

            # Notify completion
            if self.on_finished:
                if success:
                    self.on_finished(True, "Encoding completed successfully!")
                else:
                    self.on_finished(False, f"Encoding failed with code {return_code}")

            return success

        except Exception as e:
            if self.on_finished:
                self.on_finished(False, f"Error during encoding: {e}")
            return False

    def cancel_encoding(self) -> None:
        """Cancel running encoding process."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def is_running(self) -> bool:
        """
        Check if encoding is currently running.

        Returns:
            True if process is running
        """
        return self.process is not None and self.process.poll() is None


class EncodingErrorHandler:
    """Handles and analyzes FFMPEG errors."""

    @staticmethod
    def analyze_error(error_output: str) -> ErrorInfo:
        """
        Analyze FFMPEG error output.

        Args:
            error_output: Error output from FFMPEG

        Returns:
            ErrorInfo with user-friendly message
        """
        error_patterns = {
            r"No such file or directory": (
                "Eingabedatei nicht gefunden",
                "Überprüfen Sie den Input-Ordner und die Dateinamen",
                True
            ),
            r"Invalid pixel format": (
                "Ungültiges Pixelformat",
                "Das gewählte Pixelformat wird vom Codec nicht unterstützt",
                True
            ),
            r"height not divisible by 2": (
                "Bildgröße nicht durch 2 teilbar",
                "Aktivieren Sie den Padding-Filter für ungerade Dimensionen",
                True
            ),
            r"width not divisible by 2": (
                "Bildbreite nicht durch 2 teilbar",
                "Aktivieren Sie den Padding-Filter für ungerade Dimensionen",
                True
            ),
            r"Permission denied": (
                "Zugriff verweigert",
                "Keine Schreibberechtigung für den Output-Ordner",
                True
            ),
            r"Codec .* not found": (
                "Codec nicht gefunden",
                "Der gewählte Codec ist in Ihrer FFMPEG-Installation nicht verfügbar",
                False
            ),
            r"Unknown encoder": (
                "Unbekannter Encoder",
                "Der gewählte Codec ist nicht verfügbar",
                False
            ),
        }

        for pattern, (user_msg, details, recoverable) in error_patterns.items():
            if re.search(pattern, error_output, re.IGNORECASE):
                return ErrorInfo(
                    user_message=user_msg,
                    technical_details=f"{details}\n\nTechnische Details:\n{error_output}",
                    recoverable=recoverable
                )

        # Unknown error
        return ErrorInfo(
            user_message="Ein unbekannter Fehler ist aufgetreten",
            technical_details=error_output,
            recoverable=False
        )


# Import for error pattern matching
import re
