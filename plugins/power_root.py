"""Built-in plugin group for exponent and root helpers."""

from calculator.expression import root
from calculator.plugin_api import CalcPlugin


def register() -> list[CalcPlugin]:
    """Return grouped plugins for power and root syntax."""
    return [
        CalcPlugin(
            label="X^Y",
            insert="^",
            plugin_name="Power Root",
            plugin_version="1.0.0",
            plugin_description="Exponent shorthand operator.",
            plugin_author="Calcforshort",
        ),
        CalcPlugin(
            label="Xroot(Y)",
            insert="root(",
            name="root",
            handler=root,
            plugin_name="Power Root",
            plugin_version="1.0.0",
            plugin_description="Nth-root helper function.",
            plugin_author="Calcforshort",
        ),
    ]