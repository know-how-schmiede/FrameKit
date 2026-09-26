# Querträger und Deckplattenmontage – 0.2.1

Aktualisierung vom 26.09.2026: Die Versionen 0.2.0, 0.2.1 und 0.3.0 funktionieren laut Benutzerprüfung. Ab 0.3.1 gelten zusätzlich [getrennte Profilwahl und rechteckige Querschnitte](profile_je_bauteilgruppe.md); deren Fusion-Prüfung steht noch aus. Die folgenden Angaben beschreiben den jeweiligen ursprünglichen Versionsumfang.

S03 ergänzt je vorhandener Ebene zwei Auswahlfelder: **Anzahl 0–5** (0 deaktiviert die Träger) und **Ausrichtung Quer/Längs**. Oben, optional unten und jeder Zwischenboden lassen sich unabhängig konfigurieren. Die Schaltfläche **Für alle Ebenen übernehmen** kopiert die beiden gemeinsamen Auswahlwerte einmalig auf alle aktuell vorhandenen Ebenen. Anschließend sind einzelne Abweichungen möglich. Neu eingeblendete Ebenen beginnen mit 0 Trägern; im selben Dialog zuvor ausgeblendete Ebenen behalten ihre Auswahl.

Quer verläuft vorne–hinten (Y), Längs links–rechts (X). Die Träger verwenden das Rahmenprofil, schließen oben bündig mit dem Rahmen ab und enden an dessen inneren Flächen. Bei lichter Verteilbreite `D`, Profilbreite `p` und Anzahl `n` beträgt jedes freie Feld `(D - n*p)/(n+1)`. Sind bei gewählter Anzahl keine positiven freien Felder möglich, verhindert eine Fehlermeldung Vorschau und Erstellung.

Die Auswahl **Deckplatte** bietet:

- **Zwischen Pfosten (mit Aussparungen):** bisherige Bauart; Pfosten und Platte enden auf der eingegebenen Gesamthöhe.
- **Auf Profilen (ohne Aussparungen):** durchgehende rechteckige Deckplatte über dem Rahmen und den Pfosten. Die Pfosten enden eine Plattenstärke unter der Gesamthöhe. Pfostenlänge = Gesamthöhe − Zubehörhöhe − Plattenstärke.

Die Gesamthöhe bleibt in beiden Fällen die fertige Höhe ab Aufstandsfläche einschließlich Füßen/Rollen und Deckplatte. Der obere Rahmen liegt weiterhin direkt unter der Platte. Untere und Zwischenbodenplatten behalten ihre Pfostenaussparungen. Beispiel: 750 mm Gesamthöhe, 100 mm Zubehörhöhe, 18 mm Platte ergeben bei Montage auf Profilen 632 mm Pfostenlänge.

Alle Einstellungen werden beim Speichern der Standardwerte und in den Baugruppendaten abgelegt. Alte Einstellungen erhalten 0 Querträger und die bisherige ausgeklinkte Deckplatte. Querträger besitzen stabile Bauteil-IDs, Zuschnittlängen und Mittellinien; Vorschau und fixierte Layoutskizze verwenden dieselben Daten.

## Prüfung

46 lokale Tests prüfen unter anderem 0–5 Träger in beiden Richtungen auf allen Ebenen, gleiche freie Felder, Anschlussmaße, enge Rahmen, beide Deckplattenkonturen, Zubehörhöhen, ID-Stabilität, Speichern/Laden sowie Dialogübernahme und Einzelabweichungen.

Fusion-Prüffälle (Version 0.2.1 laut Benutzerprüfung vom 26.09.2026 funktionsfähig):

1. Oben, unten und zwei Zwischenböden anlegen; 0, 1 und 5 Träger sowie beide Richtungen ausprobieren. Freie Felder und bündige Anschlüsse messen.
2. Werte auf alle Ebenen übernehmen, einzelne Ebene ändern; unteren Rahmen und Zwischenböden aus-/einblenden und Werkseinstellungen laden.
3. Beide Deckplattenmontagen mit und ohne Füße/Rollen erstellen. Gesamthöhe, Pfostenlänge, Aussparungen und Auflage kontrollieren.
4. Vorschau mit Bodenflächen und gespeicherte Layoutskizze mit der fertigen Geometrie vergleichen; Standardwerte speichern und erneut laden.
5. Zu enge Rahmen eingeben: verständliche Fehlermeldung und keine Erstellung.
