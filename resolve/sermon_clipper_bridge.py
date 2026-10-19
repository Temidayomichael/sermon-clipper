"""Sermon Clipper bridge for DaVinci Resolve (works in the free version).

Start it from Resolve: Workspace > Scripts > Utility > sermon_clipper_bridge.
It watches <project>/resolve/inbox for command files (*.py), runs each one inside Resolve with
`resolve` available, and writes the result to resolve/outbox/<name>.json. Only that folder is read.
It stops after 3 hours, or when it receives a command file named stop.py.
"""
import json
import os
import time
import traceback

ROOT = "__SERMON_CLIPPER_ROOT__/resolve"  # filled in by ./clip resolve-install
INBOX = os.path.join(ROOT, "inbox")
OUTBOX = os.path.join(ROOT, "outbox")
os.makedirs(INBOX, exist_ok=True)
os.makedirs(OUTBOX, exist_ok=True)

try:
    resolve  # provided when run from the Workspace > Scripts menu
except NameError:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")

with open(os.path.join(OUTBOX, "_status.json"), "w") as f:
    json.dump({"running": True, "since": time.time(), "version": resolve.GetVersionString()}, f)
print("Sermon Clipper bridge running. Leave this open; it stops by itself after 3 hours.")

deadline = time.time() + 3 * 3600
while time.time() < deadline:
    names = sorted(n for n in os.listdir(INBOX) if n.endswith(".py"))
    for name in names:
        path = os.path.join(INBOX, name)
        with open(path) as f:
            code = f.read()
        os.remove(path)
        if name == "stop.py":
            deadline = 0
            break
        scope = {"resolve": resolve, "result": None}
        try:
            exec(code, scope)
            out = {"ok": True, "result": scope.get("result")}
        except Exception:
            out = {"ok": False, "error": traceback.format_exc()}
        with open(os.path.join(OUTBOX, name[:-3] + ".json"), "w") as f:
            json.dump(out, f, default=str)
    time.sleep(0.3)

with open(os.path.join(OUTBOX, "_status.json"), "w") as f:
    json.dump({"running": False, "stopped": time.time()}, f)
print("Sermon Clipper bridge stopped.")
