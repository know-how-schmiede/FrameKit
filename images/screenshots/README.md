# FrameKit – Screenshot-Sätze / Screenshot sets

Screenshots werden **pro tatsächlich abgebildeter Add-in-Version** in einem eigenen Ordner abgelegt. Ein Ordner entspricht einem zusammengehörigen Bildsatz. Die aktuelle Codeversion und das Dateidatum sind keine Grundlage für die Zuordnung.

## Vorhandene Bildsätze

| Version | Ordner | Enthaltene Ansichten |
| --- | --- | --- |
| 0.3.0 | [0.3.0](0.3.0/) | Gestell, Browserstruktur, Vorschau, Erstellungsdialog, Bibliotheken, historischer POINT-Importhinweis |
| 0.1.5 | [0.1.5](0.1.5/) | Gestell mit Dialog, Erstellungsdialog, Einstellungen, Browserstruktur, Info |

Die vorhandenen Namen `FrameKit_015_*.png` gehören ausdrücklich zu **0.1.5**. Die Originaldateinamen wurden im Versionsordner beibehalten.

## Neue Screenshots hinzufügen

1. Version anhand der Aufnahme oder einer eindeutigen Benutzerangabe bestimmen. Bei unklarer Zuordnung nachfragen; keinen vorhandenen Bildsatz damit ergänzen.
2. Einen Ordner mit vollständiger Versionsnummer anlegen, beispielsweise `images/screenshots/0.2.0/`. Keine verkürzten Versionsnummern wie `020` für neue Ordner verwenden.
3. Alle Aufnahmen dieser Version dort ablegen. Empfohlene Dateinamen: `FrameKit_0.2.0_FrameErstellen.png`, `FrameKit_0.2.0_FrameErstellenDialog.png`, `FrameKit_0.2.0_Einstellungen.png`, `FrameKit_0.2.0_BrowserStruktur.png`, `FrameKit_0.2.0_Info.png`.
4. Den Bildsatz in der Tabelle ergänzen. Eine fehlende Ansicht bleibt fehlend; sie wird **nicht durch ein Bild einer älteren Version ersetzt**.
5. In der deutschen und englischen README denselben Versionssatz in derselben Reihenfolge verwenden. Überschrift und Bildpfade müssen dieselbe Version nennen. Beschreibungen anhand der tatsächlichen Bilder prüfen.
6. Einen neueren Satz als eigenen Abschnitt oberhalb älterer Sätze ergänzen. Ältere Abschnitte können eingeklappt oder zugunsten eines Links auf ihren Versionsordner entfernt werden. Originalaufnahmen älterer Versionen nicht überschreiben oder umbenennen, um sie als neuere Version auszugeben.

Die READMEs sind statische Markdown-Dateien. Neue Dateien erscheinen dort erst, wenn ihre Bildverweise ergänzt werden; es gibt keine automatische Auswahl oder Vermischung anhand des Dateinamens. Die Versionsordner und diese Zuordnung sind bei künftigen Aktualisierungen maßgeblich.

## English summary

Keep each screenshot set in its own full-version folder. Use the version actually shown in the image, not the current code version or file date. Both READMEs must use matching version headings, image paths, and ordering. Never fill missing views with screenshots from another version. New sets require an explicit README update; older sets remain separate.

[Deutsche README](../../README.md) · [English README](../../README.en.md)
