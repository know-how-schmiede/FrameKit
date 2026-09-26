"""Consistent read-only Fusion status text; never interpret user text as HTML."""
from html import escape

STYLES = {
    'error': ('Fehler', '#B71C1C', '#FFF3F3'),
    'warning': ('Hinweis', '#854700', '#FFF4DB'),
}


def set_status(control, message='', severity='info'):
    text = escape(str(message)).replace('\n', '<br>') if message else ''
    if text and severity in STYLES:
        label, color, background = STYLES[severity]
        text = (f'<span style="color:{color}; background-color:{background};">'
                f'<b>{label}:</b> {text}</span>')
    set_if_changed(control, 'formattedText', text)


def set_if_changed(control, property_name, value):
    """Avoid redundant native UI writes, which can disturb an active text editor."""
    if getattr(control, property_name) != value:
        setattr(control, property_name, value)
