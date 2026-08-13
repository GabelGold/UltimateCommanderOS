"""Network adapters via ifaddr (no netifaces / C compiler)."""

from __future__ import annotations

from typing import Any

import psutil

try:
    import ifaddr
except ImportError:  # pragma: no cover - fallback if wheel missing
    ifaddr = None


def list_adapters() -> list[dict[str, Any]]:
    adapters: list[dict[str, Any]] = []
    if ifaddr is None:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        for name, nic_addrs in addrs.items():
            ips = [a.address for a in nic_addrs if a.family.name in {"AF_INET", "AF_INET6"}]
            up = bool(stats.get(name) and stats[name].isup)
            adapters.append({"name": name, "ips": ips, "up": up})
        return adapters

    stats = psutil.net_if_stats()
    for adapter in ifaddr.get_adapters():
        ips = [ip.ip if isinstance(ip.ip, str) else str(ip.ip[0]) for ip in adapter.ips]
        name = adapter.nice_name or adapter.name
        up = bool(stats.get(name) and stats[name].isup)
        adapters.append({"name": name, "ips": ips, "up": up})
    return adapters


def net_status() -> dict[str, Any]:
    adapters = list_adapters()
    up_count = sum(1 for a in adapters if a.get("up"))
    io = psutil.net_io_counters()
    primary = next((a["name"] for a in adapters if a.get("up") and a.get("ips")), "offline")
    return {
        "online": up_count > 0,
        "adapters": adapters,
        "up_count": up_count,
        "primary": primary,
        "bytes_sent": int(getattr(io, "bytes_sent", 0)),
        "bytes_recv": int(getattr(io, "bytes_recv", 0)),
        "label": f"{primary} · {up_count} up" if up_count else "offline",
    }
