# FFMPEG Timelapse - Project Documentation

## Project Overview

FFMPEG Timelapse ist eine Python-Desktop-Anwendung mit PyQt5 GUI zur Erstellung von Timelapse-Videos aus Bildsequenzen. Die App bietet eine benutzerfreundliche Oberfläche mit umfangreichen FFMPEG-Einstellungen und vorgefertigten Presets für verschiedene Plattformen (YouTube, Instagram, Twitter, etc.).

## Tech Stack

- **Language:** Python 3.8+
- **GUI Framework:** PyQt5
- **Image Processing:** Pillow (PIL)
- **Video Encoding:** FFMPEG (externe Binary)
- **Build System:** setuptools

## Project Structure

```
FFMPEG_Timeslap/
├── src/ffmpeg_timeslap/          # Main application package
│   ├── core/                     # Core business logic
│   │   ├── models.py            # Data models (EncodingConfig, SequenceInfo, etc.)
│   │   ├── sequence_detector.py # Image sequence detection & analysis
│   │   ├── command_builder.py   # FFMPEG command generation
│   │   ├── encoder.py           # FFMPEG subprocess management
│   │   └── progress_parser.py   # FFMPEG output parsing
│   ├── gui/                      # PyQt5 GUI components
│   │   ├── main_window.py       # Main application window
│   │   ├── widgets/             # Custom widgets
│   │   └── dialogs/             # Dialog windows
│   ├── presets/                  # Preset system
│   │   ├── preset_manager.py    # Preset load/save/delete
│   │   └── defaults/            # Built-in presets (JSON)
│   └── utils/                    # Utility functions
│       ├── constants.py         # App constants
│       ├── validators.py        # Input validation
│       ├── ffmpeg_locator.py    # FFMPEG executable detection
│       └── file_utils.py        # File operations
├── tests/                        # Unit tests
├── docs/                         # Documentation
│   └── ffmpeg_info.md           # FFMPEG parameter reference
├── ffmpeg_binaries/             # Bundled FFMPEG binaries (not in repo)
│   └── windows/
│       └── ffmpeg.exe
├── pyproject.toml               # Project configuration
└── README.md

```

## Key Features

### 1. Automatic Image Sequence Detection
- Detects various naming patterns (IMG_0001.jpg, img_1.png, etc.)
- Identifies gaps in sequences
- Generates concat files for non-sequential images
- Extracts image dimensions and format

### 2. FFMPEG Integration
- Dynamic command building with proper parameter ordering
- Support for H.264, H.265, and AV1 codecs
- Automatic padding for odd image dimensions
- Filter support: Deflicker, Crop, Rotate, Scale

### 3. Preset System
- Built-in presets for popular platforms:
  - YouTube HD (1080p, H.264, CRF 18)
  - YouTube 4K (2160p, H.265, CRF 20)
  - Instagram (1080x1080, H.264, CRF 23)
  - Twitter (720p, H.264, CRF 23)
  - Archiv (Original, H.265, CRF 15)
  - Schnelle Vorschau (720p, ultrafast)
- User can create and save custom presets
- Presets stored as JSON in user config folder

### 4. Progress Tracking
- Real-time progress bar during encoding
- FPS and time remaining estimation
- Live FFMPEG output display

### 5. Portable App Support
- FFMPEG binary detection with fallback chain:
  1. System PATH
  2. Bundled binary
  3. User-configured path
- Can be distributed as standalone app

## Architecture

### MVC Pattern
- **Model:** `core/models.py` - Data structures
- **View:** `gui/widgets/*` - UI components
- **Controller:** `gui/main_window.py` - Logic coordination

### Data Flow
```
User Input (GUI)
    ↓
Validation (validators.py)
    ↓
Config Model (EncodingConfig)
    ↓
Sequence Detection (sequence_detector.py)
    ↓
Command Building (command_builder.py)
    ↓
Encoding (encoder.py)
    ↓
Progress Updates (progress_parser.py)
    ↓
GUI Updates
```

## Core Components

