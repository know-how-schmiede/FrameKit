"""Fusion-independent definitions for cylindrical foot/caster placeholders."""
import math
from copy import deepcopy
from uuid import uuid4

KINDS = ('Fuß', 'Lenkrolle', 'Bockrolle', 'Absenkbare Rolle', 'Sonstiges')
PRESETS = [
    dict(id='demo-foot', name='Demo-Fuß', kind='Fuß', height=40.0, diameter=50.0),
    dict(id='demo-caster', name='Demo-Rolle', kind='Lenkrolle', height=100.0, diameter=75.0),
    dict(id='demo-fixed-caster', name='Demo-Bockrolle', kind='Bockrolle', height=100.0, diameter=75.0),
]
CORNERS = ('front:left', 'back:left', 'front:right', 'back:right')
CORNER_LABELS = ('Vorne links', 'Hinten links', 'Vorne rechts', 'Hinten rechts')


def corner_specs(values):
    """Legacy common selection or four independent, self-contained snapshots."""
    if 'corner_accessories' not in values:
        return {key: values.get('accessory') for key in CORNERS}
    entries = values['corner_accessories']
    if not isinstance(entries, dict) or set(entries) != set(CORNERS):
        raise ValueError('Für jede der vier Ecken muss eine Zubehörauswahl vorhanden sein.')
    return entries


def support_height(values):
    specs = corner_specs(values)
    heights = []
    for spec in specs.values():
        if spec is not None:
            validate_spec(spec)
        heights.append(spec['height'] if spec else 0)
    if max(heights)-min(heights) > 1e-6:
        raise ValueError('Füße/Rollen müssen an allen vier Ecken dieselbe Bauhöhe haben. '
                         'Höhen einstellen; ein automatischer Höhenausgleich ist nicht definiert.')
    return heights[0]


def arrangement(frame_type):
    """Synthetic presets, not manufacturer dimensions."""
    if frame_type == 'frame':
        return {key: deepcopy(PRESETS[0]) for key in CORNERS}
    if frame_type == 'cart':
        return {key: deepcopy(PRESETS[1 if key.startswith('front:') else 2]) for key in CORNERS}
    raise ValueError('Unbekannte Bauart.')


def validate_spec(spec):
    if not isinstance(spec, dict):
        raise ValueError('Ungültige Fuß-/Rollendefinition.')
    for key in ('id', 'name'):
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            raise ValueError('Name und ID des Platzhalters dürfen nicht leer sein.')
    if len(spec['name']) > 80:
        raise ValueError('Der Name darf höchstens 80 Zeichen enthalten.')
    if spec.get('kind') not in KINDS:
        raise ValueError('Bitte eine gültige Art für den Platzhalter wählen.')
    for key, label in (('height', 'Höhe'), ('diameter', 'Durchmesser')):
        value = spec.get(key)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or not 1 <= value <= 10000):
            raise ValueError(f'{label} des Platzhalters muss zwischen 1 und 10000 mm liegen.')
    for key in ('brake', 'adjustable'):
        if key in spec and not isinstance(spec[key], bool):
            raise ValueError('Bremse und Höhenverstellung müssen Wahrheitswerte sein.')
    for key in ('mounting', 'reference', 'operating_state'):
        if key in spec and (not isinstance(spec[key], str) or len(spec[key]) > 200):
            raise ValueError('Montage-, Referenz- und Stellungsangaben dürfen maximal 200 Zeichen enthalten.')
    if spec.get('adjustable'):
        for key in ('min_height', 'max_height'):
            value = spec.get(key)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or not 1 <= value <= 10000):
                raise ValueError('Für Höhenverstellung gültige minimale und maximale Bauhöhe angeben.')
        if not spec['min_height'] <= spec['height'] <= spec['max_height']:
            raise ValueError('Bauhöhe muss innerhalb des angegebenen Verstellbereichs liegen.')
    if spec.get('brake') and spec['kind'] not in ('Lenkrolle', 'Bockrolle', 'Absenkbare Rolle'):
        raise ValueError('Eine Bremse ist nur für Rollen vorgesehen.')
    # Existing pre-S06 snapshots remain readable; new definitions require explicit semantics.
    if spec.get('definition_version') == 2 and spec['kind'] == 'Absenkbare Rolle':
        if not spec.get('reference', '').strip() or not spec.get('operating_state', '').strip():
            raise ValueError('Für absenkbare Rollen Referenztyp und Betriebsstellung angeben.')


def validate_library(entries):
    if not isinstance(entries, list):
        raise ValueError('Die Platzhalterbibliothek muss eine Liste sein.')
    ids, names = set(), set()
    for spec in entries:
        validate_spec(spec)
        name = spec['name'].strip().casefold()
        if spec['id'] in ids or name in names:
            raise ValueError('Name und ID müssen in der Bibliothek eindeutig sein.')
        ids.add(spec['id'])
        names.add(name)


def new_spec(name, kind, height, diameter, **properties):
    spec = dict(id=uuid4().hex, name=name.strip(), kind=kind, height=height, diameter=diameter)
    spec.update(properties)
    validate_spec(spec)
    return spec


def duplicate(spec, entries):
    result = deepcopy(spec)
    result['id'] = uuid4().hex
    result['definition_version'] = 2
    names = {entry['name'].casefold() for entry in entries}
    number = 1
    while True:
        suffix = f' (Kopie {number})'
        result['name'] = spec['name'][:80-len(suffix)]+suffix
        if result['name'].casefold() not in names:
            break
        number += 1
    validate_spec(result)
    return result


def label(spec):
    return (f'{spec["name"]} ({spec["kind"]}) – '
            f'H {spec["height"]:g} mm / Ø {spec["diameter"]:g} mm')
