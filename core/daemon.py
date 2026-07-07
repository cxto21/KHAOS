#!/usr/bin/env python3
"""KHAOS Agent Supervisor — Core Daemon

Monitors AI coding agents, tracks sessions, and exposes state via Unix socket.
"""

import argparse
import json
import logging
import os
import signal
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any

from .detectors import get_all_detectors, AgentSession

logger = logging.getLogger("khaos.daemon")


class KhaosDaemon:
    """Main daemon that monitors agents and serves state over Unix socket."""

    def __init__(self, socket_path: str, log_level: str = "INFO"):
        self.socket_path = socket_path
        self.state_dir = Path("/tmp/khaos/states")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.running = False
        self.sessions: dict[str, AgentSession] = {}
        self.detectors = get_all_detectors()
        self._lock = threading.Lock()

        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    def start(self):
        """Start the daemon."""
        self.running = True
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        logger.info("KHAOS daemon starting...")
        logger.info(f"Socket: {self.socket_path}")
        logger.info(f"Detectors: {[d.name for d in self.detectors]}")

        server_thread = threading.Thread(target=self._socket_server, daemon=True)
        server_thread.start()

        self._scan_loop()

    def _scan_loop(self):
        """Main scan loop — detect agent sessions."""
        while self.running:
            try:
                new_sessions: dict[str, AgentSession] = {}
                for detector in self.detectors:
                    sessions = detector.scan()
                    for session in sessions:
                        key = f"{session.agent}:{session.pid}"
                        new_sessions[key] = session

                        with self._lock:
                            if key not in self.sessions:
                                logger.info(f"New session: {session.agent} (PID {session.pid})")
                                self._emit_event("session_started", session)
                            elif self.sessions[key].state != session.state:
                                logger.info(
                                    f"State change: {session.agent} "
                                    f"{self.sessions[key].state} -> {session.state}"
                                )
                                self._emit_event("state_changed", session)

                with self._lock:
                    for key, old_session in self.sessions.items():
                        if key not in new_sessions:
                            logger.info(f"Session ended: {old_session.agent} (PID {old_session.pid})")
                            self._emit_event("session_ended", old_session)

                    self.sessions = new_sessions
                    self._save_state()

            except Exception as e:
                logger.error(f"Scan error: {e}")

            time.sleep(2)

    def _socket_server(self):
        """Unix socket server for IPC."""
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.socket_path)
        server.listen(5)
        server.settimeout(1.0)

        while self.running:
            try:
                conn, _ = server.accept()
                data = conn.recv(4096).decode()
                response = self._handle_request(json.loads(data))
                conn.sendall(json.dumps(response).encode())
                conn.close()
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Socket error: {e}")

        server.close()

    def _handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle an IPC request."""
        action = request.get("action", "")

        if action == "status":
            with self._lock:
                agents = {
                    k: {
                        "agent": s.agent,
                        "pid": s.pid,
                        "state": s.state,
                        "started_at": s.started_at,
                        "cwd": s.cwd,
                        "command": s.command,
                    }
                    for k, s in self.sessions.items()
                }
            return {"status": "ok", "agents": agents, "detector_count": len(self.detectors)}

        elif action == "sessions":
            with self._lock:
                sessions_list = [
                    {
                        "agent": s.agent,
                        "pid": s.pid,
                        "state": s.state,
                        "started_at": s.started_at,
                        "cwd": s.cwd,
                    }
                    for s in self.sessions.values()
                ]
            return {"status": "ok", "sessions": sessions_list}

        elif action == "ping":
            return {"status": "ok", "pong": True}

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def _emit_event(self, event_type: str, session: AgentSession):
        """Emit an event to the events log."""
        event = {
            "type": event_type,
            "agent": session.agent,
            "pid": session.pid,
            "state": session.state,
            "timestamp": time.time(),
        }
        event_path = self.state_dir / "events.jsonl"
        with open(event_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def _save_state(self):
        """Persist current state to disk."""
        state = {
            "timestamp": time.time(),
            "sessions": {
                k: {
                    "agent": s.agent,
                    "pid": s.pid,
                    "state": s.state,
                    "started_at": s.started_at,
                    "cwd": s.cwd,
                }
                for k, s in self.sessions.items()
            },
        }
        state_path = self.state_dir / "daemon.json"
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False


def main():
    parser = argparse.ArgumentParser(description="KHAOS Agent Supervisor Daemon")
    parser.add_argument("--socket", default="/tmp/khaos/khaos.sock", help="Unix socket path")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    args = parser.parse_args()

    daemon = KhaosDaemon(socket_path=args.socket, log_level=args.log_level)
    daemon.start()


if __name__ == "__main__":
    main()
