"""Tkinter GUI for Calcforshort: The Extensible Calculator App."""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Callable, Sequence

from calculator.api import calculate
from calculator.cli import run_cli
from calculator.expression import ExpressionError, format_result, set_angle_mode
from calculator.plugin_loader import LoadedPlugin, load_plugins
from calculator.settings import AppSettings, load_settings, save_settings


LIGHT_THEME = {
    "root_bg": "#f2f2f2",
    "panel_bg": "#f2f2f2",
    "display_bg": "#ffffff",
    "display_fg": "#111111",
    "button_bg": "#ffffff",
    "button_fg": "#111111",
    "button_active_bg": "#d9d9d9",
    "menu_bg": "#f7f7f7",
    "menu_fg": "#111111",
}

DARK_THEME = {
    "root_bg": "#1e1f24",
    "panel_bg": "#1e1f24",
    "display_bg": "#2a2d34",
    "display_fg": "#f3f4f6",
    "button_bg": "#343842",
    "button_fg": "#f3f4f6",
    "button_active_bg": "#4a5160",
    "menu_bg": "#2a2d34",
    "menu_fg": "#f3f4f6",
}

BUTTON_WIDTH = 6
BUTTON_HEIGHT = 2
BUTTON_PADX = 4
BUTTON_PADY = 4
PLUGIN_COLUMN_WIDTH = 88
PLUGIN_MIN_COLUMNS = 2
WINDOW_MIN_WIDTH = 420
WINDOW_MIN_HEIGHT = 320
ENTRY_FONT = ("TkFixedFont", 18)
RESULT_FONT = ("TkDefaultFont", 12)

_DIGITS_AND_DOT = frozenset("0123456789.")
_BINARY_LEFT = frozenset("0123456789.)")
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ICON_PNG = _PROJECT_ROOT / "Calc For Short.png"
_ICON_ICO = _PROJECT_ROOT / "Calc For Short.ico"


def _find_matching_open_paren(text: str, close_index: int) -> int | None:
    """Return the index of the '(' that matches text[close_index], or None."""
    depth = 0
    for i in range(close_index, -1, -1):
        if text[i] == ")":
            depth += 1
        elif text[i] == "(":
            depth -= 1
            if depth == 0:
                return i
    return None


def _plugin_group_key(plugin: LoadedPlugin) -> str:
    """Return the group key derived from a plugin's module path."""
    module_name = plugin.plugin_id.split(":", 1)[0]
    return module_name.rsplit(".", 1)[-1]


def _plugin_group_label(group_key: str) -> str:
    """Return a human-friendly group label for menu display."""
    return group_key.replace("_", " ").title()


