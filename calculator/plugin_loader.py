from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, List

from calculator.plugin_api import CalcPlugin


@dataclass(frozen=True)
class LoadedPlugin:
    plugin_id: str
    label: str
    insert: str
    name: str
    handler: Callable[..., Any] | None

    def namespace_entry(self) -> tuple[str, Callable[..., Any]] | None:
        """Return (name, callable) to add to the eval namespace, or None."""
        if self.name and self.handler is not None:
            return (self.name, self.handler)
        return None


def _normalize_registered_plugins(registered: object) -> list[CalcPlugin]:
    if registered is None:
        return []
    if isinstance(registered, list):
        return registered
    return [registered]


def _load_plugin_from_module(module: ModuleType) -> list[LoadedPlugin]:
    register = getattr(module, "register", None)
    if register is None:
        return []

    loaded = _normalize_registered_plugins(register())
    plugins: list[LoadedPlugin] = []
    for index, plugin in enumerate(loaded):
        if not hasattr(plugin, "label") or not hasattr(plugin, "insert"):
            raise TypeError(
                f"Plugin from module {module.__name__!r} must define 'label' and 'insert'."
            )
        plugin_id = f"{module.__name__}:{index}"
        plugins.append(
            LoadedPlugin(
                plugin_id=plugin_id,
                label=plugin.label,
                insert=plugin.insert,
                name=getattr(plugin, "name", ""),
                handler=getattr(plugin, "handler", None),
            )
        )
    return plugins


def load_plugins(package_name: str = "plugins") -> List[LoadedPlugin]:
    package = importlib.import_module(package_name)
    discovered: list[LoadedPlugin] = []

    for module_info in pkgutil.iter_modules(package.__path__, prefix=f"{package_name}."):
        if module_info.ispkg:
            continue
        module = importlib.import_module(module_info.name)
        discovered.extend(_load_plugin_from_module(module))

    return sorted(discovered, key=lambda p: (p.label, p.name, p.plugin_id))