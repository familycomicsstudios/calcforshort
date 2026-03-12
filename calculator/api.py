from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from calculator.expression import evaluate_expression_string
from calculator.plugin_loader import LoadedPlugin, load_plugins


def get_plugins(package_name: str = "plugins") -> list[LoadedPlugin]:
    return load_plugins(package_name)


def calculate(
    expression: str,
    plugins: Sequence[LoadedPlugin] | None = None,
    enabled_plugin_ids: Iterable[str] | None = None,
    package_name: str = "plugins",
) -> Any:
    loaded_plugins = list(plugins) if plugins is not None else load_plugins(package_name)
    enabled_ids = set(enabled_plugin_ids) if enabled_plugin_ids is not None else None

    extra_namespace: dict[str, object] = {}
    for plugin in loaded_plugins:
        if enabled_ids is None or plugin.plugin_id in enabled_ids:
            entry = plugin.namespace_entry()
            if entry is not None:
                extra_namespace[entry[0]] = entry[1]

    return evaluate_expression_string(expression, extra_namespace)