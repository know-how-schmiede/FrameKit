"""Manufacturing/ordering list from saved FrameKit properties, not display names."""
import csv
import io
import json
from decimal import Decimal, ROUND_HALF_UP
from . import cut_list

HEADERS = ['Hersteller', 'Serie', 'Artikelnummer', 'Bezeichnung', 'Länge (mm)',
           'Menge', 'Endbearbeitung', 'Bauteil-IDs', 'Art', 'Breite (mm)',
           'Stärke / Höhe (mm)', 'Durchmesser (mm)', 'Eckausklinkungen',
           'Material', 'Definitions-ID', 'Gestell-ID', 'Status', 'Definition']
WARNING = 'Montagezuordnung unvollständig: Schrauben/Muttern und weitere Befestigungen nicht definiert.'


def number(value, international=False):
    if value is None:
        return ''
    text = format(Decimal(str(value)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), 'f').rstrip('0').rstrip('.')
    return text if international else text.replace('.', ',')


def rows(model):
    result = []
    for row in cut_list.rows(model):
        manufacturer, series, article, name, ref, length, count, ends, ids, assembly = row
        spec = model['profiles'][ref]
        result.append(dict(manufacturer=manufacturer, series=series, article=article, name=name,
            length=length, count=count, ends=ends, ids=ids, kind='Profil', width=spec['width_mm'],
            height=spec['height_mm'], material=spec.get('material') or '', ref=ref,
            status='Demo-Vollprofil' if spec.get('is_demo') else '',
            definition={k: spec.get(k) for k in ('id', 'name', 'manufacturer', 'series', 'article_number',
                        'width_mm', 'height_mm', 'material', 'slot_size', 'source_sha256')} ))
    grouped = {}
    for part in model['parts']:
        kind = part['kind']
        if kind == 'profile':
            continue
        if kind == 'panel':
            spec = part['panel_definition']
            row = dict(name='Platte', kind='Platte', length=spec['length_mm'], width=spec['width_mm'],
                       height=spec['thickness_mm'], cutouts=spec['corner_cutouts'],
                       material=spec.get('material') or '', status='Material nicht festgelegt' if not spec.get('material') else '')
        elif kind == 'support':
            spec = part['accessory_definition']
            row = dict(name=spec['name'], kind=spec['kind'], ref=spec['id'], height=spec['height'],
                       diameter=spec['diameter'], status='Platzhalter; Zubehördefinition prüfen')
        elif kind == 'connection':
            spec = {k: v for k, v in part['connection_definition'].items()
                    if k not in ('member_keys', 'parallel_count')}
            spec['source'] = part['geometry']['source']
            size = spec['size_mm']
            row = dict(name=f'Winkel {size:g}x{size:g}', kind='Winkel', length=size, width=size,
                       height=size, ref=spec['source'], status='STEP-Winkel; Schrauben/Muttern fehlen')
        else:
            raise ValueError(f'Unbekannte Bauteilart: {kind}')
        key = (kind, json.dumps(spec, sort_keys=True, ensure_ascii=False))
        if key not in grouped:
            row.update(definition=spec, count=0, ids=[])
            grouped[key] = row
        grouped[key]['count'] += 1
        grouped[key]['ids'].append(part['id'])
    result.extend(grouped.values())
    return result


def csv_text(model, international=False):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=',' if international else ';', lineterminator='\r\n')
    writer.writerow(HEADERS)
    for row in rows(model):
        cutouts = ' | '.join(f"{c['corner']}: {number(c['length_mm'], international)} x {number(c['width_mm'], international)} mm"
                             for c in row.get('cutouts', []))
        if row['kind'] == 'Platte' and not cutouts:
            cutouts = 'Keine'
        values = [row.get('manufacturer', ''), row.get('series', ''), row.get('article', ''), row['name'],
            number(row.get('length'), international), row['count'], row.get('ends', ''), ' | '.join(row['ids']),
            row['kind'], number(row.get('width'), international), number(row.get('height'), international),
            number(row.get('diameter'), international), cutouts, row.get('material', ''), row.get('ref', ''),
            model['assembly_id'], row.get('status', ''), json.dumps(row['definition'], ensure_ascii=False, sort_keys=True)]
        writer.writerow(["'"+str(v) if str(v).lstrip().startswith(('=', '+', '-', '@')) else v for v in values])
    # Explicit warning even for frames without optional brackets.
    warning = [''] * len(HEADERS)
    warning[3], warning[8], warning[15], warning[16] = 'Hinweis zur Vollständigkeit', 'Hinweis', model['assembly_id'], WARNING
    writer.writerow(warning)
    for message in model.get('connection_warnings', []):
        warning[16] = message
        writer.writerow(warning)
    return stream.getvalue()
