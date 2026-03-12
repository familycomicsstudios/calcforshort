"""Built-in plugin that inserts multiplication syntax."""

from calculator.plugin_api import CalcPlugin


def register() -> CalcPlugin:
    """Return the built-in multiplication plugin definition."""
    return CalcPlugin(label="*", insert=" * ")