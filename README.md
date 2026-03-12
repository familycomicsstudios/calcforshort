# Calcforshort: The Extensible Calculator App

Calcforshort is a Tkinter calculator with plugin-based syntax buttons and callable extensions. The GUI behaves like a lightweight expression-entry calculator: you type directly into the input, and the buttons insert text at the cursor. The app also includes a top menu with dark mode and per-plugin enable or disable toggles.

## Run

```bash
python app.py
```

CLI mode:

```bash
python app.py "(2 + 3) * 4"
python app.py --cli "(2 + 3) * 4"
python app.py --cli
```

## Menus

- `Settings -> Dark mode` switches the calculator between light and dark themes.
- `Settings -> Live Mode` evaluates the current expression while you type.
- `Plugins` lets you enable or disable operator plugins at runtime.

## Default controls

- `(` and `)` insert parentheses into the current expression.
- `(-)` inserts a minus sign for unary negation when used at the start of a value.
- `⌫` removes the current selection or the character before the cursor.
- `C` clears the full expression.
- `=` evaluates the full expression and shows the result in the read-only result field.
- You can type directly into the expression field, including with the keyboard.
- Invalid expressions show `Error: ...` in the result field instead of opening a popup.

## Expression syntax

- `^` is treated as exponentiation, so `2^8` evaluates to `256`.
- `root(Y)` means the square root of `Y`.
- `Xroot(Y)` means the `X`th root of `Y`, so `3root(27)` evaluates to `3`.
- Statements separated by `;` run left to right, so `a=2; b=a; b^3` works.
- Strings are supported, so `"Hello" + "World"` evaluates to `"HelloWorld"`.

## Resizing and settings

- The window can be resized or maximized.
- Buttons stay fixed-size while extra window width is used to fit more plugin buttons across the plugin area.
- Settings are saved automatically.
- On Linux and macOS, settings are written to `~/.calcforshort/settings.json`.
- On Windows, settings are written to `%APPDATA%\Calcforshort\settings.json`.
- Existing settings from the older `PluginCalculator` location are still read automatically.

## Plugin model

Add a module under `plugins/` and expose a `register()` function returning a `CalcPlugin`
(or a list of them).

**Syntax button** — inserts text, no extra function needed:

```python
from calculator.plugin_api import CalcPlugin

def register() -> CalcPlugin:
    return CalcPlugin(label="^", insert=" ** ")
```

Built-in examples now include `X^Y` with `insert="^"` and `Xroot(Y)` with
`insert="root("`.

**Function button** — adds a callable to the expression namespace *and* a button that
inserts the opening call:

```python
import math
from calculator.plugin_api import CalcPlugin

def register() -> CalcPlugin:
    return CalcPlugin(
        label="sin(",
        insert="sin(",
        name="sin",
        handler=math.sin,
    )
```

- `label` is shown on the button.
- `insert` is the text inserted when the button is clicked.
- `name` (optional) registers the callable under that identifier in the evaluator,
  so users can type `name(...)` directly.
- `handler` (optional) is the Python callable added to the namespace.

All expressions are normalized into Python before evaluation. That means the app
supports standard Python operators (`+`, `-`, `*`, `/`, `**`, `%`, `//`) as well as
calculator shorthand such as `^` and `Xroot(Y)`.

## API

You can import the calculator as a library:

```python
from calculator import calculate

result = calculate("(2 + 3) * 4")
print(result)
```