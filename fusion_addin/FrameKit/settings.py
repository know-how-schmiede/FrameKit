"""Personal defaults stored outside the add-in installation."""
import json
import os
from pathlib import Path
import sys
import tempfile
from copy import deepcopy
from .demo import DEFAULTS, validate
from .accessories import PRESETS, validate_library


def settings_path():
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:
        base = Path.home() / 'Library' / 'Application Support'
    return base / 'FrameKit' / 'settings.json'


def load(path=None):
    path = Path(path) if path is not None else settings_path()
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if data['schema'] != 1:
            raise ValueError('Unbekannte Einstellungsversion.')
        stored = data['defaults']
        values = {key: stored[key] for key in ('length', 'width', 'height', 'profile', 'bottom')}
        # Settings from 0.1.0/0.1.1 have no shelf fields.
        for key in ('shelf_count', 'shelf_heights', 'shelf_thickness', 'accessory'):
            values[key] = deepcopy(stored.get(key, DEFAULTS[key]))
        validate(values)
        return values, ''
    except FileNotFoundError:
        return deepcopy(DEFAULTS), ''
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return deepcopy(DEFAULTS), f'Standardwerte verwendet: {exc}'


def save(values, path=None):
    validate(values)
    path = Path(path) if path is not None else settings_path()
    _write_json(path, {'schema': 1, 'defaults': values})


def library_path():
    return settings_path().with_name('accessories.json')


def load_library(path=None):
    path = Path(path) if path is not None else library_path()
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if data['schema'] != 1:
            raise ValueError('Unbekannte Bibliotheksversion.')
        validate_library(data['entries'])
        return data['entries'], ''
    except FileNotFoundError:
        return deepcopy(PRESETS), ''
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [], f'Platzhalterbibliothek konnte nicht geladen werden: {exc}'


def save_library(entries, path=None):
    validate_library(entries)
    path = Path(path) if path is not None else library_path()
    _write_json(path, {'schema': 1, 'entries': entries})


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as stream:
            temp_path = Path(stream.name)
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
