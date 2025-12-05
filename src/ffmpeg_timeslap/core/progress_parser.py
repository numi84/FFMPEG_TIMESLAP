"""FFMPEG output parser for progress tracking."""

import re
from typing import Optional

from .models import ProgressInfo


class ProgressParser:
    """Parses FFMPEG output for progress information."""

    def __init__(self, total_frames: Optional[int] = None):
        """
        Initialize progress parser.

        Args:
            total_frames: Total number of frames to encode
        """
        self.total_frames = total_frames

        # FFMPEG output patterns
        self.frame_pattern = re.compile(r'frame=\s*(\d+)')
        self.fps_pattern = re.compile(r'fps=\s*([\d.]+)')
        self.time_pattern = re.compile(r'time=(\d+):(\d+):([\d.]+)')
        self.speed_pattern = re.compile(r'speed=\s*([\d.]+)x')

    def set_total_frames(self, total: int) -> None:
        """
        Set total number of frames for percentage calculation.

        Args:
            total: Total number of frames
        """
        self.total_frames = total

    def parse_output(self, text: str) -> ProgressInfo:
        """
        Parse FFMPEG output for progress information.

        Args:
            text: FFMPEG output text

        Returns:
            ProgressInfo object with extracted information
        """
        info = ProgressInfo()

        # Extract current frame number
        frame_match = self.frame_pattern.search(text)
        if frame_match:
            info.current_frame = int(frame_match.group(1))

        # Extract FPS
        fps_match = self.fps_pattern.search(text)
        if fps_match:
            info.fps = float(fps_match.group(1))

        # Extract time
        time_match = self.time_pattern.search(text)
        if time_match:
            hours, minutes, seconds = time_match.groups()
            info.elapsed_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

        # Calculate percentage if total frames is known
        if self.total_frames and info.current_frame:
            info.percentage = min(int((info.current_frame / self.total_frames) * 100), 100)
            info.total_frames = self.total_frames

        return info

    def extract_error_message(self, output: str) -> Optional[str]:
        """
        Extract error message from FFMPEG output.

        Args:
            output: FFMPEG output/error text

        Returns:
            Error message or None
        """
        # Look for common error patterns
        error_patterns = [
            r"Error.*?:\s*(.+)",
            r"(.+):\s*No such file or directory",
            r"(.+):\s*Permission denied",
            r"Invalid.*?:\s*(.+)",
            r"Unknown.*?:\s*(.+)",
        ]

        for pattern in error_patterns:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(0).strip()

        # If no specific error pattern found, return last non-empty line
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        if lines:
            return lines[-1]

        return None

    def is_encoding_started(self, output: str) -> bool:
        """
        Check if encoding has started.

        Args:
            output: FFMPEG output text

        Returns:
            True if encoding has started
        """
        # Look for frame= in output
        return self.frame_pattern.search(output) is not None

    def is_completed(self, output: str) -> bool:
        """
        Check if encoding is completed.

        Args:
            output: FFMPEG output text

        Returns:
            True if encoding completed successfully
        """
        # Look for common completion indicators
        completion_patterns = [
            r'video:\d+kB',  # Final statistics line
            r'muxing overhead',
            r'Conversion successful',
        ]

        for pattern in completion_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return True

        return False

    def get_estimated_time_remaining(self, current_frame: int, fps: float) -> Optional[float]:
        """
        Estimate time remaining for encoding.

        Args:
            current_frame: Current frame number
            fps: Current encoding FPS

        Returns:
            Estimated seconds remaining or None
        """
        if not self.total_frames or not fps or fps <= 0:
            return None

        remaining_frames = self.total_frames - current_frame

        if remaining_frames <= 0:
            return 0.0

        return remaining_frames / fps

    def format_time_remaining(self, seconds: Optional[float]) -> str:
        """
        Format estimated time remaining as human-readable string.

        Args:
            seconds: Seconds remaining

        Returns:
            Formatted string (e.g., "2m 30s" or "Unknown")
        """
        if seconds is None:
            return "Unbekannt"

        if seconds < 60:
            return f"{int(seconds)}s"

        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)

        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"

        hours = minutes // 60
        remaining_minutes = minutes % 60

        return f"{hours}h {remaining_minutes}m"
