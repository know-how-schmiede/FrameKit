"""Create a simple demo assembly using Fusion's modeling API."""
import json
import adsk.core
import adsk.fusion
from .demo import members, panels, panel_outline
from .version import __version__


def create_frame(design, values):
    layout = [(part, False) for part in members(values)]
    layout.extend((part, True) for part in panels(values))
    assembly = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    assembly.component.name = f'FrameKit Demo {__version__}'
    try:
        for index, ((name, origin, size), is_panel) in enumerate(layout, 1):
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(*(v / 10 for v in origin))
            occurrence = assembly.component.occurrences.addNewComponent(transform)
            component = occurrence.component
            component.name = f'P{index:03d} | {name}'
            sketch = component.sketches.add(component.xYConstructionPlane)
            if is_panel:
                sketch.name = 'Bodenplatte mit Eckausklinkungen'
                outline = panel_outline(size[0], size[1], values['profile'])
                points = [adsk.core.Point3D.create(x / 10, y / 10, 0) for x, y in outline]
                lines = sketch.sketchCurves.sketchLines
                first = lines.addByTwoPoints(points[0], points[1])
                end = first.endSketchPoint
                for point in points[2:]:
                    end = lines.addByTwoPoints(end, point).endSketchPoint
                lines.addByTwoPoints(end, first.startSketchPoint)
            else:
                sketch.name = 'Demo-Rechteck'
                sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(0, 0, 0),
                    adsk.core.Point3D.create(size[0] / 10, size[1] / 10, 0))
            if sketch.profiles.count != 1:
                raise ValueError(f'{name}: keine eindeutige geschlossene Kontur.')
            extrusion = component.features.extrudeFeatures.addSimple(
                sketch.profiles.item(0), adsk.core.ValueInput.createByReal(size[2] / 10),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extrusion.name = name
            extrusion.bodies.item(0).name = name
            sketch.isVisible = False
        assembly.component.attributes.add('FrameKit', 'version', __version__)
        assembly.component.attributes.add('FrameKit', 'demoConfiguration', json.dumps(values))
        return assembly
    except Exception:
        if assembly.isValid:
            assembly.deleteMe()
        raise
