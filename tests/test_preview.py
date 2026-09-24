"""Numerical preview checks and graphics lifetime tests without a Fusion kernel."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

from fusion_addin.FrameKit import accessories, demo, model, preview_data


class PreviewDataTests(unittest.TestCase):
    def test_profiles_match_cut_faces_for_changed_dimensions_and_options(self):
        previous = None
        for values in (demo.DEFAULTS, dict(demo.DEFAULTS, bottom=False, length=90, width=95),
                       dict(demo.DEFAULTS, shelf_count=3, shelf_heights=[None, 400, None]),
                       dict(demo.DEFAULTS, accessory=accessories.PRESETS[0])):
            data = model.build_model(values, previous)
            snapshot = deepcopy(data)
            geometry = preview_data.display_geometry(data)
            expected = [p for part in data['parts'] if part['kind'] == 'profile' for p in part['centerline_mm']]
            self.assertEqual(geometry['profiles'], expected)
            self.assertEqual(data, snapshot)
            hidden = preview_data.display_geometry(data, False, False)
            self.assertEqual(hidden['profiles'], expected)
            self.assertEqual(hidden['panels'], [])
            self.assertEqual(hidden['accessories'], [])
            geometry['profiles'][0][0] = -999
            self.assertEqual(data, snapshot)
            previous = data

    def test_panel_surface_area_cutouts_and_elevations(self):
        for length, width in ((800, 500), (90, 95)):
            values = dict(demo.DEFAULTS, length=length, width=width, shelf_count=2, shelf_heights=[300, None])
            data = model.build_model(values)
            points = preview_data.display_geometry(data)['panels']
            areas = {}
            for i in range(0, len(points), 3):
                a, b, c = points[i:i+3]
                self.assertEqual(a[2], b[2])
                self.assertEqual(a[2], c[2])
                area = ((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]))/2
                self.assertGreater(area, 0)
                areas[a[2]] = areas.get(a[2], 0) + area
                # Interior samples must never fill any of the four post cutouts.
                for u, v, w in ((1/3, 1/3, 1/3), (0.8, 0.1, 0.1), (0.1, 0.8, 0.1)):
                    x, y = [u*a[j]+v*b[j]+w*c[j] for j in (0, 1)]
                    self.assertFalse((x < 40 or x > length-40) and (y < 40 or y > width-40))
            expected_tops = {part['position_mm'][2]+part['geometry']['depth_mm']
                             for part in data['parts'] if part['kind'] == 'panel'}
            self.assertEqual(set(areas), expected_tops)
            for area in areas.values():
                self.assertAlmostEqual(area, length*width-4*40**2)

    def test_support_outline_matches_cylinder_bounds_and_preserves_overhang(self):
        data = model.build_model(dict(demo.DEFAULTS, accessory=accessories.PRESETS[0]))
        points = preview_data.display_geometry(data)['accessories']
        supports = [part for part in data['parts'] if part['kind'] == 'support']
        stride = (32*2*2 + 4*2)
        self.assertEqual(len(points), 4*stride)
        for index, part in enumerate(supports):
            outline = points[index*stride:(index+1)*stride]
            for axis in range(3):
                self.assertAlmostEqual(min(p[axis] for p in outline), part['position_mm'][axis])
                self.assertAlmostEqual(max(p[axis] for p in outline),
                                       part['position_mm'][axis]+part['bounds_mm'][axis])
        self.assertLess(min(p[0] for p in points), 0)


class GraphicsGroup:
    def __init__(self, owner):
        self.owner, self.isValid, self.entities = owner, True, []

    def deleteMe(self):
        self.isValid = False
        self.owner.groups.remove(self)
        return True

    def entity(self, kind, points):
        if self.owner.fail_kind == kind:
            raise RuntimeError('Simulated graphics failure')
        result = NS(kind=kind, points=points, setOpacity=lambda *args: None)
        self.entities.append(result)
        return result

    def addMesh(self, coordinates, *args):
        return self.entity('mesh', coordinates)

    def addLines(self, coordinates, *args):
        return self.entity('lines', coordinates)


class Graphics:
    def __init__(self):
        self.groups, self.fail_kind = [], None

    def add(self):
        group = GraphicsGroup(self)
        self.groups.append(group)
        return group


class PreviewAdapterTests(unittest.TestCase):
    def setUp(self):
        adsk = ModuleType('adsk')
        core, fusion = ModuleType('adsk.core'), ModuleType('adsk.fusion')
        adsk.core, adsk.fusion = core, fusion
        core.Color = NS(create=lambda *args: args)
        fusion.CustomGraphicsCoordinates = NS(create=lambda values: values)
        fusion.CustomGraphicsSolidColorEffect = NS(create=lambda color: color)
        modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': core, 'adsk.fusion': fusion})
        modules.start()
        self.addCleanup(modules.stop)
        path = Path(__file__).resolve().parents[1] / 'fusion_addin/FrameKit/preview.py'
        spec = importlib.util.spec_from_file_location('fusion_addin.FrameKit.preview_under_test', path)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        self.preview = adapter.Preview()
        self.graphics = Graphics()
        self.design = NS(rootComponent=NS(customGraphicsGroups=self.graphics))
        self.model = model.build_model(dict(demo.DEFAULTS, accessory=accessories.PRESETS[0]))

    def test_refresh_toggles_units_and_repeated_cleanup_preserve_foreign_graphics(self):
        foreign = self.graphics.add()
        self.preview.show(self.design, self.model)
        group = self.preview.group
        self.assertFalse(group.isSelectable or group.isChildrenSelectable)
        self.assertEqual(len(group.entities), 3)
        expected = preview_data.display_geometry(self.model)['profiles']
        self.assertEqual(group.entities[0].points, [v/10 for p in expected for v in p])
        self.preview.show(self.design, self.model, False, False)
        self.assertFalse(group.isValid)
        self.assertEqual(len(self.preview.group.entities), 1)
        self.assertEqual(len(self.graphics.groups), 2)
        self.preview.clear()
        self.preview.clear()
        self.assertEqual(self.graphics.groups, [foreign])

    def test_render_failure_removes_partial_graphics(self):
        foreign = self.graphics.add()
        self.graphics.fail_kind = 'mesh'
        with self.assertRaises(RuntimeError):
            self.preview.show(self.design, self.model)
        self.assertEqual(self.graphics.groups, [foreign])
        self.assertIsNone(self.preview.group)

    def test_fusion_rollback_invalidated_graphics_can_be_recreated(self):
        self.preview.show(self.design, self.model)
        self.preview.group.deleteMe()
        self.preview.clear()
        self.preview.show(self.design, self.model)
        self.assertEqual(len(self.graphics.groups), 1)
        self.preview.clear()
        self.assertEqual(self.graphics.groups, [])
