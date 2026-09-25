# Profilbibliothek und DXF-Import – 0.3.0

S04 ergänzt ein gemeinsames, frei importierbares DXF-Profil für das gesamte Gestell. Pfosten, Rahmen und Querträger erhalten denselben echten Querschnitt einschließlich Nuten und Hohlräumen. Das bisherige Demo-Vollprofil bleibt auswählbar. Rechteckige Außenmaße, getrennte Profile je Bauteilgruppe und deren Ausrichtung folgen in S05.

## Bedienung

1. Ein Fusion-Konstruktionsdokument öffnen. Unter **Einstellungen verwalten → Eigene DXF-Profile** einen Profilnamen eingeben; alternativ wird zunächst der DXF-Dateiname verwendet.
2. **DXF-Einheit** wählen: „Aus DXF“ liest `$INSUNITS`. Fehlt diese Angabe, ausdrücklich mm, cm, m, in oder ft auswählen. Eine explizite Auswahl überschreibt die Dateiangabe.
3. **Lokale DXF auswählen und prüfen** anklicken. FrameKit liest den Querschnitt, prüft Maße und Konturen und führt in Fusion eine temporäre Probeextrusion aus. Die Prüfgeometrie wird wieder entfernt.
4. Erkannte Außenmaße, Einheit und Anzahl der Hohlräume kontrollieren und **Erkannte Profilmaße sind korrekt** aktivieren. Das bestätigt auch den Maßstab; eine falsch deklarierte Einheit lässt sich nicht allein geometrisch erkennen. Änderungen der Einheit erfordern eine erneute Dateiauswahl und Prüfung.
5. Optional Hersteller, Serie, Artikelnummer, Nutgröße und Material eintragen. Diese Angaben sind Metadaten; „Material“ weist noch kein physikalisches Fusion-Material zu. Es werden keine Herstellerdaten erfunden.
6. **Geprüftes Profil speichern** anklicken. Der Eintrag wird sofort gespeichert und unter **Frame erstellen → Profil für das gesamte Gestell** ausgewählt. Die Demo-Profilbreite wird ausgeblendet; die DXF-Außenmaße bestimmen die Berechnung.
7. Zum Löschen unter **Gespeicherte Profile** auswählen und **Ausgewähltes Profil löschen** anklicken. Der Listeneintrag und die Bibliothekskopie der DXF werden entfernt. Originaldatei und vorhandene Gestelle bleiben erhalten.

Speichern und Löschen wirken sofort und werden durch **Abbrechen** des Gestelldialogs nicht rückgängig gemacht. Die Profilverwaltung ist unabhängig von „Als Standardwerte speichern“. Werkseinstellungen wählen das Demo-Profil, löschen aber keine Bibliothekseinträge. Wird das aktuell gewählte Profil gelöscht, bleibt die fehlende Auswahl sichtbar und die Erstellung wird gesperrt, bis der Benutzer ein anderes Profil auswählt. Ein verschwundenes DXF-Profil wird niemals stillschweigend durch ein Vollprofil ersetzt.

## Anforderungen an die DXF

- ASCII-DXF mit Geometrie im Modellbereich. Unterstützt: **LINE, ARC, CIRCLE, LWPOLYLINE und einfache 2D-POLYLINE**, einschließlich Kreisbögen über Bulge-Werte.
- Nur den Profilquerschnitt exportieren. Blöcke/INSERT vorher auflösen; Beschriftungen, Bemaßungen, Schraffuren, Splines, Ellipsen und andere nicht unterstützte Elemente werden mit einer Fehlermeldung abgewiesen. Binäre DXF wird ebenfalls abgewiesen.
- Querschnitt in **XY bei Z=0**, Normalenrichtung **+Z**, keine Polylinienbreite oder Objekthöhe.
- **Mitte der äußeren Begrenzung im Ursprung (0, 0)**. Gemeint ist nicht der Materialschwerpunkt. Zentrierung und Endpunktzuordnung verwenden eine Toleranz von 0,00001 mm; versetzte Dateien werden nicht automatisch verschoben.
- Quadratische Außenmaße zwischen 1 und 10000 mm. Bei nichtquadratischen Außenmaßen verweist die Fehlermeldung auf S05.
- Geschlossene Konturen, eine zusammenhängende Materialfläche mit beliebig vielen getrennten Hohlräumen. Keine offenen, doppelten, sich kreuzenden oder verzweigten Konturen; keine separaten Materialinseln.
- Höchstens 4 MiB und 2000 Kurvenelemente pro Datei.

Linien, Kreise und Kreisbögen werden als native Fusion-Skizzenelemente erstellt, nicht als angenäherte Polygone. Nach der vorläufigen Konturprüfung prüft Fusion, ob genau eine Materialregion alle eingelesenen Kurven genau einmal verwendet und Anzahl der Konturen sowie Querschnittsfläche übereinstimmen. Nur diese Region wird extrudiert. Die von Fusion ebenfalls erkannten Innenflächen der Hohlräume werden nicht extrudiert. Auch bei der Gestellerstellung wird diese Auswahl erneut geprüft.

## Speicherung und Bauteildaten

Die Bibliothek liegt **außerhalb des Add-in-Installationsverzeichnisses**, neben den persönlichen Einstellungen:

