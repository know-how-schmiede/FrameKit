# Projektplan: Fusion-Add-in für Aluprofil-Gestelle und Transportwagen

## Ziel

Die konkrete Reihenfolge und Versionszuordnung der weiteren Umsetzung stehen im [bearbeitbaren Ablaufplan](ablaufplan.md). Vor neuen Umsetzungsschritten dessen aktuellen Stand und die Benutzeränderungen lesen. Dieser Projektplan beschreibt die fachlichen Anforderungen; bereits getroffene Entscheidungen und der bestätigte Implementierungsstand sind im Ablaufplan zusammengefasst.

Ein Fusion-Add-in erzeugt aus Dialogeingaben ein verschraubtes Untergestell oder einen einfachen Transportwagen aus Alu-Nutprofilen. Vor der Bauteilerstellung prüft der Benutzer eine räumliche Mittellinien-Vorschau.

Die erste Version unterstützt gerade Profilzuschnitte, Zwischenböden mit Querträgern sowie Füße und Rollen. Eigene Profilquerschnitte lassen sich ohne Programmänderung ergänzen.

## 1. Konstruktionsregeln festlegen

Als Ausgangskonstruktion gelten:

- Vier durchgehende Eckpfosten.
- Oberer Rahmen zwischen den Pfosten.
- Optionaler unterer Rahmen.
- Zwischenböden mit umlaufendem Tragrahmen.
- Zusätzliche Querträger je Bodenebene, gleichmäßig verteilt.
- Verschraubte Verbindungen über hinterlegte Montagewinkel beziehungsweise Verbindungssätze.

Länge und Breite bezeichnen die Außenmaße des Profilrahmens. Die Gesamthöhe reicht von der Aufstandsfläche bis zur definierten Oberkante des Gestells einschließlich einer gegebenenfalls aufliegenden Deckplatte.

Profilquerschnitte, Plattenstärken, Zubehörbauhöhen und Montageabstände müssen in die Berechnung eingehen. Rollenüberstände gehören nicht zu den Rahmenmaßen.

Vor der Umsetzung festlegen:

- Erstes konkretes Referenzprofil einschließlich Hersteller, Serie und Nutgröße.
- Passender Verbindungssatz und dessen Platzbedarf.
- Aufliegende oder eingelegte Bodenplatten; für Version 1 zunächst eine Variante wählen.
- Maßbezug der Bodenhöhen, vorzugsweise Oberkante der Platte.
- Höhenstellung absenkbarer Rollen und Bedeutung von „absenkbar“ anhand eines Referenzprodukts.

## 2. Add-in-Grundstruktur erstellen

Das Add-in erhält eine modulare Struktur für:

- Fusion-Befehle und Dialog.
- Konfiguration und Speicherung.
- Profil- und Zubehörbibliothek.
- Geometrie- und Zuschnittberechnung.
- Vorschau.
- Bauteilerstellung.
- Zuschnitt- und Stücklistenexport.

Die Berechnungslogik wird von der Fusion-Geometrieerstellung getrennt. Vorschau, Bauteile und Listen verwenden dieselben berechneten Bauteildaten.

Zunächst prüfen, welche Fusion-Version und Entwicklungsumgebung verfügbar sind. Prüfungen innerhalb von Fusion müssen ausdrücklich von Tests außerhalb von Fusion unterschieden werden.

## 3. Erweiterbare Bibliotheken umsetzen

### Profile

DXF dient als erstes Austauschformat für Profilquerschnitte. SVG bleibt eine spätere Erweiterung.

Ein Profil besteht aus einer Querschnittsdatei und Metadaten:

- Eindeutige Bibliotheks-ID.
- Hersteller, Serie, Artikelnummer und Anzeigename.
- Nutgröße und Außenmaße.
- Einheit, Bezugspunkt und Ausrichtung.
- Material.
- Zugeordnete kompatible Verbindungssätze.

„Profil hinzufügen“ führt durch Dateiauswahl, Importprüfung und Metadateneingabe. Maßstab, geschlossene Konturen und Hohlräume werden geprüft. Ungeeignete Dateien werden mit verständlicher Begründung abgelehnt.

