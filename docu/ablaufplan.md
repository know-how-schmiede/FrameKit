# FrameKit – Ablaufplan für die weitere Umsetzung

Stand: **26.09.2026** · Aktuelle Add-in-Version: **0.5.4**

**Status: S02 / 0.2.0, S03 / 0.2.1 und S04 / 0.3.0 sind laut Benutzerprüfung vom 26.09.2026 in Fusion bestätigt. Auch S05 / 0.3.1 funktioniert laut Benutzerrückmeldung vom 26.09.2026. S06 / 0.4.0 läuft laut Benutzerprüfung vom 26.09.2026 ohne Fehler. Die Dialogverbesserungen sind als 0.4.1 implementiert; Fusion-Prüfung offen. S07 / 0.4.2 ist mit vereinfachten Winkelkörpern implementiert; Fusion-Prüfung offen. Die STEP-Erweiterung 0.4.3 funktioniert laut Benutzerrückmeldung vom 26.09.2026 in Fusion (108 lokale Tests zuvor erfolgreich). Die Eingabekorrektur 0.4.4 wurde am 26.09.2026 vom Benutzer in Fusion als behoben bestätigt (110 lokale Tests zuvor erfolgreich). S08 / 0.5.0 ist implementiert; der Benutzer meldete einen leeren Bearbeitungsdialog. Der Dialogaufbau aus 0.5.1 wurde vom Benutzer bestätigt. Die Vorschaukorrektur 0.5.2 blieb beim Benutzer wirkungslos. Auch 0.5.3 zeigte eine statische Vorschau. Die Korrektur 0.5.4 erzeugt alle Editorfelder vorab und trennt Grafikaktualisierung von Originalsichtbarkeit (133 lokale Tests); Fusion-Prüfung einschließlich Rückgängig offen. Weitere Schritte nur auf Benutzerauftrag starten.**

## Verwendung dieses Plans

- Diese Datei legt die Reihenfolge, Versionsnummern und den Umfang der weiteren Umsetzung fest. Der Benutzer kann Aufgaben verschieben, ergänzen, streichen oder Versionen ändern.
- Vor jeder weiteren Umsetzung die aktuelle Fassung dieser Datei lesen. Bei Abweichungen gelten der jüngste Benutzerauftrag und anschließend dieser Ablaufplan; der [Projektplan](projektplan_FrameKit.md) liefert die fachlichen Details.
- Die Schritt-IDs bleiben beim Umnummerieren erhalten. Abhängigkeiten beziehen sich auf diese IDs, nicht auf die vorgeschlagene Versionsnummer.
- Nach der Benutzerprüfung nur die beauftragten Schritte umsetzen. Ein Planeintrag allein ist kein Auftrag, alle Versionen automatisch abzuarbeiten.
- Jede neue Funktion erhält die hier zugeordnete Version. Zusammengehörende Aufgaben werden gemeinsam umgesetzt, getestet und dokumentiert.
- Je fertiggestellter Version `version.py`, Manifest und aktuelle Dokumentation abgleichen; in der [Timeline](timeline.md) nur Git-Zusammenfassung, wenige Änderungspunkte, Prüfstand und Detailverweise ergänzen.
- Status je Schritt pflegen: **Geplant → In Arbeit → Implementiert → In Fusion bestätigt**. Lokale Tests und Benutzerprüfung in Fusion getrennt ausweisen. Technische Einzelheiten gehören in eigene Dokumente unter `docu`.

## Bestätigte Ausgangsbasis

Version **0.1.4** funktioniert laut Benutzerrückmeldung. Vorhanden sind:

- Fusion-Integration unter **Volumenkörper → Erstellen**, drei Dialogreiter, Icons und Info-Bereich.
- Gestell aus rechteckigen Demo-Profilen mit optionalem unteren Rahmen und automatischem Zoom.
- Zwischenböden mit festen oder automatisch verteilten Höhen.
- Aufliegende Platten auf allen Rahmenebenen mit Eckausklinkungen für die Pfosten.
- Vier gleiche Fuß-/Rollenplatzhalter; eigene Definitionen speichern, auflisten und löschen.
- Gespeicherte Standardwerte, Bibliotheksdatei, Konfigurationsattribute an der Baugruppe und 19 lokale Tests.

