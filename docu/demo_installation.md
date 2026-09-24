# FrameKit 0.1.3 – Integrationsdemo

Die Demo prüft die Einbindung als natives Autodesk-Fusion-Add-in. Sie erzeugt ein einfaches Gestell mit vier Pfosten, oberem und optional unterem Rahmen aus massiven Rechteckprofilen. Ohne Zwischenböden entstehen acht beziehungsweise zwölf Profilkomponenten sowie eine obere und gegebenenfalls eine untere Bodenplatte. Jeder Zwischenboden ergänzt vier Rahmenprofile und eine Platte als eigene Komponenten. Nutquerschnitte, Vorschau, Zubehör, Projektbearbeitung und CSV-Export sind noch nicht implementiert.

## In Fusion laden

1. Den vollständigen Ordner `fusion_addin/FrameKit` lokal bereitstellen. Manifest, `lib` und `resources` müssen enthalten sein. Weitere Python-Pakete sind nicht erforderlich.
2. In Fusion **Dienstprogramme → Zusatzmodule → Skripte und Zusatzmodule** öffnen (alternativ `Umschalt+S`).
3. Im Bereich **Zusatzmodule** über das Hinzufügen-Symbol den Ordner `fusion_addin/FrameKit` als lokales Add-in auswählen.
4. **FrameKit** auswählen und **Ausführen** anklicken. Optional den automatischen Start aktivieren.
5. Ein Konstruktionsdokument öffnen und **Volumenkörper → Erstellen → FrameKit** aufrufen. Der Befehl ist zusätzlich an die Werkzeugleiste angeheftet.

Nach Codeänderungen das Add-in stoppen und erneut starten. Falls Fusion noch alte Module verwendet, Fusion neu starten.

Nach erfolgreicher Gestellerstellung wird die Ansicht automatisch mit **Zoom auf alles** eingepasst. Beim ausschließlichen Speichern von Einstellungen bleibt die Ansicht unverändert.

## Dialog

- **Frame erstellen:** Außenlänge, Außenbreite, Höhe und quadratische Profilbreite in Millimetern einstellen; unteren Rahmen optional deaktivieren. **Ausführen** erstellt eine neue Demo-Baugruppe. Mehrfaches Ausführen erzeugt unabhängige Baugruppen.
- **Einstellungen verwalten:** Aktuelle Abmessungen als Standardwerte speichern oder Werkseinstellungen in den Dialog laden. Zum ausschließlichen Speichern im ersten Reiter **Demo-Gestell erstellen** deaktivieren. Änderungen werden erst mit **Ausführen** gespeichert; **Abbrechen** ändert weder Modell noch Einstellungsdatei.
- **info:** Aufbau nach der PrintThread-Wizard-Vorlage: Name und Version aus `version.py`, FrameKit-Logo, Kurzbeschreibung sowie Links zu Homepage, Quellcode, Releases, Issues und YouTube. Autor und Lizenz schließen den Bereich ab.

Die Einstellungen liegen unter Windows in `%APPDATA%/FrameKit/settings.json`, auf macOS in `~/Library/Application Support/FrameKit/settings.json`. Fehlende oder beschädigte Einstellungen führen zu Werkseinstellungen; beschädigte Dateien werden nicht automatisch überschrieben.

## Icons und Version

Aktueller Stand: **0.1.3**.

Die vorhandenen `CreateFrame`- und `ProfileLibrary`-SVGs werden im Add-in mitgeliefert: `16x16.svg` für kleine Bedienelemente, `32x32.svg` für große sowie jeweils `-dark_blue`-Varianten. Die Vektorgrafiken skalieren auch bei hoher Bildschirmauflösung. Das Add-in-Symbol verwendet ebenfalls das FrameKit-Rahmensymbol.

Die Version beginnt bei **0.1.0** und wird nur auf ausdrückliche Aufforderung erhöht. Maßgeblich ist [`version.py`](../fusion_addin/FrameKit/version.py); bei Änderungen muss das Feld `version` in `FrameKit.manifest` denselben Wert erhalten. Ein automatisierter Test prüft die Übereinstimmung.

## Integrationstest in Fusion

