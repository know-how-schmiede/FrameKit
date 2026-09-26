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
from ...preview_camera import fit_preview
from ...dialog_status import set_status, set_if_changed
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
    command.setDialogInitialSize(580, 640)
    command.okButtonText = 'Ausführen'
    inputs = command.commandInputs
    values, warning = settings.load()
    library, library_warning = settings.load_library()
    profiles, profiles_warning = profile_library.load()
    def dropdown(parent, identifier, label, choices, selected):
        control = parent.addDropDownCommandInput(
            identifier, label, adsk.core.DropDownStyles.TextListDropDownStyle)
        for index, text in enumerate(choices):
            control.listItems.add(text, index == selected)
        return control

    def collapsed_group(parent, identifier, label):
        group = parent.addGroupCommandInput(identifier, label)
        group.isExpanded = False
        return group

    frame = inputs.addTabCommandInput('frame_tab', 'Frame erstellen', str(RESOURCES / 'CreateFrame'))
    frame_inputs = frame.children
    frame_inputs.addTextBoxCommandInput('intro', '',
        '<b>FrameKit</b><br>Gestell aus Demo-Vollprofilen oder eigenen DXF-Profilen. '
        'STEP-Winkel optional; keine Tragfähigkeitsberechnung.', 3, True)
    frame_type = dropdown(frame_inputs, 'frame_type', 'Bauart', ['Untergestell', 'Transportwagen'],
                          int(values.get('frame_type', 'frame') == 'cart'))
    fields = {}
    for key, label in (('length', 'Länge'), ('width', 'Breite'),
                       ('height', 'Gesamthöhe'), ('profile', 'Demo-Profilbreite')):
        fields[key] = frame_inputs.addValueInput(key, label, 'mm',
            adsk.core.ValueInput.createByString(f'{values[key]} mm'))
    profile_choice = frame_inputs.addDropDownCommandInput(
        'profile_choice', 'Profil für das gesamte Gestell', adsk.core.DropDownStyles.TextListDropDownStyle)
    profile_dimensions = frame_inputs.addTextBoxCommandInput('profile_dimensions', '', '', 2, True)
    bottom = frame_inputs.addBoolValueInput('bottom', 'Unterer Rahmen', True, '', values['bottom'])
    support_inputs = collapsed_group(frame_inputs, 'support_options', 'Füße / Rollen je Ecke').children
    support_individual = support_inputs.addBoolValueInput('support_individual', 'Einzeln je Ecke',
        True, '', 'corner_accessories' in values)
    support_choice = dropdown(support_inputs, 'support_choice', 'Gemeinsam für alle Ecken', [], 0)
    corner_choices = {key: dropdown(support_inputs, 'support_'+key.replace(':', '_'), label, [], 0)
                      for key, label in zip(accessories.CORNERS, accessories.CORNER_LABELS)}
    support_error = support_inputs.addTextBoxCommandInput('support_error', '', '', 3, True)
    support_error.isVisible = False
    def support_visibility():
        support_choice.isVisible = not support_individual.value
        for choice in corner_choices.values():
            choice.isVisible = support_individual.value
    support_visibility()
    shelves = collapsed_group(frame_inputs, 'shelves', 'Bodenplatten und Zwischenböden')
    shelf_inputs = shelves.children
    count = shelf_inputs.addIntegerSpinnerCommandInput(
        'shelf_count', 'Anzahl Zwischenböden', 0, demo.MAX_SHELVES, 1, values['shelf_count'])
    thickness = shelf_inputs.addValueInput('shelf_thickness', 'Plattenstärke', 'mm',
        adsk.core.ValueInput.createByString(f'{values["shelf_thickness"]} mm'))
    common_rotation = dropdown(frame_inputs, 'profile_rotation', 'Gemeinsame Profildrehung',
        ['0°', '90°', '180°', '270°'], values.get('profile_rotation', 0)//90)
    section_fields = {}
    initial_sections = {}

    def section_controls(parent, key, label, saved=None):
        identifier = key.replace(':', '_')
        choice = dropdown(parent, 'section_'+identifier, label+': Profil', [], 0)
        rotation = dropdown(parent, 'rotation_'+identifier, label+': Profildrehung',
            ['Übernehmen', '0°', '90°', '180°', '270°'],
            saved['rotation']//90+1 if saved and 'rotation' in saved else 0)
        section_fields[key] = (choice, rotation)
        initial_sections[key] = saved
        return choice, rotation

    profile_groups = collapsed_group(frame_inputs, 'profile_groups', 'Profile je Bauteilgruppe').children
    profile_groups.addTextBoxCommandInput('section_help', '',
        'Übernehmen verwendet das gemeinsame Profil bzw. bei Ebenen das Querträgerprofil. '
        '0°: Pfosten DXF-X entlang Gestell-X, DXF-Y entlang Gestell-Y. '
        'Bei Trägern ist DXF-X die horizontale Querschnittsbreite, DXF-Y die Höhe '
        '(Längs nach oben, Quer nach unten). Drehung um die Extrusionsachse.', 5, True)
    for key, label in (('posts', 'Pfosten'), ('frame', 'Rahmen'), ('cross', 'Querträger')):
        section_controls(profile_groups, key, label, values.get('group_profiles', {}).get(key))

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
    cross_group = collapsed_group(frame_inputs, 'cross_members', 'Querträger je Ebene')
    cross_inputs = cross_group.children
    cross_inputs.addTextBoxCommandInput('cross_help', '',
        '0 = keine Träger. Quer: vorne–hinten (Y), Längs: links–rechts (X). '
        'Gleich große freie Felder; Oberkanten bündig mit dem Rahmen.', 3, True)
    all_count = dropdown(cross_inputs, 'cross_all_count', 'Anzahl für alle Ebenen',
                         [str(i) for i in range(6)], 0)
    all_direction = dropdown(cross_inputs, 'cross_all_direction', 'Ausrichtung für alle Ebenen',
                             ['Quer', 'Längs'], 0)
    all_section = section_controls(cross_inputs, 'all', 'Für alle Ebenen')
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
        controls = section_controls(cross_inputs, key, label, saved.get('section'))
        for control in controls:
            control.isVisible = number.isVisible
    bracket_inputs = collapsed_group(frame_inputs, 'bracket_options', 'Winkel').children
    brackets = bracket_inputs.addBoolValueInput('brackets', 'Winkelkörper erstellen', True, '',
                                               values.get('brackets', True))
    brackets_double = bracket_inputs.addBoolValueInput('brackets_double', 'Zwei parallel bei doppelter Montagehöhe',
        True, '', values.get('brackets_double', False))
    bracket_inputs.addTextBoxCommandInput('bracket_help', '',
        'STEP-Winkel 20/30/40 mm an den Profilaußenflächen. Bei doppelter gemeinsamer '
        'Montagehöhe optional zwei parallele Winkel. Gemeinsam unter „91 | Winkel“ '
        'ein-/ausblendbar. Vorschau: Montagehüllen in Originalgröße.', 3, True)
    bracket_status = frame_inputs.addTextBoxCommandInput('bracket_status', '', '', 3, True)
    create = frame_inputs.addBoolValueInput('create_geometry', 'Gestell erstellen', True, '', True)
    preview_inputs = collapsed_group(frame_inputs, 'preview_options', 'Vorschau').children
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
    settings_status = manage.addTextBoxCommandInput('settings_status', '', '', 2, True)
    set_status(settings_status, warning, 'warning')
    library_group = collapsed_group(manage, 'support_library', 'Eigene Füße und Rollen')
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
    new_height = lib_inputs.addStringValueInput('support_height', 'Eingestellte Bauhöhe (mm)', '100')
    new_diameter = lib_inputs.addStringValueInput('support_diameter', 'Durchmesser (mm)', '75')
    brake = lib_inputs.addBoolValueInput('support_brake', 'Bremse', True, '', False)
    adjustable = lib_inputs.addBoolValueInput('support_adjustable', 'Höhenverstellbar', True, '', False)
    min_height = lib_inputs.addStringValueInput('support_min_height', 'Minimale Bauhöhe (mm)', '100')
    max_height = lib_inputs.addStringValueInput('support_max_height', 'Maximale Bauhöhe (mm)', '100')
    mounting = lib_inputs.addStringValueInput('support_mounting', 'Befestigung / Montagehinweis', '')
    reference = lib_inputs.addStringValueInput('support_reference', 'Referenztyp / Produkt', '')
    operating_state = lib_inputs.addStringValueInput('support_operating_state', 'Betriebsstellung', '')
    lib_inputs.addTextBoxCommandInput('support_definition_help', '',
        'Bauhöhe = eingestellte Höhe in der genannten Betriebsstellung, inklusive Befestigung. '
        'Bei Höhenverstellung Min/Max angeben; kein automatischer Ausgleich. '
        'Absenkbare Rollen benötigen Referenztyp und Betriebsstellung. Montage mittig unter dem Pfosten; '
        'Bremse und Befestigung werden als Eigenschaften gespeichert, nicht detailliert modelliert.', 5, True)
    load_entry = lib_inputs.addBoolValueInput('load_support', 'Auswahl zum Bearbeiten laden', False, '', False)
    update_entry = lib_inputs.addBoolValueInput('update_support', 'Geladenen Eintrag aktualisieren', False, '', False)
    duplicate_entry = lib_inputs.addBoolValueInput('duplicate_support', 'Auswahl duplizieren', False, '', False)
    editing_support_id = None
    update_entry.isEnabled = False
    save_entry = lib_inputs.addBoolValueInput('save_support', 'Neuen Eintrag speichern', False, '', False)
    library_status = lib_inputs.addTextBoxCommandInput('library_status', '', '', 3, True)
    set_status(library_status, library_warning, 'error')
    lib_inputs.addTextBoxCommandInput('library_path', 'Bibliotheksdatei',
        html.escape(str(settings.library_path())), 3, True)

    profile_group = collapsed_group(manage, 'profile_library', 'Eigene DXF-Profile')
    profile_inputs = profile_group.children
    profile_inputs.addTextBoxCommandInput('profile_help', '',
        'Querschnitt mit rechteckigen Außenmaßen in XY, Mittelpunkt im Ursprung. '
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
    profile_status = profile_inputs.addTextBoxCommandInput('profile_status', '', '', 3, True)
    set_status(profile_status, profiles_warning, 'error')
    profile_inputs.addTextBoxCommandInput('profile_path', 'Bibliotheksordner',
        html.escape(str(profile_library.directory())), 3, True)
    pending_profile = None
    selectable_profiles = []

    def selected_profile():
        item = profile_choice.selectedItem
        return selectable_profiles[item.index-1] if item and item.index > 0 else None

    def refresh_profiles(selected_id=None, listed_id=None, saved=None):
        nonlocal selectable_profiles
        previous_sections = {key: read_section(key) for key in section_fields} if selectable_profiles else initial_sections
        selectable_profiles = list(profiles)
        for selection in previous_sections.values():
            spec = selection.get('definition') if selection else None
            if spec and not any(p['id'] == spec['id'] for p in selectable_profiles):
                selectable_profiles.append(spec)
        if saved and not any(spec['id'] == saved['id'] for spec in selectable_profiles):
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
        for key, (choice, rotation) in section_fields.items():
            previous = previous_sections.get(key) or {}
            selected = previous.get('definition')
            choice.listItems.clear()
            choice.listItems.add('Übernehmen', True)
            for spec in selectable_profiles:
                suffix = ' (nicht in Bibliothek verfügbar)' if spec not in profiles else ''
                choice.listItems.add(profile_library.label(spec)+suffix,
                                     bool(selected and selected['id'] == spec['id']))
        delete_profile.isEnabled = bool(profiles)
        update_profile_display()

    def update_profile_display():
        spec = selected_profile()
        fields['profile'].isVisible = fields['profile'].isEnabled = spec is None
        profile_dimensions.text = (html.escape(profile_library.label(spec)) if spec else '')

    def read_section(key):
        choice, rotation = section_fields[key]
        result = {}
        if choice.selectedItem and choice.selectedItem.index:
            result['definition'] = deepcopy(selectable_profiles[choice.selectedItem.index-1])
        if rotation.selectedItem.index:
            result['rotation'] = (rotation.selectedItem.index-1)*90
        return result or None

    saved_profile = values.get('profile_definition')
    refresh_profiles(saved_profile['id'] if saved_profile else None, saved=saved_profile)

    support_options = []
    support_controls = {'common': support_choice, **corner_choices}

    def selected_support(key='common'):
        selected = support_controls[key].selectedItem
        return support_options[selected.index-1] if selected and selected.index > 0 else None

    def refresh_library(listed_id=None, selections=None):
        nonlocal support_options
        if selections is None:
            selections = {key: selected_support(key) for key in support_controls}
        support_options = list(library)
        for spec in selections.values():
            if spec is not None and spec not in support_options:
                support_options.append(deepcopy(spec))
        for key, choice in support_controls.items():
            choice.listItems.clear()
            choice.listItems.add('Keine Füße / Rollen', True)
            for spec in support_options:
                suffix = ' (gespeicherter Stand)' if spec not in library else ''
                choice.listItems.add(accessories.label(spec)+suffix, spec == selections.get(key))
        library_choice.listItems.clear()
        for index, spec in enumerate(library):
            library_choice.listItems.add(accessories.label(spec),
                spec['id'] == listed_id if listed_id else index == 0)
        if not library:
            library_choice.listItems.add('Keine gespeicherten Einträge', True)
        delete_entry.isEnabled = load_entry.isEnabled = duplicate_entry.isEnabled = bool(library)

    refresh_library(selections={'common': values.get('accessory'), **accessories.corner_specs(values)})

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
    preview_fit_pending = True

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
        if common_rotation.selectedItem.index:
            result['profile_rotation'] = common_rotation.selectedItem.index*90
        groups = {key: read_section(key) for key in ('posts', 'frame', 'cross') if read_section(key)}
        if groups:
            result['group_profiles'] = groups
        result['bottom'] = bottom.value
        selected = selected_support()
        result['accessory'] = deepcopy(selected)
        result['brackets'] = brackets.value
        result['brackets_double'] = brackets_double.value
        result['frame_type'] = 'cart' if frame_type.selectedItem.index else 'frame'
        if support_individual.value:
            result['corner_accessories'] = {key: deepcopy(selected_support(key)) for key in corner_choices}
            result['accessory'] = None
        result['shelf_count'] = count.value
        result['top_panel_mount'] = 'on_top' if mount.selectedItem.index else 'notched'
        result['cross_members'] = {
            key: dict(count=cross_fields[key][0].selectedItem.index,
                      direction='laengs' if cross_fields[key][1].selectedItem.index else 'quer')
            for key, _ in demo.frame_levels(result)}
        for key in result['cross_members']:
            selection = read_section(key)
            if selection:
                result['cross_members'][key]['section'] = selection
        used = list(groups.values()) + [spec.get('section') for spec in result['cross_members'].values()]
        for selection in used:
            definition = selection.get('definition') if selection else None
            if definition:
                if not any(spec['id'] == definition['id'] for spec in profiles):
                    raise ValueError('Gespeichertes Profil fehlt in der Bibliothek. Neu importieren oder anderes Profil wählen.')
                profile_library.verify_source(definition)
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

    def validation_message(update_display=True):
        message, support_message, summary, heights_text = '', '', '', ''
        try:
            current = read_values()
            calculated = current_model(current)
            warnings = calculated.get('connection_warnings', [])
            summary = '; '.join(warnings[:3])
            if len(warnings) > 3:
                summary += f'; weitere {len(warnings)-3} Hinweise in den Baugruppendaten.'
            heights = demo.shelf_heights(current)
            heights_text = ('Oberkanten: ' + '; '.join(
                f'{index:02d}: {height:.1f} mm' for index, height in enumerate(heights, 1))) if heights else ''
            if create.value and not adsk.fusion.Design.cast(app.activeProduct):
                message = 'Zum Erstellen bitte ein Fusion-Konstruktionsdokument öffnen.'
        except ValueError as exc:
            message = str(exc)
            if any(term in message for term in ('Füße/Rollen', 'Fuß-/Rollen')):
                support_message = message
        if update_display:
            set_status(support_error, support_message, 'error')
            set_if_changed(support_error, 'isVisible', bool(support_message))
            set_status(bracket_status, summary, 'warning')
            set_if_changed(resolved, 'text', heights_text)
        return message

    def validate(event):
        # Fusion can validate between keystrokes. Do not rebuild native controls
        # or write status text here; inputChanged updates the display separately.
        event.areInputsValid = not bool(validation_message(update_display=False))

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

    handling_change = False

    def changed(event):
        nonlocal handling_change
        if handling_change or updating:
            return
        handling_change = True
        try:
            changed_impl(event)
        finally:
            handling_change = False

    def changed_impl(event):
        nonlocal updating, library, profiles, pending_profile, editing_support_id
        nonlocal preview_fit_pending
        if updating:
            return
        if event.input.id in (show_preview.id, create.id):
            preview_fit_pending = True
        preview.clear()
        set_status(preview_status)
        if event.input.id == profile_unit.id:
            pending_profile = None
            profile_confirm.value = False
            set_status(profile_detected, 'Einheit geändert: DXF erneut auswählen und prüfen.', 'warning')
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
                        set_status(profile_detected)
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
                        set_status(profile_detected,
                            f'{spec["source_name"]}: {spec["width_mm"]:g} × {spec["height_mm"]:g} mm; '
                            f'{spec["loop_count"]-1} Hohlräume; Einheit {spec["source_unit"]}. '
                            'Maße prüfen und bestätigen.')
                        set_status(profile_status, 'Konturen und Probeextrusion erfolgreich geprüft.')
                        ignored = spec.get('ignored_entities', {})
                        if any(ignored.values()):
                            set_status(profile_status, profile_status.text + (
                                f' Ausgelassen: {ignored.get("points", 0)} Punkte, '
                                f'{ignored.get("construction", 0)} Hilfselemente. '
                                'Kontur und Hohlräume kontrollieren.'), 'warning')
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
                    set_status(profile_detected)
                    set_status(profile_status, 'Gespeichert und ausgewählt: '+profile_library.label(spec))
                elif profiles and profile_list.selectedItem:
                    removed = profiles[profile_list.selectedItem.index]
                    profiles = profile_library.remove(removed['id'])
                    # Preserve a missing selection visibly; never silently substitute a solid profile.
                    refresh_profiles(selected_id, saved=selected)
                    set_status(profile_status, 'Gelöscht: '+removed['name'])
            except Exception as exc:
                set_status(profile_status, 'Profilaktion fehlgeschlagen: '+str(exc), 'error')
            finally:
                event.input.value = False
                updating = False
        set_if_changed(save_profile, 'isEnabled', pending_profile is not None and profile_confirm.value)
        if event.input.id == profile_choice.id:
            update_profile_display()
        if event.input.id == frame_type.id:
            updating = True
            try:
                kind = 'cart' if frame_type.selectedItem.index else 'frame'
                arrangement = accessories.arrangement(kind)
                support_individual.value = kind == 'cart'
                refresh_library(selections={'common': arrangement['front:left'], **arrangement})
                if kind == 'cart':
                    bottom.value = True
                support_visibility()
            finally:
                updating = False
        if event.input.id == support_individual.id:
            if support_individual.value:
                common = support_choice.selectedItem.index
                for choice in corner_choices.values():
                    choice.listItems.item(common).isSelected = True
            support_visibility()
        actions = (save_entry.id, delete_entry.id, load_entry.id, update_entry.id, duplicate_entry.id)
        if event.input.id in actions and event.input.value:
            updating = True
            try:
                if library_warning:
                    raise ValueError('Bibliothek konnte nicht geladen werden. Datei reparieren und Dialog erneut öffnen.')
                listed = library[library_choice.selectedItem.index] if library else None
                if event.input.id == load_entry.id and listed:
                    editing_support_id = listed['id']
                    new_name.value = listed['name']
                    new_kind.listItems.item(accessories.KINDS.index(listed['kind'])).isSelected = True
                    new_height.value = str(listed['height'])
                    new_diameter.value = str(listed['diameter'])
                    brake.value = listed.get('brake', False)
                    adjustable.value = listed.get('adjustable', False)
                    min_height.value = str(listed.get('min_height', listed['height']))
                    max_height.value = str(listed.get('max_height', listed['height']))
                    mounting.value = listed.get('mounting', '')
                    reference.value = listed.get('reference', '')
                    operating_state.value = listed.get('operating_state', '')
                    update_entry.isEnabled = True
                    set_status(library_status, 'Zum Bearbeiten geladen: '+listed['name'])
                elif event.input.id in (save_entry.id, update_entry.id):
                    spec = accessories.new_spec(new_name.value, new_kind.selectedItem.name,
                        library_number(new_height), library_number(new_diameter),
                        definition_version=2, brake=brake.value, adjustable=adjustable.value,
                        mounting=mounting.value.strip(), reference=reference.value.strip(),
                        operating_state=operating_state.value.strip(),
                        **(dict(min_height=library_number(min_height), max_height=library_number(max_height))
                           if adjustable.value else {}))
                    if event.input.id == update_entry.id:
                        if not any(entry['id'] == editing_support_id for entry in library):
                            raise ValueError('Zuerst einen vorhandenen Eintrag zum Bearbeiten laden.')
                        spec['id'] = editing_support_id
                        revised = [spec if entry['id'] == editing_support_id else entry for entry in library]
                    else:
                        revised = library + [spec]
                    settings.save_library(revised)
                    library = revised
                    refresh_library(listed_id=spec['id'])
                    set_status(library_status, 'Gespeichert: '+accessories.label(spec)+'; Auswahl im Gestell bleibt unverändert.')
                elif event.input.id == duplicate_entry.id and listed:
                    spec = accessories.duplicate(listed, library)
                    revised = library + [spec]
                    settings.save_library(revised)
                    library = revised
                    refresh_library(listed_id=spec['id'])
                    set_status(library_status, 'Dupliziert: '+spec['name'])
                elif event.input.id == delete_entry.id and listed:
                    revised = [spec for spec in library if spec['id'] != listed['id']]
                    settings.save_library(revised)
                    library = revised
                    refresh_library()
                    if editing_support_id == listed['id']:
                        editing_support_id = None
                        update_entry.isEnabled = False
                    set_status(library_status, 'Gelöscht: '+listed['name']+'; gespeicherte Gestellauswahl bleibt erhalten.')
            except (ValueError, OSError) as exc:
                set_status(library_status, f'Nicht gespeichert: {exc}', 'error')
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
                    for target, source in zip(section_fields[key], all_section):
                        target.listItems.item(source.selectedItem.index).isSelected = True
                apply_all.value = False
            finally:
                updating = False
        if event.input.id == reset.id and reset.value:
            common_rotation.listItems.item(0).isSelected = True
            for choice, rotation in section_fields.values():
                choice.listItems.item(0).isSelected = True
                rotation.listItems.item(0).isSelected = True
            profile_choice.listItems.item(0).isSelected = True
            update_profile_display()
            mount.listItems.item(0).isSelected = True
            all_count.listItems.item(0).isSelected = True
            all_direction.listItems.item(0).isSelected = True
            for number, direction in cross_fields.values():
                number.listItems.item(0).isSelected = True
                direction.listItems.item(0).isSelected = True
            brackets.value = True
            brackets_double.value = False
            frame_type.listItems.item(0).isSelected = True
            support_individual.value = False
            for choice in support_controls.values():
                choice.listItems.item(0).isSelected = True
            support_visibility()
            for key, field in fields.items():
                field.expression = f'{demo.DEFAULTS[key]} mm'
            bottom.value = demo.DEFAULTS['bottom']
            count.value = demo.DEFAULTS['shelf_count']
            thickness.expression = f'{demo.DEFAULTS["shelf_thickness"]} mm'
            for field in height_fields:
                field.value = ''
            reset.value = False
        if event.input.id in (count.id, bottom.id, frame_type.id, reset.id):
            for index, field in enumerate(height_fields):
                set_if_changed(field, 'isVisible', index < count.value)
            active_levels = dict(demo.frame_levels(dict(bottom=bottom.value, shelf_count=count.value)))
            for key, (number, direction) in cross_fields.items():
                for control in (number, direction, *section_fields[key]):
                    set_if_changed(control, 'isVisible', key in active_levels)
        set_status(error, validation_message(), 'error')
        set_if_changed(show_preview, 'isEnabled', create.value)
        for control in (show_panels, show_accessories):
            set_if_changed(control, 'isEnabled', create.value and show_preview.value)

    def execute_preview(event):
        nonlocal preview_fit_pending
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
            set_status(preview_status)
            if preview_fit_pending:
                try:
                    fit_preview(app.activeViewport, current_model(current))
                    preview_fit_pending = False
                except Exception as exc:
                    set_status(preview_status, f'Vorschau sichtbar, Einpassen fehlgeschlagen: {exc}', 'warning')
            app.activeViewport.refresh()
        except Exception as exc:
            preview.clear()
            set_status(preview_status, f'Vorschau nicht verfügbar: {exc}', 'error')
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
                try:
                    settings.save(current)
                    set_status(settings_status, 'Standardwerte gespeichert.')
                except (ValueError, OSError) as exc:
                    set_status(settings_status, f'Standardwerte nicht gespeichert: {exc}', 'error')
                    raise
        except Exception as exc:
            set_status(error, f'FrameKit: {exc}', 'error')
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
    set_status(error, validation_message(), 'error')
