"""Named configurations and validated, portable user-data backups."""
from copy import deepcopy
import base64
import json
from pathlib import Path
from uuid import uuid4

from . import settings, profile_library, accessories, demo, dxf_profile


def root():
    return settings.settings_path().parent


def read_json(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else deepcopy(default)


def validate_templates(entries):
    if not isinstance(entries, list):
        raise ValueError('Ungültige Vorlagenliste.')
    ids, names = set(), set()
    for entry in entries:
        name = entry['name']
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise ValueError('Vorlagenname erforderlich (maximal 80 Zeichen).')
        if not isinstance(entry['id'], str) or not entry['id'] or entry['id'] in ids or name.casefold() in names:
            raise ValueError('Vorlagennamen und IDs müssen eindeutig sein.')
        demo.validate(entry['values'])
        ids.add(entry['id'])
        names.add(name.casefold())


def load(folder=None):
    data = read_json(Path(folder or root()) / 'templates.json', dict(schema=1, entries=[]))
    if data['schema'] != 1:
        raise ValueError('Unbekannte Vorlagenversion.')
    validate_templates(data['entries'])
    return data['entries']


def save(entries, folder=None):
    validate_templates(entries)
    settings._write_json(Path(folder or root()) / 'templates.json', dict(schema=1, entries=entries))


def snapshot(folder=None):
    folder = Path(folder or root())
    profiles = profile_library._read(folder / 'profiles')
    files = {}
    for spec in profiles:
        profile_library.verify_source(spec, folder / 'profiles')
        files[spec['filename']] = base64.b64encode((folder / 'profiles' / spec['filename']).read_bytes()).decode('ascii')
    library = read_json(folder / 'accessories.json', dict(schema=1, entries=accessories.PRESETS))
    if library['schema'] != 1:
        raise ValueError('Unbekannte Zubehörversion.')
    data = dict(schema=1, templates=load(folder), accessories=library['entries'], profiles=profiles, files=files)
    validate_backup(data)
    return data


def validate_backup(data):
    try:
        if data['schema'] != 1:
            raise ValueError('Unbekannte Sicherungsversion.')
        validate_templates(data['templates'])
        accessories.validate_library(data['accessories'])
        ids, names = set(), set()
        for spec in data['profiles']:
            profile_library.validate(spec)
            if spec['id'] in ids or spec['name'].casefold() in names:
                raise ValueError('Doppelte Profile in der Sicherung.')
            ids.add(spec['id'])
            names.add(spec['name'].casefold())
            raw = base64.b64decode(data['files'][spec['filename']], validate=True)
            if len(raw) > dxf_profile.MAX_BYTES or profile_library._digest(raw) != spec['source_sha256']:
                raise ValueError('DXF-Prüfsumme oder Dateigröße ungültig.')
            if dxf_profile.read(raw, spec['source_unit'])['curves'] != spec['curves']:
                raise ValueError('DXF und Profilkontur stimmen nicht überein.')
        if set(data['files']) != {p['filename'] for p in data['profiles']}:
            raise ValueError('Unerwartete Profildateien in der Sicherung.')
    except (KeyError, TypeError, AttributeError, OverflowError) as exc:
        raise ValueError('Unvollständige oder beschädigte Sicherung.') from exc


def export_file(path, folder=None):
    settings._write_json(Path(path), snapshot(folder))


def read_backup(path):
    path = Path(path)
    if path.stat().st_size > 100 * 1024 * 1024:
        raise ValueError('Sicherung überschreitet 100 MB.')
    data = json.loads(path.read_text(encoding='utf-8'))
    validate_backup(data)
    return data


def plan_import(incoming, mode, folder=None):
    """Pure planning: conflict decisions are reviewable before any write."""
    validate_backup(incoming)
    if mode not in ('skip', 'copy', 'replace'):
        raise ValueError('Unbekannte Konfliktregel.')
    result = snapshot(folder)
    report = []
    for category in ('templates', 'accessories', 'profiles'):
        for source in incoming[category]:
            entry = deepcopy(source)
            conflicts = [e for e in result[category] if e['id'] == entry['id'] or e['name'].casefold() == entry['name'].casefold()]
            action = mode if conflicts else 'add'
            report.append(f'{category}: {entry["name"]} – '+dict(skip='überspringen', copy='als Kopie', replace='ersetzen', add='hinzufügen')[action])
            if action == 'skip':
                continue
            if action == 'replace':
                result[category] = [e for e in result[category] if e not in conflicts]
            if action == 'copy':
                entry['id'] = uuid4().hex
                names = {e['name'].casefold() for e in result[category]}
                n = 1
                while True:
                    suffix = f' (Kopie {n})'
                    entry['name'] = source['name'][:80-len(suffix)] + suffix
                    if entry['name'].casefold() not in names:
                        break
                    n += 1
                if category == 'profiles':
                    entry['filename'] = entry['id'] + '.dxf'
            result[category].append(entry)
            if category == 'profiles':
                result['files'][entry['filename']] = incoming['files'][source['filename']]
    result['files'] = {p['filename']: result['files'][p['filename']] for p in result['profiles']}
    # Configurations contain immutable snapshots; never substitute library IDs in them.
    validate_backup(result)
    return result, '\n'.join(report)


def apply_import(data, folder=None):
    """Validate first and roll back all touched files on a write failure."""
    validate_backup(data)
    folder = Path(folder or root())
    payloads = {
        folder / 'templates.json': dict(schema=1, entries=data['templates']),
        folder / 'accessories.json': dict(schema=1, entries=data['accessories']),
        folder / 'profiles' / 'index.json': dict(schema=1, entries=data['profiles']),
    }
    writes = {path: (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8') for path, value in payloads.items()}
    for name, encoded in data['files'].items():
        writes[folder / 'profiles' / name] = base64.b64decode(encoded, validate=True)
    previous = {path: path.read_bytes() if path.exists() else None for path in writes}
    touched = []
    try:
        for path, content in writes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            touched.append(path)
            atomic_bytes(path, content)
    except Exception:
        for path in reversed(touched):
            if previous[path] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_bytes(path, previous[path])
        raise


def atomic_bytes(path, content):
    import os
    import tempfile
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
