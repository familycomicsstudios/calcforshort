"""Expression evaluation helpers for Calcforshort.

The evaluator uses a restricted Python namespace containing selected built-in
functions, math helpers, and any plugin-provided callables.
"""

from __future__ import annotations

import ast
import math
import re
import sys
from typing import Any


# Safe base namespace available in every expression.
BASE_NAMESPACE: dict[str, Any] = {
    "__builtins__": {},
    # basic built-ins
    "abs": abs,
    "round": round,
    "int": int,
    "float": float,
    "bool": bool,
    "str": str,
    "list": list,
    "tuple": tuple,
    "dict": dict,
    "set": set,
    "frozenset": frozenset,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "any": any,
    "all": all,
    "sorted": sorted,
    "reversed": reversed,
    "zip": zip,
    "map": map,
    "filter": filter,
    "enumerate": enumerate,
    "tuple": tuple,
    "dict": dict,
    "set": set,
    "frozenset": frozenset,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "any": any,
    "all": all,
    "sorted": sorted,
    "reversed": reversed,
    "zip": zip,
    "map": map,
    "filter": filter,
    "enumerate": enumerate,
    "pow": pow,
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
}
# Drop None entries (functions unavailable on older Python)
BASE_NAMESPACE = {k: v for k, v in BASE_NAMESPACE.items() if v is not None}
MAX_FLOAT = sys.float_info.max
# Floats can represent values up to just under 2**max_exp.
# Any integer power whose result exceeds that many bits is Inf.
_FLOAT_MAX_EXP: int = sys.float_info.max_exp  # 1024 on all standard platforms
_ANGLE_MODE = "radian"


def set_angle_mode(mode: str) -> None:
    """Set trig angle mode to ``radian`` or ``degree``."""
    normalized = mode.strip().lower()
    if normalized not in {"radian", "degree"}:
        raise ValueError("Angle mode must be 'radian' or 'degree'.")
    global _ANGLE_MODE
    _ANGLE_MODE = normalized


def get_angle_mode() -> str:
    """Return the currently configured trig angle mode."""
    return _ANGLE_MODE


def _to_radians(value: float) -> float:
    """Convert an input angle to radians when degree mode is active."""
    return math.radians(value) if _ANGLE_MODE == "degree" else value


def _from_radians(value: float) -> float:
    """Convert a radian output angle to current mode units."""
    return math.degrees(value) if _ANGLE_MODE == "degree" else value


def _snap_trig_output(value: float) -> float:
    """Snap tiny floating-point trig noise to expected canonical values."""
    epsilon = 1e-12
    if abs(value) < epsilon:
        return 0.0
    if abs(value - 1.0) < epsilon:
        return 1.0
    if abs(value + 1.0) < epsilon:
        return -1.0
    return value


def trig_sin(value: Any) -> Any:
    """Sine honoring the configured angle mode."""
    result = math.sin(_to_radians(float(value)))
    return _sanitize_result(_snap_trig_output(result))


def trig_cos(value: Any) -> Any:
    """Cosine honoring the configured angle mode."""
    result = math.cos(_to_radians(float(value)))
    return _sanitize_result(_snap_trig_output(result))


def trig_tan(value: Any) -> Any:
    """Tangent honoring the configured angle mode."""
    result = math.tan(_to_radians(float(value)))
    return _sanitize_result(_snap_trig_output(result))


def trig_asin(value: Any) -> Any:
    """Inverse sine honoring the configured angle mode."""
    return _sanitize_result(_from_radians(math.asin(float(value))))


def trig_acos(value: Any) -> Any:
    """Inverse cosine honoring the configured angle mode."""
    return _sanitize_result(_from_radians(math.acos(float(value))))


def trig_atan(value: Any) -> Any:
    """Inverse tangent honoring the configured angle mode."""
    return _sanitize_result(_from_radians(math.atan(float(value))))


class ExpressionError(ValueError):
    """Raised when a user expression cannot be parsed or evaluated."""

    pass


def _sanitize_result(value: Any) -> Any:
    """Convert unsupported or unbounded results into calculator-friendly values."""
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if abs(value) > MAX_FLOAT:
            return math.inf if value > 0 else -math.inf
        return value

    if isinstance(value, float):
        return value

    if isinstance(value, complex):
        if value.imag == 0:
            return _sanitize_result(value.real)
        return math.nan

    if isinstance(value, str):
        return value

    if callable(value):
        return value

    # Pass through collections, None, and any other type unchanged.
    return value


