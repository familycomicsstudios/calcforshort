"""Built-in plugin group for default constants like pi and e."""

import math

from calculator.plugin_api import CalcPlugin


def register() -> list[CalcPlugin]:
    """Return default constants as namespace entries and visible buttons."""
    meta = {
        "plugin_name": "Constants",
        "plugin_version": "1.0.0",
        "plugin_description": "Provides default constants such as pi and e.",
        "plugin_author": "Calcforshort",
        "plugin_simplicity": 30,
        "show_button": True,
    }
    return [
        CalcPlugin(label="π", insert="pi", name="pi", handler=math.pi, **meta),
        CalcPlugin(label="e", insert="e", name="e", handler=math.e, **meta),
        CalcPlugin(label="τ", insert="tau", name="tau", handler=math.tau, **meta),
        CalcPlugin(label="∞", insert="inf", name="inf", handler=math.inf, **meta),
        CalcPlugin(label="NaN", insert="nan", name="nan", handler=math.nan, **meta),
    ]