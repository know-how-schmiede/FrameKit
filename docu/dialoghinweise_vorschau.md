# Dialoghinweise und Vorschau – 0.4.1

Fehler erscheinen einheitlich in Rot mit der Kennzeichnung **Fehler**, Warnungen in Braunorange mit **Hinweis**. Ein heller Hintergrund hinter dem Text hält den Kontrast unabhängig vom Fusion-Theme. Betroffen sind Eingabeprüfung, Vorschau, Laden/Speichern der Standardwerte und die Zubehör-/DXF-Bibliotheken. Erfolgreiche Aktionen entfernen die vorherige Fehlerformatierung. Namen und Fehlermeldungen werden als Text behandelt und für die HTML-Ausgabe maskiert.

Beim Einschalten von **Vorschau anzeigen** wird das Gestell vollständig im vorhandenen Ansichtsbereich angezeigt. Eingeschlossen sind Profilquerschnitte, Platten und Zubehörüberstände. Andere Gestelle oder entfernte Bauteile im Dokument bestimmen diesen Ausschnitt nicht. Fusion wechselt nicht in den Vollbildmodus.

Die Blickrichtung und der Kameratyp bleiben erhalten. Die Berechnung verwendet eine umschließende Kugel mit 12 % Rand, bei Perspektive zusätzlich das Seitenverhältnis des Ansichtsbereichs. Die Kamera wird einmal beim Einschalten eingepasst; spätere Änderungen im Dialog überschreiben manuelles Zoomen nicht. Zum erneuten Einpassen die Vorschau aus- und wieder einschalten. Schlägt nur das Einpassen fehl, bleibt die Vorschau sichtbar und zeigt einen Warnhinweis.

**Prüfstand:** 95 lokale Tests und Syntaxprüfung erfolgreich. Geprüft sind Statusformatierung, Maskierung, Rücksetzen der Fehlerfarben, Kameratypen, Ansichtsgrößen, Zubehörüberstände sowie einmaliges Einpassen und Fehlerbehandlung. Darstellung im laufenden Fusion noch offen.

In Fusion prüfen: von stark vergrößerter/verschobener Ansicht aus die Vorschau einschalten, einschließlich eines Dokuments mit anderen entfernten Bauteilen. Das gesamte Gestell soll sichtbar sein. Danach manuell zoomen und Maße ändern; Zoom soll erhalten bleiben. In hellem und dunklem Theme unterschiedliche Rollenhöhen, ungültige DXF-Dateien und Bibliotheksfehler auslösen; Meldungen müssen farbig und lesbar sein. Auch Dialogposition und Bildschirm-Skalierung prüfen, da ein über der Ansicht liegendes Dialogfenster weiterhin Modellteile verdecken kann.

API-Grundlagen: [TextBoxCommandInput.formattedText](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_TextBoxCommandInput_formattedText.htm), [Camera.setExtents](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Camera_setExtents.htm) und [Viewport.camera](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Viewport_camera.htm).

Ab 0.4.2 sind [vereinfachte Winkelkörper](winkel.md) umgesetzt; reale Befestigungsteile bleiben offen.
