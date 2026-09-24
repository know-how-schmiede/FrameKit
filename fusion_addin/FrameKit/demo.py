"""Fusion-independent demo layout; dimensions in millimeters."""
import math
from .accessories import validate_spec

MAX_SHELVES = 20
DEFAULTS = dict(length=800.0, width=500.0, height=750.0, profile=40.0, bottom=True,
                shelf_count=0, shelf_heights=[], shelf_thickness=18.0, accessory=None)


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
    spec = values.get('accessory')
    if spec is not None:
        validate_spec(spec)
        if spec['diameter'] > min(values['length'], values['width']) - values['profile']:
            raise ValueError('Durchmesser zu groß: Fuß-/Rollenplatzhalter würden sich überlappen.')
    shelf_heights(values)


def base_height(values):
    spec = values.get('accessory')
    return spec['height'] if spec is not None else 0


def shelf_heights(values):
    """Resolve optional shelf tops with equal clear gaps between fixed anchors."""
    count = values.get('shelf_count', 0)
    if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= MAX_SHELVES:
        raise ValueError(f'Anzahl der Zwischenböden muss zwischen 0 und {MAX_SHELVES} liegen.')
    requested = values.get('shelf_heights', [])
    if not isinstance(requested, list) or len(requested) != count:
        raise ValueError('Für jeden Zwischenboden ist eine Höhe oder ein leerer Wert erforderlich.')
    p = values['profile']
    thickness = values.get('shelf_thickness', 18.0)
    if (isinstance(thickness, bool) or not isinstance(thickness, (int, float))
            or not math.isfinite(thickness) or not 1 <= thickness <= 10000):
        raise ValueError('Plattenstärke muss zwischen 1 und 10000 mm liegen.')
    depth = p + thickness
    lower = base_height(values) + (depth if values['bottom'] else 0)
    anchors = [(-1, lower)]
    for index, height in enumerate(requested):
        if height is None:
            continue
        if (isinstance(height, bool) or not isinstance(height, (int, float))
                or not math.isfinite(height)):
            raise ValueError(f'Boden {index + 1}: ungültige Höhe.')
        anchors.append((index, height))
    # Top plate ends at the specified overall height, including its thickness.
    anchors.append((count, values['height']))
    result = [None] * count
    for (left_index, left_top), (right_index, right_top) in zip(anchors, anchors[1:]):
        steps = right_index - left_index
        gap = (right_top - left_top - steps * depth) / steps
        if gap < -1e-7:
            raise ValueError('Zwischenböden überlappen oder liegen außerhalb des Gestells. '
                             'Höhen von unten nach oben angeben oder Anzahl reduzieren.')
        for index in range(left_index + 1, min(right_index + 1, count)):
            result[index] = left_top + (index - left_index) * (depth + gap)
    return result


def panel_outline(length, width, notch):
    """Counterclockwise perimeter with four square post cutouts, in mm."""
    return [(notch, 0), (length-notch, 0), (length-notch, notch),
            (length, notch), (length, width-notch), (length-notch, width-notch),
            (length-notch, width), (notch, width), (notch, width-notch),
            (0, width-notch), (0, notch), (notch, notch)]



def _legacy_parts(values, kind):
    # Compatibility view for callers of the original demo API; one calculation source.
    from .model import build_model
    return [(part['function'], tuple(part['position_mm']), tuple(part['bounds_mm']))
            for part in build_model(values)['parts'] if part['kind'] == kind]


def members(values):
    return _legacy_parts(values, 'profile')


def panels(values):
    return _legacy_parts(values, 'panel')


def supports(values):
    return _legacy_parts(values, 'support')
