"""D · TASTENFUZZ — every key and modifier combination, in a real JupyterLab.

Starts its own `jupyter lab` when none answers at DIGICHEM_LAB_URL (see
lab_keys.ensure_lab), so it runs as a suite: exit 0 = FUZZ KEYS OK.

    python3 tests/test_fuzz_keys.py <notebook> [contexts] [out.json]

Contexts (from C): command · field (the `your own cell` box) · panel (keyboard
mode). After EVERY key the five invariants are checked against the state the
notebook had before the key:

  1  exactly two cells
  2  the panel host is there (if it was there before)
  3  the progress record is unchanged (its heartbeat `t` aside) — unless a task
     was solved
  4  the lock state is unchanged
  5  no uncaught JavaScript exception (pageerror)

and after every RUN — each fresh copy is opened with Run All, then the first
coding exercise is solved; a key may run the notebook itself (2026-09-28):

  7  panel mark count = source mark count
  8  panel chapter locks = document chapter locks = source chapter locks

A key that breaks one is a FAILURE with its name, context and the invariant.
2026-09-25h."""
import sys, os, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
LAB = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab")
BASE, LAB = ensure_lab(BASE)
SRC = sys.argv[1]
ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else ["command", "field", "panel"]
OUT = sys.argv[3] if len(sys.argv) > 3 else None

BASEKEYS = (list("abcdefghijklmnopqrstuvwxyz") + list("0123456789") +
            ["Minus", "Equal", "BracketLeft", "BracketRight", "Semicolon", "Quote",
             "Backslash", "Comma", "Period", "Slash", "Backquote", "Space",
             "Enter", "Escape", "Tab", "Backspace", "Delete", "Insert",
             "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
             "Home", "End", "PageUp", "PageDown"] +
            ["F%d" % i for i in range(1, 13)])
