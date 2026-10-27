"""D · CODEFUZZ — hostile code in the reader's code boxes, in a real JupyterLab.

Starts its own `jupyter lab` when none answers at DIGICHEM_LAB_URL (see
lab_keys.ensure_lab), so it runs as a suite: exit 0 = FUZZ CODE OK.

    python3 tests/test_fuzz_code.py <notebook> [payloads] [boxes]

Boxes: `own` — "your own cell" (the bring-your-own box, runs the code as is)
and `code1` — the coding field of the first exercise (runs, then checks). Each
payload runs in a FRESH copy of the notebook. Afterwards:

  1  exactly two cells
  2  the panel host is there (a script may remove it; the panel must come back)
  3  the progress record is what running harmless code (`pass`) in the same box
     leaves — nothing more
  4  the lock state is what `pass` in the same box leaves — nothing more.
     (2026-09-28: since 28a/K1 a WRONG answer opens the next coding exercise,
     and `pass` in the coding field is a wrong answer: codetask:t2 opens. Until
     28a this line said "unchanged" and went red on every payload in `code1`
     for the rule the user decided. `pass` itself may only OPEN locks.)
  5  no uncaught JavaScript exception from the notebook's own scripts
  6  the progress can still be SET: the first coding exercise, solved with its
     own solution, turns purple and counts

and after every RUN — the Run All that opens each copy, the payload, the
solve in 6 (2026-09-28):

  7  panel mark count = source mark count
  8  panel chapter locks = document chapter locks = source chapter locks

Box `unlock` (2026-09-30, E10 Teil 2 · FINAL-KRITERIEN 1): the reader's own
cell CALLS `_unlock_next("t1"); _unlock_next("t2")` — the night fuzz of 28.09.
found the document opening chapters while the panel kept them locked. Measured
from the click: chapters 2 and 3 leave the document's locks, and panel locks =
document locks = source locks, within UNLOCK_S (3 s).

Box `runs` (2026-09-28): coding 1 solved, then RUNS× "Restart Kernel and Run
All Cells…" (palette, dialog accepted). After each: 7 and 8, and the solve survives (record c = 1,
panel mark `cd-done`). 27a saw the panel keep a stale structure in about one
run of three; RUNS=6 would have missed that with 9 % odds.

2026-09-25h."""
import sys, os, json, re, ast, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
LAB = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab")
BASE, LAB = ensure_lab(BASE)
SRC = sys.argv[1]
RUNS = int(os.environ.get("FUZZ_RUNS", "6"))
UNLOCK_S = float(os.environ.get("FUZZ_UNLOCK_S", "3"))

PAYLOADS = {
  "pass":          "pass",
  "reset":         "%reset -f",
  "del-all":       "for _n in [k for k in list(globals()) if not k.startswith('__')]:\n    del globals()[_n]",
  "del-named":     "del task_solved, task_wrong, task_code_solved, _TASKS, _LOCKS, _refresh_progress, display",
  "raise":         "raise RuntimeError('fuzz')",
  "loop":          "while True:\n    pass",
  "print10mb":     "print('x' * 10_000_000)",
  "script":        "from IPython.display import display, HTML\n"
                   "display(HTML(\"<script>var h = document.getElementById('nbpanel-root'); if (h) h.remove();</script>\"))",
  "rebind-solved": "task_solved = lambda *a, **k: None\ntask_code_solved = lambda *a, **k: None\ntask_wrong = lambda *a, **k: None",
  "rebind-locks":  "_unlock_next = lambda *a, **k: None\n_unlock_next_code = lambda *a, **k: None\n"
                   "_refresh_progress = lambda *a, **k: None",
}
ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else list(PAYLOADS)
BOXES = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else ["own", "code1", "runs", "unlock"]

# the first coding exercise's own solution, read from the notebook's source
mega = max(json.load(open(SRC, encoding="utf-8"))["cells"], key=lambda c: len("".join(c["source"])))
msrc = "\n".join(l for l in __import__("megasrc").expand("".join(mega["source"])).splitlines() if not l.strip().startswith("%pip"))
SOLUTION, FIRST = None, None
for node in ast.walk(ast.parse(msrc)):
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "code_fold":
        kw = {k.arg: k.value for k in node.keywords}
        if "task" in kw and "solution" in kw and "locked_by" not in kw:
            try:
                SOLUTION, FIRST = ast.literal_eval(kw["solution"]), ast.literal_eval(kw["task"])
                break
            except Exception:
                pass

