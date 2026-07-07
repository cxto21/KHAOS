"""Base detector interface and shared models."""

import os
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time


@dataclass
class AgentSession:
    """Represents a detected agent session."""
    agent: str
    pid: int
    state: str = "running"
    started_at: float = field(default_factory=time.time)
    cwd: str = ""
    command: str = ""
    extra: dict = field(default_factory=dict)


class BaseDetector(ABC):
    """Base class for agent detectors."""

    name: str = "unknown"

    @abstractmethod
    def scan(self) -> list[AgentSession]:
        """Scan for active agent sessions."""
        ...

    def _find_pids(self, pattern: str) -> list[int]:
        """Find PIDs matching a process name pattern."""
        pids = []
        try:
            result = subprocess.run(
                ["pgrep", "-f", pattern],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line:
                    pids.append(int(line))
        except (subprocess.TimeoutExpired, ValueError):
            pass
        return pids

    def _get_cwd(self, pid: int) -> str:
        """Get the working directory of a process."""
        try:
            return os.readlink(f"/proc/{pid}/cwd")
        except (OSError, FileNotFoundError):
            return ""

    def _get_command(self, pid: int) -> str:
        """Get the command line of a process."""
        try:
            with open(f"/proc/{pid}/cmdline", "r") as f:
                return f.read().replace("\x00", " ").strip()
        except (OSError, FileNotFoundError):
            return ""
