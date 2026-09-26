# Bauart und Zubehöranordnung – S06 / 0.4.0

## Kompakter Dialog

Alle Ausklappbereiche starten geschlossen, auch Profil- und Zubehörbibliothek. Das Fenster wird mit 580 × 640 statt 580 × 800 geöffnet. Eingaben, Vorschau und Prüfung funktionieren auch bei geschlossenen Bereichen. Zum Bearbeiten nur den benötigten Bereich öffnen. Die tatsächliche Darstellung bei hoher Bildschirm-Skalierung muss in Fusion geprüft werden.

## Bauart und Eckauswahl

**Bauart** bietet Untergestell und Transportwagen. Ein bewusster Wechsel belegt das Zubehör neu:

- **Untergestell:** vier Demo-Füße, Bauhöhe 40 mm, Durchmesser 50 mm.
- **Transportwagen:** vorne zwei Demo-Lenkrollen, hinten zwei Demo-Bockrollen, jeweils Bauhöhe 100 mm und Durchmesser 75 mm; unterer Rahmen aktiviert.

Die Maße sind synthetische Demo-Vorgaben, keine Herstellerdaten. Bestehende gespeicherte Einstellungen werden beim Öffnen unverändert übernommen; alte Einstellungen ohne Zubehör bleiben ohne Zubehör. Die Werkseinstellungen bleiben ebenfalls ohne Zubehör. Weitere Maße und Boden-/Profileinstellungen werden beim Bauartwechsel beibehalten und erneut geprüft.

Unter **Füße / Rollen je Ecke** gilt die gemeinsame Auswahl für alle vier Pfosten. **Einzeln je Ecke** übernimmt zunächst die gemeinsame Auswahl und erlaubt danach getrennte Einträge vorne links, vorne rechts, hinten links und hinten rechts. Zurückschalten verwendet die gemeinsame Auswahl. Die Orientierung bleibt X = links nach rechts, Y = vorne nach hinten.

Alle Zubehörteile stehen auf Z = 0, mittig unter dem jeweiligen Pfosten. Die gespeicherte Montageposition bezeichnet den oberen Mittelpunkt am Pfosten. Die vier Bauhöhen müssen gleich sein (numerische Toleranz 0,000001 mm). Kombinationen unterschiedlicher Höhen oder einzelner leerer Ecken mit Zubehör an anderen Ecken sperren die Erstellung. Es gibt keinen automatischen Höhenausgleich und keine automatische Verkürzung einzelner Pfosten. Unterschiedliche Durchmesser sind erlaubt, solange sich die Zylinder nicht überschneiden.

Gesamthöhe, Pfostenlänge und Bodenhöhen berücksichtigen die gemeinsame Zubehörbauhöhe. Zubehörüberstände zählen weiterhin nicht zu Länge und Breite des Profilrahmens. Vorschau, Layout und Geometrie nutzen dieselben Bauteildaten.

## Zubehör anlegen, bearbeiten und duplizieren

Unter **Einstellungen verwalten → Eigene Füße und Rollen**:

1. Name, Art, eingestellte Bauhöhe und Platzhalterdurchmesser eingeben.
2. Optional Bremse, Höhenverstellung, Befestigung/Montagehinweis, Referenztyp und Betriebsstellung ergänzen.
3. **Neuen Eintrag speichern** legt einen neuen Bibliothekseintrag an. Namen müssen eindeutig sein.
4. Zum Ändern einen Eintrag auswählen und **Auswahl zum Bearbeiten laden** drücken. **Geladenen Eintrag aktualisieren** speichert Änderungen unter derselben Bibliotheks-ID. Ein späterer Wechsel der Bibliotheksauswahl ändert das geladene Bearbeitungsziel nicht.
5. **Auswahl duplizieren** erstellt eine unabhängige Kopie mit neuer ID und eindeutigem Namen „(Kopie n)“.
6. **Ausgewählten Eintrag löschen** entfernt nur den Bibliothekseintrag.

Die Darstellung bleibt ein ausdrücklich benannter Zylinderplatzhalter. Bremse, Befestigung und Betriebsstellung werden als Eigenschaften gespeichert; Rad-, Brems- und Befestigungsgeometrie wird nicht modelliert. Bremse ist nur für Rollen zulässig. Montage erfolgt mittig unter dem Pfosten; freie Montageversätze gehören nicht zu S06.

