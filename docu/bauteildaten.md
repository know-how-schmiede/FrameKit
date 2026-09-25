# Bauteildaten und Baugruppenstruktur – ab 0.1.5

Dieses Dokument beschreibt **S01** aus dem [Ablaufplan](ablaufplan.md). Seit S02 / 0.2.0 verwenden auch [Vorschau und Layout](vorschau_layout.md) diese Bauteildaten. Seit S04 / 0.3.0 werden echte DXF-Profilquerschnitte unterstützt; die Bearbeitung vorhandener Gestelle folgt in S08.

## Berechnung und Geometrie

[`model.py`](../fusion_addin/FrameKit/model.py) berechnet ein vollständiges, als JSON speicherbares Gestellmodell. Die Fusion-Geometrie liest ausschließlich diese Bauteildaten. Die bisherigen Funktionen `members`, `panels` und `supports` liefern kompatible Ansichten desselben Modells; sie enthalten keine zweite Geometrieberechnung.

Alle Maße werden in **Millimetern** gespeichert. Erst bei der Übergabe an Fusion erfolgt die Umrechnung in Zentimeter. Profile werden entlang ihrer Längsachse extrudiert; Position und Orientierung platzieren den Querschnitt im Gestell. Auch ein Träger, dessen Zuschnitt kürzer als die Profilbreite ist, behält die richtige Achse.

| Feld | Bedeutung |
| --- | --- |
| `assembly_id` | Eindeutige Kennung des Gestells |
| `id_registry` | Dauerhafte Zuordnung von Bauteilrollen zu lokalen IDs |
| `configuration` | Kopie der verwendeten Dialogwerte und Zubehördefinition |
| `groups` | Unterbaugruppen mit sprachunabhängigen Gruppenkennungen |
| `profiles` | Verwendete Demo-Vollprofile oder eigenständige DXF-Profildefinitionen einschließlich Konturen und Metadaten |
| `parts` | Berechnete Profile, Platten und Zubehörplatzhalter |

Jedes Bauteil enthält ID, eindeutige Gesamtkennung, Rolle, Funktion, Gruppe, Lage, Orientierung, Abmessungen und Geometriebeschreibung. Bei Profilen kommen Profilreferenz, Zuschnittlänge und Mittellinien-Endpunkte an den Schnittflächen hinzu. Platten speichern ihre ausgeklinkte Kontur; Zubehörteile speichern die verwendete Definition. Vorschau und Layout verwenden dieselben Mittellinien.

`position_mm` bezeichnet den lokalen Geometrieursprung relativ zur Hauptbaugruppe. `orientation` enthält die lokalen X-, Y- und Z-Achsen als Richtungsvektoren im Gestellkoordinatensystem; Z ist die Extrusionsrichtung. `bounds_mm` beschreibt die achsparallelen Ausdehnungen im Gestell. Die Geometriebeschreibung enthält lokale Querschnittsdaten und Extrusionstiefe. Bei DXF-Profilen liegt `position_mm` im Querschnittsmittelpunkt an der ersten Schnittfläche; die exakten Konturen stehen unter `profiles[profile_ref]`, der Geometrietyp ist `dxf`. Demo-Profile behalten ihren bisherigen Ursprung an der unteren Querschnittsecke. Details: [Profilbibliothek und DXF-Import](profilbibliothek_dxf.md).

## Stabile IDs

- Jedes neu erzeugte Gestell erhält eine eigene UUID. Lokale Bauteilnummern wie `P001` dürfen in unterschiedlichen Gestellen vorkommen; `assembly_id/P001` ist die eindeutige Gesamtkennung.
- Sprachunabhängige Schlüssel wie `post:front:left`, `top:beam:front` oder `shelf:01:panel` bezeichnen die Funktion im Gestell. IDs hängen weder vom Anzeigenamen noch von Maßen oder Bibliotheksnamen ab.
- `build_model(values, previous=last_model)` behält die Gestellkennung und bestehende ID-Zuordnungen bei einer Neuberechnung. Neue Rollen erhalten neue Nummern; vorübergehend entfallene Rollen bleiben in der Zuordnung reserviert.
- Bodenrollen werden von unten nach oben nummeriert. Eine Änderung der Anzahl ergänzt oder entfernt obere Ebenen. Individuelles Löschen oder Einfügen einer mittleren Ebene ist noch keine unterstützte Bearbeitungsfunktion.
- Der vorhandene Befehl erstellt weiterhin eine **neue** Baugruppe. Das erneute Laden und Bearbeiten einer ausgewählten Baugruppe folgt in **S08 / 0.5.0**. Die ID-Erhaltung bei Neuberechnung ist dafür vorbereitet und lokal getestet.

## Fusion-Browser und Eigenschaften

Die Hauptbaugruppe heißt beispielsweise `FrameKit 0.1.5 | a1b2c3d4`. Darunter liegen:

