"""Local secret bootstrap. Generates ENCRYPTION_KEY on first start."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"


def _read_env_key(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("ENCRYPTION_KEY="):
            return stripped.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def ensure_encryption_key(env_path: Path | None = None) -> str:
    """Return a 64-char hex key, creating .env if needed."""
    path = env_path or ENV_PATH
    existing = os.environ.get("ENCRYPTION_KEY", "").strip() or _read_env_key(path)
    if existing:
        os.environ["ENCRYPTION_KEY"] = existing
        return existing

    key = secrets.token_hex(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "ENCRYPTION_KEY=" in text:
            lines = []
            for line in text.splitlines():
                if line.strip().startswith("ENCRYPTION_KEY="):
                    lines.append(f"ENCRYPTION_KEY={key}")
                else:
                    lines.append(line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"\nENCRYPTION_KEY={key}\n")
    else:
        example = ROOT / ".env.example"
        if example.exists():
            body = example.read_text(encoding="utf-8")
            body = body.replace("ENCRYPTION_KEY=", f"ENCRYPTION_KEY={key}", 1)
            path.write_text(body, encoding="utf-8")
        else:
            path.write_text(
                "UCOS_HOST=127.0.0.1\n"
                "UCOS_PORT=8765\n"
                "OLLAMA_URL=http://127.0.0.1:11434\n"
                f"ENCRYPTION_KEY={key}\n"
                "GITHUB_REPO=GabelGold/UltimateCommanderOS\n",
                encoding="utf-8",
            )
    os.environ["ENCRYPTION_KEY"] = key
    return key
