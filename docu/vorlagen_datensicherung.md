# Vorlagen und Datensicherung – 0.8.0 (S11)

Unter **Einstellungen verwalten → Vorlagen und Datensicherung** stehen benannte Gestellvorlagen und die Übertragung eigener Bibliotheken zur Verfügung.

## Vorlagen

- Gestell im ersten Reiter einstellen, einen Namen eingeben und **Aktuelle Werte als neue Vorlage speichern** wählen.
- Eine gespeicherte Vorlage auswählen und **Vorlage laden** wählen. Die Werte werden in den bestehenden Dialog übernommen; erst die Gestellerstellung beziehungsweise der Neuaufbau ändert das Dokument.
- Zum Umbenennen einen neuen Namen eingeben und **Vorlage umbenennen** wählen. **Vorlage löschen** entfernt die ausgewählte Vorlage.
- Namen sind ohne Beachtung der Groß-/Kleinschreibung eindeutig und maximal 80 Zeichen lang. Gleiche Namen werden beim Speichern abgelehnt.
- Vorlagen enthalten die vollständige Konfiguration mit eingebetteten Profil- und Zubehördefinitionen. Auch nach Entfernen eines Bibliothekseintrags bleiben gespeicherte Profilkonturen verwendbar.
- Verwaltungsschaltflächen speichern sofort. Abbrechen des Gestelldialogs nimmt bereits gespeicherte, umbenannte oder gelöschte Vorlagen nicht zurück. Persönliche Standardwerte bleiben separat bestehen.

## Sicherung exportieren und importieren

**Sicherung exportieren** schreibt eine JSON-Datei mit allen Vorlagen, der Zubehörbibliothek, der Profilbibliothek und deren DXF-Dateien. DXF-Dateien sind Base64-kodiert enthalten. Persönliche Standardwerte und Fusion-Dokumente gehören nicht zum Archiv; gewünschte Standardkonfigurationen zuvor als Vorlage speichern. Die installierten STEP-Winkel gehören zum Add-in-Paket.

Vor dem Import eine Konfliktregel wählen:

| Regel | Verhalten bei gleichem Namen oder gleicher ID |
| --- | --- |
| Überspringen | Bestehenden Eintrag behalten |
| Als Kopie übernehmen | Neue ID und freien Namen mit „Kopie“-Zusatz erzeugen |
| Ersetzen | Konfliktierende Einträge durch den importierten Eintrag ersetzen |

Die Regel gilt für die ausgewählte Sicherung. **Sicherung zum Import prüfen** liest und validiert die Datei und zeigt für jeden Eintrag die geplante Aktion. Erst **Geprüften Import ausführen** schreibt diese Daten. Zum Abbrechen den Dialog schließen oder keine Übernahme ausführen. Eine geänderte Konfliktregel oder zwischenzeitlich geänderte Benutzerdaten erfordern eine erneute Prüfung.

Gespeicherte Konfigurationen behalten ihre eingebetteten Definitionen; das Ersetzen eines Bibliothekseintrags verändert keine bestehenden Gestelle oder Vorlagen. Aktuelle Dialogauswahlen und persönliche Standardwerte bleiben beim Import erhalten.

## Speicherung und Fehlerbehandlung

Vorlagen liegen in `templates.json` neben `settings.json`. Export und Import prüfen Schema, Namen/IDs, Konfigurationen, Profilkonturen und die SHA-256-Prüfsummen der DXF-Dateien. Importierte DXF-Daten müssen zur gespeicherten Kontur passen. Unbekannte Dateinamen werden abgelehnt; es werden keine Archivpfade extrahiert. Die maximale Importdateigröße beträgt 100 MB.

Beschädigte vorhandene Bibliotheken werden nicht stillschweigend überschrieben. Dateien werden jeweils atomar ersetzt; bei einem Schreibfehler werden bereits angefasste Dateien aus dem vorher eingelesenen Stand zurückgeschrieben. Das ist keine transaktionale Garantie bei Stromausfall oder gleichzeitigem Zugriff mehrerer Fusion-Prozesse. Nicht mehr referenzierte alte DXF-Dateien werden beim Import nicht gelöscht.

## Prüfstand

160 lokale Tests erfolgreich, einschließlich Vorlagenaktionen im Dialog, Importvorschau und Abbrechen, Übertragung auf leere Benutzerdaten, DXF-Prüfung, Konfliktregeln und simuliertem Schreibfehler mit Wiederherstellung. Tests verwenden API-Doubles. Benutzerbestätigung vom 26.09.2026: Vorlagen funktionieren in Fusion. Prüfung der Datensicherung einschließlich Export, Import und Konfliktregeln offen.

Ergänzende Prüffälle (nicht einzeln vom Benutzer bestätigt): Vorlage mit unterschiedlichen Gruppenprofilen und gemischtem Zubehör speichern/laden; beim Bearbeiten eines bestehenden Gestells übernehmen; JSON exportieren und auf einer leeren Benutzerkonfiguration importieren; alle drei Konfliktregeln und Abbrechen prüfen.
