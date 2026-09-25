"""Exercise Fusion adapter contracts with a small API double, not a CAD kernel."""
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

from fusion_addin.FrameKit import accessories, demo, model


class Matrix:
    def setWithCoordinateSystem(self, origin, *axes):
        self.origin, self.axes = origin, axes
        return True


class Attributes(dict):
    def add(self, group, name, value):
        self[(group, name)] = value


class Component:
    def __init__(self, design):
        self.design, self.children, self.sketch_list, self.extrusions = design, [], [], []
        self.name = ''
        self.attributes = Attributes()
        self.occurrences = NS(addNewComponent=self.add_component)
        self.xYConstructionPlane = object()
        self.sketches = NS(add=self.add_sketch)
        self.features = NS(extrudeFeatures=NS(addSimple=self.extrude))

    def add_component(self, transform):
        component = Component(self.design)
        occurrence = NS(component=component, transform=transform, timelineObject=self.design.tick(), isValid=True)

        def delete():
            occurrence.isValid = False
            self.children.remove(occurrence)

        occurrence.deleteMe = delete
        self.children.append(occurrence)
        return occurrence

    def add_sketch(self, plane):
        sketch = NS(points=[], lines=[], attributes=Attributes(), circle=None, timelineObject=self.design.tick(),
                    profiles=NS(count=1, item=lambda index: object()))

        def line(start, end):
            if self.design.fail_line:
                raise RuntimeError('Simulated layout failure')
            sketch.points.extend((start, end))
            result = NS(startSketchPoint=start, endSketchPoint=end, attributes=Attributes())
            sketch.lines.append(result)
            return result

        def circle(center, radius):
            sketch.circle = (center, radius)

        sketch.sketchCurves = NS(sketchLines=NS(addByTwoPoints=line, addTwoPointRectangle=line),
                                sketchCircles=NS(addByCenterRadius=circle))
        self.sketch_list.append(sketch)
        return sketch

    def extrude(self, profile, distance, operation):
        if self.design.fail_extrude:
            raise RuntimeError('Simulated extrusion failure')
        body = NS(name='')
        feature = NS(timelineObject=self.design.tick(), distance=distance, profile=profile, bodies=NS(item=lambda index: body))
        self.extrusions.append(feature)
        return feature


class Design:
    def __init__(self, parametric=True):
        self.designType = 1 if parametric else 0
        self.events, self.groups, self.calls = [], [], []
        self.fail_extrude = False
        self.fail_line = False
        self.fail_group_at = None
        self.timeline = NS(moveToEnd=lambda: None, timelineGroups=NS(add=self.add_group))
        self.rootComponent = Component(self)

    def tick(self):
        event = NS(index=len(self.events))
        self.events.append(event)
        return event

    def add_group(self, start, end):
        self.calls.append((start, end))
        if len(self.calls) == self.fail_group_at:
            raise RuntimeError('Simulated grouping failure')
        if any(not (end < group.start or start > group.end) for group in self.groups):
            raise AssertionError('Nested or overlapping timeline groups')
        group = NS(start=start, end=end, isValid=True)

        def delete(contents):
            assert contents is False
            group.isValid = False
            self.groups.remove(group)

        group.deleteMe = delete
        self.groups.append(group)
        return group


