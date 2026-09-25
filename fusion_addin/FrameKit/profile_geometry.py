"""Native Fusion sketch/extrusion of the exact, centered DXF primitives."""
from math import isclose
import adsk.core
import adsk.fusion
from .dxf_profile import arc_point


def draw_section(sketch, spec):
    def point(xy):
        return adsk.core.Point3D.create(xy[0]/10, xy[1]/10, 0)

    sketch.isComputeDeferred = True
    try:
        for index, curve in enumerate(spec['curves']):
            kind = curve['type']
            if kind == 'line':
                entity = sketch.sketchCurves.sketchLines.addByTwoPoints(
                    point(curve['start']), point(curve['end']))
            elif kind == 'circle':
                entity = sketch.sketchCurves.sketchCircles.addByCenterRadius(
                    point(curve['center']), curve['radius']/10)
            elif kind == 'arc':
                entity = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(
                    point(curve['center']), point(arc_point(curve, curve['start_angle'])), curve['sweep'])
            else:
                raise ValueError('Unbekanntes Profilsegment.')
            if entity is None:
                raise ValueError('Fusion konnte eine DXF-Kurve nicht erstellen.')
            entity.attributes.add('FrameKit', 'sourceCurve', str(index))
    finally:
        sketch.isComputeDeferred = False
    return material_region(sketch, spec)


def material_region(sketch, spec):
    """Select the ONE region using every input curve exactly once, holes excluded.

    A hole also appears as a standalone Fusion profile. Never extrude all profiles
    or just profiles.item(0): both would silently fill real extrusion cavities.
    Splits, duplicate lines, islands, intersections and nested material are rejected.
    """
    matches = []
    expected = sorted(str(i) for i in range(len(spec['curves'])))
    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        loops = profile.profileLoops
        if loops.count != spec['loop_count']:
            continue
        used = []
        for j in range(loops.count):
            curves = loops.item(j).profileCurves
            for k in range(curves.count):
                attribute = curves.item(k).sketchEntity.attributes.itemByName('FrameKit', 'sourceCurve')
                used.append(attribute.value if attribute else None)
        if None in used or sorted(used) != expected:
            continue
        area = profile.areaProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy).area*100
        if isclose(area, spec['area_mm2'], rel_tol=1e-5, abs_tol=1e-5):
            matches.append(profile)
    if len(matches) != 1:
        raise ValueError('DXF ergibt keine eindeutige zusammenhängende Materialfläche mit Hohlräumen. '
                         'Doppelte, sich kreuzende, offene oder getrennte Konturen prüfen.')
    return matches[0]


def validate_in_fusion(design, spec):
    """Temporary 1 mm extrusion; always remove test geometry, also after failures."""
    occurrence = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    try:
        component = occurrence.component
        component.name = 'FrameKit | DXF-Importprüfung (temporär)'
        sketch = component.sketches.add(component.xYConstructionPlane)
        region = draw_section(sketch, spec)
        feature = component.features.extrudeFeatures.addSimple(
            region, adsk.core.ValueInput.createByReal(0.1),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        if feature is None or feature.bodies.count != 1:
            raise ValueError('DXF muss genau einen extrudierbaren Profilkörper ergeben.')
    finally:
        if occurrence.isValid:
            occurrence.deleteMe()