### models.py
Defines all data structures using Python dataclasses:
- `SequenceInfo`: Image sequence information
- `EncodingConfig`: Complete encoding configuration
- `ValidationResult`: Validation results with errors/warnings
- `ProgressInfo`: Encoding progress information
- `ErrorInfo`: Error details from FFMPEG

### sequence_detector.py
Image sequence detection and analysis:
- `detect_sequence()`: Main detection function
- `analyze_naming_pattern()`: Extract prefix, number, extension
- `detect_gaps()`: Find missing images in sequence
- `generate_concat_file()`: Create FFMPEG concat file for gaps
- `get_image_info()`: Extract dimensions using Pillow

### command_builder.py
FFMPEG command construction:
- `FFmpegCommandBuilder`: Main builder class
- Proper parameter ordering (framerate → input → filters → codec → output)
- Filter chain building (padding, scale, crop, rotate, deflicker)
- Support for sequential and concat input modes

### encoder.py
FFMPEG process management:
- `FFmpegEncoder`: Manages subprocess execution
- Callbacks for progress, output, and completion
- `EncodingErrorHandler`: Error analysis and user-friendly messages

### progress_parser.py
FFMPEG output parsing:
- `ProgressParser`: Extracts frame number, FPS, time
- Regex-based pattern matching
- Percentage calculation based on total frames
- Error message extraction

### preset_manager.py
Preset management:
- Load/save/delete presets
- Default presets bundled with app
- User presets stored in `%APPDATA%/FFMPEG_Timeslap/presets/`
- JSON format for easy editing

### ffmpeg_locator.py
FFMPEG executable location:
- Multi-platform support (Windows, macOS, Linux)
- Fallback chain: System → Bundled → User config
- Version detection
- User config persistence

## FFMPEG Command Structure

The app generates FFMPEG commands with this structure:

```bash
ffmpeg
  -framerate <fps>              # MUST come before input
  [-start_number <n>]           # Optional, for non-zero start
  -i <input_pattern>            # Sequence pattern or concat file
  [-vf <filter_chain>]          # Filters (order matters!)
  -c:v <codec>                  # Video codec
  -preset <preset>              # Encoding speed
  -profile:v <profile>          # Codec profile
  -level <level>                # Codec level
  -crf <quality>                # Quality (0-51)
  [-movflags +faststart]        # Optional streaming optimization
  [<custom_args>]               # User custom arguments
  <output_file>                 # Output path
```

### Filter Chain Order
1. **pad** - Fix odd dimensions (must be first)
2. **scale** - Resize to target resolution
3. **crop** - Crop to specific area
4. **transpose** - Rotate image
5. **deflicker** - Reduce brightness flicker
6. **format** - Set pixel format (must be last)

Filters are comma-separated: `pad=...,scale=...,format=yuv420p`

## Configuration Files

### User Config Location
- **Windows:** `%APPDATA%/FFMPEG_Timeslap/`
- **macOS:** `~/Library/Application Support/FFMPEG_Timeslap/`
- **Linux:** `~/.config/FFMPEG_Timeslap/`

### Files
- `presets/*.json` - User-created presets
- `ffmpeg_path.txt` - Custom FFMPEG path (optional)

