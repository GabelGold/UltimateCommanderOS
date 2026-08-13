from __future__ import annotations

from pathlib import Path

from src.backend.security import ensure_encryption_key


def test_key_generated_once() -> None:
    folder = Path(__file__).resolve().parents[1] / "cache" / "test-tmp"
    folder.mkdir(parents=True, exist_ok=True)
    env = folder / ".env"
    if env.exists():
        env.unlink()
    first = ensure_encryption_key(env)
    second = ensure_encryption_key(env)
    assert first == second
    assert len(first) == 64
    assert "ENCRYPTION_KEY=" in env.read_text(encoding="utf-8")