**Höhenverstellung:** Bauhöhe bezeichnet die aktuell eingestellte Gesamthöhe inklusive Befestigung. Bei aktivierter Höhenverstellung sind minimale und maximale Bauhöhe erforderlich; die eingestellte Höhe muss innerhalb dieses Bereichs liegen. Eine mechanische Verstellung oder automatische Angleichung wird nicht simuliert.

**Absenkbare Rollen:** Ein konkretes Herstellerprodukt ist bisher nicht festgelegt. Neue oder aktualisierte Einträge müssen daher einen vom Benutzer benannten Referenztyp und eine ausdrückliche Betriebsstellung enthalten, etwa „auf Rad“ oder „auf Stellfuß“. Die Bauhöhe gilt ausschließlich für diese Stellung. Es werden weder Hub noch Maße eines realen Produkts angenommen. Ältere Definitionen ohne diese Angaben bleiben lesbar; beim Aktualisieren werden die Angaben erforderlich.

## Speicherung

Bibliotheksänderungen wirken sofort, auch wenn der Erstellungsdialog anschließend abgebrochen wird. Standardwerte werden erst mit **Ausführen** und **Als Standardwerte speichern** übernommen.

Aktuelle Auswahlen, gespeicherte Standardwerte und erzeugte Baugruppen enthalten eigenständige Kopien der Zubehördefinitionen. Bearbeiten oder Löschen in der Bibliothek verändert diese nicht. Eine abweichende oder gelöschte Definition bleibt als **gespeicherter Stand** auswählbar; um einen geänderten Bibliothekseintrag zu verwenden, diesen ausdrücklich erneut auswählen. Im Gegensatz zu DXF-Profilen benötigen diese Zylinderplatzhalter keine externe Quelldatei.

Eine beschädigte Zubehörbibliothek sperrt Schreibaktionen im Dialog, bis die Datei repariert und der Dialog erneut geöffnet wurde. Werkseinstellungen löschen keine Bibliothek. Die bestehende JSON-Schemaversion bleibt kompatibel; Bauart und Eckauswahl sind zusätzliche Konfigurationsfelder.

## Prüfstand

**90 lokale Tests erfolgreich**, einschließlich gemischter Rollen, gemeinsamer Aufstandsebene, ungültiger Höhen, Platzbedarf bei verschiedenen Durchmessern, Eigenschaften, Kopien, gespeicherter Eckauswahl, Bibliotheksänderungen, Schreibfehlern und Dialogereignissen. Syntax und Versionsgleichstand sind geprüft.

**0.3.1 funktioniert laut Benutzerrückmeldung vom 26.09.2026. Auch 0.4.0 läuft laut Benutzerrückmeldung vom 26.09.2026 ohne Fehler.**

1. Dialog auf dem verwendeten Monitor öffnen: alle Gruppen geschlossen, Ausführen/Abbrechen erreichbar; auch Windows-Skalierung prüfen.
2. Transportwagen wählen, Vorschau aktivieren und erstellen: zwei Lenkrollen vorne, zwei Bockrollen hinten; Zylinderhöhen 100 mm, Gesamthöhe unverändert.
3. Einzelne Ecken ändern: andere Durchmesser bei gleicher Bauhöhe zulassen, andere Bauhöhen und eine leere Ecke ablehnen.
4. Höhenverstellbaren Fuß mit gültigem Bereich anlegen; Werte außerhalb des Bereichs ablehnen. Absenkbare Rolle ohne Referenz/Stellung ablehnen.
5. Zubehör laden, bearbeiten, aktualisieren und duplizieren; ursprüngliche Auswahl bleibt unverändert. Geänderten Eintrag bewusst auswählen und neue Baugruppe erzeugen.
6. Standardwerte mit gemischten Rollen speichern und Dialog erneut öffnen. Bibliothekseintrag ändern/löschen: gespeicherter Stand und bestehende Gestelle bleiben erhalten.
7. Werkseinstellungen, Abbrechen, Rückgängig und mehrere Gestelle prüfen.

[Ablaufplan](ablaufplan.md) · [Installation](demo_installation.md) · [Deutsche README](../README.md) · [English README](../README.en.md)
