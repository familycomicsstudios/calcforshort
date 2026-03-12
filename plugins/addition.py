from calculator.plugin_api import CalcPlugin


def register() -> CalcPlugin:
    return CalcPlugin(label="+", insert=" + ")