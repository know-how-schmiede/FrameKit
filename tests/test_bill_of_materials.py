import csv
import io
import tempfile
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch
from fusion_addin.FrameKit import model, demo, accessories, bill_of_materials as bom, csv_export


class BomTests(unittest.TestCase):
    def data(self, **changes):
        values = dict(demo.DEFAULTS, brackets=True, accessory=accessories.PRESETS[0],
                      shelf_count=1, shelf_heights=[300])
        values.update(changes)
        return model.build_model(values)

    def test_all_parts_counted_once_with_identifiers(self):
        data = self.data()
        rows = bom.rows(data)
        self.assertEqual(sum(r['count'] for r in rows), len(data['parts']))
        self.assertEqual(sorted(i for r in rows for i in r['ids']), sorted(p['id'] for p in data['parts']))
        self.assertEqual(sum(r['count'] for r in rows if r['kind']=='Platte'), 3)
        self.assertEqual(sum(r['count'] for r in rows if r['kind']=='Fuß'), 4)
        self.assertEqual(sum(r['count'] for r in rows if r['kind']=='Winkel'), 12)

    def test_notched_and_plain_panels_not_grouped(self):
        rows = [r for r in bom.rows(self.data(top_panel_mount='on_top')) if r['kind']=='Platte']
        self.assertEqual(sorted(r['count'] for r in rows), [1, 2])
        self.assertEqual(sorted(len(r['cutouts']) for r in rows), [0, 4])
        notched = next(r for r in rows if r['cutouts'])
        self.assertTrue(all(c['length_mm']==40 and c['width_mm']==40 for c in notched['cutouts']))

    def test_same_name_accessories_keep_definition_identity(self):
        first = deepcopy(accessories.PRESETS[0])
        second = dict(first, id='different')
        specs = {k: (first if i<2 else second) for i,k in enumerate(accessories.CORNERS)}
        rows = [r for r in bom.rows(self.data(corner_accessories=specs)) if r['kind']=='Fuß']
        self.assertEqual([r['count'] for r in rows], [2, 2])
        self.assertTrue(all('Platzhalter' in r['status'] for r in rows))

    def test_csv_both_formats_warnings_and_updated_dimensions(self):
        before = self.data()
        after = model.build_model(dict(before['configuration'], length=1234.5), before)
        after['connection_warnings'].append('Keine Montagefläche')
        for international in (False, True):
            text = bom.csv_text(after, international)
            rows = list(csv.DictReader(io.StringIO(text), delimiter=',' if international else ';'))
            self.assertEqual(next(r for r in rows if r['Art']=='Platte')['Länge (mm)'],
                             '1234.5' if international else '1234,5')
            self.assertTrue(any('Schrauben/Muttern' in r['Status'] for r in rows))
            self.assertTrue(any(r['Status']=='Keine Montagefläche' for r in rows))
        self.assertIn(bom.WARNING, bom.csv_text(self.data(brackets=False)))

    def test_export_two_files_and_rollback_second_write(self):
        with tempfile.TemporaryDirectory() as folder:
            a,b = Path(folder)/'a.csv', Path(folder)/'b.csv'
            a.write_text('original-a'); b.write_text('original-b')
            real = csv_export.os.replace
            def fail_second(source, target):
                if Path(target)==b:
                    raise OSError('locked')
                return real(source, target)
            with patch.object(csv_export.os, 'replace', side_effect=fail_second):
                with self.assertRaises(OSError):
                    csv_export.write_files([(a,'new-a'),(b,'new-b')])
            self.assertEqual(a.read_text(), 'original-a')
            self.assertEqual(b.read_text(), 'original-b')
            self.assertEqual(set(Path(folder).iterdir()), {a,b})
            csv_export.write_files([(a,'Müller'),(b,'Platte')])
            self.assertEqual(a.read_text(encoding='utf-8-sig'),'Müller')
            self.assertTrue(b.read_bytes().startswith(b'\xef\xbb\xbf'))

    def test_same_destination_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'list.csv'
            with self.assertRaises(ValueError):
                csv_export.write_files([(target,'one'),(target,'two')])
            self.assertFalse(target.exists())
