from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from fusion_addin.FrameKit import demo, model, settings
from fusion_addin.FrameKit.connections import envelope, overlaps
from fusion_addin.FrameKit.preview_data import display_geometry
from test_sections import rectangle


class ConnectionTests(unittest.TestCase):
    def test_sizes_counts_group_and_collision_free_contacts(self):
        for size in (20, 30, 40):
            values = dict(demo.DEFAULTS, profile=size, brackets=True, shelf_count=1,
                          shelf_heights=[350], cross_members={'top': dict(count=1, direction='quer')})
            data = model.build_model(values)
            brackets = [p for p in data['parts'] if p['kind'] == 'connection']
            self.assertEqual(len(brackets), 14)
            self.assertEqual(data['connection_warnings'], [])
            self.assertEqual({p['group_id'] for p in brackets}, {'connections'})
            self.assertFalse(next(g for g in data['groups'] if g['id'] == 'connections')['reserved'])
            for p in brackets:
                self.assertEqual(p['connection_definition']['size_mm'], size)
                self.assertFalse(p['connection_definition']['fastening_complete'])
                self.assertFalse(p['is_placeholder'])
                self.assertEqual(len(p['geometry']['points_mm']), 4)
                self.assertEqual(p['geometry']['type'], 'step')
                prism = envelope(p)
                for other in data['parts']:
                    if other['kind'] != 'connection':
                        self.assertFalse(overlaps(prism, envelope(other)), (p['key'], other['key']))
            self.assertEqual(len(display_geometry(data)['connections']), len(brackets)*24)

    def test_double_wide_is_optional_and_uses_common_vertical_space(self):
        with tempfile.TemporaryDirectory() as folder:
            definition = rectangle(folder, 40, 80)
        values = dict(demo.DEFAULTS, profile_definition=definition, brackets=True)
        single = model.build_model(values)
        double = model.build_model(dict(values, brackets_double=True), single)
        first = [p for p in single['parts'] if p['kind'] == 'connection']
        second = [p for p in double['parts'] if p['kind'] == 'connection']
        self.assertEqual(len(first), 8)
        self.assertEqual(len(second), 16)
        self.assertEqual(double['connection_warnings'], [])
        for p in first:
            matching = next(q for q in second if q['key'] == p['key'])
            self.assertEqual(p['id'], matching['id'])
        top = [p for p in second if p['key'].startswith('connection:top:front:left')]
        self.assertEqual(len(top), 2)
        self.assertGreater(top[1]['position_mm'][2]-top[0]['position_mm'][2], 4)

    def test_unknown_sizes_and_tight_spaces_are_reported_not_intersected(self):
        data = model.build_model(dict(demo.DEFAULTS, profile=25, brackets=True))
        self.assertFalse(any(p['kind'] == 'connection' for p in data['parts']))
        self.assertEqual(len(data['connection_warnings']), 8)
        data = model.build_model(dict(demo.DEFAULTS, length=100, width=100, brackets=True))
        self.assertTrue(any('Montageraum' in warning for warning in data['connection_warnings']))
        self.assertLess(sum(p['kind'] == 'connection' for p in data['parts']), 8)

    def test_disable_and_settings_roundtrip_preserve_non_connector_parts(self):
        values = dict(demo.DEFAULTS, brackets=True, brackets_double=True)
        data = model.build_model(values)
        disabled = model.build_model(dict(values, brackets=False), data)
        self.assertEqual([p for p in data['parts'] if p['kind'] != 'connection'], disabled['parts'])
        self.assertEqual(model.build_model(values, disabled), data)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'settings.json'
            settings.save(values, path)
            self.assertEqual(settings.load(path), (values, ''))
        for key in ('brackets', 'brackets_double'):
            with self.assertRaises(ValueError):
                model.build_model(dict(values, **{key: 'yes'}))
