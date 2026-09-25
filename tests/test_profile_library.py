"""DXF contracts and profile storage; synthetic data, no manufacturer claims."""
from copy import deepcopy
import hashlib
import json
from math import pi
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fusion_addin.FrameKit import demo, dxf_profile as dxf, model, profile_library as library, settings
from fusion_addin.FrameKit.preview_data import display_geometry, world_point

FIXTURE = Path(__file__).parent / 'fixtures/synthetic_tslot_40.dxf'


def document(entities, unit=4):
    pairs = [(0, 'SECTION'), (2, 'HEADER')]
    if unit is not None:
        pairs += [(9, '$INSUNITS'), (70, unit)]
    pairs += [(0, 'ENDSEC'), (0, 'SECTION'), (2, 'ENTITIES')]+entities+[(0, 'ENDSEC'), (0, 'EOF')]
    return ''.join(f'{key}\n{value}\n' for key, value in pairs).encode()


def poly(points, closed=True):
    pairs = [(0, 'LWPOLYLINE'), (90, len(points)), (70, int(closed))]
    for point in points:
        pairs += [(10, point[0]), (20, point[1])]
        if len(point) > 2:
            pairs.append((42, point[2]))
    return pairs


def square(half=20):
    return poly([(-half, -half), (half, -half), (half, half), (-half, half)])


def circle(x=0, y=0, radius=3):
    return [(0, 'CIRCLE'), (10, x), (20, y), (40, radius)]


