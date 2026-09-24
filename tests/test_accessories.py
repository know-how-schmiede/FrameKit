"""Accessory storage and dimension tests without Fusion."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from fusion_addin.FrameKit import accessories, demo, settings


class AccessoryTests(unittest.TestCase):
    def test_create_save_reload_delete_and_empty_library(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'accessories.json'
            entries, warning = settings.load_library(path)
            self.assertFalse(warning)
            self.assertEqual(entries, accessories.PRESETS)
            spec = accessories.new_spec('Eigene Rolle', 'Bockrolle', 120, 80)
            entries.append(spec)
            settings.save_library(entries, path)
            self.assertEqual(settings.load_library(path), (entries, ''))
            entries = [entry for entry in entries if entry['id'] != spec['id']]
            settings.save_library(entries, path)
            self.assertEqual(settings.load_library(path), (entries, ''))
            settings.save_library([], path)
            self.assertEqual(settings.load_library(path), ([], ''))

    def test_invalid_entries_and_duplicates_do_not_overwrite(self):
        spec = accessories.new_spec('Fuß A', 'Fuß', 40, 50)
        bad_specs = [dict(spec, height=value) for value in (0, -1, float('nan'), float('inf'), True, '40')]
        bad_specs += [dict(spec, diameter=value) for value in (0, 10001, None)]
        bad_specs += [dict(spec, name=' '), dict(spec, kind='Unbekannt'), dict(spec, id='')]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'accessories.json'
            settings.save_library([spec], path)
            before = path.read_bytes()
            for bad in bad_specs:
                with self.subTest(spec=bad), self.assertRaises(ValueError):
                    settings.save_library([bad], path)
                self.assertEqual(path.read_bytes(), before)
            for duplicate in (spec.copy(), dict(spec, id='different', name=' FUß A ')):
                with self.assertRaises(ValueError):
                    settings.save_library([spec, duplicate], path)
                self.assertEqual(path.read_bytes(), before)

    def test_bad_library_is_reported_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'accessories.json'
            for text in ('broken', 'null', '[]', '{"schema":2}', '{"schema":1,"entries":null}'):
                path.write_text(text, encoding='utf-8')
                entries, warning = settings.load_library(path)
                self.assertEqual(entries, [])
                self.assertTrue(warning)
                self.assertEqual(path.read_text(encoding='utf-8'), text)

    def test_four_cylinders_under_posts_with_constant_overall_height(self):
        for kind in accessories.KINDS:
            spec = accessories.new_spec('Platzhalter', kind, 100, 75)
            values = dict(demo.DEFAULTS, accessory=spec, shelf_count=2, shelf_heights=[None, None])
            supports = demo.supports(values)
            self.assertEqual(len(supports), 4)
            posts = [part for part in demo.members(values) if part[0].startswith('Pfosten')]
            for support, post in zip(supports, posts):
                _, origin, size = support
                self.assertEqual(size, (75, 75, 100))
                self.assertEqual(origin[2], 0)
                for axis in (0, 1):
                    self.assertEqual(origin[axis] + size[axis]/2, post[1][axis] + post[2][axis]/2)
                self.assertEqual(origin[2] + size[2], post[1][2])
                self.assertEqual(post[1][2] + post[2][2], values['height'])
            lower_plate = next(part for part in demo.panels(values) if part[0] == 'unten Platte')
            self.assertEqual(lower_plate[1][2], 140)
            self.assertEqual(max(part[1][2] + part[2][2] for part in demo.panels(values)), 750)
        self.assertEqual(demo.supports(demo.DEFAULTS), [])

    def test_support_height_affects_free_space_and_fixed_heights(self):
        spec = accessories.new_spec('Rolle', 'Lenkrolle', 100, 75)
        values = dict(demo.DEFAULTS, accessory=spec, shelf_count=2, shelf_heights=[None, None])
        tops = demo.shelf_heights(values)
        depth = 58
        previous = 100 + depth
        gaps = []
        for top in tops:
            gaps.append(top - depth - previous)
            previous = top
        gaps.append(750-depth-previous)
        for gap in gaps:
            self.assertAlmostEqual(gap, gaps[0])
        fixed = dict(values, shelf_heights=[300, 500])
        self.assertEqual(demo.shelf_heights(fixed), [300, 500])
        for bad in (dict(spec, height=700), dict(spec, diameter=600)):
            with self.assertRaises(ValueError):
                demo.members(dict(demo.DEFAULTS, accessory=bad))
        with self.assertRaises(ValueError):
            demo.members(dict(values, shelf_heights=[150, 500]))

    def test_saved_selection_is_a_snapshot_and_legacy_defaults_work(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.json'
            lib_path = Path(folder) / 'accessories.json'
            old = deepcopy(demo.DEFAULTS)
            old.pop('accessory')
            path.write_text(json.dumps({'schema': 1, 'defaults': old}), encoding='utf-8')
            migrated, warning = settings.load(path)
            self.assertFalse(warning)
            self.assertIsNone(migrated['accessory'])
            spec = accessories.new_spec('Eigener Fuß', 'Fuß', 50, 60)
            values = dict(migrated, accessory=spec)
            settings.save(values, path)
            settings.save_library([spec], lib_path)
            settings.save_library([], lib_path)
            self.assertEqual(settings.load(path), (values, ''))


if __name__ == '__main__':
    unittest.main()
