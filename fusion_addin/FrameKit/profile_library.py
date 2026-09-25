"""Persistent user profiles with immutable, self-contained geometry snapshots."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from uuid import uuid4

from . import dxf_profile

METADATA = ('manufacturer', 'series', 'article_number', 'slot_size', 'material')


def directory():
    from .settings import settings_path
    return settings_path().parent / 'profiles'


def label(spec):
    return f'{spec["name"]} | {spec["width_mm"]:g} × {spec["height_mm"]:g} mm'


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _geometry_digest(curves):
    return _digest(json.dumps(curves, sort_keys=True, allow_nan=False).encode('utf-8'))


def prepare(path, name, unit='auto', metadata=None):
    path = Path(path)
    if path.suffix.lower() != '.dxf':
        raise ValueError('Bitte eine lokale DXF-Datei auswählen.')
    with path.open('rb') as stream:
        data = stream.read(dxf_profile.MAX_BYTES+1)
    shape = dxf_profile.read(data, unit)
    identifier = uuid4().hex
    spec = dict(id=identifier, name=name.strip(), filename=identifier+'.dxf',
                source_name=path.name, source_sha256=_digest(data),
                geometry_sha256=_geometry_digest(shape['curves']),
                units='mm', origin='bounds-center', extrusion_axis='z',
                is_demo=False, **shape)
    for key in METADATA:
        spec[key] = (metadata or {}).get(key, '').strip()
    validate(spec)
    return spec, data


def validate(spec):
    try:
        if (not isinstance(spec, dict) or not re.fullmatch(r'[0-9a-f]{32}', spec['id'])
                or spec['filename'] != spec['id']+'.dxf'
                or spec['units'] != 'mm' or spec['origin'] != 'bounds-center'
                or spec['extrusion_axis'] != 'z' or spec['is_demo'] is not False):
            raise ValueError('Ungültige Profildefinition.')
        for key in ('name', *METADATA):
            text = spec[key]
            if not isinstance(text, str) or len(text) > 200 or (key == 'name' and not text.strip()):
                raise ValueError('Profilname erforderlich; Textfelder maximal 200 Zeichen.')
        if not re.fullmatch(r'[0-9a-f]{64}', spec['source_sha256']):
            raise ValueError('Ungültige DXF-Prüfsumme.')
        shape = dxf_profile.inspect(spec['curves'])
        for key in ('width_mm', 'height_mm', 'area_mm2', 'loop_count'):
            if abs(dxf_profile.number(spec[key])-shape[key]) > dxf_profile.TOL:
                raise ValueError('Profilmaße oder Konturen stimmen nicht mit den gespeicherten Daten überein.')
        if spec['geometry_sha256'] != _geometry_digest(spec['curves']):
            raise ValueError('Gespeicherte Profilkontur wurde verändert.')
    except (KeyError, TypeError, AttributeError, OverflowError) as exc:
        raise ValueError('Unvollständige oder beschädigte Profildefinition.') from exc


def _read(folder):
    path = folder / 'index.json'
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('entries'), list):
        raise ValueError('Ungültige Profilbibliothek.')
    entries = data['entries']
    for spec in entries:
        validate(spec)
    if len({entry['id'] for entry in entries}) != len(entries):
        raise ValueError('Doppelte Profil-IDs in der Bibliothek.')
    return entries


def load(folder=None):
    folder = Path(folder) if folder is not None else directory()
    try:
        return _read(folder), ''
    except (OSError, ValueError, TypeError) as exc:
        return [], f'Profilbibliothek konnte nicht geladen werden: {exc}'


def verify_source(spec, folder=None):
    """Check only library creation inputs; existing assemblies use their snapshot."""
    validate(spec)
    folder = Path(folder) if folder is not None else directory()
    path = folder / spec['filename']
    try:
        with path.open('rb') as stream:
            data = stream.read(dxf_profile.MAX_BYTES+1)
    except OSError as exc:
        raise ValueError(f'DXF für „{spec["name"]}“ fehlt oder ist nicht lesbar. Profil neu importieren.') from exc
    if _digest(data) != spec['source_sha256']:
        raise ValueError(f'DXF für „{spec["name"]}“ wurde verändert. Profil neu importieren.')


def add(spec, data, folder=None):
    """Publish after Fusion validation. Roll back the copy if index writing fails."""
    from .settings import _write_json
    validate(spec)
    if _digest(data) != spec['source_sha256']:
        raise ValueError('DXF wurde seit der Prüfung verändert.')
    # Do not accept mismatched snapshots, even if supplied by another caller.
    parsed = dxf_profile.read(data, spec['source_unit'])
    if parsed['curves'] != spec['curves']:
        raise ValueError('DXF und geprüfte Konturen stimmen nicht überein.')
    folder = Path(folder) if folder is not None else directory()
    entries = _read(folder)  # A damaged index must never be overwritten with an empty one.
    if any(entry['id'] == spec['id'] for entry in entries):
        raise ValueError('Dieses Profil ist bereits gespeichert.')
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / spec['filename']
    revised = entries + [deepcopy(spec)]
    created = False
    try:
        with path.open('xb') as stream:
            created = True
            stream.write(data)
        _write_json(folder / 'index.json', dict(schema=1, entries=revised))
    except Exception:
        if created:
            path.unlink()
        raise
    return revised


def remove(identifier, folder=None):
    """Delete only the library-owned DXF; restore it on an index write failure."""
    from .settings import _write_json
    folder = Path(folder) if folder is not None else directory()
    entries = _read(folder)
    removed = next((entry for entry in entries if entry['id'] == identifier), None)
    if removed is None:
        raise ValueError('Profil nicht in der Bibliothek gefunden.')
    path = folder / removed['filename']
    backup = path.with_suffix('.deleting')
    moved = False
    if path.exists():
        path.replace(backup)
        moved = True
    revised = [entry for entry in entries if entry['id'] != identifier]
    try:
        _write_json(folder / 'index.json', dict(schema=1, entries=revised))
    except Exception:
        if moved:
            backup.replace(path)
        raise
    if moved:
        backup.unlink()
    return revised
