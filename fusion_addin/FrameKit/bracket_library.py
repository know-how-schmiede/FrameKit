"""Bundled STEP solids, imported once outside command transactions."""
from pathlib import Path

SIZES = (20, 30, 40)
DIRECTORY = Path(__file__).resolve().parent / 'resources' / 'brackets'
_bodies = {}
_errors = {}


def filename(size):
    if size not in SIZES:
        raise ValueError(f'Unbekannte Winkelgröße: {size}')
    return f'Winkel_{size}x{size}.step'


def prepare(app):
    """Called during add-in startup, never from a command event.

    Only our temporary import documents are closed. Independent transient copies
    survive closing them. No source document or user design is modified.
    """
    import adsk.core
    import adsk.fusion
    _bodies.clear()
    _errors.clear()
    previous = app.activeDocument
    manager = adsk.fusion.TemporaryBRepManager.get()
    try:
        for size in SIZES:
            document = None
            try:
                options = app.importManager.createSTEPImportOptions(str(DIRECTORY / filename(size)))
                document = app.importManager.importToNewDocument(options)
                if document is None:
                    raise ValueError('STEP-Import fehlgeschlagen.')
                design = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
                bodies = list(design.rootComponent.bRepBodies)
                for occurrence in design.rootComponent.allOccurrences:
                    bodies.extend(occurrence.bRepBodies)
                if len(bodies) != 1 or not bodies[0].isSolid:
                    raise ValueError('Genau ein geschlossener Winkelkörper erwartet.')
                body = manager.copy(bodies[0])
                if body is None:
                    raise ValueError('Winkelkörper konnte nicht kopiert werden.')
                box = body.boundingBox
                for low, high in zip(box.minPoint.asArray(), box.maxPoint.asArray()):
                    if abs(low) > 1e-4 or abs(high-size/10) > 1e-4:
                        raise ValueError('STEP-Außenmaße oder Ursprung passen nicht zur Winkeldefinition.')
                # Supplied files: mounting planes X=0 and Z=0; width along Y.
                # Normalize to mounting planes X=0, Y=0 and width along +Z.
                transform = adsk.core.Matrix3D.create()
                transform.setWithCoordinateSystem(
                    adsk.core.Point3D.create(0, 0, size/10),
                    adsk.core.Vector3D.create(1, 0, 0),
                    adsk.core.Vector3D.create(0, 0, -1),
                    adsk.core.Vector3D.create(0, 1, 0))
                if not manager.transform(body, transform):
                    raise ValueError('Winkelausrichtung fehlgeschlagen.')
                _bodies[size] = body
            except Exception as error:
                _errors[size] = str(error)
            finally:
                if document is not None:
                    document.close(False)
    finally:
        if previous is not None:
            previous.activate()


def body(size):
    if size not in _bodies:
        detail = _errors.get(size, 'Winkelbibliothek wurde noch nicht geladen.')
        raise ValueError(f'{filename(size)}: {detail} FrameKit nach Korrektur neu starten.')
    return _bodies[size]
