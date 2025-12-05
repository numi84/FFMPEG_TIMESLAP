# Issue #2: Crop-Einstellungen beim Bilder-Slider verloren

## Beschreibung
Wenn der Benutzer mit dem Bild-Slider durch die Bildsequenz navigiert, gehen die zuvor festgelegten Crop-Einstellungen verloren.

## Erwartetes Verhalten
- Crop-Einstellungen (Position, Größe) bleiben beim Wechsel zwischen Bildern erhalten
- Der Crop-Bereich bleibt konsistent über alle Bilder hinweg
- Nur das Hintergrundbild sollte sich ändern, nicht die Crop-Maske

## Aktuelles Verhalten
- Benutzer definiert Crop-Bereich (z.B. x=100, y=100, w=500, h=500)
- Benutzer bewegt den Bild-Slider zu einem anderen Bild
- Crop-Einstellungen werden zurückgesetzt oder gehen verloren

## Betroffene Komponenten
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py` - Zeilen 365-388 (`load_image()`)
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py` - Zeilen 351-356 (`on_image_slider_changed()`)

## Mögliche Ursache
- `load_image()` ruft `set_image()` auf, was möglicherweise den Crop-Bereich zurücksetzt
- Crop-Rechteck wird nicht zwischen Bildwechseln persistiert

## Lösungsansatz
- Crop-Einstellungen vor Bildwechsel speichern
- Nach `set_image()` die gespeicherten Crop-Einstellungen wiederherstellen
- Oder: `set_image()` so anpassen, dass es den Crop-Bereich nicht zurücksetzt

## Priorität
High - Benutzer kann aktuell nicht effektiv mit dem Bild-Slider arbeiten

## Labels
`bug`, `ui`, `crop`, `state-management`
