# Installation und Abnahme – FrameKit 0.9.0 (S12)

## Paket und Zielumgebung

S12 stellt ein portables ZIP-Paket und seit dem Benutzerauftrag vom 27.09.2026 zusätzlich einen Windows-Installer mit Inno Setup bereit. Die EXE liegt unter `installer/dist/FrameKit-Setup-0.9.0.exe`; Aufbau und Build entsprechen dem SegmentJoinPilot-Setup. [Installer-Anleitung](../installer/README.md). Die lokale Paketprüfung erfolgt unter Windows, Build 26200, mit Python 3.14.0 aus der vorhandenen Fusion-Installation. Für Benutzer ist keine separate Python-Installation notwendig.

Die genaue Fusion-Buildnummer und die zu bestätigende Plattform sind noch vom Benutzer anzugeben. Es wird keine ungetestete Mindestversion zugesichert. Windows ist die vorläufige Abnahmeplattform. Das Manifest lässt weiterhin Windows und macOS zu; macOS ist nicht geprüft und erhält in 0.9.0 keine Abnahmebestätigung. Die native Abnahme ist offen; 0.9.0 ist ein Prüfpaket, noch keine Freigabe 1.0.0.

## Windows-EXE installieren

Fusion schließen, FrameKit-Setup-0.9.0.exe ausführen und das vorgeschlagene Add-in-Verzeichnis prüfen. Das Setup benötigt keine Administratorrechte, unterstützt Deutsch/Englisch und erkennt die Produktordner Autodesk Fusion sowie Autodesk Fusion 360. Danach Fusion neu starten und das Add-in aktivieren. Updates mit geschlossenem Fusion im bisherigen Zielordner ausführen; Deinstallation über die Windows-Appverwaltung. Persönliche Daten liegen separat unter %APPDATA%/FrameKit und bleiben erhalten. Andere Add-in-Kopien werden nicht entfernt.

Build mit Inno Setup 6.7.0 am 27.09.2026 erfolgreich; Installation/Update/Deinstallation sind noch praktisch zu prüfen. Die folgenden Schritte beschreiben die alternative ZIP-Installation.

## ZIP installieren

1. `FrameKit-0.9.0.zip` in einen dauerhaften, beschreibbaren lokalen Ordner entpacken, beispielsweise `Dokumente/FrameKit-0.9.0`. Nicht direkt aus dem ZIP starten.
2. Optional vor dem Entpacken die SHA-256-Prüfsumme mit der beiliegenden `.zip.sha256` vergleichen. Unter PowerShell: `Get-FileHash -Algorithm SHA256 -LiteralPath .\FrameKit-0.9.0.zip`. Der Hash schützt vor versehentlichen Änderungen; er ist keine digitale Signatur.
3. In Fusion **Dienstprogramme → Zusatzmodule → Skripte und Zusatzmodule** (`Umschalt+S`) öffnen. Unter **Zusatzmodule** das Hinzufügen-Symbol wählen.
4. Den entpackten Unterordner **FrameKit** wählen. Direkt darin liegen `FrameKit.py` und `FrameKit.manifest`; nicht den übergeordneten Paketordner auswählen.
5. FrameKit ausführen und ein Konstruktionsdokument öffnen. Unter **Volumenkörper → Erstellen** müssen Gestellerstellung, Gestellbearbeitung und CSV-Export verfügbar sein. Den automatischen Start erst nach erfolgreichem manuellem Start aktivieren.
6. Im Info-Reiter Version **0.9.0** kontrollieren.

Das Paket enthält den vollständigen Add-in-Ordner mit Python-Bibliotheken, Icons und STEP-Winkeln, Dokumentation, Lizenz und Beispiele. Es schreibt selbst keine Dateien in die Benutzerkonfiguration.

## Update und Rückkehr zur vorherigen Version

