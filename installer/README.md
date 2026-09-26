# FrameKit Windows-Installer

Der Installer orientiert sich an `SegmentJoinPilot.iss`: Installation pro Benutzer ohne Administratorrechte, moderne deutsch/englische Oberfläche und Erkennung beider Fusion-Verzeichnisse.

```text
%APPDATA%\Autodesk\Autodesk Fusion\API\AddIns\FrameKit
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FrameKit
```

Vorhandene `API\AddIns`-Verzeichnisse haben Vorrang vor Produktverzeichnissen. Bei Gleichstand wird `Autodesk Fusion` bevorzugt. Die Zielauswahl wird immer angezeigt und bei Updates erneut ermittelt. Eine vorhandene Ordnerstruktur garantiert nicht, dass die aktive Fusion-Installation sie verwendet. Andere Installationskopien werden nicht gelöscht.

Vor Installation oder Update Fusion schließen. Die EXE ausführen, Ziel prüfen und Fusion anschließend neu starten. FrameKit unter Skripte und Zusatzmodule aktivieren. Persönliche Daten unter `%APPDATA%\FrameKit` bleiben beim normalen Installieren, Aktualisieren und Deinstallieren erhalten. Deinstallation über die Windows-Appverwaltung. Für eine vollständige Sicherung den Benutzerdatenordner bei geschlossenem Fusion kopieren.

Die EXE enthält den Add-in-Code, Bibliotheken und Ressourcen. Dokumentation und importierbare Beispiele stehen im separaten ZIP-Paket bereit. Der Installer hat eine eigene, dauerhaft beizubehaltende AppId; Version 0.9.0 bleibt unverändert.

## Build

Inno Setup 6 installieren, dann im Repository ausführen:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-installer.ps1
```

Das Skript prüft die Übereinstimmung von `.iss`, Manifest und `version.py`. Ausgabe:

- `installer/dist/FrameKit-Setup-0.9.0.exe`
- `installer/dist/FrameKit-Setup-0.9.0.exe.sha256`

Bytecode und `__pycache__` werden nicht eingebunden. Der Build vom 27.09.2026 mit Inno Setup 6.7.0 war erfolgreich; die erzeugte EXE wurde auf Versionsinformationen und Prüfsumme geprüft. Installation/Update/Deinstallation und native Fusion-Abnahme sind noch nicht ausgeführt. Die EXE ist nicht digital signiert.
