# KHAOS — Agent Instructions

You are building KHAOS, an AI Agent Supervisor for Linux.

## Stack
- Python 3 (daemon, detectors, MCP server)
- Shell scripts (infrastructure: guacamole, VNC, tunnels)
- HTML/JS (web dashboard)
- Unix sockets (IPC between components)

## Conventions
- All scripts use `set -euo pipefail`
- Python files use type hints
- Config via `.env` file, loaded by scripts
- Logs go to `/tmp/khaos/logs/`
- PID files go to `/tmp/khaos/pids/`

## Architecture Rules
- The daemon is the single source of truth for agent state
- Detectors are pluggable — one per agent type
- MCP server reads daemon state, never directly from agents
- Web dashboard polls daemon via Unix socket
- All IPC uses JSON over Unix sockets
