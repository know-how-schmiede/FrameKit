# FrameKit 0.2.1 – Integrationsdemo

Die Demo prüft die Einbindung als natives Autodesk-Fusion-Add-in. Sie erzeugt ein einfaches Gestell mit vier Pfosten, oberem und optional unterem Rahmen aus massiven Rechteckprofilen. Ohne Zwischenböden entstehen acht beziehungsweise zwölf Profilkomponenten sowie eine obere und gegebenenfalls eine untere Bodenplatte. Jeder Zwischenboden ergänzt vier Rahmenprofile und eine Platte als eigene Komponenten. Optional werden vier Fuß-/Rollenplatzhalter erzeugt. Nutquerschnitte, detailliertes Zubehör, Projektbearbeitung und CSV-Export sind noch nicht implementiert.

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
- **Einstellungen verwalten:** Aktuelle Abmessungen und Fuß-/Rollenauswahl als Standardwerte speichern oder Werkseinstellungen in den Dialog laden. Zum ausschließlichen Speichern im ersten Reiter **Demo-Gestell erstellen** deaktivieren. Standardwerte werden erst mit **Ausführen** gespeichert. Die separate Platzhalterbibliothek wird über eigene Schaltflächen sofort gespeichert; diese Änderungen bleiben auch nach **Abbrechen** erhalten.
- **info:** Aufbau nach der PrintThread-Wizard-Vorlage: Name und Version aus `version.py`, FrameKit-Logo, Kurzbeschreibung sowie Links zu Homepage, Quellcode, Releases, Issues und YouTube. Autor und Lizenz schließen den Bereich ab.

Die Einstellungen liegen unter Windows in `%APPDATA%/FrameKit/settings.json`, auf macOS in `~/Library/Application Support/FrameKit/settings.json`. Fehlende oder beschädigte Einstellungen führen zu Werkseinstellungen; beschädigte Dateien werden nicht automatisch überschrieben.

## Vorschau und Layout

Im ersten Reiter **Vorschau anzeigen** einschalten. Bodenflächen und Zubehörumrisse sind unabhängig schaltbar. Änderungen gültiger Maße aktualisieren die Darstellung. Beim Erstellen wird eine fixierte 3D-Mittellinienskizze unter **00 | Layout** gespeichert und ausgeblendet. Die Dialogwerte bleiben maßgeblich. Bedienung, Orientierung und Prüfschritte: [Vorschau und Layout](vorschau_layout.md).

## Icons und Version

Aktueller Stand: **0.2.1**. Querträger und Deckplattenmontage: siehe [Anleitung und Prüfschritte](quertraeger_deckplatte.md). Die Bauteile werden in Unterbaugruppen mit stabiler ID-Zuordnung und separaten Eigenschaften erzeugt. In parametrischen Dokumenten sind ihre Erzeugungsschritte in der Zeitleiste gruppiert. Details und Prüfschritte stehen unter [Bauteildaten und Baugruppenstruktur](bauteildaten.md).

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
- Abbrechen: keine neue Geometrie und keine geänderten Standardwerte. Bereits explizit gespeicherte oder gelöschte Bibliothekseinträge bleiben bestehen.
- Füße/Rollen: Demo-Rolle wählen, vier Zylinder mit 100 mm Höhe und 75 mm Durchmesser prüfen. Bei Gesamthöhe 750 mm müssen die Pfosten bei 100 mm beginnen und 650 mm lang sein; obere Platte endet weiterhin bei 750 mm.
- Bibliothek: eigenen Eintrag anlegen, in beiden Auswahllisten prüfen und Dialog erneut öffnen. Eintrag löschen und erneut öffnen; er darf nicht wieder erscheinen. Auch das Löschen aller Einträge prüfen.
- Doppelte Namen, leere Namen, ungültige Maße, zu große Durchmesser und eine Bauhöhe ohne ausreichend Platz für den Rahmen müssen abgefangen werden.
- Standardwerte speichern, Dialog erneut öffnen und Werte prüfen; Werkseinstellungen laden und speichern.
- Erzeugung rückgängig machen; bestehende fremde Komponenten müssen unverändert bleiben.
- Add-in stoppen: Befehl verschwindet. Erneuter Start: Befehl erscheint einmal und funktioniert wieder.

Lokale Tests: `python -m unittest discover -s tests -v`. 46 Tests prüfen Berechnungen und Dateien, Gestellmodell, ID-Stabilität, Profilorientierung, Vorschauflächen und Layout sowie Geometrie-, Grafik- und Dialogereignisse mit einem vereinfachten API-Ersatz. Sie ersetzen keinen Integrationstest im laufenden Fusion. Der Benutzer hat am 25.09.2026 bestätigt, dass Version 0.1.4 funktioniert. Struktur und Zeitleiste aus 0.1.5 sowie Vorschau und Layout aus 0.2.0 sowie Querträger und Deckplattenmontage aus 0.2.1 sind noch in Fusion zu prüfen; die vollständige Abnahme ist im [Ablaufplan](ablaufplan.md) vorgesehen.

## Zwischenböden

Unter **Frame erstellen → Bodenplatten und Zwischenböden** lässt sich die Anzahl von 0 bis 20 einstellen. Für jeden Boden erscheint ein optionales Höhenfeld. Höhen beziehen sich auf die **Oberkante der Platte**, gemessen ab Aufstandsfläche einschließlich gewählter Füße/Rollen; die Nummerierung erfolgt von unten nach oben. Zahlen ohne Einheit werden als Millimeter interpretiert; Angaben wie `25 cm` sind ebenfalls möglich.

