"""Built-in plugin group for common scientific functions."""

import math

from calculator.plugin_api import CalcPlugin


PLUGIN_NAME = "Scientific Functions"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Common scientific helpers such as sqrt, exp, factorial, and combinatorics."
PLUGIN_AUTHOR = "Calcforshort"
PLUGIN_SIMPLICITY = 50


def register() -> list[CalcPlugin]:
    """Return grouped plugins for scientific helper functions."""
    plugins = [
        CalcPlugin(label="factorial(", insert="factorial(", name="factorial", handler=math.factorial, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY),
        CalcPlugin(label="ceil(", insert="ceil(", name="ceil", handler=math.ceil, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY),
        CalcPlugin(label="floor(", insert="floor(", name="floor", handler=math.floor, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY),
        CalcPlugin(label="hypot(", insert="hypot(", name="hypot", handler=math.hypot, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY),
    ]

    if hasattr(math, "comb"):
        plugins.append(CalcPlugin(label="comb(", insert="comb(", name="comb", handler=math.comb, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY))
    if hasattr(math, "perm"):
        plugins.append(CalcPlugin(label="perm(", insert="perm(", name="perm", handler=math.perm, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY))
    return plugins
