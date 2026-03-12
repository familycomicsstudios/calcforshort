"""Built-in plugin that inserts division syntax."""

from calculator.plugin_api import CalcPlugin


def register() -> CalcPlugin:
    """Return the built-in division plugin definition."""
    return CalcPlugin(label="/", insert=" / ")