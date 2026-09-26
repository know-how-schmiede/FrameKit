"""STEP asset contracts and startup-import lifecycle without a CAD kernel."""
from pathlib import Path
import re
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

from fusion_addin.FrameKit import bracket_library as library
from fusion_addin.FrameKit import demo, model
from fusion_addin.FrameKit.preview_data import world_point
from fusion_addin.FrameKit.connections import overlaps, envelope
from test_sections import rectangle
import tempfile


class BracketLibraryTests(unittest.TestCase):
    def test_bundled_sources_are_identical_single_solids_in_mm(self):
        root = Path(__file__).resolve().parents[1]
        for size in library.SIZES:
            original = root / 'profiles' / 'winkel' / library.filename(size)
            packaged = library.DIRECTORY / library.filename(size)
            self.assertEqual(original.read_bytes(), packaged.read_bytes())
            text = original.read_text()
            self.assertEqual(text.count('MANIFOLD_SOLID_BREP('), 1)
            self.assertIn('SI_UNIT(.MILLI.,.METRE.)', text)
            points = {int(i): tuple(float(x) for x in v.split(',')) for i, v in re.findall(
                r"#(\d+)=CARTESIAN_POINT\('[^']*',\(([^)]+)\)\)", text)}
            vertices = [points[int(i)] for i in re.findall(r"VERTEX_POINT\('[^']*',#(\d+)\)", text)]
            for axis in range(3):
                self.assertAlmostEqual(min(p[axis] for p in vertices), 0)
                self.assertAlmostEqual(max(p[axis] for p in vertices), size)

    def test_placement_is_rotation_and_mounts_on_both_member_faces(self):
        data = model.build_model(dict(demo.DEFAULTS, brackets=True,
                                     cross_members={'top': dict(count=1, direction='quer')}))
        by_key = {p['key']: p for p in data['parts']}
        for p in data['parts']:
            if p['kind'] != 'connection':
                continue
            u, v, w = p['orientation']
            self.assertEqual([u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2],
                              u[0]*v[1]-u[1]*v[0]], w)
            size = p['geometry']['size_mm']
            corners = [world_point(p, [x, y, z]) for x in (0, size)
                       for y in (0, size) for z in (0, size)]
            for axis in range(3):
                self.assertAlmostEqual(min(c[axis] for c in corners), p['bounds_origin_mm'][axis])
                self.assertAlmostEqual(max(c[axis] for c in corners),
                                       p['bounds_origin_mm'][axis]+p['bounds_mm'][axis])
            for key in p['connection_definition']['member_keys']:
                member = by_key[key]
                # Mounting corner lies on an exterior side of both members.
                self.assertTrue(any(abs(p['position_mm'][a]-edge) < 1e-6
                    for a in (0, 1) for edge in (member['bounds_origin_mm'][a],
                        member['bounds_origin_mm'][a]+member['bounds_mm'][a])))

    def test_parallel_full_width_brackets_do_not_overlap(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = rectangle(directory, 40, 80)
        data = model.build_model(dict(demo.DEFAULTS, profile_definition=profile,
                                     brackets=True, brackets_double=True))
        brackets = [p for p in data['parts'] if p['kind'] == 'connection']
        self.assertEqual(len(brackets), 16)
        for i, part in enumerate(brackets):
            for other in brackets[i+1:]:
                self.assertFalse(overlaps(envelope(part), envelope(other)))

    def test_startup_copies_solids_closes_imports_and_restores_user_document(self):
        documents, transforms = [], []
        def import_file(path):
            size = int(Path(path).stem.split('_')[1].split('x')[0])
            solid = NS(isSolid=True, boundingBox=NS(
                minPoint=NS(asArray=lambda: [0, 0, 0]),
                maxPoint=NS(asArray=lambda: [size/10]*3)))
            design = NS(rootComponent=NS(bRepBodies=[solid], allOccurrences=[]))
            document = NS(close=Mock(), products=NS(itemByProductType=lambda _: design))
            documents.append(document)
            return document
        def transform(body, matrix):
            transforms.append(matrix)
            return True
        manager = NS(copy=lambda body: body, transform=transform)
        core = NS(Matrix3D=NS(create=lambda: NS(setWithCoordinateSystem=Mock(return_value=True))),
                  Point3D=NS(create=lambda *v: v), Vector3D=NS(create=lambda *v: v))
        fusion = NS(TemporaryBRepManager=NS(get=lambda: manager), Design=NS(cast=lambda d: d))
        app = NS(activeDocument=NS(activate=Mock()), importManager=NS(
            createSTEPImportOptions=lambda path: path, importToNewDocument=import_file))
        with patch.dict(sys.modules, {'adsk': NS(core=core, fusion=fusion),
                                     'adsk.core': core, 'adsk.fusion': fusion}), \
                patch.object(library, '_bodies', {}), patch.object(library, '_errors', {}):
            library.prepare(app)
            self.assertEqual(len(documents), 3)
            for size, matrix in zip(library.SIZES, transforms):
                self.assertTrue(library.body(size).isSolid)
                matrix.setWithCoordinateSystem.assert_called_once_with(
                    (0, 0, size/10), (1, 0, 0), (0, 0, -1), (0, 1, 0))
            for document in documents:
                document.close.assert_called_once_with(False)
            app.activeDocument.activate.assert_called_once()
            manager.copy = Mock(side_effect=ValueError('invalid solid'))
            library.prepare(app)
            with self.assertRaisesRegex(ValueError, 'invalid solid'):
                library.body(20)
            for document in documents[3:]:
                document.close.assert_called_once_with(False)