class CalculatorApp:
    """Own the calculator window, widgets, theming, and user interactions."""

    def __init__(self, root: tk.Tk, plugins: list[LoadedPlugin], settings: AppSettings) -> None:
        self.root = root
        self.root.title("Calcforshort: The Extensible Calculator App")
        self._icon_photo: tk.PhotoImage | None = None
        self._apply_window_icon()
        self.root.resizable(True, True)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.plugins = plugins
        self.settings = settings
        all_plugin_ids = {plugin.plugin_id for plugin in plugins}
        disabled_from_settings = set(settings.disabled_plugin_ids)
        self.enabled_plugin_ids = all_plugin_ids - disabled_from_settings
        self.plugin_groups = self._build_plugin_groups()
        self.group_enabled_vars = {
            group_key: tk.BooleanVar(
                value=bool(plugin_ids)
                and all(plugin_id in self.enabled_plugin_ids for plugin_id in plugin_ids)
            )
            for group_key, plugin_ids in self.plugin_groups.items()
        }
        self.dark_mode = tk.BooleanVar(value=settings.dark_mode)
        self.live_mode = tk.BooleanVar(value=settings.live_mode)
        self.angle_mode = tk.StringVar(value=settings.angle_mode)
        set_angle_mode(self.angle_mode.get())

        self.expression_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="")
        self.result_is_error = False
        self.frame: tk.Frame | None = None
        self.body_frame: tk.Frame | None = None
        self.keypad_frame: tk.Frame | None = None
        self.plugin_frame: tk.Frame | None = None
        self.controls_frame: tk.Frame | None = None
        self.display: tk.Entry | None = None
        self.result_display: tk.Entry | None = None
        self.buttons: list[tk.Button] = []
        self.plugin_buttons: list[tk.Button] = []
        self.menu_bar = tk.Menu(self.root)
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.angle_mode_menu = tk.Menu(self.settings_menu, tearoff=0)
        self.plugins_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.plugin_column_count = PLUGIN_MIN_COLUMNS
        self.resize_after_id: str | None = None

        self._build_ui()
        self._apply_saved_window_state()
        self.root.bind("<Configure>", self._on_root_configure)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.expression_var.trace_add("write", self._on_expression_changed)

    def _apply_window_icon(self) -> None:
        """Apply app icons from the project root if available."""
        if _ICON_PNG.exists():
            try:
                # Keep a reference to avoid Tk garbage-collecting the icon image.
                self._icon_photo = tk.PhotoImage(file=str(_ICON_PNG))
                self.root.iconphoto(True, self._icon_photo)
            except tk.TclError:
                pass

        if _ICON_ICO.exists():
            try:
                self.root.iconbitmap(str(_ICON_ICO))
            except tk.TclError:
                pass

    def _build_ui(self) -> None:
        """Create the menu bar and the initial window layout."""
        self.root.config(menu=self.menu_bar)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_checkbutton(
            label="Dark mode",
            variable=self.dark_mode,
            command=self.toggle_dark_mode,
        )
        self.settings_menu.add_checkbutton(
            label="Live Mode",
            variable=self.live_mode,
            command=self.toggle_live_mode,
        )
        self.settings_menu.add_cascade(label="Angle Mode", menu=self.angle_mode_menu)
        self.angle_mode_menu.add_radiobutton(
            label="Radians",
            value="radian",
            variable=self.angle_mode,
            command=self.toggle_angle_mode,
        )
        self.angle_mode_menu.add_radiobutton(
            label="Degrees",
            value="degree",
            variable=self.angle_mode,
            command=self.toggle_angle_mode,
        )
        self.menu_bar.add_cascade(label="Plugins", menu=self.plugins_menu)

        for group_key in sorted(self.plugin_groups.keys()):
            menu_label = _plugin_group_label(group_key)
            self.plugins_menu.add_checkbutton(
                label=menu_label,
                variable=self.group_enabled_vars[group_key],
                command=lambda current_group=group_key: self.toggle_plugin_group(current_group),
            )

        self._render_layout()
        self._apply_theme()

    def _render_layout(self) -> None:
        """Rebuild the main calculator layout from the current state."""
        if self.frame is not None:
            self.frame.destroy()

        self.frame = tk.Frame(self.root, padx=12, pady=12)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.buttons = []
        self.plugin_buttons = []

        self.display = tk.Entry(
            self.frame,
            textvariable=self.expression_var,
            justify="right",
            font=ENTRY_FONT,
        )
        self.display.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        self.display.bind("<Return>", self._on_return_pressed)
        self.display.bind("<KP_Enter>", self._on_return_pressed)

        self.result_display = tk.Entry(
            self.frame,
            textvariable=self.result_var,
            justify="right",
            font=RESULT_FONT,
            state="readonly",
            relief="sunken",
        )
        self.result_display.grid(row=1, column=0, pady=(0, 10), sticky="ew")

        self.controls_frame = tk.Frame(self.frame)
        self.controls_frame.grid(row=2, column=0, pady=(0, 10), sticky="w")

        control_buttons = [
            ("(", lambda: self.insert_text("(")),
            (")", lambda: self.insert_text(")")),
            ("(-)", self.negate),
            ("⌫", self.backspace),
        ]
        for column_index, (label, command) in enumerate(control_buttons):
            button = tk.Button(
                self.controls_frame,
                text=label,
                width=BUTTON_WIDTH,
                height=BUTTON_HEIGHT,
                command=command,
            )
            button.grid(row=0, column=column_index, padx=BUTTON_PADX, pady=BUTTON_PADY)
            self.buttons.append(button)

        self.body_frame = tk.Frame(self.frame)
        self.body_frame.grid(row=3, column=0, sticky="nw")

        self.keypad_frame = tk.Frame(self.body_frame)
        self.keypad_frame.grid(row=0, column=0, sticky="nw")

        self.plugin_frame = tk.Frame(self.body_frame)
        self.plugin_frame.grid(row=0, column=1, padx=(12, 0), sticky="nw")

        number_rows = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            ["0", ".", "="],
        ]

        for row_index, row_values in enumerate(number_rows, start=1):
            for column_index, value in enumerate(row_values):
                command = self._make_insert_handler(value)
                if value == "=":
                    command = self.calculate_result
                button = tk.Button(
                    self.keypad_frame,
                    text=value,
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    command=command,
                )
                button.grid(
                    row=row_index - 1,
                    column=column_index,
                    padx=BUTTON_PADX,
                    pady=BUTTON_PADY,
                )
                self.buttons.append(button)

        clear_button = tk.Button(
            self.keypad_frame,
            text="C",
            width=BUTTON_WIDTH * 3 + 2,
            height=BUTTON_HEIGHT,
            command=self.clear,
        )
        clear_button.grid(
            row=len(number_rows),
            column=0,
            columnspan=3,
            padx=BUTTON_PADX,
            pady=(BUTTON_PADY + 4, BUTTON_PADY),
        )
        self.buttons.append(clear_button)

        self._render_plugin_buttons()
        if self.display is not None:
            self.display.focus_set()

    def _render_plugin_buttons(self) -> None:
        """Render buttons for all currently enabled plugins."""
        if self.plugin_frame is None:
            return

        for button in self.plugin_buttons:
            if button in self.buttons:
                self.buttons.remove(button)
        self.plugin_buttons = []

        for child in self.plugin_frame.winfo_children():
            child.destroy()

        enabled_plugins = self._enabled_plugins()
        visible_plugins = [plugin for plugin in enabled_plugins if plugin.show_button]
        if not visible_plugins:
            placeholder = tk.Label(self.plugin_frame, text="No plugins enabled")
            placeholder.grid(row=0, column=0, padx=BUTTON_PADX, pady=BUTTON_PADY, sticky="w")
            self._apply_theme()
            return

        column_count = min(self.plugin_column_count, max(1, len(visible_plugins)))
        for index, plugin in enumerate(visible_plugins):
            row_index = index // column_count
            column_index = index % column_count
            button = tk.Button(
                self.plugin_frame,
                text=plugin.label,
                width=BUTTON_WIDTH,
                height=BUTTON_HEIGHT,
                command=self._make_insert_handler(plugin.insert),
            )
            button.grid(
                row=row_index,
                column=column_index,
                padx=BUTTON_PADX,
                pady=BUTTON_PADY,
            )
            self.buttons.append(button)
            self.plugin_buttons.append(button)

    def _make_insert_handler(self, value: str) -> Callable[[], None]:
        """Return a button command that inserts *value* into the entry."""
        return lambda: self.insert_text(value)

    def _enabled_plugins(self) -> list[LoadedPlugin]:
        """Return plugins that are currently enabled in the UI."""
        return [plugin for plugin in self.plugins if plugin.plugin_id in self.enabled_plugin_ids]

    def _build_plugin_groups(self) -> dict[str, list[str]]:
        """Build a map of group key to plugin IDs for grouped menu toggles."""
        groups: dict[str, list[str]] = {}
        for plugin in self.plugins:
            group_key = _plugin_group_key(plugin)
            groups.setdefault(group_key, []).append(plugin.plugin_id)
        return groups

    def _sync_group_enabled_vars(self) -> None:
        """Refresh group menu check states from current enabled plugin IDs."""
        for group_key, plugin_ids in self.plugin_groups.items():
            is_group_enabled = bool(plugin_ids) and all(
                plugin_id in self.enabled_plugin_ids for plugin_id in plugin_ids
            )
            if group_key in self.group_enabled_vars:
                self.group_enabled_vars[group_key].set(is_group_enabled)

    def _on_expression_changed(self, *_: object) -> None:
        """Refresh the result display after entry edits in live mode."""
        if self.live_mode.get():
            self._evaluate_into_result(live=True)
            return

        self._clear_result_display()

    def toggle_dark_mode(self) -> None:
        """Apply the selected color theme and persist the preference."""
        self._apply_theme()
        self._save_settings()

    def toggle_live_mode(self) -> None:
        """Enable or disable automatic evaluation while typing."""
        if self.live_mode.get():
            self._evaluate_into_result(live=True)
        else:
            self._clear_result_display()
        self._save_settings()

    def toggle_angle_mode(self) -> None:
        """Switch trig calculations between radian and degree modes."""
        set_angle_mode(self.angle_mode.get())
        if self.live_mode.get():
            self._evaluate_into_result(live=True)
        else:
            self._clear_result_display()
        self._save_settings()

    def toggle_plugin_group(self, group_key: str) -> None:
        """Enable or disable all plugins belonging to *group_key*."""
        group_plugin_ids = self.plugin_groups.get(group_key, [])
        if self.group_enabled_vars[group_key].get():
            self.enabled_plugin_ids.update(group_plugin_ids)
        else:
            self.enabled_plugin_ids.difference_update(group_plugin_ids)

        self._sync_group_enabled_vars()

        self._render_layout()
        self._apply_theme()
        if self.live_mode.get():
            self._evaluate_into_result(live=True)
        else:
            self._clear_result_display()
        self._save_settings()

    def _apply_theme(self) -> None:
        """Update widget colors to match the active light or dark theme."""
        theme = DARK_THEME if self.dark_mode.get() else LIGHT_THEME

        self.root.configure(bg=theme["root_bg"])
        self.menu_bar.configure(
            background=theme["menu_bg"],
            foreground=theme["menu_fg"],
            activebackground=theme["button_active_bg"],
            activeforeground=theme["button_fg"],
        )
        self.settings_menu.configure(
            background=theme["menu_bg"],
            foreground=theme["menu_fg"],
            activebackground=theme["button_active_bg"],
            activeforeground=theme["button_fg"],
            selectcolor=theme["panel_bg"],
        )
        self.angle_mode_menu.configure(
            background=theme["menu_bg"],
            foreground=theme["menu_fg"],
            activebackground=theme["button_active_bg"],
            activeforeground=theme["button_fg"],
            selectcolor=theme["panel_bg"],
        )
        self.plugins_menu.configure(
            background=theme["menu_bg"],
            foreground=theme["menu_fg"],
            activebackground=theme["button_active_bg"],
            activeforeground=theme["button_fg"],
            selectcolor=theme["panel_bg"],
        )

        if self.frame is not None:
            self.frame.configure(bg=theme["panel_bg"])
        if self.body_frame is not None:
            self.body_frame.configure(bg=theme["panel_bg"])
        if self.controls_frame is not None:
            self.controls_frame.configure(bg=theme["panel_bg"])
        if self.keypad_frame is not None:
            self.keypad_frame.configure(bg=theme["panel_bg"])
        if self.plugin_frame is not None:
            self.plugin_frame.configure(bg=theme["panel_bg"])
        if self.display is not None:
            self.display.configure(
                bg=theme["display_bg"],
                fg=theme["display_fg"],
                insertbackground=theme["display_fg"],
            )
        if self.result_display is not None:
            self.result_display.configure(
                readonlybackground=theme["display_bg"],
                fg=theme["display_fg"] if not self.result_is_error else "#c0392b",
            )
        for button in self.buttons:
            button.configure(
                bg=theme["button_bg"],
                fg=theme["button_fg"],
                activebackground=theme["button_active_bg"],
                activeforeground=theme["button_fg"],
            )
        if self.plugin_frame is not None:
            for child in self.plugin_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=theme["panel_bg"], fg=theme["display_fg"])

    def _apply_saved_window_state(self) -> None:
        """Restore saved window geometry and maximized state."""
        if self.settings.window_geometry:
            self.root.geometry(self.settings.window_geometry)
        if self.settings.maximized:
            self._maximize_window()

    def _maximize_window(self) -> None:
        """Maximize the window using the platform-specific Tk mechanism."""
        if sys.platform.startswith("win"):
            self.root.state("zoomed")
            return

        try:
            self.root.attributes("-zoomed", True)
        except tk.TclError:
            pass

    def _on_root_configure(self, event: tk.Event[tk.Misc]) -> None:
        """Debounce resize handling for the root window."""
        if event.widget is not self.root:
            return

        if self.resize_after_id is not None:
            self.root.after_cancel(self.resize_after_id)
        self.resize_after_id = self.root.after(100, self._handle_resized_window)

    def _handle_resized_window(self) -> None:
        """Reflow plugin buttons after the window size changes."""
        self.resize_after_id = None
        if self.body_frame is None or self.keypad_frame is None:
            return

        self.root.update_idletasks()
        available_width = self.body_frame.winfo_width() - self.keypad_frame.winfo_width() - 12
        calculated_columns = max(PLUGIN_MIN_COLUMNS, available_width // PLUGIN_COLUMN_WIDTH)
        if calculated_columns != self.plugin_column_count:
            self.plugin_column_count = calculated_columns
            self._render_plugin_buttons()
            self._apply_theme()

    def _save_settings(self) -> None:
        """Persist the current UI state to the settings file."""
        self.settings.dark_mode = self.dark_mode.get()
        self.settings.live_mode = self.live_mode.get()
        self.settings.angle_mode = self.angle_mode.get()
        self.settings.disabled_plugin_ids = sorted(
            plugin.plugin_id for plugin in self.plugins if plugin.plugin_id not in self.enabled_plugin_ids
        )
        self.settings.maximized = self._is_maximized()
        if not self.settings.maximized:
            self.settings.window_geometry = self.root.geometry()

        try:
            save_settings(self.settings)
        except OSError:
            messagebox.showwarning("Settings", "Unable to save settings.")

    def _is_maximized(self) -> bool:
        """Return whether the root window is currently maximized."""
        try:
            return self.root.state() == "zoomed"
        except tk.TclError:
            pass

        try:
            return bool(self.root.attributes("-zoomed"))
        except tk.TclError:
            return False

    def on_close(self) -> None:
        """Persist settings and close the application window."""
        self._save_settings()
        self.root.destroy()

    def insert_text(self, value: str) -> None:
        """Insert *value* at the cursor, replacing any active selection."""
        if self.display is None:
            return

        self._replace_selection_or_insert(value)
        self.display.focus_set()

    def backspace(self) -> None:
        """Delete the current selection or the character before the cursor."""
        if self.display is None:
            return

        if self._delete_selection_if_present():
            self.display.focus_set()
            return

        insert_at = self.display.index(tk.INSERT)
        if insert_at <= 0:
            return

        self.display.delete(insert_at - 1)
        self.display.focus_set()

    def negate(self) -> None:
        """Toggle the sign of the token immediately before the cursor.

        * cursor after a number   →  wraps as -(number) or unwraps
        * cursor after ')'        →  prepends '-' or removes it
        * otherwise               →  inserts '-' at cursor
        """
        if self.display is None:
            return

        text = self.display.get()
        pos = self.display.index(tk.INSERT)

        # ── Case 1: cursor right after a numeric literal ──────────────────────
        num_start = pos
        while num_start > 0 and text[num_start - 1] in _DIGITS_AND_DOT:
            num_start -= 1

        if num_start < pos:
            token = text[num_start:pos]
            already_negated = (
                num_start >= 2
                and text[num_start - 2] == "-"
                and text[num_start - 1] == "("
                and pos < len(text)
                and text[pos] == ")"
            )
            if already_negated:
                # Remove the wrapping "-(" and ")"
                self.display.delete(pos)           # delete ")" first (higher index)
                self.display.delete(num_start - 2, num_start)  # delete "-("
                self.display.icursor(num_start - 2 + len(token))
            else:
                self.display.delete(num_start, pos)
                self.display.insert(num_start, f"-({token})")
                self.display.icursor(num_start + len(token) + 3)
            self.display.focus_set()
            return

        # ── Case 2: cursor right after ")" ────────────────────────────────────
        if pos > 0 and text[pos - 1] == ")":
            match_pos = _find_matching_open_paren(text, pos - 1)
            if match_pos is not None:
                # '-' is a unary negation only when not preceded by a digit/dot/)
                is_unary_neg = (
                    match_pos >= 1
                    and text[match_pos - 1] == "-"
                    and (match_pos < 2 or text[match_pos - 2] not in _BINARY_LEFT)
                )
                if is_unary_neg:
                    self.display.delete(match_pos - 1)
                    self.display.icursor(pos - 1)
                else:
                    self.display.insert(match_pos, "-")
                    self.display.icursor(pos + 1)
            self.display.focus_set()
            return

        # ── Fallback: insert "-" at cursor ────────────────────────────────────
        self._replace_selection_or_insert("-")
        self.display.focus_set()

    def calculate_result(self) -> None:
        """Evaluate the current expression and show the formatted result."""
        self._evaluate_into_result(live=False)

    def clear(self) -> None:
        """Clear the entry and result display, then refocus the input."""
        self.expression_var.set("")
        self._clear_result_display()
        if self.display is not None:
            self.display.focus_set()

    def _evaluate_into_result(self, live: bool) -> None:
        """Evaluate the entry contents and update the result field."""
        expression = self.expression_var.get().strip()
        if not expression:
            self._clear_result_display()
            return

        try:
            result = calculate(
                expression,
                plugins=self.plugins,
                enabled_plugin_ids=self.enabled_plugin_ids,
            )
        except ZeroDivisionError:
            self._set_result_display("Error: Division by zero is not allowed.", is_error=True)
            return
        except ExpressionError as error:
            self._set_result_display(f"Error: {error}", is_error=True)
            return

        self._set_result_display(f"= {format_result(result)}")

    def _set_result_display(self, text: str, is_error: bool = False) -> None:
        """Show *text* in the result field and apply the correct styling."""
        self.result_is_error = is_error
        self.result_var.set(text)
        self._apply_theme()

    def _clear_result_display(self) -> None:
        """Remove any current result or error message from the UI."""
        self.result_is_error = False
        self.result_var.set("")
        self._apply_theme()

    def _replace_selection_or_insert(self, value: str) -> None:
        """Replace the current selection with *value*, or insert at the cursor."""
        if self.display is None:
            return

        try:
            selection_start = self.display.index("sel.first")
            selection_end = self.display.index("sel.last")
        except tk.TclError:
            insert_at = self.display.index(tk.INSERT)
            self.display.insert(insert_at, value)
            self.display.icursor(insert_at + len(value))
            return

        self.display.delete(selection_start, selection_end)
        self.display.insert(selection_start, value)
        self.display.icursor(selection_start + len(value))

    def _delete_selection_if_present(self) -> bool:
        """Delete the active selection and return whether one existed."""
        if self.display is None:
            return False

        try:
            selection_start = self.display.index("sel.first")
            selection_end = self.display.index("sel.last")
        except tk.TclError:
            return False

        self.display.delete(selection_start, selection_end)
        self.display.icursor(selection_start)
        return True

    def _on_return_pressed(self, _: tk.Event[tk.Misc]) -> str:
        """Evaluate the current expression and suppress Tk's default behavior."""
        self.calculate_result()
        return "break"


def run_gui() -> int:
    """Start the Tkinter GUI and return the process exit code."""
    root = tk.Tk()

    try:
        plugins = load_plugins()
    except Exception as error:
        messagebox.showerror("Plugin error", f"Failed to load plugins: {error}")
        root.destroy()
        return 1

    settings = load_settings()
    CalculatorApp(root, plugins, settings)
    root.mainloop()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Parse command-line arguments and run the GUI or CLI entry point."""
    parser = argparse.ArgumentParser(description="Calcforshort: The Extensible Calculator App")
    parser.add_argument("expression", nargs="?", help="Expression to evaluate in CLI mode")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args(argv)

    if args.cli or args.expression is not None:
        return run_cli(args.expression)

    return run_gui()