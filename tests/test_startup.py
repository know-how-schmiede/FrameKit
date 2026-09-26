import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch


class StartupTests(unittest.TestCase):
    def setUp(self):
        prefix = 'fusion_addin.FrameKit'
        self.commands = NS(start=Mock(), stop=Mock())
        self.library = NS(prepare=Mock())
        self.utilities = NS(add_handler=Mock(side_effect=lambda event, callback: callback),
                            clear_handlers=Mock(), handle_error=Mock())
        self.app = NS(isStartupComplete=False, startupCompleted=NS(remove=Mock()), log=Mock())
        core = ModuleType('adsk.core'); core.Application=NS(get=lambda:self.app)
        adsk = ModuleType('adsk'); adsk.core=core
        self.patch = patch.dict(sys.modules, {'adsk':adsk, 'adsk.core':core,
            prefix+'.commands':self.commands, prefix+'.bracket_library':self.library,
            prefix+'.lib.fusionAddInUtils':self.utilities})
        self.patch.start(); self.addCleanup(self.patch.stop)
        import fusion_addin.FrameKit as package
        self.attrs = patch.multiple(package, commands=self.commands, bracket_library=self.library, create=True)
        self.attrs.start(); self.addCleanup(self.attrs.stop)
        spec=importlib.util.spec_from_file_location(prefix+'.lifecycle_test',
            Path(__file__).resolve().parents[1]/'fusion_addin/FrameKit/FrameKit.py')
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)

    def test_automatic_start_defers_import_until_fusion_ready_and_runs_once(self):
        self.module.run({})
        self.library.prepare.assert_not_called();self.commands.start.assert_not_called()
        callback=self.utilities.add_handler.call_args.args[1]
        self.app.isStartupComplete=True
        callback(None);callback(None)
        self.library.prepare.assert_called_once_with(self.app)
        self.commands.start.assert_called_once()
        self.app.startupCompleted.remove.assert_called_once_with(callback)

    def test_manual_activation_initializes_immediately(self):
        self.app.isStartupComplete=True
        self.module.run({})
        self.library.prepare.assert_called_once_with(self.app)
        self.commands.start.assert_called_once()
        self.utilities.add_handler.assert_not_called()

    def test_stop_before_startup_detaches_pending_handler(self):
        self.module.run({})
        callback=self.utilities.add_handler.call_args.args[1]
        self.module.stop({})
        self.app.startupCompleted.remove.assert_called_once_with(callback)
        self.library.prepare.assert_not_called()
        self.commands.stop.assert_not_called()
