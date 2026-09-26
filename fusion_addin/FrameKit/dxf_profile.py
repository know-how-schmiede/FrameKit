"""Strict 2D ASCII DXF reader for extrusion sections; exact lines/arcs/circles.

No optional Python packages are required in Fusion. Reference points and marked
construction geometry are ignored; unsupported contour geometry is rejected. Coordinates and
tolerances below are in mm.
"""
from math import atan2, atan, cos, sin, hypot, isfinite, pi, tau

TOL = 1e-5
MAX_BYTES = 4 * 1024 * 1024
MAX_CURVES = 2000
UNITS = {1: ('in', 25.4), 2: ('ft', 304.8), 4: ('mm', 1.0),
         5: ('cm', 10.0), 6: ('m', 1000.0)}
SCALES = {name: factor for name, factor in UNITS.values()}
# Export convention, not a universal DXF construction flag. Do not infer
# construction geometry from open endpoints or arbitrary layer names.
CONSTRUCTION_LINETYPES = {name + suffix
    for name in ('DASHED', 'DASHDOT', 'CENTER', 'CENTRE', 'PHANTOM')
    for suffix in ('', '2', 'X2')}


def number(value):
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ValueError('DXF enthält eine ungültige Zahl.') from None
    if not isfinite(result) or abs(result) > 1e9:
        raise ValueError('DXF enthält eine nicht endliche oder zu große Koordinate.')
    return result


def integer(value):
    result = number(value)
    if result != int(result):
        raise ValueError('DXF-Flags und Einheiten müssen ganze Zahlen sein.')
    return int(result)


