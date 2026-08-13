from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_entrypoints_parse() -> None:
    for name in ("ultimate_commander.py", "live_check.py"):
        ast.parse((ROOT / name).read_text(encoding="utf-8"))


def test_all_python_parses() -> None:
    for path in ROOT.rglob("*.py"):
        if any(part in {"venv", ".venv", "dist", "build"} for part in path.parts):
            continue
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))


def test_init_files_present() -> None:
    assert (ROOT / "src" / "__init__.py").is_file()
    assert (ROOT / "src" / "backend" / "__init__.py").is_file()
    assert (ROOT / "src" / "ui" / "__init__.py").is_file()


def test_qml_dashboard_exists() -> None:
    qml = (ROOT / "src" / "ui" / "Dashboard.qml").read_text(encoding="utf-8")
    assert "ApplicationWindow" in qml
    assert "StatusBar" in qml
