"""QObject bridge: system metrics → QML signals (Fluent dashboard)."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from .commander_api import request_ui_reload
from .ollama_client import OllamaClient
from .system_monitor import SystemMonitor


class DashboardBackend(QObject):
    cpuChanged = Signal(float)
    ramChanged = Signal(float)
    diskChanged = Signal(float)
    netChanged = Signal(str)
    netBytesChanged = Signal(float, float)
    hostnameChanged = Signal(str)
    systemChanged = Signal(str)
    ollamaChanged = Signal(str)
    statusChanged = Signal(str)
    reloadRequested = Signal(int)
    coresChanged = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._monitor = SystemMonitor()
        self._ollama = OllamaClient()
        self._cpu = 0.0
        self._ram = 0.0
        self._disk = 0.0
        self._net = "offline"
        self._sent = 0.0
        self._recv = 0.0
        self._hostname = ""
        self._system = ""
        self._ollama_label = "…"
        self._status = "boot"
        self._cores = 1
        self._reload_token = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self.refresh()

    @Property(float, notify=cpuChanged)
    def cpu(self) -> float:
        return self._cpu

    @Property(float, notify=ramChanged)
    def ram(self) -> float:
        return self._ram

    @Property(float, notify=diskChanged)
    def disk(self) -> float:
        return self._disk

    @Property(str, notify=netChanged)
    def net(self) -> str:
        return self._net

    @Property(str, notify=hostnameChanged)
    def hostname(self) -> str:
        return self._hostname

    @Property(str, notify=systemChanged)
    def system(self) -> str:
        return self._system

    @Property(str, notify=ollamaChanged)
    def ollama(self) -> str:
        return self._ollama_label

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(int, notify=coresChanged)
    def cores(self) -> int:
        return self._cores

    @Slot()
    def refresh(self) -> None:
        snap = self._monitor.snapshot()
        self._cpu = float(snap["cpu"])
        self._ram = float(snap["ram"])
        self._disk = float(snap["disk"])
        self._net = str(snap["net"]["label"])
        self._sent = float(snap["net"]["bytes_sent"]) / (1024 * 1024)
        self._recv = float(snap["net"]["bytes_recv"]) / (1024 * 1024)
        self._hostname = str(snap["hostname"])
        self._system = str(snap["system"])
        self._cores = int(snap["cores"])
        health = self._ollama.health()
        self._ollama_label = str(health["label"])
        self._status = "ready"
        self.cpuChanged.emit(self._cpu)
        self.ramChanged.emit(self._ram)
        self.diskChanged.emit(self._disk)
        self.netChanged.emit(self._net)
        self.netBytesChanged.emit(self._sent, self._recv)
        self.hostnameChanged.emit(self._hostname)
        self.systemChanged.emit(self._system)
        self.ollamaChanged.emit(self._ollama_label)
        self.coresChanged.emit(self._cores)
        self.statusChanged.emit(self._status)

    @Slot()
    def reloadUi(self) -> None:
        result = request_ui_reload()
        self._reload_token = int(result["reload_token"])
        self.reloadRequested.emit(self._reload_token)
        self._status = f"ui reload #{self._reload_token}"
        self.statusChanged.emit(self._status)

    @Slot(str, result=str)
    def ask(self, prompt: str) -> str:
        return self._ollama.generate(prompt)
