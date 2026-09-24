"""FrameKit integration demo: one native Fusion command with three tabs."""
import html
from pathlib import Path
import adsk.core
import adsk.fusion
from ... import accessories, config, demo, settings
from ...geometry import create_frame
from ...model import build_model
from ...preview import Preview
from ...version import __version__
from ...lib import fusionAddInUtils as futil

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_CreateFrame'
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'
RESOURCES = Path(__file__).resolve().parents[2] / 'resources'
_handlers = []
_dialog_handlers = []
_previews = []


def start():
    ui = adsk.core.Application.get().userInterface
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID) if workspace else None
    if panel is None:
        raise RuntimeError('Fusion-Bereich Volumenkörper / Erstellen nicht gefunden.')
    stop()
    definition = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, f'FrameKit {__version__}', 'Ein einfaches Demo-Gestell erstellen.',
        str(RESOURCES / 'CreateFrame'))
    futil.add_handler(definition.commandCreated, command_created, local_handlers=_handlers)
    control = panel.controls.addCommand(definition)
    control.isPromotedByDefault = True
    control.isPromoted = True


def stop():
    for preview in list(_previews):
        preview.clear()
    _previews.clear()
    ui = adsk.core.Application.get().userInterface
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID) if workspace else None
    control = panel.controls.itemById(CMD_ID) if panel else None
    if control:
        control.deleteMe()
    definition = ui.commandDefinitions.itemById(CMD_ID)
    if definition:
        definition.deleteMe()
    _handlers.clear()
    _dialog_handlers.clear()