MODS = ["", "Shift+", "Control+", "Alt+", "Control+Shift+", "Alt+Shift+", "Control+Alt+", "Meta+", "Shift+Meta+"]
# Not pressed, with the reason: Ctrl+Shift+Q asks to shut the Jupyter server
# down and, accepted, does — the reader's decision, and the end of any
# measurement. It is not a way of breaking the notebook.
SKIP = {"Control+Shift+q"}
# FUZZ_ONLY="Control+Enter,…" re-measures single keys (the whole set is the suite)
ONLYKEYS = set(filter(None, os.environ.get("FUZZ_ONLY", "").split(",")))
if os.environ.get("FUZZ_QUICK"):
    MODS = MODS[:int(os.environ["FUZZ_QUICK"])]

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
          rec: rec, locks: locks,
          solved: (rec || '').split('"s":').length,
          tabs: document.querySelectorAll('.lm-DockPanel .lm-TabBar-tab').length,
          dialog: !!document.querySelector('.jp-Dialog'),
          palette: !!document.querySelector('.lm-CommandPalette:not(.lm-mod-hidden) .lm-CommandPalette-input:focus'),
          fullscreen: !!document.fullscreenElement,
          notebookFocus: !!(P && P.contains(document.activeElement)) || (h && h.contains(document.activeElement))};
}"""

def state(pg): return pg.evaluate(STATE_JS)

def solved_count(rec):
    try:
        d = json.loads(rec); return sum(sum(v.get("a", [0])[:1]) + sum(v.get("c", [0])[:1]) for v in d.values() if isinstance(v, dict))
    except Exception: return None

def violations(a, b, errs, ran=False):
    """`ran`: the key ran the notebook. A run starts the kernel empty and brings
    the kept progress back through the progress code, whose rule is generous —
    everything settled is opened. So after a run a lock may have OPENED; none
    may have CLOSED."""
    v = []
    if b["cells"] != 2: v.append("cells %d" % b["cells"])
    if a["host"] and not b["host"]: v.append("panel host gone")
    if a["rec"] != b["rec"]:
        sa, sb = solved_count(a["rec"]), solved_count(b["rec"])
        if not (sa is not None and sb is not None and sb > sa):
            v.append("progress record changed")
    la = set(filter(None, (a["locks"] or "").split("|")))
    lb = set(filter(None, (b["locks"] or "").split("|")))
    if ran:
        if lb - la: v.append("a run locked again: %s" % ", ".join(sorted(lb - la))[:120])
    elif la != lb:
        v.append("lock state changed: %s" % ", ".join(sorted(la ^ lb))[:120])
    if errs: v.append("js exception: %s" % errs[0][:120])
    return v

SETTERS = {"command": to_command, "field": to_textarea, "panel": to_panel}

WITH_PROGRESS = os.environ.get("FUZZ_EMPTY") is None
LABEL = [""]
RUNFAILS, RUNS = [], [0]
def run_check(pg, where):
    """invariants 7 and 8 after a run; a violation is kept with where it happened"""
    RUNS[0] += 1
    v = consistency(pg)
    if v:
        RUNFAILS.append("%s · %s" % (where, "; ".join(v)))
        print("  !! %-31s %s" % (where, "; ".join(v))); sys.stdout.flush()
    return v
def fresh_ok(b, ctx):
    for attempt in range(3):
        try:
            r = fresh(b, BASE, SRC, LAB, ctx)
            LABEL[0] = r[1].evaluate("() => (document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current .lm-TabBar-tabLabel')||{}).textContent || ''").strip()
            run_check(r[1], "open + Run All")
            # start from one solved exercise, so a key that WIPES progress shows
            if WITH_PROGRESS and first_code_solution(SRC)[0]:
                if not solve_first(r[1], SRC):
                    raise RuntimeError("could not solve the first coding exercise to start from")
                r[1].keyboard.press("Escape")
                run_check(r[1], "open + Run All + coding 1 solved")
            return r
        except Exception as e:
            print("  (fresh open failed, retrying: %s)" % str(e)[:80]); sys.stdout.flush()
            ctx = None
    raise RuntimeError("the notebook could not be opened three times in a row")

BACK_JS = r"""(label) => {
  // back to the notebook under test: ITS tab — Ctrl+Shift+T reopens an earlier
  // probe copy, so "a probe_ tab" is not enough
  var tabs = [].slice.call(document.querySelectorAll('.lm-DockPanel .lm-TabBar-tab'));
  var mine = tabs.filter(function(t){ return t.textContent.trim() === label; })[0];
  if (mine && !mine.classList.contains('lm-mod-current')) {
    mine.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, button: 0}));
    return 'switched';
  }
  return '';
}"""

def ours(err):
    st = getattr(err, "stack", "") or str(err)
    # the notebook's own scripts run from eval'd outputs; JupyterLab's from its bundles
    return not re.search(r"/static/|labextensions|/lab/", st) or "eval" in st

fails, rows = [], []
t0 = time.time()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = None
    for cname in ONLY:
        ctx, pg, errs = fresh_ok(b, ctx)
        pageerrs = []
        pg.on("pageerror", lambda e: pageerrs.append(e))
        base_host = state(pg)["host"]
        n = 0
        for mod in MODS:
            for key in BASEKEYS:
                k = mod + key
                if k in SKIP: continue
                if ONLYKEYS and k not in ONLYKEYS: continue
                pre = SETTERS[cname](pg)
                if not pre.startswith("ok"):
                    ctx, pg, errs = fresh_ok(b, ctx)
                    pageerrs = []; pg.on("pageerror", lambda e: pageerrs.append(e))
                    pre = SETTERS[cname](pg)
                a = state(pg); del pageerrs[:]
                try:
                    pg.keyboard.press(k)
                except Exception as e:
                    rows.append({"ctx": cname, "key": k, "skip": str(e)[:80]}); continue
                pg.wait_for_timeout(260)
                # a key that RUNS the notebook changes the record while it runs;
                # judge it when the kernel is done, not in the middle
                busy = False
                KS = "() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')"
                # a run may take a moment to START under load — look for it
                for _ in range(4):
                    if pg.evaluate(KS) == "busy": busy = True; break
                    pg.wait_for_timeout(250)
                for _ in range(120):
                    if pg.evaluate(KS) != "busy": break
                    busy = True; pg.wait_for_timeout(500)
                if busy:
                    # the last word of a run is the resume and the final panel;
                    # measured: seconds after the kernel went idle
                    pg.wait_for_timeout(5000)
                bb = state(pg)
                if busy:
                    # the panel builds itself for seconds after the kernel is idle
                    # (measured: ten); judge the state once it has stopped moving
                    for _ in range(20):
                        pg.wait_for_timeout(1000)
                        b2 = state(pg)
                        if b2 == bb: break
                        bb = b2
                note = ["ran the notebook"] if busy else []
                if bb["dialog"]:
                    # a dialog is a question; the harm is in the answer. Accept it.
                    note.append("dialog, accepted")
                    pg.keyboard.press("Enter"); pg.wait_for_timeout(600); bb = state(pg)
                if bb["palette"]:
                    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
                label = LABEL[0]
                sw = pg.evaluate(BACK_JS, label)
                if sw or bb["tabs"] != 1:
                    note.append("another tab came up")
                    try:
                        pg.click(".lm-DockPanel .lm-TabBar-tab:has-text('%s')" % label, timeout=3000)
                    except Exception:
                        pass
                    pg.wait_for_timeout(900); bb = state(pg)
                if bb["cells"] == -1 and not pg.query_selector(".lm-DockPanel .lm-TabBar-tab:has-text('%s')" % label):
                    # the reader closed the notebook (Alt+W, accepted): not a break
                    note.append("notebook closed")
                    bb = dict(a)
                jl = [str(e)[:100] for e in pageerrs if not ours(e)]
                mine = [str(e) for e in pageerrs if ours(e)]
                if jl: note.append("JupyterLab's own exception: %s" % jl[0])
                v = violations(a, bb, mine, ran=busy)
                if busy:
                    v += consistency(pg); RUNS[0] += 1
                row = {"ctx": cname, "key": k, "pre": pre, "viol": v, "note": note}
                if v:
                    row["before"] = {x: a[x] for x in ("rec", "locks", "cells", "host")}
                    row["after"] = {x: bb[x] for x in ("rec", "locks", "cells", "host")}
                rows.append(row)
                if note and not v:
                    print("  .. %-8s %-22s %s" % (cname, k, "; ".join(note))); sys.stdout.flush()
                n += 1
                if v:
                    fails.append("%s · %s · %s%s" % (cname, k, "; ".join(v), (" (" + "; ".join(note) + ")") if note else ""))
                    print("  !! %-8s %-22s %s %s" % (cname, k, "; ".join(v), note)); sys.stdout.flush()
                # anything that leaves the page in another state is reset, so the
                # next key is measured from the same start
                if v or note or bb["dialog"] or bb["tabs"] != 1 or bb["fullscreen"] or bb["palette"]:
                    ctx, pg, errs = fresh_ok(b, ctx)
                    pageerrs = []; pg.on("pageerror", lambda e: pageerrs.append(e))
        print("%-8s %d keys pressed (%.0f s so far)" % (cname, n, time.time() - t0)); sys.stdout.flush()
    if ctx: ctx.close()
    b.close()
kill_sessions(BASE)
fails += ["run · " + x for x in RUNFAILS]
print("runs checked for panel = source = document: %d" % RUNS[0])
if OUT: json.dump(rows, open(OUT, "w"), indent=0, ensure_ascii=False)
print("\n" + ("FUZZ KEYS OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
