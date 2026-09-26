# Profile je Bauteilgruppe – S05 / 0.3.1

## Auswahl und Drehung

Das gemeinsame Profil bleibt der Standard. Unter **Profile je Bauteilgruppe** können Pfosten, Rahmen und Querträger jeweils ein eigenes DXF-Profil erhalten. **Übernehmen** verwendet das gemeinsame Profil. Einträge stammen aus der bestehenden lokalen DXF-Bibliothek; auch rechteckige Querschnitte sind jetzt zulässig. Der Mittelpunkt der Außenmaße muss weiterhin im Ursprung liegen.

Die Profildrehung lässt sich gemeinsam oder je Gruppe auf **0°, 90°, 180° oder 270°** einstellen. Profilwahl und Drehung werden unabhängig übernommen. Bei Pfosten liegt in Grundstellung DXF-X entlang Gestell-X und DXF-Y entlang Gestell-Y. Bei Längsträgern liegt DXF-X entlang Gestell-Y, DXF-Y nach oben; bei Querträgern entlang Gestell-X beziehungsweise nach unten. Positive Drehungen erfolgen um die lokale Extrusionsachse (Pfosten +Z, Längsträger +X, Querträger +Y). Die importierte Kontur bleibt unverändert, einschließlich Nuten und Hohlräumen.

Jede Rahmen-/Bodenebene bietet zusätzlich Profilwahl und Drehung für ihre Querträger. Hier übernimmt **Übernehmen** die Auswahl der Querträgergruppe. **Für alle Ebenen übernehmen** kopiert Anzahl, Laufrichtung, Profilwahl und Profildrehung auf alle gerade vorhandenen Ebenen. Anschließend sind einzelne Ebenen wieder unabhängig einstellbar. Die Laufrichtung Quer/Längs und die Drehung des Querschnitts sind getrennte Einstellungen.

## Maßregeln

- Länge und Breite bleiben Außenmaße. Pfosten belegen ihre gedrehten tatsächlichen X-/Y-Maße; die Eckausklinkungen der Platten folgen diesen Maßen.
- Rahmenprofile liegen außen bündig zwischen den Pfosten. Ihre horizontale Breite darf keines der Pfostenmaße überschreiten, da sonst die Rahmenprofile an den Ecken kollidieren würden. Eine entsprechende Fehlermeldung fordert eine andere Profilwahl oder Drehung.
- Rahmen und Querträger enden oben an derselben Plattenunterseite. Unterschiedliche Querschnittshöhen werden nach unten ausgeglichen; es entsteht keine Stufe in der Plattenauflage.
- Querträger laufen zwischen den inneren Rahmenflächen. Ihre tatsächliche Breite wird bei der Verteilung gleich großer freier Felder berücksichtigt. Kollisionen mit den Pfosten werden abgelehnt.
- Für freie Bodenabstände zählt je Ebene die größere Höhe von Rahmen und vorhandenen Querträgern plus Plattenstärke. Auch die Unterkante der untersten Ebene bleibt oberhalb der Aufstandsfläche beziehungsweise Zubehörbauhöhe. Überlappende oder zu niedrige Ebenen werden abgelehnt.
- Zubehör bleibt unter den tatsächlichen Pfostenmittelpunkten. Bei aufliegender Deckplatte enden die Pfosten an der Plattenunterseite; die Gesamthöhe bleibt unverändert.

Bauteildaten enthalten Profilreferenz, Profildrehung, Transformation, Zuschnittlänge und äußere Begrenzung. Vorschau, Layout und Bauteilerstellung nutzen dasselbe Modell. Die gespeicherten Standardwerte und Baugruppen enthalten alle verwendeten Profildefinitionen als eigenständige Kopien. Alte Einstellungen ohne Gruppenwahl verwenden weiterhin das gemeinsame Profil. Fehlende Bibliothekseinträge bleiben im Dialog sichtbar und sperren die Neuerstellung, bis eine verfügbare Auswahl getroffen wird.

## Prüfung

**Lokal:** 82 Tests erfolgreich, darunter synthetische Hohlprofile 40 × 80, 20 × 40 und 30 × 60 mm. Geprüft sind gedrehte Außenmaße, Schnittflächen, Aussparungen, kollisionsfreie Profilkörper, gleiche freie Felder, bündige Auflagen, variable Ebenenhöhen, gespeicherte Auswahl, ID-Stabilität und Dialogereignisse. Synthetische Testprofile sind keine Herstellerprofile.

**Fusion:** Die Versionen 0.2.0, 0.2.1 und 0.3.0 funktionieren laut Benutzerrückmeldung vom 26.09.2026. Auch **0.3.1** funktioniert laut Benutzerrückmeldung vom 26.09.2026. Prüffälle zur Nachvollziehbarkeit:

1. Zwei oder mehr unterschiedliche quadratische/rechteckige DXF-Profile importieren und Pfosten, Rahmen sowie Querträgern zuweisen.
2. Pfosten und Träger um 90° drehen, zusätzlich bei asymmetrischen Nuten 180°/270° vergleichen. Außenmaße und Lage der Konturen messen.
3. Querträger in beiden Laufrichtungen je Ebene variieren und auf alle Ebenen übernehmen. Freie Felder und Kontakt zur Plattenunterseite prüfen.
4. Mehrere Böden mit automatischen und festen Höhen sowie beide Deckplattenmontagen erstellen. Aussparungen, Gesamtmaß und Zubehörzentrierung prüfen.
5. Zu enge Maße und überlappende Höhen eingeben; Erstellung muss mit verständlichem Hinweis gesperrt sein.
6. Standardwerte speichern, Dialog erneut öffnen, Profilzuordnungen und Drehungen prüfen. Ein verwendetes Bibliotheksprofil löschen: bestehendes Gestell bleibt erhalten, Neuerstellung fordert eine verfügbare Auswahl.

[Ablaufplan](ablaufplan.md) · [DXF-Bibliothek](profilbibliothek_dxf.md) · [Deutsche README](../README.md) · [English README](../README.en.md)
