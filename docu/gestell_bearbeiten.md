# Vorhandenes Gestell bearbeiten – S08 / 0.5.4

Unter **Volumenkörper → Erstellen → FrameKit: Gestell bearbeiten** kann eine gespeicherte FrameKit-Hauptbaugruppe im aktiven Dokument ausgewählt werden. Der bisherige FrameKit-Befehl erstellt weiterhin neue, unabhängige Gestelle.

## Bedienung

1. **Gestell bearbeiten** öffnen, das gewünschte Gestell in der Liste wählen und **Gestell laden** anklicken. Bei mehreren Gestellen unterscheiden Listenposition und Baugruppenname die Einträge.
2. Abmessungen, Profile, Drehungen, Ebenen, Querträger, Zubehör und Winkel wie beim Erstellen ändern. Der Dialog lädt die gespeicherte Konfiguration des gewählten Gestells, keine persönlichen Standardwerte.
3. **Vorschau anzeigen** aktivieren. Das bisherige Gestell wird während der Vorschau ausgeblendet; die neue Vorschau berücksichtigt seine Position und Drehung im Dokument. Andere Gestelle werden nicht ausgeblendet. Beim Ausschalten, bei ungültiger Vorschau oder beim Abbrechen wird die ursprüngliche Sichtbarkeit wiederhergestellt.
4. **Neu aufbauen** erzeugt den neuen Stand vollständig und ersetzt anschließend das ausgewählte Gestell. Die Ansicht wird auf das bearbeitete Gestell eingepasst. **Abbrechen** erhält das bisherige Gestell.

Bibliotheksaktionen im Einstellungsreiter speichern weiterhin sofort und werden durch Abbrechen des Gestelldialogs nicht rückgängig gemacht. Persönliche Standardwerte werden nur mit der entsprechenden Option gespeichert.

## Erhaltene Daten und Grenzen

- Gestellkennung und Bauteil-IDs bleiben anhand ihrer fachlichen Rollen erhalten. Neue Rollen erhalten neue IDs, entfallene bleiben reserviert. Änderungen der Bodenanzahl ergänzen oder entfernen obere Ebenen; das Einfügen/Löschen einer einzelnen mittleren Ebene ist nicht vorgesehen.
- Die gespeicherten DXF-Konturen und Zubehördefinitionen werden geladen. Ein in der Bibliothek gelöschtes Profil bleibt beim Bearbeiten aus seinem eingebetteten Stand verwendbar. Neu gewählte Bibliotheksprofile werden wie bisher einschließlich Quelldatei geprüft.
- Konfigurationsschema **1** und Bauteilschema **1** bleiben gültig. Frühere `demoConfiguration`-Daten werden um damalige Standardoptionen ergänzt. Alte Gestelle erhalten beim bloßen Laden keine zusätzlichen Winkel. Ohne historische ID-Zuordnung werden neue Bauteil-IDs vergeben; eine vorhandene Gestellkennung bleibt erhalten. Unbekannte Schemata oder widersprüchliche Daten werden mit einer Meldung abgelehnt.
- Position und Drehung der Hauptbaugruppe sowie deren Sichtbarkeit bleiben erhalten. Manuelle Änderungen an generierten Teilen, Materialien, Untergruppen-Sichtbarkeiten oder deren Geometrie werden beim Neuaufbau ersetzt. Externe Flächenreferenzen und Gelenke werden nicht neu zugeordnet.
- Andere Hauptbaugruppen bleiben unverändert. Zusätzlich eingefügte fremde Komponenten innerhalb des gewählten Gestells blockieren den Neuaufbau; sie müssen vorher außerhalb des Gestells abgelegt werden. Verknüpfte oder mehrfach verwendete Gestellkomponenten werden ebenfalls abgelehnt. Die Auswahl umfasst Hauptbaugruppen direkt unter der Dokumentwurzel.

## Austausch und Rückgängig

Der Austausch läuft im Ausführen-Ereignis eines Fusion-Befehls. Erst wenn die neue Geometrie samt Attributen und Zeitleistengruppen vollständig erstellt ist, wird das alte Gestell entfernt. Das alte Vorkommen wird in parametrischen Dokumenten und Direktmodellen über **deleteMe** gelöscht. Damit wird auch die zugehörige alte Komponentenhistorie entfernt, statt einen weiteren Remove-Schritt anzuhängen. Externe Referenzen auf die gelöschte Geometrie können dabei verloren gehen. Ein Fehler setzt `executeFailed`, wodurch Fusion die Befehlstransaktion abbricht. Änderungen an gespeicherten Daten oder der Hauptbaugruppenposition zwischen Laden und Ausführen werden erkannt.

