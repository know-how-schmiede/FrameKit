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


if __name__ == '__main__':
    unittest.main()
