# FrameKit – Änderungshistorie

Pro Version: kurze Git-Zusammenfassung, Prüfstand und Links. Technische Details und Anleitungen werden in eigenen Dokumenten unter `docu` gepflegt.

## 26.09.2026 – 0.4.4

**Git-Zusammenfassung:** `fix: Unnötige Dialogaktualisierungen beim Tippen vermeiden (0.4.4)`

- Gemeldeten Cursorversatz (`600` → `006`) adressiert: keine wiederholten Schreibzugriffe auf unveränderte Sichtbarkeit, Aktivierung und Hinweistexte.
- Eingabevalidierung ohne UI-Änderungen; Schutz gegen verschachtelte Änderungsereignisse. Zubehörfehler werden direkt auf ihren Zielzustand gesetzt, ohne vorheriges Aus-/Einblenden.

**Prüfstand:** 110 lokale Tests erfolgreich, einschließlich Zahlen-/Textfelder und schreibfreier Validierung. Cursorverhalten im laufenden Fusion noch zu bestätigen. 0.4.3 wurde zuvor vom Benutzer als funktionsfähig bestätigt.

## 26.09.2026 – 0.4.3

**Git-Zusammenfassung:** `feat: STEP-Winkel als wiederverwendbare Komponenten (0.4.3)`

- Gelieferte 20er-/30er-/40er-STEP-Dateien integriert; einmaliger Import beim Add-in-Start, gemeinsame Komponente je Größe und separate Platzierungs-IDs.
- Auflage an äußeren Profilflächen, vollständige Montagehüllen und überschneidungsfreie parallele Anordnung; gemeinsame Gruppe „91 | Winkel“.
- Statischen Zubehör-Platzhaltertext durch lokale rote Fehlermeldung ersetzt; beide READMEs und Installation aktualisiert.

**Prüfstand:** 108 lokale Tests erfolgreich; Version 0.4.3 am 26.09.2026 durch den Benutzer als funktionsfähig in Fusion bestätigt.

**Details:** [STEP-Winkel](winkel.md)

## 26.09.2026 – 0.4.2

**Nachkorrektur:** Die Rahmen-/Pfostenprüfung berücksichtigt jetzt die DXF-Toleranz von 0,00001 mm. Beide 20er-Dateien unter `profiles` reproduzierten zuvor die falsche Ablehnung bei nur rund 0,00000007 mm Differenz zwischen Breite und Höhe. Originalkonturen bleiben unverändert; tatsächliche Überbreiten werden weiterhin abgelehnt. 103 lokale Tests erfolgreich, einschließlich beider Dateien und der Toleranzgrenze. Fusion-Prüfung der Korrektur offen.

**Git-Zusammenfassung:** `feat: Vereinfachte Winkelkörper in gemeinsamer Baugruppe (0.4.2)`

- Dreieckkörper 20/30/40 an Rahmeninnenecken und Querträgerenden, optional parallel bei doppelter gemeinsamer Montagehöhe.
- Gemeinsame ein-/ausblendbare Gruppe „91 | Winkel (vereinfacht)“, stabile IDs und violette Vorschauumrisse.
- Belegte Montagebereiche und fehlende Größen werden gemeldet; Körper ohne Bohrungen, Schrauben oder Muttern.

**Prüfstand:** 101 lokale Tests und Syntaxprüfung erfolgreich; Fusion-Prüfung von 0.4.2 offen.

**Details:** [Vereinfachte Winkel](winkel.md)

## 26.09.2026 – 0.4.1

**Git-Zusammenfassung:** `feat: Farbige Dialoghinweise und Vorschau einpassen (0.4.1)`

- Fehler rot, Warnhinweise farblich abgesetzt in Eingabeprüfung, Vorschau, Einstellungen und Bibliotheken; Text wird sicher formatiert.
- Vorschau beim Einschalten anhand der Gestellabmessungen inklusive Zubehör einpassen; manuelles Zoomen bei späteren Eingabeänderungen beibehalten.
- 0.4.0 als fehlerfrei bestätigt dokumentiert; Benutzerregeln für dreieckige Winkel für S07 / 0.4.2 vorgemerkt.

**Prüfstand:** 95 lokale Tests und Syntaxprüfung erfolgreich; Fusion-Prüfung von 0.4.1 offen. Verbindungsteile sind noch nicht umgesetzt.

**Details:** [Dialoghinweise und Vorschau](dialoghinweise_vorschau.md)

## 26.09.2026 – 0.4.0

**Git-Zusammenfassung:** `feat: Bauart, gemischtes Zubehör und kompakter Dialog (0.4.0)`