Festgelegte Maßbezüge bleiben erhalten: Länge/Breite sind Rahmenaußenmaße; Gesamthöhe und Bodenoberkanten beziehen sich auf die Aufstandsfläche einschließlich Zubehör und oberer Platte. Aufliegende Platten sind die gewählte Grundvariante. Eine statische Tragfähigkeitsberechnung gehört nicht zum geplanten Funktionsumfang.

## Versionsübersicht

Die Versionsnummern sind Vorschläge und dürfen vor der Umsetzung geändert werden.

| Schritt | Zielversion | Zusammengehöriger Funktionsumfang | Voraussetzung | Status |
| --- | --- | --- | --- | --- |
| S01 | 0.1.5 | Bauteildaten, stabile IDs und strukturierte Baugruppe | 0.1.4 | Implementiert |
| S02 | 0.2.0 | Mittellinien-Vorschau und dauerhafte Layoutskizze | S01 | In Fusion bestätigt |
| S03 | 0.2.1 | Querträger je Ebene und Deckplattenmontage | S01, S02 | In Fusion bestätigt |
| S04 | 0.3.0 | Profilbibliothek, DXF-Import und echte Nutprofile | S01, S02 | In Fusion bestätigt |
| S05 | 0.3.1 | Unterschiedliche Profile und Ausrichtungen | S03, S04 | In Fusion bestätigt |
| S06 | 0.4.0 | Bauart, gemischte Füße/Rollen und Zubehörverwaltung | S01, S02 | In Fusion bestätigt |
| Z01 | 0.4.1 | Farbige Hinweise und Vorschau im Ansichtsbereich einpassen | S06 | Implementiert |
| S07 | 0.4.2 | Vereinfachte Winkelkörper und Montageraum | S04, S05, S06 | Implementiert |
| S07a | 0.4.3 | Gelieferte STEP-Winkel, gemeinsame Komponenten und Montageflächen | S07 | In Fusion bestätigt |
| Z02 | 0.4.4 | Cursorversatz bei Zahlen-/Texteingabe korrigieren | S07a | In Fusion bestätigt |
| S08 | 0.5.0 | Vorhandenes Gestell bearbeiten und neu aufbauen | S01–S07 | Implementiert |
| Z03 | 0.5.1 | Leeren Bearbeitungsdialog beim Laden korrigieren | S08 | In Fusion bestätigt |
| Z04 | 0.5.4 | Editorfelder vorab erzeugen und Vorschau live aktualisieren | Z03 | Implementiert; Fusion-Prüfung offen |
| S09 | 0.7.0 | Zuschnittliste als CSV | S04, S05, S08 | Geplant |
| S10 | 0.7.2 | Vollständige Stückliste als CSV | S06, S07, S09 | Geplant |
| S11 | 0.8.0 | Benannte Vorlagen und Datensicherung | S08 | Geplant |
| S12 | 0.9.0 | Installierbares Paket und durchgängiger Abnahmetest | S01–S11 | Geplant |
| S13 | 1.0.0 | Freigabe des geprüften Grundumfangs | S12 | Geplant |

## Schritte und Optionen

### S01 · 0.1.5 – Bauteildaten und Baugruppenstruktur

**Ergebnis:** [Bauteildaten und Baugruppenstruktur](bauteildaten.md). 28 lokale Tests einschließlich Modell- und API-Adaptertests erfolgreich; Fusion-Abnahme offen. Die Bearbeitung bestehender Gestelle im Dialog folgt erst in S08.

