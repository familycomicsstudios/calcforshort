"""Built-in plugin group for the four core arithmetic operators."""

from calculator.plugin_api import CalcPlugin


def register() -> list[CalcPlugin]:
    """Return plugins for +, -, *, and /."""
    simplicity = 10
    return [
        CalcPlugin(
            label="+",
            insert=" + ",
            plugin_name="Core Arithmetic",
            plugin_version="1.0.0",
            plugin_description="Addition operator.",
            plugin_author="Calcforshort",
            plugin_simplicity=simplicity,
        ),
        CalcPlugin(
            label="-",
            insert=" - ",
            plugin_name="Core Arithmetic",
            plugin_version="1.0.0",
            plugin_description="Subtraction operator.",
            plugin_author="Calcforshort",
            plugin_simplicity=simplicity,
        ),
        CalcPlugin(
            label="*",
            insert=" * ",
            plugin_name="Core Arithmetic",
            plugin_version="1.0.0",
            plugin_description="Multiplication operator.",
            plugin_author="Calcforshort",
            plugin_simplicity=simplicity,
        ),
        CalcPlugin(
            label="/",
            insert=" / ",
            plugin_name="Core Arithmetic",
            plugin_version="1.0.0",
            plugin_description="Division operator.",
            plugin_author="Calcforshort",
            plugin_simplicity=simplicity,
        ),
    ]