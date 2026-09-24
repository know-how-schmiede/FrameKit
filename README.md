![FrameKit – Parametrische Gestelle für Autodesk Fusion](images/FrameKit-GitHub-Banner.png)

# FrameKit

**Deutsch** | [English](README.en.md)

FrameKit ist ein geplantes Add-in für Autodesk Fusion, das aus Dialogeingaben ein verschraubtes Untergestell oder einen einfachen Transportwagen aus Alu-Nutprofilen erzeugt. Vor der Bauteilerstellung lässt sich die Konstruktion anhand einer räumlichen Mittellinien-Vorschau prüfen.

## Projektstatus

Die Integrationsdemo (**0.1.2**) liegt unter [`fusion_addin/FrameKit`](fusion_addin/FrameKit) vor. Sie bietet drei Dialogreiter, speicherbare Standardwerte und die Erstellung eines einfachen Gestells aus Rechteckprofilen mit optionalen Zwischenböden und anschließendem „Zoom auf alles“. Bodenanzahl, Einzelhöhen und Plattenstärke sind einstellbar; leere Höhen werden gleichmäßig verteilt. Zum Laden und Testen sowie zum aktuellen Prüfstand siehe [Demo-Anleitung](docu/demo_installation.md). Die folgenden Funktionen beschreiben den geplanten vollständigen Umfang.

## Geplanter Funktionsumfang

- **Gestelle und Transportwagen:** Vier durchgehende Eckpfosten, ein oberer Rahmen und ein optionaler unterer Rahmen mit verschraubten Verbindungen.
- **Konfigurierbare Abmessungen:** Länge, Breite und Gesamthöhe sowie gemeinsame oder unterschiedliche Profile für Pfosten und Träger.
- **Zwischenböden und Querträger:** Bodenebenen mit Platten und umlaufendem Tragrahmen; Querträger werden unter Berücksichtigung ihrer Breite gleichmäßig verteilt.
- **Füße und Rollen:** Feste oder höhenverstellbare Füße, Lenkrollen mit optionaler Bremse, Bockrollen und absenkbare Rollen nach einem noch festzulegenden Referenztyp.
- **Erweiterbare Profilbibliothek:** Eigene DXF-Querschnitte mit Metadaten wie Hersteller, Serie, Artikelnummer, Nutgröße, Material und kompatiblen Verbindungssätzen – ohne Programmänderung. Importprüfungen kontrollieren Maßstab, geschlossene Konturen und Hohlräume.
- **3D-Vorschau und Eingabeprüfung:** Profilmittellinien mit Enden an den tatsächlichen Schnittflächen; ungültige Eingaben verhindern die Erstellung und werden verständlich erklärt.
- **Strukturierte Fusion-Baugruppen:** Jedes Profil erhält eine eigene Komponente mit stabiler ID, aussagekräftigem Namen, Bauteileigenschaften und benannten Zeitleistengruppen.
- **Gespeicherte Konfiguration:** Gestelle lassen sich über den Dialog erneut öffnen und kontrolliert neu aufbauen.
- **CSV-Export:** Gruppierte Zuschnittlisten mit Profil, Länge, Menge und Bauteil-IDs sowie Stücklisten einschließlich Platten, Füßen, Rollen und definierten Verbindungssätzen.

## Vorgesehener Ablauf

1. Bauart wählen und Abmessungen, Profile, Böden, Querträger sowie Füße oder Rollen konfigurieren.
2. Mittellinien-Vorschau anzeigen und die Konstruktion prüfen.
3. Gestell als strukturierte Fusion-Baugruppe erzeugen.
4. Bei Bedarf die gespeicherte Konfiguration bearbeiten und das Gestell neu aufbauen.
5. Zuschnitt- und Stücklisten als CSV exportieren.

Vorschau, Bauteilerstellung und Listen sollen dieselben berechneten Bauteildaten verwenden. Die Berechnungslogik wird von der Fusion-Geometrieerstellung getrennt.

## Konstruktionsregeln und Grenzen der ersten Version

Länge und Breite bezeichnen die Außenmaße des Profilrahmens; Rollenüberstände zählen nicht dazu. Die Gesamthöhe reicht von der Aufstandsfläche bis zur definierten Oberkante einschließlich einer gegebenenfalls aufliegenden Deckplatte. Profilquerschnitte, Plattenstärken, Zubehörbauhöhen und Montageabstände fließen in die Berechnung ein.

Die erste Version ist für gerade Profilzuschnitte vorgesehen. Das Referenzprofil, die Verbindungssätze, die Plattenauflage und der Referenztyp absenkbarer Rollen müssen vor der Umsetzung konkret festgelegt werden.

- Dialog und gespeicherte Konfiguration bleiben maßgeblich; manuelle Änderungen an Layoutskizzen werden nicht als Eingaben übernommen.
- Manuelle Änderungen an generierten Bauteilen bleiben beim Neuaufbau nicht erhalten. Andere, nicht vom Add-in verwaltete Komponenten bleiben unberührt.
- Externe Referenzen auf neu erzeugte Flächen werden nicht zugesichert.
- Verbindungsteile können nur bei hinterlegten Montage- und Mengenregeln vollständig in der Stückliste erscheinen; fehlende Zuordnungen werden gekennzeichnet.
- Eine statische Tragfähigkeitsberechnung ist nicht enthalten. Die Querträgerverteilung setzt geometrische Benutzervorgaben um.

## Umsetzungsetappen

1. **Grundprototyp:** Referenzprofil, vier Pfosten, oberer Rahmen, Dialog und Mittellinien-Vorschau.
2. **Profilbaugruppe:** DXF-Extrusion, Benennung, Eigenschaften und Zeitleistengruppen.
3. **Böden und Querträger:** Ebenen, Platten und gleichmäßige Abstützung.
4. **Zubehör:** Füße, Rollen und konkrete Verbindungssätze.
5. **Projektbearbeitung und Export:** Konfiguration laden, kontrollierter Neuaufbau und CSV-Listen.
6. **Abnahme:** Prüfungen in Fusion, Beispieldateien sowie Installations- und Bibliotheksanleitung.

Geplant sind gezielte Tests der Berechnungslogik sowie separate Prüfungen in Fusion. Dabei sollen insbesondere Maße, Profilhohlräume, die Übereinstimmung von Vorschau und Baugruppe, Exportmengen und das erneute Öffnen der Konfiguration geprüft werden.

Spätere Erweiterungen umfassen unter anderem weitere Rahmenformen, individuelle Querträgerpositionen, eine Querträgeranzahl anhand einer maximalen freien Spannweite, Griffbügel, Diagonalstreben, zusätzliche Importformate und die Zuschnittoptimierung für Lagerstangen.

## Dokumentation

- [Änderungshistorie](docu/timeline.md) – bisherige Änderungen und aktueller Prüfstand.
- [Demo installieren und testen](docu/demo_installation.md) – Dialog, Icons, Versionierung und Fusion-Prüfschritte.
- [Projektplan](docu/projektplan_FrameKit.md) – vollständige Anforderungen, Konstruktionsregeln, Umsetzungsschritte und Abnahmekriterien.
- [Branding und Grafikressourcen](images/README.md) – Informationen zu Logo, GitHub-Banner und Fusion-Befehlssymbolen (Englisch).
- [English README](README.en.md) – englische Projektübersicht.

## Lizenz

Die Lizenzbedingungen stehen in [LICENSE](LICENSE).
