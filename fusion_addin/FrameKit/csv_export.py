"""Stage CSV exports before replacing destinations, with rollback on write errors."""
import os
from pathlib import Path
import shutil
import tempfile


def write_files(files):
    targets = [Path(path).resolve() for path, _ in files]
    if len(set(targets)) != len(targets):
        raise ValueError('Für beide Listen unterschiedliche Dateinamen wählen.')
    staged, backups, committed = {}, {}, []
    preserve = set()
    def temporary(target):
        handle, name = tempfile.mkstemp(prefix='.framekit-', dir=target.parent)
        os.close(handle)
        return Path(name)
    try:
        for target, (_, content) in zip(targets, files):
            staged[target] = temporary(target)
            staged[target].write_text(content, encoding='utf-8-sig', newline='')
            if target.exists():
                backups[target] = temporary(target)
                shutil.copyfile(target, backups[target])
        for target in targets:
            os.replace(staged[target], target)
            committed.append(target)
    except Exception as error:
        failures = []
        for target in reversed(committed):
            try:
                if target in backups:
                    os.replace(backups[target], target)
                else:
                    target.unlink()
            except OSError:
                if target in backups:
                    preserve.add(backups[target])
                failures.append(str(target))
        if failures:
            raise OSError(f'{error}; Wiederherstellung fehlgeschlagen: {failures}. Sicherungen: {list(preserve)}') from error
        raise
    finally:
        for path in [*staged.values(), *backups.values()]:
            if path not in preserve:
                path.unlink(missing_ok=True)
