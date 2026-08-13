#!/usr/bin/env python3
"""
Live-Checker — Tasten 1-5:
  1  Server neu starten
  2  Cache leeren
  3  UI per QML-Reload anstoßen
  4  GitHub-Status prüfen
  5  Freigaben sticky machen
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SRC = ROOT / "src"
os.environ.setdefault("UCOS_SKIP_VENV", "1")

EXPECTED = [
    ROOT / "ultimate_commander.py",
    ROOT / "live_check.py",
    ROOT / "requirements.txt",
    SRC / "__init__.py",
    SRC / "backend" / "__init__.py",
    SRC / "backend" / "Dashboard.py",
    SRC / "backend" / "network.py",
    SRC / "backend" / "system_monitor.py",
    SRC / "backend" / "ollama_client.py",
    SRC / "backend" / "security.py",
    SRC / "backend" / "commander_api.py",
    SRC / "ui" / "__init__.py",
    SRC / "ui" / "Dashboard.qml",
    SRC / "ui" / "StatusBar.qml",
    SRC / "ui" / "Theme.qml",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compile_all() -> list[dict]:
    results = []
    for path in ROOT.rglob("*.py"):
        if any(part in {"venv", ".venv", "dist", "build"} for part in path.parts):
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            results.append({"ok": True, "file": str(path.relative_to(ROOT))})
        except SyntaxError as exc:
            results.append({"ok": False, "file": str(path.relative_to(ROOT)), "error": str(exc)})
    return results


def check_requirements() -> dict:
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8-sig")
    pkgs = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return {
        "ok": any(p.startswith("ifaddr") for p in pkgs) and not any(p.startswith("netifaces") for p in pkgs),
        "netifaces_present": any(p.startswith("netifaces") for p in pkgs),
        "ifaddr_present": any(p.startswith("ifaddr") for p in pkgs),
    }


def structural() -> list[dict]:
    rows = []
    for path in EXPECTED:
        rows.append({"ok": path.exists(), "path": str(path.relative_to(ROOT))})
    return rows


def action(key: str) -> dict:
    from src.backend import commander_api as api

    mapping = {
        "1": api.restart_http,
        "2": api.clear_cache,
        "3": api.request_ui_reload,
        "4": api.github_status,
        "5": api.make_shares_sticky,
    }
    fn = mapping.get(key)
    if fn is None:
        return {"ok": False, "error": f"unknown key {key}"}
    if key == "1":
        return fn()
    # For 2-5 talk to a running server if present, else run locally.
    try:
        import urllib.request

        host = os.environ.get("UCOS_HOST", "127.0.0.1")
        port = os.environ.get("UCOS_PORT", "8765")
        cmd = {
            "2": "clear_cache",
            "3": "reload_ui",
            "4": "github_status",
            "5": "shares_sticky",
        }[key]
        req = urllib.request.Request(
            f"http://{host}:{port}/command",
            data=json.dumps({"command": cmd}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return fn()


def report() -> dict:
    compiles = compile_all()
    files = structural()
    reqs = check_requirements()
    payload = {
        "when": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "files": files,
        "syntax": compiles,
        "requirements": reqs,
        "files_ok": all(r["ok"] for r in files),
        "syntax_ok": all(r["ok"] for r in compiles),
        "reqs_ok": reqs["ok"],
        "hashes": {
            str(p.relative_to(ROOT)): sha256_file(p)
            for p in EXPECTED
            if p.exists() and p.is_file()
        },
    }
    payload["ok"] = payload["files_ok"] and payload["syntax_ok"] and payload["reqs_ok"]
    return payload


def print_report(payload: dict) -> None:
    print("=" * 72)
    print("ULTIMATE COMMANDER OS — LIVE CHECK")
    print(payload["when"])
    print("root:", payload["root"])
    print("=" * 72)
    print("Struktur:", "OK" if payload["files_ok"] else "FEHLER")
    for row in payload["files"]:
        mark = "OK" if row["ok"] else "MISSING"
        print(f"  [{mark}] {row['path']}")
    print("Syntax:", "OK" if payload["syntax_ok"] else "FEHLER")
    for row in payload["syntax"]:
        if not row["ok"]:
            print(f"  [FAIL] {row['file']}: {row.get('error')}")
    print("requirements ifaddr:", "OK" if payload["reqs_ok"] else "FEHLER")
    print("GESAMT:", "GRÜN" if payload["ok"] else "ROT")


def interactive() -> int:
    payload = report()
    print_report(payload)
    print()
    print("1 Server neu starten")
    print("2 Cache leeren")
    print("3 UI / QML neu laden")
    print("4 GitHub-Status")
    print("5 Freigaben sticky")
    print("q Beenden")
    while True:
        try:
            key = input("Taste> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if key in {"q", "quit", "exit"}:
            return 0 if payload["ok"] else 1
        result = action(key)
        print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> int:
    if "--once" in sys.argv or os.environ.get("CI"):
        payload = report()
        print_report(payload)
        (ROOT / "test_report.txt").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return 0 if payload["ok"] else 1
    if len(sys.argv) > 1 and sys.argv[1] in {"1", "2", "3", "4", "5"}:
        print(json.dumps(action(sys.argv[1]), ensure_ascii=False, indent=2))
        return 0
    return interactive()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(2)
