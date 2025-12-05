"""Image sequence detection and analysis."""

import re
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image

from .models import SequenceInfo
from ..utils.constants import SUPPORTED_IMAGE_FORMATS


def detect_sequence(input_folder: Path) -> Optional[SequenceInfo]:
    """
    Detect image sequence in given folder.

    Args:
        input_folder: Path to folder containing images

    Returns:
        SequenceInfo object or None if no valid sequence found
    """
    if not input_folder.exists() or not input_folder.is_dir():
        return None

    # Get all image files
    image_files = get_image_files(input_folder)

    if not image_files:
        return None

    # Analyze naming patterns
    pattern_info = analyze_naming_pattern(image_files)

    if not pattern_info:
        return None

    prefix, padding, extension, numbers = pattern_info

    # Build FFMPEG pattern
    if padding > 0:
        ffmpeg_pattern = f"{prefix}%0{padding}d{extension}"
    else:
        ffmpeg_pattern = f"{prefix}%d{extension}"

    # Detect gaps
    has_gaps, gaps = detect_gaps(numbers)

    # Get image dimensions from first image
    first_image = image_files[0]
    width, height, img_format = get_image_info(first_image)

    # Check if dimensions are odd (need padding)
    needs_padding = (width % 2 != 0) or (height % 2 != 0)

    # Create SequenceInfo
    sequence_info = SequenceInfo(
        pattern=ffmpeg_pattern,
        count=len(image_files),
        start_number=min(numbers),
        end_number=max(numbers),
        image_width=width,
        image_height=height,
        image_format=img_format,
        has_gaps=has_gaps,
        gaps=gaps,
        needs_padding=needs_padding,
        use_concat=has_gaps,  # Use concat if gaps exist
        concat_file=None  # Will be set later if needed
    )

    return sequence_info


def get_image_files(folder: Path) -> List[Path]:
    """
    Get all image files in folder, sorted by name.

    Args:
        folder: Path to folder

    Returns:
        List of image file paths
    """
    image_files = []

    for file in folder.iterdir():
        if file.is_file() and file.suffix in SUPPORTED_IMAGE_FORMATS:
            image_files.append(file)

    return sorted(image_files)


def analyze_naming_pattern(files: List[Path]) -> Optional[Tuple[str, int, str, List[int]]]:
    """
    Analyze naming pattern of image files.

    Args:
        files: List of image file paths

    Returns:
        Tuple of (prefix, padding_length, extension, numbers) or None if no pattern found
    """
    if not files:
        return None

    # Try to extract pattern from filenames
    # Pattern: prefix + number + extension
    # e.g., "IMG_0001.jpg" -> prefix="IMG_", number=1 (padding=4), ext=".jpg"

    numbers = []
    prefixes = []
    extensions = []

    for file in files:
        match = re.match(r'^(.+?)(\d+)(\.\w+)$', file.name)

        if match:
            prefix, number_str, extension = match.groups()
            numbers.append(int(number_str))
            prefixes.append(prefix)
            extensions.append(extension)

    # Check if all files have the same prefix and extension
    if not numbers:
        return None

    unique_prefixes = set(prefixes)
    unique_extensions = set(extensions)

    if len(unique_prefixes) != 1 or len(unique_extensions) != 1:
        # Mixed naming patterns - not supported
        return None

    prefix = prefixes[0]
    extension = extensions[0]

    # Determine padding length (leading zeros)
    # Check the first file's number string
    first_file = files[0]
    match = re.match(r'^.+?(\d+)\.\w+$', first_file.name)

    if match:
        number_str = match.group(1)
        padding = len(number_str) if number_str.startswith('0') else 0
    else:
        padding = 0

    return (prefix, padding, extension, numbers)


def detect_gaps(numbers: List[int]) -> Tuple[bool, List[int]]:
    """
    Detect gaps in number sequence.

    Args:
        numbers: List of numbers

    Returns:
        Tuple of (has_gaps, list_of_missing_numbers)
    """
    if not numbers:
        return (False, [])

    numbers = sorted(numbers)
    expected = set(range(min(numbers), max(numbers) + 1))
    actual = set(numbers)

    missing = sorted(expected - actual)

    return (len(missing) > 0, missing)


def get_image_info(image_path: Path) -> Tuple[int, int, str]:
    """
    Get image dimensions and format.

    Args:
        image_path: Path to image file

    Returns:
        Tuple of (width, height, format)
    """
    try:
        with Image.open(image_path) as img:
            return (img.width, img.height, img.format)
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return (0, 0, "UNKNOWN")


def generate_concat_file(image_files: List[Path], output_path: Path) -> Path:
    """
    Generate concat file for non-sequential images.

    Args:
        image_files: List of image file paths
        output_path: Directory where to save concat file

    Returns:
        Path to generated concat file
    """
    concat_file = output_path / "filelist.txt"

    with open(concat_file, 'w', encoding='utf-8') as f:
        for file in sorted(image_files):
            # Use absolute path to ensure FFMPEG finds the files
            abs_path = file.resolve()
            # Escape single quotes and backslashes for FFMPEG concat format
            safe_path = str(abs_path).replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    return concat_file


def get_estimated_duration(frame_count: int, framerate: int) -> float:
    """
    Calculate estimated video duration.

    Args:
        frame_count: Number of frames/images
        framerate: Frames per second

    Returns:
        Duration in seconds
    """
    if framerate <= 0:
        return 0.0

    return frame_count / framerate


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    return f"{hours}h {remaining_minutes}m"
