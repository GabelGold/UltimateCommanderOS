"""Local command HTTP API (127.0.0.1). Used by live_check and the dashboard."""

from __future__ import annotations

import json
import os
import shutil
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "cache"
LOGS = ROOT / "logs"

_state: dict[str, Any] = {
    "server": None,
    "thread": None,
    "reload_token": 0,
    "sticky_shares": False,
    "last_command": "",
}


def _json(handler: BaseHTTPRequestHandler, code: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def clear_cache() -> dict[str, Any]:
    removed = 0
    for folder in (CACHE, ROOT / "__pycache__", ROOT / "src" / "__pycache__"):
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
            removed += 1
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)
        removed += 1
    for path in ROOT.rglob("*.qmlc"):
        try:
            path.unlink()
            removed += 1
        except OSError:
            pass
    CACHE.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "removed": removed, "action": "cache_cleared"}


def request_ui_reload() -> dict[str, Any]:
    _state["reload_token"] = int(_state.get("reload_token", 0)) + 1
    return {"ok": True, "reload_token": _state["reload_token"], "action": "ui_reload"}


def github_status() -> dict[str, Any]:
    import urllib.request

    repo = os.environ.get("GITHUB_REPO", "GabelGold/UltimateCommanderOS")
    url = f"https://api.github.com/repos/{repo}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UltimateCommanderOS"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {
            "ok": True,
            "repo": repo,
            "private": data.get("private"),
            "default_branch": data.get("default_branch"),
            "html_url": data.get("html_url"),
            "pushed_at": data.get("pushed_at"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "repo": repo, "error": f"{type(exc).__name__}: {exc}"}


def make_shares_sticky() -> dict[str, Any]:
    """Persist SMB share visibility on Windows. No-op / recorded elsewhere."""
    _state["sticky_shares"] = True
    note = "sticky flag set"
    if os.name == "nt":
        try:
            import subprocess

            result = subprocess.run(
                ["net", "config", "server"],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            note = (result.stdout or result.stderr or note)[:400]
        except Exception as exc:  # noqa: BLE001
            note = f"{type(exc).__name__}: {exc}"
    return {"ok": True, "sticky_shares": True, "note": note, "action": "shares_sticky"}


COMMANDS: dict[str, Callable[[], dict[str, Any]]] = {
    "clear_cache": clear_cache,
    "reload_ui": request_ui_reload,
    "github_status": github_status,
    "shares_sticky": make_shares_sticky,
}


class CommanderHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/health"}:
            _json(self, 200, {"ok": True, "service": "ultimate-commander", "reload_token": _state["reload_token"]})
            return
        if path == "/status":
            from .system_monitor import SystemMonitor
            from .ollama_client import OllamaClient

            snap = SystemMonitor().snapshot()
            ollama = OllamaClient().health()
            _json(
                self,
                200,
                {
                    "ok": True,
                    "snapshot": snap,
                    "ollama": ollama,
                    "reload_token": _state["reload_token"],
                    "sticky_shares": _state["sticky_shares"],
                    "last_command": _state["last_command"],
                },
            )
            return
        _json(self, 404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/command", "/cmd"}:
            _json(self, 404, {"ok": False, "error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            data = json.loads(raw) if raw.strip().startswith("{") else {"command": raw}
        except json.JSONDecodeError:
            data = {"command": raw}
        command = str(data.get("command") or data.get("cmd") or "").strip()
        _state["last_command"] = command
        action = COMMANDS.get(command)
        if action is None:
            _json(self, 400, {"ok": False, "error": f"unknown command: {command}"})
            return
        _json(self, 200, action())

    def log_message(self, fmt: str, *args: Any) -> None:
        LOGS.mkdir(parents=True, exist_ok=True)
        line = "HTTP " + (fmt % args)
        with (LOGS / "commander.log").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def start_http(host: str | None = None, port: int | None = None) -> ThreadingHTTPServer:
    if _state["server"] is not None:
        return _state["server"]
    host = host or os.environ.get("UCOS_HOST", "127.0.0.1")
    port = int(port or os.environ.get("UCOS_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), CommanderHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="ucos-api")
    thread.start()
    _state["server"] = server
    _state["thread"] = thread
    return server


def stop_http() -> dict[str, Any]:
    server = _state.get("server")
    if server is None:
        return {"ok": True, "action": "already_stopped"}
    server.shutdown()
    server.server_close()
    _state["server"] = None
    _state["thread"] = None
    return {"ok": True, "action": "stopped"}


def restart_http() -> dict[str, Any]:
    stop_http()
    server = start_http()
    host, port = server.server_address[:2]
    return {"ok": True, "action": "restarted", "url": f"http://{host}:{port}"}