1. Offene Fusion-Dokumente speichern. Vor dem Update im Einstellungsreiter eine Datensicherung exportieren. Zusätzlich bei beendetem Fusion den vollständigen Benutzerdatenordner kopieren, wenn auch persönliche Standardwerte gesichert werden sollen.
2. FrameKit stoppen und Fusion schließen. Das neue ZIP in einen **neuen Versionsordner** entpacken. Die vorherige Installation behalten.
3. Fusion öffnen, die alte Add-in-Registrierung entfernen und den neuen `FrameKit`-Ordner registrieren. Nicht beide Versionen automatisch starten lassen.
4. Version, gespeicherte Standardwerte, Vorlagen und Bibliotheken prüfen. Ein vorhandenes Gestell in einer Kopie des Dokuments laden und bearbeiten.
5. Bei Problemen FrameKit stoppen, Fusion schließen und anschließend die vorherige Version erneut registrieren. Bei Bedarf den zuvor separat gesicherten Benutzerdatenordner wiederherstellen. Neuere Datenformate sind in älteren Versionen nicht allgemein zugesichert.

Keine Paketdatei überschreibt `settings.json`, `templates.json`, `accessories.json` oder eigene Profile. Ein Update ersetzt ausschließlich den gewählten Installationsordner beziehungsweise dessen Registrierung. Bestehende Fusion-Dokumente werden erst durch ausdrücklich ausgeführte Bearbeitungsbefehle geändert.

## Datensicherung

- Windows: `%APPDATA%/FrameKit`
- macOS (ungeprüft): `~/Library/Application Support/FrameKit`

Der Ordner enthält persönliche Standardwerte, Vorlagen und Bibliotheken einschließlich Profildateien. Eine vollständige Ordnerkopie bei beendetem Fusion sichert diesen Stand. Fusion-Dokumente separat speichern/sichern.

Die integrierte JSON-Sicherung überträgt Vorlagen und Bibliotheken mit DXF-Dateien, aber keine persönlichen Standardwerte und keine Fusion-Dokumente. Import zuerst prüfen, Konfliktregel auswählen und erst dann übernehmen. Details: [Vorlagen und Datensicherung](vorlagen_datensicherung.md).

## Deinstallieren

FrameKit stoppen, automatischen Start deaktivieren und die Registrierung unter Zusatzmodule entfernen. Fusion schließen und ausschließlich den zuvor entpackten Versionsordner entfernen. Benutzerkonfiguration und Fusion-Dokumente bleiben erhalten. Wer auch persönliche Daten entfernen möchte, sichert den oben genannten Benutzerdatenordner zuvor separat und entfernt ihn bewusst unabhängig von der Installation.

## Paket reproduzieren und prüfen

Im Quellrepository mit Python (Standardbibliothek, keine Zusatzpakete):

```text
python -m unittest discover -s tests -v
python installer/create_examples.py
python installer/package.py
python installer/package.py --verify dist/FrameKit-0.9.0.zip
```

`dist` enthält ZIP und äußere SHA-256-Prüfsumme. `PACKAGE.json` im ZIP verzeichnet jede Nutzdatei mit SHA-256. Die Prüfung kontrolliert Pflichtdateien, Version/Manifest, Python-Syntax, Pfade, doppelte Einträge und vollständige Hash-Zuordnung. Persönliche Einstellungsdateien, Bytecode und Git-Daten dürfen nicht enthalten sein. Das Archiv wird zur Prüfung nicht extrahiert.

Identische Quelldateien erzeugen identische ZIP-Bytes: sortierte Einträge, festes Datum und Dateirechte sowie unkomprimierte Speicherung vermeiden variable ZIP-Metadaten und Kompressionsunterschiede. Geänderte Zeilenenden oder Dokumentation ändern bewusst die Prüfsumme. Die Tests bauen zweimal und vergleichen die Bytes; manipulierte und unvollständige Archive müssen scheitern.

Der Prüfer ist auch im Paket unter `installer/package.py` enthalten; dort steht nur die `--verify`-Verwendung zur Verfügung, der Build erfordert das Quellrepository. Ein erfolgreicher Pakettest bestätigt keine native Fusion-Geometrie.

## Native Abnahmeprotokolle

