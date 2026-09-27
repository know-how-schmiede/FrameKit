# Stückliste – S10 / 0.7.2

Unter **Volumenkörper → Erstellen → FrameKit: CSV-Listen exportieren** ein gespeichertes Gestell auswählen. Im Feld **Listen** stehen **Zuschnittliste**, **Stückliste** und **Beide Listen** zur Verfügung. Die Zuschnittliste bleibt vorausgewählt. Deutsch: Semikolon/Dezimalkomma; International: Komma/Dezimalpunkt. Beide Formate verwenden UTF-8 mit BOM und maximal drei Nachkommastellen in mm.

Bei „Beide Listen“ nacheinander zwei verschiedene CSV-Zielpfade wählen. Erst nach Bestätigung beider Speicherdialoge werden Dateien geschrieben. Abbrechen eines Dialogs schreibt nichts. Alle Inhalte werden zunächst in temporären Dateien vorbereitet. Scheitert das Ersetzen einer Zieldatei, werden bereits ersetzte Dateien wiederhergestellt; bei einem zusätzlichen Wiederherstellungsfehler nennt die Fehlermeldung die erhaltenen Sicherungsdateien.

Die Stückliste enthält:

- Profile: Hersteller, Serie, Artikelnummer, Bezeichnung, Zuschnittlänge, Menge, Endbearbeitung und Bauteil-IDs, ergänzt um Querschnitt, Material und Definitions-ID.
- Platten: Außenmaße, Stärke und jede Eckausklinkung mit Ecke und Abmessungen. Aufliegende Deckplatten ohne Ausklinkung bleiben von ausgeklinkten Platten getrennt. Nicht festgelegtes Material ist gekennzeichnet.
- Füße/Rollen: gespeicherte Zubehördefinition, Höhe, Durchmesser und Menge. Gleiche Namen unterschiedlicher Definitionen bleiben getrennt. Die Geometrie ist ausdrücklich als Platzhalter bezeichnet.
- Winkel: STEP-Definition, Größe und tatsächlich platzierte Menge, unabhängig davon, ob die Geometrie im Direktmodus oder mit Historie erzeugt wurde.

Die Spalten beginnen mit Hersteller, Serie, Artikelnummer, Bezeichnung, Länge, Menge, Endbearbeitung und Bauteil-IDs. Danach folgen Art, Breite, Stärke/Höhe, Durchmesser, Eckausklinkungen, Material, Definitions-ID, Gestell-ID, Status und Definition. Die letzte Spalte enthält die relevanten Definitionseigenschaften als JSON.

**Keine vollständige Befestigungsbestellung:** Schrauben, Muttern und weitere Befestigungszuordnungen sind noch nicht definiert. Ein eigener Hinweis in der CSV benennt diese Lücke, auch wenn die optionalen Winkel ausgeschaltet sind. Warnungen für nicht platzierte oder nicht zuordenbare Winkel werden ebenfalls exportiert. S10 weist alle definierten Bauteile aus, erfindet aber keine fehlenden Verbindungsteile.

Wie bei der Zuschnittliste stammen die Angaben aus den gespeicherten FrameKit-Einstellungen und Bauteildaten. Manuelle Geometrieänderungen werden nicht vermessen. Änderungen vorher mit „Neu aufbauen“ übernehmen.

## Geplant: Preise und erste Kostenschätzung (Z05)

Benutzerauftrag vom 27.09.2026: **Für die nächste Änderung vorgesehen, noch nicht implementiert**; siehe [Z05 im Ablaufplan](ablaufplan.md). Preise sind freiwillige Angaben für eine erste, unverbindliche Kostenschätzung.

| Bauteil | Preiseingabe | Berechnung je Stücklistenposition |
| --- | --- | --- |
| Profil | €/m je Profildefinition | Zuschnittlänge in mm / 1000 × Stückzahl × Preis je Meter |
| Rolle oder Fuß | €/Stück je Zubehördefinition | Stückzahl × Preis je Stück |

Beispiel: Vier Profile à 850 mm zu 12 €/m ergeben 40,80 €. Vier Rollen zu 15 €/Stück ergeben 60,00 €. Die Summe dieser bepreisten Positionen beträgt 100,80 €.

Geplanter Umfang:

