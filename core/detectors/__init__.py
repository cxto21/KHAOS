"""Agent detectors — each agent type has its own detector module."""

from .base import AgentSession, BaseDetector
from .claude import ClaudeDetector
from .codex import CodexDetector
from .opencode import OpenCodeDetector
from .gemini import GeminiDetector
from .cursor import CursorDetector

__all__ = [
    "AgentSession",
    "BaseDetector",
    "get_all_detectors",
]


def get_all_detectors() -> list[BaseDetector]:
    """Return all available detectors."""
    return [
        ClaudeDetector(),
        CodexDetector(),
        OpenCodeDetector(),
        GeminiDetector(),
        CursorDetector(),
    ]
