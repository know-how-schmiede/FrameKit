"""Calculated, JSON-serializable assembly model. Lengths are always millimeters.

Semantic keys identify parts within a frame; retained ID registries make recalculation
independent of geometry and of optional parts. Fusion is only a consumer of this model.
"""
from copy import deepcopy
from uuid import uuid4

from .demo import validate, base_height, shelf_heights, panel_outline
from .sections import resolve, level_depth
from .accessories import corner_specs

SCHEMA_VERSION = 1
ORIENTATIONS = {
    'x': [[0, 1, 0], [0, 0, 1], [1, 0, 0]],
    'y': [[0, 0, 1], [1, 0, 0], [0, 1, 0]],
    'z': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
}


def build_model(values, previous=None):
    """Recalculate; pass the last model to retain assembly and part identities.

    Shelf keys use the bottom-to-top level index. Removing a middle shelf is not
    a supported edit operation; increasing/decreasing count acts at top.
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
    length, width, height = (values[key] for key in ('length', 'width', 'height'))
    thickness = values.get('shelf_thickness', 18.0)
    base = base_height(values)
    on_top = values.get('top_panel_mount', 'notched') == 'on_top'
    post_top = height - thickness if on_top else height
    px, py = resolve(values, 'posts')[2]
    fw, fh = resolve(values, 'frame')[2]
    profiles = {}
    groups = [dict(id='layout', name='00 | Layout'), dict(id='posts', name='01 | Pfosten'),
              dict(id='top', name='02 | Rahmen oben')]
    levels = [('top', 'oben', height)]
    if values['bottom']:
        groups.append(dict(id='bottom', name='03 | Rahmen unten'))
        levels.append(('bottom', 'unten', base+level_depth(values, 'bottom')))
    for index, top in enumerate(shelf_heights(values), 1):
        key = f'shelf:{index:02d}'
        groups.append(dict(id=key, name=f'{index+3:02d} | Boden {index:02d}'))
        levels.append((key, f'Boden {index:02d}', top))
    support_specs = corner_specs(values)
    if any(spec is not None for spec in support_specs.values()):
        groups.append(dict(id='accessories', name='90 | Füße und Rollen'))
    brackets_enabled = values.get('brackets', False)
    groups.append(dict(id='connections', name='91 | Winkel' if brackets_enabled
                       else '91 | Verbindungen', reserved=not brackets_enabled))
    parts = []

    def add(key, kind, group, function, origin, bounds, shape, axis='z', section=None):
        nonlocal next_number
        if key not in registry:
            registry[key] = f'P{next_number:03d}'
            next_number += 1
        part_id = registry[key]
        part = dict(id=part_id, uid=f'{frame_id}/{part_id}', key=key, kind=kind,
                    group_id=group, function=function, position_mm=list(origin),
                    orientation=deepcopy(ORIENTATIONS[axis]), bounds_mm=list(bounds),
                    bounds_origin_mm=list(origin),
                    geometry=shape, profile_ref=None, cut_length_mm=None,
                    centerline_mm=None, is_placeholder=kind == 'support')
        if kind == 'profile':
            profile, rotation, _ = section
            profiles[profile['id']] = profile
            part['profile_ref'] = profile['id']
            part['section_rotation_deg'] = rotation
            part['cut_length_mm'] = shape['depth_mm']
            part['end_treatment'] = 'Beidseitig rechtwinklig; keine weitere Bearbeitung'
            # In horizontal beams local section width is horizontal, height vertical.
            axes = (ORIENTATIONS[axis] if axis != 'y'
                    else [[1, 0, 0], [0, 0, -1], [0, 1, 0]])
            if profile['is_demo'] and rotation == 0:
                # Retain the legacy transform for the symmetric demo square.
                axes = ORIENTATIONS[axis]
            u, v, w = [list(a) for a in axes]
            for _ in range(rotation//90):
                u, v = v, [-n for n in u]
            part['orientation'] = [u, v, w]
            start = [origin[i] + bounds[i]/2 - shape['depth_mm']*w[i]/2 for i in range(3)]
            end = [start[i] + shape['depth_mm']*w[i] for i in range(3)]
            part['centerline_mm'] = [start, end]
            if not profile['is_demo']:
                part['position_mm'] = start
                part['geometry'] = dict(type='dxf', depth_mm=shape['depth_mm'])
            else:
                part['position_mm'] = [start[i] - profile['width_mm']*u[i]/2
                                       - profile['height_mm']*v[i]/2 for i in range(3)]
                shape.update(width_mm=profile['width_mm'], height_mm=profile['height_mm'])
            detail = f'{profile["name"]} | L={shape["depth_mm"]:g} mm'
        elif kind == 'panel':
            finish = 'ohne Aussparungen' if group == 'top' and on_top else 'ausgeklinkt'
            detail = f'{length:g}x{width:g}x{thickness:g} mm | {finish}'
        elif kind == 'connection':
            detail = 'STEP-Bauteil | ohne Schrauben/Muttern'
        else:
            part['accessory_definition'] = deepcopy(support_specs[key.removeprefix('support:')])
            part['mounting_position_mm'] = [origin[0]+bounds[0]/2, origin[1]+bounds[1]/2, bounds[2]]
            detail = f'Ø={bounds[0]:g} mm | H={bounds[2]:g} mm'
        part['display_name'] = f'{part_id} | {function} | {detail}'
        parts.append(part)

    post_section = resolve(values, 'posts')
    frame_section = resolve(values, 'frame')
    for x, side, side_key in ((0, 'links', 'left'), (length-px, 'rechts', 'right')):
        for y, depth, depth_key in ((0, 'vorne', 'front'), (width-py, 'hinten', 'back')):
            add(f'post:{depth_key}:{side_key}', 'profile', 'posts', f'Pfosten {depth} {side}',
                (x, y, base), (px, py, post_top-base),
                dict(type='rectangle', depth_mm=post_top-base), section=post_section)
    for group, label, top in levels:
        z = top-thickness-fh
        for y, side, key in ((0, 'vorne', 'front'), (width-fw, 'hinten', 'back')):
            add(f'{group}:beam:{key}', 'profile', group, f'Rahmen {label} {side}',
                (px, y, z), (length-2*px, fw, fh),
                dict(type='rectangle', depth_mm=length-2*px), 'x', frame_section)
        for x, side, key in ((0, 'links', 'left'), (length-fw, 'rechts', 'right')):
            add(f'{group}:beam:{key}', 'profile', group, f'Rahmen {label} {side}',
                (x, py, z), (fw, width-2*py, fh),
                dict(type='rectangle', depth_mm=width-2*py), 'y', frame_section)
        spec = values.get('cross_members', {}).get(group, {'count': 0, 'direction': 'quer'})
        cross_section = resolve(values, 'cross', group)
        cw, ch = cross_section[2]
        count = spec['count']
        transverse = spec['direction'] == 'quer'
        span, run = (length, width) if transverse else (width, length)
        gap = (span - 2*fw - count*cw) / (count+1)
        for index in range(count):
            offset = fw + gap + index*(cw+gap)
            cross_z = top-thickness-ch
            origin = (offset, fw, cross_z) if transverse else (fw, offset, cross_z)
            bounds = (cw, run-2*fw, ch) if transverse else (run-2*fw, cw, ch)
            add(f'{group}:cross:{index+1:02d}', 'profile', group,
                f'Querträger {label} {index+1:02d}', origin, bounds,
                dict(type='rectangle', depth_mm=run-2*fw),
                'y' if transverse else 'x', cross_section)
        outline = ([(0, 0), (length, 0), (length, width), (0, width)]
                   if group == 'top' and on_top else panel_outline(length, width, px, py))
        add(f'{group}:panel', 'panel', group, f'{label} Platte', (0, 0, top-thickness),
            (length, width, thickness), dict(type='polygon',
                points_mm=[list(point) for point in outline], depth_mm=thickness))
    for x, side, side_key in ((px/2, 'links', 'left'), (length-px/2, 'rechts', 'right')):
        for y, depth, depth_key in ((py/2, 'vorne', 'front'), (width-py/2, 'hinten', 'back')):
            spec = support_specs[f'{depth_key}:{side_key}']
            if spec is None:
                continue
            radius = spec['diameter']/2
            add(f'support:{depth_key}:{side_key}', 'support', 'accessories',
                f'{spec["kind"]} {depth} {side} | {spec["name"]} | Platzhalter',
                (x-radius, y-radius, 0), (2*radius, 2*radius, spec['height']),
                dict(type='circle', center_mm=[radius, radius], radius_mm=radius,
                     depth_mm=spec['height']))
    connection_warnings = []
    if brackets_enabled:
        from .connections import generate
        brackets, connection_warnings = generate(parts, profiles, values.get('brackets_double', False))
        for bracket in brackets:
            add(bracket['key'], 'connection', 'connections',
                f'Winkel {bracket["size"]}x{bracket["size"]} | {bracket["label"]}',
                bracket['origin'], bracket['bounds'],
                dict(type='step', points_mm=bracket['points'], depth_mm=bracket['size'],
                     size_mm=bracket['size'], source=f'Winkel_{bracket["size"]}x{bracket["size"]}.step'))
            parts[-1]['bounds_origin_mm'] = bracket['bounds_origin']
            parts[-1]['orientation'] = bracket['orientation']
            parts[-1]['connection_definition'] = dict(size_mm=bracket['size'],
                mounting_width_mm=bracket['size'], member_keys=bracket['members'],
                parallel_count=bracket['parallel_count'], fastening_complete=False)
    return dict(schema=SCHEMA_VERSION, units='mm', assembly_id=frame_id,
                id_registry=registry, configuration=deepcopy(values), groups=groups,
                profiles=profiles, parts=parts, connection_warnings=connection_warnings)
