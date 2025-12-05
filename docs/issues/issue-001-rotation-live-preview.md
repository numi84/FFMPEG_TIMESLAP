# Issue #1: Rotation ohne Live-Vorschau

## Beschreibung
Der Rotation-Slider zeigt keine sofortige Live-Vorschau. Der Benutzer muss erst auf "Beispielbild laden" klicken, damit die Rotation in der Vorschau sichtbar wird.

## Erwartetes Verhalten
- Beim Bewegen des Rotation-Sliders sollte die Vorschau sofort aktualisiert werden
- Keine zusätzliche Aktion (Button-Klick) sollte notwendig sein

## Aktuelles Verhalten
- Rotation-Slider kann bewegt werden
- Vorschau bleibt unverändert
- Erst nach Klick auf "Beispielbild laden" wird die Rotation angezeigt

## Betroffene Komponenten
- `src/ffmpeg_timeslap/gui/widgets/filter_settings_widget.py` - Rotation-Slider
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py` - Vorschau-Widget
- Signal-Verbindungen zwischen Slider und Preview

## Mögliche Ursache
- Rotation-Slider Signal nicht korrekt mit `set_transforms()` verbunden
- `update_display()` wird nicht bei Slider-Änderung aufgerufen

## Priorität
Medium - Feature funktioniert, aber UX ist beeinträchtigt

## Labels
`bug`, `ui`, `preview`
