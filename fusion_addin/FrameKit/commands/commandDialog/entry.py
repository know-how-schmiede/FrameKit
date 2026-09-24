"""FrameKit integration demo: one native Fusion command with three tabs."""
import html
from pathlib import Path
import adsk.core
import adsk.fusion
from ... import config, demo, settings
from ...geometry import create_frame
from ...version import __version__
from ...lib import fusionAddInUtils as futil

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_CreateFrame'
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'
RESOURCES = Path(__file__).resolve().parents[2] / 'resources'
_handlers = []
_dialog_handlers = []


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
    frame = inputs.addTabCommandInput('frame_tab', 'Frame erstellen', str(RESOURCES / 'CreateFrame'))
    frame_inputs = frame.children
    frame_inputs.addTextBoxCommandInput('intro', '',
        '<b>FrameKit Demo</b><br>Einfaches Gestell aus massiven Rechteckprofilen. '
        'Keine Nutgeometrie, Verbinder oder Tragfähigkeitsberechnung.', 3, True)
    fields = {}
    for key, label in (('length', 'Länge'), ('width', 'Breite'),
                       ('height', 'Höhe'), ('profile', 'Profilbreite')):
        fields[key] = frame_inputs.addValueInput(key, label, 'mm',
            adsk.core.ValueInput.createByString(f'{values[key]} mm'))
    bottom = frame_inputs.addBoolValueInput('bottom', 'Unterer Rahmen', True, '', values['bottom'])
    create = frame_inputs.addBoolValueInput('create_geometry', 'Demo-Gestell erstellen', True, '', True)
    error = frame_inputs.addTextBoxCommandInput('validation', '', '', 2, True)

    manage = inputs.addTabCommandInput('settings_tab', 'Einstellungen verwalten',
                                       str(RESOURCES / 'ProfileLibrary')).children
    manage.addTextBoxCommandInput('settings_help', '',
        'Die Werte aus „Frame erstellen“ können als persönliche Standardwerte gespeichert werden. '
        'Zum reinen Speichern „Demo-Gestell erstellen“ abwählen. '
        'Erst „Ausführen“ speichert; „Abbrechen“ verwirft die Änderungen.', 4, True)
    persist = manage.addBoolValueInput('save_defaults', 'Als Standardwerte speichern', True, '', False)
    reset = manage.addBoolValueInput('reset_defaults', 'Werkseinstellungen laden', False, '', False)
    manage.addTextBoxCommandInput('settings_path', 'Datei', html.escape(str(settings.settings_path())), 3, True)
    manage.addTextBoxCommandInput('settings_status', '', html.escape(warning), 2, True)

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

    def read_values():
        if any(not field.isValidExpression for field in fields.values()):
            raise ValueError('Bitte gültige Längen eingeben.')
        result = {key: field.value * 10 for key, field in fields.items()}
        result['bottom'] = bottom.value
        demo.validate(result)
        return result

    def validation_message():
        try:
            read_values()
            if create.value and not adsk.fusion.Design.cast(app.activeProduct):
                return 'Zum Erstellen bitte ein Fusion-Konstruktionsdokument öffnen.'
            return ''
        except ValueError as exc:
            return str(exc)

    def validate(event):
        message = validation_message()
        error.text = message
        event.areInputsValid = not bool(message)

    def changed(event):
        if event.input.id == reset.id and reset.value:
            for key, field in fields.items():
                field.expression = f'{demo.DEFAULTS[key]} mm'
            bottom.value = demo.DEFAULTS['bottom']
            reset.value = False
        error.text = validation_message()

    def execute(event):
        try:
            current = read_values()
            if create.value:
                design = adsk.fusion.Design.cast(app.activeProduct)
                if not design:
                    raise ValueError('Bitte ein Fusion-Konstruktionsdokument öffnen.')
                create_frame(design, current)
                app.activeViewport.fit()
            if persist.value:
                settings.save(current)
        except Exception as exc:
            event.executeFailed = True
            event.executeFailedMessage = f'FrameKit: {exc}'
            futil.handle_error('FrameKit ausführen')

    def destroy(event):
        if handlers in _dialog_handlers:
            _dialog_handlers.remove(handlers)
        handlers.clear()

    for event, callback in ((command.execute, execute), (command.inputChanged, changed),
                            (command.validateInputs, validate), (command.destroy, destroy)):
        futil.add_handler(event, callback, local_handlers=handlers)
    error.text = validation_message()