Verwendete Profildefinitionen sollen am Projekt nachvollziehbar bleiben, auch wenn sich die externe Bibliothek später ändert.

### Füße, Rollen und Verbindungen

Zubehör erhält eigene Definitionen mit Bauhöhe, Montageposition, Befestigung und vereinfachter Geometrie.

Unterstützte Kategorien:

- Feste und höhenverstellbare Füße.
- Lenkrollen, optional mit Bremse.
- Bockrollen.
- Absenkbare Rollen gemäß festgelegtem Referenztyp.

Vereinfachte Modelle werden als solche gekennzeichnet. Detaillierte Herstellergeometrie ist für den ersten Prototyp nicht erforderlich.

## 4. Einstellungsdialog erstellen

Der Dialog enthält:

- Bauart: Untergestell oder Transportwagen.
- Länge, Breite und Gesamthöhe.
- Gemeinsames Profil sowie optionale abweichende Profile für Pfosten und Träger.
- Optionalen unteren Rahmen.
- Anzahl und Höhen der Zwischenböden.
- Plattenstärke.
- Querträger je Ebene: aktiviert, Anzahl, Richtung und Profil.
- „Für alle Böden übernehmen“.
- Füße beziehungsweise Rollen und deren Anordnung.
- „Vorschau anzeigen“ und „Gestell erstellen“.

Ungültige Eingaben verhindern die Erstellung und zeigen eine konkrete Ursache, etwa eine negative Zuschnittlänge oder eine Bodenebene außerhalb des verfügbaren Raums.

## 5. Berechnung und 3D-Vorschau umsetzen

Für jedes Profil werden stabile ID, Funktion, Querschnitt, Lage, Orientierung und Zuschnittlänge berechnet.

Die Vorschau zeigt:

- Eine räumliche Mittellinie pro Profil.
- Linienenden an den tatsächlichen Schnittflächen.
- Optional vereinfachte Bodenflächen und Zubehörumrisse.
- Die festgelegte Orientierung für vorne, hinten, links und rechts.

Querträger teilen die lichte Öffnung unter Berücksichtigung ihrer eigenen Breiten in gleich große freie Felder. Ihre Oberseiten liegen bündig mit den zugehörigen Rahmenprofilen.

Layoutlinien werden fixiert. Manuelle Skizzenänderungen werden nicht als Eingaben übernommen; der Dialog und die gespeicherte Konfiguration bleiben maßgeblich.

Beim Abbrechen bleiben keine temporären Vorschauobjekte zurück.

## 6. Fusion-Baugruppe erzeugen

Jedes Profil wird als eigene Komponente erstellt. Die Hauptbaugruppe enthält:

- `00 | Layout`
- `01 | Pfosten`
- `02 | Rahmen oben`
- `03 | Rahmen unten`, sofern vorhanden
- Je eine Unterbaugruppe pro Bodenebene
- Unterbaugruppen für Füße beziehungsweise Rollen und Verbindungsteile

Die Layoutskizze heißt:

`Layout | Profilachsen – automatisch erzeugt`

Sie bleibt nach der Erstellung erhalten und wird standardmäßig ausgeblendet.

Ein Bauteilname folgt diesem Muster:

`P001 | Pfosten vorne links | 40x40 Nut 8 | L=850 mm`

Die Bauteil-ID bleibt bei Änderungen eines bestehenden Bauteils stabil. Profil und Länge im Anzeigenamen werden aktualisiert. Böden werden von unten nach oben nummeriert.

Bauteildaten werden zusätzlich als Eigenschaften gespeichert. Listen dürfen nicht vom Zerlegen der Anzeigenamen abhängen.

## 7. Zeitleiste strukturieren

Die zusammenhängenden Erstellungsschritte jedes Bauteils erhalten eine eigene benannte Zeitleistengruppe.

Beispiel:

`P013 | Boden 01 Quertraeger 01`

Darin liegen die zugehörigen Schritte wie Bezugsebene, Profilskizze, Extrusion und gegebenenfalls Bearbeitungen.

Layout und übergreifende Montageschritte erhalten separate Gruppen. Die Umsetzung muss die zeitliche Reihenfolge und Gruppierungsmöglichkeiten von Fusion berücksichtigen.

## 8. Konfiguration speichern und Gestell bearbeiten