- Starten: genau ein FrameKit-Befehl unter **Volumenkörper → Erstellen**, Symbol in Menü und Werkzeugleiste sichtbar; auch mit dunklem Theme und hoher Skalierung prüfen.
- Dialog: alle drei Reiter öffnen, Texte und Links prüfen.
- Standardgestell erzeugen: **800 × 500 × 750 mm**, Profil **40 mm**, zwölf Profile und zwei Platten unter einer FrameKit-Demo-Baugruppe. Ohne unteren Rahmen acht Profile und eine obere Platte.
- Automatischer Zoom: vorher weit hineinzoomen und ein Gestell erstellen; anschließend müssen alle sichtbaren Modellobjekte in die Ansicht passen.
- Zwei Zwischenböden mit leeren Höhen: gleichmäßige freie Abstände und zehn zusätzliche Komponenten prüfen; Plattenoberkanten müssen den im Dialog angezeigten Höhen entsprechen.
- Drei Böden mit den Höhen leer / 400 mm / leer: bei Standardmaßen Oberkanten 229, 400 und 575 mm prüfen.
- Ungültige Bodenhöhen, vertauschte Reihenfolge und überlappende Ebenen müssen Ausführen sperren. Anzahl reduzieren und erneut erhöhen; nur sichtbare Höhenfelder dürfen berücksichtigt werden.
- Bodenanzahl, leere und feste Höhen sowie Plattenstärke speichern und erneut laden; bestehende Einstellungen aus 0.1.0/0.1.1 müssen ohne Böden weiter funktionieren.
- Negative oder zu kleine Maße eingeben: Ausführen muss gesperrt sein. Länge, Breite und Höhe müssen jeweils größer als zwei Profilbreiten sein.
- Abbrechen: keine neue Geometrie und keine gespeicherten Änderungen.
- Standardwerte speichern, Dialog erneut öffnen und Werte prüfen; Werkseinstellungen laden und speichern.
- Erzeugung rückgängig machen; bestehende fremde Komponenten müssen unverändert bleiben.
- Add-in stoppen: Befehl verschwindet. Erneuter Start: Befehl erscheint einmal und funktioniert wieder.

Lokale Tests: `python -m unittest discover -s tests -v`. 13 Tests prüfen Berechnung, Bodenverteilung, Eckausklinkungen, Plattenauflage, Überlappungen, Einstellungsdateien einschließlich Migration und Versionsabgleich außerhalb von Fusion. Sie ersetzen keinen Integrationstest im laufenden Fusion. Die ursprüngliche Demo wurde vom Benutzer als passend bestätigt. Automatischer Zoom und die neuen Zwischenbodenfunktionen sind noch in Fusion zu prüfen.

## Zwischenböden

Unter **Frame erstellen → Bodenplatten und Zwischenböden** lässt sich die Anzahl von 0 bis 20 einstellen. Für jeden Boden erscheint ein optionales Höhenfeld. Höhen beziehen sich auf die **Oberkante der Platte**, gemessen von der Unterseite des Gestells; die Nummerierung erfolgt von unten nach oben. Zahlen ohne Einheit werden als Millimeter interpretiert; Angaben wie `25 cm` sind ebenfalls möglich.

- **Alle Höhen leer:** Die Böden werden mit gleichen freien Abständen zwischen der Oberseite der unteren Platte und der Unterseite des oberen Tragrahmens verteilt. Ohne unteren Rahmen beginnt der freie Bereich bei 0 mm.
- **Höhen vorgegeben:** Diese Werte werden übernommen. Leere Felder zwischen festgelegten Höhen werden innerhalb des verbleibenden Bereichs gleichmäßig verteilt. Der Dialog zeigt die berechneten Oberkanten an.
- **Konstruktion:** Auf jedem Rahmen liegt eine Platte auf, einschließlich oberem und optional unterem Rahmen. Sie reicht bis zu den Außenmaßen des Gestells und erhält vier quadratische Eckausklinkungen in Profilbreite für die Pfosten. Die Plattenstärke ist für alle Ebenen gemeinsam einstellbar, standardmäßig 18 mm. Die Gesamthöhe schließt die obere Platte ein; bei Zwischenböden liegt der Tragrahmen um die Plattenstärke unter der angegebenen Oberkante. Befestigungsteile und Montagespiel werden in der Demo nicht modelliert.
- **Prüfung:** Überlappende, absteigende oder außerhalb des Gestells liegende Ebenen verhindern die Erstellung. Auch automatisch verteilte Böden müssen einschließlich Rahmen und Plattenstärke in den verfügbaren Raum passen. Dies gilt auch ohne Zwischenböden für die obere und untere Ebene.

Beispiel bei Standardmaßen (Höhe 750 mm, Profil 40 mm, unterer Rahmen): Zwei automatische Böden liegen bei ungefähr **288,7 mm** und **519,3 mm**. Mit drei Böden und einer festen mittleren Höhe von **400 mm** ergeben sich **229 / 400 / 575 mm**.

Gespeichert werden die vorgegebenen Höhen einschließlich leerer Werte. Automatische Höhen werden bei geänderten Gestellmaßen neu berechnet. Alte Einstellungsdateien werden mit null Zwischenböden ergänzt. Werkseinstellungen setzen die Anzahl auf null zurück.

API-Grundlagen: [Autodesk: UI-Anpassung und Icon-Ressourcen](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserInterface_UM.htm), [Dialogreiter](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CommandInputs_addTabCommandInput.htm).

[Deutsche README](../README.md) · [English README](../README.en.md) · [Projektplan](projektplan_FrameKit.md)
