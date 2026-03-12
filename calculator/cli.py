"""Command-line interface for Calcforshort."""

from __future__ import annotations

import sys

from calculator.api import calculate, get_plugins
from calculator.expression import ExpressionError, format_result


def run_cli(expression: str | None = None) -> int:
    """Run the calculator in interactive or one-shot CLI mode."""
    try:
        plugins = get_plugins()
    except Exception as error:
        print(f"Plugin error: {error}", file=sys.stderr)
        return 1

    if expression is not None:
        return _print_calculation(expression, plugins)

    print("Calcforshort: The Extensible Calculator App")
    print("Type an expression, or 'quit' to exit.")
    while True:
        try:
            line = input("calc> ").strip()
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            return 0

        if not line:
            continue
        if line.lower() in {"quit", "exit"}:
            return 0

        _print_calculation(line, plugins)


def _print_calculation(expression: str, plugins: list) -> int:
    """Evaluate *expression* and print the formatted result to stdout."""
    try:
        result = calculate(expression, plugins=plugins)
    except (ExpressionError, ZeroDivisionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(format_result(result))
    return 0