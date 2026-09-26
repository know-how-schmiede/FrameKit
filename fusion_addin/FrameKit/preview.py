"""Transient Fusion graphics owned by a single FrameKit command dialog."""
import adsk.core
import adsk.fusion
from .preview_data import display_geometry


class Preview:
    def __init__(self):
        self.group = None

    def clear(self):
        # Fusion may already have discarded graphics when rolling back a preview.
        if self.group is not None:
            if self.group.isValid:
                if not self.group.deleteMe():
                    raise RuntimeError('FrameKit-Vorschau konnte nicht entfernt werden.')
            self.group = None

    def show(self, design, model, show_panels=True, show_accessories=True):
        self.clear()
        data = display_geometry(model, show_panels, show_accessories)
        try:
            self.group = design.rootComponent.customGraphicsGroups.add()
            self.group.name = 'FrameKit | Vorschau'
            self.group.isSelectable = False
            self.group.isChildrenSelectable = False
            for kind, rgb in (('profiles', (30, 130, 215)), ('panels', (110, 170, 190)),
                              ('accessories', (220, 140, 40)), ('connections', (160, 80, 190))):
                if not data[kind]:
                    continue
                coordinates = adsk.fusion.CustomGraphicsCoordinates.create(
                    [value / 10 for point in data[kind] for value in point])
                if kind == 'panels':
                    entity = self.group.addMesh(coordinates, [], [], [])
                    entity.setOpacity(0.25, True)
                else:
                    entity = self.group.addLines(coordinates, [], False)
                    entity.weight = 3 if kind == 'profiles' else 1.5
                entity.isSelectable = False
                entity.color = adsk.fusion.CustomGraphicsSolidColorEffect.create(
                    adsk.core.Color.create(*rgb, 255))
        except Exception:
            self.clear()
            raise
