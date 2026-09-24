"""Create a simple demo assembly using Fusion's modeling API."""
import json
import adsk.core
import adsk.fusion
from .demo import members
from .version import __version__


def create_frame(design, values):
    layout = members(values)
    assembly = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    assembly.component.name = f'FrameKit Demo {__version__}'
    try:
        for index, (name, origin, size) in enumerate(layout, 1):
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(*(v / 10 for v in origin))
            occurrence = assembly.component.occurrences.addNewComponent(transform)
            component = occurrence.component
            component.name = f'P{index:03d} | {name}'
            sketch = component.sketches.add(component.xYConstructionPlane)
            sketch.name = 'Demo-Rechteck'
            sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(0, 0, 0),
                adsk.core.Point3D.create(size[0] / 10, size[1] / 10, 0))
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