def read(data, unit='auto'):
    if not isinstance(data, bytes) or not data or len(data) > MAX_BYTES:
        raise ValueError('DXF ist leer oder größer als 4 MiB.')
    if data.startswith(b'AutoCAD Binary DXF'):
        raise ValueError('Binäre DXF nicht unterstützt. Bitte als ASCII-DXF exportieren.')
    lines = data.decode('utf-8-sig', errors='replace').splitlines()
    if len(lines) % 2:
        raise ValueError('DXF-Gruppencodes sind unvollständig.')
    try:
        pairs = [(int(lines[i].strip()), lines[i+1].strip()) for i in range(0, len(lines), 2)]
    except ValueError:
        raise ValueError('Keine gültige ASCII-DXF-Datei.') from None
    if not pairs or pairs[-1] != (0, 'EOF'):
        raise ValueError('DXF-Dateiende fehlt.')
    header, entities, tables, section, record = [], [], [], None, None
    for index, (code, value) in enumerate(pairs):
        if code == 0 and value == 'SECTION':
            if section is not None or index+1 >= len(pairs) or pairs[index+1][0] != 2:
                raise ValueError('Ungültige DXF-Abschnitte.')
            section = pairs[index+1][1]
            continue
        if code == 0 and value == 'ENDSEC':
            section, record = None, None
            continue
        if section == 'HEADER':
            header.append((code, value))
        elif section in ('ENTITIES', 'TABLES'):
            if code == 0:
                record = [value, []]
                (entities if section == 'ENTITIES' else tables).append(record)
            elif record is not None:
                record[1].append((code, value))
    if section is not None:
        raise ValueError('DXF-Abschnitt wurde nicht mit ENDSEC abgeschlossen.')
    declared = 0
    for index, pair in enumerate(header):
        if pair == (9, '$INSUNITS') and index+1 < len(header):
            declared = integer(header[index+1][1])
    if unit == 'auto':
        if declared not in UNITS:
            raise ValueError('DXF-Einheit fehlt oder wird nicht unterstützt. Einheit ausdrücklich auswählen.')
        unit, scale = UNITS[declared]
    elif unit in SCALES:
        scale = SCALES[unit]
    else:
        raise ValueError('Ungültige DXF-Einheit.')
    curves, pending, vertices = [], None, []
    ignored = dict(points=0, construction=0)
    skip_polyline = False

    def text_field(fields, code, default):
        values = [value for key, value in fields if key == code]
        if len(values) > 1:
            raise ValueError(f'DXF-Gruppencode {code} ist mehrdeutig.')
        return values[0].upper() if values else default

    layers = {}
    for kind, fields in tables:
        if kind == 'LAYER':
            layers[text_field(fields, 2, '0')] = text_field(fields, 6, 'CONTINUOUS')

    def construction(fields):
        linetype = text_field(fields, 6, 'BYLAYER')
        if linetype == 'BYLAYER':
            linetype = layers.get(text_field(fields, 8, '0'), 'CONTINUOUS')
        return linetype in CONSTRUCTION_LINETYPES

    def get(fields, code, default=None):
        found = [value for key, value in fields if key == code]
        if len(found) > 1:
            raise ValueError(f'DXF-Gruppencode {code} ist mehrdeutig.')
        if not found:
            if default is None:
                raise ValueError(f'DXF-Gruppencode {code} fehlt.')
            return default
        return number(found[0])

    def planar(fields):
        for code, value in fields:
            if code in (30, 31, 38, 39) and abs(number(value)*scale) > TOL:
                raise ValueError('Der Profilquerschnitt muss in der XY-Ebene bei Z=0 liegen.')
        normal = [get(fields, code, default) for code, default in ((210, 0), (220, 0), (230, 1))]
        if any(abs(a-b) > 1e-9 for a, b in zip(normal, (0, 0, 1))):
            raise ValueError('DXF-Ausrichtung muss +Z sein; bitte in die XY-Ebene exportieren.')
        if get(fields, 67, 0) != 0:
            raise ValueError('Papierbereich wird nicht unterstützt; nur den Querschnitt exportieren.')

    def point(fields, x=10, y=20):
        return [get(fields, x)*scale, get(fields, y)*scale]

    def poly(fields, points):
        flags = integer(get(fields, 70, 0))
        if flags & ~129:
            raise ValueError('Nur ebene, ungeglättete 2D-Polylinien sind unterstützt.')
        if len(points) < 2:
            raise ValueError('Polylinie enthält zu wenige Punkte.')
        for code, value in fields:
            if code in (40, 41, 43) and number(value) != 0:
                raise ValueError('Polylinienbreite muss 0 sein; bitte Konturen exportieren.')
        edges = list(zip(points, points[1:]))
        if flags & 1:
            edges.append((points[-1], points[0]))
        for (start, bulge), (end, _) in edges:
            dx, dy = end[0]-start[0], end[1]-start[1]
            if hypot(dx, dy) <= TOL:
                raise ValueError('DXF enthält ein Segment ohne Länge oder doppelte Endpunkte.')
            if abs(bulge) < 1e-12:
                curves.append(dict(type='line', start=start, end=end))
            else:
                center = [(start[0]+end[0])/2-dy*(1-bulge*bulge)/(4*bulge),
                          (start[1]+end[1])/2+dx*(1-bulge*bulge)/(4*bulge)]
                curves.append(dict(type='arc', center=center,
                    radius=hypot(start[0]-center[0], start[1]-center[1]),
                    start_angle=atan2(start[1]-center[1], start[0]-center[0]), sweep=4*atan(bulge)))

    for kind, fields in entities:
        if skip_polyline:
            if kind == 'SEQEND':
                skip_polyline = False
            elif kind != 'VERTEX':
                raise ValueError('POLYLINE ohne SEQEND.')
            continue
        planar(fields)
        if pending is not None:
            if kind == 'VERTEX':
                if integer(get(fields, 70, 0)) != 0:
                    raise ValueError('Nur einfache 2D-Polylinienpunkte werden unterstützt.')
                for code in (40, 41):
                    if get(fields, code, 0) != 0:
                        raise ValueError('Polylinienbreite muss 0 sein.')
                vertices.append((point(fields), get(fields, 42, 0)))
                continue
            if kind != 'SEQEND':
                raise ValueError('POLYLINE ohne SEQEND.')
            poly(pending, vertices)
            pending, vertices = None, []
            continue
        if kind == 'POINT':
            # Sketch exports may include reference/origin points. These have
            # no contour or area and must not affect bounds or connectivity.
            point(fields)
            ignored['points'] += 1
            continue
        if kind in ('XLINE', 'RAY') or (kind in (
                'LINE', 'ARC', 'CIRCLE', 'LWPOLYLINE', 'POLYLINE') and construction(fields)):
            ignored['construction'] += 1
            skip_polyline = kind == 'POLYLINE'
            continue
        if kind == 'LINE':
            curves.append(dict(type='line', start=point(fields), end=point(fields, 11, 21)))
        elif kind in ('ARC', 'CIRCLE'):
            curve = dict(type=kind.lower(), center=point(fields), radius=get(fields, 40)*scale)
            if kind == 'ARC':
                curve.update(start_angle=get(fields, 50)*pi/180,
                             sweep=((get(fields, 51)-get(fields, 50)) % 360)*pi/180)
            curves.append(curve)
        elif kind == 'LWPOLYLINE':
            points, vertex = [], []
            for code, value in fields:
                if code == 10 and vertex:
                    points.append((point(vertex), get(vertex, 42, 0)))
                    vertex = []
                if code in (10, 20, 42):
                    vertex.append((code, value))
            if vertex:
                points.append((point(vertex), get(vertex, 42, 0)))
            if get(fields, 90) != len(points):
                raise ValueError('Falsche Punktanzahl in LWPOLYLINE.')
            poly(fields, points)
        elif kind == 'POLYLINE':
            pending = fields
        else:
            raise ValueError(f'DXF-Element {kind} wird nicht unterstützt. '
                             'Nur LINE, ARC, CIRCLE und 2D-(LW)POLYLINE exportieren; Blöcke vorher auflösen.')
        if len(curves) > MAX_CURVES:
            raise ValueError('DXF enthält zu viele Konturelemente (maximal 2000).')
    if pending is not None or skip_polyline:
        raise ValueError('POLYLINE ohne SEQEND.')
    geometry = inspect(curves)
    geometry.update(source_unit=unit, declared_unit=declared, scale_to_mm=scale)
    geometry['ignored_entities'] = ignored
    return geometry


