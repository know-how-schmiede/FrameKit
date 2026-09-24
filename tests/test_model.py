"""Model identity and geometry contracts, without Fusion."""
import itertools
import json
import unittest

from fusion_addin.FrameKit import accessories, demo, model


class ModelTests(unittest.TestCase):
    def test_independent_assemblies_and_json_roundtrip(self):
        first = model.build_model(demo.DEFAULTS)
        second = model.build_model(demo.DEFAULTS)
        self.assertNotEqual(first['assembly_id'], second['assembly_id'])
        self.assertFalse({part['uid'] for part in first['parts']} & {part['uid'] for part in second['parts']})
        restored = json.loads(json.dumps(first))
        self.assertEqual(restored, first)
        self.assertEqual(model.build_model(demo.DEFAULTS, restored), first)

    def test_identity_survives_dimensions_profiles_and_options(self):
        initial = dict(demo.DEFAULTS, shelf_count=2, shelf_heights=[None, None],
                       accessory=accessories.PRESETS[0])
        first = model.build_model(initial)
        changed = dict(initial, length=900, width=600, height=1000, profile=50,
                       shelf_heights=[300, 600], accessory=accessories.PRESETS[1])
        second = model.build_model(changed, first)
        self.assertEqual(first['assembly_id'], second['assembly_id'])
        self.assertEqual(first['id_registry'], second['id_registry'])
        reduced = dict(changed, bottom=False, shelf_count=1, shelf_heights=[300], accessory=None)
        third = model.build_model(reduced, second)
        self.assertEqual(third['id_registry'], first['id_registry'])
        for part in third['parts']:
            self.assertEqual(part['id'], first['id_registry'][part['key']])
        restored = model.build_model(changed, third)
        self.assertEqual(restored, second)
        more = model.build_model(dict(changed, shelf_count=3, shelf_heights=[300, 600, 800]), restored)
        self.assertEqual(len(set(more['id_registry'].values())), len(more['id_registry']))
        for key, value in first['id_registry'].items():
            self.assertEqual(more['id_registry'][key], value)

    def test_profile_orientation_bounds_and_cut_endpoints(self):
        # Beams shorter than their cross section must still extrude along X/Y.
        values = dict(demo.DEFAULTS, length=90, width=95, shelf_count=1, shelf_heights=[300])
        calculated = model.build_model(values)
        for part in calculated['parts']:
            if part['kind'] != 'profile':
                self.assertIsNone(part['cut_length_mm'])
                continue
            shape, axes, origin = part['geometry'], part['orientation'], part['position_mm']
            a, b, c = axes
            self.assertEqual([a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]], c)
            dimensions = (shape['width_mm'], shape['height_mm'], shape['depth_mm'])
            corners = [[origin[i] + sum(axes[j][i]*point[j] for j in range(3)) for i in range(3)]
                       for point in itertools.product(*[(0, dim) for dim in dimensions])]
            self.assertEqual([min(point[i] for point in corners) for i in range(3)], origin)
            self.assertEqual([max(point[i] for point in corners)-origin[i] for i in range(3)], part['bounds_mm'])
            start, end = part['centerline_mm']
            self.assertEqual(sum((end[i]-start[i])**2 for i in range(3)), part['cut_length_mm']**2)
            axis = c.index(1)
            self.assertEqual(start[axis], origin[axis])
            self.assertEqual(end[axis], origin[axis] + part['bounds_mm'][axis])
        by_key = {part['key']: part for part in calculated['parts']}
        self.assertEqual(by_key['top:beam:front']['cut_length_mm'], 10)
        self.assertEqual(by_key['top:beam:left']['cut_length_mm'], 15)

    def test_groups_and_properties_are_independent_of_display_names(self):
        values = dict(demo.DEFAULTS, shelf_count=2, shelf_heights=[None, None], accessory=accessories.PRESETS[0])
        data = model.build_model(values)
        ids = {group['id'] for group in data['groups']}
        self.assertEqual(ids, {'posts', 'top', 'bottom', 'shelf:01', 'shelf:02', 'accessories', 'connections'})
        self.assertEqual(len(data['parts']), 28)
        for part in data['parts']:
            self.assertIn(part['group_id'], ids)
            part['display_name'] = 'beliebig geändert'
            if part['kind'] == 'profile':
                self.assertIn(part['profile_ref'], data['profiles'])
                self.assertGreater(part['cut_length_mm'], 0)
        self.assertFalse(any(part['group_id'] == 'connections' for part in data['parts']))
        self.assertTrue(next(group for group in data['groups'] if group['id'] == 'connections')['reserved'])

    def test_configuration_and_profile_snapshots_are_detached(self):
        values = dict(demo.DEFAULTS, accessory=accessories.new_spec('Fuß', 'Fuß', 40, 50))
        data = model.build_model(values)
        values['accessory']['height'] = 200
        self.assertEqual(data['configuration']['accessory']['height'], 40)
        self.assertTrue(all(part['accessory_definition']['height'] == 40
                            for part in data['parts'] if part['kind'] == 'support'))

    def test_invalid_previous_registry_is_rejected(self):
        previous = model.build_model(demo.DEFAULTS)
        previous['id_registry']['duplicate'] = 'P001'
        with self.assertRaises(ValueError):
            model.build_model(demo.DEFAULTS, previous)
        with self.assertRaises(ValueError):
            model.build_model(demo.DEFAULTS, dict(previous, schema=999))
