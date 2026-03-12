"""Built-in plugin that inserts root syntax and exposes the root helper."""

from calculator.expression import root
from calculator.plugin_api import CalcPlugin


def register() -> CalcPlugin:
    """Return the built-in root plugin definition."""
    return CalcPlugin(
        label="Xroot(Y)",
        insert="root(",
        name="root",
        handler=root,
    )