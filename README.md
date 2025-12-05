# FFMPEG Timeslap

Eine benutzerfreundliche Python-Desktop-Anwendung zur Erstellung von Timelapse-Videos aus Bildsequenzen mit FFMPEG.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

- **Automatische Bildsequenz-Erkennung** mit verschiedenen Namensmustern
- **Vorgefertigte Presets** für YouTube, Instagram, Twitter, Archivierung
- **Umfangreiche FFMPEG-Einstellungen** (Codec, Qualität, Filter, etc.)
- **Live-Fortschrittsanzeige** während des Encodings
- **Portable** - kann mit FFMPEG-Binary ausgeliefert werden
- **Benutzerfreundliche GUI** mit PyQt5

## Screenshots

*(Screenshots folgen)*

## Voraussetzungen

- Python 3.8 oder höher
- FFMPEG (wird automatisch erkannt oder kann mitgeliefert werden)

## Installation

### Option 1: Development Installation

```bash
# Repository klonen
git clone <repository-url>
cd FFMPEG_Timeslap

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -e .
```

### Option 2: Portable Version

*(Wird später als Release bereitgestellt)*

## FFMPEG Installation

Die App benötigt FFMPEG zum Erstellen der Videos.

### Windows
```bash
# Mit Chocolatey
choco install ffmpeg

# Oder manuell von https://ffmpeg.org/download.html
```

### macOS
```bash
brew install ffmpeg
```

### Linux
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

## Verwendung

### App starten

```bash
# Nach Installation
python -m ffmpeg_timeslap.main

# Oder direkt
python src/ffmpeg_timeslap/main.py
```

### Workflow

1. **Input Ordner wählen** - Ordner mit Ihrer Bildsequenz
2. **Output Ordner wählen** - Wo das Video gespeichert werden soll
3. **Preset wählen** (optional) - z.B. "YouTube HD" oder "Instagram"
4. **Einstellungen anpassen** - Framerate, Codec, Qualität, Filter
5. **Vorschau** - FFMPEG-Befehl ansehen
6. **Start** - Video erstellen

### Unterstützte Bildformate

- JPEG (.jpg, .jpeg, .JPG, .JPEG)
- PNG (.png, .PNG)
- TIFF (.tiff, .TIFF)

### Namens-Muster

Die App erkennt automatisch verschiedene Namens-Muster:
- `IMG_0001.jpg, IMG_0002.jpg, ...` (mit führenden Nullen)
- `img_1.png, img_2.png, ...` (ohne führende Nullen)
- `photo_001.jpg, photo_002.jpg, ...`

## Presets

### Vorgefertigte Presets

- **YouTube HD** - 1080p, H.264, optimiert für YouTube
- **YouTube 4K** - 2160p, H.265, 4K Upload
- **Instagram** - 1080x1080, quadratisches Format
- **Twitter** - 720p, schnelle Uploads
- **Archiv** - Original-Auflösung, höchste Qualität
- **Schnelle Vorschau** - 720p, ultrafast encoding zum Testen

### Eigene Presets erstellen

1. Einstellungen nach Wunsch anpassen
2. Menü: *Presets → Preset speichern...*
3. Namen und Beschreibung eingeben
4. Fertig - Preset ist gespeichert

Presets werden gespeichert in:
- Windows: `%APPDATA%\FFMPEG_Timeslap\presets\`
- macOS: `~/Library/Application Support/FFMPEG_Timeslap/presets/`
- Linux: `~/.config/FFMPEG_Timeslap/presets/`

## Entwicklung

### Setup für Entwickler

```bash
# Repository klonen
git clone <repository-url>
cd FFMPEG_Timeslap

# Development Dependencies installieren
pip install -e ".[dev]"

# Tests ausführen
pytest tests/

# Code formatieren
black src/

# Linting
flake8 src/
mypy src/
```

### Projekt-Struktur

```
src/ffmpeg_timeslap/
├── core/              # Business Logic
│   ├── models.py
│   ├── sequence_detector.py
│   ├── command_builder.py
│   └── encoder.py
├── gui/               # PyQt5 GUI
│   ├── main_window.py
│   ├── widgets/
│   └── dialogs/
├── presets/           # Preset-System
└── utils/             # Hilfsfunktionen
```

Siehe [claude.md](claude.md) für detaillierte Architektur-Dokumentation.

## Bekannte Einschränkungen

- Aktuell nur einzelne Ordner (kein Batch-Processing in v1.0)
- Primär für Windows optimiert (FFMPEG-Binaries)
- Beste Performance mit fortlaufend nummerierten Bildern

## Troubleshooting

### FFMPEG nicht gefunden
- Überprüfen Sie, ob FFMPEG installiert ist: `ffmpeg -version`
- Konfigurieren Sie den Pfad in den Einstellungen
- Download: https://ffmpeg.org/download.html

### Bilder werden nicht erkannt
- Prüfen Sie, ob Bilder nummeriert sind
- Unterstützte Formate: JPG, PNG, TIFF
- Konsistente Namensgebung verwenden

### Encoding schlägt fehl
- Überprüfen Sie FFMPEG-Output in der App
- Testen Sie mit "Schnelle Vorschau" Preset
- Prüfen Sie Schreibrechte im Output-Ordner

## Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei

FFMPEG ist unter GPL/LGPL lizenziert - siehe `ffmpeg_binaries/LICENSE.txt`

## Autor

**Christian Neumayer**
- Email: numi@nech.at

## Contributing

Contributions sind willkommen! Bitte öffnen Sie ein Issue oder Pull Request.

## Danksagung

- [FFMPEG](https://ffmpeg.org/) - Video encoding
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- [Pillow](https://python-pillow.org/) - Image processing
