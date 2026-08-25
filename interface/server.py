#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = int(os.environ.get("TAMMY_V2_PORT", "4173"))
# The existing Vinext Tammy runtime on macOS binds to IPv6 loopback (::1).
# Use the explicit IPv6 literal by default so the bridge reaches the live API
# reliably instead of depending on localhost/IPv4 resolution order.
BACKEND_URL = os.environ.get("TAMMY_BACKEND_URL", "http://[::1]:3000/api/tammy")
ROOT = Path(__file__).resolve().parent

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        original = super().translate_path(path)
        rel = os.path.relpath(original, os.getcwd())
        return str(ROOT / rel)

    def do_POST(self):
        if self.path != "/api/tammy":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)

        request = urllib.request.Request(
            BACKEND_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as upstream:
                data = upstream.read()
                self.send_response(upstream.status)
                self.send_header("Content-Type", upstream.headers.get("Content-Type", "application/json"))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            data = exc.read() or json.dumps({"error": f"Tammy backend returned {exc.code}"}).encode()
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:
            data = json.dumps({
                "error": f"Could not reach Tammy backend at {BACKEND_URL}: {exc}"
            }).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

if __name__ == "__main__":
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Tammy v2 interface: http://localhost:{PORT}")
    print(f"Proxying live Tammy requests to: {BACKEND_URL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Tammy v2.")
