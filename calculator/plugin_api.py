"""Plugin protocol objects exposed to third-party calculator plugins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CalcPlugin:
    """A plugin contributing a button and optionally a function to the evaluator namespace.

    label:   Text shown on the button.
    insert:  Text inserted into the expression when the button is clicked.
    name:    Identifier used in expressions (e.g. ``sin``). Leave empty for
             pure operator/syntax buttons that rely on Python operators.
    handler: Object added to the eval namespace under ``name`` (callable or value).
    """

    label: str
    insert: str
    name: str = ""
    handler: Any | None = None
    show_button: bool = True
    plugin_name: str = ""
    plugin_version: str = "1.0.0"
    plugin_description: str = ""
    plugin_author: str = ""