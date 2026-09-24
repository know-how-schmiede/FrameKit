# FrameKit – Änderungshistorie

Pro Version: kurze Git-Zusammenfassung, Prüfstand und Links. Technische Details und Anleitungen werden in eigenen Dokumenten unter `docu` gepflegt.

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
