# KHAOS

**AI Agent Supervisor for Linux** — system-level intelligence for coding agents.

KHAOS monitors your AI coding agents, provides a live web dashboard, and gives agents a bridge to communicate with the system. Think of it as [Open Island](https://github.com/Octane0411/open-vibe-island) for Linux — but built to scale to multi-platform and multi-device.

## What it does

- **Agent Monitoring** — detects and tracks Claude Code, Codex, OpenCode, Gemini CLI, Cursor sessions
- **Live Dashboard** — web UI showing agent status, sessions, and system health
- **MCP Bridge** — agents can query the supervisor about system state
- **Remote Access** — Guacamole + Cloudflare tunnel for browser-based desktop access
- **Hook Protocol** — standardized event system for agent integration

## Quick Start

```bash
git clone https://github.com/cxto21/KHAOS.git
cd KHAOS
cp .env.example .env
nano .env  # set your passwords
./run
```

Then open the URL shown in the output (local or Cloudflare tunnel).

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  KHAOS Core                      │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Daemon   │  │MCP Server│  │  Dashboard   │  │
│  │ (monitor) │  │ (bridge) │  │  (web UI)    │  │
│  └─────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│        │              │               │           │
│  ┌─────┴──────────────┴───────────────┴───────┐  │
│  │           Hook Protocol (IPC)              │  │
│  └────────────────────────────────────────────┘  │
│        │              │               │           │
│  ┌─────┴─────┐  ┌────┴────┐  ┌───────┴───────┐  │
│  │Claude Code│  │  Codex  │  │   OpenCode    │  │
│  │  detector │  │detector │  │   detector    │  │
│  └───────────┘  └─────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│              Infrastructure Layer                │
│  Xvfb + fluxbox + x11vnc + Guacamole + CF tunnel│
└─────────────────────────────────────────────────┘
```

## Supported Agents

| Agent | Status | Integration |
|-------|--------|-------------|
| Claude Code | ✅ Supported | Hook + process detection |
| Codex CLI | ✅ Supported | Hook + process detection |
| OpenCode | ✅ Supported | JS plugin + process detection |
| Gemini CLI | ✅ Supported | Hook + process detection |
| Cursor | ✅ Supported | Hook + process detection |

## Project Structure

```
KHAOS/
├── core/                 # Agent monitoring daemon
│   ├── daemon.py         # Main daemon loop
│   ├── detectors/        # Agent-specific detectors
│   └── ipc.py            # Unix socket IPC
├── mcp/                  # MCP server bridge
│   └── server.py
├── web/                  # Dashboard UI
│   ├── index.html
│   └── api.py
├── run                   # Main entry point
├── stop                  # Stop all services
├── status                # Show status
├── .env.example          # Configuration template
└── README.md
```

## Roadmap

- [x] Phase 1: Linux MVP — agent monitoring + web dashboard
- [ ] Phase 2: MCP server + browser automation
- [ ] Phase 3: Multi-platform (macOS, Windows)
- [ ] Phase 4: Intelligence layer (system monitoring, autonomy)

## License

MIT
