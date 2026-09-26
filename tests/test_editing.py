from copy import deepcopy
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

from fusion_addin.FrameKit import demo, editing, model
import test_geometry_adapter as geometry_tests
from test_geometry_adapter import Design, Matrix
from test_sections import rectangle


class StoredConfigurationTests(unittest.TestCase):
    def test_legacy_defaults_migrate_without_adding_brackets(self):
        legacy = {k: demo.DEFAULTS[k] for k in ('length', 'width', 'height', 'profile', 'bottom')}
        values, calculated = editing.decode(legacy=json.dumps(legacy), assembly_id='legacy-id')
        self.assertEqual(values['shelf_count'], 0)
        self.assertFalse(values['brackets'])
        self.assertEqual(calculated['assembly_id'], 'legacy-id')

    def test_snapshot_ids_and_removed_level_ids_survive(self):
        values = dict(demo.DEFAULTS, shelf_count=2, shelf_heights=[250, 500])
        first = model.build_model(values)
        loaded, previous = editing.decode(json.dumps(dict(schema=1, values=values)),
            model_data=json.dumps(first), assembly_id=first['assembly_id'])
        reduced = model.build_model(dict(loaded, shelf_count=1, shelf_heights=[250]), previous)
        restored = model.build_model(loaded, reduced)
        self.assertEqual(restored['id_registry'], first['id_registry'])
        self.assertEqual(restored['assembly_id'], first['assembly_id'])

    def test_unknown_schema_corruption_and_mismatches_are_rejected(self):
        for raw in ('{', '{}', '{"schema": 2, "values": {}}',
                    '{"schema": 1, "values": null}', '{"schema": 1, "values": {}}'):
            with self.assertRaises(ValueError):
                editing.decode(configuration=raw)
        data = model.build_model(demo.DEFAULTS)
        for previous in (dict(data, schema=77), dict(data, id_registry={'one': 'invalid'}),
                         dict(data, configuration={}), dict(data, assembly_id='other')):
            with self.assertRaises(ValueError):
                editing.decode(json.dumps(dict(schema=1, values=demo.DEFAULTS)),
                               model_data=json.dumps(previous), assembly_id=data['assembly_id'])

    def test_embedded_dxf_is_usable_without_original_file(self):
        with tempfile.TemporaryDirectory() as folder:
            profile = rectangle(folder, 30, 30)
        values = dict(demo.DEFAULTS, profile=30, profile_definition=profile)
        data = model.build_model(values)
        loaded, result = editing.decode(json.dumps(dict(schema=1, values=values)),
                                       model_data=json.dumps(data))
        self.assertEqual(loaded['profile_definition'], profile)
        self.assertEqual(result['profiles'], data['profiles'])

    def test_translated_rotated_preview_leaves_saved_model_local(self):
        data = model.build_model(demo.DEFAULTS)
        original = deepcopy(data)
        transform = Matrix()
        transform.setWithCoordinateSystem((100, 20, 3), (0, 1, 0), (-1, 0, 0), (0, 0, 1))
        result = editing.preview_model(data, transform)
        self.assertEqual(data, original)
        for before, after in zip(data['parts'], result['parts']):
            x, y, z = before['position_mm']
            self.assertEqual(after['position_mm'], [1000-y, 200+x, 30+z])
            self.assertEqual(after['bounds_mm'], [before['bounds_mm'][1],
                                                 before['bounds_mm'][0], before['bounds_mm'][2]])


