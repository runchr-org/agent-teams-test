#!/usr/bin/env python3
"""Local dev server for the Ejentum Evaluation Module.

Serves demo.html and proxies the Ejentum gateway call server-side so the
browser is not blocked by the gateway's missing CORS headers. API keys
travel browser -> localhost -> gateway only, never to any third party.

Quickstart:
    python serve.py
    open http://localhost:8000/demo.html

Environment variables:
    PORT      override the listening port (default 8000)
    GATEWAY   override the Ejentum gateway URL (default points at the
              public Zuplo deployment). Useful for self-hosted gateways
              or staging endpoints.

Deploy in production:
    Any reverse proxy that forwards POST /ejentum-proxy to the Ejentum
    gateway and serves demo.html as a static file is equivalent. nginx,
    Caddy, Cloudflare Workers, etc. This script is the simplest reference
    implementation: stdlib-only, no install, no dependencies.
"""
import http.server
import os
import urllib.request
import urllib.error
import json

PORT = int(os.environ.get("PORT", "8000"))
GATEWAY = os.environ.get(
    "GATEWAY",
    "https://ejentum-main-ab125c3.zuplo.app/logicv1/",
)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") != "/ejentum-proxy":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        req = urllib.request.Request(
            GATEWAY,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": self.headers.get("Authorization", ""),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                status, data = resp.status, resp.read()
        except urllib.error.HTTPError as e:
            status, data = e.code, e.read()
        except Exception as e:
            status, data = 502, json.dumps({"error": str(e)}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    httpd = http.server.ThreadingHTTPServer(("", PORT), Handler)
    print("Ejentum Evaluation Module  ->  http://localhost:%d/demo.html" % PORT)
    print("                Gateway   ->  %s" % GATEWAY)
    print("Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
