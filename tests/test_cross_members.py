"""S03 geometry, persistence and height contracts without Fusion."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from fusion_addin.FrameKit import accessories, demo, model, settings
from fusion_addin.FrameKit.preview_data import display_geometry


class CrossMemberTests(unittest.TestCase):
    def test_equal_clear_gaps_both_directions_all_counts_and_levels(self):
        for direction in ('quer', 'laengs'):
            for count in range(6):
                values = dict(demo.DEFAULTS, shelf_count=2, shelf_heights=[250, 450])
                values['cross_members'] = {key: dict(count=count, direction=direction)
                                          for key, _ in demo.frame_levels(values)}
                parts = model.build_model(values)['parts']
                axis = 0 if direction == 'quer' else 1
                span = values['length' if axis == 0 else 'width']
                run = values['width' if axis == 0 else 'length']
                p = values['profile']
                for key, _ in demo.frame_levels(values):
                    beams = [part for part in parts if part['key'].startswith(key+':cross:')]
                    self.assertEqual(len(beams), count)
                    end = p
                    gaps = []
                    panel = next(part for part in parts if part['key'] == key+':panel')
                    for beam in beams:
                        gaps.append(beam['position_mm'][axis]-end)
                        end = beam['position_mm'][axis]+p
                        self.assertEqual(beam['cut_length_mm'], run-2*p)
                        self.assertEqual(beam['position_mm'][2]+p, panel['position_mm'][2])
                        self.assertEqual(beam['position_mm'][1-axis], p)
                    gaps.append(span-p-end)
                    for gap in gaps:
                        self.assertAlmostEqual(gap, (span-(count+2)*p)/(count+1))

    def test_top_mount_height_outline_and_preview(self):
        for mount in ('notched', 'on_top'):
            for accessory in (None, accessories.PRESETS[0]):
                values = dict(demo.DEFAULTS, top_panel_mount=mount, accessory=accessory)
                calculated = model.build_model(values)
                parts = calculated['parts']
                panel = next(p for p in parts if p['key'] == 'top:panel')
                self.assertEqual(len(panel['geometry']['points_mm']), 4 if mount == 'on_top' else 12)
                self.assertEqual(panel['position_mm'][2]+panel['bounds_mm'][2], values['height'])
                for post in (p for p in parts if p['group_id'] == 'posts'):
                    self.assertEqual(post['position_mm'][2], demo.base_height(values))
                    self.assertEqual(post['position_mm'][2]+post['cut_length_mm'],
                                     values['height']-(values['shelf_thickness'] if mount == 'on_top' else 0))
                bottom = next(p for p in parts if p['key'] == 'bottom:panel')
                self.assertEqual(len(bottom['geometry']['points_mm']), 12)
                shown = display_geometry(calculated)
                self.assertEqual(len(shown['panels']), (4 if mount == 'on_top' else 12)*3+36)

    def test_invalid_counts_direction_mount_and_tight_dimensions(self):
        for count in (-1, 6, True, 1.5):
            with self.assertRaises(ValueError):
                demo.validate(dict(demo.DEFAULTS, cross_members={'top': dict(count=count, direction='quer')}))
        for direction, dimension in (('quer', 'length'), ('laengs', 'width')):
            values = dict(demo.DEFAULTS, cross_members={'top': dict(count=5, direction=direction)})
            values[dimension] = 280
            with self.assertRaisesRegex(ValueError, 'zu wenig Platz'):
                demo.validate(values)
            values[dimension] = 281
            demo.validate(values)
        with self.assertRaises(ValueError):
            demo.validate(dict(demo.DEFAULTS, top_panel_mount='invalid'))
        with self.assertRaises(ValueError):
            demo.validate(dict(demo.DEFAULTS, cross_members={'top': dict(count=1, direction='invalid')}))

    def test_ids_persistence_and_legacy_defaults(self):
        values = deepcopy(demo.DEFAULTS)
        values.update(top_panel_mount='on_top', cross_members={'top': dict(count=5, direction='quer')})
        first = model.build_model(values)
        changed = dict(values, cross_members={'top': dict(count=2, direction='laengs')})
        second = model.build_model(changed, first)
        for part in second['parts']:
            self.assertEqual(part['id'], first['id_registry'][part['key']])
        self.assertEqual(model.build_model(values, second), first)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'settings.json'
            settings.save(values, path)
            self.assertEqual(settings.load(path), (values, ''))
            legacy = {k: v for k, v in demo.DEFAULTS.items() if k not in ('cross_members', 'top_panel_mount')}
            settings.save(legacy, path)
            self.assertEqual(settings.load(path), (demo.DEFAULTS, ''))
