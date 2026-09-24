"""Calculated, JSON-serializable assembly model. Lengths are always millimeters.

Semantic keys identify parts within a frame; retained ID registries make recalculation
independent of geometry and of optional parts. Fusion is only a consumer of this model.
"""
from copy import deepcopy
from uuid import uuid4

from .demo import validate, base_height, shelf_heights, panel_outline

SCHEMA_VERSION = 1
ORIENTATIONS = {
    'x': [[0, 1, 0], [0, 0, 1], [1, 0, 0]],
    'y': [[0, 0, 1], [1, 0, 0], [0, 1, 0]],
    'z': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
}


def build_model(values, previous=None):
    """Recalculate; pass the last model to retain assembly and part identities.

    Shelf keys use the bottom-to-top level index. Removing a middle shelf is not
    yet a supported edit operation (S08); increasing/decreasing count acts at top.
    """
    validate(values)
    if previous is not None:
        if previous.get('schema') != SCHEMA_VERSION:
            raise ValueError('Nicht unterstützte Bauteildaten-Version.')
        frame_id = previous['assembly_id']
        registry = deepcopy(previous['id_registry'])
        ids = list(registry.values())
        if (not isinstance(frame_id, str) or not frame_id
                or len(ids) != len(set(ids))
                or any(not isinstance(value, str) or not value.startswith('P')
                       or not value[1:].isdigit() for value in ids)):
            raise ValueError('Ungültige Bauteil-ID-Zuordnung.')
    else:
        frame_id, registry = uuid4().hex, {}
    next_number = max((int(value[1:]) for value in registry.values()), default=0) + 1
    length, width, height, p = (values[key] for key in ('length', 'width', 'height', 'profile'))
    thickness = values.get('shelf_thickness', 18.0)
    base = base_height(values)
    profile = dict(id=f'demo:square:{p:g}x{p:g}', name=f'{p:g}x{p:g} Demo-Vollprofil',
                   width_mm=p, height_mm=p, material=None, is_demo=True)
    groups = [dict(id='posts', name='01 | Pfosten'), dict(id='top', name='02 | Rahmen oben')]
    levels = [('top', 'oben', height)]
    if values['bottom']:
        groups.append(dict(id='bottom', name='03 | Rahmen unten'))
        levels.append(('bottom', 'unten', base+p+thickness))
    for index, top in enumerate(shelf_heights(values), 1):
        key = f'shelf:{index:02d}'
        groups.append(dict(id=key, name=f'{index+3:02d} | Boden {index:02d}'))
        levels.append((key, f'Boden {index:02d}', top))
    if values.get('accessory') is not None:
        groups.append(dict(id='accessories', name='90 | Füße und Rollen'))
    groups.append(dict(id='connections', name='91 | Verbindungen', reserved=True))
    parts = []

    def add(key, kind, group, function, origin, bounds, shape, axis='z'):
        nonlocal next_number
        if key not in registry:
            registry[key] = f'P{next_number:03d}'
            next_number += 1
        part_id = registry[key]
        part = dict(id=part_id, uid=f'{frame_id}/{part_id}', key=key, kind=kind,
                    group_id=group, function=function, position_mm=list(origin),
                    orientation=deepcopy(ORIENTATIONS[axis]), bounds_mm=list(bounds),
                    geometry=shape, profile_ref=None, cut_length_mm=None,
                    centerline_mm=None, is_placeholder=kind == 'support')
        if kind == 'profile':
            part['profile_ref'] = profile['id']
            part['cut_length_mm'] = shape['depth_mm']
            u, v, w = part['orientation']
            start = [origin[i] + p/2*(u[i]+v[i]) for i in range(3)]
            end = [start[i] + shape['depth_mm']*w[i] for i in range(3)]
            part['centerline_mm'] = [start, end]
            detail = f'{profile["name"]} | L={shape["depth_mm"]:g} mm'
        elif kind == 'panel':
            detail = f'{length:g}x{width:g}x{thickness:g} mm | ausgeklinkt'
        else:
            part['accessory_definition'] = deepcopy(values['accessory'])
            detail = f'Ø={bounds[0]:g} mm | H={bounds[2]:g} mm'
        part['display_name'] = f'{part_id} | {function} | {detail}'
        parts.append(part)

    for x, side, side_key in ((0, 'links', 'left'), (length-p, 'rechts', 'right')):
        for y, depth, depth_key in ((0, 'vorne', 'front'), (width-p, 'hinten', 'back')):
            add(f'post:{depth_key}:{side_key}', 'profile', 'posts', f'Pfosten {depth} {side}',
                (x, y, base), (p, p, height-base),
                dict(type='rectangle', width_mm=p, height_mm=p, depth_mm=height-base))
    for group, label, top in levels:
        z = top-thickness-p
        for y, side, key in ((0, 'vorne', 'front'), (width-p, 'hinten', 'back')):
            add(f'{group}:beam:{key}', 'profile', group, f'Rahmen {label} {side}',
                (p, y, z), (length-2*p, p, p),
                dict(type='rectangle', width_mm=p, height_mm=p, depth_mm=length-2*p), 'x')
        for x, side, key in ((0, 'links', 'left'), (length-p, 'rechts', 'right')):
            add(f'{group}:beam:{key}', 'profile', group, f'Rahmen {label} {side}',
                (x, p, z), (p, width-2*p, p),
                dict(type='rectangle', width_mm=p, height_mm=p, depth_mm=width-2*p), 'y')
        add(f'{group}:panel', 'panel', group, f'{label} Platte', (0, 0, top-thickness),
            (length, width, thickness), dict(type='polygon',
                points_mm=[list(point) for point in panel_outline(length, width, p)], depth_mm=thickness))
    spec = values.get('accessory')
    if spec is not None:
        radius = spec['diameter']/2
        for x, side, side_key in ((p/2, 'links', 'left'), (length-p/2, 'rechts', 'right')):
            for y, depth, depth_key in ((p/2, 'vorne', 'front'), (width-p/2, 'hinten', 'back')):
                add(f'support:{depth_key}:{side_key}', 'support', 'accessories',
                    f'{spec["kind"]} {depth} {side} | {spec["name"]} | Platzhalter',
                    (x-radius, y-radius, 0), (2*radius, 2*radius, spec['height']),
                    dict(type='circle', center_mm=[radius, radius], radius_mm=radius,
                         depth_mm=spec['height']))
    return dict(schema=SCHEMA_VERSION, units='mm', assembly_id=frame_id,
                id_registry=registry, configuration=deepcopy(values), groups=groups,
                profiles={profile['id']: profile}, parts=parts)
