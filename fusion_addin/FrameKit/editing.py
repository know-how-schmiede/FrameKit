"""Read stored frames and replace only a validated, owned root occurrence."""
from copy import deepcopy
from itertools import product
import json

from . import demo
from .model import build_model

CONFIGURATION_SCHEMA = 1


def attribute(entity, name):
    item = entity.attributes.itemByName('FrameKit', name)
    return item.value if item else None


def frames(design):
    return [occ for occ in design.rootComponent.occurrences
            if attribute(occ.component, 'configuration') is not None
            or attribute(occ.component, 'demoConfiguration') is not None]


def decode(configuration=None, legacy=None, model_data=None, assembly_id=None):
    """Migrate legacy defaults without substituting current library definitions."""
    try:
        if configuration is not None:
            saved = json.loads(configuration)
            if saved['schema'] != CONFIGURATION_SCHEMA:
                raise ValueError('Nicht unterstützte Konfigurationsversion.')
            stored = saved['values']
        elif legacy is not None:
            stored = json.loads(legacy)
        else:
            raise ValueError('Keine gespeicherte FrameKit-Konfiguration vorhanden.')
        if not isinstance(stored, dict):
            raise ValueError('Ungültige Gestellkonfiguration.')
        for key in ('length', 'width', 'height', 'profile', 'bottom'):
            if key not in stored:
                raise ValueError(f'Gespeicherte Konfiguration unvollständig: {key}.')
        values = deepcopy(demo.DEFAULTS)
        values.update(stored)
        # Old frames without brackets must not acquire them simply by opening.
        values.setdefault('brackets', False)
        values.setdefault('brackets_double', False)
        previous = json.loads(model_data) if model_data is not None else None
        if previous is not None:
            if assembly_id and previous['assembly_id'] != assembly_id:
                raise ValueError('Baugruppen-ID und gespeicherte Bauteildaten widersprechen sich.')
            if previous.get('configuration') != stored:
                raise ValueError('Konfiguration und gespeicherte Bauteildaten widersprechen sich.')
        elif assembly_id:
            previous = dict(schema=1, assembly_id=assembly_id, id_registry={})
        calculated = build_model(values, previous)
        return values, calculated
    except (KeyError, TypeError, AttributeError, OverflowError) as error:
        raise ValueError('Gespeicherte FrameKit-Daten sind unvollständig oder beschädigt.') from error


def check_owned(design, occurrence):
    if not occurrence.isValid or occurrence not in list(design.rootComponent.occurrences):
        raise ValueError('Das Gestell ist nicht mehr als Hauptbaugruppe verfügbar. Dialog erneut öffnen.')
    if occurrence.isReferencedComponent:
        raise ValueError('Verknüpftes Gestell zuerst im Quelldokument bearbeiten.')
    component = occurrence.component
    if sum(o.component == component for o in design.rootComponent.allOccurrences) != 1:
        raise ValueError('Mehrfach verwendete Gestellkomponente zuerst unabhängig machen.')
    frame_id = attribute(component, 'assemblyId')

    def visit(parent):
        for child in parent.occurrences:
            owner = attribute(child, 'assemblyId') or attribute(child.component, 'assemblyId')
            if not frame_id or owner != frame_id:
                raise ValueError('Zusätzlich eingefügte oder fremde Komponente im Gestell: '
                                 f'{child.component.name}. Vor dem Neuaufbau außerhalb des Gestells ablegen.')
            visit(child.component)
    visit(component)


def load(design, occurrence):
    check_owned(design, occurrence)
    component = occurrence.component
    stamp = tuple(attribute(component, key) for key in
                  ('configuration', 'demoConfiguration', 'modelData', 'assemblyId'))
    values, calculated = decode(*stamp)
    return dict(occurrence=occurrence, design=design, stamp=stamp,
                values=values, model=calculated, transform=occurrence.transform2.copy())


def check_current(context):
    occurrence = context['occurrence']
    check_owned(context['design'], occurrence)
    stamp = tuple(attribute(occurrence.component, key) for key in
                  ('configuration', 'demoConfiguration', 'modelData', 'assemblyId'))
    if stamp != context['stamp']:
        raise ValueError('Das gespeicherte Gestell wurde zwischenzeitlich geändert. Dialog erneut öffnen.')
    if occurrence.transform2.asArray() != context['transform'].asArray():
        raise ValueError('Das Gestell wurde zwischenzeitlich verschoben. Dialog erneut öffnen.')


def replace(context, values, calculated):
    """Must run in a Fusion execute transaction; the caller aborts on any error."""
    from .geometry import create_frame
    check_current(context)
    design, old = context['design'], context['occurrence']
    new = create_frame(design, values, calculated, placement=context['transform'])
    new.isLightBulbOn = old.isLightBulbOn
    # Last operation: retain the old occurrence until the new frame is complete.
    # Delete the owned occurrence and its component history instead of appending
    # a Remove feature. The execute transaction still provides command-level Undo.
    if not old.deleteMe():
        raise RuntimeError('Altes Gestell konnte nicht ersetzt werden.')
    return new


def preview_model(model, transform):
    """Apply the root occurrence placement only to display data (cm -> mm)."""
    matrix = [[transform.getCell(i, j) for j in range(4)] for i in range(3)]
    def vector(v):
        return [sum(matrix[i][j]*v[j] for j in range(3)) for i in range(3)]
    def point(v):
        return [n+10*matrix[i][3] for i, n in enumerate(vector(v))]
    result = deepcopy(model)
    for part in result['parts']:
        part['position_mm'] = point(part['position_mm'])
        part['orientation'] = [vector(axis) for axis in part['orientation']]
        if part['centerline_mm'] is not None:
            part['centerline_mm'] = [point(v) for v in part['centerline_mm']]
        corners = [point([a+b*t for a, b, t in zip(part['bounds_origin_mm'], part['bounds_mm'], bits)])
                   for bits in product((0, 1), repeat=3)]
        low = [min(v[i] for v in corners) for i in range(3)]
        part['bounds_origin_mm'] = low
        part['bounds_mm'] = [max(v[i] for v in corners)-low[i] for i in range(3)]
    return result