- **Alle Höhen leer:** Die Böden werden mit gleichen freien Abständen zwischen der Oberseite der unteren Platte und der Unterseite des oberen Tragrahmens verteilt. Ohne unteren Rahmen beginnt der freie Bereich an der Unterseite der Pfosten, also bei der Höhe der Füße/Rollen beziehungsweise 0 mm ohne Zubehör.
- **Höhen vorgegeben:** Diese Werte werden übernommen. Leere Felder zwischen festgelegten Höhen werden innerhalb des verbleibenden Bereichs gleichmäßig verteilt. Der Dialog zeigt die berechneten Oberkanten an.
- **Konstruktion:** Auf jedem Rahmen liegt eine Platte auf, einschließlich oberem und optional unterem Rahmen. Sie reicht bis zu den Außenmaßen des Gestells und erhält vier quadratische Eckausklinkungen in Profilbreite für die Pfosten. Die Plattenstärke ist für alle Ebenen gemeinsam einstellbar, standardmäßig 18 mm. Die Gesamthöhe schließt die obere Platte ein; bei Zwischenböden liegt der Tragrahmen um die Plattenstärke unter der angegebenen Oberkante. Befestigungsteile und Montagespiel werden in der Demo nicht modelliert.
- **Prüfung:** Überlappende, absteigende oder außerhalb des Gestells liegende Ebenen verhindern die Erstellung. Auch automatisch verteilte Böden müssen einschließlich Rahmen und Plattenstärke in den verfügbaren Raum passen. Dies gilt auch ohne Zwischenböden für die obere und untere Ebene.

Beispiel ohne Füße/Rollen bei Standardmaßen (Höhe 750 mm, Profil 40 mm, unterer Rahmen): Zwei automatische Böden liegen bei ungefähr **288,7 mm** und **519,3 mm**. Mit drei Böden und einer festen mittleren Höhe von **400 mm** ergeben sich **229 / 400 / 575 mm**.

Gespeichert werden die vorgegebenen Höhen einschließlich leerer Werte. Automatische Höhen werden bei geänderten Gestellmaßen neu berechnet. Alte Einstellungsdateien werden mit null Zwischenböden ergänzt. Werkseinstellungen setzen die Anzahl auf null zurück.

## Füße, Rollen und eigene Platzhalter

Unter **Frame erstellen → Füße / Rollen** stehen „Keine Füße / Rollen“ und alle gespeicherten Bibliothekseinträge zur Auswahl. Ohne vorhandene Bibliotheksdatei werden ein Demo-Fuß (Höhe 40 mm, Durchmesser 50 mm) und eine Demo-Lenkrolle (100 / 75 mm) angeboten. Die gewählte Variante gilt für alle vier Eckpfosten.

Die Darstellung erfolgt unabhängig von der Art als **aufrechter Zylinder**, eindeutig als Platzhalter benannt. Höhe und Durchmesser beschreiben den Platzbedarf, keine detaillierte Rad- oder Montagegeometrie. Die Zylinder stehen mittig unter den Pfosten auf Z = 0. Die Gesamthöhe bleibt einschließlich Zubehör und oberer Platte erhalten; die Pfosten verkürzen sich um die Zubehörhöhe. Manuelle Bodenhöhen bleiben auf die Aufstandsfläche bezogen. Überstände der Platzhalter zählen nicht zu Länge und Breite des Profilrahmens.

Unter **Einstellungen verwalten → Eigene Füße und Rollen**:

1. Einen eindeutigen Namen und eine Art wählen: Fuß, Lenkrolle, Bockrolle, absenkbare Rolle oder Sonstiges.
2. Höhe und Durchmesser eingeben. Zahlen ohne Einheit sind Millimeter; in einem geöffneten Dokument sind auch Einheiten wie `10 cm` möglich.
3. **Neuen Eintrag speichern** anklicken. Der Eintrag wird sofort dauerhaft gespeichert und erscheint mit Art und Maßen in beiden Auswahllisten.
4. Zum Entfernen unter **Gespeicherte Einträge** auswählen und **Ausgewählten Eintrag löschen** anklicken. Löschen wird sofort gespeichert. War der Eintrag für das Gestell gewählt, wechselt diese Auswahl auf „Keine“.

Die Bibliothek liegt in `accessories.json` neben der Datei `settings.json`. Ihre Speichern-/Löschen-Schaltflächen arbeiten unabhängig von **Ausführen** und der Option **Als Standardwerte speichern**. **Abbrechen** nimmt Bibliotheksänderungen nicht zurück. Werkseinstellungen löschen die Bibliothek nicht. Auch eine vollständig geleerte Bibliothek bleibt nach erneutem Öffnen leer.

Die ausgewählte Definition wird beim Speichern der Standardwerte und in erzeugten Baugruppen mit ihren Maßen hinterlegt. Bereits erzeugte Geometrie ändert sich beim Löschen eines Eintrags nicht. Verweist eine gespeicherte Auswahl auf einen inzwischen gelöschten Eintrag, wird beim Öffnen „Keine“ gewählt und ein Hinweis angezeigt. Frühere Einstellungsdateien erhalten automatisch die Auswahl „Keine“.

API-Grundlagen: [Autodesk: UI-Anpassung und Icon-Ressourcen](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserInterface_UM.htm), [Dialogreiter](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CommandInputs_addTabCommandInput.htm).

[Deutsche README](../README.md) · [English README](../README.en.md) · [Projektplan](projektplan_FrameKit.md)
