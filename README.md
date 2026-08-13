# Ultimate Commander OS

[![CI](https://github.com/GabelGold/UltimateCommanderOS/actions/workflows/ci.yml/badge.svg)](https://github.com/GabelGold/UltimateCommanderOS/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/Qt-PySide6%20QML-41CD52.svg)](https://doc.qt.io/qtforpython-6/)
[![License](https://img.shields.io/badge/license-proprietary-lightgrey.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/GabelGold/UltimateCommanderOS)

Windows-11-Kommandozentrale mit Fluent-QML-Oberfläche, lokalem HTTP-Commander und optionaler Ollama-Schicht.

**Entwickler:** Christian Schmitt, Solingen  
**Stand:** 13. August 2026 · Version **1.0.0**  
**GitHub:** https://github.com/GabelGold/UltimateCommanderOS

## Start

```powershell
# Einmal-Deploy (venv, Tests, EXE, Git)
powershell -ExecutionPolicy Bypass -File ".\GODMODE_DEPLOY.ps1"

# Oder direkt
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\start.bat
```

Live-Checker (Tasten 1–5):

```powershell
.\venv\Scripts\python.exe live_check.py
```

| Taste | Aktion |
|------:|--------|
| 1 | Commander-Server neu starten |
| 2 | Cache / `__pycache__` / QML-Cache leeren |
| 3 | UI-Reload-Token setzen (QML lädt neu) |
| 4 | GitHub-Status `GabelGold/UltimateCommanderOS` |
| 5 | Freigaben sticky markieren |

## Architektur

- `ultimate_commander.py` — Einstieg, Portable-venv, PySide6-Fenster
- `src/backend/Dashboard.py` — Signale CPU / RAM / Netz / Ollama → QML
- `src/ui/Dashboard.qml` + `StatusBar.qml` — Fluent Dark
- `src/backend/network.py` — **ifaddr** (kein `netifaces`)
- `src/backend/ollama_client.py` — echter Dienst oder Mock
- `installer/UltimateCommander.spec` — fensterlose EXE
- `installer/UltimateInstaller.iss` — Inno Setup

## Tests & Build

```powershell
pytest tests/ -v
pyinstaller --noconfirm installer\UltimateCommander.spec
# optional, wenn Inno Setup installiert ist:
# iscc installer\UltimateInstaller.iss
```

ISO-Platzhalter: `tools\create_iso.ps1` (benötigt `oscdimg` aus dem Windows ADK).
