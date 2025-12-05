# Issue #2: Crop-Einstellungen beim Bilder-Slider verloren [GELÖST]

## Status
✅ **GELÖST** - 2025-12-05

## Beschreibung
Wenn der Benutzer mit dem Bild-Slider durch die Bildsequenz navigiert, gehen die zuvor festgelegten Crop-Einstellungen verloren.

## Erwartetes Verhalten
- Crop-Einstellungen (Position, Größe) bleiben beim Wechsel zwischen Bildern erhalten
- Der Crop-Bereich bleibt konsistent über alle Bilder hinweg
- Nur das Hintergrundbild sollte sich ändern, nicht die Crop-Maske

## Aktuelles Verhalten (vor Fix)
- Benutzer definiert Crop-Bereich (z.B. x=100, y=100, w=500, h=500)
- Benutzer bewegt den Bild-Slider zu einem anderen Bild
- Crop-Einstellungen werden zurückgesetzt oder gehen verloren

## Betroffene Komponenten
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py` - Zeilen 443-481 (`load_image()`)

## Ursache
- `load_image()` rief `set_image()` auf, welches das `crop_rect` auf die volle Bildgröße zurücksetzte
- Crop-Rechteck wurde nicht zwischen Bildwechseln persistiert

## Lösung
Die `load_image()` Methode wurde angepasst:

1. **Crop-Einstellungen speichern**: Vor dem Laden eines neuen Bildes werden die aktuellen Crop-Einstellungen gespeichert
2. **Crop-Einstellungen wiederherstellen**: Nach dem Aufruf von `set_image()` werden die gespeicherten Einstellungen wiederhergestellt
3. **Validierung**: Es wird geprüft, ob die gespeicherten Crop-Einstellungen innerhalb der neuen Bilddimensionen liegen

```python
# Save current crop settings before loading new image
saved_crop = None
if self.crop_label.original_pixmap:
    saved_crop = QRect(self.crop_label.crop_rect)

self.crop_label.set_image(pixmap)

# Restore crop settings if they exist and are valid for new image
if saved_crop is not None:
    # Check if saved crop fits within new image dimensions
    if (saved_crop.right() <= pixmap.width() and
        saved_crop.bottom() <= pixmap.height()):
        self.crop_label.set_crop_rect(
            saved_crop.x(), saved_crop.y(),
            saved_crop.width(), saved_crop.height()
        )
```

## Änderungen
- Datei: [interactive_crop_widget.py:443-481](../src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py#L443-L481)
- Crop-Einstellungen werden beim Bildwechsel beibehalten
- Validierung stellt sicher, dass Crop-Bereich in neuen Bilddimensionen passt

## Priorität
High - Benutzer kann aktuell nicht effektiv mit dem Bild-Slider arbeiten

## Labels
`bug`, `ui`, `crop`, `state-management`, `fixed`
