"""Regenerate portable synthetic examples and their local acceptance summary."""
from copy import deepcopy
import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fusion_addin.FrameKit import accessories, demo, model, profile_library, templates, cut_list, bill_of_materials


def generate():
    folder = ROOT/'examples'
    spec, raw = profile_library.prepare(ROOT/'tests/fixtures/synthetic_tslot_40.dxf', 'Synthetisches Nutprofil 40')
    spec['id'] = '00000000000000000000000000000040'
    spec['filename'] = spec['id']+'.dxf'
    basic = deepcopy(demo.DEFAULTS)
    shelves = dict(deepcopy(basic), height=1200.0, shelf_count=2, shelf_heights=[400.0, 800.0],
                   cross_members={key: dict(count=2, direction='quer') for key in ('top', 'shelf:01', 'shelf:02')})
    cart = dict(deepcopy(basic), frame_type='cart', corner_accessories=accessories.arrangement('cart'))
    dxf = dict(deepcopy(basic), profile_definition=spec)
    mixed = dict(deepcopy(basic), group_profiles={'posts': dict(definition=spec)})
    feet = dict(deepcopy(basic), accessory=deepcopy(accessories.PRESETS[0]))
    lowering = accessories.new_spec('Synthetische absenkbare Rolle', 'Absenkbare Rolle', 100, 75,
                                    reference='Synthetisches Beispiel, kein Herstellerteil', operating_state='abgesenkt',
                                    definition_version=2)
    lowering['id'] = 'example-lowering'
    entries = []
    summary = []
    for index, (name, values) in enumerate([
            ('01 Einfaches Gestell', basic), ('02 Zwei Zwischenböden', shelves),
            ('03 Transportwagen gemischte Rollen', cart), ('04 Eigenes DXF-Profil', dxf),
            ('05 Unterschiedliche Gruppenprofile', mixed), ('06 Gestell mit Füßen', feet),
            ('07 Absenkbare Rollen (synthetisch)', dict(deepcopy(basic), accessory=lowering))], 1):
        calculated = model.build_model(values)
        entries.append(dict(id=f'framekit-example-{index:02}', name=name, values=values))
        summary.append(dict(name=name, dimensions_mm=[values[k] for k in ('length', 'width', 'height')],
                            profile_count=sum(p['kind'] == 'profile' for p in calculated['parts']),
                            part_count=len(calculated['parts']), cut_list_positions=len(cut_list.rows(calculated)),
                            bom_positions=len(bill_of_materials.rows(calculated))))
    data = dict(schema=1, templates=entries, accessories=deepcopy(accessories.PRESETS)+[lowering],
                profiles=[spec], files={spec['filename']: base64.b64encode(raw).decode('ascii')})
    templates.validate_backup(data)
    (folder/'FrameKit-Beispiele.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (folder/'Erwartungswerte.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (folder/'synthetic_tslot_40.dxf').write_bytes(raw)


if __name__ == '__main__':
    generate()
