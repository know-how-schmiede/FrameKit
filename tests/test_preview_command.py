"""Drive command events with UI/graphics doubles; no running Fusion required."""
from copy import deepcopy
import html
import re
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

from fusion_addin.FrameKit import accessories, demo, profile_library, model, editing
from test_preview import Graphics


class Item:
    def __init__(self, owner, name, selected, index):
        self.owner, self.name, self.index = owner, name, index
        self.isSelected = selected

    @property
    def isSelected(self):
        return self._selected

    @isSelected.setter
    def isSelected(self, value):
        if value:
            for item in self.owner.items:
                item._selected = False
        self._selected = value


class Items:
    def __init__(self):
        self.items = []

    def add(self, name, selected):
        if selected:
            for item in self.items:
                item.isSelected = False
        item = Item(self, name, selected, len(self.items))
        self.items.append(item)
        return item

    def clear(self):
        self.items.clear()

    def item(self, index):
        return self.items[index]


class Control(NS):
    @property
    def isExpanded(self):
        return getattr(self, '_expanded', True)

    @isExpanded.setter
    def isExpanded(self, value):
        if getattr(self, 'nested_group', False):
            raise RuntimeError('3 : the group cannot be folded')
        self._expanded = value

    @property
    def formattedText(self):
        return getattr(self, '_formatted', '')

    @formattedText.setter
    def formattedText(self, value):
        self._formatted = value
        self.text = html.unescape(re.sub('<[^>]+>', '', value.replace('<br>', '\n')))

    @property
    def selectedItem(self):
        return next((item for item in self.listItems.items if item.isSelected), None)


class Inputs:
    def __init__(self, registry, in_group=False):
        self.registry = registry
        self.in_group = in_group
        self.controls = []

    @property
    def count(self):
        return len(self.controls)

    def item(self, index):
        return self.controls[index]

    def add(self, identifier, name, **values):
        result = Control(id=identifier, name=name, isVisible=True, isEnabled=True,
                         isValidExpression=True, **values)
        self.registry[identifier] = result
        self.controls.append(result)
        return result

    def addTabCommandInput(self, identifier, name, *args):
        return self.add(identifier, name, children=Inputs(self.registry), activate=Mock(return_value=True))

    def addGroupCommandInput(self, identifier, name):
        return self.add(identifier, name, children=Inputs(self.registry, in_group=True),
                        nested_group=self.in_group)

    def addBoolValueInput(self, identifier, name, check, resource, value):
        return self.add(identifier, name, value=value)

    def addTextBoxCommandInput(self, identifier, name, text, *args):
        return self.add(identifier, name, text=text)

    def addStringValueInput(self, identifier, name, value):
        return self.add(identifier, name, value=value)

    def addValueInput(self, identifier, name, units, value):
        return self.add(identifier, name, value=value)

    def addIntegerSpinnerCommandInput(self, identifier, name, minimum, maximum, step, value):
        return self.add(identifier, name, value=value)

    def addDropDownCommandInput(self, identifier, name, style):
        return self.add(identifier, name, listItems=Items())

    def addImageCommandInput(self, identifier, name, path):
        return self.add(identifier, name)


class PreviewCommandTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.profile_folder = Path(folder.name)/'profiles'
        location = patch.object(profile_library, 'directory', return_value=self.profile_folder)
        location.start()
        self.addCleanup(location.stop)
        adsk = ModuleType('adsk')
        core, fusion = ModuleType('adsk.core'), ModuleType('adsk.fusion')
        adsk.core, adsk.fusion = core, fusion
        self.graphics = Graphics()
        self.design = NS(rootComponent=NS(customGraphicsGroups=self.graphics),
                         unitsManager=NS(isValidExpression=lambda text, unit: True,
                                         evaluateExpression=lambda text, unit: float(text.split()[0])/10))
        ui = NS(workspaces=NS(itemById=lambda key: None),
                commandDefinitions=NS(itemById=lambda key: None))
        self.app = NS(activeProduct=self.design, activeViewport=NS(refresh=Mock(), fit=Mock()), userInterface=ui)
        core.Application = NS(get=lambda: self.app)
        core.ValueInput = NS(createByString=lambda s: float(s.split()[0])/10)
        core.DropDownStyles = NS(TextListDropDownStyle=0)
        core.Color = NS(create=lambda *args: args)
        fusion.Design = NS(cast=lambda product: product)
        fusion.CustomGraphicsCoordinates = NS(create=lambda values: values)
        fusion.CustomGraphicsSolidColorEffect = NS(create=lambda color: color)
        utilities = ModuleType('fusionAddInUtils')
        utilities.handle_error = Mock()

        def add_handler(event, callback, local_handlers):
            if not hasattr(event, 'callbacks'):
                event.callbacks = []
                def dispatch(args):
                    for handler in list(event.callbacks):
                        handler(args)
                event.callback = dispatch
            event.callbacks.append(callback)
            local_handlers.append(callback)

        utilities.add_handler = add_handler
        geometry = ModuleType('geometry')
        geometry.create_frame = Mock()
        self.create_frame = geometry.create_frame
        prefix = 'fusion_addin.FrameKit'
        modules = patch.dict(sys.modules, {
            'adsk': adsk, 'adsk.core': core, 'adsk.fusion': fusion,
            prefix+'.geometry': geometry, prefix+'.lib.fusionAddInUtils': utilities,
        })
        modules.start()
        self.addCleanup(modules.stop)
        folder = Path(__file__).resolve().parents[1] / 'fusion_addin/FrameKit'

        def load(name, path):
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        sys.modules[prefix+'.preview'] = load(prefix+'.preview', folder/'preview.py')
        self.entry = load(prefix+'.commands.commandDialog.entry_under_test', folder/'commands/commandDialog/entry.py')
        fit = patch.object(self.entry, 'fit_preview')
        self.fit_preview = fit.start()
        self.addCleanup(fit.stop)
        library = deepcopy(accessories.PRESETS)
        for name, value in (('load', (deepcopy(demo.DEFAULTS), '')), ('load_library', (library, ''))):
            patcher = patch.object(self.entry.settings, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        save = patch.object(self.entry.settings, 'save')
        self.save_defaults = save.start()
        self.addCleanup(save.stop)
        self.controls = {}
        self.command = NS(commandInputs=Inputs(self.controls), setDialogInitialSize=Mock(), doExecutePreview=Mock(return_value=True),
                          **{name: NS() for name in ('execute', 'executePreview', 'inputChanged', 'validateInputs', 'destroy')})
        self.entry.command_created(NS(command=self.command))

    def fire(self, name, **values):
        event = NS(**values)
        getattr(self.command, name).callback(event)
        return event

    def change(self, name, value):
        self.controls[name].value = value
        self.fire('inputChanged', input=self.controls[name])

    def show(self):
        self.change('show_preview', True)
        event = self.fire('executePreview')
        self.assertFalse(event.isValidResult)
        self.assertEqual(len(self.graphics.groups), 1)

    def test_changes_invalid_inputs_and_cancel_remove_temporary_graphics(self):
        self.show()
        first_points = self.graphics.groups[0].entities[0].points
        self.change('length', 100)
        self.assertEqual(self.graphics.groups, [])
        self.fire('executePreview')
        self.assertNotEqual(self.graphics.groups[0].entities[0].points, first_points)
        self.controls['length'].isValidExpression = False
        self.fire('inputChanged', input=self.controls['length'])
        event = self.fire('validateInputs')
        self.assertFalse(event.areInputsValid)
        self.assertEqual(self.graphics.groups, [])
        self.controls['length'].isValidExpression = True
        self.fire('executePreview')
        self.fire('destroy')
        self.assertEqual(self.graphics.groups, [])
        self.assertEqual(self.entry._previews, [])
        self.create_frame.assert_not_called()
        self.save_defaults.assert_not_called()

    def test_execute_clears_preview_and_creates_matching_model_then_fits(self):
        self.show()
        expected = self.graphics.groups[0].entities[0].points
        self.fire('execute')
        self.assertEqual(self.graphics.groups, [])
        design, values, calculated = self.create_frame.call_args.args
        self.assertIs(design, self.design)
        self.assertEqual(calculated['configuration'], values)
        self.assertEqual(expected, [v/10 for part in calculated['parts'] if part['kind'] == 'profile'
                                    for point in part['centerline_mm'] for v in point])
        self.app.activeViewport.fit.assert_called_once()

    def test_display_toggles_and_save_only(self):
        self.show()
        self.change('preview_panels', False)
        self.fire('executePreview')
        self.assertEqual(len(self.graphics.groups[0].entities), 2)  # profiles and bracket outlines
        self.change('show_preview', False)
        self.fire('executePreview')
        self.assertEqual(self.graphics.groups, [])
        self.show()
        self.change('create_geometry', False)
        self.fire('executePreview')
        self.assertEqual(self.graphics.groups, [])
        self.assertFalse(self.controls['show_preview'].isEnabled)
        self.controls['save_defaults'].value = True
        self.fire('execute')
        self.create_frame.assert_not_called()
        self.save_defaults.assert_called_once()
        self.app.activeViewport.fit.assert_not_called()

    def test_render_and_execute_failures_and_stop(self):
        self.graphics.fail_kind = 'mesh'
        self.change('show_preview', True)
        self.fire('executePreview')
        self.assertEqual(self.graphics.groups, [])
        self.assertIn('Vorschau nicht verfügbar', self.controls['preview_status'].text)
        self.graphics.fail_kind = None
        self.show()
        self.create_frame.side_effect = RuntimeError('Simulated assembly failure')
        event = self.fire('execute')
        self.assertTrue(event.executeFailed)
        self.assertEqual(self.graphics.groups, [])
        self.show()
        self.entry.stop()
        self.assertEqual(self.graphics.groups, [])
        self.assertEqual(self.entry._previews, [])

    def select(self, name, index):
        self.controls[name].listItems.item(index).isSelected = True
        self.fire('inputChanged', input=self.controls[name])

    def test_cross_member_copy_override_visibility_and_top_mount(self):
        self.change('shelf_count', 1)
        self.select('cross_all_count', 3)
        self.select('cross_all_direction', 1)
        self.change('cross_apply_all', True)
        self.select('cross_bottom_count', 0)
        self.select('cross_shelf_01_direction', 0)
        self.select('top_panel_mount', 1)
        self.assertTrue(self.controls['cross_shelf_01_count'].isVisible)
        self.assertFalse(self.controls['cross_shelf_02_count'].isVisible)
        self.show()
        self.fire('execute')
        _, values, calculated = self.create_frame.call_args.args
        self.assertEqual(values['top_panel_mount'], 'on_top')
        self.assertEqual(values['cross_members'], {
            'top': dict(count=3, direction='laengs'),
            'bottom': dict(count=0, direction='laengs'),
            'shelf:01': dict(count=3, direction='quer')})
        self.assertEqual(sum(':cross:' in p['key'] and p['kind'] == 'profile'
                             for p in calculated['parts']), 6)
        self.change('bottom', False)
        self.assertFalse(self.controls['cross_bottom_count'].isVisible)
        self.change('reset_defaults', True)
        self.assertEqual(self.controls['top_panel_mount'].selectedItem.index, 0)
        self.assertEqual(self.controls['cross_top_count'].selectedItem.index, 0)

    def test_cross_members_reject_tight_frame_in_dialog(self):
        self.select('cross_top_count', 5)
        self.change('length', 28)
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        self.assertIn('zu wenig Platz', self.controls['validation'].text)

    def profile_dialog(self, filename, accepted=True):
        core = sys.modules['adsk.core']
        core.DialogResults = NS(DialogOK=1)
        dialog = NS(filename=str(filename), showOpen=lambda: 1 if accepted else 0)
        self.app.userInterface.createFileDialog = lambda: dialog
        adapter = ModuleType('profile_geometry')
        adapter.validate_in_fusion = Mock()
        modules = patch.dict(sys.modules, {'fusion_addin.FrameKit.profile_geometry': adapter})
        modules.start()
        self.addCleanup(modules.stop)
        return adapter

    def test_dxf_import_confirm_save_select_and_delete(self):
        from test_profile_library import FIXTURE
        adapter = self.profile_dialog(FIXTURE)
        self.change('choose_profile', True)
        adapter.validate_in_fusion.assert_called_once()
        self.assertIn('40 × 40 mm', self.controls['profile_detected'].text)
        self.assertFalse(self.controls['save_profile'].isEnabled)
        self.change('profile_confirm', True)
        self.assertTrue(self.controls['save_profile'].isEnabled)
        self.change('profile_name', 'Mein Profil')
        self.change('profile_manufacturer', 'Benutzereingabe')
        self.change('save_profile', True)
        entries, warning = profile_library.load()
        self.assertEqual(warning, '')
        self.assertEqual(entries[0]['name'], 'Mein Profil')
        self.assertEqual(entries[0]['manufacturer'], 'Benutzereingabe')
        self.assertFalse(self.controls['profile'].isVisible)
        self.assertEqual(self.controls['profile_choice'].selectedItem.index, 1)
        self.show()
        self.fire('execute')
        _, values, calculated = self.create_frame.call_args.args
        self.assertEqual(values['profile_definition'], entries[0])
        self.assertEqual(values['profile'], 40)
        self.assertTrue(any(p['geometry']['type'] == 'dxf' for p in calculated['parts']))
        self.change('delete_profile', True)
        self.assertEqual(profile_library.load(), ([], ''))
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        self.assertIn('fehlt in der Bibliothek', self.controls['validation'].text)
        self.select('profile_choice', 0)
        self.assertTrue(self.fire('validateInputs').areInputsValid)
        self.assertTrue(self.controls['profile'].isVisible)

    def test_dxf_cancel_unit_change_and_failed_probe_do_not_save(self):
        from test_profile_library import FIXTURE
        adapter = self.profile_dialog(FIXTURE, accepted=False)
        self.change('choose_profile', True)
        adapter.validate_in_fusion.assert_not_called()
        self.assertFalse(self.controls['save_profile'].isEnabled)
        adapter = self.profile_dialog(FIXTURE)
        adapter.validate_in_fusion.side_effect = ValueError('Kontur fehlerhaft')
        self.change('choose_profile', True)
        self.assertIn('Kontur fehlerhaft', self.controls['profile_status'].text)
        self.assertEqual(profile_library.load(), ([], ''))
        adapter.validate_in_fusion.side_effect = None
        self.change('choose_profile', True)
        self.change('profile_confirm', True)
        self.select('profile_unit', 1)
        self.assertFalse(self.controls['save_profile'].isEnabled)
        self.change('save_profile', True)
        self.assertIn('Zuerst DXF prüfen', self.controls['profile_status'].text)
        self.assertEqual(profile_library.load(), ([], ''))

    def test_dxf_file_change_blocks_creation_and_reset_restores_demo(self):
        from test_profile_library import FIXTURE
        self.profile_dialog(FIXTURE)
        self.change('choose_profile', True)
        self.change('profile_confirm', True)
        self.change('save_profile', True)
        entries, _ = profile_library.load()
        (self.profile_folder/entries[0]['filename']).write_text('changed')
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        self.change('length', self.controls['length'].value)
        self.assertIn('verändert', self.controls['validation'].text)
        self.change('reset_defaults', True)
        self.assertTrue(self.fire('validateInputs').areInputsValid)
        self.assertEqual(self.controls['profile_choice'].selectedItem.index, 0)

    def test_group_profiles_level_copy_rotation_and_deleted_selection(self):
        from test_sections import rectangle
        with tempfile.TemporaryDirectory() as folder:
            rectangle(folder, 20, 40)
            self.profile_dialog(Path(folder)/'20x40.dxf')
            self.change('choose_profile', True)
            self.change('profile_confirm', True)
            self.change('save_profile', True)
        # Shared demo 40; narrow rectangular frame and cross members.
        self.select('profile_choice', 0)
        self.select('section_frame', 1)
        self.select('section_cross', 1)
        self.change('shelf_count', 1)
        self.select('cross_all_count', 2)
        self.select('section_all', 1)
        self.select('rotation_all', 2)  # 90 degrees
        self.change('cross_apply_all', True)
        self.select('rotation_shelf_01', 1)  # 0 degrees on one level
        self.show()
        self.fire('execute')
        _, values, data = self.create_frame.call_args.args
        self.assertEqual(values['cross_members']['top']['section']['rotation'], 90)
        self.assertEqual(values['cross_members']['shelf:01']['section']['rotation'], 0)
        top = next(p for p in data['parts'] if p['key'] == 'top:cross:01')
        self.assertEqual(top['bounds_mm'], [40, 460, 20])
        self.change('delete_profile', True)
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        self.assertIn('fehlt in der Bibliothek', self.controls['validation'].text)
        self.assertIn('nicht in Bibliothek', self.controls['section_frame'].selectedItem.name)
        self.change('reset_defaults', True)
        self.assertTrue(self.fire('validateInputs').areInputsValid)
        self.assertEqual(self.controls['section_frame'].selectedItem.index, 0)
        self.assertEqual(self.controls['rotation_top'].selectedItem.index, 0)

    def test_saved_missing_group_profile_is_visible_and_blocks_creation(self):
        from test_sections import rectangle
        with tempfile.TemporaryDirectory() as folder:
            spec = rectangle(folder, 20, 40)
        saved = dict(deepcopy(demo.DEFAULTS), group_profiles={
            'frame': dict(definition=spec, rotation=180)})
        with patch.object(self.entry.settings, 'load', return_value=(saved, '')):
            self.entry.command_created(NS(command=self.command))
        self.assertIn('nicht in Bibliothek', self.controls['section_frame'].selectedItem.name)
        self.assertEqual(self.controls['rotation_frame'].selectedItem.index, 3)
        self.assertFalse(self.fire('validateInputs').areInputsValid)

    def open_edit(self, values=None, chooser=False):
        from test_geometry_adapter import Matrix
        self.fire('destroy')
        values = deepcopy(values if values is not None else demo.DEFAULTS)
        values.setdefault('brackets', False)
        values.setdefault('brackets_double', False)
        occurrence = NS(name='FrameKit saved', isLightBulbOn=True, isValid=True)
        transform = Matrix()
        transform.origin = (100, 0, 0)
        context = dict(occurrence=occurrence, values=values, model=model.build_model(values),
                       design=self.design, transform=transform)
        self.controls = {}
        self.command = NS(commandInputs=Inputs(self.controls), setDialogInitialSize=Mock(), doExecutePreview=Mock(return_value=True),
                          **{name: NS() for name in ('execute', 'executePreview', 'inputChanged', 'validateInputs', 'destroy')})
        if not chooser:
            self.entry.command_created(NS(command=self.command), context)
        return context

    def test_edit_selection_loads_target_and_requires_load_before_execute(self):
        context = self.open_edit(dict(demo.DEFAULTS, length=1300), chooser=True)
        other = NS(name='Other frame')
        with patch.object(editing, 'frames', return_value=[other, context['occurrence']]), \
                patch.object(editing, 'load', return_value=context) as load:
            self.entry.edit_created(NS(command=self.command))
            self.assertFalse(self.fire('validateInputs').areInputsValid)
            self.select('edit_target', 1)
            self.change('edit_load', True)
            load.assert_called_once_with(self.design, context['occurrence'])
        self.assertFalse(self.controls['edit_selection'].isVisible)
        self.assertEqual(self.controls['length'].value, 130)
        self.assertEqual(self.command.okButtonText, 'Neu aufbauen')
        self.assertTrue(self.fire('validateInputs').areInputsValid)

    def test_edit_load_reuses_tabs_without_accessing_expired_created_event(self):
        context = self.open_edit(chooser=True)
        class CreatedEvent:
            expired = False
            @property
            def command(event):
                if event.expired:
                    raise RuntimeError('CommandCreatedEventArgs is no longer valid')
                return self.command
        args = CreatedEvent()
        with patch.object(editing, 'frames', return_value=[context['occurrence']]), \
                patch.object(editing, 'load', return_value=context), \
                patch.object(self.command.commandInputs, 'addGroupCommandInput',
                             side_effect=AssertionError('Only tabs at the root')):
            self.entry.edit_created(args)
            tabs = {key: self.controls[key] for key in ('frame_tab', 'settings_tab', 'info_tab')}
            self.assertTrue(tabs['frame_tab'].isVisible)
            self.assertFalse(tabs['settings_tab'].isVisible)
            self.assertFalse(tabs['info_tab'].isVisible)
            args.expired = True
            with patch.object(self.command.commandInputs, 'addTabCommandInput',
                              side_effect=AssertionError('Do not create tabs during inputChanged')):
                self.change('edit_load', True)
        for key, tab in tabs.items():
            self.assertIs(self.controls[key], tab)
            self.assertTrue(tab.isVisible)
        self.assertFalse(self.controls['edit_selection'].isVisible)
        self.assertIn('length', self.controls)
        self.assertTrue(self.fire('validateInputs').areInputsValid)

    def test_failed_editor_population_keeps_selection_and_error_visible(self):
        context = self.open_edit(chooser=True)
        with patch.object(editing, 'frames', return_value=[context['occurrence']]), \
                patch.object(editing, 'load', return_value=context):
            self.entry.edit_created(NS(command=self.command))
            with patch.object(self.controls['profile_choice'].listItems, 'clear',
                              side_effect=RuntimeError('Native control failed')):
                self.change('edit_load', True)
        self.assertTrue(self.controls['edit_selection'].isVisible)
        self.assertFalse(self.controls['length'].isVisible)
        self.assertFalse(self.controls['edit_load'].isEnabled)
        self.assertIn('Native control failed', self.controls['edit_status'].text)
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        with patch.object(editing, 'replace') as rebuild:
            self.assertTrue(self.fire('execute').executeFailed)
            rebuild.assert_not_called()
        self.create_frame.assert_not_called()

    def test_loading_populates_existing_controls_and_preview_updates_repeatedly(self):
        from test_sections import rectangle
        with tempfile.TemporaryDirectory() as folder:
            definition = rectangle(folder, 30, 30)
        values = dict(demo.DEFAULTS, length=1200, width=600, profile=30,
                      profile_definition=definition, shelf_count=1, shelf_heights=[350],
                      accessory=accessories.PRESETS[0], profile_rotation=90,
                      group_profiles={'posts': {'definition': definition, 'rotation': 180}},
                      cross_members={'top': {'count': 2, 'direction': 'quer'}},
                      brackets=True, brackets_double=True)
        context = self.open_edit(values, chooser=True)
        with patch.object(editing, 'frames', return_value=[context['occurrence']]), \
                patch.object(editing, 'load', return_value=context), \
                patch.object(editing, 'check_current'), patch.object(editing, 'replace') as rebuild:
            self.entry.edit_created(NS(command=self.command))
            ids = {key: id(control) for key, control in self.controls.items()}
            self.assertIn('length', ids)
            self.assertNotIn('edit_fields', ids)
            for key in ('support_options', 'shelves', 'profile_groups', 'cross_members',
                        'bracket_options', 'preview_options'):
                self.assertFalse(self.controls[key].nested_group)
                self.assertFalse(self.controls[key].isExpanded)
                self.assertFalse(self.controls[key].isVisible)
            self.assertFalse(self.controls['length'].isVisible)
            def native_preview():
                # The original must be hidden before entering the preview transaction.
                self.assertFalse(context['occurrence'].isLightBulbOn)
                self.fire('executePreview')
                return True
            self.command.doExecutePreview.side_effect = native_preview
            with patch.object(Inputs, 'add', side_effect=AssertionError('Late control creation')):
                self.change('edit_load', True)
                self.assertEqual(ids, {key: id(control) for key, control in self.controls.items()})
                self.assertTrue(self.controls['length'].isVisible)
                self.assertTrue(self.controls['preview_options'].isVisible)
                self.assertFalse(self.controls['profile'].isVisible)
                self.change('show_preview', True)
                for length in (900, 300, 750):
                    self.change('length', length/10)
                    self.assertFalse(context['occurrence'].isLightBulbOn)
                    points = self.graphics.groups[0].entities[0].points
                    self.assertAlmostEqual(max(points[::3])-min(points[::3]), (length-30)/10)
                self.fire('execute')
            edited = rebuild.call_args.args[1]
            self.assertEqual(edited['shelf_heights'], [350])
            self.assertEqual(edited['group_profiles'], values['group_profiles'])
            self.assertEqual(edited['profile_rotation'], 90)
            self.assertEqual(edited['accessory'], values['accessory'])
            self.assertEqual(edited['cross_members']['top']['count'], 2)
            self.assertTrue(edited['brackets_double'])

    def test_editor_routes_through_handlers_registered_before_loading(self):
        context = self.open_edit(chooser=True)
        with patch.object(editing, 'frames', return_value=[context['occurrence']]), \
                patch.object(editing, 'load', return_value=context), \
                patch.object(editing, 'check_current'), patch.object(editing, 'replace') as rebuild:
            self.entry.edit_created(NS(command=self.command))
            def native_preview():
                self.fire('executePreview')
                return True
            self.command.doExecutePreview.side_effect = native_preview
            with patch.object(self.entry.futil, 'add_handler',
                              side_effect=AssertionError('Late event binding is not allowed')):
                self.change('edit_load', True)
                self.assertTrue(self.fire('validateInputs').areInputsValid)
                self.change('show_preview', True)
                self.assertTrue(self.controls['preview_panels'].isEnabled)
                self.assertTrue(self.controls['preview_accessories'].isEnabled)
                self.assertEqual(len(self.graphics.groups), 1)
                self.assertFalse(context['occurrence'].isLightBulbOn)
                self.change('length', 100)
                self.fire('execute')
                rebuild.assert_called_once()
                self.assertEqual(rebuild.call_args.args[1]['length'], 1000)
                self.fire('destroy')
                self.assertEqual(self.graphics.groups, [])

    def test_edit_selection_reports_missing_frames_and_invalid_data(self):
        context = self.open_edit(chooser=True)
        with patch.object(editing, 'frames', return_value=[]):
            self.entry.edit_created(NS(command=self.command))
        self.assertFalse(self.controls['edit_load'].isEnabled)
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        context = self.open_edit(chooser=True)
        with patch.object(editing, 'frames', return_value=[context['occurrence']]), \
                patch.object(editing, 'load', side_effect=ValueError('Nicht unterstützte Konfigurationsversion.')):
            self.entry.edit_created(NS(command=self.command))
            self.change('edit_load', True)
        self.assertIn('Konfigurationsversion', self.controls['edit_status'].text)
        self.assertTrue(self.controls['edit_selection'].isVisible)
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        self.assertFalse(self.controls['length'].isVisible)

    def test_edit_preview_failure_restores_visibility_and_does_not_replace(self):
        context = self.open_edit()
        self.graphics.fail_kind = 'mesh'
        with patch.object(editing, 'check_current'), patch.object(editing, 'replace') as rebuild:
            self.change('show_preview', True)
            self.fire('executePreview')
            self.assertTrue(context['occurrence'].isLightBulbOn)
            self.assertEqual(self.graphics.groups, [])
            self.assertIn('Vorschau nicht verfügbar', self.controls['preview_status'].text)
            rebuild.assert_not_called()

    def test_edit_requests_native_preview_without_waiting_for_automatic_event(self):
        context = self.open_edit()
        def native_preview():
            self.fire('executePreview')
            return True
        self.command.doExecutePreview.side_effect = native_preview
        with patch.object(editing, 'check_current'):
            self.change('show_preview', True)
            self.command.doExecutePreview.assert_called_once()
            self.assertEqual(len(self.graphics.groups), 1)
            self.assertFalse(context['occurrence'].isLightBulbOn)
            points = list(self.graphics.groups[0].entities[0].points)
            self.change('length', 100)
            self.assertEqual(self.command.doExecutePreview.call_count, 2)
            self.assertNotEqual(self.graphics.groups[0].entities[0].points, points)
            self.change('show_preview', False)
            self.assertEqual(self.graphics.groups, [])
            self.assertTrue(context['occurrence'].isLightBulbOn)

    def test_preview_survives_output_and_reentrant_events(self):
        self.show()
        original = self.graphics.groups[0]
        for key, kind in (('preview_status', 'TextBoxCommandInput'),
                          ('preview_options', 'GroupCommandInput'), ('frame_tab', 'TabCommandInput')):
            control = self.controls[key]
            control.objectType = 'adsk::core::'+kind
            self.fire('inputChanged', input=control)
            self.assertIs(self.graphics.groups[0], original)
        # An automatic preview may trigger callbacks while changing visibility,
        # setting status text or updating the camera. They must not clear it.
        def refresh_events():
            self.fire('inputChanged', input=self.controls['length'])
            self.fire('executePreview')
        self.app.activeViewport.refresh.side_effect = refresh_events
        self.fire('executePreview')
        self.assertEqual(len(self.graphics.groups), 1)
        self.assertEqual(self.app.activeViewport.refresh.call_count, 2)

    def test_failed_native_preview_request_has_visible_error(self):
        self.command.doExecutePreview.return_value = False
        self.change('show_preview', True)
        self.assertIn('nicht gestartet', self.controls['preview_status'].text)
        self.assertEqual(self.graphics.groups, [])

    def test_edit_preview_and_cancel_restore_original_without_building(self):
        context = self.open_edit()
        with patch.object(editing, 'check_current'), patch.object(editing, 'replace') as rebuild:
            self.show()
            self.assertFalse(context['occurrence'].isLightBulbOn)
            self.assertGreaterEqual(min(self.graphics.groups[0].entities[0].points[::3]), 100)
            self.change('length', 100)
            self.assertFalse(context['occurrence'].isLightBulbOn)
            self.fire('executePreview')
            self.assertFalse(context['occurrence'].isLightBulbOn)
            self.fire('destroy')
            self.assertTrue(context['occurrence'].isLightBulbOn)
            self.assertEqual(self.graphics.groups, [])
            rebuild.assert_not_called()
        self.create_frame.assert_not_called()

    def test_edit_execute_uses_previous_ids_and_signals_transaction_failure(self):
        context = self.open_edit()
        with patch.object(editing, 'replace') as rebuild:
            self.change('length', 100)
            self.fire('execute')
            received, values, calculated = rebuild.call_args.args
            self.assertIs(received, context)
            self.assertEqual(values['length'], 1000)
            self.assertEqual(calculated['assembly_id'], context['model']['assembly_id'])
            self.assertEqual(calculated['id_registry'], context['model']['id_registry'])
            rebuild.side_effect = RuntimeError('Rebuild failed')
            failure = self.fire('execute')
            self.assertTrue(failure.executeFailed)
            self.assertIn('Rebuild failed', failure.executeFailedMessage)
        self.create_frame.assert_not_called()

    def test_edit_uses_saved_dxf_after_library_and_file_are_gone(self):
        from test_sections import rectangle
        with tempfile.TemporaryDirectory() as folder:
            definition = rectangle(folder, 30, 30)
        context = self.open_edit(dict(demo.DEFAULTS, profile=30, profile_definition=definition))
        self.assertTrue(self.fire('validateInputs').areInputsValid)
        with patch.object(editing, 'replace') as rebuild:
            self.fire('execute')
            self.assertEqual(rebuild.call_args.args[1]['profile_definition'], definition)
            self.assertEqual(rebuild.call_args.args[2]['profiles'], context['model']['profiles'])

    def test_typing_does_not_rewrite_editors_or_layout_and_validation_is_read_only(self):
        original = Control.__setattr__
        writes = []
        def record(control, name, value):
            writes.append((control.id, name, value))
            original(control, name, value)
        # Value inputs and string inputs in the frame/library tabs share the handler.
        for key in ('length', 'width', 'height', 'profile', 'shelf_thickness',
                    'support_height', 'support_diameter', 'support_name'):
            control = self.controls[key]
            for text in ('6', '60', '600', '600.5', '600'):
                control.expression = text
                control.value = float(text)/10 if key in (
                    'length', 'width', 'height', 'profile', 'shelf_thickness') else text
                writes.clear()
                with patch.object(Control, '__setattr__', record):
                    self.fire('inputChanged', input=control)
                self.assertEqual(control.expression, text)
                self.assertFalse([w for w in writes if w[1] in
                    ('isVisible', 'isEnabled', 'expression', 'value')], (key, text, writes))
                writes.clear()
                with patch.object(Control, '__setattr__', record):
                    self.fire('validateInputs')
                self.assertEqual(writes, [], (key, text))

    def test_unchanged_status_does_not_write_native_text_again(self):
        from fusion_addin.FrameKit.dialog_status import set_status
        control = self.controls['validation']
        set_status(control, 'Ungültige Länge', 'error')
        original = Control.__setattr__
        writes = []
        def record(control, name, value):
            writes.append(name)
            original(control, name, value)
        with patch.object(Control, '__setattr__', record):
            set_status(control, 'Ungültige Länge', 'error')
        self.assertEqual(writes, [])
        set_status(control)
        self.assertEqual(control.text, '')

    def test_collapsed_groups_and_cart_preset_with_individual_validation(self):
        for key in ('support_options', 'shelves', 'profile_groups', 'cross_members',
                    'preview_options', 'support_library', 'profile_library'):
            self.assertFalse(self.controls[key].isExpanded)
        self.command.setDialogInitialSize.assert_called_with(580, 640)
        self.select('frame_type', 1)
        self.assertTrue(self.controls['support_individual'].value)
        self.assertFalse(self.controls['support_choice'].isVisible)
        self.show()
        self.fire('execute')
        _, values, data = self.create_frame.call_args.args
        self.assertEqual(values['frame_type'], 'cart')
        self.assertEqual(values['corner_accessories']['back:right']['kind'], 'Bockrolle')
        self.assertEqual(sum(p['kind'] == 'support' for p in data['parts']), 4)
        self.select('support_front_left', 1)  # 40 mm foot vs 100 mm casters
        self.assertFalse(self.fire('validateInputs').areInputsValid)
        self.assertIn('Bauhöhe', self.controls['validation'].text)
        self.assertIn('Bauhöhe', self.controls['support_error'].text)
        self.assertTrue(self.controls['support_error'].isVisible)
        self.assertNotIn('support_help', self.controls)
        self.assertEqual(self.graphics.groups, [])
        self.select('frame_type', 0)
        self.assertFalse(self.controls['support_individual'].value)
        self.assertTrue(self.fire('validateInputs').areInputsValid)
        self.assertFalse(self.controls['support_error'].isVisible)
        self.assertEqual(self.controls['support_error'].text, '')
        self.change('reset_defaults', True)
        self.assertEqual(self.controls['support_choice'].selectedItem.index, 0)

    def test_accessory_edit_duplicate_and_delete_preserve_selected_snapshot(self):
        with patch.object(self.entry.settings, 'save_library') as save:
            self.select('support_choice', 2)
            self.select('library_choice', 1)
            self.change('load_support', True)
            self.change('support_name', 'Neue Rolle')
            self.change('support_height', '120')
            self.change('support_brake', True)
            self.change('support_mounting', 'Vierlochplatte')
            self.change('update_support', True)
            revised = deepcopy(save.call_args.args[0])
            self.assertEqual(revised[1]['id'], accessories.PRESETS[1]['id'])
            self.assertEqual(revised[1]['height'], 120)
            self.assertTrue(revised[1]['brake'])
            self.assertIn('gespeicherter Stand', self.controls['support_choice'].selectedItem.name)
            self.fire('execute')
            _, values, first = self.create_frame.call_args.args
            self.assertEqual(values['accessory']['height'], 100)
            self.select('support_choice', 2)  # opt into the updated library entry
            self.fire('execute')
            _, values, second = self.create_frame.call_args.args
            self.assertEqual(values['accessory']['height'], 120)
            self.assertEqual(next(p for p in first['parts'] if p['kind'] == 'support')['bounds_mm'][2], 100)
            self.change('duplicate_support', True)
            self.assertEqual(len(save.call_args.args[0]), 4)
            self.assertNotEqual(save.call_args.args[0][-1]['id'], revised[1]['id'])
            self.change('delete_support', True)
            self.assertEqual(len(save.call_args.args[0]), 3)
            self.select('library_choice', 1)
            self.change('delete_support', True)
            self.assertTrue(self.fire('validateInputs').areInputsValid)
            self.assertIn('gespeicherter Stand', self.controls['support_choice'].selectedItem.name)

    def test_failed_accessory_write_keeps_library_and_selection(self):
        self.select('support_choice', 1)
        self.change('load_support', True)
        self.change('support_name', 'Changed')
        with patch.object(self.entry.settings, 'save_library', side_effect=OSError('disk full')):
            self.change('update_support', True)
        self.assertIn('disk full', self.controls['library_status'].text)
        self.assertIn('Demo-Fuß', self.controls['support_choice'].selectedItem.name)
        self.assertIn('Demo-Fuß', self.controls['library_choice'].selectedItem.name)

    def test_error_colors_across_validation_preview_and_libraries(self):
        self.select('frame_type', 1)
        self.select('support_front_left', 1)
        self.assertIn('#B71C1C', self.controls['validation'].formattedText)
        self.select('frame_type', 0)
        self.assertEqual(self.controls['validation'].formattedText, '')
        self.graphics.fail_kind = 'mesh'
        self.change('show_preview', True)
        self.fire('executePreview')
        self.assertIn('#B71C1C', self.controls['preview_status'].formattedText)
        self.change('support_name', '<invalid & name>')
        self.change('support_height', '-1')
        self.change('save_support', True)
        self.assertIn('#B71C1C', self.controls['library_status'].formattedText)
        self.change('save_profile', True)
        self.assertIn('#B71C1C', self.controls['profile_status'].formattedText)

    def test_loading_warnings_are_formatted_and_user_names_are_escaped(self):
        self.fire('destroy')
        for event in ('execute', 'executePreview', 'inputChanged', 'validateInputs', 'destroy'):
            setattr(self.command, event, NS())
        with patch.object(self.entry.settings, 'load', return_value=(deepcopy(demo.DEFAULTS), 'Warnung <x>')):
            self.entry.command_created(NS(command=self.command))
        self.assertIn('#854700', self.controls['settings_status'].formattedText)
        self.assertIn('&lt;x&gt;', self.controls['settings_status'].formattedText)
        self.change('support_name', '<Fuß & Test>')
        with patch.object(self.entry.settings, 'save_library'):
            self.change('save_support', True)
        text = self.controls['library_status'].formattedText
        self.assertIn('&lt;Fuß &amp; Test&gt;', text)
        self.assertNotIn('#B71C1C', text)

    def test_preview_fits_on_open_and_reopen_but_preserves_manual_zoom_on_updates(self):
        self.show()
        self.fit_preview.assert_called_once()
        self.change('length', 100)
        self.fire('executePreview')
        self.fit_preview.assert_called_once()
        self.change('show_preview', False)
        self.fire('executePreview')
        self.show()
        self.assertEqual(self.fit_preview.call_count, 2)
        viewport, data = self.fit_preview.call_args.args
        self.assertIs(viewport, self.app.activeViewport)
        self.assertEqual(data['configuration']['length'], 1000)

    def test_failed_fit_keeps_preview_visible_and_reports_warning(self):
        self.fit_preview.side_effect = ValueError('camera unavailable')
        self.show()
        self.assertIn('Einpassen fehlgeschlagen', self.controls['preview_status'].text)
        self.assertIn('#854700', self.controls['preview_status'].formattedText)

    def test_brackets_default_toggle_saved_options_and_missing_size_warning(self):
        self.assertFalse(self.controls['bracket_options'].isExpanded)
        self.assertTrue(self.controls['brackets'].value)
        self.fire('execute')
        _, values, data = self.create_frame.call_args.args
        self.assertEqual(sum(p['kind'] == 'connection' for p in data['parts']), 8)
        self.change('brackets', False)
        self.fire('execute')
        _, values, data = self.create_frame.call_args.args
        self.assertFalse(values['brackets'])
        self.assertFalse(any(p['kind'] == 'connection' for p in data['parts']))
        self.change('brackets', True)
        self.change('profile', 2.5)
        self.assertTrue(self.fire('validateInputs').areInputsValid)
        self.assertIn('keine gemeinsame Winkelgröße', self.controls['bracket_status'].text)
        self.assertIn('#854700', self.controls['bracket_status'].formattedText)
