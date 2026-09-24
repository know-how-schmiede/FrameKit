"""Exercise Fusion adapter contracts with a small API double, not a CAD kernel."""
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

from fusion_addin.FrameKit import accessories, demo


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
        sketch = NS(points=[], circle=None, timelineObject=self.design.tick(),
                    profiles=NS(count=1, item=lambda index: object()))

        def line(start, end):
            sketch.points.extend((start, end))
            return NS(startSketchPoint=start, endSketchPoint=end)

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
        feature = NS(timelineObject=self.design.tick(), distance=distance, bodies=NS(item=lambda index: body))
        self.extrusions.append(feature)
        return feature


class Design:
    def __init__(self, parametric=True):
        self.designType = 1 if parametric else 0
        self.events, self.groups, self.calls = [], [], []
        self.fail_extrude = False
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
        for failure in ('extrusion', 'group'):
            with self.subTest(failure=failure):
                design = Design()
                foreign = design.rootComponent.add_component(Matrix())
                design.fail_extrude = failure == 'extrusion'
                design.fail_group_at = 3 if failure == 'group' else None
                with self.assertRaises(RuntimeError):
                    self.adapter.create_frame(design, demo.DEFAULTS)
                self.assertEqual(design.rootComponent.children, [foreign])
                self.assertEqual(design.groups, [])

    def test_direct_mode_does_not_change_design_type(self):
        design = Design(parametric=False)
        assembly = self.adapter.create_frame(design, demo.DEFAULTS)
        self.assertEqual(design.designType, 0)
        self.assertEqual(design.groups, [])
        self.assertEqual(assembly.component.attributes['FrameKit', 'timelineMode'], 'direct-no-timeline')
