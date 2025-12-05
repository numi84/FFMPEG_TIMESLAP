FFmpeg-Einstellungen für Timelapse-Videos aus Bildern
FFmpeg bietet zahlreiche Parameter, um aus einer Bildsequenz ein professionelles Timelapse-Video zu erstellen. Hier sind die wichtigsten Einstellungsmöglichkeiten:

Grundlegender Befehl
Der einfachste Befehl sieht so aus:

bash
ffmpeg -framerate 25 -i img_%04d.jpg -c:v libx264 -pix_fmt yuv420p timelapse.mp4
Wichtige Eingabe-Parameter
Bildsequenz-Muster (-i)
FFmpeg unterstützt verschiedene Muster für die Eingabe-Dateinamen:​

Mit führenden Nullen: -i img_%03d.png erfasst img_001.png bis img_999.png

Ohne führende Nullen: -i img_%d.png erfasst img_1.png bis img_999.png

Glob-Pattern: -pattern_type glob -i "*.JPG" erfasst alle JPGs​

Startnummer (-start_number)
Falls deine Bildsequenz nicht bei 0 oder 1 beginnt, kannst du die Startnummer angeben:​

bash
ffmpeg -start_number 1233 -i img_%04d.jpg output.mp4
Bildrate (-framerate / -r)
Die Eingabe-Framerate bestimmt, wie lange jedes Bild angezeigt wird:​

-framerate 25 – Standardwert, 25 Bilder pro Sekunde (schnelles Video)

-framerate 10 – 10 Bilder pro Sekunde (langsameres Video)

-framerate 2 – Für langsame Slideshows, 2 Bilder pro Sekunde

Wichtig: Wenn -r vor dem Input steht, interpretiert es die Bildsequenz mit dieser Framerate. Bei Bildsequenzen ohne Metadata nimmt FFmpeg standardmäßig 25 fps an.​

Videocodec-Einstellungen
Codec (-c:v / -vcodec)
Die gängigsten Codecs für Timelapses:​

Codec	Beschreibung
libx264	H.264 – beste Kompatibilität, empfohlen
libx265	H.265/HEVC – kleinere Dateien, bessere Qualität
libsvtav1	AV1 – modernster Codec, beste Kompression
Qualität (-crf)
Der Constant Rate Factor kontrolliert die Qualität bei Single-Pass-Encoding:​

-crf 0 – Verlustfrei (sehr große Datei)

-crf 18 – Perzeptuell verlustfrei, empfohlen​

-crf 23 – Standard/Ausgeglichen

-crf 28-30 – Kleinere Dateien, niedrigere Qualität

Hinweis: H.264 und H.265 verwenden unterschiedliche CRF-Skalen für gleiche Qualität.​

Encoding-Geschwindigkeit (-preset)
Beeinflusst Encoding-Zeit vs. Dateigröße:​

bash
-preset ultrafast  # Schnell, größere Datei, gut zum Testen
-preset medium     # Standard, guter Kompromiss
-preset slow       # Bessere Kompression, längere Encoding-Zeit
-preset veryslow   # Maximale Kompression
Profil und Level (-profile:v, -level)
Für maximale Kompatibilität mit Geräten:​

bash
-profile:v high -level 4.0
Pixelformat und Kompatibilität
Pixelformat (-pix_fmt)
Essenziell für Wiedergabe-Kompatibilität:​

bash
-pix_fmt yuv420p
Ohne diese Option können viele Player das Video nicht abspielen. Dieses Format ist praktisch universell kompatibel.​

Movflags für Streaming
Für schnelleres Starten beim Web-Streaming:​

bash
-movflags +faststart
Video-Filter (-vf)
Skalierung
Die Ausgabeauflösung anpassen:​

bash
-s 1920x1080        # Exakte Größe
-s hd1080           # Kurzform für 1080p
-vf "scale=1920:-1" # Breite festlegen, Höhe automatisch
Für ungerade Dimensionen (wichtig bei yuv420p):​

bash
-vf "pad=w='ceil(iw/2)*2':h='ceil(ih/2)*2'"
Deflicker-Filter
Reduziert Helligkeitsschwankungen zwischen Frames – sehr nützlich bei Timelapses:​

bash
-vf "deflicker,mode=pm,size=10"
Mehrere Filter kombinieren
bash
-vf "scale=1920:1080,format=yuv420p,deflicker"
Vollständige Beispiel-Befehle
Einfaches Timelapse
bash
ffmpeg -framerate 30 -i image%04d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4
Hochwertige Ausgabe mit allen Optimierungen
bash
ffmpeg -framerate 25 -pattern_type glob -i "*.JPG" \
  -c:v libx264 -preset slow -crf 18 \
  -profile:v high -level 4.0 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  timelapse.mp4
H.265 mit Deflicker und Skalierung
bash
ffmpeg -pattern_type glob -i "*.JPG" \
  -vf "deflicker,scale=hd1080" \
  -c:v libx265 -crf 20 -preset medium \
  -pix_fmt yuv420p -tag:v hvc1 \
  timelapse.mp4
Mit Dateiliste (für nicht-fortlaufende Dateinamen)
Erstelle eine files.txt:

text
file 'IMG_0001.jpg'
file 'IMG_0005.jpg'
file 'IMG_0008.jpg'
Dann:

bash
ffmpeg -f concat -safe 0 -i files.txt -c:v libx264 -pix_fmt yuv420p output.mp4
Parameter-Übersicht
Parameter	Funktion	Typische Werte
-framerate	Eingabe-Bildrate	10, 25, 30 fps
-r	Ausgabe-Bildrate	24, 30, 60 fps
-c:v	Video-Codec	libx264, libx265
-crf	Qualitätsfaktor	18-23 (niedriger = besser)
-preset	Encoding-Geschwindigkeit	slow, medium, fast
-pix_fmt	Pixelformat	yuv420p
-s	Ausgabegröße	1920x1080, hd1080
-vf	Videofilter	scale, deflicker
-pattern_type glob	Glob-Pattern aktivieren	für *.jpg
-start_number	Erste Bildnummer	beliebige Zahl
Diese Optionen lassen sich je nach Bedarf kombinieren, um das gewünschte Ergebnis zu erzielen