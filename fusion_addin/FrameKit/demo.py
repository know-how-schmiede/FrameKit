"""Fusion-independent demo layout; dimensions in millimeters."""
import math

DEFAULTS = dict(length=800.0, width=500.0, height=750.0, profile=40.0, bottom=True)


def validate(values):
    for key in ('length', 'width', 'height', 'profile'):
        value = values.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('Abmessungen müssen Zahlen sein.')
        if not math.isfinite(value) or not 1 <= value <= 10000:
            raise ValueError('Abmessungen müssen zwischen 1 und 10000 mm liegen.')
    if not isinstance(values.get('bottom'), bool):
        raise ValueError('Unterer Rahmen muss ein Wahrheitswert sein.')
    if min(values['length'], values['width'], values['height']) <= 2 * values['profile']:
        raise ValueError('Länge, Breite und Höhe müssen größer als zwei Profilbreiten sein.')


def members(values):
    """Return (name, origin, box dimensions) for non-overlapping members."""
    validate(values)
    length, width, height, p = (values[k] for k in ('length', 'width', 'height', 'profile'))
    result = []
    for x, side in ((0, 'links'), (length - p, 'rechts')):
        for y, depth in ((0, 'vorne'), (width - p, 'hinten')):
            result.append((f'Pfosten {depth} {side}', (x, y, 0), (p, p, height)))
    levels = [('oben', height - p)]
    if values['bottom']:
        levels.append(('unten', 0))
    for level, z in levels:
        for y, side in ((0, 'vorne'), (width - p, 'hinten')):
            result.append((f'Rahmen {level} {side}', (p, y, z), (length - 2*p, p, p)))
        for x, side in ((0, 'links'), (length - p, 'rechts')):
            result.append((f'Rahmen {level} {side}', (x, p, z), (p, width - 2*p, p)))
    return result
