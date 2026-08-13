#!/usr/bin/env python3
# Ultimate Commander OS
# Entwickler: Christian Schmitt, Solingen
# Entry point — windowed PySide6 shell + local commander API.
# Missing hashes / comments were a prior syntax trap; every line here is valid Python.

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def ensure_venv() -> None:
    """Portable mode: create venv + install deps when running from source."""
    if _is_frozen():
        return
    if os.environ.get("UCOS_SKIP_VENV") == "1":
        return
    if sys.prefix != sys.base_prefix:
        return
    venv = ROOT / "venv"
    py = Path(sys.executable)
    if not venv.exists():
        subprocess.check_call([str(py), "-m", "venv", str(venv)])
    scripts = venv / "Scripts" if os.name == "nt" else venv / "bin"
    venv_py = scripts / ("python.exe" if os.name == "nt" else "python")
    marker = venv / ".ucos_installed"
    if not marker.exists():
        subprocess.check_call(
            [str(venv_py), "-m", "pip", "install", "--upgrade", "pip"],
        )
        subprocess.check_call(
            [str(venv_py), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
        )
        marker.write_text("ok\n", encoding="utf-8")
    os.execv(str(venv_py), [str(venv_py), str(ROOT / "ultimate_commander.py"), *sys.argv[1:]])


def resource_path(*parts: str) -> Path:
    if _is_frozen():
        base = Path(getattr(sys, "_MEIPASS", ROOT))
        return base.joinpath(*parts)
    return ROOT.joinpath(*parts)


def main() -> int:
    ensure_venv()
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except Exception:
        pass

    from src.backend.security import ensure_encryption_key
    from src.backend.commander_api import start_http

    ensure_encryption_key()
    start_http()

    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    from src.backend.Dashboard import DashboardBackend

    app = QGuiApplication(sys.argv)
    app.setApplicationName("Ultimate Commander OS")
    app.setOrganizationName("Christian Schmitt")
    app.setOrganizationDomain("solingen")

    backend = DashboardBackend()
    engine = QQmlApplicationEngine()
    qml_dir = resource_path("src", "ui")
    engine.addImportPath(str(qml_dir))
    engine.rootContext().setContextProperty("backend", backend)

    qml_file = qml_dir / "Dashboard.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        print("QML load failed:", qml_file, file=sys.stderr)
        return 1
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
