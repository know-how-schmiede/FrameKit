# Vorschau und Layout – 0.2.0

Aktualisierung vom 26.09.2026: Die Versionen 0.2.0, 0.2.1 und 0.3.0 funktionieren laut Benutzerprüfung. Ab 0.3.1 gelten zusätzlich [getrennte Profilwahl und rechteckige Querschnitte](profile_je_bauteilgruppe.md); deren Fusion-Prüfung steht noch aus. Die folgenden Angaben beschreiben den jeweiligen ursprünglichen Versionsumfang.

## Bedienung

Unter **Frame erstellen → Vorschau → Vorschau anzeigen** lässt sich das Gestell vor der Erstellung prüfen. Die Vorschau ist beim Öffnen ausgeschaltet. Nach gültigen Eingabeänderungen wird sie aktualisiert; ungültige Eingaben entfernen die bisherige Darstellung.

- **Blaue Linien:** Mittellinien aller Profile. Jeder Endpunkt liegt in der Mitte der tatsächlichen Schnittfläche. Trägerlinien werden deshalb nicht bis zu den Mittellinien der angrenzenden Pfosten verlängert.
- **Bodenflächen anzeigen:** Halbtransparente Flächen an den Plattenoberkanten, einschließlich der vier Eckausklinkungen. Die Vorschau stellt keine Plattendicke dar; die erzeugte Baugruppe enthält die eingestellte Stärke.
- **Zubehörumrisse anzeigen:** Orange Umrisse der vier Zylinderplatzhalter mit den gewählten Höhen und Durchmessern. Kreisumrisse werden vereinfacht durch jeweils 32 Segmente dargestellt.

Die beiden Anzeigeoptionen verändern ausschließlich die Vorschau, nicht die spätere Baugruppe. Sie werden nicht als persönliche Standardwerte gespeichert. Bei deaktiviertem **Demo-Gestell erstellen** wird keine Vorschau angezeigt. **Ausführen** erstellt die Baugruppe und führt anschließend wie bisher „Zoom auf alles“ aus.

## Orientierung und Maße

Der Gestellursprung liegt vorne links am Profilrahmen auf Höhe der Aufstandsfläche. **X** verläuft von links nach rechts, **Y** von vorne nach hinten und **Z** nach oben. „Vorne“ bezeichnet die Seite bei Y = 0, unabhängig von der aktuellen Kameraposition. Länge und Breite beschreiben die Rahmenaußenmaße; größere Rollen dürfen darüber hinausragen. Bodenhöhen und Gesamthöhe werden ab Aufstandsfläche gemessen.

Vorschau, Layoutskizze und Bauteilerstellung verwenden dasselbe berechnete Gestellmodell. Bei Eingabeänderungen bleiben die IDs innerhalb des Dialogs erhalten. Jeder neu gestartete Erstellungsbefehl erzeugt weiterhin eine unabhängige Baugruppe.

## Dauerhafte Layoutskizze

Jede neue Baugruppe enthält **00 | Layout → Skizzen → FrameKit | Profilmittellinien (fixiert)**. Die räumliche Skizze enthält je Profil eine fixierte Konstruktionslinie mit den gleichen Endpunkten wie die Vorschau. Sie ist standardmäßig ausgeblendet und lässt sich im Fusion-Browser über ihre Sichtbarkeit einschalten. Zum Vergleichen können die anderen Unterbaugruppen vorübergehend ausgeblendet werden.

Die Skizze ist eine abgeleitete Darstellung. Dialogwerte und gespeicherte Konfiguration bleiben maßgeblich; manuelles Entfixieren oder Bearbeiten verändert weder die Konfiguration noch automatisch die Bauteile. Das Bearbeiten vorhandener Gestelle über den Dialog folgt erst mit S08.

Die Skizze speichert die Gestellkennung, ihre Linien speichern Bauteil-ID und Gesamtkennung. In parametrischen Dokumenten liegt ihre Erstellung in der Zeitleistengruppe **Struktur und Layout**. Auch direkte Modellierungsdokumente erhalten die Skizze, ohne Änderung des Dokumenttyps.

## Temporäre Darstellung und Fehler

Die Vorschau verwendet eine eigene Custom-Graphics-Gruppe im Dokument und erzeugt keine temporären Komponenten, Skizzen oder Volumenkörper. Die Gruppe wird beim Aktualisieren ersetzt und beim Ausschalten, Abbrechen, Ausführen oder Stoppen des Add-ins entfernt. Fehler beim Zeichnen bereinigen auch bereits erzeugte Teilgrafik. Fremde Grafikgruppen bleiben bestehen. Ein Vorschaufehler erscheint im Dialog; die normale Bauteilerstellung bleibt verfügbar, sofern die Maße gültig sind.

## Prüfstand und Fusion-Abnahme

**40 lokale Tests sowie Syntaxprüfung erfolgreich.** Abgedeckt sind unter anderem Schnittflächen-Endpunkte, Plattenflächen und Ausklinkungen, Zubehörgrenzen, identische Vorschau-/Layout-/Bauteildaten, Anzeigeoptionen, Eingabeänderungen, Abbrechen und simulierte Fehler. Die Fusion-Anbindung wird dabei mit einem vereinfachten API-Ersatz geprüft; Darstellung und Skizzenverhalten im laufenden Fusion sind noch nicht bestätigt.

In Fusion nach Neustart des Add-ins prüfen:

1. Standardgestell mit eingeschalteter Vorschau betrachten; Ansicht drehen und bei Bedarf einpassen. Länge, Breite und Profilbreite ändern. Linien müssen sofort den gültigen Werten folgen und an den Schnittflächen enden.
2. Unteren Rahmen aus-/einschalten, mehrere Böden mit leeren und festen Höhen anlegen und Füße/Rollen wählen. Flächen, Ausklinkungen und Zubehörumrisse mit den Eingaben vergleichen. Die beiden Anzeigeoptionen unabhängig schalten.
3. Ungültige Maße eingeben: alte Vorschau verschwindet und Ausführen bleibt gesperrt. Gültige Werte wiederherstellen: Vorschau erscheint erneut.
4. Mit sichtbarer Vorschau abbrechen, erneut öffnen und mehrfach ein-/ausschalten. Es dürfen keine zusätzlichen Komponenten, Skizzen, Zeitleisteneinträge oder Restgrafiken entstehen. Auch Stoppen und erneutes Starten des Add-ins prüfen.
5. Gestell erstellen: Vorschau verschwindet, Zoom passt die Ansicht ein. Layoutskizze im Browser einschalten; räumliche Linien, Fixierung und Endpunkte mit den Profilen vergleichen. Speichern, neu öffnen und standardmäßig ausgeblendete Skizze prüfen.
6. Ein weiteres Gestell im selben Dokument sowie eines im direkten Modellierungsmodus erstellen. Bestehende Baugruppen bleiben unverändert; Rückgängig entfernt jeweils die zuletzt erzeugte Baugruppe samt Layout.

API-Grundlage: [Autodesk Custom Graphics](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CustomGraphics_UM.htm).

[Demo-Anleitung](demo_installation.md) · [Bauteildaten](bauteildaten.md) · [Ablaufplan](ablaufplan.md) · [Timeline](timeline.md) · [Deutsch](../README.md) · [English](../README.en.md)
