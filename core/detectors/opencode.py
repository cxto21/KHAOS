"""OpenCode detector."""

from .base import BaseDetector, AgentSession


class OpenCodeDetector(BaseDetector):
    name = "opencode"

    def scan(self) -> list[AgentSession]:
        sessions = []
        pids = self._find_pids("opencode")
        for pid in pids:
            cmd = self._get_command(pid)
            if "opencode" not in cmd.lower():
                continue

            cwd = self._get_cwd(pid)
            sessions.append(AgentSession(
                agent="opencode",
                pid=pid,
                state="running",
                cwd=cwd,
                command=cmd,
            ))
        return sessions
