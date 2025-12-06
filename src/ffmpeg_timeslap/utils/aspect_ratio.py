"""Aspect ratio calculation utilities for crop functionality."""

from typing import Tuple, Optional
import math


def gcd(a: int, b: int) -> int:
    """
    Calculate Greatest Common Divisor using Euclidean algorithm.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Greatest common divisor of a and b
    """
    while b:
        a, b = b, a % b
    return a


def simplify_ratio(width: int, height: int) -> Tuple[int, int]:
    """
    Simplify aspect ratio to smallest integer components.

    Args:
        width: Width in pixels
        height: Height in pixels

    Returns:
        Tuple of (ratio_w, ratio_h) in simplified form

    Example:
        simplify_ratio(1920, 1080) -> (16, 9)
        simplify_ratio(1080, 1080) -> (1, 1)
    """
    if width == 0 or height == 0:
        return (0, 0)

    divisor = gcd(width, height)
    return (width // divisor, height // divisor)


def parse_ratio_string(ratio_str: str) -> Tuple[int, int]:
    """
    Parse ratio string like "16:9" or "2.39:1" into integer components.

    Args:
        ratio_str: String in format "W:H" (e.g., "16:9", "2.39:1")

    Returns:
        Tuple of (ratio_w, ratio_h) as integers

    Raises:
        ValueError: If string format is invalid

    Examples:
        parse_ratio_string("16:9") -> (16, 9)
        parse_ratio_string("2.39:1") -> (239, 100)
    """
    if ":" not in ratio_str:
        raise ValueError(f"Invalid ratio format: {ratio_str}")

    parts = ratio_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid ratio format: {ratio_str}")

    try:
        # Parse with decimal support
        w_float = float(parts[0])
        h_float = float(parts[1])
    except ValueError:
        raise ValueError(f"Invalid ratio format: {ratio_str}")

    # Convert to integers by scaling up for decimal ratios
    # For 2.39:1, multiply by 100 -> 239:100
    if w_float % 1 != 0 or h_float % 1 != 0:
        # Find decimal places needed
        w_str = str(w_float).split('.')[1] if '.' in str(w_float) else ''
        h_str = str(h_float).split('.')[1] if '.' in str(h_float) else ''
        decimals = max(len(w_str), len(h_str))
        multiplier = 10 ** decimals

        w_int = int(w_float * multiplier)
        h_int = int(h_float * multiplier)
    else:
        w_int = int(w_float)
        h_int = int(h_float)

    # Simplify the ratio
    return simplify_ratio(w_int, h_int)


def calculate_height_from_width(width: int, ratio_w: int, ratio_h: int,
                                 round_to_even: bool = True) -> int:
    """
    Calculate height to maintain aspect ratio given width.

    Args:
        width: Target width in pixels
        ratio_w: Aspect ratio width component
        ratio_h: Aspect ratio height component
        round_to_even: If True, ensure result is even (FFMPEG requirement)

    Returns:
        Calculated height in pixels (minimum 32)

    Example:
        calculate_height_from_width(1920, 16, 9) -> 1080
        calculate_height_from_width(1000, 16, 9) -> 562 (even)
    """
    if ratio_w == 0:
        return 32

    height = int(round(width * ratio_h / ratio_w))

    if round_to_even:
        height = (height // 2) * 2

    return max(32, height)


def calculate_width_from_height(height: int, ratio_w: int, ratio_h: int,
                                 round_to_even: bool = True) -> int:
    """
    Calculate width to maintain aspect ratio given height.

    Args:
        height: Target height in pixels
        ratio_w: Aspect ratio width component
        ratio_h: Aspect ratio height component
        round_to_even: If True, ensure result is even (FFMPEG requirement)

    Returns:
        Calculated width in pixels (minimum 32)

    Example:
        calculate_width_from_height(1080, 16, 9) -> 1920
        calculate_width_from_height(500, 16, 9) -> 888 (even)
    """
    if ratio_h == 0:
        return 32

    width = int(round(height * ratio_w / ratio_h))

    if round_to_even:
        width = (width // 2) * 2

    return max(32, width)


def constrain_rect_to_ratio(x: int, y: int, w: int, h: int,
                             ratio_w: int, ratio_h: int,
                             max_w: int, max_h: int,
                             anchor: str = "center") -> Tuple[int, int, int, int]:
    """
    Constrain rectangle to aspect ratio while staying within bounds.

    Args:
        x, y, w, h: Current rectangle coordinates and dimensions
        ratio_w, ratio_h: Target aspect ratio components
        max_w, max_h: Maximum bounds (image dimensions)
        anchor: Position anchor - "center", "topleft", "topright", "bottomleft", "bottomright"

    Returns:
        Tuple of (new_x, new_y, new_w, new_h) constrained to ratio and bounds

    Algorithm:
        1. Calculate target dimensions based on ratio
        2. Choose dimension that fits within bounds
        3. Calculate other dimension to match ratio
        4. Adjust position based on anchor point
        5. Ensure even values and within bounds

    Example:
        constrain_rect_to_ratio(100, 100, 800, 600, 16, 9, 1920, 1080, "center")
        -> (100, 150, 800, 450) # Height adjusted to match 16:9
    """
    # Calculate both possible dimensions
    height_from_width = calculate_height_from_width(w, ratio_w, ratio_h)
    width_from_height = calculate_width_from_height(h, ratio_w, ratio_h)

    # Choose dimension strategy that fits
    if height_from_width <= max_h and w <= max_w:
        # Use width as base
        new_w = w
        new_h = height_from_width
    elif width_from_height <= max_w and h <= max_h:
        # Use height as base
        new_w = width_from_height
        new_h = h
    else:
        # Neither fits, scale down based on which is more constrained
        width_ratio = max_w / w if w > 0 else 1
        height_ratio = max_h / h if h > 0 else 1

        if width_ratio < height_ratio:
            # Width is more constrained
            new_w = max_w
            new_h = calculate_height_from_width(new_w, ratio_w, ratio_h)

            # If still doesn't fit, recalculate from height
            if new_h > max_h:
                new_h = max_h
                new_w = calculate_width_from_height(new_h, ratio_w, ratio_h)
        else:
            # Height is more constrained
            new_h = max_h
            new_w = calculate_width_from_height(new_h, ratio_w, ratio_h)

            # If still doesn't fit, recalculate from width
            if new_w > max_w:
                new_w = max_w
                new_h = calculate_height_from_width(new_w, ratio_w, ratio_h)

    # Ensure even values
    new_w = (new_w // 2) * 2
    new_h = (new_h // 2) * 2

    # Ensure minimum size
    new_w = max(32, new_w)
    new_h = max(32, new_h)

    # Adjust position based on anchor
    if anchor == "center":
        # Keep center point same
        center_x = x + w // 2
        center_y = y + h // 2
        new_x = center_x - new_w // 2
        new_y = center_y - new_h // 2
    elif anchor == "topleft":
        new_x = x
        new_y = y
    elif anchor == "topright":
        new_x = (x + w) - new_w
        new_y = y
    elif anchor == "bottomleft":
        new_x = x
        new_y = (y + h) - new_h
    elif anchor == "bottomright":
        new_x = (x + w) - new_w
        new_y = (y + h) - new_h
    else:
        # Default to topleft
        new_x = x
        new_y = y

    # Ensure within bounds
    new_x = max(0, min(new_x, max_w - new_w))
    new_y = max(0, min(new_y, max_h - new_h))

    # Ensure even positions
    new_x = (new_x // 2) * 2
    new_y = (new_y // 2) * 2

    return (new_x, new_y, new_w, new_h)


def find_closest_preset_ratio(width: int, height: int,
                               presets: list) -> Optional[str]:
    """
    Find closest matching preset ratio for given dimensions.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        presets: List of preset ratio strings (e.g., ["16:9", "4:3", "1:1"])

    Returns:
        Closest matching preset string or None if no match within tolerance

    Algorithm:
        1. Calculate actual ratio (width/height)
        2. For each preset, calculate ratio difference
        3. Return preset with smallest difference (within 2% tolerance)

    Example:
        find_closest_preset_ratio(1920, 1080, ["16:9", "4:3", "1:1"])
        -> "16:9"

        find_closest_preset_ratio(1920, 1200, ["16:9", "4:3"])
        -> "4:3" (1920/1200 = 1.6 = 8/5, close to 4:3 = 1.333)
    """
    if width == 0 or height == 0:
        return None

    actual_ratio = width / height
    tolerance = 0.02  # 2% tolerance

    closest_preset = None
    min_diff = float('inf')

    for preset in presets:
        try:
            ratio_w, ratio_h = parse_ratio_string(preset)
            if ratio_h == 0:
                continue

            preset_ratio = ratio_w / ratio_h
            diff = abs(actual_ratio - preset_ratio)

            if diff < min_diff and diff < tolerance:
                min_diff = diff
                closest_preset = preset
        except ValueError:
            # Skip invalid preset strings
            continue

    return closest_preset