- `01 | Pfosten`
- `02 | Rahmen oben`, einschließlich oberer Platte
- `03 | Rahmen unten`, einschließlich unterer Platte, sofern aktiviert
- `04 | Boden 01`, danach weitere Ebenen von unten nach oben, jeweils mit Trägern und Platte
- `90 | Füße und Rollen`, sofern ausgewählt
- `91 | Verbindungen`, vorerst leer und als reserviert gekennzeichnet

Seit S02 / 0.2.0 kommt `00 | Layout` mit einer fixierten, standardmäßig ausgeblendeten Mittellinienskizze hinzu; siehe [Vorschau und Layout](vorschau_layout.md). Die leere Verbindungsgruppe enthält keine erfundenen Montage- oder Stücklistendaten.

Bauteilnamen enthalten ID, Funktion und passende Abmessungen. Profile zeigen zusätzlich die Profilbezeichnung und Zuschnittlänge. Die native Fusion-Bauteilnummer enthält die lokale ID, die Beschreibung die Bauteilfunktion.

Zusätzlich werden Attribute unter **FrameKit** gespeichert: unter anderem `assemblyId`, `partId`, `partUid`, `partKey`, `kind`, `groupId`, `profileRef`, `positionMm`, `orientation`, `cutLengthMm` und der vollständige Datensatz `partData`. Künftige Exporte sollen diese Eigenschaften verwenden und keine Anzeigenamen zerlegen.

Die Hauptbaugruppe speichert `modelData` einschließlich ID-Zuordnung und Profildaten sowie eine versionierte `configuration`. Das bisherige Attribut `demoConfiguration` bleibt für Kompatibilität erhalten. Modell und Konfiguration beginnen jeweils mit Schemaversion 1; diese Nummern sind von der Add-in-Version unabhängig.

## Fusion-Zeitleiste

In parametrischen Dokumenten erhält jedes Bauteil eine benannte Gruppe mit seinen aufeinanderfolgenden Schritten: Komponentenerstellung, Querschnittsskizze und Extrusion. Die Erstellung der Haupt- und Unterbaugruppen erhält eine separate Strukturgruppe, seit 0.2.0 einschließlich Layoutskizze unter „Struktur und Layout“. Gruppennamen enthalten die kurze Gestellkennung, damit mehrere Gestelle zugeordnet werden können.

Die Gruppen überlappen sich nicht und werden nicht verschachtelt. Sie werden nach der Geometrieerstellung von hinten nach vorne angelegt und anschließend eingeklappt. Vor der Erstellung wird die Zeitleiste ans Ende gesetzt. Bei einem Fehler werden bereits erstellte eigene Gruppen und die neue Baugruppe bereinigt; der Befehl meldet die Ausführung als fehlgeschlagen.

In einem **direkten Modellierungsdokument** werden dieselben Komponenten und Eigenschaften erzeugt, aber keine Zeitleistengruppen. Der Dokumenttyp wird nicht automatisch geändert. `timelineMode` dokumentiert den verwendeten Modus.

## Prüfung

28 lokale Tests erfolgreich: bisherige Geometrie- und Bibliothekstests sowie zusätzliche Tests für ID-Erhaltung, JSON-Speicherung, Profilorientierung, Schnittflächen-Endpunkte, Gruppenzuordnung und getrennte Gestellkennungen. Ein vereinfachter Fusion-API-Ersatz prüft außerdem die Übergabe der Transformationen und Eigenschaften, nicht überlappende Zeitleistenbereiche, direkten Modus und Aufräumen nach simulierten Fehlern. Diese Tests ersetzen den Fusion-Geometriekern nicht.

**Noch in Fusion prüfen:**

1. Ein Standardgestell und ein Gestell mit Böden und Rollen im selben parametrischen Dokument erzeugen. Browserstruktur und unterschiedliche Gestellkennungen prüfen.
2. Außenmaße, Gesamthöhe, Plattenausklinkungen und Zubehörpositionen mit dem bestätigten Stand 0.1.4 vergleichen. Längs- und Querträger müssen korrekt orientiert sein.
3. Bauteilnummer, Beschreibung und Anzeigenamen prüfen; Profilzuschnitte mit den tatsächlichen Längen vergleichen.
4. Die Zeitleistengruppen öffnen: Pro Bauteil müssen die eigenen Erzeugungsschritte enthalten sein. Fremde Dokumentelemente dürfen nicht in FrameKit-Gruppen landen.
5. Erstellung rückgängig machen und erneut ausführen. Bestehende Gestelle müssen unverändert bleiben.
6. Ein direktes Modellierungsdokument prüfen: gleiche Geometrie und Eigenschaften, unveränderter Dokumenttyp, keine Zeitleistengruppen.

API-Grundlage: [Autodesk: TimelineGroups.add](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_TimelineGroups_add.htm) und [TimelineGroup.deleteMe](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/TimelineGroup_deleteMe.htm).

[Demo-Anleitung](demo_installation.md) · [Ablaufplan](ablaufplan.md) · [Timeline](timeline.md)
