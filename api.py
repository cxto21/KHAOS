#!/usr/bin/env python3
"""KHAOS Island — API server with terminal exec, VNC proxy, and daemon bridge."""

import json
import os
import socket
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import urlopen


class IslandHandler(BaseHTTPRequestHandler):
    daemon_socket = os.environ.get("KHAOS_DAEMON_SOCKET", "/tmp/khaos/khaos.sock")
    web_dir = Path(__file__).parent

    def do_GET(self):
        if self.path == "/api/status":
            self._daemon_query("status")
        elif self.path == "/api/sessions":
            self._daemon_query("sessions")
        elif self.path == "/api/ping":
            self._daemon_query("ping")
        elif self.path == "/" or self.path == "/index.html":
            self._serve("island.html")
        elif self.path == "/terminal":
            self._serve("terminal.html")
        elif self.path == "/vnc.html" or self.path.startswith("/vnc"):
            self._proxy("http://127.0.0.1:6080", self.path)
        elif self.path.startswith("/websockify") or self.path.endswith(".js") or self.path.endswith(".css"):
            self._proxy("http://127.0.0.1:6080", self.path)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/exec":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            cmd = body.get("command", "")
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=30
                )
                self._json(200, {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                })
            except subprocess.TimeoutExpired:
                self._json(200, {"stdout": "", "stderr": "Command timed out", "returncode": -1})
            except Exception as e:
                self._json(500, {"stdout": "", "stderr": str(e), "returncode": -1})
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _daemon_query(self, action):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect(self.daemon_socket)
            sock.sendall(json.dumps({"action": action}).encode())
            response = sock.recv(8192).decode()
            sock.close()
            self._json(200, json.loads(response))
        except Exception as e:
            self._json(503, {"error": str(e)})

    def _proxy(self, base, path):
        try:
            resp = urlopen(f"{base}{path}", timeout=5)
            data = resp.read()
            ct = resp.headers.get("Content-Type", "text/html")
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self.send_response(502)
            self.end_headers()

    def _serve(self, filename):
        fp = self.web_dir / filename
        if fp.exists():
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(fp.read_bytes())
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--socket", default="/tmp/khaos/khaos.sock")
    args = parser.parse_args()

    IslandHandler.daemon_socket = args.socket
    server = HTTPServer(("0.0.0.0", args.port), IslandHandler)
    print(f"KHAOS Island: http://localhost:{args.port}")
    server.serve_forever()
