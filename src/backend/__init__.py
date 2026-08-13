"""Backend services for Ultimate Commander OS."""

from .Dashboard import DashboardBackend
from .network import list_adapters, net_status
from .ollama_client import OllamaClient
from .security import ensure_encryption_key
from .system_monitor import SystemMonitor

__all__ = [
    "DashboardBackend",
    "SystemMonitor",
    "list_adapters",
    "net_status",
    "OllamaClient",
    "ensure_encryption_key",
]
