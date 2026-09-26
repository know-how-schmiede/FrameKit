# Vorhandenes Gestell bearbeiten – S08 / 0.5.2

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

Der Austausch läuft im Ausführen-Ereignis eines Fusion-Befehls. Erst wenn die neue Geometrie samt Attributen und Zeitleistengruppen vollständig erstellt ist, wird das alte Gestell entfernt. Im parametrischen Dokument erfolgt dies über ein **Remove-Feature**, sodass die bisherige Historie erhalten bleibt. Im Direktmodell wird das alte Vorkommen am Ende gelöscht. Ein Fehler setzt `executeFailed`, wodurch Fusion die Befehlstransaktion abbricht. Änderungen an gespeicherten Daten oder der Hauptbaugruppenposition zwischen Laden und Ausführen werden erkannt.

**Rückgängig** soll den gesamten Bearbeitungsschritt einschließlich Entfernung des alten Gestells zurücknehmen; **Wiederholen** soll ihn erneut anwenden. Die Historie parametrischer Dokumente wächst beim Neuaufbau bewusst weiter.

API-Grundlagen: [Transaktion bei executeFailed abbrechen](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_CommandEventArgs_executeFailed.htm), [RemoveFeatures.add](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_RemoveFeatures_add.htm), [Position und Orientierung über transform2](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_Occurrence_transform2.htm).

## Prüfstand

**131 lokale Tests erfolgreich.** Neue Prüfungen umfassen Konfigurationsmigration, Schemafehler, eingebettete DXF-Daten, ID-Erhaltung, Auswahl mehrerer Gestelle, verschobene/gedrehte Vorschau, Abbrechen, Sichtbarkeitswiederherstellung, fehlgeschlagenen Aufbau und Schutz fremder Komponenten. Fusion-API-Ereignisse und Geometrieadapter werden dabei durch Testobjekte ersetzt.

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
