"""Built-in plugin group for trigonometric functions."""

from calculator.expression import trig_acos, trig_asin, trig_atan, trig_cos, trig_sin, trig_tan
from calculator.plugin_api import CalcPlugin


def register() -> list[CalcPlugin]:
    """Return grouped plugins for common trig functions."""
    return [
        CalcPlugin(
            label="sin(",
            insert="sin(",
            name="sin",
            handler=trig_sin,
            plugin_name="Trigonometry",
            plugin_version="1.0.0",
            plugin_description="Sine function.",
            plugin_author="Calcforshort",
        ),
        CalcPlugin(
            label="cos(",
            insert="cos(",
            name="cos",
            handler=trig_cos,
            plugin_name="Trigonometry",
            plugin_version="1.0.0",
            plugin_description="Cosine function.",
            plugin_author="Calcforshort",
        ),
        CalcPlugin(
            label="tan(",
            insert="tan(",
            name="tan",
            handler=trig_tan,
            plugin_name="Trigonometry",
            plugin_version="1.0.0",
            plugin_description="Tangent function.",
            plugin_author="Calcforshort",
        ),
        CalcPlugin(
            label="asin(",
            insert="asin(",
            name="asin",
            handler=trig_asin,
            plugin_name="Trigonometry",
            plugin_version="1.0.0",
            plugin_description="Inverse sine function.",
            plugin_author="Calcforshort",
        ),
        CalcPlugin(
            label="acos(",
            insert="acos(",
            name="acos",
            handler=trig_acos,
            plugin_name="Trigonometry",
            plugin_version="1.0.0",
            plugin_description="Inverse cosine function.",
            plugin_author="Calcforshort",
        ),
        CalcPlugin(
            label="atan(",
            insert="atan(",
            name="atan",
            handler=trig_atan,
            plugin_name="Trigonometry",
            plugin_version="1.0.0",
            plugin_description="Inverse tangent function.",
            plugin_author="Calcforshort",
        ),
    ]