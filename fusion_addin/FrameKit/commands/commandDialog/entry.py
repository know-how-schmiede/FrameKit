"""FrameKit integration demo: one native Fusion command with three tabs."""
import html
from copy import deepcopy
from pathlib import Path
import adsk.core
import adsk.fusion
from ... import accessories, config, demo, settings, profile_library
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
        CMD_ID, f'FrameKit {__version__}', 'Ein Gestell aus Demo- oder DXF-Profilen erstellen.',
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
    profiles, profiles_warning = profile_library.load()
    frame = inputs.addTabCommandInput('frame_tab', 'Frame erstellen', str(RESOURCES / 'CreateFrame'))
    frame_inputs = frame.children
    frame_inputs.addTextBoxCommandInput('intro', '',
        '<b>FrameKit</b><br>Gestell aus Demo-Vollprofilen oder eigenen DXF-Profilen. '
        'Keine Verbinder oder Tragfähigkeitsberechnung.', 3, True)
    fields = {}
    for key, label in (('length', 'Länge'), ('width', 'Breite'),
                       ('height', 'Gesamthöhe'), ('profile', 'Demo-Profilbreite')):
        fields[key] = frame_inputs.addValueInput(key, label, 'mm',
            adsk.core.ValueInput.createByString(f'{values[key]} mm'))
    profile_choice = frame_inputs.addDropDownCommandInput(
        'profile_choice', 'Profil für das gesamte Gestell', adsk.core.DropDownStyles.TextListDropDownStyle)
    profile_dimensions = frame_inputs.addTextBoxCommandInput('profile_dimensions', '', '', 2, True)
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
    def dropdown(parent, identifier, label, choices, selected):
        control = parent.addDropDownCommandInput(
            identifier, label, adsk.core.DropDownStyles.TextListDropDownStyle)
        for index, text in enumerate(choices):
            control.listItems.add(text, index == selected)
        return control

    mount = dropdown(shelf_inputs, 'top_panel_mount', 'Deckplatte',
        ['Zwischen Pfosten (mit Aussparungen)', 'Auf Profilen (ohne Aussparungen)'],
        int(values.get('top_panel_mount', 'notched') == 'on_top'))
    shelf_inputs.addTextBoxCommandInput('shelf_help', '',
        'Höhe = Oberkante Boden ab Aufstandsfläche. Von unten nach oben angeben. '
        'Leer = automatisch gleichmäßige freie Abstände. Eingaben in mm, z. B. 250 oder 25 cm. '
        'Untere Platten haben Aussparungen für die Pfosten. Bei Deckplatte auf Profilen '
        'enden die Pfosten unter der Platte. '
        'Gesamthöhe inklusive oberer Platte.', 5, True)
    height_fields = []
    for index in range(demo.MAX_SHELVES):
        saved = values['shelf_heights'][index] if index < count.value else None
        field = shelf_inputs.addStringValueInput(f'shelf_height_{index}',
            f'Boden {index + 1:02d} Höhe', '' if saved is None else f'{saved:g} mm')
        field.isVisible = index < count.value
        height_fields.append(field)
    resolved = shelf_inputs.addTextBoxCommandInput('shelf_resolved', '', '', 3, True)
    cross_group = frame_inputs.addGroupCommandInput('cross_members', 'Querträger je Ebene')
    cross_inputs = cross_group.children
    cross_inputs.addTextBoxCommandInput('cross_help', '',
        '0 = keine Träger. Quer: vorne–hinten (Y), Längs: links–rechts (X). '
        'Gleich große freie Felder; Oberkanten bündig mit dem Rahmen.', 3, True)
    all_count = dropdown(cross_inputs, 'cross_all_count', 'Anzahl für alle Ebenen',
                         [str(i) for i in range(6)], 0)
    all_direction = dropdown(cross_inputs, 'cross_all_direction', 'Ausrichtung für alle Ebenen',
                             ['Quer', 'Längs'], 0)
    apply_all = cross_inputs.addBoolValueInput(
        'cross_apply_all', 'Für alle Ebenen übernehmen', False, '', False)
    cross_fields = {}
    for key, label in demo.frame_levels(dict(bottom=True, shelf_count=demo.MAX_SHELVES)):
        saved = values.get('cross_members', {}).get(key, {'count': 0, 'direction': 'quer'})
        identifier = key.replace(':', '_')
        number = dropdown(cross_inputs, f'cross_{identifier}_count', f'{label}: Anzahl',
                          [str(i) for i in range(6)], saved['count'])
        direction = dropdown(cross_inputs, f'cross_{identifier}_direction', f'{label}: Ausrichtung',
                             ['Quer', 'Längs'], int(saved['direction'] == 'laengs'))
        number.isVisible = direction.isVisible = key in dict(demo.frame_levels(values))
        cross_fields[key] = (number, direction)
    create = frame_inputs.addBoolValueInput('create_geometry', 'Gestell erstellen', True, '', True)
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
        'Zum reinen Speichern „Gestell erstellen“ abwählen. '
        'Erst „Ausführen“ speichert Standardwerte; „Abbrechen“ verwirft deren Änderungen. '
        'Die Bibliotheken werden über eigene Schaltflächen sofort gespeichert.', 5, True)
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

    profile_group = manage.addGroupCommandInput('profile_library', 'Eigene DXF-Profile')
    profile_group.isExpanded = True
    profile_inputs = profile_group.children
    profile_inputs.addTextBoxCommandInput('profile_help', '',
        'Quadratischer Querschnitt in XY, Mittelpunkt im Ursprung. '
        'LINE, ARC, CIRCLE und 2D-(LW)POLYLINE; Blöcke vorher auflösen. '
        'Punkte und markierte Hilfsgeometrie werden ausgelassen. '
        'DXF wählen, erkannte Maße prüfen und Profil speichern. '
        'Speichern/Löschen wirken sofort, auch bei Abbrechen; bestehende Gestelle bleiben erhalten.', 5, True)
    profile_list = dropdown(profile_inputs, 'profile_list', 'Gespeicherte Profile', [], 0)
    delete_profile = profile_inputs.addBoolValueInput(
        'delete_profile', 'Ausgewähltes Profil löschen', False, '', False)
    profile_name = profile_inputs.addStringValueInput('profile_name', 'Profilname', '')
    profile_unit = dropdown(profile_inputs, 'profile_unit', 'DXF-Einheit',
                            ['Aus DXF', 'mm', 'cm', 'm', 'in', 'ft'], 0)
    choose_profile = profile_inputs.addBoolValueInput(
        'choose_profile', 'Lokale DXF auswählen und prüfen', False, '', False)
    profile_detected = profile_inputs.addTextBoxCommandInput('profile_detected', '', '', 3, True)
    profile_confirm = profile_inputs.addBoolValueInput(
        'profile_confirm', 'Erkannte Profilmaße sind korrekt', True, '', False)
    metadata_fields = {}
    for key, label in (('manufacturer', 'Hersteller'), ('series', 'Serie'),
                       ('article_number', 'Artikelnummer'), ('slot_size', 'Nutgröße'),
                       ('material', 'Material')):
        metadata_fields[key] = profile_inputs.addStringValueInput('profile_'+key, label+' (optional)', '')
    save_profile = profile_inputs.addBoolValueInput(
        'save_profile', 'Geprüftes Profil speichern', False, '', False)
    save_profile.isEnabled = False
    profile_status = profile_inputs.addTextBoxCommandInput('profile_status', '', html.escape(profiles_warning), 3, True)
    profile_inputs.addTextBoxCommandInput('profile_path', 'Bibliotheksordner',
        html.escape(str(profile_library.directory())), 3, True)
    pending_profile = None
    selectable_profiles = []

    def selected_profile():
        item = profile_choice.selectedItem
        return selectable_profiles[item.index-1] if item and item.index > 0 else None

    def refresh_profiles(selected_id=None, listed_id=None, saved=None):
        nonlocal selectable_profiles
        selectable_profiles = list(profiles)
        if saved and not any(spec['id'] == saved['id'] for spec in profiles):
            selectable_profiles.append(saved)
        profile_choice.listItems.clear()
        profile_choice.listItems.add('Demo-Vollprofil (einstellbare Breite)', True)
        profile_list.listItems.clear()
        for spec in selectable_profiles:
            suffix = ' (nicht in Bibliothek verfügbar)' if spec not in profiles else ''
            profile_choice.listItems.add(profile_library.label(spec)+suffix, spec['id'] == selected_id)
        for index, spec in enumerate(profiles):
            profile_list.listItems.add(profile_library.label(spec),
                spec['id'] == listed_id if listed_id else index == 0)
        if not profiles:
            profile_list.listItems.add('Keine gespeicherten Profile', True)
        delete_profile.isEnabled = bool(profiles)
        update_profile_display()

    def update_profile_display():
        spec = selected_profile()
        fields['profile'].isVisible = fields['profile'].isEnabled = spec is None
        profile_dimensions.text = (html.escape(profile_library.label(spec)) if spec else '')

    saved_profile = values.get('profile_definition')
    refresh_profiles(saved_profile['id'] if saved_profile else None, saved=saved_profile)

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
        'Erstellt Rahmen aus Demo-Vollprofilen oder eigenen DXF-Profilquerschnitten.', 3)
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
        definition = selected_profile()
        if any(not field.isValidExpression for key, field in fields.items()
               if key != 'profile' or definition is None):
            raise ValueError('Bitte gültige Längen eingeben.')
        result = {key: field.value * 10 for key, field in fields.items()
                  if key != 'profile' or definition is None}
        result['profile_definition'] = deepcopy(definition)
        if definition is not None:
            if not any(spec['id'] == definition['id'] for spec in profiles):
                raise ValueError('Gespeichertes Profil fehlt in der Bibliothek. Neu importieren oder anderes Profil wählen.')
            profile_library.verify_source(definition)
            result['profile'] = definition['width_mm']
        result['bottom'] = bottom.value
        selected = selected_support()
        result['accessory'] = selected.copy() if selected else None
        result['shelf_count'] = count.value
        result['top_panel_mount'] = 'on_top' if mount.selectedItem.index else 'notched'
        result['cross_members'] = {
            key: dict(count=cross_fields[key][0].selectedItem.index,
                      direction='laengs' if cross_fields[key][1].selectedItem.index else 'quer')
            for key, _ in demo.frame_levels(result)}
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
        nonlocal updating, library, profiles, pending_profile
        if updating:
            return
        preview.clear()
        preview_status.text = ''
        if event.input.id == profile_unit.id:
            pending_profile = None
            profile_confirm.value = False
            profile_detected.text = 'Einheit geändert: DXF erneut auswählen und prüfen.'
        if event.input.id in (choose_profile.id, save_profile.id, delete_profile.id) and event.input.value:
            updating = True
            try:
                selected = selected_profile()
                selected_id = selected['id'] if selected else None
                if event.input.id == choose_profile.id:
                    dialog = app.userInterface.createFileDialog()
                    dialog.title = 'Profilquerschnitt auswählen'
                    dialog.filter = 'DXF-Dateien (*.dxf)'
                    dialog.isMultiSelectEnabled = False
                    if dialog.showOpen() == adsk.core.DialogResults.DialogOK:
                        pending_profile = None
                        profile_confirm.value = False
                        profile_detected.text = ''
                        unit = ('auto', 'mm', 'cm', 'm', 'in', 'ft')[profile_unit.selectedItem.index]
                        name = profile_name.value.strip() or Path(dialog.filename).stem
                        candidate = profile_library.prepare(dialog.filename, name, unit)
                        design = adsk.fusion.Design.cast(app.activeProduct)
                        if not design:
                            raise ValueError('Zur DXF-Prüfung bitte ein Fusion-Konstruktionsdokument öffnen.')
                        from ...profile_geometry import validate_in_fusion
                        validate_in_fusion(design, candidate[0])
                        pending_profile = candidate
                        spec = candidate[0]
                        profile_name.value = spec['name']
                        profile_detected.text = html.escape(
                            f'{spec["source_name"]}: {spec["width_mm"]:g} × {spec["height_mm"]:g} mm; '
                            f'{spec["loop_count"]-1} Hohlräume; Einheit {spec["source_unit"]}. '
                            'Maße prüfen und bestätigen.')
                        profile_status.text = 'Konturen und Probeextrusion erfolgreich geprüft.'
                        ignored = spec.get('ignored_entities', {})
                        if any(ignored.values()):
                            profile_status.text += (
                                f' Ausgelassen: {ignored.get("points", 0)} Punkte, '
                                f'{ignored.get("construction", 0)} Hilfselemente. '
                                'Kontur und Hohlräume kontrollieren.')
                elif event.input.id == save_profile.id:
                    if pending_profile is None or not profile_confirm.value:
                        raise ValueError('Zuerst DXF prüfen und erkannte Maße bestätigen.')
                    spec, data = pending_profile
                    spec = deepcopy(spec)
                    spec['name'] = profile_name.value.strip()
                    for key, field in metadata_fields.items():
                        spec[key] = field.value.strip()
                    profiles = profile_library.add(spec, data)
                    refresh_profiles(spec['id'], spec['id'])
                    pending_profile = None
                    profile_confirm.value = False
                    profile_detected.text = ''
                    profile_status.text = 'Gespeichert und ausgewählt: '+html.escape(profile_library.label(spec))
                elif profiles and profile_list.selectedItem:
                    removed = profiles[profile_list.selectedItem.index]
                    profiles = profile_library.remove(removed['id'])
                    # Preserve a missing selection visibly; never silently substitute a solid profile.
                    refresh_profiles(selected_id, saved=selected)
                    profile_status.text = 'Gelöscht: '+html.escape(removed['name'])
            except Exception as exc:
                profile_status.text = 'Profilaktion fehlgeschlagen: '+html.escape(str(exc))
            finally:
                event.input.value = False
                updating = False
        save_profile.isEnabled = pending_profile is not None and profile_confirm.value
        if event.input.id == profile_choice.id:
            update_profile_display()
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
        if event.input.id == apply_all.id and apply_all.value:
            updating = True
            try:
                for key, _ in demo.frame_levels(dict(bottom=bottom.value, shelf_count=count.value)):
                    number, direction = cross_fields[key]
                    number.listItems.item(all_count.selectedItem.index).isSelected = True
                    direction.listItems.item(all_direction.selectedItem.index).isSelected = True
                apply_all.value = False
            finally:
                updating = False
        if event.input.id == reset.id and reset.value:
            profile_choice.listItems.item(0).isSelected = True
            update_profile_display()
            mount.listItems.item(0).isSelected = True
            all_count.listItems.item(0).isSelected = True
            all_direction.listItems.item(0).isSelected = True
            for number, direction in cross_fields.values():
                number.listItems.item(0).isSelected = True
                direction.listItems.item(0).isSelected = True
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
        active_levels = dict(demo.frame_levels(dict(bottom=bottom.value, shelf_count=count.value)))
        for key, (number, direction) in cross_fields.items():
            number.isVisible = direction.isVisible = key in active_levels
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