- Windows: `%APPDATA%/FrameKit/profiles/`
- macOS: `~/Library/Application Support/FrameKit/profiles/`

`index.json` enthält Namen, eindeutige IDs, Metadaten, erkannte Maße, Einheit, Mittelpunktbezug, exakte Konturen und Prüfsummen. Jede Original-DXF wird unverändert als `<Profil-ID>.dxf` kopiert. Gleiche Anzeigenamen bleiben über unterschiedliche IDs getrennt. Die ursprüngliche Quelldatei wird nach dem Import nicht mehr benötigt.

Beim Auswählen und Erstellen werden fehlende oder veränderte Bibliotheks-DXF-Dateien erkannt. Ein beschädigter Index wird mit einer Fehlermeldung angezeigt und durch einen neuen Import nicht überschrieben. Bei fehlgeschlagener Indexspeicherung werden neue Kopien entfernt beziehungsweise zum Löschen vorgemerkte Dateien wiederhergestellt.

Gespeicherte Standardwerte und Baugruppen enthalten eine eigenständige Profildefinition einschließlich exakter Konturen und Herkunftsprüfsumme. Die Geometrie vorhandener Gestelle ist nicht mit der Bibliotheksdatei verknüpft. Späteres Bearbeiten bestehender Gestelle bleibt S08 vorbehalten.

DXF-Bauteile verwenden den **Querschnittsmittelpunkt an der ersten Schnittfläche** als lokalen Ursprung und extrudieren entlang der lokalen Z-Achse. Die Platzierung berücksichtigt den Versatz zum bisherigen unteren Eckpunkt. Außenmaße, Aussparungen, Plattenhöhen, Zuschnitte und Mittellinien bleiben dadurch mit dem gleich großen Demo-Profil identisch. Vorschau und Layout bleiben Mittelliniendarstellungen; sie zeigen keine Nutdetails.

## Prüfstand und Fusion-Abnahme

**68 lokale Tests** erfolgreich. Die zusätzlichen Prüfungen decken DXF-Einheiten, Mittelpunkt, Konturschluss, Linien/Bögen/Bulges, Hohlräume, Dateifehler, Speichern/Löschen, Snapshots, Profilauswahl und Fusion-API-Verträge ab. API-Doubles ersetzen nicht den Fusion-Geometriekern.

[`tests/fixtures/synthetic_tslot_40.dxf`](../tests/fixtures/synthetic_tslot_40.dxf) ist ein **synthetisches 40 × 40-mm-Testprofil** mit vier T-förmigen Nuten und fünf Hohlräumen. Es ist kein Herstellerprofil und enthält keine Aussage über Normen oder Tragfähigkeit. Ein Hersteller-Referenzprofil wurde bisher nicht benannt oder bereitgestellt; dessen Abnahme bleibt offen.

Im laufenden Fusion prüfen:

1. Test-DXF importieren, 40 × 40 mm und fünf Hohlräume bestätigen. Nach der Prüfung dürfen keine temporären Prüfkomponenten zurückbleiben; auch Abbruch und Fehler testen.
2. Profil speichern, Dialog schließen und erneut öffnen; Listeneintrag und Auswahl als Standardwerte prüfen.
3. Gestell mit Zwischenböden, Querträgern in beiden Richtungen, Füßen/Rollen und beiden Deckplattenmontagen erstellen. Nuten und Hohlräume müssen auf allen Achsen erhalten bleiben. Außenmaße, Gesamthöhe und Zuschnitte messen.
4. Vorschau und Layout mit den Profilmittellinien der erzeugten Bauteile vergleichen. Parametrischen und direkten Dokumenttyp prüfen; Rückgängig testen.
5. Offene, versetzte, falsch skalierte, doppelte und sich kreuzende Konturen ausprobieren. Unzulässige Dateien dürfen nicht in der Bibliothek landen.
6. Originaldatei verschieben: Bibliotheksprofil bleibt verwendbar. Bibliothekskopie ändern/entfernen: klare Fehlermeldung statt veränderter Geometrie.
7. Ein Profil aus der Liste löschen: Bibliothekskopie entfernt, bestehendes Gestell unverändert, fehlende aktuelle Auswahl sichtbar. Werkseinstellungen und erneute Auswahl prüfen.
8. Ein vom Benutzer festgelegtes reales Herstellerprofil importieren; Nuten, Radien, Hohlräume, Außenmaße und Maßstab gegen dessen Zeichnung prüfen.

## API-Grundlage

Der direkte Fusion-[ImportManager](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_ImportManager.htm) unterstützt den Import innerhalb von Command-Ereignissen nicht. Deshalb verwendet FrameKit einen begrenzten DXF-Reader und native Skizzenoperationen innerhalb des bestehenden Dialogs. Grundlage: [DXF-LWPOLYLINE](https://help.autodesk.com/cloudhelp/2026/DEU/AutoCAD-DXF/files/GUID-748FC305-F3F2-4F74-825A-61F04D757A50.htm), [SketchArcs.addByCenterStartSweep](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchArcs_addByCenterStartSweep.htm), [ProfileLoop](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ProfileLoop.htm), [ProfileCurve](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ProfileCurve.htm) und [Profile.areaProperties](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Profile_areaProperties.htm).
