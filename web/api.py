#!/usr/bin/env python3
"""Simple HTTP API server for the KHAOS dashboard."""

import json
import os
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class KhaosAPIHandler(SimpleHTTPRequestHandler):
    """HTTP handler with API endpoints."""

    daemon_socket = os.environ.get("KHAOS_SOCKET", "/tmp/khaos/khaos.sock")

    def do_GET(self):
        if self.path == "/api/status":
            self._proxy_to_daemon("status")
        elif self.path == "/api/sessions":
            self._proxy_to_daemon("sessions")
        elif self.path == "/api/ping":
            self._proxy_to_daemon("ping")
        elif self.path == "/" or self.path == "/index.html":
            self._serve_file("index.html")
        else:
            super().do_GET()

    def _proxy_to_daemon(self, action: str):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.daemon_socket)
            sock.sendall(json.dumps({"action": action}).encode())
            response = sock.recv(8192).decode()
            sock.close()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.encode())
        except Exception as e:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _serve_file(self, filename: str):
        web_dir = Path(__file__).parent
        filepath = web_dir / filename
        if filepath.exists():
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(filepath.read_bytes())
        else:
            self.send_response(404)
            self.end_headers()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--socket", default="/tmp/khaos/khaos.sock")
    args = parser.parse_args()

    os.environ["KHAOS_SOCKET"] = args.socket
    KhaosAPIHandler.daemon_socket = args.socket

    server = HTTPServer(("0.0.0.0", args.port), KhaosAPIHandler)
    print(f"KHAOS dashboard: http://localhost:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