class RebuildTests(unittest.TestCase):
    setUp = geometry_tests.GeometryAdapterTests.setUp

    def replace(self, context, values, calculated):
        with patch.dict(sys.modules, {'fusion_addin.FrameKit.geometry': self.adapter}):
            return editing.replace(context, values, calculated)

    def test_replace_only_selected_frame_preserving_ids_and_placement(self):
        for parametric in (True, False):
            design = Design(parametric)
            first = self.adapter.create_frame(design, demo.DEFAULTS)
            second = self.adapter.create_frame(design, dict(demo.DEFAULTS, length=1200))
            first.transform2.origin = (100, 0, 0)
            first.isLightBulbOn = False
            context = editing.load(design, first)
            values = dict(context['values'], length=900)
            data = model.build_model(values, context['model'])
            rebuilt = self.replace(context, values, data)
            self.assertEqual(design.rootComponent.children, [second, rebuilt])
            self.assertEqual(rebuilt.transform2.origin, (100, 0, 0))
            self.assertFalse(rebuilt.isLightBulbOn)
            self.assertEqual(data['id_registry'], context['model']['id_registry'])
            self.assertEqual(json.loads(editing.attribute(rebuilt.component, 'modelData')), data)
            self.assertEqual(len(editing.frames(design)), 2)
            editing.load(design, rebuilt)  # The replacement must itself remain editable.
            self.assertFalse(first.isValid)  # Delete old construction, not a Remove feature.

    def test_direct_brackets_are_populated_at_origin_before_placement_on_repeated_edits(self):
        from fusion_addin.FrameKit import bracket_library
        from test_geometry_adapter import Component
        design = Design(False)
        source = object()
        original_add = Component.add_body
        imports = []

        def add_at_origin(component, body, feature=None):
            self.assertIsNone(feature)
            # Every ancestor and bracket instance must still be unplaced at import.
            def visit(parent, ancestors):
                for occurrence in parent.children:
                    chain = ancestors + [occurrence]
                    if occurrence.component is component:
                        for entry in chain:
                            self.assertEqual(entry.transform2.asArray(), Matrix().asArray())
                        imports.append(component)
                    visit(occurrence.component, chain)
            visit(design.rootComponent, [])
            return original_add(component, body, feature)

        with patch.object(bracket_library, 'body', return_value=source), \
                patch.object(Component, 'add_body', add_at_origin):
            values = dict(demo.DEFAULTS, brackets=True, shelf_count=1, shelf_heights=[300],
                          cross_members={'top': {'count': 1, 'direction': 'quer'}})
            frame = self.adapter.create_frame(design, values)
            placement = Matrix()
            placement.setWithCoordinateSystem((100, 20, 5), (0, 1, 0), (-1, 0, 0), (0, 0, 1))
            frame.transform2 = placement
            for length in (1200, 600):
                context = editing.load(design, frame)
                values = dict(context['values'], length=length)
                data = model.build_model(values, context['model'])
                frame = self.replace(context, values, data)
                self.assertEqual(frame.transform2.asArray(), placement.asArray())
                group = next(g.component for g in frame.component.children
                             if editing.attribute(g.component, 'groupId') == 'connections')
                parts = [p for p in data['parts'] if p['kind'] == 'connection']
                self.assertEqual(len(group.children), len(parts))
                self.assertEqual(len({id(o.component) for o in group.children}), len(parts))
                for occurrence in group.children:
                    part = next(p for p in parts if p['id'] == editing.attribute(occurrence, 'partId'))
                    self.assertEqual(occurrence.transform2.asArray(), Matrix().asArray())
                    solid = occurrence.component.imported[0]
                    self.assertIs(solid.source, source)
                    self.assertEqual(solid.placement.origin, tuple(v/10 for v in part['position_mm']))
                    self.assertEqual(solid.placement.axes, tuple(tuple(a) for a in part['orientation']))
            self.assertEqual(len(imports), 3 * len(parts))

    def test_failed_build_keeps_original_and_other_frames(self):
        design = Design()
        old = self.adapter.create_frame(design, demo.DEFAULTS)
        foreign = design.rootComponent.add_component(Matrix())
        context = editing.load(design, old)
        before = deepcopy(old.component.attributes)
        design.fail_extrude = True
        with self.assertRaises(RuntimeError):
            self.replace(context, context['values'], context['model'])
        self.assertEqual(design.rootComponent.children, [old, foreign])
        self.assertEqual(old.component.attributes, before)

    def test_foreign_children_shared_and_changed_frames_block_edit(self):
        design = Design()
        old = self.adapter.create_frame(design, demo.DEFAULTS)
        context = editing.load(design, old)
        extra = old.component.children[0].component.add_component(Matrix())
        with self.assertRaisesRegex(ValueError, 'fremde Komponente'):
            editing.load(design, old)
        extra.deleteMe()
        clone = design.rootComponent.add_existing(old.component, Matrix())
        with self.assertRaisesRegex(ValueError, 'Mehrfach'):
            editing.load(design, old)
        clone.deleteMe()
        old.transform2.origin = (2, 0, 0)
        with self.assertRaisesRegex(ValueError, 'verschoben'):
            editing.check_current(context)
        old.transform2.origin = (0, 0, 0)
        old.component.attributes.add('FrameKit', 'configuration', '{}')
        with self.assertRaisesRegex(ValueError, 'geändert'):
            editing.check_current(context)

    def test_delete_failure_keeps_old_frame_until_command_transaction_aborts(self):
        design = Design()
        old = self.adapter.create_frame(design, demo.DEFAULTS)
        context = editing.load(design, old)
        with patch.object(old, 'deleteMe', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'ersetzt'):
                self.replace(context, context['values'], context['model'])
        self.assertTrue(old.isValid)
        self.assertIn(old, design.rootComponent.children)
        # The command's executeFailed abort restores the rest of this transaction.

    def test_step_occurrences_are_recognized_as_owned(self):
        from fusion_addin.FrameKit import bracket_library
        design = Design()
        with patch.object(bracket_library, 'body', return_value=object()):
            old = self.adapter.create_frame(design, dict(demo.DEFAULTS, brackets=True))
        self.assertTrue(editing.load(design, old)['values']['brackets'])
