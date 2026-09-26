from copy import deepcopy
import importlib.util
from math import pi, sqrt, tan
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

from fusion_addin.FrameKit import demo, model, accessories


class CameraTests(unittest.TestCase):
    def test_fit_bounds_units_and_camera_types_with_accessory_overhang(self):
        adsk = ModuleType('adsk')
        adsk.core = ModuleType('adsk.core')
        adsk.core.Point3D = NS(create=lambda x, y, z: NS(x=x, y=y, z=z))
        adsk.core.CameraTypes = NS(OrthographicCameraType=0)
        path = Path(__file__).parents[1]/'fusion_addin/FrameKit/preview_camera.py'
        with patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': adsk.core}):
            spec = importlib.util.spec_from_file_location('camera_under_test', path)
            adapter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(adapter)
            data = model.build_model(dict(demo.DEFAULTS, accessory=accessories.PRESETS[1]))
            original = deepcopy(data)
            for kind in (0, 1, 2):
                for width, height in ((1920, 1080), (700, 1200)):
                    extents = []
                    camera = NS(eye=NS(x=0, y=0, z=100), target=NS(x=0, y=0, z=0),
                        cameraType=kind, perspectiveAngle=pi/4,
                        setExtents=lambda w, h: extents.append((w, h)) or True)
                    viewport = NS(camera=camera, width=width, height=height)
                    adapter.fit_preview(viewport, data)
                    self.assertEqual((camera.target.x, camera.target.y, camera.target.z), (40, 25, 37.5))
                    self.assertEqual(camera.cameraType, kind)
                    self.assertFalse(camera.isFitView)
                    self.assertEqual(camera.eye.x, camera.target.x)
                    self.assertEqual(camera.eye.y, camera.target.y)
                    radius = sqrt(83.5**2+53.5**2+75**2)/2
                    if kind == 0:
                        self.assertGreater(extents[0][0], 2*radius)
                        self.assertEqual(extents[0][0], extents[0][1])
                    else:
                        self.assertEqual(extents, [])
                        distance = camera.eye.z-camera.target.z
                        self.assertGreater((distance-radius)*tan(pi/8), radius*0.75)
                    self.assertEqual(data, original)
