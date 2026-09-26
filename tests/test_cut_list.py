import csv
import io
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fusion_addin.FrameKit import cut_list, demo, model


class CutListTests(unittest.TestCase):
    def test_quantities_lengths_and_ids_match_generated_parts(self):
        data = model.build_model(dict(demo.DEFAULTS, shelf_count=2, shelf_heights=[250, 500],
                                     cross_members={'top': {'count': 2, 'direction': 'quer'}}))
        profiles = [p for p in data['parts'] if p['kind'] == 'profile']
        rows = cut_list.rows(data)
        self.assertEqual(sum(r[6] for r in rows), len(profiles))
        self.assertEqual({i for r in rows for i in r[8]}, {p['id'] for p in profiles})
        for row in rows:
            for identifier in row[8]:
                part = next(p for p in profiles if p['id'] == identifier)
                self.assertAlmostEqual(float(row[5]), part['cut_length_mm'], places=6)
        self.assertEqual(sum(r[6] for r in rows if float(r[5]) == 750), 4)

    def test_same_names_different_definitions_and_end_treatments_stay_separate(self):
        data = model.build_model(demo.DEFAULTS)
        part = data['parts'][0]
        other = deepcopy(data['profiles'][part['profile_ref']])
        other['id'] = 'different-profile'
        data['profiles'][other['id']] = other
        data['parts'][1]['profile_ref'] = other['id']
        data['parts'][2]['end_treatment'] = 'Bohrung'
        rows = [r for r in cut_list.rows(data) if float(r[5]) == part['cut_length_mm']]
        self.assertEqual(sorted(r[6] for r in rows), [1, 1, 2])

    def test_edit_uses_new_lengths_and_retains_part_ids(self):
        before = model.build_model(demo.DEFAULTS)
        after = model.build_model(dict(demo.DEFAULTS, length=1234.5), before)
        self.assertEqual({i for r in cut_list.rows(before) for i in r[8]},
                         {i for r in cut_list.rows(after) for i in r[8]})
        self.assertNotEqual(cut_list.csv_text(before), cut_list.csv_text(after))
        self.assertIn('1154,5', cut_list.csv_text(after))
        self.assertIn('1154.5', cut_list.csv_text(after, True))

    def test_csv_unicode_quotes_metadata_and_formula_protection(self):
        data = model.build_model(demo.DEFAULTS)
        profile = next(iter(data['profiles'].values()))
        profile.update(manufacturer='Müller; "Alu"', series='Serie A', article_number='=1+1')
        for international in (False, True):
            text = cut_list.csv_text(data, international)
            parsed = list(csv.reader(io.StringIO(text), delimiter=',' if international else ';'))
            self.assertEqual(parsed[1][0], 'Müller; "Alu"')
            self.assertEqual(parsed[1][2], "'=1+1")
            self.assertEqual(len(parsed[1]), len(cut_list.HEADERS))

    def test_atomic_utf8_export_and_failure_preserves_destination(self):
        data = model.build_model(demo.DEFAULTS)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'Zuschnitt.csv'
            cut_list.write_csv(target, data)
            original = target.read_bytes()
            self.assertTrue(original.startswith(b'\xef\xbb\xbf'))
            with patch.object(cut_list.os, 'replace', side_effect=OSError('locked')):
                with self.assertRaises(OSError):
                    cut_list.write_csv(target, data)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(Path(folder).iterdir()), [target])

    def test_invalid_length_is_rejected(self):
        data = model.build_model(demo.DEFAULTS)
        data['parts'][0]['cut_length_mm'] = float('nan')
        with self.assertRaises(ValueError):
            cut_list.rows(data)

    def test_rounding_noise_is_grouped_and_formatted_in_both_csv_formats(self):
        data = model.build_model(demo.DEFAULTS)
        data['parts'] = [p for p in data['parts'] if p['kind'] == 'profile'][:6]
        for part, length in zip(data['parts'],
                                (439.999999, 440.000001, 939.999999, 940, 440.125, 440.1255)):
            part['cut_length_mm'] = length
        for international, expected in ((False, ['440', '440,125', '440,126', '940']),
                                        (True, ['440', '440.125', '440.126', '940'])):
            records = list(csv.DictReader(io.StringIO(cut_list.csv_text(data, international)),
                                          delimiter=',' if international else ';'))
            self.assertEqual([r['Länge (mm)'] for r in records], expected)
            self.assertEqual([r['Menge'] for r in records], ['2', '1', '1', '2'])
            self.assertEqual(records[0]['Bauteil-IDs'], 'P001 | P002')
        self.assertEqual(data['parts'][0]['cut_length_mm'], 439.999999)