class DxfTests(unittest.TestCase):
    def test_reference_points_do_not_change_contours_or_bounds(self):
        markers = [(0, 'POINT'), (10, 0), (20, 0), (30, 0)]
        markers += [(0, 'POINT'), (10, 100), (20, -200), (30, 0)]
        outline = square() + circle()
        shape = dxf.read(document(markers + outline + markers))
        expected = dxf.read(document(outline))
        self.assertEqual(shape.pop('ignored_entities'), dict(points=4, construction=0))
        expected.pop('ignored_entities')
        self.assertEqual(shape, expected)
        with self.assertRaisesRegex(ValueError, 'Konturelemente'):
            dxf.read(document(markers))
        with self.assertRaisesRegex(ValueError, 'Offene'):
            dxf.read(document(markers + poly([(-20, -20), (20, -20),
                                              (20, 20), (-20, 20)], False)))

    def test_point_does_not_hide_unterminated_polyline(self):
        with self.assertRaisesRegex(ValueError, 'SEQEND'):
            dxf.read(document([(0, 'POLYLINE'), (70, 1),
                               (0, 'POINT'), (10, 0), (20, 0)]))

    def test_marked_construction_geometry_is_excluded(self):
        for linetype in ('DASHED', 'center2', 'PHANTOMX2', 'DASHDOT'):
            # Crosses the outline and extends beyond its bounds.
            helper = [(0, 'LINE'), (6, linetype), (10, -100), (20, 0),
                      (11, 100), (21, 0)]
            shape = dxf.read(document(square() + circle() + helper))
            self.assertEqual(shape['width_mm'], 40)
            self.assertEqual(shape['loop_count'], 2)
            self.assertEqual(shape['ignored_entities'], dict(points=0, construction=1))
            with self.assertRaisesRegex(ValueError, 'Konturelemente'):
                dxf.read(document(helper))
        for kind in ('XLINE', 'RAY'):
            helper = [(0, kind), (10, 0), (20, 0), (11, 1), (21, 0)]
            self.assertEqual(dxf.read(document(square() + helper))['width_mm'], 40)

    def test_construction_linetype_inherited_from_layer_and_overridden(self):
        tables = (b'0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n'
                  b'0\nLAYER\n2\nGuides\n6\nDASHED\n0\nENDTAB\n0\nENDSEC\n')
        helper = [(0, 'LINE'), (8, 'guides'), (10, -10), (20, 0), (11, 10), (21, 0)]
        for setting in ([], [(6, 'BYLAYER')]):
            data = tables + document(square() + helper + setting)
            shape = dxf.read(data)
            self.assertEqual(shape['width_mm'], 40)
            self.assertEqual(shape['ignored_entities']['construction'], 1)
        for linetype in ('CONTINUOUS', 'BYBLOCK', 'CUSTOM', 'HIDDEN'):
            with self.assertRaisesRegex(ValueError, 'Offene|Ursprung'):
                dxf.read(tables + document(square() + helper + [(6, linetype)]))

    def test_construction_polylines_skip_the_complete_sequence(self):
        old = [(0, 'POLYLINE'), (6, 'DASHED'), (70, 0),
               (0, 'VERTEX'), (10, -100), (20, 0),
               (0, 'VERTEX'), (10, 100), (20, 0)]
        for helper in (old + [(0, 'SEQEND')],
                       poly([(-100, 0), (100, 0)], False) + [(6, 'DASHED')],
                       circle(radius=100) + [(6, 'CENTER')]):
            shape = dxf.read(document(helper + square()))
            self.assertEqual(shape['width_mm'], 40)
            self.assertEqual(len(shape['curves']), 4)
            self.assertEqual(shape['ignored_entities']['construction'], 1)
        with self.assertRaisesRegex(ValueError, 'SEQEND'):
            dxf.read(document(square() + old))
        with self.assertRaisesRegex(ValueError, 'SEQEND'):
            dxf.read(document(old + square()))

    def test_unmarked_open_geometry_is_not_discarded(self):
        helper = [(0, 'LINE'), (10, -20), (20, -20), (11, 20), (21, 20)]
        with self.assertRaisesRegex(ValueError, 'Offene|verzweigte'):
            dxf.read(document(square() + helper))
        with self.assertRaisesRegex(ValueError, 'SPLINE'):
            dxf.read(document(square() + [(0, 'SPLINE'), (6, 'DASHED')]))

    def test_original_sketch_with_points_and_construction_lines(self):
        source = FIXTURE.with_name('sketch_20_with_construction.dxf')
        original = source.read_bytes()
        spec, data = library.prepare(source, '20er')
        self.assertEqual(data, original)
        self.assertAlmostEqual(spec['width_mm'], 20, places=5)
        self.assertAlmostEqual(spec['height_mm'], 20, places=5)
        self.assertEqual(spec['loop_count'], 1)
        self.assertEqual(len(spec['curves']), 44)
        self.assertEqual(spec['ignored_entities'], dict(points=3, construction=3))
        with tempfile.TemporaryDirectory() as folder:
            library.add(spec, data, folder)
            library.verify_source(spec, folder)
            self.assertEqual((Path(folder) / spec['filename']).read_bytes(), original)
            entries, warning = library.load(folder)
            self.assertEqual(warning, '')
            self.assertEqual(entries[0]['curves'], spec['curves'])

    def test_synthetic_tslots_and_holes(self):
        spec = dxf.read(FIXTURE.read_bytes())
        self.assertEqual((spec['width_mm'], spec['height_mm']), (40, 40))
        self.assertEqual(spec['loop_count'], 6)
        self.assertEqual(len(spec['curves']), 41)
        self.assertAlmostEqual(spec['area_mm2'], 1600-4*(8*3+14*5)-25*pi)

    def test_all_units_and_explicit_override(self):
        for code, (name, factor) in dxf.UNITS.items():
            shape = dxf.read(document(square(20/factor), code))
            self.assertAlmostEqual(shape['width_mm'], 40)
            self.assertEqual(shape['source_unit'], name)
        with self.assertRaisesRegex(ValueError, 'Einheit'):
            dxf.read(document(square(), None))
        self.assertEqual(dxf.read(document(square(), None), 'mm')['width_mm'], 40)
        self.assertEqual(dxf.read(document(square(2), 4), 'cm')['width_mm'], 40)

    def test_lines_form_closed_contours_independent_of_order_and_direction(self):
        points = [(-20,-20),(20,-20),(20,20),(-20,20)]
        entities = []
        for index in (2, 0, 3, 1):
            a, b = points[index], points[(index+1)%4]
            if index % 2:
                a, b = b, a
            entities += [(0,'LINE'),(10,a[0]),(20,a[1]),(11,b[0]),(21,b[1])]
        shape = dxf.read(document(entities+circle()))
        self.assertEqual(shape['loop_count'], 2)
        self.assertAlmostEqual(shape['area_mm2'], 1600-9*pi)

    def test_arcs_and_bulges_remain_exact(self):
        arcs=[]
        for start in (0,90,180,270):
            arcs += [(0,'ARC'),(10,0),(20,0),(40,20),(50,start),(51,start+90)]
        shape=dxf.read(document(arcs+circle()))
        self.assertAlmostEqual(shape['area_mm2'], (400-9)*pi)
        for bulge, points in ((1,[(-20,0,1),(20,0,1)]),(-1,[(-20,0,-1),(20,0,-1)])):
            shape=dxf.read(document(poly(points)))
            self.assertAlmostEqual(shape['width_mm'],40)
            self.assertAlmostEqual(shape['height_mm'],40)
            self.assertAlmostEqual(shape['area_mm2'],400*pi)
            self.assertTrue(all(c['sweep']*bulge>0 for c in shape['curves']))

    def test_old_polyline_and_open_chain(self):
        entities=[(0,'POLYLINE'),(70,1),(10,0),(20,0),(30,0)]
        for x,y in [(-20,-20),(20,-20),(20,20),(-20,20)]:
            entities += [(0,'VERTEX'),(10,x),(20,y),(30,0)]
        shape=dxf.read(document(entities+[(0,'SEQEND')]))
        self.assertEqual(shape['area_mm2'],1600)
        with self.assertRaisesRegex(ValueError,'SEQEND'):
            dxf.read(document(entities))
        with self.assertRaisesRegex(ValueError,'Offene'):
            dxf.read(document(poly([(-20,-20),(20,-20),(20,20),(-20,20)],False)))

    def test_reject_offset_rectangle_and_3d(self):
        for entities, message in (
            (poly([(-19,-20),(21,-20),(21,20),(-19,20)]), 'Ursprung'),
            (poly([(-20,-10),(20,-10),(20,10),(-20,10)]), 'S05'),
            (square()+[(38,1)], 'XY-Ebene'),
            (circle(radius=20)+[(230,-1)], 'Ausrichtung'),
            (square()+[(43,2)], 'Polylinienbreite'),
            (square()+[(67,1)], 'Papierbereich')):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError,message):
                dxf.read(document(entities))

    def test_reject_invalid_and_unsupported_data(self):
        for data in (b'', b'AutoCAD Binary DXF\x00', b'broken', b'0\nEOF\n',
                     document(square()+[(0,'INSERT'),(2,'block')]),
                     document(square()+[(0,'SPLINE')]),
                     document(circle(radius=float('nan'))),
                     document(circle(radius=-3)), document(square(0)),
                     document(square(0.1)), document(square(6000))):
            with self.subTest(data=data[:40]), self.assertRaises(ValueError):
                dxf.read(data)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)/'profiles'
        self.spec,self.data=library.prepare(FIXTURE,'Synthetic test profile',metadata={'manufacturer':'Test only'})

    def test_add_load_select_snapshot_and_delete(self):
        entries=library.add(self.spec,self.data,self.folder)
        self.assertEqual(library.load(self.folder),(entries,''))
        library.verify_source(self.spec,self.folder)
        self.assertEqual((self.folder/self.spec['filename']).read_bytes(),self.data)
        values=dict(demo.DEFAULTS,profile_definition=self.spec,profile=self.spec['width_mm'])
        calculated=model.build_model(values)
        self.assertFalse(next(iter(calculated['profiles'].values()))['is_demo'])
        for part in calculated['parts']:
            if part['kind']!='profile':continue
            self.assertEqual(part['geometry']['type'],'dxf')
            self.assertEqual(part['position_mm'],part['centerline_mm'][0])
            self.assertEqual(world_point(part,[0,0,part['cut_length_mm']]),part['centerline_mm'][1])
        path=Path(self.temp.name)/'settings.json'
        settings.save(values,path)
        self.assertEqual(settings.load(path),(values,''))
        before=display_geometry(calculated)
        self.assertEqual(library.remove(self.spec['id'],self.folder),[])
        self.assertFalse((self.folder/self.spec['filename']).exists())
        self.assertTrue(FIXTURE.exists())
        self.assertEqual(model.build_model(values,calculated),calculated)
        self.assertEqual(display_geometry(calculated),before)

    def test_real_and_demo_geometry_have_identical_world_centerlines(self):
        values=dict(demo.DEFAULTS,profile_definition=self.spec,shelf_count=2,shelf_heights=[250,450],
                    cross_members={'top':dict(count=5,direction='quer'),'shelf:01':dict(count=3,direction='laengs')})
        real=model.build_model(values)
        solid=model.build_model(dict(values,profile_definition=None))
        self.assertEqual(display_geometry(real),display_geometry(solid))
        self.assertEqual([p['bounds_mm'] for p in real['parts']],[p['bounds_mm'] for p in solid['parts']])
        with self.assertRaisesRegex(ValueError,'Profilbreite'):
            model.build_model(dict(values,profile=50))

    def test_changed_or_missing_source_rejected_without_affecting_snapshot(self):
        library.add(self.spec,self.data,self.folder)
        path=self.folder/self.spec['filename']
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'verändert'):library.verify_source(self.spec,self.folder)
        path.unlink()
        with self.assertRaisesRegex(ValueError,'fehlt'):library.verify_source(self.spec,self.folder)
        self.assertEqual(library.remove(self.spec['id'],self.folder),[])

    def test_unique_ids_and_duplicate_names(self):
        other,data=library.prepare(FIXTURE,self.spec['name'])
        library.add(self.spec,self.data,self.folder)
        entries=library.add(other,data,self.folder)
        self.assertEqual(len(entries),2)
        self.assertNotEqual(entries[0]['id'],entries[1]['id'])
        with self.assertRaises(ValueError):library.add(other,data,self.folder)

    def test_atomic_save_and_delete_rollback(self):
        with patch.object(settings,'_write_json',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):library.add(self.spec,self.data,self.folder)
        self.assertFalse((self.folder/self.spec['filename']).exists())
        library.add(self.spec,self.data,self.folder)
        with patch.object(settings,'_write_json',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):library.remove(self.spec['id'],self.folder)
        library.verify_source(self.spec,self.folder)
        self.assertEqual(library.load(self.folder),([self.spec],''))

    def test_corrupt_index_not_overwritten_and_unsafe_paths_rejected(self):
        self.folder.mkdir()
        path=self.folder/'index.json'
        path.write_text('{broken')
        entries,warning=library.load(self.folder)
        self.assertEqual(entries,[])
        self.assertIn('nicht geladen',warning)
        with self.assertRaises(ValueError):library.add(self.spec,self.data,self.folder)
        self.assertEqual(path.read_text(),'{broken')
        invalid=deepcopy(self.spec)
        invalid['filename']='../settings.json'
        with self.assertRaises(ValueError):library.validate(invalid)
        invalid=deepcopy(self.spec)
        invalid['curves'][0]['start'][0]=123
        with self.assertRaises(ValueError):library.validate(invalid)
        with self.assertRaises(ValueError):library.add(self.spec,b'changed',self.folder)

    def test_snapshot_preserves_metadata_and_dimensions(self):
        self.assertEqual(self.spec['manufacturer'],'Test only')
        self.assertEqual(self.spec['series'],'')
        self.assertEqual(self.spec['origin'],'bounds-center')
        self.assertEqual(self.spec['source_sha256'],hashlib.sha256(self.data).hexdigest())
        json.dumps(self.spec,allow_nan=False)
