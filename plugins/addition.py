"""Built-in plugin that inserts addition syntax."""

from calculator.plugin_api import CalcPlugin


def register() -> CalcPlugin:
    """Return the built-in addition plugin definition."""
    return CalcPlugin(label="+", insert=" + ")