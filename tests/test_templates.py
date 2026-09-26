from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fusion_addin.FrameKit import templates, demo, profile_library


class TemplatesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.entries = [dict(id='example', name='Werkbank', values=deepcopy(demo.DEFAULTS))]
        templates.save(self.entries, self.folder)

    def test_names_and_corrupt_file_preserved(self):
        with self.assertRaises(ValueError):
            templates.save(self.entries * 2, self.folder)
        self.assertEqual(templates.load(self.folder), self.entries)
        path = self.folder/'templates.json'
        path.write_text('{broken', encoding='utf-8')
        with self.assertRaises(ValueError):
            templates.snapshot(self.folder)
        self.assertEqual(path.read_text(), '{broken')

    def test_round_trip_with_dxf_and_defaults_untouched(self):
        spec, raw = profile_library.prepare(Path(__file__).parent/'fixtures/synthetic_tslot_40.dxf', 'Profil')
        profile_library.add(spec, raw, self.folder/'profiles')
        archive = self.folder/'backup.json'
        templates.export_file(archive, self.folder)
        backup = templates.read_backup(archive)
        target = self.folder/'target'
        target.mkdir()
        (target/'settings.json').write_bytes(b'personal defaults')
        planned, report = templates.plan_import(backup, 'skip', target)
        self.assertIn('Werkbank', report)
        self.assertFalse((target/'templates.json').exists())
        templates.apply_import(planned, target)
        self.assertEqual(templates.load(target), self.entries)
        profile_library.verify_source(spec, target/'profiles')
        self.assertEqual((target/'settings.json').read_bytes(), b'personal defaults')
        backup['files'][spec['filename']] = 'broken'
        with self.assertRaises(ValueError):
            templates.apply_import(backup, target)
        self.assertEqual(templates.load(target), self.entries)

    def test_conflicts_skip_copy_replace_and_cancel(self):
        incoming = templates.snapshot(self.folder)
        incoming['templates'][0]['values']['length'] += 100
        for mode, count in [('skip', 1), ('copy', 2), ('replace', 1)]:
            planned, report = templates.plan_import(incoming, mode, self.folder)
            self.assertEqual(len(planned['templates']), count)
            self.assertEqual(templates.load(self.folder), self.entries)
            if mode == 'replace':
                self.assertEqual(planned['templates'], incoming['templates'])
            elif mode == 'copy':
                self.assertNotEqual(planned['templates'][1]['id'], 'example')
        incoming['files']['../escape.dxf'] = ''
        with self.assertRaises(ValueError):
            templates.apply_import(incoming, self.folder)

    def test_failed_import_rolls_back_every_changed_file(self):
        incoming = templates.snapshot(self.folder)
        incoming['templates'][0]['name'] = 'Changed'
        before = {p.relative_to(self.folder): p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
        original = templates.atomic_bytes
        calls = 0
        def fail_once(path, content):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('disk full')
            original(path, content)
        with patch.object(templates, 'atomic_bytes', side_effect=fail_once):
            with self.assertRaises(OSError):
                templates.apply_import(incoming, self.folder)
        after = {p.relative_to(self.folder): p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
