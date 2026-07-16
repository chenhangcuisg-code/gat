#!/usr/bin/env python3
"""mock_broker.py — a faithful TEST DOUBLE of the Hastur Operation broker.

Implements the same HTTP contract as the real Node/Express broker so you can
exercise `gop.py` (auth, targeting, request/response shape, error surfacing)
WITHOUT a running Godot editor:

  GET  /api/health                 -> 200 {"status":"ok"}            (no auth)
  GET  /api/executors   (Bearer)   -> 200 {"success":true,"data":[...]}
  POST /api/execute     (Bearer)   -> 200 {"success":true,"data":{...}}

It does NOT run real GDScript. It SIMULATES execution: a light "compiler" flags
obvious Python-isms, and `executeContext.output("k", expr)` calls are
regex-echoed back as outputs so responses look realistic. Use only for testing.

Run:  python mock_broker.py [--port 5302] [--token TESTTOKEN]
"""
import argparse
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

OUTPUT_RE = re.compile(r'executeContext\.output\(\s*"([^"]+)"\s*,\s*(.+?)\)\s*$', re.M)
PYISM_RE = re.compile(r'(^|\s)(def |elif :|True\b|False\b|None\b|print\([^)]*\bend=)')

EXECUTORS = [
    {"id": "ed-0001", "type": "editor", "project_name": "修仙放置 · Godot",
     "project_path": "C:/Users/User/idle-engines/xiuxian-godot", "connected": True},
    {"id": "gm-0002", "type": "game", "project_name": "修仙放置 · Godot",
     "project_path": "C:/Users/User/idle-engines/xiuxian-godot", "connected": True},
]


class Handler(BaseHTTPRequestHandler):
    token = "TESTTOKEN"

    def log_message(self, *a):
        sys.stderr.write("  mock-broker: " + (a[0] % a[1:]) + "\n")

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth_ok(self):
        h = self.headers.get("Authorization", "")
        return h == "Bearer " + self.token

    def do_GET(self):
        if self.path == "/api/health":
            return self._send(200, {"status": "ok", "uptime": 1})
        if self.path == "/api/executors":
            if not self._auth_ok():
                return self._send(401, {"success": False, "error": "unauthorized"})
            return self._send(200, {"success": True, "data": EXECUTORS})
        self._send(404, {"success": False, "error": "not found"})

    def do_POST(self):
        if self.path != "/api/execute":
            return self._send(404, {"success": False, "error": "not found"})
        if not self._auth_ok():
            return self._send(401, {"success": False, "error": "unauthorized"})
        n = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(n).decode() or "{}")
        except Exception:
            return self._send(400, {"success": False, "error": "bad json"})
        code = body.get("code", "")
        if not code.strip():
            return self._send(400, {"success": False, "error": "missing code"})
        if not any(k in body for k in ("executor_id", "project_name", "project_path")):
            return self._send(400, {"success": False, "error": "no target specified"})

        # simulate compile
        compile_err = ""
        if PYISM_RE.search(code):
            compile_err = "Parse error: looks like Python, not GDScript " \
                          "(def/True/False/None/print kwargs)"
        compile_ok = compile_err == ""
        run_ok = compile_ok
        outs = []
        if compile_ok:
            for k, expr in OUTPUT_RE.findall(code):
                outs.append([k, "<sim:" + expr.strip()[:40] + ">"])
            if not outs:
                outs = [["result", "ok (simulated)"]]
        self._send(200, {"success": True, "data": {
            "request_id": "mock-0001",
            "compile_success": compile_ok, "compile_error": compile_err,
            "run_success": run_ok, "run_error": "",
            "outputs": outs,
        }})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5302)
    ap.add_argument("--token", default="TESTTOKEN")
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    Handler.token = args.token
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[mock-broker] http://{args.host}:{args.port}  token={args.token}", flush=True)
    print("[mock-broker] endpoints: /api/health /api/executors /api/execute", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
