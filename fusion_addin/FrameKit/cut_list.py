"""Profile cut lists from calculated properties, independent of Fusion UI."""
import csv
import io
import json
import math
import os
from pathlib import Path
import tempfile
from decimal import Decimal, ROUND_HALF_UP

HEADERS = ['Hersteller', 'Serie', 'Artikelnummer', 'Bezeichnung', 'Länge (mm)',
           'Menge', 'Endbearbeitung', 'Bauteil-IDs', 'Profil-ID', 'Gestell-ID']
FORMATS = ('Deutsch: Semikolon / Dezimalkomma', 'International: Komma / Dezimalpunkt')


def rows(model):
    if model.get('schema') != 1 or model.get('units') != 'mm':
        raise ValueError('Nicht unterstützte Bauteildaten für den Zuschnitt.')
    grouped = {}
    seen = set()
    for part in model['parts']:
        if part['kind'] != 'profile':
            continue
        profile = model['profiles'][part['profile_ref']]
        length = part['cut_length_mm']
        if not isinstance(length, (float, int)) or not math.isfinite(length) or length <= 0:
            raise ValueError('Ungültige Zuschnittlänge.')
        if part['id'] in seen:
            raise ValueError('Doppelte Bauteil-ID.')
        seen.add(part['id'])
        # Use the same 0.001 mm precision for grouping and displayed cut lengths.
        length = Decimal(str(length)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        ends = part.get('end_treatment', 'Beidseitig rechtwinklig; keine weitere Bearbeitung')
        key = (json.dumps(profile, sort_keys=True, ensure_ascii=False), length, ends)
        if key not in grouped:
            grouped[key] = [profile.get(field) or '' for field in
                            ('manufacturer', 'series', 'article_number', 'name', 'id')]
            grouped[key] += [length, 0, ends, [], model['assembly_id']]
        row = grouped[key]
        row[6] += 1
        row[8].append(part['id'])
    if not grouped:
        raise ValueError('Das Gestell enthält keine Profile.')
    return sorted(grouped.values(), key=lambda row: (row[0], row[1], row[3], row[4], row[5], row[7]))


def csv_text(model, international=False):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=',' if international else ';', lineterminator='\r\n')
    writer.writerow(HEADERS)
    for source in rows(model):
        row = list(source)
        length = format(row[5], 'f').rstrip('0').rstrip('.')
        row[5] = length if international else length.replace('.', ',')
        row[8] = ' | '.join(row[8])
        # Prevent spreadsheet formulas in user-provided metadata.
        for index in (0, 1, 2, 3, 4, 7, 8, 9):
            if str(row[index]).lstrip().startswith(('=', '+', '-', '@')):
                row[index] = "'" + str(row[index])
        writer.writerow([row[index] for index in (0, 1, 2, 3, 5, 6, 7, 8, 4, 9)])
    return stream.getvalue()


def write_csv(path, model, international=False):
    """Write UTF-8 with BOM atomically; failed exports preserve existing files."""
    content = csv_text(model, international)
    target = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8-sig', newline='',
                                         dir=target.parent, delete=False) as output:
            temporary = output.name
            output.write(content)
        os.replace(temporary, target)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)
