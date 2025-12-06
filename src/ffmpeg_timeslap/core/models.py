"""Data models for FFMPEG Timeslap application."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class SequenceInfo:
    """Information about detected image sequence."""

    pattern: str  # e.g. "IMG_%04d.JPG"
    count: int
    start_number: int
    end_number: int
    image_width: int
    image_height: int
    image_format: str  # e.g. "JPEG", "PNG"
    has_gaps: bool
    gaps: List[int] = field(default_factory=list)
    needs_padding: bool = False  # True if dimensions are odd
    use_concat: bool = False  # True if gaps exist
    concat_file: Optional[Path] = None

    @property
    def dimensions_str(self) -> str:
        """Return dimensions as string."""
        return f"{self.image_width}x{self.image_height}"

    @property
    def range_str(self) -> str:
        """Return number range as string."""
        return f"{self.start_number} - {self.end_number}"


@dataclass
class EncodingConfig:
    """Configuration for FFMPEG encoding."""

    # Input/Output
    input_folder: Path
    output_folder: Path
    output_filename: str = "timelapse.mp4"

    # Sequence info
    sequence_info: Optional[SequenceInfo] = None

    # Basic settings
    framerate: int = 25
    codec: str = "libx264"
    crf: int = 18
    preset: str = "medium"
    output_resolution: str = "original"  # or "1920x1080", "3840x2160", etc.
    custom_resolution: Optional[str] = None  # for custom "WIDTHxHEIGHT"

    # Advanced settings
    profile: str = "high"
    level: str = "4.0"
    pixel_format: str = "yuv420p"
    movflags_faststart: bool = True
    start_number: Optional[int] = None
    pattern_type: str = "sequential"  # or "glob"
    custom_args: str = ""

    # Filters
    deflicker_enabled: bool = False
    deflicker_mode: str = "pm"
    deflicker_size: int = 10

    crop_enabled: bool = False
    crop_x: int = 0
    crop_y: int = 0
    crop_w: int = 0
    crop_h: int = 0

    # Aspect ratio settings for crop
    aspect_ratio_locked: bool = False
    aspect_ratio_mode: str = "free"  # "free", "preset", "custom", "auto"
    aspect_ratio_preset: str = "16:9"
    aspect_ratio_custom_w: int = 16
    aspect_ratio_custom_h: int = 9

    rotate_enabled: bool = False
    rotate_angle: float = 0.0  # Any angle in degrees (0-359)

    flip_enabled: bool = False
    flip_horizontal: bool = False
    flip_vertical: bool = False

    @property
    def output_path(self) -> Path:
        """Return full output file path."""
        return self.output_folder / self.output_filename

    @property
    def needs_padding(self) -> bool:
        """Check if padding filter is needed."""
        if self.sequence_info:
            return self.sequence_info.needs_padding
        return False

    @property
    def use_concat(self) -> bool:
        """Check if concat file should be used."""
        if self.sequence_info:
            return self.sequence_info.use_concat
        return False


@dataclass
class ValidationResult:
    """Result of input validation."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)


@dataclass
class ProgressInfo:
    """Progress information during encoding."""

    current_frame: Optional[int] = None
    total_frames: Optional[int] = None
    fps: Optional[float] = None
    elapsed_seconds: Optional[float] = None
    percentage: Optional[int] = None

    @property
    def is_valid(self) -> bool:
        """Check if progress info contains valid data."""
        return self.current_frame is not None and self.percentage is not None


@dataclass
class ErrorInfo:
    """Error information from FFMPEG."""

    user_message: str
    technical_details: str
    recoverable: bool = False