class GeometryAdapterTests(unittest.TestCase):
    def setUp(self):
        adsk = ModuleType('adsk')
        core, fusion = ModuleType('adsk.core'), ModuleType('adsk.fusion')
        adsk.core, adsk.fusion = core, fusion
        core.Matrix3D = NS(create=Matrix)
        core.Point3D = core.Vector3D = NS(create=lambda *values: values)
        core.ValueInput = NS(createByReal=lambda value: value)
        fusion.DesignTypes = NS(ParametricDesignType=1)
        fusion.FeatureOperations = NS(NewBodyFeatureOperation=0)
        self.modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': core, 'adsk.fusion': fusion})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        path = Path(__file__).resolve().parents[1] / 'fusion_addin/FrameKit/geometry.py'
        spec = importlib.util.spec_from_file_location('fusion_addin.FrameKit.geometry_under_test', path)
        self.adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.adapter)

    def test_hierarchy_attributes_orientations_and_nonoverlapping_timeline(self):
        design = Design()
        foreign = design.rootComponent.add_component(Matrix())
        values = dict(demo.DEFAULTS, shelf_count=1, shelf_heights=[300], accessory=accessories.PRESETS[0])
        assembly = self.adapter.create_frame(design, values)
        data = json.loads(assembly.component.attributes['FrameKit', 'modelData'])
        groups = {group.component.attributes['FrameKit', 'groupId']: group.component for group in assembly.component.children}
        self.assertEqual(set(groups), {group['id'] for group in data['groups']})
        self.assertEqual(len(design.groups), len(data['parts']) + 1)
        self.assertEqual(design.calls, sorted(design.calls, reverse=True))
        self.assertTrue(all(group.start > foreign.timelineObject.index for group in design.groups))
        for part in data['parts']:
            occurrence = next(child for child in groups[part['group_id']].children
                              if child.component.attributes['FrameKit', 'partId'] == part['id'])
            attrs = occurrence.component.attributes
            self.assertEqual(occurrence.component.partNumber, part['id'])
            self.assertEqual(occurrence.component.description, part['function'])
            self.assertEqual(json.loads(attrs['FrameKit', 'partData']), part)
            self.assertEqual(occurrence.transform.origin, tuple(value/10 for value in part['position_mm']))
            self.assertEqual(occurrence.transform.axes, tuple(tuple(axis) for axis in part['orientation']))
            self.assertEqual(occurrence.component.extrusions[0].distance, part['geometry']['depth_mm']/10)
        other = self.adapter.create_frame(design, values)
        self.assertNotEqual(assembly.component.attributes['FrameKit', 'assemblyId'], other.component.attributes['FrameKit', 'assemblyId'])
        self.assertTrue(foreign.isValid)

    def test_failure_cleans_own_assembly_and_groups(self):
        for failure in ('layout', 'extrusion', 'group'):
            with self.subTest(failure=failure):
                design = Design()
                foreign = design.rootComponent.add_component(Matrix())
                design.fail_extrude = failure == 'extrusion'
                design.fail_line = failure == 'layout'
                design.fail_group_at = 3 if failure == 'group' else None
                with self.assertRaises(RuntimeError):
                    self.adapter.create_frame(design, demo.DEFAULTS)
                self.assertEqual(design.rootComponent.children, [foreign])
                self.assertEqual(design.groups, [])

    def test_layout_is_fixed_hidden_and_matches_preview_model_in_both_modes(self):
        values = dict(demo.DEFAULTS, shelf_count=2, shelf_heights=[300, None], accessory=accessories.PRESETS[0])
        calculated = model.build_model(values)
        for parametric in (True, False):
            with self.subTest(parametric=parametric):
                design = Design(parametric)
                assembly = self.adapter.create_frame(design, values, calculated)
                saved = json.loads(assembly.component.attributes['FrameKit', 'modelData'])
                self.assertEqual(saved, calculated)
                layout = next(child.component for child in assembly.component.children
                              if child.component.attributes['FrameKit', 'groupId'] == 'layout')
                sketch, = layout.sketch_list
                self.assertFalse(sketch.isVisible)
                self.assertFalse(sketch.isComputeDeferred)
                profiles = [part for part in saved['parts'] if part['kind'] == 'profile']
                self.assertEqual(len(sketch.lines), len(profiles))
                for line, part in zip(sketch.lines, profiles):
                    self.assertTrue(line.isFixed and line.isConstruction)
                    self.assertEqual(line.attributes['FrameKit', 'partUid'], part['uid'])
                    self.assertEqual([line.startSketchPoint, line.endSketchPoint],
                                     [tuple(v/10 for v in p) for p in part['centerline_mm']])

    def test_stale_preview_cannot_create_geometry(self):
        design = Design()
        with self.assertRaises(ValueError):
            self.adapter.create_frame(design, dict(demo.DEFAULTS, length=900), model.build_model(demo.DEFAULTS))
        self.assertEqual(design.rootComponent.children, [])

    def test_direct_mode_does_not_change_design_type(self):
        design = Design(parametric=False)
        assembly = self.adapter.create_frame(design, demo.DEFAULTS)
        self.assertEqual(design.designType, 0)
        self.assertEqual(design.groups, [])
        self.assertEqual(assembly.component.attributes['FrameKit', 'timelineMode'], 'direct-no-timeline')

    def test_dxf_profiles_use_centered_origins_and_selected_hollow_region(self):
        from fusion_addin.FrameKit import profile_library
        from test_profile_library import FIXTURE
        definition, _ = profile_library.prepare(FIXTURE, 'Synthetic')
        values = dict(demo.DEFAULTS, profile_definition=definition,
                      cross_members={'top': dict(count=2, direction='quer')})
        native = ModuleType('profile_geometry')
        material_region = object()
        drawn = []
        def draw(sketch, spec):
            drawn.append(spec)
            sketch.profiles.count = 6  # Material and five hole interiors.
            return material_region
        native.draw_section = draw
        with patch.dict(sys.modules, {'fusion_addin.FrameKit.profile_geometry': native}):
            design = Design()
            assembly = self.adapter.create_frame(design, values)
        data = json.loads(assembly.component.attributes['FrameKit', 'modelData'])
        parts = {part['id']: part for part in data['parts']}
        self.assertEqual(len(drawn), 14)
        for group in assembly.component.children:
            for occurrence in group.component.children:
                part = parts[occurrence.component.partNumber]
                if part['kind'] != 'profile':
                    continue
                self.assertIs(occurrence.component.extrusions[0].profile, material_region)
                self.assertEqual(occurrence.transform.origin,
                                 tuple(v/10 for v in part['centerline_mm'][0]))
        self.assertEqual(data['profiles'][definition['id']], definition)
