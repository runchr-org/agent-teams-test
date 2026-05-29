#!/usr/bin/env python3
"""Local dev server for the Ejentum Evaluation Module.

Serves demo.html and proxies the Ejentum gateway call server-side, so the
browser is not blocked by the gateway's missing CORS headers. The Ejentum
key travels browser -> localhost -> gateway only; it never touches a third
party.

Run:   python serve.py
Open:  http://localhost:8000/demo.html
"""
import http.server
import urllib.request
import urllib.error
import json

PORT = 8000
GATEWAY = "https://api.ejentum.com/harness/"


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
            with urllib.request.urlopen(req, timeout=240) as resp:
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
    httpd.serve_forever()