STATE_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var nb = P && P.querySelector('.jp-Notebook');
  var h = document.getElementById('nbpanel-root');
  var rec = null;
  try { var pr = JSON.parse(localStorage.getItem('digichemjn.progress.v1') || '{}');
        Object.keys(pr).forEach(function(k){ if (pr[k] && typeof pr[k] === 'object') delete pr[k].t; });
        rec = JSON.stringify(pr); } catch (e) { rec = 'UNREADABLE'; }
  var locks = h ? [].filter.call(h.querySelectorAll('.nbmap-node'), function(n){
        return n.classList.contains('locked') || n.querySelector('.st-lock, .cd-lock'); }).map(function(n){
        var kind = (String(n.className).match(/\b(codetask|viztask|task|chap|sub|sect)\b/) || ['', '?'])[1];
        var id = (n.getAttribute('data-task') || n.getAttribute('data-target') || n.getAttribute('title') || '')
                 .replace(/__[0-9a-f]{6,}$/, '');       // anchors carry a per-run suffix
        return kind + ':' + id + (n.classList.contains('locked') ? ':L' : '') +
               (n.querySelector('.st-lock') ? ':s' : '') + (n.querySelector('.cd-lock') ? ':c' : ''); }).sort().join('|') : null;
  return {cells: nb ? nb.querySelectorAll('.jp-Cell').length : -1,
          host: !!(h && h.classList.contains('ready') && h.querySelector('.nbrail')),
          rec: rec, locks: locks};
}"""

BOX_JS = r"""(which) => {
  // returns an id for the textarea of the box and one for its button
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var ta = null;
  if (which === 'own') {
    var all = [].slice.call(P.querySelectorAll('textarea.widget-input'));
    // the bring-your-own box is the LAST code box of the document
    ta = all.filter(function(x){ return x.closest('.codearea') || x.classList.contains('codearea') || true; }).pop();
  } else {
    var h = document.getElementById('nbpanel-root');
    var n = h && h.querySelector('.nbmap-node.codetask[data-task="' + which.split(':')[1] + '"]');
    var sp = n && document.getElementById(n.getAttribute('data-target'));
    if (sp) {
      var ts = P.querySelectorAll('textarea.widget-input');
      for (var i = 0; i < ts.length; i++)
        if (sp.compareDocumentPosition(ts[i]) & 4) { ta = ts[i]; break; }
    }
  }
  if (!ta) return null;
  var chain = [], e = ta;
  while (e) { if (e.classList && e.classList.contains('jupyter-widget-Collapse-contents') && e.classList.contains('lm-mod-hidden')) chain.push(e); e = e.parentElement; }
  chain.reverse().forEach(function(c){ var hd = c.parentElement.querySelector(':scope > .jupyter-widget-Collapse-header'); if (hd) hd.click(); });
  var b = null, up = ta.parentElement, k = 0;
  while (up && k < 12 && !b) { b = up.querySelector('button.sc-btn'); up = up.parentElement; k++; }
  ta.setAttribute('data-fz', 'ta'); if (b) b.setAttribute('data-fz', 'btn');
  return {ok: !!b, label: b ? b.textContent : null};
}"""

def run_in(pg, which, code):
    r = pg.evaluate(BOX_JS, which)
    if not r or not r["ok"]:
        return "no box %s" % which
    pg.wait_for_timeout(600)
    pg.evaluate("(c) => { var t = document.querySelector('[data-fz=ta]'); t.focus(); t.value = c;"
                " t.dispatchEvent(new Event('input', {bubbles: true})); t.dispatchEvent(new Event('change', {bubbles: true})); t.blur(); }", code)
    pg.wait_for_timeout(500)
    pg.evaluate("() => { document.querySelectorAll('[data-fz]').forEach(function(x){ if (x.tagName === 'BUTTON') x.click(); }); }")
    return "ok"

def kernel_busy(pg):
    return pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")

def settle(pg, secs=20):
    for _ in range(secs * 2):
        pg.wait_for_timeout(500)
        if kernel_busy(pg) == "idle": return True
    return False

def interrupt_all():
    for x in json.loads(urllib.request.urlopen(BASE + "/api/sessions").read()):
        urllib.request.urlopen(urllib.request.Request(BASE + "/api/kernels/%s/interrupt" % x["kernel"]["id"], method="POST", data=b""))

def fresh_ok(b, ctx):
    for attempt in range(3):
        try:
            return fresh(b, BASE, SRC, LAB, ctx)
        except Exception as e:
            print("  (fresh open failed, retrying: %s)" % str(e)[:80]); sys.stdout.flush()
            ctx = None
            time.sleep(5)
    raise RuntimeError("the notebook could not be opened three times in a row")

def code_solved(rec):
    try: return sum(v["c"][0] for v in json.loads(rec).values() if isinstance(v, dict) and "c" in v)
    except Exception: return None

fails, report = [], []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = None
    ref, ref_locks, opened = {}, {}, {}
    for box in BOXES:
        if box == "unlock":
            ctx, pg, errs = fresh_ok(b, ctx)
            perrs = []; pg.on("pageerror", lambda e: perrs.append(str(e)))
            v = consistency(pg)
            c0 = pg.evaluate(CONSIST_JS)
            want_gone = {"t1", "t2"}
            if not want_gone <= set((c0.get("docLocks") or "").split(",")):
                v.append("precondition: chapters after t1/t2 not locked (%s)" % c0.get("docLocks"))
            r = pg.evaluate(BOX_JS, "own")
            if not r or not r["ok"]:
                v.append("no own box")
            else:
                pg.wait_for_timeout(600)
                pg.evaluate("(c) => { var t = document.querySelector('[data-fz=ta]'); t.focus(); t.value = c;"
                            " t.dispatchEvent(new Event('input', {bubbles: true})); t.dispatchEvent(new Event('change', {bubbles: true})); t.blur(); }",
                            "_unlock_next('t1')\n_unlock_next('t2')")
                pg.wait_for_timeout(500)
                t0 = time.time()
                pg.evaluate("() => { var b = document.querySelector('button[data-fz=btn]'); if (b) b.click(); }")
                took, c = None, None
                while time.time() - t0 < 20:
                    c = pg.evaluate(CONSIST_JS)
                    gone = not (want_gone & set((c.get("docLocks") or "").split(",")))
                    if gone and c.get("ok"):
                        took = time.time() - t0; break
                    pg.wait_for_timeout(100)
                if took is None:
                    v.append("after 20 s: panel [%s] document [%s] source [%s]"
                             % (c.get("panelLocks"), c.get("docLocks"), c.get("srcLocks")))
                elif took > UNLOCK_S:
                    v.append("panel = document only after %.2f s (> %.0f s)" % (took, UNLOCK_S))
                settle(pg, 20); pg.wait_for_timeout(2500)
                v += ["later: " + x for x in consistency(pg, wait=3)]
            if perrs: v.append("js exception: %s" % perrs[0][:100])
            if os.environ.get("FUZZ_SHOT"): pg.screenshot(path=os.environ["FUZZ_SHOT"])
            line = "%-6s %-14s %s" % ("unlock", "_unlock_next", "; ".join(v) if v else
                                      "ok (panel = document after %.2f s)" % took)
            report.append(line); print(line); sys.stdout.flush()
            if v: fails.append("unlock · " + "; ".join(v))
            continue
        if box == "runs":
            if not FIRST:
                report.append("runs: this notebook has no coding exercise — skipped"); continue
            ctx, pg, errs = fresh_ok(b, ctx)
            perrs = []; pg.on("pageerror", lambda e: perrs.append(str(e)))
            v0 = consistency(pg)
            if not solve_first(pg, SRC): v0.append("could not solve coding 1 to start from")
            v0 += consistency(pg)
            line = "%-6s %-14s %s" % ("runs", "start", "; ".join(v0) if v0 else "ok")
            report.append(line); print(line); sys.stdout.flush()
            if v0: fails.append("runs · start · " + "; ".join(v0))
            for i in range(RUNS):
                v = []
                dlg = restart_run_all(pg)
                if not dlg or "restart" not in dlg.lower():
                    v.append("precondition: no restart dialog (%s)" % dlg)
                # judge the run when it has RUN: wait until the kernel was busy
                seen = False
                for _ in range(60):
                    pg.wait_for_timeout(250)
                    if kernel_busy(pg) == "busy": seen = True; break
                if not seen: v.append("precondition: the run never started")
                if not settle(pg, 60): v.append("kernel still busy")
                pg.wait_for_timeout(2500)
                v += consistency(pg)
                cc = pg.evaluate(STATE_JS)
                mark = pg.evaluate("(t) => { var n = document.querySelector('#nbpanel-root .nbmap-node.codetask[data-task=\"' + t + '\"] .nbcodemark'); return n ? n.className : null; }", FIRST)
                if code_solved(cc["rec"]) != 1: v.append("the solve did not survive (code solved %s)" % code_solved(cc["rec"]))
                if not (mark and "cd-done" in mark): v.append("the panel does not show the solve (mark: %s)" % mark)
                if cc["cells"] != 2: v.append("cells %d" % cc["cells"])
                if perrs: v.append("js exception: %s" % perrs[0][:100]); del perrs[:]
                line = "%-6s %-14s %s" % ("runs", "restart+run %d" % (i + 1), "; ".join(v) if v else "ok (%s)" % dlg)
                report.append(line); print(line); sys.stdout.flush()
                if v: fails.append("runs · restart+run %d · %s" % (i + 1, "; ".join(v)))
            continue
        which = box if box == "own" else "code:%s" % FIRST
        if box == "code1" and not FIRST:
            report.append("code1: this notebook has no coding exercise — skipped"); continue
        for name in (["pass"] + [x for x in ONLY if x != "pass"]):
            ctx, pg, errs = fresh_ok(b, ctx)
            perrs = []; pg.on("pageerror", lambda e: perrs.append(str(e)))
            a = pg.evaluate(STATE_JS)
            v_open = consistency(pg)            # 7, 8 after the Run All that opened it
            r = run_in(pg, which, PAYLOADS[name])
            if r != "ok":
                report.append("%s/%s: %s" % (box, name, r)); fails.append("%s · %s · %s" % (box, name, r)); continue
            if name == "loop":
                # interrupt only once the loop is really running, and until it stops
                for _ in range(20):
                    pg.wait_for_timeout(500)
                    if kernel_busy(pg) == "busy": break
                pg.wait_for_timeout(1500)
                for _ in range(5):
                    interrupt_all()
                    if settle(pg, 6): break
            ok = settle(pg, 40)
            pg.wait_for_timeout(2500)          # the panel's own sync, and a script's effect
            bb = pg.evaluate(STATE_JS)
            if name == "pass":
                ref[box] = bb["rec"]
                ref_locks[box] = bb["locks"]
            v = []
            if not ok: v.append("kernel still busy")
            if bb["cells"] != 2: v.append("cells %d" % bb["cells"])
            if a["host"] and not bb["host"]: v.append("panel host gone")
            if bb["rec"] not in (a["rec"], ref.get(box)): v.append("progress record changed beyond a plain attempt")
            la = set(filter(None, (a["locks"] or "").split("|")))
            lb = set(filter(None, (bb["locks"] or "").split("|")))
            if name == "pass":
                if lb - la: v.append("a plain attempt locked: %s" % ", ".join(sorted(lb - la))[:120])
                if la - lb: opened[box] = sorted(la - lb)
            elif bb["locks"] not in (a["locks"], ref_locks.get(box)):
                v.append("lock state changed beyond a plain attempt: %s"
                         % ", ".join(sorted(lb ^ set(filter(None, (ref_locks.get(box) or a["locks"] or "").split("|")))))[:120])
            if perrs: v.append("js exception: %s" % perrs[0][:100])
            v += ["on open: " + x for x in v_open]
            if a["host"]: v += consistency(pg)  # 7, 8 after the payload
            # 6 — can the progress still be set?
            if FIRST and SOLUTION and a["host"]:
                before = code_solved(bb["rec"])
                run_in(pg, "code:%s" % FIRST, SOLUTION); settle(pg, 30); pg.wait_for_timeout(2000)
                cc = pg.evaluate(STATE_JS)
                after = code_solved(cc["rec"])
                mark = pg.evaluate("(t) => { var n = document.querySelector('#nbpanel-root .nbmap-node.codetask[data-task=\"' + t + '\"] .nbcodemark'); return n ? n.className : null; }", FIRST)
                if not (after is not None and before is not None and after == before + 1):
                    v.append("progress can no longer be set (code solved %s -> %s)" % (before, after))
                if not (mark and "cd-done" in mark):
                    v.append("the panel does not show it (mark: %s)" % mark)
                v += ["after the solve: " + x for x in consistency(pg)]
            line = "%-6s %-14s %s" % (box, name, "; ".join(v) if v else "ok")
            report.append(line); print(line); sys.stdout.flush()
            if v: fails.append("%s · %s · %s" % (box, name, "; ".join(v)))
    if ctx: ctx.close()
    b.close()
kill_sessions(BASE)
for bx, o in sorted(opened.items()):
    print("%s: a plain attempt (`pass`) opens %s — the rule since 28a (wrong answer opens the next)" % (bx, ", ".join(o)))
print("\n" + ("FUZZ CODE OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
