"""Gemini CLI detector."""

from .base import BaseDetector, AgentSession


class GeminiDetector(BaseDetector):
    name = "gemini"

    def scan(self) -> list[AgentSession]:
        sessions = []
        pids = self._find_pids("gemini")
        for pid in pids:
            cmd = self._get_command(pid)
            if "gemini" not in cmd.lower():
                continue

            cwd = self._get_cwd(pid)
            sessions.append(AgentSession(
                agent="gemini",
                pid=pid,
                state="running",
                cwd=cwd,
                command=cmd,
            ))
        return sessions