- Untergestell/Transportwagen vorbelegen; Füße und Rollen gemeinsam oder einzeln je Ecke auswählen, gleiche Bauhöhen prüfen.
- Zubehör bearbeiten und duplizieren; Bremse, Verstellbereich, Referenz/Stellung und Montagehinweise als Eigenschaften speichern. Bestehende Auswahlen bleiben unverändert.
- Alle Ausklappbereiche starten geschlossen, Anfangshöhe des Dialogs auf 640 reduziert. 0.3.1 durch Benutzer bestätigt.

**Prüfstand:** 90 lokale Tests und Syntaxprüfung erfolgreich; Version 0.4.0 am 26.09.2026 durch den Benutzer als fehlerfrei bestätigt. Absenkbare Rollen sind frei definierbare Platzhalter; kein Herstellerprodukt festgelegt.

**Details:** [Bauart und Zubehöranordnung](bauart_zubehoer.md)

## 26.09.2026 – 0.3.1

**Git-Zusammenfassung:** `feat: Profile je Bauteilgruppe und rechteckige Querschnitte (0.3.1)`

- Eigene Profile für Pfosten, Rahmen und Querträger sowie je Ebene; Vierteldrehungen und Übernahme auf alle Ebenen.
- Maßabhängige Zuschnitte, Aussparungen, bündige Auflagen und freie Bodenabstände.
- Screenshot-Satz 0.3.0 in beiden READMEs eingebunden; Benutzerprüfung für 0.2.0, 0.2.1 und 0.3.0 festgehalten.

**Prüfstand:** 82 lokale Tests und Syntaxprüfung erfolgreich; Version 0.3.1 am 26.09.2026 durch den Benutzer als funktionsfähig bestätigt. Der Benutzer hat 0.2.0, 0.2.1 und 0.3.0 am 26.09.2026 als getestet und funktionsfähig bestätigt.

**Details:** [Profile je Bauteilgruppe](profile_je_bauteilgruppe.md)

## 25.09.2026 – 0.3.0

**Git-Zusammenfassung:** `feat: DXF-Profilbibliothek und echte Profilquerschnitte (0.3.0)`

- Lokale ASCII-DXF prüfen, Maße bestätigen, Metadaten erfassen und Profile speichern/auswählen/löschen.
- Native Linien, Kreise und Bögen mit Hohlräumen extrudieren; Mittelpunkt im Ursprung berücksichtigen.
- Bibliothekskopien mit Prüfsummen, eigenständige Profildefinitionen in Standardwerten und Baugruppen.

**Prüfstand:** 68 lokale Tests und Syntaxprüfung erfolgreich; Fusion-Funktion am 26.09.2026 durch den Benutzer bestätigt; reales Hersteller-Referenzprofil weiterhin offen. Testdaten sind synthetisch.

**Details:** [Profilbibliothek und DXF-Import](profilbibliothek_dxf.md)

## 25.09.2026 – 0.2.1

**Git-Zusammenfassung:** `feat: Querträger je Ebene und wählbare Deckplattenmontage (0.2.1)`

- Anzahl 0–5 und Quer/Längs je Ebene per Auswahlfeld, gleiche freie Felder und Übernahme auf alle Ebenen.
- Deckplatte alternativ ohne Aussparungen auf Profilen; Pfostenlänge berücksichtigt Plattenstärke und Zubehörhöhe.
- Standardwerte, Bauteildaten, Vorschau und Layout unterstützen beide Ergänzungen.

**Prüfstand:** 46 lokale Tests und Syntaxprüfung erfolgreich; Funktion im laufenden Fusion am 26.09.2026 durch den Benutzer bestätigt.

**Details:** [Querträger und Deckplattenmontage](quertraeger_deckplatte.md)

## 25.09.2026 – 0.2.0

**Git-Zusammenfassung:** `feat: Mittellinien-Vorschau und fixierte Layoutskizze (0.2.0)`

- Aktualisierte 3D-Vorschau mit optionalen Bodenflächen und Zubehörumrissen ergänzt.
- Verdeckte, fixierte Layoutskizze aus denselben Bauteildaten gespeichert; Orientierung im Dialog erklärt.
- Temporäre Grafik bei Abbruch, Änderungen und Fehlern bereinigt; Version und Dokumentation aktualisiert.

**Prüfstand:** 40 lokale Tests und Syntaxprüfung erfolgreich; Funktion im laufenden Fusion am 26.09.2026 durch den Benutzer bestätigt.

**Details:** [Vorschau und Layout](vorschau_layout.md)

## 25.09.2026 – 0.1.5

**Git-Zusammenfassung:** `feat: Gemeinsame Bauteildaten und strukturierte Baugruppen (0.1.5)`

