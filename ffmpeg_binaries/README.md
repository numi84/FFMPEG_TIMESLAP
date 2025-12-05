# FFMPEG Binaries

Dieser Ordner enthält die mitgelieferten FFMPEG-Binaries für die portable Version der App.

## Installation

### Windows

1. **FFMPEG herunterladen:**
   - Gehe zu: https://www.gyan.dev/ffmpeg/builds/
   - Lade die **"ffmpeg-release-essentials.zip"** herunter
   - Oder direkt: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

2. **Extrahieren:**
   - Entpacke die ZIP-Datei
   - Navigiere zu `bin/ffmpeg.exe` im entpackten Ordner

3. **Kopieren:**
   - Kopiere `ffmpeg.exe` nach: `ffmpeg_binaries/windows/ffmpeg.exe`

4. **Fertig!**
   - Die App wird automatisch die mitgelieferte Binary verwenden

### Alternative: Automatischer Download

Du kannst auch dieses PowerShell-Script verwenden:

```powershell
# download_ffmpeg.ps1
$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipFile = "ffmpeg.zip"
$extractPath = "ffmpeg_temp"

# Download
Write-Host "Lade FFMPEG herunter..."
Invoke-WebRequest -Uri $url -OutFile $zipFile

# Extract
Write-Host "Entpacke..."
Expand-Archive -Path $zipFile -DestinationPath $extractPath

# Find and copy ffmpeg.exe
$ffmpegExe = Get-ChildItem -Path $extractPath -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1
Copy-Item $ffmpegExe.FullName -Destination "windows/ffmpeg.exe"

# Cleanup
Remove-Item $zipFile
Remove-Item $extractPath -Recurse

Write-Host "Fertig! FFMPEG wurde installiert."
```

## Lizenz

FFMPEG ist unter **GPL v2+ / LGPL v2.1+** lizenziert.

Bei Verteilung der App mit FFMPEG müssen Sie:
- Die FFMPEG-Lizenz mitliefern (siehe `LICENSE.txt`)
- Auf die FFMPEG-Projekt-Website verweisen: https://ffmpeg.org/

## Versionsinfo

- Empfohlene Version: FFMPEG 6.0 oder höher
- Benötigte Codecs: libx264, libx265, libsvtav1 (optional)

## Größe

Die `ffmpeg.exe` ist ca. 70-120 MB groß (je nach Build).

Für eine kleinere portable Version können Sie einen Custom-Build ohne unnötige Features erstellen.

## Plattformen

### macOS
Kopiere `ffmpeg` (ohne .exe) nach: `ffmpeg_binaries/macos/ffmpeg`

Download: https://evermeet.cx/ffmpeg/

### Linux
Kopiere `ffmpeg` nach: `ffmpeg_binaries/linux/ffmpeg`

Oder installiere System-weit:
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
```

## Fallback

Die App funktioniert auch ohne mitgelieferte Binary, wenn FFMPEG:
1. Im System-PATH verfügbar ist
2. Oder manuell in den Einstellungen konfiguriert wurde

Der Ordner `ffmpeg_binaries/` wird in `.gitignore` aufgenommen, damit die Binaries nicht ins Repository committed werden.
