"""Claude Code detector."""

from pathlib import Path
from .base import BaseDetector, AgentSession


class ClaudeDetector(BaseDetector):
    name = "claude"

    def scan(self) -> list[AgentSession]:
        sessions = []
        pids = self._find_pids("claude")
        for pid in pids:
            cmd = self._get_command(pid)
            if "claude" not in cmd.lower():
                continue

            cwd = self._get_cwd(pid)
            state = self._detect_state(cwd)

            sessions.append(AgentSession(
                agent="claude",
                pid=pid,
                state=state,
                cwd=cwd,
                command=cmd,
            ))
        return sessions

    def _detect_state(self, cwd: str) -> str:
        if not cwd:
            return "running"
        project_dir = Path(cwd)
        claude_dir = project_dir / ".claude"
        if claude_dir.exists():
            return "running"
        return "running"