def safe_div(left: Any, right: Any) -> Any:
    """Divide ``left`` by ``right`` and return infinities or NaN on zero division."""
    try:
        return _sanitize_result(left / right)
    except ZeroDivisionError:
        if left == 0:
            return math.nan

        right_sign = -1.0 if isinstance(right, float) and math.copysign(1.0, right) < 0 else 1.0
        left_sign = -1.0 if left < 0 else 1.0
        return math.inf if left_sign * right_sign > 0 else -math.inf


def safe_floordiv(left: Any, right: Any) -> Any:
    """Floor-divide ``left`` by ``right`` with zero division mapped to infinities."""
    try:
        return _sanitize_result(left // right)
    except ZeroDivisionError:
        return safe_div(left, right)


def safe_mod(left: Any, right: Any) -> Any:
    """Return ``left % right`` with modulo-by-zero mapped to NaN."""
    try:
        return _sanitize_result(left % right)
    except ZeroDivisionError:
        return math.nan


def safe_pow(left: Any, right: Any) -> Any:
    """Raise ``left`` to ``right`` and clamp overflow to infinities or NaN."""
    # Fast-path: (bit_length(base) - 1) * exp approximates log2 of the result.
    # When this exceeds _FLOAT_MAX_EXP the result is guaranteed > MAX_FLOAT, so
    # skip building a potentially multi-million-digit Python integer entirely.
    if isinstance(left, int) and isinstance(right, int):
        base_abs = abs(left)
        if base_abs > 1 and right > 0 and (base_abs.bit_length() - 1) * right > _FLOAT_MAX_EXP:
            if left < 0 and right % 2 == 1:
                return -math.inf
            return math.inf
    try:
        return _sanitize_result(left**right)
    except OverflowError:
        if isinstance(left, (int, float)) and left < 0 and isinstance(right, int) and right % 2 == 1:
            return -math.inf
        return math.inf


def root(value: Any, degree: Any = 2) -> Any:
    """Return the nth root of ``value`` using ``degree`` as the index.

    The default degree is ``2``, making ``root(x)`` equivalent to a square
    root. Negative values with odd integer degrees return a real result.
    """
    if degree == 0:
        raise ValueError("Root degree cannot be zero.")

    if isinstance(value, (int, float)) and isinstance(degree, (int, float)):
        if value < 0 and float(degree).is_integer() and int(degree) % 2 == 1:
            result = -((-value) ** (1 / int(degree)))
        else:
            result = value ** (1 / degree)

        if isinstance(result, float) and math.isfinite(result):
            rounded = round(result)
            if abs(result - rounded) < 1e-12:
                return int(rounded)
        return _sanitize_result(result)

    return _sanitize_result(value ** (1 / degree))


class SafeArithmeticTransformer(ast.NodeTransformer):
    """Rewrite arithmetic operations to helpers that clamp error cases."""

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)

        helper_name: str | None = None
        if isinstance(node.op, ast.Div):
            helper_name = "safe_div"
        elif isinstance(node.op, ast.FloorDiv):
            helper_name = "safe_floordiv"
        elif isinstance(node.op, ast.Mod):
            helper_name = "safe_mod"
        elif isinstance(node.op, ast.Pow):
            helper_name = "safe_pow"

        if helper_name is None:
            return node

        return ast.copy_location(
            ast.Call(
                func=ast.Name(id=helper_name, ctx=ast.Load()),
                args=[node.left, node.right],
                keywords=[],
            ),
            node,
        )


def _compile_expression(source: str, mode: str) -> Any:
    """Parse, rewrite, and compile calculator code for execution or evaluation."""
    tree = ast.parse(source, mode=mode)
    tree = SafeArithmeticTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    return compile(tree, "<calculator>", mode)


