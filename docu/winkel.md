# Vereinfachte Winkel – 0.4.2

Unter **Winkel (vereinfacht)** ist **Winkelkörper erstellen** beim Öffnen einer Konfiguration ohne bisherige Winkeloption standardmäßig aktiviert. Die Option lässt sich abschalten und als Standard speichern. Alle neuen Ausklappbereiche bleiben anfangs geschlossen.

Die Körper liegen in der eigenen Fusion-Unterbaugruppe **91 | Winkel (vereinfacht)**. Das Augensymbol dieser Gruppe blendet alle Winkel des jeweiligen Gestells gemeinsam ein oder aus. Jeder Winkel ist zusätzlich eine eigene Komponente mit stabiler ID und kann einzeln geschaltet werden. Andere Gestelle und Profil-/Plattengruppen bleiben unabhängig.

## Geometrische Regeln

- Profilgrundgrößen 20, 30 und 40 mm ergeben rechtwinklige Dreieckkörper mit gleich langen Schenkeln 20 × 20, 30 × 30 beziehungsweise 40 × 40 mm. Die Grundgröße ist die kleinere Querschnittsabmessung. Beide zugeordneten Profile müssen dieselbe unterstützte Grundgröße besitzen; andere Kombinationen werden als fehlende Zuordnung gemeldet.
- Die Dreiecke liegen horizontal in den Rahmeninnenecken, unter der Plattenunterseite innerhalb der gemeinsamen Profilhöhe. Pro Querträger kommt zusätzlich ein Körper an jedes Ende, auf einer freien seitlichen Flanke. Dies ist eine geometrische Darstellung der Winkelpositionen, keine vollständige Pfosten-/Rahmenverschraubung.
- Zur Darstellung wird das Dreieck **4 mm** hoch extrudiert. Das ist eine ausdrücklich vereinfachte Darstellungsdicke, keine behauptete Hersteller-Wandstärke. Bohrungen, Radien, Schrauben und Muttern werden nicht erzeugt.
- **Zwei parallel bei doppelter Montagehöhe** ist optional und standardmäßig aus. Bei aktivierter Option und einer gemeinsamen vertikalen Profilhöhe von mindestens zweimal der Grundgröße werden zwei Körper gleichmäßig über diese Höhe verteilt. Beispielsweise kann ein vertikal 80 mm hohes 40 × 80-Profil zwei 40er-Körper erhalten. Ein um 90° gedrehtes, nur 40 mm hohes Profil erhält in dieser horizontalen Anordnung einen Körper. Eine automatische Aussage über Nutpositionen oder Schraubpunkte ist damit nicht verbunden.
- Nutbreiten erzeugen gemäß Benutzerregel keine unterschiedlichen Winkelkörper. Passende Schrauben/Muttern sind noch nicht festgelegt; die gespeicherten Winkeldaten kennzeichnen die Befestigung als unvollständig.

Körper werden gegen die äußeren Profil-, Platten- und Zubehörabmessungen sowie bereits platzierte Winkel geprüft. Berührung an Montageflächen ist erlaubt, Überschneidung nicht. An Querträgern wird bei belegter Flanke die andere Seite versucht. Falls kein Platz vorhanden ist, wird der Winkel ausgelassen und ein farbiger Hinweis angezeigt. Auch fehlende Größenzuordnungen erscheinen als Hinweis. Alle Hinweise stehen zusätzlich in den gespeicherten Baugruppendaten; im Dialog werden die ersten drei plus die Anzahl weiterer Hinweise angezeigt. Die Prüfung der Außenabmessungen ist konservativ und nutzt keine Nuten oder Hohlräume als freien Montageraum.

Die Vorschau zeigt die Winkel als violette Dreieckprismen-Umrisse. Sie verwendet dieselben Positionen wie die späteren Körper. Deaktivieren von **Winkelkörper erstellen** entfernt auch diese Umrisse. Die einheitliche Fusion-Gruppe steht nach der Erstellung zur Verfügung.

## Prüfstand

**101 lokale Tests erfolgreich**, einschließlich Größen, Stückzahlen der Platzhalter, Orientierung, Kollisionen, optionaler Doppelanordnung, stabiler IDs, Einstellungen, Dialogoptionen und Dreieckextrusion im API-Ersatz. **Prüfung im laufenden Fusion offen.**

1. Gestelle mit Profilen 20 × 20, 30 × 30 und 40 × 40 erstellen: vier Winkel pro Rahmenebene sowie zwei zusätzliche pro Querträger, soweit ausreichend Platz besteht.
2. Gruppe **91 | Winkel (vereinfacht)** aus-/einblenden und einzelne Winkel separat schalten.
3. Breites 40 × 80-Profil mit 80 mm vertikaler Montagehöhe prüfen: Einzel-/Doppeloption vergleichen.
4. Enge Gestelle, Querträger nahe den Ecken und nicht zugeordnete Profilgrößen prüfen: keine sich überschneidenden Körper; Hinweise sichtbar.
5. Vorschau mit Körpern vergleichen, Optionen speichern und erneut laden; mehrere Gestelle unabhängig schalten.

[Ablaufplan](ablaufplan.md) · [Installation](demo_installation.md) · [Deutsche README](../README.md)
