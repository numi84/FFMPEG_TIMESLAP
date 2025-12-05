"""Constants for FFMPEG Timeslap application."""

from typing import Dict, List, Tuple

# Codecs
CODECS: List[Tuple[str, str]] = [
    ("libx264", "H.264 (libx264) - Beste Kompatibilität"),
    ("libx265", "H.265 (libx265) - Kleinere Dateien"),
    ("libsvtav1", "AV1 (libsvtav1) - Modernster Codec"),
]

DEFAULT_CODEC = "libx264"

# Encoding Presets
ENCODING_PRESETS: List[str] = [
    "ultrafast",
    "superfast",
    "veryfast",
    "faster",
    "fast",
    "medium",
    "slow",
    "slower",
    "veryslow",
]

DEFAULT_PRESET = "medium"

# Profiles
PROFILES: List[str] = [
    "baseline",
    "main",
    "high",
    "high10",
    "high422",
    "high444",
]

DEFAULT_PROFILE = "high"

# Levels
LEVELS: List[str] = [
    "3.0",
    "3.1",
    "4.0",
    "4.1",
    "4.2",
    "5.0",
    "5.1",
    "5.2",
]

DEFAULT_LEVEL = "4.0"

# Pixel Formats
PIXEL_FORMATS: List[str] = [
    "yuv420p",
    "yuv422p",
    "yuv444p",
]

DEFAULT_PIXEL_FORMAT = "yuv420p"

# Framerates
FRAMERATES: List[int] = [10, 15, 24, 25, 30, 60]

DEFAULT_FRAMERATE = 25

# CRF Quality Presets
CRF_PRESETS: Dict[str, int] = {
    "Verlustfrei": 0,
    "Sehr gut": 18,
    "Gut": 23,
    "Kompakt": 28,
}

DEFAULT_CRF = 18

# Output Resolutions
RESOLUTIONS: List[Tuple[str, str]] = [
    ("original", "Original beibehalten"),
    ("3840x2160", "3840x2160 (4K UHD)"),
    ("2560x1440", "2560x1440 (QHD/2K)"),
    ("1920x1080", "1920x1080 (Full HD)"),
    ("1280x720", "1280x720 (HD)"),
    ("854x480", "854x480 (SD)"),
    ("custom", "Custom"),
]

DEFAULT_RESOLUTION = "original"

# Deflicker Modes
DEFLICKER_MODES: List[str] = [
    "pm",  # Progressive Mean
    "am",  # Arithmetic Mean
]

DEFAULT_DEFLICKER_MODE = "pm"
DEFAULT_DEFLICKER_SIZE = 10

# Rotate Angles
ROTATE_ANGLES: List[Tuple[int, str]] = [
    (0, "0° (Keine Rotation)"),
    (90, "90° (Im Uhrzeigersinn)"),
    (180, "180° (Auf den Kopf)"),
    (270, "270° (Gegen Uhrzeigersinn)"),
]

DEFAULT_ROTATE_ANGLE = 0

# Supported Image Formats
SUPPORTED_IMAGE_FORMATS: List[str] = [
    ".jpg",
    ".jpeg",
    ".JPG",
    ".JPEG",
    ".png",
    ".PNG",
    ".tiff",
    ".TIFF",
]

# Pattern Types
PATTERN_TYPES: List[str] = [
    "sequential",
    "glob",
]

DEFAULT_PATTERN_TYPE = "sequential"

# App Settings
APP_NAME = "FFMPEG Timeslap"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Christian Neumayer"

# Config paths (will be resolved at runtime)
USER_PRESETS_FOLDER_NAME = "FFMPEG_Timeslap"
USER_PRESETS_SUBFOLDER = "presets"
FFMPEG_CONFIG_FILE = "ffmpeg_path.txt"