- Gemeinsames Gestellmodell mit Rollen, stabiler ID-Zuordnung, Profilreferenzen, Ausrichtung und Zuschnittlängen eingeführt.
- Fusion-Unterbaugruppen, Bauteileigenschaften und getrennte Gestellkennungen ergänzt.
- Erzeugungsschritte in parametrischen Dokumenten pro Bauteil benannt und gruppiert; bisherigen Geometrieumfang erhalten.

**Prüfstand:** 28 lokale Tests und Syntaxprüfung erfolgreich; neue Struktur und Zeitleiste noch in Fusion zu prüfen.

**Details:** [Bauteildaten und Baugruppenstruktur](bauteildaten.md)

## 25.09.2026 – 0.1.4

**Git-Zusammenfassung:** `feat: Füße und Rollen mit eigener Platzhalterbibliothek (0.1.4)`

- Auswahl von Füßen/Rollen ergänzt; vier Zylinderplatzhalter unter den Pfosten, Bauhöhe in Gesamthöhe berücksichtigt.
- Eigene Einträge mit Name, Art, Höhe und Durchmesser in den Einstellungen speichern, auflisten und löschen.
- Separate Bibliotheksdatei, gespeicherte Auswahl und Kompatibilität mit bisherigen Einstellungen ergänzt; Version **0.1.4**.

**Prüfstand:** 19 lokale Tests und Syntaxprüfung erfolgreich. Funktion laut Benutzerrückmeldung am 25.09.2026 bestätigt.

**Details:** [Füße, Rollen und eigene Platzhalter](demo_installation.md#füße-rollen-und-eigene-platzhalter)

## 25.09.2026 – 0.1.3

**Git-Zusammenfassung:** `feat: Aufliegende Bodenplatten mit Eckausklinkungen (0.1.3)`

- Auf jedem Rahmen eine aufliegende Platte ergänzt, auch oben und auf dem optionalen unteren Rahmen.
- Vier Eckausklinkungen für die Pfosten modelliert; Plattenstärke bei Höhen und automatischer Verteilung berücksichtigt.
- Gesamthöhe einschließlich oberer Platte beibehalten; Version auf **0.1.3** erhöht.

**Prüfstand:** 13 lokale Tests und Syntaxprüfung erfolgreich; Geometrie noch in Fusion zu prüfen.

**Details:** [Bodenplatten und Zwischenböden](demo_installation.md#zwischenböden)

## 24.09.2026 – 0.1.2

**Git-Zusammenfassung:** `feat: Zwischenböden mit optionalen Höhen ergänzen (0.1.2)`

- Anzahl der Zwischenböden, optionale Einzelhöhen und Plattenstärke im Dialog ergänzt.
- Leere Höhen mit gleichen freien Abständen verteilt; Böden mit Tragrahmen erzeugt und Überschneidungen geprüft.
- Einstellungen um Böden erweitert; vorhandene Einstellungsdateien bleiben lesbar. Version auf **0.1.2** erhöht.

**Prüfstand:** Zehn lokale Tests und Syntaxprüfung erfolgreich; neue Dialogfelder und Böden noch in Fusion zu prüfen.

**Details:** [Demo und Installation](demo_installation.md#zwischenböden)

## 24.09.2026 – 0.1.1

**Git-Zusammenfassung:** `fix: Nach Gestellerstellung auf alles zoomen (0.1.1)`

- Nach erfolgreicher Gestellerstellung automatisch „Zoom auf alles“ ausführen.
- Version in `version.py`, Manifest und aktueller Dokumentation auf **0.1.1** erhöht.

**Prüfstand:** Bisherige Demo laut Benutzerrückmeldung in Ordnung. Fünf lokale Tests und Syntaxprüfung erfolgreich; neuer automatischer Zoom in Fusion noch zu prüfen.

**Details:** [Demo und Installation](demo_installation.md)

## 24.09.2026 – 0.1.0

**Git-Zusammenfassung:** `feat: FrameKit-Integrationsdemo 0.1.0 ergänzen`

- Fusion-Befehl unter **Volumenkörper → Erstellen** mit FrameKit-Icons und drei Dialogreitern integriert.
- Einfache Gestellerstellung mit Eingabeprüfung und speicherbaren Standardwerten ergänzt.
- Info-Reiter nach Vorlage mit Logo und Projektlinks gestaltet; Version zentral in `version.py` hinterlegt.
- Deutsche und englische README, Banner, Dokumentationslinks und Installationsanleitung ergänzt; Git-Ausnahmen für benötigte Add-in-Dateien korrigiert.

**Prüfstand:** Fünf lokale Tests erfolgreich; Syntax, Ressourcen und Links geprüft. Integrationstest in Fusion noch offen.

**Details:** [Demo und Installation](demo_installation.md) · [Projektplan](projektplan_FrameKit.md)