- Gemeinsame berechnete Bauteildaten für Geometrie, Vorschau und spätere Exporte einführen: ID, Funktion, Profilreferenz, Position, Orientierung und Zuschnittlänge.
- Komponenten nach Pfosten, oberem/unterem Rahmen, Bodenebenen, Zubehör und Verbindungen gruppieren. Anzeigenamen verständlich halten; Eigenschaften separat speichern.
- IDs bei Änderungen bestehender Bauteile erhalten und die zusammengehörigen Erzeugungsschritte in der Fusion-Zeitleiste benennen und gruppieren.
- **Prüfung:** Mehrere Gestelle im selben Dokument bleiben getrennt; Eigenschaften und Geometrie stimmen überein. Die bisherige Demo-Geometrie bleibt maßhaltig.

### S02 · 0.2.0 – Vorschau und Layout

**Ergebnis:** [Vorschau und Layout](vorschau_layout.md). 40 lokale Tests einschließlich Grafik- und Dialogereignissen erfolgreich; in Fusion am 26.09.2026 durch den Benutzer bestätigt.

- „Vorschau anzeigen“ mit räumlichen Profilmittellinien ergänzen. Endpunkte entsprechen den tatsächlichen Schnittflächen; vorne/hinten/links/rechts eindeutig festlegen.
- **Optionen:** Bodenflächen und Zubehörumrisse in der Vorschau ein-/ausblenden.
- Nach Erstellung eine fixierte Layoutskizze erhalten und standardmäßig ausblenden. Dialogwerte bleiben maßgeblich; Skizzenänderungen sind keine Eingaben.
- **Prüfung:** Vorschau und Baugruppe stimmen überein. Änderungen aktualisieren die Vorschau; Abbrechen und Fehler hinterlassen keine temporären Objekte.

### S03 · 0.2.1 – Querträger

**Ergebnis:** [Querträger und Deckplattenmontage](quertraeger_deckplatte.md). 46 lokale Tests erfolgreich; in Fusion am 26.09.2026 durch den Benutzer bestätigt.

- Ergänzung: Deckplatte wahlweise mit Aussparungen oder auf den Profilen ohne Aussparungen; Pfostenlänge berücksichtigt Plattenstärke bei unveränderter Gesamthöhe.

- Querträger pro vorhandener Rahmen-/Bodenebene aktivieren und Anzahl sowie Richtung längs/quer einstellen.
- „Für alle Ebenen übernehmen“ ergänzen; anschließend einzelne Ebenen abweichend konfigurieren können.
- Freie Felder unter Berücksichtigung der Trägerbreite gleichmäßig verteilen. Querträger schließen oben bündig mit dem zugehörigen Rahmen ab und tragen die aufliegende Platte.
- Zunächst das vorhandene Rahmenprofil verwenden; eine gesonderte Profilwahl folgt in S05.
- **Prüfung:** Beide Richtungen, null/mehrere Träger, enge Abmessungen und Kombinationen mit Platten und Pfosten prüfen.

### S04 · 0.3.0 – Profilbibliothek und DXF

**Ergebnis:** [Profilbibliothek und DXF-Import](profilbibliothek_dxf.md). 68 lokale Tests erfolgreich. Import für quadratische Querschnitte umgesetzt; In Fusion am 26.09.2026 durch den Benutzer bestätigt; reales Hersteller-Referenzprofil weiterhin offen. Synthetische Testgeometrie ist ausdrücklich kein Herstellerprofil.

