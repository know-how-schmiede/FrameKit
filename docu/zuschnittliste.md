# Zuschnittliste – S09 / 0.7.0

Unter **Volumenkörper → Erstellen → FrameKit: CSV-Listen exportieren** ein gespeichertes FrameKit-Gestell auswählen. Der Befehl ist unabhängig vom Erstellungs- und Bearbeitungsdialog. Änderungen vor dem Export mit „Neu aufbauen“ übernehmen.

1. Gestell anhand des Namens in der Auswahlliste auswählen.
2. CSV-Format wählen: **Deutsch** verwendet Semikolon und Dezimalkomma, **International** Komma und Dezimalpunkt.
3. **CSV speichern** anklicken und im Speicherdialog den Zielpfad mit Endung `.csv` wählen. Abbrechen schreibt keine Datei.

Die Datei enthält Hersteller, Serie, Artikelnummer, Bezeichnung, Länge in Millimetern, Menge, Endbearbeitung, Bauteil-IDs, Profil-ID und Gestell-ID. Fehlende Herstellerangaben bleiben leer. Texte stammen aus den gespeicherten Profileigenschaften; Umbenennen von Komponenten beeinflusst sie nicht. Vollständige Profildefinition, Zuschnittlänge und Endbearbeitung bestimmen die Zusammenfassung. Verschiedene Profil-IDs werden auch bei gleichem Anzeigenamen getrennt gehalten. Längen werden für Zusammenfassung und CSV-Ausgabe kaufmännisch auf drei Nachkommastellen in mm (0,001 mm) gerundet. Überflüssige Nachkommastellen entfallen: beispielsweise 439,999999 → 440 und 939,999999 → 940. Die Modellgeometrie bleibt unverändert.

Derzeit erzeugte Profile haben beidseitig rechtwinklige Enden ohne weitere Bearbeitung. Die Angabe ist im Bauteilmodell gespeichert. Platten, Füße/Rollen und Winkel gehören zur späteren Stückliste (S10) und sind hier nicht enthalten. Schnittfuge und Lagerstangenoptimierung sind nicht Bestandteil von S09.

Exportgrundlage sind die gespeicherten FrameKit-Einstellungen und Bauteil-IDs, keine nachträglichen manuellen Änderungen an der Geometrie. Das Exportieren verändert weder Baugruppe noch Historie. Eingebettete Profildaten ermöglichen den Export auch ohne ursprüngliche DXF-Datei. Die Prüfung des ausgewählten Gestells verhindert den Export ungültiger oder nicht eindeutig zugeordneter Daten.

UTF-8 mit BOM erhält Umlaute in Excel/LibreOffice. Felder mit Trennzeichen oder Anführungszeichen werden CSV-gerecht maskiert. Formelähnliche Metadaten erhalten ein führendes Apostroph. Schreiben erfolgt über eine temporäre Datei im Zielordner; bei Schreibfehlern bleibt eine bestehende Zieldatei erhalten.

## Prüfstand

**Benutzerbestätigung:** „Zuschnittliste funktioniert.“ Der CSV-Export in Version 0.7.0 ist damit in Fusion als funktionsfähig bestätigt. Einzelne Sonderfallprüfungen sind dadurch nicht separat bestätigt.

142 lokale Tests erfolgreich, darunter neun zusätzliche Exporttests. Geprüft: Mengen, Längen und IDs am berechneten Modell, neue Längen nach Bearbeitung, gleichnamige unterschiedliche Definitionen, verschiedene Endbearbeitungen, Umlaute/CSV-Maskierung, beide Formate, atomarer Dateiaustausch, Gestellauswahl und Abbrechen.

Ergänzende Prüffälle (nicht einzeln bestätigt): zwei unterschiedliche Gestelle erstellen; jeweils exportieren und Profile in der Baugruppe nachzählen. Ein Gestell bearbeiten und erneut exportieren; neue Längen sowie erhaltene Bauteil-IDs vergleichen. Beide CSV-Formate in der vorgesehenen Tabellenanwendung öffnen. Speicherdialog abbrechen und schreibgeschütztes Ziel testen. Bearbeiten-Icon in hellem und dunklem Theme prüfen.

Das Icon für **Gestell bearbeiten** verwendet jetzt das bestehende Grundicon mit zusätzlichem Stift in beiden Größen und Farbvarianten.

API-Grundlage des Speicherdialogs: [Autodesk File Dialog Sample](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/FileDialogSample_Sample.htm).

Das CSV-Export-Icon ergänzt dasselbe Grundicon um einen nach außen gerichteten Exportpfeil, ebenfalls in beiden Größen und Farbvarianten.

Seit S10 / 0.7.2 bietet derselbe Befehl auch [Stückliste oder beide Listen](stueckliste.md).
