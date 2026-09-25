"""Drive command events with UI/graphics doubles; no running Fusion required."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

from fusion_addin.FrameKit import accessories, demo
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
    def selectedItem(self):
        return next((item for item in self.listItems.items if item.isSelected), None)


class Inputs:
    def __init__(self, registry):
        self.registry = registry

    def add(self, identifier, name, **values):
        result = Control(id=identifier, name=name, isVisible=True, isEnabled=True,
                         isValidExpression=True, **values)
        self.registry[identifier] = result
        return result

    def addTabCommandInput(self, identifier, name, *args):
        return self.add(identifier, name, children=Inputs(self.registry))

    addGroupCommandInput = addTabCommandInput

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
            event.callback = callback
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
        library = deepcopy(accessories.PRESETS)
        for name, value in (('load', (deepcopy(demo.DEFAULTS), '')), ('load_library', (library, ''))):
            patcher = patch.object(self.entry.settings, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        save = patch.object(self.entry.settings, 'save')
        self.save_defaults = save.start()
        self.addCleanup(save.stop)
        self.controls = {}
        self.command = NS(commandInputs=Inputs(self.controls), setDialogInitialSize=Mock(),
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
        self.assertEqual(len(self.graphics.groups[0].entities), 1)
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
        self.assertEqual(sum(':cross:' in p['key'] for p in calculated['parts']), 6)
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
