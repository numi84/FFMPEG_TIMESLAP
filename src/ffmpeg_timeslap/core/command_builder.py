"""FFMPEG command builder.

Codec-Specific Parameter Support:
==================================

H.264 (libx264):
- Preset: Named (ultrafast-veryslow)
- Profile: baseline, main, high, high10, high422, high444
- Level: 3.0-5.2
- CRF: 0-51
- Tag: Not used

H.265 (libx265):
- Preset: Named (ultrafast-veryslow)
- Profile: main, main10, main422-10, main444-8 (mapped from H.264)
- Level: Optional (auto-detected)
- CRF: 0-51
- Tag: hvc1 (required for Apple compatibility)

AV1 (libsvtav1):
- Preset: Numeric 0-13 (mapped from named)
- Profile: Not supported (auto-detected)
- Level: Not supported (auto-detected)
- CRF: 0-63
- Tag: Not used

See docs/codec_compatibility.md for detailed information.
"""

import shlex
from typing import List
from pathlib import Path

from .models import EncodingConfig


class FFmpegCommandBuilder:
    """Builds FFMPEG command from encoding configuration."""

    def __init__(self, config: EncodingConfig, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize command builder.

        Args:
            config: EncodingConfig with all settings
            ffmpeg_path: Path to ffmpeg executable
        """
        self.config = config
        self.ffmpeg_path = ffmpeg_path
        self.command_parts: List[str] = []

    def build(self) -> List[str]:
        """
        Build complete FFMPEG command.

        Returns:
            List of command parts for subprocess
        """
        self.command_parts = [self.ffmpeg_path]

        # Always overwrite output file without asking
        self.command_parts.append("-y")

        # Order is important!
        self._add_input_options()
        self._add_filter_options()
        self._add_codec_options()
        self._add_quality_options()
        self._add_output_options()
        self._add_output_file()

        return self.command_parts

    def build_as_string(self) -> str:
        """
        Build command as single string (for preview).

        Returns:
            Command as string
        """
        command = self.build()
        return " ".join(shlex.quote(part) for part in command)

    def _add_input_options(self) -> None:
        """Add input options (framerate, start_number, input file/pattern)."""
        if self.config.use_concat:
            # Concat mode for non-sequential images
            # NOTE: framerate comes AFTER -i for concat demuxer
            concat_file = self.config.sequence_info.concat_file

            if concat_file:
                self.command_parts.extend([
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_file)
                ])
        else:
            # Sequential mode
            # Framerate MUST come before input for image2 demuxer
            self.command_parts.extend(["-framerate", str(self.config.framerate)])

            if self.config.start_number is not None:
                self.command_parts.extend(["-start_number", str(self.config.start_number)])

            # Build input pattern
            input_pattern = self._build_input_pattern()
            self.command_parts.extend(["-i", input_pattern])

    def _build_input_pattern(self) -> str:
        """
        Build input file pattern.

        Returns:
            Input pattern string
        """
        if self.config.pattern_type == "glob":
            # Glob pattern mode
            return f"glob:{self.config.input_folder}/*.jpg"
        else:
            # Sequential pattern mode
            if self.config.sequence_info:
                pattern = self.config.sequence_info.pattern
                return str(self.config.input_folder / pattern)

            # Fallback
            return str(self.config.input_folder / "img_%04d.jpg")

    def _add_filter_options(self) -> None:
        """Add video filter options (-vf)."""
        filters = []

        # For concat mode, add fps filter to set framerate
        if self.config.use_concat:
            filters.append(f"fps={self.config.framerate}")

        # Padding for odd dimensions (must come first)
        if self.config.needs_padding:
            filters.append("pad=ceil(iw/2)*2:ceil(ih/2)*2")

        # Scaling/Resolution
        scale_filter = self._build_scale_filter()
        if scale_filter:
            filters.append(scale_filter)

        # Rotate (BEFORE crop so crop stays axis-aligned)
        if self.config.rotate_enabled:
            rotate_filter = self._build_rotate_filter()
            if rotate_filter:
                filters.append(rotate_filter)

        # Flip/Mirror (BEFORE crop so crop stays axis-aligned)
        if self.config.flip_enabled:
            flip_filters = self._build_flip_filters()
            filters.extend(flip_filters)

        # Crop (AFTER rotate/flip so it's applied to transformed image)
        if self.config.crop_enabled:
            crop_filter = self._build_crop_filter()
            if crop_filter:
                filters.append(crop_filter)

        # Deflicker
        if self.config.deflicker_enabled:
            deflicker_filter = self._build_deflicker_filter()
            if deflicker_filter:
                filters.append(deflicker_filter)

        # Pixel format (should be last)
        filters.append(f"format={self.config.pixel_format}")

        # Add all filters to command
        if filters:
            self.command_parts.extend(["-vf", ",".join(filters)])

    def _build_scale_filter(self) -> str:
        """
        Build scale filter based on output resolution.

        Returns:
            Scale filter string or empty if no scaling needed
        """
        resolution = self.config.output_resolution

        if resolution == "original":
            return ""

        if resolution == "custom" and self.config.custom_resolution:
            # Custom resolution
            width, height = self.config.custom_resolution.split('x')
            return f"scale={width}:{height}"

        if resolution != "custom":
            # Preset resolution
            width, height = resolution.split('x')
            return f"scale={width}:{height}"

        return ""

    def _build_crop_filter(self) -> str:
        """
        Build crop filter.

        Returns:
            Crop filter string
        """
        return f"crop={self.config.crop_w}:{self.config.crop_h}:{self.config.crop_x}:{self.config.crop_y}"

    def _build_rotate_filter(self) -> str:
        """
        Build rotate filter.

        Returns:
            Rotate filter string or empty if no rotation
        """
        angle = self.config.rotate_angle

        if angle == 0:
            return ""

        # Use transpose for 90° increments (faster, lossless)
        if angle == 90:
            return "transpose=1"  # 90 degrees clockwise
        elif angle == 180:
            return "transpose=2,transpose=2"  # 180 degrees
        elif angle == 270:
            return "transpose=2"  # 90 degrees counter-clockwise
        else:
            # Use rotate filter for arbitrary angles
            # Convert degrees to radians (PI/180)
            # Fill transparent areas with black
            return f"rotate={angle}*PI/180:c=black:ow='iw':oh='ih'"

    def _build_flip_filters(self) -> List[str]:
        """
        Build flip/mirror filters.

        Returns:
            List of flip filter strings
        """
        filters = []

        if self.config.flip_horizontal:
            filters.append("hflip")

        if self.config.flip_vertical:
            filters.append("vflip")

        return filters

    def _build_deflicker_filter(self) -> str:
        """
        Build deflicker filter.

        Returns:
            Deflicker filter string
        """
        mode = self.config.deflicker_mode
        size = self.config.deflicker_size

        return f"deflicker=mode={mode}:size={size}"

    def _map_preset_to_av1(self) -> int:
        """
        Map x264/x265 preset names to AV1 preset numbers.

        SVT-AV1 uses numeric presets 0-13 (lower = slower/better quality).
        """
        preset_map = {
            "ultrafast": 13,
            "superfast": 12,
            "veryfast": 10,
            "faster": 8,
            "fast": 6,
            "medium": 5,
            "slow": 4,
            "slower": 2,
            "veryslow": 0,
        }
        return preset_map.get(self.config.preset, 5)  # Default to medium (5)

    def _map_profile_to_h265(self, h264_profile: str) -> str:
        """
        Map H.264 profile names to H.265 profile names.

        Args:
            h264_profile: H.264 profile name

        Returns:
            H.265 profile name or empty string if not applicable
        """
        profile_map = {
            "baseline": "main",
            "main": "main",
            "high": "main",
            "high10": "main10",
            "high422": "main422-10",
            "high444": "main444-8",
        }
        return profile_map.get(h264_profile, "main")

    def _add_codec_options(self) -> None:
        """Add codec options."""
        self.command_parts.extend(["-c:v", self.config.codec])

        # Codec-specific options
        if self.config.codec in ["libx264", "libx265"]:
            self.command_parts.extend(["-preset", self.config.preset])

            # H.265 uses different profiles than H.264
            if self.config.codec == "libx265":
                # Map H.264 profiles to H.265 equivalents
                h265_profile = self._map_profile_to_h265(self.config.profile)
                if h265_profile:
                    self.command_parts.extend(["-profile:v", h265_profile])
                self.command_parts.extend(["-tag:v", "hvc1"])
            else:
                # H.264 profiles
                self.command_parts.extend(["-profile:v", self.config.profile])
                self.command_parts.extend(["-level", self.config.level])

        elif self.config.codec == "libsvtav1":
            # AV1 specific options
            self.command_parts.extend(["-preset", str(self._map_preset_to_av1())])
            # SVT-AV1 uses different CRF range, but we'll keep the same interface

    def _add_quality_options(self) -> None:
        """Add quality options (CRF)."""
        self.command_parts.extend(["-crf", str(self.config.crf)])

    def _add_output_options(self) -> None:
        """Add output options (movflags, custom args)."""
        # Movflags for faster streaming start
        if self.config.movflags_faststart:
            self.command_parts.extend(["-movflags", "+faststart"])

        # Custom FFMPEG arguments (advanced users)
        if self.config.custom_args:
            # Parse custom args and add them
            custom_parts = shlex.split(self.config.custom_args)
            self.command_parts.extend(custom_parts)

    def _add_output_file(self) -> None:
        """Add output file path."""
        self.command_parts.append(str(self.config.output_path))

    def get_command_info(self) -> dict:
        """
        Get information about the command.

        Returns:
            Dictionary with command information
        """
        return {
            "ffmpeg_path": self.ffmpeg_path,
            "input_folder": str(self.config.input_folder),
            "output_file": str(self.config.output_path),
            "codec": self.config.codec,
            "framerate": self.config.framerate,
            "crf": self.config.crf,
            "resolution": self.config.output_resolution,
            "filters_enabled": {
                "padding": self.config.needs_padding,
                "deflicker": self.config.deflicker_enabled,
                "crop": self.config.crop_enabled,
                "rotate": self.config.rotate_enabled,
            },
            "use_concat": self.config.use_concat,
        }
