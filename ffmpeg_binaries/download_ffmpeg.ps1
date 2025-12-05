# PowerShell Script to download FFMPEG for Windows
# Run this from the ffmpeg_binaries folder

Write-Host "FFMPEG Download Script für FFMPEG Timeslap" -ForegroundColor Cyan
Write-Host "=" * 50

$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipFile = "ffmpeg_temp.zip"
$extractPath = "ffmpeg_temp"
$targetPath = "windows\ffmpeg.exe"

# Check if already exists
if (Test-Path $targetPath) {
    Write-Host ""
    Write-Host "WARNUNG: ffmpeg.exe existiert bereits!" -ForegroundColor Yellow
    $response = Read-Host "Möchten Sie es überschreiben? (j/n)"
    if ($response -ne "j" -and $response -ne "J") {
        Write-Host "Abgebrochen." -ForegroundColor Red
        exit
    }
}

# Download
Write-Host ""
Write-Host "Schritt 1/4: Lade FFMPEG herunter..." -ForegroundColor Green
Write-Host "URL: $url"
Write-Host "Größe: ca. 80 MB - Dies kann einige Minuten dauern..."

try {
    Invoke-WebRequest -Uri $url -OutFile $zipFile -UseBasicParsing
    Write-Host "✓ Download abgeschlossen" -ForegroundColor Green
}
catch {
    Write-Host "✗ Fehler beim Download: $_" -ForegroundColor Red
    exit 1
}

# Extract
Write-Host ""
Write-Host "Schritt 2/4: Entpacke ZIP-Archiv..." -ForegroundColor Green

try {
    Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force
    Write-Host "✓ Entpacken abgeschlossen" -ForegroundColor Green
}
catch {
    Write-Host "✗ Fehler beim Entpacken: $_" -ForegroundColor Red
    Remove-Item $zipFile -ErrorAction SilentlyContinue
    exit 1
}

# Find ffmpeg.exe
Write-Host ""
Write-Host "Schritt 3/4: Suche ffmpeg.exe..." -ForegroundColor Green

$ffmpegExe = Get-ChildItem -Path $extractPath -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1

if ($null -eq $ffmpegExe) {
    Write-Host "✗ ffmpeg.exe nicht gefunden!" -ForegroundColor Red
    Remove-Item $zipFile -ErrorAction SilentlyContinue
    Remove-Item $extractPath -Recurse -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "✓ Gefunden: $($ffmpegExe.FullName)" -ForegroundColor Green

# Create windows directory if it doesn't exist
if (-not (Test-Path "windows")) {
    New-Item -ItemType Directory -Path "windows" | Out-Null
}

# Copy
Write-Host ""
Write-Host "Schritt 4/4: Kopiere ffmpeg.exe..." -ForegroundColor Green

try {
    Copy-Item $ffmpegExe.FullName -Destination $targetPath -Force
    Write-Host "✓ Kopiert nach: $targetPath" -ForegroundColor Green
}
catch {
    Write-Host "✗ Fehler beim Kopieren: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Write-Host ""
Write-Host "Räume auf..." -ForegroundColor Green
Remove-Item $zipFile -ErrorAction SilentlyContinue
Remove-Item $extractPath -Recurse -ErrorAction SilentlyContinue

# Get version
Write-Host ""
Write-Host "=" * 50
Write-Host "Installation abgeschlossen!" -ForegroundColor Green
Write-Host ""

# Try to get version
try {
    $versionOutput = & $targetPath -version 2>&1 | Select-Object -First 1
    Write-Host "Version: $versionOutput" -ForegroundColor Cyan
}
catch {
    Write-Host "Konnte Version nicht ermitteln." -ForegroundColor Yellow
}

$fileSize = (Get-Item $targetPath).Length / 1MB
Write-Host "Größe: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "FFMPEG wurde erfolgreich installiert!" -ForegroundColor Green
Write-Host "Pfad: $(Resolve-Path $targetPath)" -ForegroundColor Green
Write-Host ""
Write-Host "Die App kann nun FFMPEG verwenden." -ForegroundColor White
