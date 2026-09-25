"""Fusion API contract tests; these doubles are not a replacement for its CAD kernel."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

from fusion_addin.FrameKit import profile_library
from test_profile_library import FIXTURE
from test_geometry_adapter import Design, Matrix


class Collection:
    def __init__(self, items):
        self.items=items
        self.count=len(items)

    def item(self,index):return self.items[index]


class Attributes(dict):
    def add(self,group,name,value):self[group,name]=value
    def itemByName(self,group,name):
        value=self.get((group,name))
        return NS(value=value) if value is not None else None


def region(indices, loops, area):
    groups=[[] for _ in range(loops)]
    for index,value in enumerate(indices):
        attrs=Attributes()
        attrs.add('FrameKit','sourceCurve',str(value))
        groups[index%loops].append(NS(sketchEntity=NS(attributes=attrs)))
    return NS(profileLoops=Collection([NS(profileCurves=Collection(items)) for items in groups]),
              areaProperties=lambda accuracy: NS(area=area/100))


class ProfileGeometryTests(unittest.TestCase):
    def setUp(self):
        adsk=ModuleType('adsk')
        adsk.core=ModuleType('adsk.core')
        adsk.fusion=ModuleType('adsk.fusion')
        adsk.core.Point3D=NS(create=lambda *xyz:xyz)
        adsk.core.Matrix3D=NS(create=Matrix)
        adsk.core.ValueInput=NS(createByReal=lambda value:value)
        adsk.fusion.CalculationAccuracy=NS(HighCalculationAccuracy=2)
        adsk.fusion.FeatureOperations=NS(NewBodyFeatureOperation=0)
        modules=patch.dict(sys.modules,{'adsk':adsk,'adsk.core':adsk.core,'adsk.fusion':adsk.fusion})
        modules.start();self.addCleanup(modules.stop)
        path=Path(__file__).resolve().parents[1]/'fusion_addin/FrameKit/profile_geometry.py'
        spec=importlib.util.spec_from_file_location('fusion_addin.FrameKit.profile_geometry_under_test',path)
        self.adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.adapter)
        self.spec,_=profile_library.prepare(FIXTURE,'Synthetic')
        self.material=region(range(41),6,self.spec['area_mm2'])

    def test_selects_material_with_holes_not_first_profile_or_all_regions(self):
        hole=region([40],1,4*3.141592653589793)
        sketch=NS(profiles=Collection([hole,self.material]))
        self.assertIs(self.adapter.material_region(sketch,self.spec),self.material)

    def test_rejects_split_missing_duplicate_island_or_wrong_area(self):
        candidates=[region(range(40),6,self.spec['area_mm2']),
                    region(list(range(40))+[39],6,self.spec['area_mm2']),
                    region(range(41),5,self.spec['area_mm2']),
                    region(range(41),6,self.spec['area_mm2']+1)]
        for candidate in candidates:
            with self.subTest(candidate=candidate),self.assertRaisesRegex(ValueError,'Materialfläche'):
                self.adapter.material_region(NS(profiles=Collection([candidate])),self.spec)
        with self.assertRaises(ValueError):
            self.adapter.material_region(NS(profiles=Collection([self.material,self.material])),self.spec)

    def test_exact_curve_creation_and_deferred_cleanup(self):
        calls=[]
        def create(kind):
            def run(*args):
                entity=NS(attributes=Attributes())
                calls.append((kind,args,entity))
                return entity
            return run
        sketch=NS(sketchCurves=NS(sketchLines=NS(addByTwoPoints=create('line')),
            sketchCircles=NS(addByCenterRadius=create('circle')),
            sketchArcs=NS(addByCenterStartSweep=create('arc'))))
        spec=dict(self.spec,curves=[dict(type='line',start=[-20,-20],end=[20,-20]),
            dict(type='circle',center=[0,0],radius=3),
            dict(type='arc',center=[0,0],radius=20,start_angle=0,sweep=-1.5)])
        with patch.object(self.adapter,'material_region',return_value=self.material):
            self.assertIs(self.adapter.draw_section(sketch,spec),self.material)
        self.assertEqual(calls[0][1],((-2,-2,0),(2,-2,0)))
        self.assertEqual(calls[1][1],((0,0,0),0.3))
        self.assertEqual(calls[2][1],((0,0,0),(2,0,0),-1.5))
        self.assertFalse(sketch.isComputeDeferred)
        self.assertEqual([c[2].attributes['FrameKit','sourceCurve'] for c in calls],['0','1','2'])
        sketch.sketchCurves.sketchLines.addByTwoPoints=Mock(side_effect=RuntimeError('failure'))
        with self.assertRaises(RuntimeError):self.adapter.draw_section(sketch,spec)
        self.assertFalse(sketch.isComputeDeferred)

    def test_validation_temporary_geometry_removed_success_and_failure(self):
        for failure in ('none','draw','extrude','bodies'):
            design=Design()
            foreign=design.rootComponent.add_component(Matrix())
            original=design.rootComponent.occurrences.addNewComponent
            def add(transform):
                occurrence=original(transform)
                def extrude(*args):
                    if failure=='extrude':raise RuntimeError('extrusion failure')
                    return NS(bodies=NS(count=2 if failure=='bodies' else 1))
                occurrence.component.features.extrudeFeatures.addSimple=extrude
                return occurrence
            design.rootComponent.occurrences.addNewComponent=add
            with patch.object(self.adapter,'draw_section',side_effect=RuntimeError('draw failure') if failure=='draw' else None,return_value=self.material):
                if failure=='none':self.adapter.validate_in_fusion(design,self.spec)
                else:
                    with self.assertRaises((RuntimeError,ValueError)):
                        self.adapter.validate_in_fusion(design,self.spec)
            self.assertEqual(design.rootComponent.children,[foreign])
