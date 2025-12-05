"""FFMPEG executable locator."""

import shutil
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from .constants import FFMPEG_CONFIG_FILE, USER_PRESETS_FOLDER_NAME


def get_user_config_path() -> Path:
    """
    Get user configuration directory path.

    Returns:
        Path to user config directory
    """
    if sys.platform == "win32":
        # Windows: %APPDATA%/FFMPEG_Timeslap
        appdata = Path.home() / "AppData" / "Roaming"
        config_path = appdata / USER_PRESETS_FOLDER_NAME
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/FFMPEG_Timeslap
        config_path = Path.home() / "Library" / "Application Support" / USER_PRESETS_FOLDER_NAME
    else:
        # Linux: ~/.config/FFMPEG_Timeslap
        config_path = Path.home() / ".config" / USER_PRESETS_FOLDER_NAME

    # Create if it doesn't exist
    config_path.mkdir(parents=True, exist_ok=True)

    return config_path


def find_ffmpeg() -> str:
    """
    Find FFMPEG executable in following order:
    1. System PATH
    2. Bundled binary
    3. User-configured path

    Returns:
        Path to ffmpeg executable

    Raises:
        FileNotFoundError: If FFMPEG is not found
    """
    # 1. Check system PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # 2. Check bundled binary
    bundled_path = get_bundled_ffmpeg_path()
    if bundled_path and bundled_path.exists():
        return str(bundled_path)

    # 3. Check user-configured path
    custom_path = get_custom_ffmpeg_path()
    if custom_path and Path(custom_path).exists():
        return custom_path

    raise FileNotFoundError(
        "FFMPEG wurde nicht gefunden. Bitte installieren Sie FFMPEG oder konfigurieren Sie den Pfad in den Einstellungen."
    )


def get_bundled_ffmpeg_path() -> Optional[Path]:
    """
    Get path to bundled FFMPEG binary.

    Returns:
        Path to bundled FFMPEG or None if not available
    """
    # Get path to this file's parent directories
    # This file is in src/ffmpeg_timeslap/utils/
    # Bundled binary should be in ffmpeg_binaries/windows/ffmpeg.exe
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent

    if sys.platform == "win32":
        bundled_path = project_root / "ffmpeg_binaries" / "windows" / "ffmpeg.exe"
    elif sys.platform == "darwin":
        bundled_path = project_root / "ffmpeg_binaries" / "macos" / "ffmpeg"
    else:
        bundled_path = project_root / "ffmpeg_binaries" / "linux" / "ffmpeg"

    return bundled_path if bundled_path.exists() else None


def get_custom_ffmpeg_path() -> Optional[str]:
    """
    Get user-configured FFMPEG path from config file.

    Returns:
        Path to FFMPEG or None if not configured
    """
    config_file = get_user_config_path() / FFMPEG_CONFIG_FILE

    if not config_file.exists():
        return None

    try:
        custom_path = config_file.read_text().strip()
        if custom_path and Path(custom_path).exists():
            return custom_path
    except Exception:
        return None

    return None


def set_custom_ffmpeg_path(path: str) -> None:
    """
    Save custom FFMPEG path to config file.

    Args:
        path: Path to FFMPEG executable
    """
    config_file = get_user_config_path() / FFMPEG_CONFIG_FILE
    config_file.write_text(path)


def get_ffmpeg_version(ffmpeg_path: str) -> Optional[str]:
    """
    Get FFMPEG version string.

    Args:
        ffmpeg_path: Path to FFMPEG executable

    Returns:
        Version string or None if failed
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # First line contains version info
            first_line = result.stdout.split('\n')[0]
            return first_line
        return None
    except Exception:
        return None


def check_ffmpeg_available() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if FFMPEG is available and get its version.

    Returns:
        Tuple of (is_available, ffmpeg_path, version_string)
    """
    try:
        ffmpeg_path = find_ffmpeg()
        version = get_ffmpeg_version(ffmpeg_path)
        return (True, ffmpeg_path, version)
    except FileNotFoundError:
        return (False, None, None)


def get_available_encoders(ffmpeg_path: str) -> list[str]:
    """
    Get list of available video encoders from FFMPEG.

    Args:
        ffmpeg_path: Path to FFMPEG executable

    Returns:
        List of available encoder names
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-encoders"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return []

        encoders = []
        # Parse output: lines starting with " V" are video encoders
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('V'):
                # Format: " V..... libx264              H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (codec h264)"
                parts = line.split()
                if len(parts) >= 2:
                    encoder_name = parts[1]
                    encoders.append(encoder_name)

        return encoders

    except Exception:
        return []


def check_codec_available(ffmpeg_path: str, codec: str) -> bool:
    """
    Check if a specific codec is available in FFMPEG.

    Args:
        ffmpeg_path: Path to FFMPEG executable
        codec: Codec name (e.g., "libx264", "libx265", "libsvtav1")

    Returns:
        True if codec is available
    """
    encoders = get_available_encoders(ffmpeg_path)
    return codec in encoders