- Ein vom Benutzer festgelegtes Referenzprofil mit realem Nutquerschnitt integrieren und durch Extrusion erzeugen; Hohlräume erhalten.
- „Profil hinzufügen“ mit DXF-Dateiauswahl, Importprüfung und Metadaten umsetzen: Hersteller, Serie, Artikelnummer, Nutgröße, Außenmaße, Einheit, Bezugspunkt, Ausrichtung und Material.
- Bestätigter Bibliotheksablauf: lokale DXF auswählen, prüfen und mit Profilnamen sowie eindeutiger ID in den persönlichen FrameKit-Datenordner kopieren (außerhalb des Installationsverzeichnisses). Auswahl beim Erstellen über die Profilliste; Löschen entfernt Eintrag und Bibliothekskopie, nicht die Originaldatei oder bereits erzeugte Gestelle.
- Importvoraussetzung: Querschnitt in der XY-Ebene, Mittelpunkt der äußeren Profilabmessungen im Ursprung (0, 0); gemeint ist die Mitte der äußeren Begrenzung, nicht der Materialschwerpunkt. Zentrierung beim Import mit numerischer Toleranz prüfen und bei Abweichungen eine verständliche Fehlermeldung anzeigen. Extrusion entlang der lokalen Z-Achse.
- Bibliothekseinträge auswählen, auflisten und entfernen; verwendete Profildefinitionen im Projekt nachvollziehbar sichern. Fehlende oder geänderte externe Dateien dürfen gespeicherte Gestelle nicht stillschweigend verändern.
- **Vorher festlegen:** Hersteller, Serie, erstes Profil und geeignete DXF-Referenzdatei. Keine Maße oder Produktdaten erfinden.
- **Prüfung:** Referenzprofil sowie fehlerhafte Skalierung, offene Konturen und Hohlprofile testen. Fehlermeldungen müssen die Ursache nennen.

### S05 · 0.3.1 – Profile je Bauteilgruppe

**Ergebnis:** [Profile je Bauteilgruppe](profile_je_bauteilgruppe.md). 82 lokale Tests erfolgreich; getrennte Profilwahl, rechteckige Querschnitte, Vierteldrehungen und Ebenenübernahme umgesetzt. Version 0.3.1 am 26.09.2026 durch den Benutzer als funktionsfähig bestätigt.

- Gemeinsames Profil als Standard sowie getrennte Profilwahl für Pfosten, Rahmen und Querträger anbieten.
- Nichtquadratische Querschnitte und deren Orientierung in Länge, Breite, Höhenberechnung und Zuschnitten berücksichtigen.
- Eckausklinkungen, Plattenauflage und Querträgerpositionen an tatsächliche Pfosten-/Trägermaße anpassen. Höhenunterschiede an Auflagen erkennen.
- **Optionen:** Eigene Querträgerprofile je Ebene und Übernahme auf alle Ebenen.
- **Prüfung:** Mindestens zwei unterschiedliche Querschnitte kombinieren; Außenmaße, Aussparungen und bündige Auflagen prüfen.

### S06 · 0.4.0 – Bauart und Zubehöranordnung

**Ergebnis:** [Bauart und Zubehöranordnung](bauart_zubehoer.md). 90 lokale Tests erfolgreich; Bauartvorbelegung, Eckauswahl, Zubehör bearbeiten/duplizieren, Eigenschaften und Höhenprüfung umgesetzt. Alle Dialoggruppen starten geschlossen. Version 0.4.0 am 26.09.2026 durch den Benutzer als fehlerfrei bestätigt.

**Referenzentscheidung:** Kein Herstellerprodukt benannt; absenkbare Rollen vorerst als frei definierbare Platzhalter mit erforderlichem Referenztyp und Betriebsstellung. Eingestellte Bauhöhe inklusive Befestigung, Verstellbereich nur zur Prüfung; kein automatischer Ausgleich.

- Bauart **Untergestell / Transportwagen** mit passenden vorbelegten Einstellungen ergänzen.
- Zubehör einzeln pro Ecke oder gemeinsam auswählen, insbesondere zwei Lenkrollen und zwei Bockrollen. Bibliothekseinträge zusätzlich bearbeiten und duplizieren können.
- Eigenschaften für Bremse, Höhenverstellung, Montageposition und Befestigung ergänzen; einfache Platzhalter bleiben zulässig und gekennzeichnet.
- Unterschiedliche Bauhöhen erkennen. Ohne definierte Ausgleichsregel keine schief stehende Baugruppe erzeugen.
- **Vorher festlegen:** Referenztyp und Betriebsstellung absenkbarer Rollen; Bedeutung und Grenzen von Höhenverstellungen.
- **Prüfung:** Gemischte Rollen, gleiche Aufstandsebene, geänderte Bibliothekseinträge und unveränderte bestehende Gestelle prüfen.

