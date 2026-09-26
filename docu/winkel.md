# STEP-Winkel – 0.4.3

FrameKit verwendet die bereitgestellten Dateien `profiles/winkel/Winkel_20x20.step`, `Winkel_30x30.step` und `Winkel_40x40.step`. Unveränderte Kopien liegen im installierbaren Add-in unter `resources/brackets`; die Installation benötigt keinen Zugriff auf den Repository-Ordner.

Unter **Winkel → Winkelkörper erstellen** werden die Bauteile aktiviert. Die Gruppe **91 | Winkel** schaltet alle Winkel eines Gestells gemeinsam. Je verwendeter Größe wird innerhalb des Gestells eine Komponente angelegt; weitere Positionen verwenden Instanzen derselben Komponente. Einzelne Vorkommen lassen sich separat ein-/ausblenden. Geometrieänderungen an der gemeinsamen Komponente wirken auf alle ihre Vorkommen. Verschiedene Gestelle bleiben unabhängig. Stabile Platzierungs-IDs, Position und vollständige Bauteildaten liegen an den Vorkommen; die Komponente trägt die gemeinsame Typ-/Quelldatei-Information.

## Montage und Vorschau

- Die gelieferten Dateien enthalten jeweils einen Volumenkörper mit Außenmaßen 20³, 30³ beziehungsweise 40³ mm. Die Auflageflächen liegen bei X=0 und Z=0, die Breite verläuft entlang Y. FrameKit normalisiert diese Ausrichtung ohne Skalierung oder Spiegelung.
- Je Rahmeninnenecke sowie je Querträgerende wird ein Winkel mit beiden Auflageflächen an den äußeren Profilflächen angeordnet. Der Körper wird über die gemeinsame Montagehöhe zentriert; Nuten gelten nicht als freier Montageraum.
- Beide beteiligten Profile müssen dieselbe Grundgröße 20, 30 oder 40 mm besitzen. Die Grundgröße ist ihre kleinere Querschnittsabmessung. Die Nutbreite erzeugt keine zusätzliche Variante.
- **Zwei parallel bei doppelter Montagehöhe** verwendet denselben Winkeltyp zweimal. Bei einem vertikal 80 mm hohen 40×80-Profil liegen zwei 40-mm-breite Winkel in getrennten, gleichmäßig verteilten Montagebereichen. Nach einer Drehung auf nur 40 mm vertikale Höhe bleibt ein Winkel.
- Die Kollisionsprüfung verwendet konservative quaderförmige Außenhüllen. Berührende Flächen sind erlaubt; bei belegtem Raum wird am Querträger die andere Flanke versucht, andernfalls der Winkel ausgelassen und ein farbiger Hinweis angezeigt. Die Prüfung nutzt keine Aussparungen der STEP-Körper als freien Raum.
- Die **violette Vorschau zeigt die Montagehüllen**, nicht die detaillierten STEP-Kanten. Sie verwendet die tatsächlichen Außenmaße und dieselben Positionen wie die späteren Bauteile. Die Liniengrafik wird bei einer Änderung erneuert; die STEP-Dateien werden dabei nicht erneut importiert.
- Schrauben, Muttern und Tragfähigkeitsberechnungen sind nicht Bestandteil dieser Integration. Die vorhandenen STEP-Körper werden unverändert verwendet.

## Import und Installation

Das Add-in lädt die drei STEP-Dateien einmal beim Start über temporäre Fusion-Dokumente. Diese werden nach dem Kopieren der Körper ungespeichert geschlossen; das vorher aktive Dokument wird wieder aktiviert. Während der Dialogausführung werden nur die zwischengespeicherten Körper eingefügt. Nach Austausch der Dateien muss FrameKit neu gestartet werden. Bei fehlenden Dateien, falschen Außenmaßen oder ungültigen Körpern wird die betroffene Winkelerstellung mit einer Fehlermeldung abgebrochen; es gibt keinen stillen Rückfall auf Platzhalter.

API-Grundlagen: [Import in ein neues Dokument](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_ImportManager_importToNewDocument.htm), [Einfügen von BRep-Körpern und Basisfeatures](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_BRepBodies_add.htm).

## Prüfstand

**108 lokale Tests erfolgreich.** Geprüft werden unter anderem identische Original-/Paketdateien, Maße und Einheiten, Montageausrichtung ohne Spiegelung, kollisionsfreie Doppelanordnung, gemeinsame Komponente mit individuellen Vorkommens-IDs, Import-Lebenszyklus und Fehlerbereinigung im API-Ersatz. **Version 0.4.3 wurde am 26.09.2026 vom Benutzer als funktionsfähig in Fusion bestätigt.** Die folgenden Punkte bleiben als wiederverwendbare Prüfliste dokumentiert.

1. Add-in vollständig aktualisieren und neu starten; das vorherige Dokument muss erhalten bleiben.
2. Gestelle mit 20er-, 30er- und 40er-Profilen erstellen: Auflageflächen und Ausrichtung an allen vier Ecken sowie Querträgerenden prüfen.
3. Einzelne Vorkommen und die Gruppe **91 | Winkel** aus-/einblenden; Wiederverwendung derselben Komponente prüfen.
4. 40×80 mit 80 mm vertikaler Höhe und Doppeloption prüfen; anschließend Profil drehen und Einzelanordnung vergleichen.
5. Vorschau-Montagehüllen mit fertigen Körpern vergleichen; enge Montagebereiche und mehrere unabhängige Gestelle prüfen.

[Ablaufplan](ablaufplan.md) · [Installation](demo_installation.md) · [Deutsche README](../README.md)