Die Hauptbaugruppe speichert eine versionierte Konfiguration einschließlich der verwendeten Bibliotheksreferenzen.

„Gestell bearbeiten“ lädt diese Werte erneut in den Dialog. Nach Vorschau und Bestätigung wird das vom Add-in verwaltete Gestell kontrolliert neu aufgebaut.

Für Version 1 gilt:

- Manuelle Änderungen an generierten Bauteilen werden beim Neuaufbau nicht erhalten.
- Andere, nicht vom Add-in verwaltete Komponenten bleiben unberührt.
- Fehler dürfen keine unvollständige Ersatzbaugruppe hinterlassen.
- Referenzen externer Bauteile auf neu erzeugte Flächen sind keine zugesicherte Funktion.

## 9. Zuschnitt- und Stücklisten erstellen

Export zunächst als CSV.

Die Zuschnittliste gruppiert gleiche Profile nach eindeutiger Profildefinition, Länge und Endbearbeitung. Sie enthält:

- Zuschnittposition.
- Hersteller, Serie und Artikelnummer, soweit hinterlegt.
- Profilbezeichnung.
- Länge in Millimetern.
- Stückzahl.
- Zugehörige Bauteil-IDs.

Die Stückliste enthält zusätzlich Bodenplatten, Füße, Rollen und definierte Verbindungssätze.

Verbindungsteile werden nur vollständig ausgewiesen, wenn konkrete Montage- und Mengenregeln hinterlegt sind. Fehlende Zuordnungen werden sichtbar gekennzeichnet.

## 10. Prüfung und Abnahme

Die Berechnungslogik erhält gezielte Tests für Zuschnittlängen, unterschiedliche Querschnitte, Querträgerverteilung und Höhenberechnung.

In Fusion werden mindestens folgende Fälle geprüft:

- Einfaches Gestell ohne Zwischenboden.
- Gestell mit mehreren Böden und Querträgern.
- Unterschiedliche Profile für Pfosten und Rahmen.
- Transportwagen mit zwei Lenkrollen und zwei Bockrollen.
- Gestell mit Füßen beziehungsweise absenkbaren Rollen.
- Import eines eigenen Hohl- oder Nutprofils.
- Ungültige Eingaben und fehlerhafte Profildateien.
- Abbrechen, erneutes Bearbeiten und mehrere Gestelle im selben Dokument.

Abnahmekriterien:

- Vorschau und erzeugte Baugruppe stimmen überein.
- Außenmaße und Gesamthöhe entsprechen der definierten Maßkonvention.
- Hohlräume der Profilquerschnitte bleiben erhalten.
- Komponenten sind eindeutig benannt und Schritte nachvollziehbar gruppiert.
- Exportierte Mengen und Zuschnittlängen stimmen mit der Baugruppe überein.
- Die gespeicherte Konfiguration lässt sich erneut öffnen.

## Umsetzungsetappen

1. **Grundprototyp:** Ein Referenzprofil, vier Pfosten, oberer Rahmen, Dialog und Mittellinien-Vorschau.
2. **Profilbaugruppe:** DXF-Extrusion, Benennung, Eigenschaften und Zeitleistengruppen.
3. **Böden und Querträger:** Ebenen, Platten und gleichmäßige Abstützung.
4. **Zubehör:** Füße, Rollen und konkrete Verbindungssätze.
5. **Projektbearbeitung und Export:** Konfiguration laden, kontrollierter Neuaufbau, CSV-Listen.
6. **Abnahme:** Fusion-Prüfungen, Beispieldateien sowie Installations- und Bibliotheksanleitung.

## Spätere Erweiterungen

- Querträgeranzahl aus einer vom Benutzer vorgegebenen maximalen freien Spannweite.
- Individuelle Querträgerpositionen.
- Weitere Rahmenformen und zusätzliche Pfosten.
- Griffbügel, Diagonalstreben und detaillierte Herstellerteile.
- Weitere Profilimportformate.
- Zuschnittoptimierung für Lagerstangen.

Eine statische Tragfähigkeitsberechnung ist nicht Bestandteil der ersten Version. Die Querträgerverteilung setzt Benutzervorgaben geometrisch um.
