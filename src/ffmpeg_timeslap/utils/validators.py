"""Validation functions for FFMPEG Timeslap."""

import re
from pathlib import Path
from typing import Optional

from ..core.models import EncodingConfig, ValidationResult
from .ffmpeg_locator import find_ffmpeg, check_codec_available


def validate_folder_path(path: Path, must_exist: bool = True, must_be_writable: bool = False) -> ValidationResult:
    """
    Validate a folder path.

    Args:
        path: Path to validate
        must_exist: If True, path must exist
        must_be_writable: If True, path must be writable

    Returns:
        ValidationResult with errors if validation failed
    """
    result = ValidationResult(valid=True)

    if not path:
        result.add_error("Pfad ist leer")
        return result

    if must_exist and not path.exists():
        result.add_error(f"Ordner existiert nicht: {path}")
        return result

    if must_exist and not path.is_dir():
        result.add_error(f"Pfad ist kein Ordner: {path}")
        return result

    if must_be_writable and path.exists():
        # Try to create a test file
        test_file = path / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception:
            result.add_error(f"Ordner ist nicht beschreibbar: {path}")

    return result


def validate_framerate(framerate: int) -> ValidationResult:
    """
    Validate framerate value.

    Args:
        framerate: Framerate value to validate

    Returns:
        ValidationResult with errors if validation failed
    """
    result = ValidationResult(valid=True)

    if framerate <= 0:
        result.add_error("Framerate muss größer als 0 sein")
    elif framerate > 240:
        result.add_error("Framerate darf nicht größer als 240 sein")

    if framerate > 120:
        result.add_warning(f"Sehr hohe Framerate ({framerate} fps) kann zu großen Dateien führen")

    return result


def validate_crf(crf: int, codec: str = "libx264") -> ValidationResult:
    """
    Validate CRF value for given codec.

    Args:
        crf: CRF value to validate
        codec: Codec being used

    Returns:
        ValidationResult with errors if validation failed
    """
    result = ValidationResult(valid=True)

    if codec in ["libx264", "libx265"]:
        if not (0 <= crf <= 51):
            result.add_error(f"CRF für {codec} muss zwischen 0 und 51 liegen")
    elif codec == "libsvtav1":
        if not (0 <= crf <= 63):
            result.add_error(f"CRF für {codec} muss zwischen 0 und 63 liegen")

    return result


def validate_resolution(resolution: str, custom_resolution: Optional[str] = None) -> ValidationResult:
    """
    Validate output resolution.

    Args:
        resolution: Resolution preset (e.g. "original", "1920x1080", "custom")
        custom_resolution: Custom resolution string if resolution is "custom"

    Returns:
        ValidationResult with errors if validation failed
    """
    result = ValidationResult(valid=True)

    if resolution == "custom":
        if not custom_resolution:
            result.add_error("Custom-Auflösung wurde nicht angegeben")
            return result

        # Validate format: WIDTHxHEIGHT
        if not re.match(r'^\d+x\d+$', custom_resolution):
            result.add_error("Custom-Auflösung muss im Format 'BREITExHÖHE' sein (z.B. 1920x1080)")
            return result

        # Extract width and height
        width, height = map(int, custom_resolution.split('x'))

        if width <= 0 or height <= 0:
            result.add_error("Breite und Höhe müssen größer als 0 sein")
        elif width > 7680 or height > 4320:
            result.add_warning(f"Sehr hohe Auflösung ({custom_resolution}) kann zu Performance-Problemen führen")

        # Check if dimensions are even (required for yuv420p)
        if width % 2 != 0 or height % 2 != 0:
            result.add_warning(
                f"Auflösung {custom_resolution} hat ungerade Dimensionen. "
                "Padding-Filter wird automatisch angewendet."
            )

    return result


