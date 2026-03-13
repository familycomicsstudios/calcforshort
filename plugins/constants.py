"""Built-in plugin group for default constants like pi and e."""

import math

from calculator.plugin_api import CalcPlugin


def register() -> list[CalcPlugin]:
    """Return namespace-only constants provided by a plugin group."""
    meta = {
        "plugin_name": "Constants",
        "plugin_version": "1.0.0",
        "plugin_description": "Provides default constants such as pi and e.",
        "plugin_author": "Calcforshort",
        "show_button": False,
    }
    return [
        CalcPlugin(label="", insert="", name="pi", handler=math.pi, **meta),
        CalcPlugin(label="", insert="", name="e", handler=math.e, **meta),
        CalcPlugin(label="", insert="", name="tau", handler=math.tau, **meta),
        CalcPlugin(label="", insert="", name="inf", handler=math.inf, **meta),
        CalcPlugin(label="", insert="", name="nan", handler=math.nan, **meta),
    ]