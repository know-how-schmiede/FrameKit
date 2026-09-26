"""Distribution integrity and portable acceptance examples; no Fusion UI."""
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from installer import package
from fusion_addin.FrameKit import templates, model, cut_list, bill_of_materials


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def test_reproducible_complete_package_and_hashes(self):
        first = package.build(self.folder/'first.zip')
        second = package.build(self.folder/'second.zip')
        self.assertEqual(first.read_bytes(), second.read_bytes())
        version, count = package.verify(first)
        self.assertGreater(count, 50)
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(json.loads(archive.read('FrameKit/FrameKit.manifest'))['version'], version)
            self.assertFalse(any('__pycache__' in name for name in archive.namelist()))
        self.assertEqual(first.with_suffix('.zip.sha256').read_text().split()[0], package.digest(first.read_bytes()))

    def test_tampered_missing_and_duplicate_entries_rejected(self):
        source = package.build(self.folder/'source.zip')
        with zipfile.ZipFile(source) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        for scenario in ('tampered', 'missing', 'traversal'):
            changed = dict(files)
            if scenario == 'tampered':
                changed['FrameKit/version.py'] += b'\n# changed\n'
            elif scenario == 'missing':
                del changed['FrameKit/resources/brackets/Winkel_20x20.step']
            else:
                changed['../escape'] = b'escape'
            target = self.folder/(scenario+'.zip')
            with zipfile.ZipFile(target, 'w') as archive:
                for name, data in changed.items():
                    archive.writestr(name, data)
            with self.assertRaises(ValueError):
                package.verify(target)
        with zipfile.ZipFile(source, 'a') as archive:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                archive.writestr('LICENSE', b'duplicate')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            package.verify(source)

    def test_personal_data_and_version_mismatch_rejected(self):
        files = package.collect()
        files['FrameKit/settings.json'] = b'{}'
        with self.assertRaises(ValueError):
            package.validate(files)
        del files['FrameKit/settings.json']
        files['FrameKit/version.py'] = b"__version__ = '999.0.0'\n"
        with self.assertRaises(ValueError):
            package.validate(files)

    def test_example_transfer_and_model_list_consistency(self):
        incoming = templates.read_backup(package.ROOT/'examples/FrameKit-Beispiele.json')
        planned, _ = templates.plan_import(incoming, 'skip', self.folder)
        templates.apply_import(planned, self.folder)
        expected = json.loads((package.ROOT/'examples/Erwartungswerte.json').read_text(encoding='utf-8'))
        entries = templates.load(self.folder)
        self.assertEqual(len(entries), 7)
        for entry, reference in zip(entries, expected):
            calculated = model.build_model(entry['values'])
            self.assertEqual(entry['name'], reference['name'])
            self.assertEqual(len(calculated['parts']), reference['part_count'])
            profile_count = sum(p['kind'] == 'profile' for p in calculated['parts'])
            self.assertEqual(profile_count, reference['profile_count'])
            self.assertEqual(sum(row[6] for row in cut_list.rows(calculated)), profile_count)
            self.assertEqual(len(cut_list.rows(calculated)), reference['cut_list_positions'])
            self.assertEqual(len(bill_of_materials.rows(calculated)), reference['bom_positions'])
            previous = {part['key']: part['id'] for part in calculated['parts']}
            changed = dict(entry['values'], length=entry['values']['length']+100)
            rebuilt = model.build_model(changed, calculated)
            self.assertEqual({p['key']: p['id'] for p in rebuilt['parts']}, previous)
            self.assertTrue(cut_list.csv_text(rebuilt))
            self.assertTrue(bill_of_materials.csv_text(rebuilt))