### Preset JSON Format
```json
{
  "name": "Preset Name",
  "description": "Description text",
  "settings": {
    "framerate": 30,
    "codec": "libx264",
    "crf": 18,
    "preset": "slow",
    "profile": "high",
    "level": "4.0",
    "pixel_format": "yuv420p",
    "output_resolution": "1920x1080",
    "movflags_faststart": true,
    "deflicker_enabled": false,
    "crop_enabled": false,
    "rotate_enabled": false
  }
}
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints (Python 3.8+)
- Docstrings for all public functions
- Line length: 100 characters (Black formatter)

### Naming Conventions
- Classes: PascalCase
- Functions/variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Private methods: _leading_underscore

### Testing
- Unit tests in `tests/` folder
- Use pytest for test execution
- Test fixtures for sample image sequences

### PyQt5 Best Practices
- Use type-safe signal connections
- Run FFMPEG in separate process (not thread)
- Update GUI from main thread only
- Use QProcess for subprocess management

## Common Tasks

### Adding a New Preset
1. Create JSON file in `src/ffmpeg_timeslap/presets/defaults/`
2. Follow preset JSON format
3. Preset automatically available in app

### Adding a New Filter
1. Add filter settings to `EncodingConfig` in `models.py`
2. Add filter constants to `constants.py`
3. Implement filter builder in `command_builder.py`
4. Add GUI widget for filter settings
5. Add filter to validation in `validators.py`

### Adding a New Codec
1. Add codec to `CODECS` list in `constants.py`
2. Update codec-specific logic in `command_builder.py`
3. Update CRF validation in `validators.py`

## Error Handling

### Validation Errors
- Input validation happens before encoding
- `ValidationResult` contains errors and warnings
- User gets clear feedback for fixable issues

### FFMPEG Errors
- `EncodingErrorHandler` analyzes error output
- Pattern matching for common errors
- User-friendly messages with technical details
- Recoverable vs. non-recoverable classification

### Common Error Patterns
- **No such file or directory:** Input folder/files not found
- **height/width not divisible by 2:** Enable padding filter
- **Permission denied:** Output folder not writable
- **Codec not found:** FFMPEG build missing codec

## Performance Considerations

### Image Sequence Detection
- Only first image is read for dimensions (assumes all same size)
- File listing cached during detection
- Gap detection uses set operations (O(n))

### Encoding
- FFMPEG runs in separate process
- Output parsed line-by-line (streaming)
- Progress updates throttled if needed
- No temporary files except concat list

### Memory
- No images loaded into memory
- FFMPEG handles all image processing
- Minimal memory footprint (<50 MB typical)

## Deployment

### Bundling FFMPEG
1. Download FFMPEG static build
2. Place in `ffmpeg_binaries/windows/ffmpeg.exe`
3. Include FFMPEG license (`LICENSE.txt`)
4. Document FFMPEG version in README

### Creating Portable App
1. Use PyInstaller or cx_Freeze
2. Include FFMPEG binary in bundle
3. Set correct executable permissions
4. Test on clean system without Python

### Distribution
- **Standalone:** Bundle Python + dependencies + FFMPEG
- **Installer:** Use Inno Setup (Windows) or create .dmg (macOS)
- **Portable:** ZIP with all files, no installation needed

## Known Limitations

1. **Single folder processing:** No batch mode in v1.0
2. **Windows-first:** Primary platform is Windows (FFMPEG binaries)
3. **Sequential naming:** Best with numbered sequences
4. **Memory with large images:** FFMPEG handles, but preview might be slow
5. **No real-time preview:** Can't preview video while encoding

## Future Enhancements (v2.0+)

- Batch processing (multiple folders)
- Video preview before encoding
- Audio track support
- Image preprocessing (color correction, stabilization)
- Cloud encoding options
- Timeline editor for selecting frame ranges
- Export to multiple formats simultaneously

## Troubleshooting

### FFMPEG Not Found
1. Check system PATH
2. Check bundled binary exists
3. Manually configure in settings
4. Install FFMPEG globally

### Encoding Fails
1. Check FFMPEG output in app
2. Verify input images accessible
3. Test FFMPEG command manually
4. Check output folder permissions

### Images Not Detected
1. Verify image format supported
2. Check naming pattern consistent
3. Ensure files have numbers in name
4. Try different folder

### Performance Issues
1. Use faster preset (fast, veryfast, ultrafast)
2. Lower output resolution
3. Use H.264 instead of H.265
4. Check system resources (CPU, disk I/O)

## Resources

- [FFMPEG Documentation](https://ffmpeg.org/documentation.html)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- Project issues: GitHub Issues (when published)

## License

MIT License - See LICENSE file for details

FFMPEG is licensed under GPL/LGPL - See `ffmpeg_binaries/LICENSE.txt`

---

**Author:** Christian Neumayer (numi@nech.at)
**Version:** 0.1.0
**Last Updated:** 2025-12-02
