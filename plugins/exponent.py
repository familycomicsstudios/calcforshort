"""Built-in plugin that inserts exponent syntax."""

from calculator.plugin_api import CalcPlugin


def register() -> CalcPlugin:
    """Return the built-in exponent plugin definition."""
    return CalcPlugin(label="X^Y", insert="^")