"""Resolve section inheritance and quarter-turns without Fusion dependencies."""
from copy import deepcopy


def resolve(values, group, level=None):
    p = values['profile']
    definition = values.get('profile_definition') or dict(
        id=f'demo:square:{p:g}x{p:g}', name=f'{p:g}x{p:g} Demo-Vollprofil',
        width_mm=p, height_mm=p, material=None, is_demo=True)
    rotation = values.get('profile_rotation', 0)
    selections = [values.get('group_profiles', {}).get(group)]
    if level is not None:
        selections.append(values.get('cross_members', {}).get(level, {}).get('section'))
    for selection in selections:
        if selection is not None:
            definition = selection.get('definition') or definition
            rotation = selection.get('rotation', rotation)
    a, b = definition['width_mm'], definition['height_mm']
    return deepcopy(definition), rotation, (b, a) if rotation % 180 else (a, b)


def validate_selections(values):
    from .profile_library import validate
    groups = values.get('group_profiles', {})
    if not isinstance(groups, dict) or set(groups) - {'posts', 'frame', 'cross'}:
        raise ValueError('Ungültige Profilgruppen.')
    selections = list(groups.values())
    cross = values.get('cross_members', {})
    if not isinstance(cross, dict):
        raise ValueError('Ungültige Querträgereinstellungen.')
    for spec in cross.values():
        if not isinstance(spec, dict):
            raise ValueError('Ungültige Querträgereinstellungen.')
        selections.append(spec.get('section'))
    rotations = [values.get('profile_rotation', 0)]
    for selection in selections:
        if selection is None:
            continue
        if not isinstance(selection, dict):
            raise ValueError('Ungültige Profilauswahl.')
        if selection.get('definition') is not None:
            validate(selection['definition'])
        if 'rotation' in selection:
            rotations.append(selection['rotation'])
    if any(type(r) is not int or r not in (0, 90, 180, 270) for r in rotations):
        raise ValueError('Profildrehung muss 0°, 90°, 180° oder 270° sein.')


def level_depth(values, level):
    frame_height = resolve(values, 'frame')[2][1]
    spec = values.get('cross_members', {}).get(level, {})
    cross_height = resolve(values, 'cross', level)[2][1] if spec.get('count', 0) else 0
    return max(frame_height, cross_height) + values.get('shelf_thickness', 18.0)
