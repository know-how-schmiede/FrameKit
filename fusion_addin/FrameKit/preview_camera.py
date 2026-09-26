"""Fit only the calculated frame, independent of other document geometry."""
from math import atan, isfinite, sin, sqrt, tan
import adsk.core


def fit_preview(viewport, model):
    parts = model['parts']
    low = [min(p['bounds_origin_mm'][i] for p in parts)/10 for i in range(3)]
    high = [max(p['bounds_origin_mm'][i]+p['bounds_mm'][i] for p in parts)/10 for i in range(3)]
    center = [(a+b)/2 for a, b in zip(low, high)]
    # A padded enclosing sphere fits from every viewing direction, including overhangs.
    radius = sqrt(sum((b-a)**2 for a, b in zip(low, high)))/2 * 1.12
    camera = viewport.camera
    direction = [getattr(camera.eye, axis)-getattr(camera.target, axis) for axis in ('x', 'y', 'z')]
    length = sqrt(sum(value*value for value in direction))
    if length <= 1e-9:
        raise ValueError('Kamerarichtung ist nicht definiert.')
    distance = max(length, 2*radius)
    orthographic = camera.cameraType == adsk.core.CameraTypes.OrthographicCameraType
    if not orthographic:
        angle = camera.perspectiveAngle
        if not isfinite(angle) or not 0 < angle < 3.14:
            raise ValueError('Ungültiger Perspektivwinkel.')
        aspect = max(viewport.width, 1)/max(viewport.height, 1)
        # Conservatively account for either horizontal or vertical field-of-view convention.
        half_angle = atan(tan(angle/2)*min(aspect, 1/aspect))
        distance = radius/sin(half_angle)
    camera.target = adsk.core.Point3D.create(*center)
    camera.eye = adsk.core.Point3D.create(*(center[i]+direction[i]/length*distance for i in range(3)))
    camera.isFitView = False
    camera.isSmoothTransition = False
    if orthographic and not camera.setExtents(2*radius, 2*radius):
        raise ValueError('Ansichtsbereich konnte nicht angepasst werden.')
    viewport.camera = camera
