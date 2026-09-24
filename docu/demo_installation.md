# FrameKit 0.1.0 – Integrationsdemo

Die Demo prüft die Einbindung als natives Autodesk-Fusion-Add-in. Sie erzeugt ein einfaches Gestell mit vier Pfosten, oberem und optional unterem Rahmen aus massiven Rechteckprofilen. Jedes der acht beziehungsweise zwölf Profile ist eine eigene Komponente. Nutquerschnitte, Vorschau, Zubehör, Projektbearbeitung und CSV-Export sind noch nicht implementiert.

## In Fusion laden

1. Den vollständigen Ordner `fusion_addin/FrameKit` lokal bereitstellen. Manifest, `lib` und `resources` müssen enthalten sein. Weitere Python-Pakete sind nicht erforderlich.
2. In Fusion **Dienstprogramme → Zusatzmodule → Skripte und Zusatzmodule** öffnen (alternativ `Umschalt+S`).
3. Im Bereich **Zusatzmodule** über das Hinzufügen-Symbol den Ordner `fusion_addin/FrameKit` als lokales Add-in auswählen.
4. **FrameKit** auswählen und **Ausführen** anklicken. Optional den automatischen Start aktivieren.
5. Ein Konstruktionsdokument öffnen und **Volumenkörper → Erstellen → FrameKit** aufrufen. Der Befehl ist zusätzlich an die Werkzeugleiste angeheftet.

Nach Codeänderungen das Add-in stoppen und erneut starten. Falls Fusion noch alte Module verwendet, Fusion neu starten.

## Dialog

- **Frame erstellen:** Außenlänge, Außenbreite, Höhe und quadratische Profilbreite in Millimetern einstellen; unteren Rahmen optional deaktivieren. **Ausführen** erstellt eine neue Demo-Baugruppe. Mehrfaches Ausführen erzeugt unabhängige Baugruppen.
- **Einstellungen verwalten:** Aktuelle Abmessungen als Standardwerte speichern oder Werkseinstellungen in den Dialog laden. Zum ausschließlichen Speichern im ersten Reiter **Demo-Gestell erstellen** deaktivieren. Änderungen werden erst mit **Ausführen** gespeichert; **Abbrechen** ändert weder Modell noch Einstellungsdatei.
- **info:** Aufbau nach der PrintThread-Wizard-Vorlage: Name und Version aus `version.py`, FrameKit-Logo, Kurzbeschreibung sowie Links zu Homepage, Quellcode, Releases, Issues und YouTube. Autor und Lizenz schließen den Bereich ab.

Die Einstellungen liegen unter Windows in `%APPDATA%/FrameKit/settings.json`, auf macOS in `~/Library/Application Support/FrameKit/settings.json`. Fehlende oder beschädigte Einstellungen führen zu Werkseinstellungen; beschädigte Dateien werden nicht automatisch überschrieben.

## Icons und Version

Die vorhandenen `CreateFrame`- und `ProfileLibrary`-SVGs werden im Add-in mitgeliefert: `16x16.svg` für kleine Bedienelemente, `32x32.svg` für große sowie jeweils `-dark_blue`-Varianten. Die Vektorgrafiken skalieren auch bei hoher Bildschirmauflösung. Das Add-in-Symbol verwendet ebenfalls das FrameKit-Rahmensymbol.

Die Version beginnt bei **0.1.0** und wird nur auf ausdrückliche Aufforderung erhöht. Maßgeblich ist [`version.py`](../fusion_addin/FrameKit/version.py); bei Änderungen muss das Feld `version` in `FrameKit.manifest` denselben Wert erhalten. Ein automatisierter Test prüft die Übereinstimmung.

## Integrationstest in Fusion

- Starten: genau ein FrameKit-Befehl unter **Volumenkörper → Erstellen**, Symbol in Menü und Werkzeugleiste sichtbar; auch mit dunklem Theme und hoher Skalierung prüfen.
- Dialog: alle drei Reiter öffnen, Texte und Links prüfen.
- Standardgestell erzeugen: **800 × 500 × 750 mm**, Profil **40 mm**, zwölf Komponenten unter einer FrameKit-Demo-Baugruppe. Ohne unteren Rahmen acht Komponenten.
- Negative oder zu kleine Maße eingeben: Ausführen muss gesperrt sein. Länge, Breite und Höhe müssen jeweils größer als zwei Profilbreiten sein.
- Abbrechen: keine neue Geometrie und keine gespeicherten Änderungen.
- Standardwerte speichern, Dialog erneut öffnen und Werte prüfen; Werkseinstellungen laden und speichern.
- Erzeugung rückgängig machen; bestehende fremde Komponenten müssen unverändert bleiben.
- Add-in stoppen: Befehl verschwindet. Erneuter Start: Befehl erscheint einmal und funktioniert wieder.

Lokale Tests: `python -m unittest discover -s tests -v`. Diese prüfen Berechnung, Einstellungsdateien und Versionsabgleich außerhalb von Fusion. Sie ersetzen keinen Integrationstest im laufenden Fusion. Die tatsächliche Darstellung und Geometrieerstellung in Fusion sind noch nicht verifiziert.

API-Grundlagen: [Autodesk: UI-Anpassung und Icon-Ressourcen](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserInterface_UM.htm), [Dialogreiter](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CommandInputs_addTabCommandInput.htm).

[Deutsche README](../README.md) · [English README](../README.en.md) · [Projektplan](projektplan_FrameKit.md)