def validate_crop_settings(x: int, y: int, width: int, height: int,
                           image_width: int, image_height: int) -> ValidationResult:
    """
    Validate crop settings.

    Args:
        x: X coordinate
        y: Y coordinate
        width: Crop width
        height: Crop height
        image_width: Source image width
        image_height: Source image height

    Returns:
        ValidationResult with errors if validation failed
    """
    result = ValidationResult(valid=True)

    if width <= 0 or height <= 0:
        result.add_error("Crop-Breite und -Höhe müssen größer als 0 sein")

    if x < 0 or y < 0:
        result.add_error("Crop-Position (x, y) darf nicht negativ sein")

    if x + width > image_width:
        result.add_error(f"Crop überschreitet Bildbreite (x={x} + width={width} > {image_width})")

    if y + height > image_height:
        result.add_error(f"Crop überschreitet Bildhöhe (y={y} + height={height} > {image_height})")

    # Check if crop dimensions are even
    if width % 2 != 0 or height % 2 != 0:
        result.add_warning("Crop-Dimensionen sind ungerade. Padding-Filter wird automatisch angewendet.")

    return result


def validate_encoding_config(config: EncodingConfig) -> ValidationResult:
    """
    Validate complete encoding configuration.

    Args:
        config: EncodingConfig to validate

    Returns:
        ValidationResult with all errors and warnings
    """
    result = ValidationResult(valid=True)

    # Validate input folder
    input_result = validate_folder_path(config.input_folder, must_exist=True)
    result.errors.extend(input_result.errors)
    result.warnings.extend(input_result.warnings)

    # Validate output folder
    output_result = validate_folder_path(config.output_folder, must_exist=False, must_be_writable=True)
    result.errors.extend(output_result.errors)
    result.warnings.extend(output_result.warnings)

    # Create output folder if it doesn't exist
    if not config.output_folder.exists():
        try:
            config.output_folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            result.add_error(f"Kann Output-Ordner nicht erstellen: {e}")

    # Validate output filename
    if not config.output_filename:
        result.add_error("Output-Dateiname ist leer")
    elif not config.output_filename.endswith(('.mp4', '.mkv', '.avi', '.mov')):
        result.add_warning(f"Ungewöhnliche Dateiendung: {config.output_filename}")

    # Validate framerate
    framerate_result = validate_framerate(config.framerate)
    result.errors.extend(framerate_result.errors)
    result.warnings.extend(framerate_result.warnings)

    # Validate CRF
    crf_result = validate_crf(config.crf, config.codec)
    result.errors.extend(crf_result.errors)
    result.warnings.extend(crf_result.warnings)

    # Validate resolution
    resolution_result = validate_resolution(config.output_resolution, config.custom_resolution)
    result.errors.extend(resolution_result.errors)
    result.warnings.extend(resolution_result.warnings)

    # Validate crop if enabled
    if config.crop_enabled and config.sequence_info:
        crop_result = validate_crop_settings(
            config.crop_x, config.crop_y, config.crop_w, config.crop_h,
            config.sequence_info.image_width, config.sequence_info.image_height
        )
        result.errors.extend(crop_result.errors)
        result.warnings.extend(crop_result.warnings)

    # Check if sequence info exists
    if not config.sequence_info:
        result.add_error("Keine Bildsequenz erkannt. Bitte Input-Ordner auswählen.")

    # Validate codec availability
    try:
        ffmpeg_path = find_ffmpeg()
        if not check_codec_available(ffmpeg_path, config.codec):
            codec_names = {
                "libx264": "H.264 (libx264)",
                "libx265": "H.265 (libx265)",
                "libsvtav1": "AV1 (libsvtav1)"
            }
            codec_display = codec_names.get(config.codec, config.codec)

            result.add_error(
                f"Codec {codec_display} ist in Ihrer FFMPEG-Installation nicht verfügbar.\n\n"
                f"Mögliche Lösungen:\n"
                f"- Verwenden Sie einen anderen Codec (z.B. H.264)\n"
                f"- Installieren Sie eine FFMPEG-Version mit {codec_display}-Support\n"
                f"- Für AV1: Laden Sie FFMPEG mit libsvtav1 von https://github.com/BtbN/FFmpeg-Builds/releases"
            )
    except Exception:
        # If we can't check, don't add error (validation will happen at encoding time)
        pass

    # Update valid flag
    result.valid = len(result.errors) == 0

    return result