**Rückgängig** soll den gesamten Bearbeitungsschritt einschließlich Entfernung des alten Gestells zurücknehmen; **Wiederholen** soll ihn erneut anwenden. Künftige Bearbeitungen behalten nur die Konstruktion des aktuellen Gestells. Bereits durch frühere Bearbeitungen angesammelte Remove-Historie wird nicht rückwirkend bereinigt. Die native Prüfung von Historienbereinigung sowie Rückgängig/Wiederholen steht noch aus.

API-Grundlagen: [Transaktion bei executeFailed abbrechen](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_CommandEventArgs_executeFailed.htm), [Occurrence.deleteMe](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Occurrence_deleteMe.htm), [Position und Orientierung über transform2](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Occurrence_transform2.htm).

## Prüfstand

**133 lokale Tests erfolgreich.** Neue Prüfungen umfassen Konfigurationsmigration, Schemafehler, eingebettete DXF-Daten, ID-Erhaltung, Auswahl mehrerer Gestelle, verschobene/gedrehte Vorschau, Abbrechen, Sichtbarkeitswiederherstellung, fehlgeschlagenen Aufbau und Schutz fremder Komponenten. Fusion-API-Ereignisse und Geometrieadapter werden dabei durch Testobjekte ersetzt.

**Die praktische Prüfung in Fusion ist offen**, insbesondere:

1. 0.4.4-Gestell laden, Maße ändern, Vorschau prüfen, neu aufbauen und erneut laden.
2. Zweites Gestell sowie fremde Hauptbaugruppe im Dokument lassen: nur das ausgewählte Gestell darf ersetzt werden.
3. Verschobenes und gedrehtes Gestell prüfen; Vorschau und Neuaufbau müssen dieselbe Lage besitzen.
4. Vorschau öffnen und abbrechen: ursprüngliche Geometrie und Sichtbarkeit müssen wiederhergestellt sein.
5. Ungültige Maße und fehlgeschlagenen Neuaufbau prüfen: bisheriges Gestell muss erhalten bleiben.
6. Nach erfolgreichem Neuaufbau **Rückgängig** und **Wiederholen** prüfen, sowohl parametrisch als auch im Direktmodell. Diese native Transaktionsprüfung ist lokal nicht ersetzbar.
7. Profile/Bibliothek entfernen, gespeichertes Gestell öffnen und mit eingebetteten Konturen bearbeiten; unbekannte Altstände und fremde Unterkomponenten auf verständliche Fehlermeldungen prüfen.

[Ablaufplan](ablaufplan.md) · [Installation](demo_installation.md)

## Dialogkorrektur 0.5.1

Der in Fusion gemeldete leere Bearbeitungsdialog wird durch einen durchgängigen Reiteraufbau adressiert. Alle drei Reiter werden beim Öffnen angelegt; die Auswahl befindet sich im ersten Reiter. Beim Laden werden die vorhandenen Reiter befüllt, ohne alte CommandCreated-Ereignisargumente erneut zu verwenden. Die Auswahl wird erst nach erfolgreichem Aufbau ausgeblendet. Fehler bleiben sichtbar und verhindern den Neuaufbau. Nach dem Update das Add-in neu starten und besonders **Gestell bearbeiten → Gestell laden** prüfen; Der Benutzer hat den Dialogaufbau inzwischen bestätigt.

## Vorschaukorrektur 0.5.2

Trotz aktivierter Vorschau wurde keine Grafik angezeigt. FrameKit fordert die Vorschau nun beim Einschalten und nach gültigen Eingabeänderungen ausdrücklich mit [Command.doExecutePreview](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Command_doExecutePreview.htm) an. Status-, Gruppen- und Reiterereignisse sowie verschachtelte Rückrufe während des Renderns entfernen die Grafik nicht. Eine abgelehnte native Vorschauanforderung wird im Vorschauabschnitt gemeldet. Nach Neustart mit einem geladenen Gestell Einschalten, Maßänderung, Ausschalten und Abbrechen prüfen. Die Bestätigung dieser Korrektur in Fusion steht noch aus.