### Z01 · 0.4.1 – Dialoghinweise und Vorschau

**Ergebnis:** [Dialoghinweise und Vorschau](dialoghinweise_vorschau.md). 95 lokale Tests erfolgreich; farbige Fehler-/Warnhinweise und einmaliges Einpassen des Gestells beim Einschalten der Vorschau. Fusion-Prüfung offen. Die Verbindungen folgen separat in S07 / 0.4.2.

### S07 · 0.4.2 – Verbindungen

**Ergebnis nach erweitertem Benutzerauftrag:** [Vereinfachte Winkel](winkel.md). 101 lokale Tests erfolgreich. Dreieckkörper 20/30/40, optionale parallele Anordnung bei doppelter gemeinsamer Montagehöhe, Kollisionsprüfung und gemeinsame Gruppe „91 | Winkel (vereinfacht)“. Vereinfachte Körper sind jetzt ausdrücklich beauftragt; reale Schrauben-/Mutternregeln bleiben offen. Fusion-Prüfung von 0.4.2 steht aus.

**Vorgemerkt nach Benutzerangabe vom 26.09.2026:** Dreieckiger Winkel 20 × 20 für Profil 20 × 20, Winkel 30 × 30 für Profil 30 × 30 und Winkel 40 × 40 für Profil 40 × 40. Bei breiteren Profilen, beispielsweise 40 × 80, kommen gegebenenfalls zwei parallel verschraubte Winkel zum Einsatz; daraus noch keine pauschale Doppelwinkelregel ableiten. Laut Benutzer gibt es keine unterschiedlichen Winkelausführungen für verschiedene Nutbreiten. Die Auswahl von Schrauben und Muttern bleibt davon getrennt zu prüfen.

**Noch festzulegen:** genaue Winkelgeometrie (unter anderem Breite, Wandstärke und Bohrungen), Montagepositionen/Abstände, Regel für einen oder zwei Winkel sowie Schrauben-/Mutternmengen. Die genannten Außenmaße allein legen diese Angaben nicht fest. Für die ausdrücklich beauftragten einfachen Körper werden diese Herstellerdetails noch nicht modelliert. Darstellungsdicke 4 mm; keine reale Wandstärke zugesichert.

- Konkrete Montagewinkel/Verbindungssätze mit Profilkompatibilität und Mengenregeln hinterlegen.
- Verbindungssatz auswählen, vereinfachte Verbindungsteile platzieren und deren Platzbedarf gegenüber Platten, Querträgern und Zubehör prüfen.
- Fehlende Zuordnungen sichtbar kennzeichnen; keine vollständige Verschraubung oder Stückliste behaupten, solange Regeln fehlen.
- **Vorher festlegen:** Mindestens ein zum Referenzprofil passender Verbindungssatz, Montageabstände und Schrauben-/Mutternmengen.
- **Prüfung:** Platzierung und Mengen für Pfosten, Rahmen und Querträger anhand eines Referenzgestells nachvollziehen.

### S08 · 0.5.0 – Gestell bearbeiten

**Ergebnis:** [Gestell bearbeiten](gestell_bearbeiten.md). Eigener Auswahl-/Ladebefehl, gespeicherte Profil- und Zubehörstände, Vorschau in Baugruppenlage und Neuaufbau mit ID-Erhaltung. Fremde Unterkomponenten sowie verknüpfte/mehrfach verwendete Gestelle werden zum Schutz abgelehnt. 126 lokale Tests erfolgreich; native Fusion-Prüfung von Austausch, Abbrechen und Rückgängig offen.