def command_created(args):
    app = adsk.core.Application.get()
    command = args.command
    command.setDialogInitialSize(580, 800)
    command.okButtonText = 'Ausführen'
    inputs = command.commandInputs
    values, warning = settings.load()
    library, library_warning = settings.load_library()
    frame = inputs.addTabCommandInput('frame_tab', 'Frame erstellen', str(RESOURCES / 'CreateFrame'))
    frame_inputs = frame.children
    frame_inputs.addTextBoxCommandInput('intro', '',
        '<b>FrameKit Demo</b><br>Einfaches Gestell aus massiven Rechteckprofilen. '
        'Keine Nutgeometrie, Verbinder oder Tragfähigkeitsberechnung.', 3, True)
    fields = {}
    for key, label in (('length', 'Länge'), ('width', 'Breite'),
                       ('height', 'Gesamthöhe'), ('profile', 'Profilbreite')):
        fields[key] = frame_inputs.addValueInput(key, label, 'mm',
            adsk.core.ValueInput.createByString(f'{values[key]} mm'))
    bottom = frame_inputs.addBoolValueInput('bottom', 'Unterer Rahmen', True, '', values['bottom'])
    support_choice = frame_inputs.addDropDownCommandInput(
        'support_choice', 'Füße / Rollen', adsk.core.DropDownStyles.TextListDropDownStyle)
    frame_inputs.addTextBoxCommandInput('support_help', '',
        'Vier gleiche Zylinderplatzhalter unter den Eckpfosten. Gesamthöhe und '
        'Bodenhöhen gelten ab Aufstandsfläche, inklusive Füßen/Rollen. '
        'Eigene Varianten unter „Einstellungen verwalten“ anlegen.', 3, True)
    shelves = frame_inputs.addGroupCommandInput('shelves', 'Bodenplatten und Zwischenböden')
    shelves.isExpanded = True
    shelf_inputs = shelves.children
    count = shelf_inputs.addIntegerSpinnerCommandInput(
        'shelf_count', 'Anzahl Zwischenböden', 0, demo.MAX_SHELVES, 1, values['shelf_count'])
    thickness = shelf_inputs.addValueInput('shelf_thickness', 'Plattenstärke', 'mm',
        adsk.core.ValueInput.createByString(f'{values["shelf_thickness"]} mm'))
    shelf_inputs.addTextBoxCommandInput('shelf_help', '',
        'Höhe = Oberkante Boden ab Aufstandsfläche. Von unten nach oben angeben. '
        'Leer = automatisch gleichmäßige freie Abstände. Eingaben in mm, z. B. 250 oder 25 cm. '
        'Auf jedem Rahmen liegt eine Platte mit Aussparungen für die Pfosten. '
        'Gesamthöhe inklusive oberer Platte.', 5, True)
    height_fields = []
    for index in range(demo.MAX_SHELVES):
        saved = values['shelf_heights'][index] if index < count.value else None
        field = shelf_inputs.addStringValueInput(f'shelf_height_{index}',
            f'Boden {index + 1:02d} Höhe', '' if saved is None else f'{saved:g} mm')
        field.isVisible = index < count.value
        height_fields.append(field)
    resolved = shelf_inputs.addTextBoxCommandInput('shelf_resolved', '', '', 3, True)
    create = frame_inputs.addBoolValueInput('create_geometry', 'Demo-Gestell erstellen', True, '', True)
    preview_inputs = frame_inputs.addGroupCommandInput('preview_options', 'Vorschau').children
    show_preview = preview_inputs.addBoolValueInput('show_preview', 'Vorschau anzeigen', True, '', False)
    show_panels = preview_inputs.addBoolValueInput('preview_panels', 'Bodenflächen anzeigen', True, '', True)
    show_accessories = preview_inputs.addBoolValueInput('preview_accessories', 'Zubehörumrisse anzeigen', True, '', True)
    show_panels.isEnabled = show_accessories.isEnabled = False
    preview_inputs.addTextBoxCommandInput('preview_help', '',
        'Blau: Profilmittellinien bis zur Schnittfläche. Orange: Zubehörplatzhalter.<br>'
        'X: links → rechts, Y: vorne → hinten, Z: nach oben. Ursprung: vorne links '
        'am Rahmen auf Höhe der Aufstandsfläche.<br>'
        'Die fixierte Layoutskizze wird beim Erstellen gespeichert und ausgeblendet. '
        'Maßgeblich bleiben die Dialogwerte.', 5, True)
    preview_status = preview_inputs.addTextBoxCommandInput('preview_status', '', '', 2, True)
    error = frame_inputs.addTextBoxCommandInput('validation', '', '', 2, True)

    manage = inputs.addTabCommandInput('settings_tab', 'Einstellungen verwalten',
                                       str(RESOURCES / 'ProfileLibrary')).children
    manage.addTextBoxCommandInput('settings_help', '',
        'Die Werte aus „Frame erstellen“ können als persönliche Standardwerte gespeichert werden. '
        'Zum reinen Speichern „Demo-Gestell erstellen“ abwählen. '
        'Erst „Ausführen“ speichert Standardwerte; „Abbrechen“ verwirft deren Änderungen. '
        'Die Platzhalterbibliothek wird über eigene Schaltflächen sofort gespeichert.', 5, True)
    persist = manage.addBoolValueInput('save_defaults', 'Als Standardwerte speichern', True, '', False)
    reset = manage.addBoolValueInput('reset_defaults', 'Werkseinstellungen laden', False, '', False)
    manage.addTextBoxCommandInput('settings_path', 'Datei', html.escape(str(settings.settings_path())), 3, True)
    manage.addTextBoxCommandInput('settings_status', '', html.escape(warning), 2, True)
    library_group = manage.addGroupCommandInput('support_library', 'Eigene Füße und Rollen')
    library_group.isExpanded = True
    lib_inputs = library_group.children
    library_choice = lib_inputs.addDropDownCommandInput(
        'library_choice', 'Gespeicherte Einträge', adsk.core.DropDownStyles.TextListDropDownStyle)
    delete_entry = lib_inputs.addBoolValueInput('delete_support', 'Ausgewählten Eintrag löschen', False, '', False)
    lib_inputs.addTextBoxCommandInput('library_help', '',
        'Neue Platzhalter anlegen: Name, Art, Höhe und Durchmesser eingeben. '
        'Speichern und Löschen wirken sofort, auch wenn der Dialog danach abgebrochen wird. '
        'Bestehende Baugruppen bleiben unverändert.', 4, True)
    new_name = lib_inputs.addStringValueInput('support_name', 'Name', '')
    new_kind = lib_inputs.addDropDownCommandInput(
        'support_kind', 'Art', adsk.core.DropDownStyles.TextListDropDownStyle)
    for index, kind in enumerate(accessories.KINDS):
        new_kind.listItems.add(kind, index == 0)
    # Text fields keep unfinished library entries from blocking frame creation.
    new_height = lib_inputs.addStringValueInput('support_height', 'Höhe (mm)', '100')
    new_diameter = lib_inputs.addStringValueInput('support_diameter', 'Durchmesser (mm)', '75')
    save_entry = lib_inputs.addBoolValueInput('save_support', 'Neuen Eintrag speichern', False, '', False)
    library_status = lib_inputs.addTextBoxCommandInput('library_status', '', html.escape(library_warning), 3, True)
    lib_inputs.addTextBoxCommandInput('library_path', 'Bibliotheksdatei',
        html.escape(str(settings.library_path())), 3, True)

    def selected_support():
        selected = support_choice.selectedItem
        return library[selected.index - 1] if selected and selected.index > 0 else None

    def refresh_library(selected_id=None, listed_id=None):
        support_choice.listItems.clear()
        support_choice.listItems.add('Keine Füße / Rollen', True)
        library_choice.listItems.clear()
        for index, spec in enumerate(library):
            support_choice.listItems.add(accessories.label(spec), spec['id'] == selected_id)
            library_choice.listItems.add(accessories.label(spec),
                spec['id'] == listed_id if listed_id else index == 0)
        if not library:
            library_choice.listItems.add('Keine gespeicherten Einträge', True)
        delete_entry.isEnabled = bool(library)

    saved_support = values.get('accessory')
    saved_id = saved_support['id'] if saved_support else None
    refresh_library(saved_id)
    if saved_id and not any(spec['id'] == saved_id for spec in library):
        library_status.text = (library_warning + '\n' if library_warning else '') + (
            'Der gespeicherte Platzhalter ist nicht mehr verfügbar. Auswahl auf „Keine“ gesetzt.')

    info = inputs.addTabCommandInput('info_tab', 'info').children
    def info_text(identifier, text, rows):
        control = info.addTextBoxCommandInput(identifier, '', text, rows, True)
        control.isFullWidth = True
        return control

    info_text('about_title', f'FrameKit {__version__}', 1)
    logo = info.addImageCommandInput('about_logo', '', str(RESOURCES / 'FrameKit-Logo-240.png'))
    logo.isFullWidth = True
    info_text('about_description',
        'FrameKit von Know-How-Schmiede erstellt Gestelle in Autodesk Fusion.<br>'
        'Diese Integrationsdemo erzeugt einfache Rahmen aus Rechteckprofilen.', 3)
    info_text('about_homepage',
        'Tutorials zu Fusion und weitere Plugins für Fusion finden Sie auf der '
        f'<a href="{config.HOMEPAGE_URL}">Homepage der Know-How-Schmiede</a>.<br>', 3)
    info_text('about_source',
        f'Der Quellcode kann im <a href="{config.PROJECT_URL}">GitHub-Repository</a> '
        'eingesehen werden.<br>', 2)
    info_text('about_releases',
        f'Updates finden Sie unter <a href="{config.PROJECT_URL}/releases">'
        'Releases im GitHub-Repository</a>.<br>', 2)
    info_text('about_issues',
        f'Fehler gefunden? Bitte unter <a href="{config.PROJECT_URL}/issues">'
        'Issues im Repository</a> melden – mit Add-in-Version und Schritten zum Nachstellen.<br>', 3)
    info_text('about_youtube',
        'Gefällt Ihnen das Plugin? Dann lassen Sie gerne ein kostenloses YouTube-Abo bei '
        f'<a href="{config.YOUTUBE_URL}">@knowhowschmiede</a> da.<br>', 3)
    info_text('about_credits', f'{html.escape(config.AUTHOR)} · MIT-Lizenz', 1)

    handlers = []
    _dialog_handlers.append(handlers)
    preview = Preview()
    _previews.append(preview)
    calculated_model = None

    def current_model(current):
        nonlocal calculated_model
        if calculated_model is None or calculated_model['configuration'] != current:
            calculated_model = build_model(current, calculated_model)
        return calculated_model

    def read_values():
        if any(not field.isValidExpression for field in fields.values()):
            raise ValueError('Bitte gültige Längen eingeben.')
        result = {key: field.value * 10 for key, field in fields.items()}
        result['bottom'] = bottom.value
        selected = selected_support()
        result['accessory'] = selected.copy() if selected else None
        result['shelf_count'] = count.value
        if not thickness.isValidExpression:
            raise ValueError('Bitte eine gültige Plattenstärke eingeben.')
        result['shelf_thickness'] = thickness.value * 10
        result['shelf_heights'] = []
        units = app.activeProduct.unitsManager if app.activeProduct else None
        for index, field in enumerate(height_fields[:count.value]):
            expression = field.value.strip()
            if not expression:
                result['shelf_heights'].append(None)
            elif units and units.isValidExpression(expression, 'mm'):
                result['shelf_heights'].append(units.evaluateExpression(expression, 'mm') * 10)
            else:
                raise ValueError(f'Boden {index + 1}: gültige Höhe eingeben oder Feld leer lassen.')
        demo.validate(result)
        return result

    def validation_message():
        try:
            current = read_values()
            heights = demo.shelf_heights(current)
            resolved.text = ('Oberkanten: ' + '; '.join(
                f'{index:02d}: {height:.1f} mm' for index, height in enumerate(heights, 1))) if heights else ''
            if create.value and not adsk.fusion.Design.cast(app.activeProduct):
                return 'Zum Erstellen bitte ein Fusion-Konstruktionsdokument öffnen.'
            return ''
        except ValueError as exc:
            resolved.text = ''
            return str(exc)

    def validate(event):
        message = validation_message()
        error.text = message
        if message:
            preview.clear()
        event.areInputsValid = not bool(message)

    updating = False

    def library_number(field):
        expression = field.value.strip()
        units = app.activeProduct.unitsManager if app.activeProduct else None
        if units and units.isValidExpression(expression, 'mm'):
            return units.evaluateExpression(expression, 'mm') * 10
        if not units:
            try:
                return float(expression.replace(',', '.'))
            except ValueError:
                pass
        raise ValueError(f'{field.name}: gültige Länge eingeben (z. B. 100 mm).')

    def changed(event):
        nonlocal updating, library
        if updating:
            return
        preview.clear()
        preview_status.text = ''
        if event.input.id in (save_entry.id, delete_entry.id) and event.input.value:
            updating = True
            try:
                selected = selected_support()
                selected_id = selected['id'] if selected else None
                if event.input.id == save_entry.id:
                    spec = accessories.new_spec(new_name.value, new_kind.selectedItem.name,
                        library_number(new_height), library_number(new_diameter))
                    revised = library + [spec]
                    settings.save_library(revised)
                    library = revised
                    refresh_library(selected_id, spec['id'])
                    library_status.text = f'Gespeichert: {accessories.label(spec)}'
                    new_name.value = ''
                elif library_choice.selectedItem and library:
                    removed = library[library_choice.selectedItem.index]
                    revised = [spec for spec in library if spec['id'] != removed['id']]
                    settings.save_library(revised)
                    library = revised
                    refresh_library(selected_id)
                    library_status.text = f'Gelöscht: {removed["name"]}'
            except (ValueError, OSError) as exc:
                library_status.text = f'Nicht gespeichert: {exc}'
            finally:
                event.input.value = False
                updating = False
        if event.input.id == reset.id and reset.value:
            support_choice.listItems.item(0).isSelected = True
            for key, field in fields.items():
                field.expression = f'{demo.DEFAULTS[key]} mm'
            bottom.value = demo.DEFAULTS['bottom']
            count.value = demo.DEFAULTS['shelf_count']
            thickness.expression = f'{demo.DEFAULTS["shelf_thickness"]} mm'
            for field in height_fields:
                field.value = ''
            reset.value = False
        for index, field in enumerate(height_fields):
            field.isVisible = index < count.value
        error.text = validation_message()
        show_preview.isEnabled = create.value
        show_panels.isEnabled = show_accessories.isEnabled = create.value and show_preview.value

    def execute_preview(event):
        # Graphics are not a completed command result: OK must always run execute.
        event.isValidResult = False
        try:
            preview.clear()
            if not create.value or not show_preview.value:
                return
            current = read_values()
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                return
            preview.show(design, current_model(current), show_panels.value, show_accessories.value)
            preview_status.text = ''
            app.activeViewport.refresh()
        except Exception as exc:
            preview.clear()
            preview_status.text = f'Vorschau nicht verfügbar: {exc}'
            futil.handle_error('FrameKit-Vorschau', show_message_box=False)

    def execute(event):
        try:
            preview.clear()
            current = read_values()
            if create.value:
                design = adsk.fusion.Design.cast(app.activeProduct)
                if not design:
                    raise ValueError('Bitte ein Fusion-Konstruktionsdokument öffnen.')
                create_frame(design, current, current_model(current))
                app.activeViewport.fit()
            if persist.value:
                settings.save(current)
        except Exception as exc:
            event.executeFailed = True
            event.executeFailedMessage = f'FrameKit: {exc}'
            futil.handle_error('FrameKit ausführen')

    def destroy(event):
        preview.clear()
        if preview in _previews:
            _previews.remove(preview)
        if handlers in _dialog_handlers:
            _dialog_handlers.remove(handlers)
        handlers.clear()

    for event, callback in ((command.execute, execute), (command.executePreview, execute_preview),
                            (command.inputChanged, changed),
                            (command.validateInputs, validate), (command.destroy, destroy)):
        futil.add_handler(event, callback, local_handlers=handlers)
    error.text = validation_message()
