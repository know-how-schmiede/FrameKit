"""Build Fusion components exclusively from the calculated assembly model."""
import json
import adsk.core
import adsk.fusion
from .model import build_model
from .version import __version__


def _json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def _set_attributes(component, values):
    for key, value in values.items():
        component.attributes.add('FrameKit', key, value)


def _create_part(parent, part, frame_id):
    transform = adsk.core.Matrix3D.create()
    axes = [adsk.core.Vector3D.create(*axis) for axis in part['orientation']]
    if not transform.setWithCoordinateSystem(
            adsk.core.Point3D.create(*(v / 10 for v in part['position_mm'])), *axes):
        raise ValueError(f'{part["id"]}: ungültige Bauteilausrichtung.')
    occurrence = parent.occurrences.addNewComponent(transform)
    component = occurrence.component
    component.name = part['display_name']
    component.partNumber = part['id']
    component.description = part['function']
    sketch = component.sketches.add(component.xYConstructionPlane)
    shape = part['geometry']
    if shape['type'] == 'circle':
        sketch.name = 'Fuß-/Rollenplatzhalter (Zylinder)'
        x, y = shape['center_mm']
        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(x / 10, y / 10, 0), shape['radius_mm'] / 10)
    elif shape['type'] == 'polygon':
        sketch.name = 'Bodenplatte mit Eckausklinkungen'
        points = [adsk.core.Point3D.create(x / 10, y / 10, 0) for x, y in shape['points_mm']]
        lines = sketch.sketchCurves.sketchLines
        first = lines.addByTwoPoints(points[0], points[1])
        end = first.endSketchPoint
        for point in points[2:]:
            end = lines.addByTwoPoints(end, point).endSketchPoint
        lines.addByTwoPoints(end, first.startSketchPoint)
    elif shape['type'] == 'rectangle':
        sketch.name = 'Demo-Profilquerschnitt'
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(shape['width_mm'] / 10, shape['height_mm'] / 10, 0))
    else:
        raise ValueError(f'Unbekannte Geometrie: {shape["type"]}')
    if sketch.profiles.count != 1:
        raise ValueError(f'{part["id"]}: keine eindeutige geschlossene Kontur.')
    extrusion = component.features.extrudeFeatures.addSimple(
        sketch.profiles.item(0), adsk.core.ValueInput.createByReal(shape['depth_mm'] / 10),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extrusion.name = f'{part["id"]} | Extrusion'
    extrusion.bodies.item(0).name = part['display_name']
    sketch.isVisible = False
    _set_attributes(component, {
        'schemaVersion': '1', 'assemblyId': frame_id, 'partId': part['id'],
        'partUid': part['uid'], 'partKey': part['key'], 'kind': part['kind'],
        'function': part['function'], 'groupId': part['group_id'],
        'profileRef': part['profile_ref'] or '', 'units': 'mm',
        'positionMm': _json(part['position_mm']), 'orientation': _json(part['orientation']),
        'cutLengthMm': '' if part['cut_length_mm'] is None else str(part['cut_length_mm']),
        'placeholder': 'true' if part['is_placeholder'] else 'false', 'partData': _json(part),
    })
    return occurrence, extrusion


def _create_layout(component, model):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'FrameKit | Profilmittellinien (fixiert)'
    sketch.isComputeDeferred = True
    try:
        for part in model['parts']:
            if part['centerline_mm'] is None:
                continue
            points = [adsk.core.Point3D.create(*(value / 10 for value in point))
                      for point in part['centerline_mm']]
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(*points)
            line.isConstruction = True
            line.isFixed = True
            _set_attributes(line, {'partId': part['id'], 'partUid': part['uid']})
    finally:
        sketch.isComputeDeferred = False
    sketch.isVisible = False
    _set_attributes(sketch, {'assemblyId': model['assembly_id'], 'generated': 'true',
                            'inputSource': 'configuration', 'units': 'mm'})
    return sketch


def create_frame(design, values, calculated_model=None):
    model = calculated_model if calculated_model is not None else build_model(values)
    if model['configuration'] != values:
        raise ValueError('Vorschau und Eingaben stimmen nicht überein.')
    frame_id = model['assembly_id']
    prefix = f'FrameKit {frame_id[:8]}'
    parametric = design.designType == adsk.fusion.DesignTypes.ParametricDesignType
    if parametric:
        design.timeline.moveToEnd()
    assembly = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    assembly.component.name = f'FrameKit {__version__} | {frame_id[:8]}'
    timeline_groups = []
    try:
        containers = {}
        last_container = assembly
        for group in model['groups']:
            last_container = assembly.component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            component = last_container.component
            component.name = group['name']
            _set_attributes(component, {'assemblyId': frame_id, 'groupId': group['id'],
                'reserved': 'true' if group.get('reserved') else 'false'})
            containers[group['id']] = component
        ranges = []
        layout = _create_layout(containers['layout'], model)
        if parametric:
            ranges.append((assembly.timelineObject, layout.timelineObject, f'{prefix} | Struktur und Layout'))
        # Each part's creation, sketch and extrusion remain sequential and independent.
        for part in model['parts']:
            occurrence, extrusion = _create_part(containers[part['group_id']], part, frame_id)
            if parametric:
                ranges.append((occurrence.timelineObject, extrusion.timelineObject,
                               f'{prefix} | {part["display_name"]}'))
        if parametric:
            # Freeze indices before grouping; group from back to front, without nesting.
            indices = [(first.index, last.index, name) for first, last, name in ranges]
            for start, end, name in reversed(indices):
                group = design.timeline.timelineGroups.add(start, end)
                if group is None:
                    raise RuntimeError(f'Zeitleistengruppe konnte nicht erstellt werden: {name}')
                timeline_groups.append(group)
                group.name = name
            for group in timeline_groups:
                group.isCollapsed = True
        _set_attributes(assembly.component, {
            'version': __version__, 'assemblyId': frame_id, 'schemaVersion': str(model['schema']),
            'modelData': _json(model),
            'configuration': _json({'schema': 1, 'version': __version__, 'values': model['configuration']}),
            'demoConfiguration': _json(model['configuration']),
            'timelineMode': 'grouped' if parametric else 'direct-no-timeline',
        })
        return assembly
    except Exception:
        for group in reversed(timeline_groups):
            try:
                if group.isValid:
                    group.deleteMe(False)
            except Exception:
                pass  # The execute handler also aborts the entire Fusion transaction.
        if assembly.isValid:
            assembly.deleteMe()
        raise
