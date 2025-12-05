"""Preset management for encoding configurations."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from ..core.models import EncodingConfig
from ..utils.ffmpeg_locator import get_user_config_path
from ..utils.constants import USER_PRESETS_SUBFOLDER


class PresetManager:
    """Manages loading and saving of encoding presets."""

    def __init__(self):
        """Initialize preset manager."""
        self.user_presets_folder = get_user_config_path() / USER_PRESETS_SUBFOLDER
        self.user_presets_folder.mkdir(parents=True, exist_ok=True)

        # Path to default presets (bundled with app)
        self.default_presets_folder = Path(__file__).parent / "defaults"

    def get_default_presets(self) -> List[str]:
        """
        Get list of default preset names.

        Returns:
            List of preset names
        """
        if not self.default_presets_folder.exists():
            return []

        presets = []
        for file in self.default_presets_folder.glob("*.json"):
            presets.append(file.stem)

        return sorted(presets)

    def get_user_presets(self) -> List[str]:
        """
        Get list of user-created preset names.

        Returns:
            List of preset names
        """
        presets = []
        for file in self.user_presets_folder.glob("*.json"):
            presets.append(file.stem)

        return sorted(presets)

    def get_all_presets(self) -> List[str]:
        """
        Get all available presets (default + user).

        Returns:
            List of all preset names
        """
        default = self.get_default_presets()
        user = self.get_user_presets()

        # Combine and remove duplicates (user presets override default)
        all_presets = list(dict.fromkeys(default + user))
        return sorted(all_presets)

    def load_preset(self, name: str) -> Optional[Dict]:
        """
        Load a preset by name.

        Args:
            name: Preset name (without .json extension)

        Returns:
            Preset dictionary or None if not found
        """
        # Check user presets first (they override defaults)
        user_file = self.user_presets_folder / f"{name}.json"
        if user_file.exists():
            try:
                return json.loads(user_file.read_text())
            except Exception as e:
                print(f"Error loading user preset {name}: {e}")
                return None

        # Check default presets
        default_file = self.default_presets_folder / f"{name}.json"
        if default_file.exists():
            try:
                return json.loads(default_file.read_text())
            except Exception as e:
                print(f"Error loading default preset {name}: {e}")
                return None

        return None

    def save_preset(self, name: str, config: EncodingConfig, description: str = "") -> bool:
        """
        Save current configuration as a preset.

        Args:
            name: Preset name
            config: EncodingConfig to save
            description: Optional description

        Returns:
            True if successful, False otherwise
        """
        preset_data = {
            "name": name,
            "description": description,
            "settings": {
                "framerate": config.framerate,
                "codec": config.codec,
                "crf": config.crf,
                "preset": config.preset,
                "profile": config.profile,
                "level": config.level,
                "pixel_format": config.pixel_format,
                "output_resolution": config.output_resolution,
                "custom_resolution": config.custom_resolution,
                "movflags_faststart": config.movflags_faststart,
                "pattern_type": config.pattern_type,
                "custom_args": config.custom_args,
                "deflicker_enabled": config.deflicker_enabled,
                "deflicker_mode": config.deflicker_mode,
                "deflicker_size": config.deflicker_size,
                "crop_enabled": config.crop_enabled,
                "crop_x": config.crop_x,
                "crop_y": config.crop_y,
                "crop_w": config.crop_w,
                "crop_h": config.crop_h,
                "rotate_enabled": config.rotate_enabled,
                "rotate_angle": config.rotate_angle,
            }
        }

        preset_file = self.user_presets_folder / f"{name}.json"

        try:
            preset_file.write_text(json.dumps(preset_data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving preset {name}: {e}")
            return False

    def apply_preset_to_config(self, preset_name: str, config: EncodingConfig) -> bool:
        """
        Apply a preset to an existing EncodingConfig.

        Args:
            preset_name: Name of preset to load
            config: EncodingConfig to modify

        Returns:
            True if successful, False if preset not found
        """
        preset_data = self.load_preset(preset_name)

        if not preset_data or "settings" not in preset_data:
            return False

        settings = preset_data["settings"]

        # Apply all settings
        config.framerate = settings.get("framerate", config.framerate)
        config.codec = settings.get("codec", config.codec)
        config.crf = settings.get("crf", config.crf)
        config.preset = settings.get("preset", config.preset)
        config.profile = settings.get("profile", config.profile)
        config.level = settings.get("level", config.level)
        config.pixel_format = settings.get("pixel_format", config.pixel_format)
        config.output_resolution = settings.get("output_resolution", config.output_resolution)
        config.custom_resolution = settings.get("custom_resolution", config.custom_resolution)
        config.movflags_faststart = settings.get("movflags_faststart", config.movflags_faststart)
        config.pattern_type = settings.get("pattern_type", config.pattern_type)
        config.custom_args = settings.get("custom_args", config.custom_args)
        config.deflicker_enabled = settings.get("deflicker_enabled", config.deflicker_enabled)
        config.deflicker_mode = settings.get("deflicker_mode", config.deflicker_mode)
        config.deflicker_size = settings.get("deflicker_size", config.deflicker_size)
        config.crop_enabled = settings.get("crop_enabled", config.crop_enabled)
        config.crop_x = settings.get("crop_x", config.crop_x)
        config.crop_y = settings.get("crop_y", config.crop_y)
        config.crop_w = settings.get("crop_w", config.crop_w)
        config.crop_h = settings.get("crop_h", config.crop_h)
        config.rotate_enabled = settings.get("rotate_enabled", config.rotate_enabled)
        config.rotate_angle = settings.get("rotate_angle", config.rotate_angle)

        return True

    def delete_preset(self, name: str) -> bool:
        """
        Delete a user preset (cannot delete default presets).

        Args:
            name: Preset name to delete

        Returns:
            True if successful, False if not found or is default preset
        """
        user_file = self.user_presets_folder / f"{name}.json"

        if not user_file.exists():
            return False

        try:
            user_file.unlink()
            return True
        except Exception as e:
            print(f"Error deleting preset {name}: {e}")
            return False

    def is_default_preset(self, name: str) -> bool:
        """
        Check if a preset is a default (bundled) preset.

        Args:
            name: Preset name

        Returns:
            True if it's a default preset
        """
        default_file = self.default_presets_folder / f"{name}.json"
        return default_file.exists()

    def get_preset_description(self, name: str) -> Optional[str]:
        """
        Get description of a preset.

        Args:
            name: Preset name

        Returns:
            Description string or None
        """
        preset_data = self.load_preset(name)

        if preset_data:
            return preset_data.get("description", "")

        return None
