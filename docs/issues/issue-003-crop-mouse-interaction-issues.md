# Issue #3: Crop-Maus-Interaktion funktioniert nicht korrekt

**Status:** ✅ RESOLVED

## Beschreibung
Die interaktive Crop-Auswahl mit der Maus weist mehrere Probleme auf, die die Benutzerfreundlichkeit beeinträchtigen.

## Problem 1: Bild wird nicht richtig skaliert beim ersten Laden
### Erwartetes Verhalten
- Bild wird automatisch an die Widget-Größe angepasst
- Aspect Ratio wird beibehalten
- Bild ist zentriert im Widget

### Aktuelles Verhalten
- Bild wird zu groß geladen
- Bild passt nicht in den sichtbaren Bereich
- Keine automatische Skalierung beim ersten Laden

### Betroffener Code
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py` - Zeilen 57-129 (`update_display()`)
- `InteractiveCropLabel.set_image()` - Initialisierung

## Problem 2: Crop-Rechteck lässt sich nicht richtig verschieben/vergrößern
### Erwartetes Verhalten
- Crop-Rechteck kann mit der Maus verschoben werden
- Resize-Handles (gelbe Punkte) sind an den Ecken/Kanten des Rechtecks
- Handles bleiben am Rechteck, auch wenn das Bild neu skaliert wird

### Aktuelles Verhalten
- Rechteck kann nicht korrekt verschoben werden
- Wenn Bild durch Neuladen kleiner wird, ist das Rechteck zwar kleiner
- **ABER:** Die Resize-Handles (Punkte zum Ziehen) sind ganz am Rand des Bildes, nicht am Rechteck
- Koordinaten-Transformation zwischen Display und Original stimmt nicht

### Betroffener Code
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py` - Zeilen 131-149 (`_scale_rect_to_display()`, `_scale_point_to_original()`)
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py` - Zeilen 151-167 (`_draw_handles()`)
- Mouse-Event-Handler für Drag & Resize

### Mögliche Ursache
- `display_scale` wird nicht korrekt berechnet nach Transformationen
- Skalierung zwischen original/transformed/display Koordinatensystemen inkonsistent
- Nach Rotation/Flip ändern sich die Dimensionen, aber Handles nutzen falsches Koordinatensystem

## Reproduktion
1. Ordner mit Bildern laden
2. Crop-Bereich mit Maus festlegen
3. "Beispielbild laden" klicken
4. Beobachten: Rechteck ist kleiner, aber Handles sind am falschen Ort

## Priorität
High - Kernfunktion (interaktives Cropping) ist nicht benutzbar

## Labels
`bug`, `ui`, `crop`, `mouse-interaction`, `coordinate-transform`

## Zusätzliche Notizen
Das Problem hängt wahrscheinlich mit der kürzlich durchgeführten Änderung der Filter-Reihenfolge zusammen (Rotate/Flip vor Crop). Die Koordinaten-Transformationen müssen überarbeitet werden, um mit dem neuen Workflow zu funktionieren.

---

## Resolution

**Resolved on:** 2025-12-05

### Changes Made

#### Problem 1: Image Scaling Fixed
- Added proper widget size validation in `update_display()` to prevent division by zero
- Ensured minimum size is used as fallback when widget size is invalid
- Added explicit integer conversion for scaled dimensions to prevent Qt warnings
- Added `updateGeometry()` call in `set_image()` to force proper widget layout before first display

#### Problem 2: Mouse Coordinate Transformation Fixed
- Added `display_offset` tracking to account for centered image position within widget
- Implemented `_widget_pos_to_pixmap_pos()` method to convert widget coordinates to pixmap coordinates
- Updated all mouse event handlers to properly account for centering offset
- Fixed coordinate transformation in drag and resize operations
- Ensured crop rectangle coordinates are in transformed image space (not original)

#### Additional Improvements
- Modified `set_transforms()` to automatically reset crop rectangle when transformations change
- This ensures crop coordinates are always valid for the current transformation state
- Added better comments explaining coordinate system transformations

### Testing Performed
- Verified image loads properly scaled on first display
- Tested crop rectangle drag and resize with mouse
- Confirmed handles stay at correct positions after transformation changes
- Verified coordinate transformations work correctly with rotation and flip operations

### Files Modified
- `src/ffmpeg_timeslap/gui/widgets/interactive_crop_widget.py`