- Vorhandene FrameKit-Baugruppe auswählen und gespeicherte Konfiguration einschließlich Bibliotheksreferenzen in den Dialog laden.
- Änderungen zunächst in der Vorschau prüfen, anschließend kontrolliert neu aufbauen. Bestehende IDs soweit fachlich möglich erhalten.
- Konfigurationsschema versionieren, bisherige Demo-Konfigurationen übernehmen oder bei nicht unterstützten Altständen verständlich informieren.
- **Verhalten:** Manuelle Änderungen an generierten Bauteilen werden beim Neuaufbau ersetzt. Fremde Komponenten bleiben unangetastet; externe Flächenreferenzen sind nicht zugesichert.
- **Prüfung:** Abbrechen, Fehler beim Neuaufbau, Rückgängig und mehrere Gestelle testen. Bei einem Fehler muss das bisherige Gestell erhalten bleiben.

### S09 · 0.7.0 – Zuschnittliste

- CSV-Export für das ausgewählte Gestell anbieten. Gleiche Profildefinitionen, Längen und Endbearbeitungen zusammenfassen.
- Hersteller, Serie, Artikelnummer, Bezeichnung, Länge in Millimetern, Menge und Bauteil-IDs aus Eigenschaften exportieren, nicht aus Anzeigenamen ableiten.
- **Optionen:** Zielpfad und verständliche CSV-Einstellungen für die vorgesehene Tabellenverarbeitung.
- **Prüfung:** Export nach Erstellung und Bearbeitung mit der Baugruppe abgleichen; gleiche Anzeigenamen verschiedener Profile nicht vermischen.

### S10 · 0.7.2 – Stückliste

- CSV-Stückliste um Platten, Füße/Rollen und definierte Verbindungsteile erweitern.
- Plattenmaße, Stärke und Eckausklinkungen sowie Zubehördefinitionen und Mengen ausweisen. Platzhalter und unvollständige Verbindungszuordnungen kennzeichnen.
- **Optionen:** Stückliste, Zuschnittliste oder beide Listen exportieren.
- **Prüfung:** Mengen am Referenzgestell nachzählen und nach Änderungen erneut vergleichen. Fehlende Montagevorgaben dürfen nicht als vollständige Stückliste erscheinen.

### S11 · 0.8.0 – Vorlagen und Sicherung

- Mehrere benannte Gestellvorlagen speichern, laden, umbenennen und löschen; die vorhandenen persönlichen Standardwerte beibehalten.
- Vorlagen und eigene Bibliotheken exportieren/importieren, einschließlich benötigter Profildateien.
- **Optionen:** Bei gleichen Namen/IDs überspringen, als Kopie übernehmen oder gezielt ersetzen; vor dem Import verständlich anzeigen.
- **Prüfung:** Übertragung auf eine leere Benutzerkonfiguration, beschädigte Dateien, ID-Konflikte und Abbrechen ohne Datenverlust testen.

### S12 · 0.9.0 – Installation und Abnahme

- Vollständiges Add-in-Paket mit Manifest, Bibliotheken und Ressourcen erstellen; reproduzierbare Paketprüfung ergänzen.
- Installations-, Update-, Deinstallations- und Datensicherungsanleitung sowie Beispieldateien bereitstellen. Updates dürfen Benutzerdaten nicht überschreiben.
- **Vorher festlegen:** Unterstützte Fusion-Versionen, tatsächlich zu prüfende Betriebssysteme und ZIP-Paket oder zusätzlicher Installer.
- **Prüfung:** Alle Fälle aus dem Projektplan in Fusion durchgehen, einschließlich eigener DXF-Datei, gemischter Rollen, Bearbeitung und Exporte. Ergebnisse mit Umgebung und Datum dokumentieren.

### S13 · 1.0.0 – Freigabe

