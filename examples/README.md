# Beispielgestelle für FrameKit 0.9.0

`FrameKit-Beispiele.json` ist eine importierbare FrameKit-Sicherung mit sieben benannten Vorlagen. In **Einstellungen verwalten → Vorlagen und Datensicherung** zuerst **Als Kopie übernehmen** wählen, die Datei prüfen und dann übernehmen. Anschließend eine Vorlage laden und das Gestell erstellen. Bestehende persönliche Standardwerte werden nicht ersetzt.

| Vorlage | Zweck |
| --- | --- |
| 01 Einfaches Gestell | Grundaufbau ohne Zwischenboden |
| 02 Zwei Zwischenböden | Zwei feste Höhen und Querträger |
| 03 Transportwagen gemischte Rollen | Zwei Lenkrollen und zwei Bockrollen |
| 04 Eigenes DXF-Profil | Synthetischer Nutquerschnitt mit Hohlräumen |
| 05 Unterschiedliche Gruppenprofile | Nutprofil-Pfosten und Demo-Vollprofilrahmen |
| 06 Gestell mit Füßen | Zubehörhöhe im Gesamthöhenbezug |
| 07 Absenkbare Rollen (synthetisch) | Explizite Stellung und Referenz, vereinfachte Zylinder |

Alle Profile und Zubehördaten sind synthetische Testdaten, keine geprüften Herstellerprodukte. `synthetic_tslot_40.dxf` dient zusätzlich zum unabhängigen Importtest. Die Sicherung enthält diese DXF bereits. `Erwartungswerte.json` enthält Abmessungen, Profil-/Bauteilmengen sowie Listenpositionen aus der lokalen Modellberechnung. Befestigungsmittel bleiben entsprechend dem aktuellen Funktionsumfang unvollständig.

Es sind keine vorab in Fusion erzeugten `.f3d`-Dateien enthalten. Die Vorlagen erzeugen die Prüfbaugruppen im jeweiligen Fusion-System. Prüfschritte und offene native Ergebnisse: [Installation und Abnahme](../docu/installation_abnahme.md).

Im Quellrepository reproduzierbar mit `python installer/create_examples.py` erzeugen.
