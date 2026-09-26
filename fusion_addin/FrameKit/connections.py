"""Mounting positions and conservative envelopes for the supplied STEP brackets."""
from itertools import product


def overlaps(a, b):
    """Convex XY footprints and Z intervals; touching mounting faces are allowed."""
    if min(a[2], b[2]) <= max(a[1], b[1])+1e-7:
        return False
    for polygon in (a[0], b[0]):
        for start, end in zip(polygon, polygon[1:]+polygon[:1]):
            axis = (start[1]-end[1], end[0]-start[0])
            pa = [sum(x*y for x, y in zip(point, axis)) for point in a[0]]
            pb = [sum(x*y for x, y in zip(point, axis)) for point in b[0]]
            if min(max(pa), max(pb)) <= max(min(pa), min(pb))+1e-7:
                return False
    return True


def envelope(part):
    x, y, z = part['bounds_origin_mm']
    w, d, h = part['bounds_mm']
    return ([(x, y), (x+w, y), (x+w, y+d), (x, y+d)], z, z+h)


def generate(parts, profiles, double_wide=False):
    """Frame inside corners and one flank at each cross-member end.

    The STEP brackets occupy size x size x size mounting envelopes.
    Optional parallel brackets are spread over the shared vertical mounting span.
    """
    result, warnings = [], []
    by_key = {p['key']: p for p in parts}
    obstacles = [envelope(p) for p in parts]
    accepted = []

    def joint(key, label, first, second, candidates):
        sizes = [min(profiles[p['profile_ref']]['width_mm'],
                     profiles[p['profile_ref']]['height_mm']) for p in (first, second)]
        size = next((s for s in (20, 30, 40) if all(abs(v-s) < 1e-5 for v in sizes)), None)
        if size is None:
            warnings.append(f'{label}: keine gemeinsame Winkelgröße 20/30/40 zugeordnet.')
            return
        bottom = max(p['bounds_origin_mm'][2] for p in (first, second))
        top = min(p['bounds_origin_mm'][2]+p['bounds_mm'][2] for p in (first, second))
        height = top-bottom
        count = 2 if double_wide and height >= 2*size-1e-5 else 1
        if height < size-1e-5:
            warnings.append(f'{label}: zu wenig gemeinsame Montagehöhe für den Winkel.')
            return
        for x, y, sx, sy in candidates:
            footprint = [(x, y), (x+sx*size, y), (x+sx*size, y+sy*size), (x, y+sy*size)]
            # Use disjoint equal-width slots: two 40-mm brackets fit an 80-mm face.
            positions = [bottom+height*(i+0.5)/count-size/2 for i in range(count)]
            prisms = [(footprint, z, z+size) for z in positions]
            if any(overlaps(prism, obstacle) for prism in prisms for obstacle in obstacles+accepted):
                continue
            for index, (footprint, z, _) in enumerate(prisms, 1):
                low = [min(p[i] for p in footprint) for i in (0, 1)]
                result.append(dict(key=f'connection:{key}:{index}', label=label, size=size,
                    origin=[x, y, z], bounds_origin=[*low, z], bounds=[size, size, size],
                    orientation=([[sx, 0, 0], [0, sy, 0], [0, 0, 1]] if sx*sy > 0
                                 else [[0, sy, 0], [sx, 0, 0], [0, 0, 1]]),
                    points=[[0, 0], [size, 0], [size, size], [0, size]],
                    members=[first['key'], second['key']], parallel_count=count))
            accepted.extend(prisms)
            return
        warnings.append(f'{label}: Montageraum belegt; Winkel nicht platziert.')

    levels = sorted({p['group_id'] for p in parts if ':beam:' in p['key']})
    for level in levels:
        front, back, left, right = [by_key[f'{level}:beam:{side}']
                                    for side in ('front', 'back', 'left', 'right')]
        lx = left['bounds_origin_mm'][0]+left['bounds_mm'][0]
        rx = right['bounds_origin_mm'][0]
        fy = front['bounds_origin_mm'][1]+front['bounds_mm'][1]
        by = back['bounds_origin_mm'][1]
        for xs, ys in product(('left', 'right'), ('front', 'back')):
            a = left if xs == 'left' else right
            b = front if ys == 'front' else back
            joint(f'{level}:{ys}:{xs}', f'{level} Ecke {ys}/{xs}', a, b,
                  [(lx if xs == 'left' else rx, fy if ys == 'front' else by,
                    1 if xs == 'left' else -1, 1 if ys == 'front' else -1)])
        for cross in (p for p in parts if p['group_id'] == level and ':cross:' in p['key']):
            x, y, _ = cross['bounds_origin_mm']
            w, d, _ = cross['bounds_mm']
            along_y = cross['orientation'][2][1] == 1
            for end in ('start', 'end'):
                if along_y:
                    beam = front if end == 'start' else back
                    cy, sy = (y, 1) if end == 'start' else (y+d, -1)
                    candidates = [(x, cy, -1, sy), (x+w, cy, 1, sy)]
                else:
                    beam = left if end == 'start' else right
                    cx, sx = (x, 1) if end == 'start' else (x+w, -1)
                    candidates = [(cx, y, sx, -1), (cx, y+d, sx, 1)]
                joint(f'{cross["key"]}:{end}', f'{cross["function"]} {end}', cross, beam, candidates)
    return result, warnings
