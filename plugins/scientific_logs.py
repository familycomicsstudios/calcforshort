"""Built-in plugin group for logarithmic functions."""

from calculator.expression import calc_ln, calc_log, logn
from calculator.plugin_api import CalcPlugin


PLUGIN_NAME = "Scientific Logs"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Base-10, natural, and arbitrary-base logarithms."
PLUGIN_AUTHOR = "Calcforshort"
PLUGIN_SIMPLICITY = 40


def register() -> list[CalcPlugin]:
    """Return grouped plugins for logarithmic functions."""
    return [
        CalcPlugin(label="log(", insert="log(", name="log", handler=calc_log, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY),
        CalcPlugin(label="ln(", insert="ln(", name="ln", handler=calc_ln, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY),
        CalcPlugin(label="logN(X)", insert="log", name="logn", handler=logn, plugin_name=PLUGIN_NAME, plugin_version=PLUGIN_VERSION, plugin_description=PLUGIN_DESCRIPTION, plugin_author=PLUGIN_AUTHOR, plugin_simplicity=PLUGIN_SIMPLICITY),
    ]
