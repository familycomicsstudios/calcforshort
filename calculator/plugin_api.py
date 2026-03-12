from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class CalcPlugin:
    """A plugin contributing a button and optionally a function to the evaluator namespace.

    label:   Text shown on the button.
    insert:  Text inserted into the expression when the button is clicked.
    name:    Identifier used in expressions (e.g. ``sin``). Leave empty for
             pure operator/syntax buttons that rely on Python operators.
    handler: Python callable added to the eval namespace under ``name``.
    """

    label: str
    insert: str
    name: str = ""
    handler: Callable[..., Any] | None = None