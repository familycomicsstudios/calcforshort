#!/usr/bin/env python3
"""Build Calcforshort executables with PyInstaller.

Usage:
  python build.py                # native build for current OS
  python build.py --target native
  python build.py --target windows
  python build.py --target all
  python build.py --windows-via-docker

Notes:
- Native builds are supported on Linux and Windows.
- True cross-compilation with PyInstaller is limited. From Linux, a Windows
  build is attempted only when ``--windows-via-docker`` is enabled and Docker
  is available.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
APP_ENTRY = PROJECT_ROOT / "app.py"
APP_NAME = "calcforshort"
ICON_PNG = PROJECT_ROOT / "Calc For Short.png"
ICON_ICO = PROJECT_ROOT / "Calc For Short.ico"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def _run(command: list[str], *, cwd: Path | None = None) -> int:
    """Run a command and return its exit code."""
    print("$", " ".join(command))
    result = subprocess.run(command, cwd=str(cwd) if cwd else None, check=False)
    return result.returncode


def _data_sep(is_windows_target: bool) -> str:
    """Return PyInstaller add-data separator for the target platform."""
    return ";" if is_windows_target else ":"


def _base_pyinstaller_args(is_windows_target: bool, *, onefile: bool, clean: bool) -> list[str]:
    """Build shared PyInstaller arguments for all targets."""
    args: list[str] = [
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name",
        APP_NAME,
        "--collect-submodules",
        "calculator",
        "--collect-submodules",
        "plugins",
    ]

    if clean:
        args.append("--clean")
    if onefile:
        args.append("--onefile")

    sep = _data_sep(is_windows_target)
    args.extend(["--add-data", f"{ICON_PNG}{sep}."])
    args.extend(["--add-data", f"{ICON_ICO}{sep}."])

    if ICON_ICO.exists():
        args.extend(["--icon", str(ICON_ICO)])

    args.append(str(APP_ENTRY))
    return args


def build_native(*, onefile: bool, clean: bool) -> int:
    """Build an executable for the current platform using local Python."""
    print("Building native executable...")
    command = [sys.executable, *_base_pyinstaller_args(platform.system() == "Windows", onefile=onefile, clean=clean)]
    return _run(command, cwd=PROJECT_ROOT)


def build_windows_via_docker(*, onefile: bool, clean: bool) -> int:
    """Attempt a Windows executable build from Linux via Docker image."""
    if platform.system() == "Windows":
        print("You are already on Windows; use native build instead.")
        return 1

    docker = shutil.which("docker")
    if not docker:
        print("Docker is not installed. Cannot build Windows executable from Linux.")
        return 1

    # cdrx/pyinstaller-windows packages a Wine-based environment.
    image = "cdrx/pyinstaller-windows:python3"
    inner_cmd = [
        "python",
        *_base_pyinstaller_args(True, onefile=onefile, clean=clean),
    ]

    command = [
        docker,
        "run",
        "--rm",
        "-v",
        f"{PROJECT_ROOT}:/src",
        "-w",
        "/src",
        image,
        *inner_cmd,
    ]
    print("Building Windows executable via Docker...")
    return _run(command)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build Calcforshort executable(s).")
    parser.add_argument(
        "--target",
        choices=["native", "windows", "all"],
        default="native",
        help="Build target: current OS, Windows, or both.",
    )
    parser.add_argument(
        "--windows-via-docker",
        action="store_true",
        help="Allow Windows build from non-Windows hosts using Docker.",
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Build in one-dir mode instead of one-file.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip PyInstaller --clean.",
    )
    return parser.parse_args()


def main() -> int:
    """Run requested build targets."""
    args = parse_args()
    onefile = not args.onedir
    clean = not args.no_clean

    exit_code = 0

    if args.target in {"native", "all"}:
        code = build_native(onefile=onefile, clean=clean)
        exit_code = exit_code or code

    if args.target in {"windows", "all"}:
        if platform.system() == "Windows":
            code = build_native(onefile=onefile, clean=clean)
            exit_code = exit_code or code
        elif args.windows_via_docker:
            code = build_windows_via_docker(onefile=onefile, clean=clean)
            exit_code = exit_code or code
        else:
            print(
                "Windows build requested from non-Windows host. "
                "Re-run with --windows-via-docker, or run this script on Windows."
            )
            exit_code = exit_code or 1

    if exit_code == 0:
        print("Build complete.")
        if DIST_DIR.exists():
            print(f"Artifacts: {DIST_DIR}")
    else:
        print("Build finished with errors.")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
