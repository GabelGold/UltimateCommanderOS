"""Ollama client with mock fallback when the daemon is missing."""

from __future__ import annotations

import os
from typing import Any

import requests


class OllamaClient:
    def __init__(self, base_url: str | None = None, timeout: float = 1.5) -> None:
        self.base_url = (base_url or os.environ.get("OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.timeout = timeout
        self.mock = False
        self.last_error = ""

    def health(self) -> dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            models = [m.get("name", "") for m in payload.get("models", [])]
            self.mock = False
            self.last_error = ""
            return {"ok": True, "mock": False, "models": models, "label": "Ollama online"}
        except Exception as exc:  # noqa: BLE001 — any failure must fall back
            self.mock = True
            self.last_error = f"{type(exc).__name__}: {exc}"
            return {
                "ok": True,
                "mock": True,
                "models": ["mock-llama"],
                "label": "Mock-Modus (Ollama nicht erreichbar)",
                "error": self.last_error,
            }

    def generate(self, prompt: str, model: str = "llama3") -> str:
        if not prompt.strip():
            return ""
        status = self.health()
        if status["mock"]:
            return f"[mock] {prompt[:240]}"
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=max(self.timeout, 30.0),
            )
            response.raise_for_status()
            return str(response.json().get("response", "")).strip()
        except Exception as exc:  # noqa: BLE001
            self.mock = True
            return f"[mock-fallback] {prompt[:240]} ({type(exc).__name__})"