- Offene Fehler aus der Abnahme beheben, Dokumentation und Beispiele abschließen; keine zusätzlichen Funktionen in diesen Schritt aufnehmen.
- Versionsstand und Paketinhalt prüfen; kurze Release-Beschreibung aus dem tatsächlich geprüften Umfang erstellen.
- **Abschluss:** Grundumfang ist in Fusion bestätigt. Eine Veröffentlichung oder ein Git-Push erfolgt nur im Rahmen eines entsprechenden Benutzerauftrags.

## Optionale Ausbauschritte nach dem Grundumfang

Diese Schritte sind Vorschläge, noch nicht zur Umsetzung beauftragt. Jeder erhält bei Aufnahme in die Umsetzung seine eigene Version; Anforderungen und Prüfung werden dann ergänzt.

| Schritt | Vorschlag | Funktion und zusammengehörige Optionen | Voraussetzung |
| --- | --- | --- | --- |
| O01 | 1.1.0 | Querträgeranzahl aus maximaler freier Spannweite berechnen; manuelle Anzahl weiterhin möglich | S03, S05 |
| O02 | 1.2.0 | Individuelle Querträgerpositionen statt gleichmäßiger Verteilung; Abstände und Kollisionen prüfen | S03, S05 |
| O03 | 1.3.0 | Griffbügel mit Position, Abmessungen und passender Befestigung | S07, S10 |
| O04 | 1.4.0 | Diagonalstreben mit Ausrichtung, Zuschnitt und Verbindungsteilen | S07, S09, S10 |
| O05 | 1.5.0 | Weitere Rahmenformen und zusätzliche Pfosten; Ebenen, Platten und Verbindungen anpassen | S05, S07, S08 |
| O06 | 1.6.0 | Detaillierte Herstellergeometrie für Zubehör; zwischen Platzhalter und Detailmodell umschalten | S06 |
| O07 | 1.7.0 | SVG als weiteres Profilimportformat mit denselben Importprüfungen wie DXF | S04 |
| O08 | 1.8.0 | Zuschnittoptimierung für Lagerstangen einschließlich Schnittfuge, Reststücken und Ergebnisexport | S09 |

## Notizen des Benutzers

Hier können Änderungen vor der Umsetzung eingetragen werden. Verbindliche Änderungen anschließend auch in der Versionsübersicht und im jeweiligen Schritt nachführen.

- Für den nächsten Umsetzungsschritt vorgemerkt: Das Icon für „Gestell bearbeiten“ behält das bestehende Grundicon und erhält zusätzlich ein Bearbeiten-Symbol (z. B. einen Stift), damit es von „Gestell erstellen“ unterscheidbar ist. Noch nicht umgesetzt.
- Gewünschte Änderungen an Reihenfolge oder Versionsnummern:
- Für den nächsten Umsetzungsschritt (Benutzerhinweis mit Screenshot von 0.4.2): Den statischen Hinweis „Zylinderplatzhalter unter den Pfosten …“ direkt unter der Auswahl in „Füße / Rollen je Ecke“ entfernen (`support_help`). An genau dieser Stelle stattdessen die zugehörige farbige Fehlermeldung anzeigen, beispielsweise bei unterschiedlichen Bauhöhen. Nach Korrektur die Meldung entfernen; den Zubehörfehler nicht ausschließlich am unteren Dialogende anzeigen. In 0.4.3 umgesetzt: statischer Text entfernt, rote Zubehörmeldung direkt unter der Auswahl; nach Korrektur ausgeblendet.
- Vorschaupräzisierung: Nur das Gestell vollständig im Ansichtsbereich anzeigen, kein Fusion-Vollbildmodus. In 0.4.1 umgesetzt; Fusion-Prüfung offen.
- Farbige Fehler-/Warnhinweise in allen Dialogbereichen: In 0.4.1 umgesetzt; Darstellung in hellem und dunklem Theme noch in Fusion prüfen.
- Winkelzuordnungen und optionale parallele Winkel als einfache Körper in gemeinsamer ein-/ausblendbarer Gruppe umgesetzt: siehe S07 / 0.4.2.
- Referenzprofil / DXF-Datei:
- Verbindungssatz / Rollenreferenz:
- Bevorzugte Installation und Zielplattformen:

[Deutsche README](../README.md) · [English README](../README.en.md) · [Projektplan](projektplan_FrameKit.md) · [Timeline](timeline.md)

### Ergänzung S07a · 0.4.3 – STEP-Winkel

Benutzerdateien aus `profiles/winkel` integriert, je Größe gemeinsame Komponente mit individuellen Vorkommen. Montage an Außenflächen, volle Winkelbreite und kollisionsfreie Doppelanordnung berücksichtigt. Paketdateien enthalten; Import einmal beim Add-in-Start. Version 0.4.3 am 26.09.2026 durch den Benutzer als funktionsfähig bestätigt. Details: [Winkel](winkel.md). S08 wird damit nicht vorgezogen.

### Z02 · 0.4.4 – Eingabe ohne unnötige Dialogaktualisierung

Benutzer meldet `600` → `006` beim Tippen. Der Handler schrieb bei jedem Tastendruck Sichtbarkeit, Aktivierung und Status erneut. Unveränderte Eigenschaften werden jetzt übersprungen; Sichtbarkeit der Ebenen wird nur bei Strukturänderungen angepasst. validateInputs prüft ohne UI-Schreibzugriffe, verschachtelte inputChanged-Aufrufe werden abgefangen. 110 lokale Tests einschließlich Schreibzugriffsprüfung beim Tippen erfolgreich. Der Benutzer hat am 26.09.2026 bestätigt: Eingabefehler in 0.4.4 beseitigt.

**Benutzerrückmeldung zu 0.4.4:** Nach Neustart läuft es wieder. Der beigefügte Fusion-Hinweis meldet einen fehlgeschlagenen vorherigen Add-in-Start und das anschließende Überspringen von FrameKit. Startursache ungeklärt. In einer späteren Rückmeldung vom 26.09.2026 wurde der Eingabefehler ausdrücklich als beseitigt bestätigt.

### Z03 · 0.5.1 – Bearbeitungsdialog sichtbar halten

Nach Benutzerbericht eines leeren Dialogs: Reiter einmalig in commandCreated anlegen, Auswahl innerhalb des ersten Reiters anzeigen, beim Laden den gehaltenen Command statt alter Ereignisargumente verwenden. Auswahl erst nach vollständigem Aufbau ausblenden. Aufbaufehler sichtbar melden und Ausführung sperren. 128 lokale Tests erfolgreich; Bestätigung im laufenden Fusion offen.

### Z04 · 0.5.2 – Fehlende Vorschau

Benutzer bestätigt den Dialogaufbau, meldet aber trotz eingeschalteter Vorschau keine Grafik. Im gelesenen aktuellen Fusion-Protokoll kein FrameKit-Vorschau-Traceback gefunden; native Ursache damit nicht eindeutig belegt. Vorschau wird jetzt nach gültigen Eingabeänderungen explizit über doExecutePreview angefordert. Text-/Gruppen-/Reiterereignisse sowie Rückrufe während des Renderns löschen keine Vorschau mehr. Fehlgeschlagene Vorschauanforderungen werden angezeigt. 131 lokale Tests erfolgreich; praktische Bestätigung offen.

**Nachkorrektur Z04 / 0.5.3:** 0.5.2 behebt die Vorschau laut Benutzer nicht. Alle nativen Handler werden nun in commandCreated gebunden und delegieren an die nachgeladenen Editor-Callbacks. 132 lokale Tests erfolgreich; reale Fusion-Bestätigung offen.

**Nachkorrektur Z04 / 0.5.4:** Benutzer sieht die statische Vorschau erst nach manuellem Ausblenden des Originals. Alle Editorfelder werden nun beim Öffnen erzeugt und beim Laden nur befüllt; Grafikaktualisierung und Originalsichtbarkeit sind getrennt. 133 lokale Tests erfolgreich; Fusion-Bestätigung offen.
