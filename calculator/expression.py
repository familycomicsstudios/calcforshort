from __future__ import annotations

import math
from typing import Any


# Safe base namespace available in every expression.
BASE_NAMESPACE: dict[str, Any] = {
    "__builtins__": {},
    # basic built-ins
    "abs": abs,
    "round": round,
    "int": int,
    "float": float,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    # trigonometry
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "degrees": math.degrees,
    "radians": math.radians,
    # algebra / general
    "sqrt": math.sqrt,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
    "gcd": math.gcd,
    "lcm": getattr(math, "lcm", None),  # Python 3.9+
    "hypot": math.hypot,
    # constants
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    "nan": math.nan,
}
# Drop None entries (functions unavailable on older Python)
BASE_NAMESPACE = {k: v for k, v in BASE_NAMESPACE.items() if v is not None}


class ExpressionError(ValueError):
    pass


def evaluate_expression_string(
    expression: str,
    extra_namespace: dict[str, Any] | None = None,
) -> Any:
    """Evaluate an expression string using Python eval.

    Semicolons separate statements: all but the last are executed as
    assignments (``exec``), the last is evaluated as an expression.
    Plugins can inject additional callables via *extra_namespace*.
    """
    if not expression.strip():
        raise ExpressionError("Enter an expression before calculating.")

    namespace: dict[str, Any] = dict(BASE_NAMESPACE)
    if extra_namespace:
        namespace.update(extra_namespace)

    parts = [p.strip() for p in expression.split(";")]
    parts = [p for p in parts if p]

    # Execute all leading statements so their bindings are in scope.
    for stmt in parts[:-1]:
        try:
            exec(stmt, namespace)  # noqa: S102
        except SyntaxError as error:
            msg = getattr(error, "msg", str(error))
            raise ExpressionError(f"Syntax error: {msg}") from error
        except ZeroDivisionError:
            raise
        except Exception as error:
            raise ExpressionError(f"Evaluation error: {error}") from error

    try:
        result = eval(parts[-1], namespace)  # noqa: S307
    except SyntaxError as error:
        msg = getattr(error, "msg", str(error))
        raise ExpressionError(f"Syntax error: {msg}") from error
    except ZeroDivisionError:
        raise
    except NameError as error:
        raise ExpressionError(str(error)) from error
    except TypeError as error:
        raise ExpressionError(str(error)) from error
    except (ArithmeticError, ValueError) as error:
        raise ExpressionError(str(error)) from error
    except Exception as error:
        raise ExpressionError(f"Evaluation error: {error}") from error

    return result


def format_result(value: Any) -> str:
    """Format any result value for display."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        try:
            if value == int(value):
                return str(int(value))
        except (ValueError, OverflowError):
            pass
        return str(value)
    if isinstance(value, str):
        return repr(value)
    return repr(value)