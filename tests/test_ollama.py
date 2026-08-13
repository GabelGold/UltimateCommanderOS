from __future__ import annotations

from src.backend.ollama_client import OllamaClient


def test_health_never_raises() -> None:
    client = OllamaClient(base_url="http://127.0.0.1:9", timeout=0.2)
    health = client.health()
    assert health["ok"] is True
    assert health["mock"] is True
    assert "Mock" in health["label"] or "mock" in health["label"].lower()


def test_generate_mock() -> None:
    client = OllamaClient(base_url="http://127.0.0.1:9", timeout=0.2)
    text = client.generate("ping")
    assert "ping" in text
