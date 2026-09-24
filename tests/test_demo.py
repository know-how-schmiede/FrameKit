"""Run with python -m unittest discover -s tests -v; no Fusion required."""
import itertools
import json
from pathlib import Path
import tempfile
import unittest

from fusion_addin.FrameKit import demo, settings
from fusion_addin.FrameKit.version import __version__


class DemoTests(unittest.TestCase):
    def test_layout_bounds_and_no_overlaps(self):
        for bottom in (True, False):
            values = dict(demo.DEFAULTS, bottom=bottom, length=1234, width=678, height=901)
            parts = demo.members(values)
            self.assertEqual(len(parts), 12 if bottom else 8)
            for axis, key in enumerate(('length', 'width', 'height')):
                self.assertEqual(min(p[1][axis] for p in parts), 0)
                self.assertEqual(max(p[1][axis] + p[2][axis] for p in parts), values[key])
            for first, second in itertools.combinations(parts, 2):
                overlap = all(min(first[1][a] + first[2][a], second[1][a] + second[2][a])
                              > max(first[1][a], second[1][a]) for a in range(3))
                self.assertFalse(overlap, (first[0], second[0]))

    def test_invalid_dimensions(self):
        for value in (0, -1, float('nan'), float('inf'), True, '800', 10001, 80):
            with self.subTest(value=value), self.assertRaises(ValueError):
                demo.members(dict(demo.DEFAULTS, length=value))

    def test_settings_roundtrip_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.json'
            self.assertEqual(settings.load(path), (demo.DEFAULTS, ''))
            values = dict(demo.DEFAULTS, length=1200, bottom=False)
            settings.save(values, path)
            self.assertEqual(settings.load(path), (values, ''))
            for content in ('broken', 'null', '[]', '{"schema": 2}',
                            '{"schema":1,"defaults":{}}'):
                path.write_text(content, encoding='utf-8')
                loaded, warning = settings.load(path)
                self.assertEqual(loaded, demo.DEFAULTS)
                self.assertTrue(warning)

    def test_invalid_save_preserves_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.json'
            settings.save(demo.DEFAULTS, path)
            previous = path.read_bytes()
            with self.assertRaises(ValueError):
                settings.save(dict(demo.DEFAULTS, height=-1), path)
            self.assertEqual(path.read_bytes(), previous)

    def test_manifest_version(self):
        manifest = Path(__file__).resolve().parents[1] / 'fusion_addin/FrameKit/FrameKit.manifest'
        self.assertEqual(json.loads(manifest.read_text(encoding='utf-8'))['version'], __version__)

    def test_automatic_shelves_have_equal_clear_gaps(self):
        for bottom in (False, True):
            values = dict(demo.DEFAULTS, bottom=bottom, shelf_count=3, shelf_heights=[None]*3)
            heights = demo.shelf_heights(values)
            depth = values['profile'] + values['shelf_thickness']
            lower = depth if bottom else 0
            gaps = []
            for top in heights:
                gaps.append(top - depth - lower)
                lower = top
            gaps.append(values['height'] - depth - lower)
            for gap in gaps:
                self.assertGreater(gap, 0)
                self.assertAlmostEqual(gap, gaps[0])

    def test_custom_and_partially_automatic_heights(self):
        values = dict(demo.DEFAULTS, shelf_count=3, shelf_heights=[None, 400, None])
        self.assertEqual(demo.shelf_heights(values), [229, 400, 575])
        values['shelf_heights'] = [200, 400, 600]
        self.assertEqual(demo.shelf_heights(values), [200, 400, 600])

    def test_shelves_and_plates_do_not_overlap(self):
        for bottom in (False, True):
            values = dict(demo.DEFAULTS, bottom=bottom, shelf_count=2, shelf_heights=[None, None])
            parts = demo.members(values)
            self.assertEqual(len(parts), (12 if bottom else 8) + 8)
            plates = demo.panels(values)
            self.assertEqual(len(plates), 4 if bottom else 3)
            for plate, height in zip([part for part in plates if part[0].startswith('Boden')],
                                     demo.shelf_heights(values)):
                self.assertAlmostEqual(plate[1][2] + plate[2][2], height)
                self.assertEqual(plate[2][2], 18)
            # Decompose the notched footprint into three disjoint rectangles.
            p = values['profile']
            for name, origin, size in plates:
                length, width, thickness = size
                z = origin[2]
                parts.extend([(name + ' Mitte', (p, 0, z), (length-2*p, width, thickness)),
                              (name + ' links', (0, p, z), (p, width-2*p, thickness)),
                              (name + ' rechts', (length-p, p, z), (p, width-2*p, thickness))])
            for first, second in itertools.combinations(parts, 2):
                overlap = all(min(first[1][a] + first[2][a], second[1][a] + second[2][a])
                              - max(first[1][a], second[1][a]) > 1e-7 for a in range(3))
                self.assertFalse(overlap, (first[0], second[0]))

    def test_invalid_shelves(self):
        cases = [dict(shelf_count=-1), dict(shelf_count=True), dict(shelf_count=21),
                 dict(shelf_count=1.5), dict(shelf_count=1, shelf_heights=[]),
                 dict(shelf_count=20, shelf_heights=[None]*20)]
        cases += [dict(shelf_count=1, shelf_heights=[value]) for value in
                  (-1, 50, 720, float('nan'), float('inf'), '200', True)]
        cases += [dict(shelf_count=2, shelf_heights=heights) for heights in
                  ([400, 300], [300, 300], [300, 320])]
        cases += [dict(shelf_count=1, shelf_heights=[300], shelf_thickness=t)
                  for t in (0, 10001, float('nan'), '18', True)]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                demo.members(dict(demo.DEFAULTS, **case))

    def test_notched_outline_area_and_corners(self):
        length, width, p = 800, 500, 40
        outline = demo.panel_outline(length, width, p)
        edges = list(zip(outline, outline[1:] + outline[:1]))
        area = sum(a[0]*b[1] - b[0]*a[1] for a, b in edges) / 2
        self.assertEqual(area, length*width - 4*p*p)
        self.assertEqual(len(set(outline)), 12)
        for a, b in edges:
            self.assertTrue((a[0] == b[0]) != (a[1] == b[1]))
        for x, y in outline:
            self.assertTrue(0 <= x <= length and 0 <= y <= width)
            self.assertFalse((x < p or x > length-p) and (y < p or y > width-p))

    def test_panel_on_each_frame_and_overall_height(self):
        for bottom in (False, True):
            for count in (0, 1, 3):
                values = dict(demo.DEFAULTS, bottom=bottom, shelf_count=count,
                              shelf_heights=[None]*count)
                parts = demo.members(values)
                plates = demo.panels(values)
                self.assertEqual(len(plates), 1 + int(bottom) + count)
                for name, origin, size in plates:
                    level = name.removesuffix(' Platte')
                    supports = [part for part in parts if part[0].startswith(f'Rahmen {level} ')]
                    self.assertEqual(len(supports), 4)
                    for _, support_origin, support_size in supports:
                        self.assertAlmostEqual(support_origin[2] + support_size[2], origin[2])
                    self.assertEqual(size[:2], (values['length'], values['width']))
                self.assertEqual(max(part[1][2] + part[2][2] for part in plates), values['height'])

    def test_thickness_checked_without_intermediate_shelves(self):
        for thickness in (0, -1, 400, float('nan'), '18', True):
            with self.subTest(thickness=thickness), self.assertRaises(ValueError):
                demo.members(dict(demo.DEFAULTS, shelf_thickness=thickness))

    def test_settings_migrate_and_preserve_shelf_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.json'
            old = {key: demo.DEFAULTS[key] for key in ('length', 'width', 'height', 'profile', 'bottom')}
            old['length'] = 1234
            path.write_text(json.dumps({'schema': 1, 'defaults': old}), encoding='utf-8')
            values, warning = settings.load(path)
            self.assertEqual(warning, '')
            self.assertEqual(values['length'], 1234)
            self.assertEqual(values['shelf_count'], 0)
            values.update(shelf_count=3, shelf_heights=[None, 400, None])
            settings.save(values, path)
            self.assertEqual(settings.load(path), (values, ''))


if __name__ == '__main__':
    unittest.main()
