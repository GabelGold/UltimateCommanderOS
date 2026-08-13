# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent

a = Analysis(
    [str(ROOT / "ultimate_commander.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "src" / "ui"), "src/ui"),
        (str(ROOT / ".env.example"), "."),
        (str(ROOT / "requirements.txt"), "."),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtNetwork",
        "ifaddr",
        "psutil",
        "dotenv",
        "src.backend.Dashboard",
        "src.backend.commander_api",
        "src.backend.network",
        "src.backend.ollama_client",
        "src.backend.security",
        "src.backend.system_monitor",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["netifaces"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="UltimateCommanderOS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="UltimateCommanderOS",
)