def _find_matching_close_paren(text: str, open_index: int) -> int | None:
    """Return the index of the matching ``)`` for ``text[open_index]``."""
    depth = 0
    quote: str | None = None
    escaped = False

    for index in range(open_index, len(text)):
        char = text[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue

        if char in {"'", '"'}:
            quote = char
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index

    return None


def _find_matching_open_paren(text: str, close_index: int) -> int | None:
    """Return the index of the matching ``(`` for ``text[close_index]``."""
    depth = 0
    for index in range(close_index, -1, -1):
        char = text[index]
        if char == ")":
            depth += 1
        elif char == "(":
            depth -= 1
            if depth == 0:
                return index
    return None


def _find_previous_operand_start(text: str) -> int | None:
    """Return the start index of the operand immediately before the cursor."""
    index = len(text) - 1
    while index >= 0 and text[index].isspace():
        index -= 1

    if index < 0:
        return None

    if text[index] == ")":
        start = _find_matching_open_paren(text, index)
        if start is None:
            return None
        func_index = start - 1
        while func_index >= 0 and (text[func_index].isalnum() or text[func_index] == "_"):
            func_index -= 1
        return func_index + 1

    if text[index].isalnum() or text[index] in {"_", "."}:
        start = index
        while start >= 0 and (text[start].isalnum() or text[start] in {"_", "."}):
            start -= 1
        return start + 1

    return None


_FUNC_DEF_RE = re.compile(
    r'^([A-Za-z_]\w*)\s*\(([^)]*)\)\s*=(?!=)\s*(.+)$',
    re.DOTALL,
)

# Characters that, when immediately preceding ``=``, indicate the ``=`` is
# part of a compound operator (``==``, ``!=``, ``<=``, ``>=``, ``+=``,
# ``-=``, ``*=``, ``/=``, ``**=``, ``//=``, ``%=``, ``&=``, ``|=``,
# ``^=``, ``@=``, ``:=``) and must NOT be rewritten to ``==``.
_EQ_PREFIX_EXCLUDED: frozenset[str] = frozenset("!<>=+-*/%&|^:@~")


def _normalize_comparison_syntax(expression: str) -> str:
    """Rewrite a bare ``=`` (comparison intent) to ``==``.

    Processes the string character-by-character so that ``=`` inside string
    literals and all compound operators are left unchanged.  Only called on
    the final *eval* expression, never on exec statements.
    """
    parts: list[str] = []
    index = 0
    quote: str | None = None
    escaped = False
    prev_char = ""

    while index < len(expression):
        char = expression[index]

        if quote is not None:
            parts.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            prev_char = char
            index += 1
            continue

        if char in {'"', "'"}:
            quote = char
            parts.append(char)
            prev_char = char
            index += 1
            continue

        if char == "=":
            next_char = expression[index + 1] if index + 1 < len(expression) else ""
            if prev_char not in _EQ_PREFIX_EXCLUDED and next_char != "=":
                parts.append("==")
            else:
                parts.append("=")
            prev_char = char
            index += 1
            continue

        parts.append(char)
        prev_char = char
        index += 1

    return "".join(parts)


def _maybe_rewrite_func_def(raw_stmt: str) -> tuple[str, str | None]:
    """Detect ``f(params) = body`` syntax and rewrite it as a lambda assignment.

    Returns ``(python_stmt, func_name)`` where *func_name* is not ``None`` when
    a function definition was detected so the caller knows to exec rather than
    eval the statement.
    """
    match = _FUNC_DEF_RE.match(raw_stmt)
    if match:
        name = match.group(1)
        params = match.group(2)
        body = _normalize_expression_syntax(match.group(3).strip())
        body = _normalize_comparison_syntax(body)
        return f"{name} = lambda {params}: ({body})", name
    return _normalize_expression_syntax(raw_stmt), None


def _normalize_expression_syntax(expression: str) -> str:
    """Translate calculator shorthand such as ``^`` and ``Xroot(Y)`` to Python."""
    parts: list[str] = []
    index = 0
    quote: str | None = None
    escaped = False

    while index < len(expression):
        char = expression[index]
        if quote is not None:
            parts.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue

        if char in {"'", '"'}:
            quote = char
            parts.append(char)
            index += 1
            continue

        if expression.startswith("root(", index):
            close_index = _find_matching_close_paren(expression, index + 4)
            if close_index is None:
                parts.append(expression[index:])
                break

            inner = expression[index + 5 : close_index]
            normalized_inner = _normalize_expression_syntax(inner)
            current = "".join(parts)
            degree_start = _find_previous_operand_start(current)

            if degree_start is None:
                parts = [current, f"root({normalized_inner})"]
            else:
                degree = current[degree_start:].strip()
                parts = [current[:degree_start], f"root({normalized_inner}, {degree})"]

            index = close_index + 1
            continue

        if char == "^":
            parts.append("**")
            index += 1
            continue

        parts.append(char)
        index += 1

    return "".join(parts)


def evaluate_expression_string(
    expression: str,
    extra_namespace: dict[str, Any] | None = None,
) -> Any:
    """Evaluate an expression string using Python eval.

    Semicolons separate statements: all but the last are executed as
    assignments (``exec``), the last is evaluated as an expression.
    Plugins can inject additional callables via *extra_namespace*.
    """
    expression = expression.replace("\r\n", "\n").replace("\r", "\n")
    expression = expression.replace("\n", ";")

    if not expression.strip():
        raise ExpressionError("Enter an expression before calculating.")

    namespace: dict[str, Any] = dict(BASE_NAMESPACE)
    namespace.update(
        {
            "safe_div": safe_div,
            "safe_floordiv": safe_floordiv,
            "safe_mod": safe_mod,
            "safe_pow": safe_pow,
            "root": root,
        }
    )
    if extra_namespace:
        namespace.update(extra_namespace)

    raw_parts = [p.strip() for p in expression.split(";") if p.strip()]
    processed: list[tuple[str, str | None]] = [
        _maybe_rewrite_func_def(p) for p in raw_parts
    ]

    # Execute all leading statements so their bindings are in scope.
    for stmt, _ in processed[:-1]:
        try:
            exec(_compile_expression(stmt, "exec"), namespace)  # noqa: S102
        except SyntaxError as error:
            msg = getattr(error, "msg", str(error))
            raise ExpressionError(f"Syntax error: {msg}") from error
        except Exception as error:
            raise ExpressionError(f"Evaluation error: {error}") from error

    last_stmt, func_name = processed[-1]

    if func_name is not None:
        # Final statement is a function definition: exec it and return the function.
        try:
            exec(_compile_expression(last_stmt, "exec"), namespace)  # noqa: S102
        except SyntaxError as error:
            msg = getattr(error, "msg", str(error))
            raise ExpressionError(f"Syntax error: {msg}") from error
        except Exception as error:
            raise ExpressionError(f"Evaluation error: {error}") from error
        return _sanitize_result(namespace.get(func_name))

    def _eval_stmt(stmt: str) -> Any:
        """Compile and evaluate *stmt*, raising ExpressionError on any failure."""
        try:
            return eval(_compile_expression(stmt, "eval"), namespace)  # noqa: S307
        except SyntaxError as error:
            raise error  # re-raise so the outer try can handle it
        except NameError as error:
            raise ExpressionError(str(error)) from error
        except TypeError as error:
            raise ExpressionError(str(error)) from error
        except (ArithmeticError, ValueError) as error:
            raise ExpressionError(str(error)) from error
        except Exception as error:
            raise ExpressionError(f"Evaluation error: {error}") from error

    try:
        result = _eval_stmt(last_stmt)
    except SyntaxError as original_error:
        # The user may have written ``5=5`` intending a comparison.  Try
        # rewriting single ``=`` to ``==`` before giving up.
        normalized = _normalize_comparison_syntax(last_stmt)
        if normalized != last_stmt:
            try:
                result = _eval_stmt(normalized)
            except SyntaxError:
                msg = getattr(original_error, "msg", str(original_error))
                raise ExpressionError(f"Syntax error: {msg}") from original_error
        else:
            msg = getattr(original_error, "msg", str(original_error))
            raise ExpressionError(f"Syntax error: {msg}") from original_error

    return _sanitize_result(result)


def format_result(value: Any) -> str:
    """Return a display-friendly string for any evaluation result."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Inf" if value > 0 else "-Inf"
        try:
            if value == int(value):
                return str(int(value))
        except (ValueError, OverflowError):
            pass
        return str(value)
    if isinstance(value, str):
        return repr(value)
    if callable(value):
        name = getattr(value, "__name__", None)
        if name and name != "<lambda>":
            return f"<function {name}>"
        return "<function>"
    return repr(value)