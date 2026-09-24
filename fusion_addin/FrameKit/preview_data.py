"""Display geometry derived from the assembly model, in millimeters."""
from math import cos, sin, tau


def world_point(part, point):
    return [part['position_mm'][i] + sum(
        part['orientation'][j][i] * point[j] for j in range(3)) for i in range(3)]


def display_geometry(model, show_panels=True, show_accessories=True):
    """Return independent line segments and triangle lists; never change the model.

    Current notched rectangular panels are star-shaped about their center, so a
    triangle fan retains all four corner cutouts. This is not a general DXF mesher.
    """
    profiles, panels, accessories = [], [], []
    for part in model['parts']:
        shape = part['geometry']
        if part['kind'] == 'profile':
            profiles.extend([list(point) for point in part['centerline_mm']])
        elif part['kind'] == 'panel' and show_panels:
            outline = shape['points_mm']
            center = [sum(p[i] for p in outline) / len(outline) for i in range(2)]
            for index, point in enumerate(outline):
                for xy in (center, point, outline[(index + 1) % len(outline)]):
                    panels.append(world_point(part, [*xy, shape['depth_mm']]))
        elif part['kind'] == 'support' and show_accessories:
            cx, cy = shape['center_mm']
            radius, height = shape['radius_mm'], shape['depth_mm']
            ring = [(cx + radius*cos(tau*i/32), cy + radius*sin(tau*i/32)) for i in range(32)]
            for z in (0, height):
                for index, xy in enumerate(ring):
                    for point in (xy, ring[(index+1) % len(ring)]):
                        accessories.append(world_point(part, [*point, z]))
            for xy in ring[::8]:
                accessories.extend(world_point(part, [*xy, z]) for z in (0, height))
    return dict(profiles=profiles, panels=panels, accessories=accessories)
