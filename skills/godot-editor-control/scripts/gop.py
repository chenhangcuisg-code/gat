#!/usr/bin/env python3
"""gop.py — Godot OPeration client for the Hastur Operation Plugin broker.

Drive a *running* Godot editor (or game) by sending GDScript over the Hastur
broker's REST API. Wraps the three endpoints:

  GET  /api/health                      -> liveness (no auth)
  GET  /api/executors        (Bearer)   -> list connected editors/games
  POST /api/execute          (Bearer)   -> run GDScript in a target instance
        body: {code, executor_id|project_name|project_path, type?}

High level: `gop.py op <name> --set k=v ...` renders a GDScript template from
`gdscript/ops/<name>.gd` and executes it (use --dry-run to just print the code).

Config resolution (first found wins):
  --broker / $HASTUR_BASE_URL   (default http://localhost:5302)
  --token  / $HASTUR_AUTH_TOKEN
  ./.hastur.json  or  ~/.hastur.json   {"broker","token","project_name","project_path"}

Stdlib only (urllib) — no third-party deps.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPS_DIR = os.path.join(SKILL_DIR, "gdscript", "ops")
MANIFEST = os.path.join(OPS_DIR, "manifest.json")
DEFAULT_BROKER = "http://localhost:5302"
TOKEN_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


# --------------------------------------------------------------- config
def load_config(args):
    cfg = {"broker": DEFAULT_BROKER, "token": None,
           "project_name": None, "project_path": None}
    for path in (os.path.join(os.getcwd(), ".hastur.json"),
                 os.path.expanduser("~/.hastur.json")):
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    cfg.update({k: v for k, v in json.load(f).items() if v})
            except Exception as e:
                print(f"warn: bad config {path}: {e}", file=sys.stderr)
            break
    cfg["broker"] = args.broker or os.environ.get("HASTUR_BASE_URL") or cfg["broker"]
    cfg["token"] = args.token or os.environ.get("HASTUR_AUTH_TOKEN") or cfg["token"]
    cfg["broker"] = cfg["broker"].rstrip("/")
    return cfg


def build_target(args, cfg, need=True):
    """Exactly one of executor_id/project_name/project_path (+ optional type)."""
    t = {}
    if args.executor_id:
        t["executor_id"] = args.executor_id
    elif args.project_name or cfg.get("project_name"):
        t["project_name"] = args.project_name or cfg["project_name"]
    elif args.project_path or cfg.get("project_path"):
        t["project_path"] = args.project_path or cfg["project_path"]
    elif need:
        raise SystemExit("error: no target - pass --executor-id / --project-name / "
                         "--project-path (or set one in .hastur.json)")
    if getattr(args, "type", None):
        t["type"] = args.type
    return t


# --------------------------------------------------------------- http
def request(cfg, method, path, body=None, auth=True, timeout=30):
    url = cfg["broker"] + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if auth:
        if not cfg["token"]:
            raise SystemExit("error: no auth token - pass --token or set "
                             "$HASTUR_AUTH_TOKEN / .hastur.json (printed by the broker)")
        req.add_header("Authorization", "Bearer " + cfg["token"])
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {"success": False, "error": e.reason}
    except urllib.error.URLError as e:
        raise SystemExit(f"error: cannot reach broker {url}: {e.reason}\n"
                         f"  is the broker running?  cd broker-server && npm run dev")


# --------------------------------------------------------------- render
def render_op(name, sets):
    path = os.path.join(OPS_DIR, name + ".gd")
    if not os.path.isfile(path):
        raise SystemExit(f"error: unknown op '{name}'  (try: gop.py op --list)")
    with open(path, encoding="utf-8") as f:
        code = f.read()
    needed = set(TOKEN_RE.findall(code))
    missing = needed - set(sets)
    if missing:
        raise SystemExit(f"error: op '{name}' needs --set for: {', '.join(sorted(missing))}")
    return TOKEN_RE.sub(lambda m: sets[m.group(1)], code)


def list_ops():
    man = {}
    if os.path.isfile(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            man = json.load(f)
    if not os.path.isdir(OPS_DIR):
        print("(no ops dir)"); return
    for fn in sorted(os.listdir(OPS_DIR)):
        if not fn.endswith(".gd"):
            continue
        name = fn[:-3]
        with open(os.path.join(OPS_DIR, fn), encoding="utf-8") as f:
            toks = sorted(set(TOKEN_RE.findall(f.read())))
        info = man.get(name, {})
        print(f"  {name:<18} {info.get('desc','')}")
        if toks:
            ex = info.get("params", {})
            parts = [f"{t}={ex.get(t, '<val>')}" for t in toks]
            print(f"      params: " + "  ".join(parts))


# --------------------------------------------------------------- output
def print_exec(status, resp):
    if status != 200 or not resp.get("success", False):
        print(f"[HTTP {status}] request failed: "
              f"{resp.get('error') or resp.get('message') or resp}")
        return 2
    d = resp.get("data", {})
    cs, rs = d.get("compile_success"), d.get("run_success")
    print(f"compile: {'OK' if cs else 'FAIL'}    run: {'OK' if rs else 'FAIL'}"
          f"    (request_id {d.get('request_id','-')})")
    if d.get("compile_error"):
        print("  compile_error: " + str(d["compile_error"]))
    if d.get("run_error"):
        print("  run_error: " + str(d["run_error"]))
    outs = d.get("outputs") or []
    if outs:
        print("  outputs:")
        for kv in outs:
            if isinstance(kv, (list, tuple)) and len(kv) == 2:
                print(f"    {kv[0]} = {kv[1]}")
            else:
                print(f"    {kv}")
    return 0 if (cs and rs) else 1


# --------------------------------------------------------------- commands
def cmd_health(args, cfg):
    status, resp = request(cfg, "GET", "/api/health", auth=False)
    print(f"[HTTP {status}] {json.dumps(resp, ensure_ascii=False)}")
    return 0 if status == 200 else 2


def cmd_executors(args, cfg):
    status, resp = request(cfg, "GET", "/api/executors")
    if status != 200:
        print(f"[HTTP {status}] {resp}"); return 2
    items = resp.get("data", resp) if isinstance(resp, dict) else resp
    if isinstance(items, dict):
        items = items.get("executors", items)
    print(json.dumps(items, ensure_ascii=False, indent=2))
    return 0


def _do_exec(cfg, code, target, dry_run, timeout):
    if dry_run:
        print("# ---- GDScript that would be sent ----")
        print(code)
        print("# ---- target ----")
        print(json.dumps(target, ensure_ascii=False))
        return 0
    body = dict(target); body["code"] = code
    status, resp = request(cfg, "POST", "/api/execute", body=body, timeout=timeout)
    return print_exec(status, resp)


def cmd_exec(args, cfg):
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        code = sys.stdin.read()
    if not code.strip():
        raise SystemExit("error: empty code (pass --code, --file, or stdin)")
    target = build_target(args, cfg, need=not args.dry_run)
    return _do_exec(cfg, code, target, args.dry_run, args.timeout)


def cmd_op(args, cfg):
    if args.list or not args.name:
        list_ops(); return 0
    sets = {}
    for kv in args.set or []:
        if "=" not in kv:
            raise SystemExit(f"error: --set expects key=value, got '{kv}'")
        k, v = kv.split("=", 1)
        sets[k.strip()] = v
    code = render_op(args.name, sets)
    target = build_target(args, cfg, need=not args.dry_run)
    return _do_exec(cfg, code, target, args.dry_run, args.timeout)


def main():
    p = argparse.ArgumentParser(description="Godot editor control via Hastur broker")
    p.add_argument("--broker", help=f"broker base URL (default {DEFAULT_BROKER})")
    p.add_argument("--token", help="bearer auth token")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_target(sp):
        sp.add_argument("--executor-id")
        sp.add_argument("--project-name")
        sp.add_argument("--project-path")
        sp.add_argument("--type", choices=["editor", "game"])
        sp.add_argument("--timeout", type=int, default=30)
        sp.add_argument("--dry-run", action="store_true",
                        help="print the GDScript/target instead of sending")

    sp = sub.add_parser("health", help="GET /api/health");
    sp.set_defaults(func=cmd_health)
    sp = sub.add_parser("executors", help="GET /api/executors")
    sp.set_defaults(func=cmd_executors)

    sp = sub.add_parser("exec", help="POST raw GDScript")
    sp.add_argument("--code"); sp.add_argument("--file")
    add_target(sp); sp.set_defaults(func=cmd_exec)

    sp = sub.add_parser("op", help="run a named operation template")
    sp.add_argument("name", nargs="?")
    sp.add_argument("--set", action="append", metavar="k=v")
    sp.add_argument("--list", action="store_true", help="list available ops")
    add_target(sp); sp.set_defaults(func=cmd_op)

    args = p.parse_args()
    cfg = load_config(args)
    sys.exit(args.func(args, cfg))


if __name__ == "__main__":
    main()
