"""Built-in plugin that inserts subtraction syntax."""

from calculator.plugin_api import CalcPlugin


def register() -> CalcPlugin:
    """Return the built-in subtraction plugin definition."""
    return CalcPlugin(label="-", insert=" - ")