Prüfdatum: **26.09.2026**. Paketversion: **0.9.0**. Fusion-Build: **noch anzugeben**. Betriebssystem der nativen Prüfung: **noch zu bestätigen**. Prüfer: **noch anzugeben**.

Für die Prüfung ein neues Dokument verwenden. Beispiele aus [examples](../examples/README.md) über die Datensicherung importieren; Konfliktregel **Als Kopie übernehmen** schützt gleichnamige eigene Einträge. Die JSON-Erwartungswerte nennen Modellmengen aus der lokalen Berechnung, keine bereits in Fusion gemessenen Ergebnisse.

| Fall | Durchführung und Abnahmekriterium | Stand 0.9.0 |
| --- | --- | --- |
| Installation / Start | Frisches ZIP registrieren; drei Befehle, Version, Icons und manuellen/automatischen Start prüfen | Offen |
| Einfaches Gestell | Beispiel 01 ohne Zwischenboden; Außenmaße 800 × 500 × 750 mm messen, Vorschau und Baugruppe vergleichen | Offen |
| Böden / Querträger | Beispiel 02; zwei Böden bei 400/800 mm, freie Felder gleich und Querträger bündig; Platten und Aussparungen prüfen | Offen |
| Gruppenprofile | Beispiel 05; Pfosten als Nutprofil, Rahmen als Vollprofil; Drehung ändern und Maße/Benennung prüfen | Offen |
| Gemischte Rollen | Beispiel 03; zwei Lenk- und zwei Bockrollen, gleiche Bauhöhe; Gesamthöhe messen | Offen |
| Füße / Absenkbare Rollen | Beispiele 06/07; Bauhöhe, Stellungsdaten, Zylinderplatzhalter und Höhenbezug prüfen | Offen |
| Eigener DXF-Import | `synthetic_tslot_40.dxf` neu importieren; Beispiel 04 mit echten Konturen erzeugen; Hohlräume erhalten | Offen |
| STEP-Winkel | Winkel aktivieren; Positionen und Sichtbarkeit prüfen, auch beim Bearbeiten im Direktmodus | Offen |
| Ungültige Eingaben | Negative Maße, überlappende Böden, unterschiedliche Zubehörhöhen und defekte DXF ablehnen; keine Teilbaugruppe | Offen |
| Vorschau / Abbrechen | Maße ändern, Vorschau prüfen, abbrechen; Original sichtbar und keine temporären Objekte | Offen |
| Bearbeiten / Isolation | Zwei Gestelle plus fremde Komponente; nur gewähltes Gestell ändern; IDs und gespeicherte Konfiguration prüfen | Offen |
| Undo / Redo | Erstellen und Neuaufbau rückgängig/wiederholen, Dokument speichern/öffnen; keine alte Ersatzhistorie oder Teilbaugruppe | Offen |
| CSV | Beide Formate und beide Listen exportieren; Mengen mit Erwartungswerten/Baugruppe vergleichen, erneut nach Änderung; fehlende Befestigungen gekennzeichnet | Offen |
| Vorlagen | Speichern, laden, umbenennen, löschen; Bestätigung aus 0.8.0 vorhanden, Paketregression noch prüfen | Offen |
| Sicherung | Auf leere Benutzerkonfiguration übertragen; Skip/Kopie/Ersetzen, beschädigte JSON/DXF und Abbrechen; vorherige Daten bleiben bei Fehler erhalten | Offen |
| Update / Deinstallation | Separaten Versionsordner verwenden; Standardwerte, Vorlagen, eigene DXF und Dokumente bleiben erhalten | Offen |

Je ausgeführtem Fall Datum, Fusion-Build, Ist-Ergebnis und gegebenenfalls Fehler-/Screenshotreferenz ergänzen. Frühere Benutzerbestätigungen stehen im [Ablaufplan](ablaufplan.md); sie ersetzen nicht die vollständige Abnahme des neuen Pakets. S13 startet erst nach gesondertem Auftrag und erfolgreicher Abnahme.
