from __future__ import annotations

from src.backend.system_monitor import SystemMonitor


def test_snapshot_keys() -> None:
    snap = SystemMonitor().snapshot()
    for key in ("cpu", "ram", "disk", "hostname", "net", "cores"):
        assert key in snap
    assert 0 <= snap["cpu"] <= 100
    assert 0 <= snap["ram"] <= 100