def arc_point(curve, angle):
    return [curve['center'][0]+curve['radius']*cos(angle),
            curve['center'][1]+curve['radius']*sin(angle)]


def endpoints(curve):
    if curve['type'] == 'line':
        return curve['start'], curve['end']
    return arc_point(curve, curve['start_angle']), arc_point(curve, curve['start_angle']+curve['sweep'])


def on_arc(curve, angle):
    if curve['type'] == 'circle':
        return True
    sweep = curve['sweep']
    delta = ((angle-curve['start_angle']) if sweep > 0 else (curve['start_angle']-angle)) % tau
    return delta <= abs(sweep)+1e-9 or tau-delta < 1e-9


def inspect(curves):
    """Validate numbers, centered square bounds, and closed nonbranching chains.

    Fusion additionally validates topology and the single connected material area
    before a profile is added to the library or extruded into a frame.
    """
    if not isinstance(curves, list) or not 1 <= len(curves) <= MAX_CURVES:
        raise ValueError('DXF benötigt 1–2000 Konturelemente.')
    bounds, nodes, edges = [], [], []

    def point(value):
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError('Ungültiger DXF-Punkt.')
        for coordinate in value:
            if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
                raise ValueError('Ungültige DXF-Koordinate.')
            number(coordinate)
        return value

    def node(value):
        for index, candidate in enumerate(nodes):
            if hypot(value[0]-candidate[0], value[1]-candidate[1]) <= TOL:
                return index
        nodes.append(value)
        return len(nodes)-1

    for curve in curves:
        if not isinstance(curve, dict) or curve.get('type') not in ('line', 'arc', 'circle'):
            raise ValueError('Ungültiges Konturelement.')
        kind = curve['type']
        if kind == 'line':
            start, end = point(curve['start']), point(curve['end'])
            if hypot(start[0]-end[0], start[1]-end[1]) <= TOL:
                raise ValueError('DXF enthält eine Linie ohne Länge.')
            bounds.extend((start, end))
        else:
            point(curve['center'])
            radius = number(curve['radius'])
            if radius <= TOL:
                raise ValueError('DXF-Kreisradius muss positiv sein.')
            if kind == 'arc':
                number(curve['start_angle'])
                sweep = number(curve['sweep'])
                if not 1e-9 < abs(sweep) < tau-1e-9:
                    raise ValueError('Ungültiger DXF-Kreisbogen.')
                start, end = endpoints(curve)
                bounds.extend((start, end))
            for angle in (0, pi/2, pi, 3*pi/2):
                if on_arc(curve, angle):
                    bounds.append(arc_point(curve, angle))
            if kind == 'circle':
                continue
        edges.append((node(start), node(end), curve))
    low = [min(p[i] for p in bounds) for i in (0, 1)]
    high = [max(p[i] for p in bounds) for i in (0, 1)]
    width, height = [high[i]-low[i] for i in (0, 1)]
    if any(abs(high[i]+low[i])/2 > TOL for i in (0, 1)):
        raise ValueError('Profilmittelpunkt liegt nicht im Ursprung (0, 0). Bitte DXF zentrieren.')
    if not 1 <= min(width, height) <= max(width, height) <= 10000:
        raise ValueError('Profilmaße müssen zwischen 1 und 10000 mm liegen. DXF-Einheit prüfen.')
    adjacent = [[] for _ in nodes]
    for index, (a, b, _) in enumerate(edges):
        adjacent[a].append(index)
        adjacent[b].append(index)
    if any(len(items) != 2 for items in adjacent):
        raise ValueError('Offene oder verzweigte DXF-Kontur: jeder Endpunkt muss genau zwei Segmente verbinden.')
    areas = [pi*c['radius']**2 for c in curves if c['type'] == 'circle']
    visited = set()
    for first in range(len(edges)):
        if first in visited:
            continue
        current, start_node = first, edges[first][0]
        here, integral = start_node, 0.0
        while current not in visited:
            visited.add(current)
            a, b, curve = edges[current]
            direction = 1 if here == a else -1
            begin, end = endpoints(curve)
            if curve['type'] == 'line':
                value = (begin[0]*end[1]-end[0]*begin[1])/2
            else:
                cx, cy = curve['center']
                value = (cx*(end[1]-begin[1])-cy*(end[0]-begin[0])
                         +curve['radius']**2*curve['sweep'])/2
            integral += direction*value
            here = b if direction == 1 else a
            current = next((i for i in adjacent[here] if i not in visited), first)
        if here != start_node or abs(integral) <= TOL*TOL:
            raise ValueError('DXF-Kontur ist nicht geschlossen oder hat keine Fläche.')
        areas.append(abs(integral))
    material_area = 2*max(areas)-sum(areas)
    if material_area <= TOL*TOL:
        raise ValueError('DXF enthält keine eindeutige Materialfläche.')
    return dict(curves=curves, width_mm=width, height_mm=height,
                loop_count=len(areas), area_mm2=material_area)
