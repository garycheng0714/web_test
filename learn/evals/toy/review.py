#!/usr/bin/env python3
"""Minimal review server for Lesson 0003. Stdlib only.

    python3 learn/evals/toy/review.py
    open http://localhost:8765

Annotations are written to toy/annotations.json on every change.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACES = HERE / "traces.jsonl"
ANNOTATIONS = HERE / "annotations.json"
STATIC = {"/": "review.html", "/review.css": "review.css", "/review.js": "review.js"}
MAX_BODY = 1_000_000


def load_traces():
    return [
        json.loads(line)
        for line in TRACES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_annotations():
    if not ANNOTATIONS.exists():
        return {}
    try:
        data = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_annotations(data):
    if not isinstance(data, dict):
        raise ValueError("annotations 必須是物件")
    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            raise ValueError("annotation 格式錯誤")
        if not all(isinstance(value.get(k, ""), str) for k in ("mode", "note")):
            raise ValueError("mode/note 必須是字串")
    tmp = ANNOTATIONS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(ANNOTATIONS)


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in STATIC:
            body = (HERE / STATIC[path]).read_bytes()
            ctype = (
                "text/html; charset=utf-8"
                if path == "/"
                else "text/css; charset=utf-8"
                if path.endswith(".css")
                else "text/javascript; charset=utf-8"
            )
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/traces":
            self.send_json(load_traces())
        elif path == "/api/annotations":
            self.send_json(load_annotations())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/annotations":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            self.send_error(413)
            return
        try:
            save_annotations(json.loads(self.rfile.read(length)))
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_json({"error": str(exc)}, status=400)
            return
        self.send_response(204)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"review app -> http://localhost:{port}")
    print("Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