## Ereigniskorrektur 0.5.3

0.5.2 zeigte beim Benutzer weiterhin keine Vorschau. Die im Screenshot deaktivierten Unteroptionen trotz gesetzter Vorschau deuten auf nicht verarbeitete Änderungsereignisse hin. Der Bearbeitungsbefehl registriert nun alle nativen Handler beim Öffnen; nach dem Laden erfolgt nur die Weiterleitung an die Editor-Callbacks. Die nachträgliche Handlerregistrierung innerhalb von inputChanged entfällt. Nach Aktualisierung und Neustart **Gestell bearbeiten → Gestell laden → Vorschau anzeigen** prüfen: Unteroptionen müssen aktiv werden, das ursprüngliche Gestell ausgeblendet und die Vorschau sichtbar werden. Abbrechen muss das Original wiederherstellen. Fusion-Bestätigung offen.

## Vorschaukorrektur 0.5.4

Die Rückmeldung zu 0.5.3 zeigt: Die Grafik existiert, ist aber vom Original verdeckt und bleibt nach Maßänderungen statisch. Der Dialog legt jetzt auch sämtliche Editorfelder beim Öffnen an. **Gestell laden** setzt nur Werte, Auswahlen und Sichtbarkeiten der vorhandenen Felder. Das Original wird vor der Vorschauanforderung ausgeblendet und bei reinen Grafikaktualisierungen nicht wieder eingeblendet. Bei ausgeschalteter/ungültiger Vorschau, Fehlern und Abbrechen wird seine ursprüngliche Sichtbarkeit wiederhergestellt.

Nach Aktualisierung und Neustart prüfen: Gestell laden, Vorschau aktivieren, Länge nacheinander auf 900, 300 und 750 mm ändern. Das Original darf nicht manuell ausgeblendet werden müssen; die Vorschau muss jeweils ihre Form ändern. Danach Vorschau ausschalten und Abbrechen prüfen. Native Fusion-Bestätigung offen.

### Winkel ohne Konstruktionshistorie – Nachkorrektur 0.7.0

Der Benutzer meldete verschobene Winkel nach Änderungen im Direktmodus. Dort werden die gemeinsam verwendeten STEP-Winkel nun im Ursprung aufgebaut und erst danach als Vorkommen positioniert. Eine Verschiebung oder Drehung des gesamten Gestells wird zuletzt angewendet. Der Weg mit Konstruktionshistorie bleibt unverändert. Lokal sind wiederholter Neuaufbau, einzelne Winkelpositionen/-orientierungen und eine gedrehte/verschobene Baugruppe geprüft; die native Fusion-Bestätigung steht noch aus.

Prüfung: Add-in neu laden, betroffenes Gestell über „Gestell bearbeiten“ neu aufbauen, danach Länge/Breite erneut ändern und alle Winkel kontrollieren. Zusätzlich ein verschobenes/gedrehtes Gestell ohne Historie prüfen.

Nach dem gemeldeten `transform2`-Fehler werden die Winkel im Direktmodus über Vorkommen-Proxys mit vollständigem Kontext bis zur Dokumentwurzel positioniert. Direkte Transformationsänderungen an verschachtelten nativen Vorkommen sind im Test nun ausdrücklich gesperrt. Die Korrektur bleibt in Version 0.7.0; Bestätigung in Fusion steht aus.

**Aktueller Stand nach erneutem Benutzerbericht:** Die Proxy-Variante wurde für den Direktmodus abgelöst. Jeder Winkel erhält eine unabhängige STEP-Körperkopie, die vor dem Einfügen in Gestellkoordinaten transformiert wird. Die Vorkommen bleiben ohne eigenen Positionsversatz; die Hauptbaugruppe wird abschließend platziert. „91 | Winkel“ bleibt gemeinsam schaltbar. Nur im parametrischen Modus teilen Winkel weiterhin eine Komponentendefinition. 144 lokale Tests erfolgreich; Sichtbarkeit und Position in Fusion noch zu bestätigen.

**Benutzerbestätigung:** Die abschließende Korrektur mit unabhängigen STEP-Körperkopien funktioniert im Direktmodus. Winkel nach dem Neuaufbau ohne Konstruktionshistorie sind damit vom Benutzer bestätigt. Version unverändert 0.7.0.
