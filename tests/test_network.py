from __future__ import annotations

from pathlib import Path

from src.backend.network import list_adapters, net_status


def test_requirements_has_ifaddr_not_netifaces() -> None:
    text = (Path(__file__).resolve().parents[1] / "requirements.txt").read_text(encoding="utf-8-sig")
    pkgs = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert any(ln.startswith("ifaddr") for ln in pkgs)
    assert not any(ln.startswith("netifaces") for ln in pkgs)


def test_list_adapters_returns_list() -> None:
    adapters = list_adapters()
    assert isinstance(adapters, list)
    assert adapters
    assert "name" in adapters[0]


def test_net_status_shape() -> None:
    status = net_status()
    assert "online" in status
    assert "label" in status
    assert "bytes_sent" in status
