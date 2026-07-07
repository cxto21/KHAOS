"""Cursor detector."""

from .base import BaseDetector, AgentSession


class CursorDetector(BaseDetector):
    name = "cursor"

    def scan(self) -> list[AgentSession]:
        sessions = []
        pids = self._find_pids("cursor")
        for pid in pids:
            cmd = self._get_command(pid)
            if "cursor" not in cmd.lower():
                continue

            cwd = self._get_cwd(pid)
            sessions.append(AgentSession(
                agent="cursor",
                pid=pid,
                state="running",
                cwd=cwd,
                command=cmd,
            ))
        return sessions
