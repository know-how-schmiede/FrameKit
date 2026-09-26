"""Add-in lifecycle: never open STEP documents during Fusion initialization."""
from . import commands, bracket_library
from .lib import fusionAddInUtils as futil

_startup_app = None
_startup_handler = None
_started = False


def _detach_startup():
    global _startup_app, _startup_handler
    if _startup_handler is not None:
        _startup_app.startupCompleted.remove(_startup_handler)
    _startup_handler = None
    _startup_app = None


def _initialize(app):
    global _started
    if _started:
        return
    _started = True  # Prevent re-entry from document events during STEP imports.
    try:
        app.log('FrameKit: initialization after Fusion startup')
        bracket_library.prepare(app)
        commands.start()
        app.log('FrameKit: initialization complete')
    except Exception:
        _started = False
        futil.handle_error('FrameKit starten', show_message_box=True)


def run(context):
    global _startup_app, _startup_handler, _started
    try:
        import adsk.core
        _detach_startup()
        _started = False
        app = adsk.core.Application.get()
        if app.isStartupComplete:
            _initialize(app)
        else:
            def completed(args):
                _detach_startup()
                _initialize(app)
            _startup_app = app
            _startup_handler = futil.add_handler(app.startupCompleted, completed)
            app.log('FrameKit: waiting for Fusion startupCompleted')
    except Exception:
        futil.handle_error('FrameKit starten', show_message_box=True)


def stop(context):
    global _started
    try:
        _detach_startup()
        futil.clear_handlers()
        if _started:
            commands.stop()
        _started = False
    except Exception:
        futil.handle_error('FrameKit stoppen')
