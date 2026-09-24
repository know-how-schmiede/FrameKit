"""Personal defaults stored outside the add-in installation."""
import json
import os
from pathlib import Path
import sys
import tempfile
from .demo import DEFAULTS, validate


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
        values = {key: data['defaults'][key] for key in DEFAULTS}
        validate(values)
        return values, ''
    except FileNotFoundError:
        return DEFAULTS.copy(), ''
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return DEFAULTS.copy(), f'Standardwerte verwendet: {exc}'


def save(values, path=None):
    validate(values)
    path = Path(path) if path is not None else settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as stream:
            temp_path = Path(stream.name)
            json.dump({'schema': 1, 'defaults': values}, stream, indent=2)
            stream.write('\n')
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
