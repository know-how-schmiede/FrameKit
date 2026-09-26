"""Mixed section dimensions, placement and inheritance (synthetic DXF)."""
from copy import deepcopy
from itertools import product, combinations
from pathlib import Path
import tempfile
import unittest

from fusion_addin.FrameKit import demo, model, profile_library, settings
from fusion_addin.FrameKit.preview_data import world_point
from test_profile_library import document, poly, circle


def rectangle(folder, width, height):
    path = Path(folder)/f'{width}x{height}.dxf'
    path.write_bytes(document(poly([(-width/2, -height/2), (width/2, -height/2),
                                   (width/2, height/2), (-width/2, height/2)]) + circle()))
    return profile_library.prepare(path, path.stem)[0]


class SectionTests(unittest.TestCase):
    def test_repository_dxf_rounding_does_not_reject_identical_sections(self):
        folder = Path(__file__).parents[1]/'profiles'
        for name in ('20erProfil_Test_Skizze1.dxf', '20erProfil_Test_Skizze1_Import.dxf'):
            definition, _ = profile_library.prepare(folder/name, name)
            self.assertGreater(definition['width_mm'], definition['height_mm'])
            for rotation in (0, 90, 180, 270):
                with self.subTest(file=name, rotation=rotation):
                    values = dict(demo.DEFAULTS, profile=definition['width_mm'],
                                  profile_definition=definition, profile_rotation=rotation)
                    data = model.build_model(values)
                    self.assertEqual(len([p for p in data['parts'] if p['kind'] == 'profile']), 12)
                    self.assertEqual(data['profiles'][definition['id']], definition)

    def test_frame_width_tolerance_still_rejects_real_oversize(self):
        for difference in (0.000005, 0.00002, 1):
            definition = rectangle(self.folder, 30+difference, 30)
            values = dict(demo.DEFAULTS, profile=definition['width_mm'], profile_definition=definition)
            with self.subTest(difference=difference):
                if difference < 0.00001:
                    model.build_model(values)
                else:
                    with self.assertRaisesRegex(ValueError, 'Rahmenbreite'):
                        model.build_model(values)

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = folder.name
        self.post = rectangle(self.folder, 40, 80)
        self.frame = rectangle(self.folder, 20, 40)
        self.cross = rectangle(self.folder, 30, 60)
        self.values = dict(deepcopy(demo.DEFAULTS), group_profiles={
            'posts': dict(definition=self.post), 'frame': dict(definition=self.frame),
            'cross': dict(definition=self.cross)}, shelf_count=2, shelf_heights=[None, None],
            cross_members={key: dict(count=2, direction='quer')
                           for key in ('top', 'bottom', 'shelf:01', 'shelf:02')})

    def test_mixed_dimensions_rotations_and_actual_transformed_bounds(self):
        for rotation, direction in product((0, 90, 180, 270), ('quer', 'laengs')):
            values = deepcopy(self.values)
            values['group_profiles']['posts']['rotation'] = rotation
            values['group_profiles']['cross']['rotation'] = rotation
            for spec in values['cross_members'].values():
                spec['direction'] = direction
            data = model.build_model(values)
            profiles = [p for p in data['parts'] if p['kind'] == 'profile']
            for part in profiles:
                section = data['profiles'][part['profile_ref']]
                a, b = section['width_mm']/2, section['height_mm']/2
                corners = [world_point(part, point) for point in product((-a, a), (-b, b),
                                                                          (0, part['cut_length_mm']))]
                low = [min(p[i] for p in corners) for i in range(3)]
                high = [max(p[i] for p in corners) for i in range(3)]
                for i in range(3):
                    self.assertAlmostEqual(low[i], part['bounds_origin_mm'][i])
                    self.assertAlmostEqual(high[i]-low[i], part['bounds_mm'][i])
                    self.assertGreaterEqual(low[i], -1e-7)
                    self.assertLessEqual(high[i], values[('length', 'width', 'height')[i]]+1e-7)
                self.assertEqual(world_point(part, [0, 0, 0]), part['centerline_mm'][0])
                self.assertEqual(world_point(part, [0, 0, part['cut_length_mm']]), part['centerline_mm'][1])
                if part['group_id'] != 'posts':
                    panel = next(p for p in data['parts'] if p['key'] == part['group_id']+':panel')
                    self.assertAlmostEqual(high[2], panel['position_mm'][2])
            for a, b in combinations(profiles, 2):
                overlap = all(min(a['bounds_origin_mm'][i]+a['bounds_mm'][i],
                                  b['bounds_origin_mm'][i]+b['bounds_mm'][i]) >
                              max(a['bounds_origin_mm'][i], b['bounds_origin_mm'][i])+1e-7
                              for i in range(3))
                self.assertFalse(overlap, (a['key'], b['key']))
            post = next(p for p in profiles if p['key'] == 'post:front:left')
            panel = next(p for p in data['parts'] if p['key'] == 'top:panel')
            self.assertEqual(panel['geometry']['points_mm'][-1], post['bounds_mm'][:2])

    def test_equal_free_fields_and_variable_shelf_depths(self):
        values = deepcopy(self.values)
        values['cross_members']['shelf:01']['section'] = dict(rotation=90)
        data = model.build_model(values)
        tops = demo.shelf_heights(values)
        # Bottom depth 78, shelf 1 depth 58, shelf 2 and top depth 78.
        gaps = [tops[0]-58-78, tops[1]-78-tops[0], 750-78-tops[1]]
        self.assertAlmostEqual(gaps[0], gaps[1])
        self.assertAlmostEqual(gaps[1], gaps[2])
        crosses = [p for p in data['parts'] if p['key'].startswith('shelf:01:cross')]
        expected = (800-2*20-2*60)/3
        self.assertAlmostEqual(crosses[0]['bounds_origin_mm'][0]-20, expected)
        self.assertAlmostEqual(crosses[1]['bounds_origin_mm'][0]-crosses[0]['bounds_origin_mm'][0]-60, expected)
        self.assertEqual(crosses[0]['cut_length_mm'], 460)
        with self.assertRaisesRegex(ValueError, 'überlappen'):
            model.build_model(dict(values, shelf_heights=[120, 160]))

    def test_settings_snapshots_inheritance_and_ids(self):
        values = deepcopy(self.values)
        values['profile_rotation'] = 180
        values['cross_members']['top']['section'] = dict(definition=self.frame, rotation=90)
        path = Path(self.folder)/'settings.json'
        settings.save(values, path)
        restored, warning = settings.load(path)
        self.assertEqual((restored, warning), (values, ''))
        first = model.build_model(values)
        values['group_profiles']['posts']['rotation'] = 90
        second = model.build_model(values, first)
        self.assertEqual(first['id_registry'], second['id_registry'])
        top = next(p for p in second['parts'] if p['key'] == 'top:cross:01')
        self.assertEqual(top['profile_ref'], self.frame['id'])
        self.assertEqual(top['section_rotation_deg'], 90)
        self.assertEqual(len(second['profiles']), 3)

    def test_invalid_selection_collision_and_rotation(self):
        for override in ({'profile_rotation': 45}, {'profile_rotation': True},
                         {'group_profiles': []}, {'group_profiles': {'posts': 'bad'}},
                         {'cross_members': {'top': {'count': 1, 'direction': 'quer', 'section': {'rotation': 12}}}}):
            with self.subTest(override=override), self.assertRaises(ValueError):
                model.build_model(dict(self.values, **override))
        values = deepcopy(self.values)
        values['group_profiles']['frame']['rotation'] = 90
        values['group_profiles']['posts']['definition'] = self.frame
        with self.assertRaisesRegex(ValueError, 'Rahmenbreite'):
            model.build_model(values)
        values = deepcopy(self.values)
        values['length'] = 170
        values['group_profiles']['posts']['rotation'] = 90
        with self.assertRaisesRegex(ValueError, 'Pfosten'):
            model.build_model(values)

    def test_on_top_panel_and_support_centers(self):
        from fusion_addin.FrameKit.accessories import PRESETS
        values = dict(self.values, top_panel_mount='on_top', accessory=PRESETS[0])
        data = model.build_model(values)
        by_key = {p['key']: p for p in data['parts']}
        self.assertEqual(len(by_key['top:panel']['geometry']['points_mm']), 4)
        post = by_key['post:front:left']
        support = by_key['support:front:left']
        self.assertEqual(post['centerline_mm'][0][:2], [20, 40])
        self.assertEqual(world_point(support, [*support['geometry']['center_mm'], 0])[:2], [20, 40])
        self.assertEqual(post['centerline_mm'][1][2], 732)