- Optionale Preisfelder beim Anlegen und Bearbeiten von Profilen, Rollen und Füßen. Leer bedeutet „Preis fehlt“, nicht 0 €. Ein ausdrücklich eingetragener Preis von 0 € bleibt davon unterscheidbar; negative oder ungültige Preise sind unzulässig.
- Die Stückliste und ihr CSV-Export enthalten Preisbasis (€/m oder €/Stück), Einheitspreis, Positionskosten und eine Summe der bepreisten Positionen in EUR. Geldbeträge werden auf zwei Nachkommastellen ausgegeben; Positionskosten erst nach Multiplikation runden, die Summe aus den gerundeten Positionskosten bilden.
- Bei fehlenden Preisen bleiben Kostenfelder leer und der Status benennt die fehlende Preisangabe. Sind Positionen unbepreist, ist die Summe ausdrücklich unvollständig. Dies betrifft auch bislang nicht bepreiste Platten, Winkel und weitere Teile.
- Preisstände werden mit den verwendeten Definitionen im Gestell gespeichert und in Standardwerten, Vorlagen und Datensicherungen erhalten. Eine spätere Preisänderung in der Bibliothek verändert gespeicherte Gestelle nicht automatisch. Alte Daten ohne Preise bleiben verwendbar. Positionen mit verschiedenen Preisständen dürfen nicht stillschweigend zusammengefasst werden.
- Die Ausgabe trägt den Hinweis **„Erste unverbindliche Kostenschätzung auf Basis der hinterlegten Preise; keine vollständigen Beschaffungskosten.“** Profilkosten beruhen auf Zuschnittlängen, ohne automatische Zuschläge für Verschnitt, Lagerstangen, Bearbeitung, Versand oder Montage. Es erfolgt keine automatische Steuerberechnung; die eingegebenen Preise müssen auf einer einheitlichen Netto- oder Bruttobasis beruhen.

## Startverhalten in 0.7.2

Benutzerbericht: Fusion stürzt beim automatischen Laden von FrameKit ab, deaktiviert das Add-in und läuft nach erneutem manuellen Aktivieren normal. Der Benutzer hat einen Fehlerbericht an Autodesk gesendet. Die Ursache ist nicht abschließend nachgewiesen.

Bisher importierte `run` sofort die drei STEP-Winkel in temporäre Dokumente. Beim automatischen Start wartet FrameKit nun auf `Application.startupCompleted`; erst danach werden die Winkel importiert und Befehle registriert. Bei manueller Aktivierung nach abgeschlossenem Fusion-Start wird sofort initialisiert. Stoppen entfernt einen noch wartenden Handler. Das Fusion-Protokoll enthält Meldungen zum Warten sowie Beginn und Ende der FrameKit-Initialisierung.

API-Grundlagen: [isStartupComplete](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Application_isStartupComplete.htm), [Autodesk-Anwendungsereignisse](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ApplicationEventSample_Sample.htm).

## Prüfstand

**Benutzerbestätigung zu 0.7.2:** Der Export hat funktioniert und Fusion stürzt beim Start nicht mehr ab. Export und Startkorrektur sind damit in Fusion bestätigt; einzelne Sonderfallprüfungen wurden nicht separat bestätigt.

154 lokale Tests erfolgreich: unter anderem Mengen und IDs aller Bauteile, Platten mit/ohne Ausklinkungen, gleichnamiges Zubehör mit unterschiedlichen IDs, Änderungen der Abmessungen, CSV-Formate, Warnungen, Abbrechen bei der zweiten Datei, Wiederherstellung nach Schreibfehler sowie automatischer/manueller Add-in-Start. Keine Ausführung im nativen Fusion-Laufzeitkontext.

Ergänzende Prüffälle (nicht einzeln bestätigt): Stückliste eines Gestells mit Zwischenboden, Rollen und Winkeln exportieren und Mengen nachzählen; danach Maße ändern und erneut vergleichen. Beide CSV-Formate in Calc öffnen. Den Export beider Listen und Abbrechen prüfen. Fusion mit aktiviertem automatischem Add-in-Start neu starten und auf den gemeldeten Absturz prüfen. Falls er wieder auftritt, die neuen FrameKit-Initialisierungsmeldungen und den Autodesk-Fehlerbericht zur Eingrenzung heranziehen.
