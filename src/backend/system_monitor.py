"""CPU / RAM / disk snapshots. Thread-safe, no GUI imports."""

from __future__ import annotations

import platform
import shutil
from typing import Any

import psutil

from .network import net_status


class SystemMonitor:
    def __init__(self) -> None:
        # Prime cpu_percent so the next call is non-blocking.
        psutil.cpu_percent(interval=None)

    def snapshot(self) -> dict[str, Any]:
        mem = psutil.virtual_memory()
        disk_root = "C:\\" if platform.system() == "Windows" else "/"
        try:
            disk = shutil.disk_usage(disk_root)
            disk_percent = round((disk.used / disk.total) * 100.0, 1) if disk.total else 0.0
            disk_free_gb = round(disk.free / (1024 ** 3), 1)
        except OSError:
            disk_percent = 0.0
            disk_free_gb = 0.0

        net = net_status()
        return {
            "cpu": float(psutil.cpu_percent(interval=None)),
            "ram": float(mem.percent),
            "ram_used_gb": round(mem.used / (1024 ** 3), 1),
            "ram_total_gb": round(mem.total / (1024 ** 3), 1),
            "disk": disk_percent,
            "disk_free_gb": disk_free_gb,
            "hostname": platform.node(),
            "system": f"{platform.system()} {platform.release()}",
            "cores": psutil.cpu_count() or 1,
            "net": net,
        }
