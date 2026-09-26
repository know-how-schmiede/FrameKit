"""Fusion-independent demo layout; dimensions in millimeters."""
import math
from .accessories import corner_specs, support_height
from .sections import resolve, validate_selections, level_depth
from .dxf_profile import TOL as PROFILE_TOLERANCE_MM

MAX_SHELVES = 20
DEFAULTS = dict(length=800.0, width=500.0, height=750.0, profile=40.0, bottom=True,
                shelf_count=0, shelf_heights=[], shelf_thickness=18.0, accessory=None,
                cross_members={}, top_panel_mount='notched', profile_definition=None)


def validate(values):
    for key in ('brackets', 'brackets_double'):
        if key in values and not isinstance(values[key], bool):
            raise ValueError('Winkeloptionen müssen Wahrheitswerte sein.')
    for key in ('length', 'width', 'height', 'profile'):
        value = values.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('Abmessungen müssen Zahlen sein.')
        if not math.isfinite(value) or not 1 <= value <= 10000:
            raise ValueError('Abmessungen müssen zwischen 1 und 10000 mm liegen.')
    definition = values.get('profile_definition')
    if definition is not None:
        from .profile_library import validate as validate_profile
        validate_profile(definition)
        if abs(values['profile']-definition['width_mm']) > 1e-5:
            raise ValueError('Profilbreite stimmt nicht mit dem ausgewählten DXF-Profil überein.')
    if not isinstance(values.get('bottom'), bool):
        raise ValueError('Unterer Rahmen muss ein Wahrheitswert sein.')
    validate_selections(values)
    px, py = resolve(values, 'posts')[2]
    fw = resolve(values, 'frame')[2][0]
    if values['length'] <= 2*max(px, fw) or values['width'] <= 2*max(py, fw):
        raise ValueError('Länge und Breite müssen größer als zwei Profilbreiten sein.')
    # DXF bounds retain floating-point export noise even for nominally square sections.
    if fw - min(px, py) > PROFILE_TOLERANCE_MM:
        raise ValueError('Rahmenbreite darf die Pfostenmaße nicht überschreiten; Profile oder Drehung ändern.')
    if values.get('frame_type', 'frame') not in ('frame', 'cart'):
        raise ValueError('Bauart muss Untergestell oder Transportwagen sein.')
    support_height(values)
    supports = corner_specs(values)
    centers = {f'{depth}:{side}': (x, y)
               for side, x in (('left', px/2), ('right', values['length']-px/2))
               for depth, y in (('front', py/2), ('back', values['width']-py/2))}
    active = [(key, spec) for key, spec in supports.items() if spec is not None]
    for index, (key, spec) in enumerate(active):
        for other_key, other in active[index+1:]:
            distance = math.dist(centers[key], centers[other_key])
            if distance < (spec['diameter']+other['diameter'])/2 - 1e-7:
                raise ValueError('Durchmesser zu groß: Fuß-/Rollenplatzhalter würden sich überlappen.')
    if values.get('top_panel_mount', 'notched') not in ('notched', 'on_top'):
        raise ValueError('Ungültige Montageart der Deckplatte.')
    settings = values.get('cross_members', {})
    if not isinstance(settings, dict):
        raise ValueError('Ungültige Querträgereinstellungen.')
    allowed = {'top', 'bottom'} | {f'shelf:{i:02d}' for i in range(1, MAX_SHELVES+1)}
    for key, spec in settings.items():
        if key not in allowed or not isinstance(spec, dict):
            raise ValueError('Ungültige Querträgerebene.')
        count = spec.get('count')
        if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= 5:
            raise ValueError('Querträgeranzahl muss zwischen 0 und 5 liegen.')
        if spec.get('direction') not in ('quer', 'laengs'):
            raise ValueError('Querträgerrichtung muss Quer oder Längs sein.')
    shelf_heights(values)
    for key, label in frame_levels(values):
        spec = settings.get(key, {'count': 0, 'direction': 'quer'})
        span = values['length' if spec['direction'] == 'quer' else 'width']
        cw = resolve(values, 'cross', key)[2][0]
        if spec['count'] and span - 2*fw - spec['count']*cw <= 0:
            raise ValueError(f'{label}: zu wenig Platz für die Querträger; Anzahl reduzieren.')
        if spec['count']:
            gap = (span - 2*fw - spec['count']*cw)/(spec['count']+1)
            post_span = px if spec['direction'] == 'quer' else py
            if fw + gap < post_span - 1e-7:
                raise ValueError(f'{label}: Querträger kollidieren mit Pfosten; Anzahl oder Profil ändern.')


def frame_levels(values):
    return ([('top', 'Oben')] + ([('bottom', 'Unten')] if values['bottom'] else [])
            + [(f'shelf:{i:02d}', f'Boden {i:02d}')
               for i in range(1, values.get('shelf_count', 0)+1)])


def base_height(values):
    return support_height(values)


def shelf_heights(values):
    """Resolve optional shelf tops with equal clear gaps between fixed anchors."""
    count = values.get('shelf_count', 0)
    if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= MAX_SHELVES:
        raise ValueError(f'Anzahl der Zwischenböden muss zwischen 0 und {MAX_SHELVES} liegen.')
    requested = values.get('shelf_heights', [])
    if not isinstance(requested, list) or len(requested) != count:
        raise ValueError('Für jeden Zwischenboden ist eine Höhe oder ein leerer Wert erforderlich.')
    thickness = values.get('shelf_thickness', 18.0)
    if (isinstance(thickness, bool) or not isinstance(thickness, (int, float))
            or not math.isfinite(thickness) or not 1 <= thickness <= 10000):
        raise ValueError('Plattenstärke muss zwischen 1 und 10000 mm liegen.')
    depths = [level_depth(values, f'shelf:{i:02d}') for i in range(1, count+1)]
    depths.append(level_depth(values, 'top'))
    lower = base_height(values) + (level_depth(values, 'bottom') if values['bottom'] else 0)
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
        gap = (right_top - left_top - sum(depths[left_index+1:right_index+1])) / steps
        if gap < -1e-7:
            raise ValueError('Zwischenböden überlappen oder liegen außerhalb des Gestells. '
                             'Höhen von unten nach oben angeben oder Anzahl reduzieren.')
        for index in range(left_index + 1, min(right_index + 1, count)):
            result[index] = left_top + sum(depths[left_index+1:index+1]) + (index-left_index)*gap
    return result


def panel_outline(length, width, notch, notch_y=None):
    """Counterclockwise perimeter with rectangular post cutouts, in mm."""
    ny = notch if notch_y is None else notch_y
    return [(notch, 0), (length-notch, 0), (length-notch, ny),
            (length, ny), (length, width-ny), (length-notch, width-ny),
            (length-notch, width), (notch, width), (notch, width-ny),
            (0, width-ny), (0, ny), (notch, ny)]



def _legacy_parts(values, kind):
    # Compatibility view for callers of the original demo API; one calculation source.
    from .model import build_model
    return [(part['function'], tuple(part['bounds_origin_mm']), tuple(part['bounds_mm']))
            for part in build_model(values)['parts'] if part['kind'] == kind]


def members(values):
    return _legacy_parts(values, 'profile')


def panels(values):
    return _legacy_parts(values, 'panel')


def supports(values):
    return _legacy_parts(values, 'support')
