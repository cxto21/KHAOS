#!/usr/bin/env python3
"""KHAOS MCP Server — Bridge between agents and the supervisor daemon.

Provides MCP-compatible tools for agents to query system state.
"""

import json
import socket
import sys
from typing import Any


class KhaosMCPServer:
    """MCP server that bridges agents to the KHAOS daemon."""

    def __init__(self, daemon_socket: str = "/tmp/khaos/khaos.sock"):
        self.daemon_socket = daemon_socket

    def _query_daemon(self, action: str) -> dict[str, Any]:
        """Query the KHAOS daemon via Unix socket."""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.daemon_socket)
            sock.sendall(json.dumps({"action": action}).encode())
            response = sock.recv(8192).decode()
            sock.close()
            return json.loads(response)
        except (ConnectionRefusedError, FileNotFoundError):
            return {"status": "error", "message": "Daemon not running"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_tools(self) -> list[dict]:
        """Return MCP tool definitions."""
        return [
            {
                "name": "khaos_status",
                "description": "Get KHAOS supervisor status and running agents",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "khaos_sessions",
                "description": "List all active agent sessions",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "khaos_ping",
                "description": "Ping the KHAOS daemon",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        """Handle an MCP tool call."""
        if tool_name == "khaos_status":
            return self._query_daemon("status")
        elif tool_name == "khaos_sessions":
            return self._query_daemon("sessions")
        elif tool_name == "khaos_ping":
            return self._query_daemon("ping")
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def run_stdio(self):
        """Run MCP server over stdio (JSON-RPC)."""
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                if request.get("method") == "tools/list":
                    response = {"tools": self.get_tools()}
                elif request.get("method") == "tools/call":
                    params = request.get("params", {})
                    tool_name = params.get("name", "")
                    arguments = params.get("arguments", {})
                    response = self.handle_tool_call(tool_name, arguments)
                else:
                    response = {"error": "Unknown method"}

                result = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response,
                }
                print(json.dumps(result), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(json.dumps({"error": str(e)}), flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="KHAOS MCP Server")
    parser.add_argument("--socket", default="/tmp/khaos/khaos.sock")
    args = parser.parse_args()

    server = KhaosMCPServer(daemon_socket=args.socket)
    server.run_stdio()


if __name__ == "__main__":
    main()
