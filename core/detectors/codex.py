"""Codex CLI detector."""

from .base import BaseDetector, AgentSession


class CodexDetector(BaseDetector):
    name = "codex"

    def scan(self) -> list[AgentSession]:
        sessions = []
        pids = self._find_pids("codex")
        for pid in pids:
            cmd = self._get_command(pid)
            if "codex" not in cmd.lower():
                continue

            cwd = self._get_cwd(pid)
            sessions.append(AgentSession(
                agent="codex",
                pid=pid,
                state="running",
                cwd=cwd,
                command=cmd,
            ))
        return sessions
