"""Plugin discovery and normalization for calculator extensions."""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from types import ModuleType
from typing import Any, List

from calculator.plugin_api import CalcPlugin


@dataclass(frozen=True)
class LoadedPlugin:
    """Runtime representation of a discovered calculator plugin."""

    plugin_id: str
    label: str
    insert: str
    name: str
    handler: Any | None
    show_button: bool
    plugin_name: str
    plugin_version: str
    plugin_description: str
    plugin_author: str
    plugin_simplicity: int

    def namespace_entry(self) -> tuple[str, Any] | None:
        """Return ``(name, value)`` to add to the eval namespace, or None."""
        if self.name and self.handler is not None:
            return (self.name, self.handler)
        return None


def _normalize_registered_plugins(registered: object) -> list[CalcPlugin]:
    """Normalize a plugin module's register result into a list."""
    if registered is None:
        return []
    if isinstance(registered, list):
        return registered
    return [registered]


def _load_plugin_from_module(module: ModuleType) -> list[LoadedPlugin]:
    """Load and validate plugin definitions exposed by *module*."""
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
                show_button=bool(getattr(plugin, "show_button", True)),
                plugin_name=getattr(plugin, "plugin_name", module.__name__.rsplit(".", 1)[-1]),
                plugin_version=getattr(plugin, "plugin_version", "1.0.0"),
                plugin_description=getattr(plugin, "plugin_description", ""),
                plugin_author=getattr(plugin, "plugin_author", ""),
                plugin_simplicity=int(getattr(plugin, "plugin_simplicity", 100)),
            )
        )
    return plugins


def load_plugins(package_name: str = "plugins") -> List[LoadedPlugin]:
    """Discover, load, and sort plugins from *package_name*."""
    package = importlib.import_module(package_name)
    discovered: list[LoadedPlugin] = []

    for module_info in pkgutil.iter_modules(package.__path__, prefix=f"{package_name}."):
        if module_info.ispkg:
            continue
        module = importlib.import_module(module_info.name)
        discovered.extend(_load_plugin_from_module(module))

    return sorted(
        discovered,
        key=lambda p: (p.plugin_simplicity, p.plugin_name.lower(), p.label, p.name, p.plugin_id),
    )