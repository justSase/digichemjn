"""Key × context × effect, from a real JupyterLab. Writes JSON rows. See lab_keys.py."""
import sys, json
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899"); SRC = sys.argv[1]; OUT = sys.argv[2]
LAB = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab")
KEYS = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else [
  "Alt+Period", "j", "k", "1", "3", "g", "Enter", "a", "Escape", "d", "s", "p", "f", "Shift+Slash",
  "x", "b", "m", "Space", "Control+s", "F2", "Control+Alt+KeyP"]
CTX = {"command": to_command, "field": to_textarea, "editor": to_editor, "panel": to_panel}
ONLY = sys.argv[4].split(",") if len(sys.argv) > 4 else list(CTX)
WAIT = {"Enter": 2400, "g": 1500, "j": 1200, "k": 1200, "1": 1500, "3": 1500}
rows = []
def broken(s): return s["cells"] not in (2, 3) or s["dialog"] or s["palette"] or s["tabs"] != 1 or s["fullscreen"]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = None
    for cname in ONLY:
        setter = CTX[cname]
        ctx, pg, errs = fresh(b, BASE, SRC, LAB, ctx)
        for k in KEYS:
            pre = setter(pg)
            a0, b0, d = press(pg, k, wait=WAIT.get(k, 700))
            rows.append({"ctx": cname, "key": k, "pre": pre, "effect": d, "errors": list(errs)})
            errs.clear()
            print("%-8s %-17s %-4s %s" % (cname, k, pre[:4], json.dumps(d, ensure_ascii=False)[:260])); sys.stdout.flush()
            if broken(b0) or (cname != "editor" and b0["cells"] != 2):
                ctx, pg, errs = fresh(b, BASE, SRC, LAB, ctx)
    ctx.close(); b.close()
kill_sessions(BASE)
json.dump(rows, open(OUT, "w"), indent=1, ensure_ascii=False)
