"""Paket 13 — A NEW SEED WITHOUT A NEW RUN, measured in a real JupyterLab
(2026-09-30, E10 Teil 2, Inhalt + Applikation).

    python3 tests/lab_seed.py <notebook> [width height]

Opens a fresh copy (Run All), solves coding 1 (so there is progress to lose),
skips t1–t5 (so chapters 2–6 and their exercises are built and open),
then types a seed into the ⚙ seed box and presses "Use this seed". The seed is
chosen so that EVERY personal number differs from the current draw (computed
with the notebook's own `_draw_tv`). Measured:

  1  every personal exercise text (t1–t6, "Your … is …") shows the new numbers
     within 2 s of the click (ms reported)
  2  no Run All: the run id (`.nbfeed[data-nbid]`, new on every run) is unchanged, the cells are still 2
  3  the progress record is unchanged (heartbeat aside), coding 1 still solved
  4  t1: the OLD root is rejected, the NEW one accepted (typed into the boxes,
     "Check answer" pressed)
  5  the new seed is stored for the next run (kernel side, ~/.digichemjn/*.seed)
  6  no page errors

2026-10-03 (E21 Rest Stufe 2, Applikation — Prüfwerkzeug) — COMPLEX AND
MODELING. BEHAUPTETE BISHER, every notebook draws Complex's numbers: the seed
search asked `_draw_tv` for q, z1, z2, n5, d5, zq, and Modeling (sse_*, gd_*,
sc_*, pk_*, …) crashed there with KeyError 'q' (gate 03.10., Stufe 2 — a crash,
not a measurement). Which notebook it is now follows from its own draw, and
the six claims are the same for both; only what they read differs:
              personal texts             t1 answer             new value shown
  Complex     "Your … is …" sentences    Re(z) = 0, Im(z) = √q  "q = <new q>"
  Modeling    every exercise box         orders = log10 ratio   "about <ms> ms", "<h> h"
              (all nine are personal)    (old ratio ≠ new ±0.2)
Complex reads, searches and checks as before; in both, claim 4 now takes the
verdict once it has settled (see there).

exit 0 = SEED OK."""
import sys, os, json, re, io, contextlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
LAB = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab")
BASE, LAB = ensure_lab(BASE)
SRC = sys.argv[1]
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1400
H = int(sys.argv[3]) if len(sys.argv) > 3 else 900

# the notebook's own draw, in plain Python
_nb = json.load(open(SRC, encoding="utf-8"))
_src = "\n".join(l for l in __import__("megasrc").expand("".join(max(_nb["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines()
                 if not l.strip().startswith("%pip"))
_G = {"__name__": "__main__", "display": lambda *a, **k: None}
_d = ipd.display; ipd.display = lambda *a, **k: None
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(_src, "m", "exec"), _G)
ipd.display = _d
np = _G["np"]
def draw(seed, level="standard"):
    return _G["_draw_tv"](np.random.default_rng(int(seed)), level)

# which notebook: its own draw says it (E21 Rest Stufe 2)
_d0 = draw(1)
if "q" in _d0:                                   # Complex
    KIND, KEYS, READ = "complex", ("q", "z1", "z2", "n5", "d5", "zq"), "your"
    T1_LABEL = r"^(Re|Im)\(z\) =$"
    def t1_vals(d): return [0.0, float(np.sqrt(d["q"]))]
    def t1_shown(d): return ["q = %d" % d["q"]]
    def t1_apart(a, b): return True
elif "sc_fast" in _d0:                           # Modeling
    KIND, KEYS, READ = "modeling", tuple(sorted(_d0)), "box"
    T1_LABEL = r"^orders =$"
    def _q1(d): return float(np.log10(d["sc_slow"] * 3600 * 1000 / d["sc_fast"]))
    def t1_vals(d): return [_q1(d)]
    def t1_shown(d): return ["about %d ms" % d["sc_fast"], "about %d h" % d["sc_slow"]]
    # 2 ms/12 h and 1 ms/6 h are the same answer: the old one must be wrong
    def t1_apart(a, b): return abs(_q1(a) - _q1(b)) >= 0.2
else:
    sys.exit("lab_seed: unknown notebook — _draw_tv gives %s" % sorted(_d0))

TEXTS_JS = r"""(read) => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var out = [];
  // Modeling: every exercise box is personal (personal(exercise_box(…))) —
  // not the task text of a coding exercise, drawn in the same box (code_fold)
  if (read === 'box') P.querySelectorAll('.nbbox-ex').forEach(function(e){
    if (!e.closest('.nbfeed, .nbcodefold, .codefold')) out.push(e.textContent.replace(/\s+/g, ' ').trim()); });
  else P.querySelectorAll('.widget-html-content').forEach(function(e){
    if (e.closest('.nbfeed')) return;
    var t = e.textContent.replace(/\s+/g, ' ');
    var m = t.match(/Your (personal value|personal number|personal pair|pair) is [^.]*?(?=\.| so |, so| Use| Give|$)/);
    if (m) out.push(m[0].trim());
  });
  var pr = null; try { pr = JSON.parse(localStorage.getItem('digichemjn.progress.v1') || '{}');
    Object.keys(pr).forEach(function(k){ if (pr[k] && typeof pr[k] === 'object') delete pr[k].t; }); } catch (e) {}
  var nb = P.querySelector('.jp-Notebook');
  var prm = [].map.call(P.querySelectorAll('.nbfeed[data-nbid]'), function(f){ return f.getAttribute('data-nbid'); })
            .filter(function(x, i, a){ return a.indexOf(x) === i; });
  var dbg = [].slice.call(P.querySelectorAll('.widget-html-content')).filter(function(e){
      return !e.closest('.nbfeed') && /Your /.test(e.textContent); }).map(function(e){ return e.textContent.replace(/\s+/g,' ').slice(0, 90); });
  var seedNote = (document.querySelector('.nbctl-seed') || document.body).textContent.match(/Seed (\d+)/);
  return {texts: out, rec: JSON.stringify(pr), prompts: prm.join('|'), dbg: dbg,
          cells: nb.querySelectorAll('.jp-Cell').length, seed: seedNote ? +seedNote[1] : null};
}"""

SEED_JS = r"""(v) => {
  var box = document.querySelector('.nbctl-seed');
  if (!box) return 'no seed box';
  var inp = box.querySelector('input'); if (!inp) return 'no input';
  inp.value = String(v);
  inp.dispatchEvent(new Event('input', {bubbles: true}));
  inp.dispatchEvent(new Event('change', {bubbles: true}));
  inp.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
  return 'ok';
}"""
CLICK_JS = r"""(label) => {
  var bs = [].slice.call(document.querySelectorAll('.nbctl-seed button'));
  var b = bs.filter(function(x){ return x.textContent.indexOf(label) >= 0; })[0];
  if (!b) return false; b.click(); return true;
}"""
T1_JS = r"""([re, vals]) => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), rx = new RegExp(re);
  var boxes = [].slice.call(P.querySelectorAll('.widget-text')).filter(function(w){
    var l = w.querySelector('label'); return l && rx.test(l.textContent.trim()); });
  if (boxes.length < vals.length) return 'no t1 boxes (' + boxes.length + ')';
  var set = function(w, x){ var i = w.querySelector('input'); i.value = String(x);
    i.dispatchEvent(new Event('input', {bubbles: true})); i.dispatchEvent(new Event('change', {bubbles: true}));
    i.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true})); i.blur(); };
  vals.forEach(function(x, j){ set(boxes[j], x); });
  var up = boxes[vals.length - 1], b = null, k = 0;
  while (up && k < 10 && !b) { b = [].slice.call(up.querySelectorAll('button')).filter(function(x){
      return x.textContent.indexOf('Check answer') >= 0; })[0]; up = up.parentElement; k++; }
  if (!b) return 'no check button';
  b.setAttribute('data-t1', '1');
  return 'ok';
}"""
T1_RESULT_JS = r"""() => {
  // the answer widget: VBox[hint, row, row?, button, OUTPUT] — the verdict is the
  // first line in the Output that follows the button's own row
  var b = document.querySelector('button[data-t1]'); if (!b) return null;
  var row = b.closest('.widget-box, .widget-hbox, .jupyter-widgets') || b.parentElement;
  var box = row, k = 0, out = null;
  while (box && k < 6 && !out) {
    var outs = box.querySelectorAll('.jupyter-widgets-output-area, .widget-output');
    for (var i = 0; i < outs.length; i++) if (b.compareDocumentPosition(outs[i]) & 4) { out = outs[i]; break; }
    box = box.parentElement; k++;
  }
  if (!out) return 'no output';
  var r = out.querySelector('.nbok, .nbwarn');
  return r ? r.className + ': ' + r.textContent.trim().slice(0, 60) : '';
}"""
BUSY_JS = "() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')"

fails, rows = [], []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx, pg, errs = fresh(b, BASE, SRC, LAB)
    if W != 1400 or H != 900: pg.set_viewport_size({"width": W, "height": H})
    perrs = []; pg.on("pageerror", lambda e: perrs.append(str(e)))
    if not solve_first(pg, SRC): fails.append("precondition: coding 1 could not be solved")
    # locked chapters are not built yet: skip t1…t5 on the answer route, so all
    # six personal exercises stand on the page (skipping opens the next one)
    for _ in range(8):
        if len(pg.evaluate(TEXTS_JS, READ)["texts"]) >= 6: break
        pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
            [].forEach.call(P.querySelectorAll('button.nbskipnow'), function(b){
              if (!b.closest('.nbfeed') && !b.closest('.nbcodefold, .codefold')) b.click(); }); }""")
        for _ in range(40):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')") == "idle": break
        pg.wait_for_timeout(1200)
    # 2026-10-04 (E19 B + E17 rebasen, Applikation — Prüfwerkzeug) — BEHAUPTETE
    # BISHER, the progress record is final once six texts stand. It is not: the
    # last skip's state can reach localStorage only after that (stage 2 after a
    # full stage 1, 04.10. ~01 UTC, Complex: "s" 3 -> 4 across the reseed; in
    # the next such run the wait below saw 1 late write before any reseed).
    # The record is read once it has stood still for 2 s with the kernel idle
    # (≤ 20 s); the wait and the late writes are reported.
    t_set, last, n_moves = time.time(), None, -1
    while time.time() - t_set < 20:
        cur = pg.evaluate(TEXTS_JS, READ)["rec"]
        if cur != last:
            last, t_last, n_moves = cur, time.time(), n_moves + 1
        elif time.time() - t_last >= 2.0 and pg.evaluate(BUSY_JS) == "idle":
            break
        pg.wait_for_timeout(200)
    rows.append("0 progress before the seed settled after %.1f s (%d late write%s)"
                % (time.time() - t_set, n_moves, "" if n_moves == 1 else "s"))
    a = pg.evaluate(TEXTS_JS, READ)
    if len(a["texts"]) < 6: fails.append("precondition: %d personal texts found, want ≥ 6" % len(a["texts"]))
    old = draw(a["seed"])
    new_seed = None
    for s in range(a["seed"] + 1, a["seed"] + 5000):
        d = draw(s)
        if all(d[k] != old[k] for k in KEYS) and t1_apart(old, d):
            new_seed = s; break
    if new_seed is None:
        fails.append("precondition: no seed in %d…%d changes every number (%s)" % (a["seed"] + 1, a["seed"] + 4999, KIND))
        new_seed = a["seed"] + 1
    rows.append("%s · seed %s -> %s  (t1 %s -> %s)" % (KIND, a["seed"], new_seed,
                ", ".join(t1_shown(old)), ", ".join(t1_shown(draw(new_seed)))))
    r = pg.evaluate(SEED_JS, new_seed); pg.wait_for_timeout(400)
    if r != "ok": fails.append("seed box: %s" % r)
    t0 = time.time()
    if not pg.evaluate(CLICK_JS, "Use this seed"): fails.append("no 'Use this seed' button")
    changed_at, bb = None, None
    while time.time() - t0 < 8:
        bb = pg.evaluate(TEXTS_JS, READ)
        if len(bb["texts"]) == len(a["texts"]) and all(x != y for x, y in zip(a["texts"], bb["texts"])):
            changed_at = time.time() - t0; break
        pg.wait_for_timeout(50)
    same = [x for x, y in zip(a["texts"], (bb or {}).get("texts", [])) if x == y]
    rows.append("1 texts changed: %s after %s ms  (%d texts)" % (
        "all" if changed_at is not None else "NOT all (%d same)" % len(same),
        "%.0f" % (changed_at * 1000) if changed_at is not None else "> 8000", len(a["texts"])))
    if changed_at is None or changed_at > 2.0:
        fails.append("1: the personal texts did not all change within 2 s (%s; unchanged: %s)"
                     % (changed_at, "; ".join(same)[:160]))
    pg.wait_for_timeout(1500)
    c = pg.evaluate(TEXTS_JS, READ)
    nd = draw(new_seed)
    if not any(all(w in x for w in t1_shown(nd)) for x in c["texts"]):
        fails.append("1: the t1 text does not show the new %s" % ", ".join(t1_shown(nd)))
    rows.append("2 run id %s -> %s · cells %d" % (a["prompts"], c["prompts"], c["cells"]))
    if c["prompts"] != a["prompts"]: fails.append("2: the run id changed — a run happened")
    if c["cells"] != 2: fails.append("2: cells %d" % c["cells"])
    rows.append("3 progress %s" % ("unchanged" if c["rec"] == a["rec"] else "CHANGED"))
    if c["rec"] != a["rec"]: fails.append("3: progress record changed: %s -> %s" % (a["rec"][:80], c["rec"][:80]))
    if '"c":[1,' not in c["rec"]: fails.append("3: coding 1 no longer solved")
    for label, vals, want in (("old", t1_vals(old), "nbwarn"), ("new", t1_vals(nd), "nbok")):
        val = vals[-1]
        r = pg.evaluate(T1_JS, [T1_LABEL, vals])
        if r != "ok": fails.append("4: %s" % r); break
        pg.wait_for_timeout(500)
        # empty the verdict first, so an earlier line cannot be read as this one
        pg.evaluate("""() => { var b = document.querySelector('button[data-t1]'); var up = b, k = 0;
            while (up && k < 6) { up.querySelectorAll('.jupyter-widgets-output-area .nbok, .jupyter-widgets-output-area .nbwarn')
              .forEach(function(e){ if (b.compareDocumentPosition(e) & 4) e.remove(); }); up = up.parentElement; k++; } }""")
        pg.evaluate("() => document.querySelector('button[data-t1]').click()")
        # 2026-10-03 (E21 Rest Stufe 2) — THE VERDICT OF THIS CLICK, SETTLED.
        # BEHAUPTETE BISHER: the first verdict seen with the kernel idle is the
        # answer to this click. The Output redraws itself from its model when
        # the kernel's reply lands, so the verdict of the click BEFORE (removed
        # from the page above) can come back for a moment: v1.61 Modeling read
        # the new answer as "Not there yet" in 2 of 3 runs, and 3 s later the
        # same box said "✓ correct" (3 of 3 with a dump). Now the verdict
        # counts once the kernel is idle and the line is the same for 1.5 s.
        res, same = None, 0
        for _ in range(80):
            pg.wait_for_timeout(250); r2 = pg.evaluate(T1_RESULT_JS)
            ok_now = r2 and r2 != "no output" and pg.evaluate(BUSY_JS) == "idle"
            same = same + 1 if (ok_now and r2 == res) else 0
            res = r2
            if same >= 6: break
        rows.append("4 t1 %s %s = %g -> %s" % (label, "√q" if KIND == "complex" else "orders", val, res))
        if not res or not res.startswith(want):
            fails.append("4: t1 with the %s root %g: %s (want %s)" % (label, val, res, want))
        pg.evaluate("() => { var b = document.querySelector('button[data-t1]'); if (b) b.removeAttribute('data-t1'); }")
    import glob
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    st = {os.path.basename(f): open(f).read().strip() for f in glob.glob(os.path.join(kh, ".digichemjn", "*.seed"))}
    rows.append("5 stored seed %s" % json.dumps(st)[:120])
    if str(new_seed) not in st.values():
        fails.append("5: the new seed %d is not stored for the next run (%s)" % (new_seed, json.dumps(st)[:100]))
    rows.append("6 page errors %d" % len(perrs))
    if perrs: fails.append("6: page error: %s" % perrs[0][:120])
    # the picture: exercise 1 with its new number and the verdict (JupyterLab's
    # own news toast answered "No" so it does not cover it)
    pg.evaluate("""([read, want]) => { [].forEach.call(document.querySelectorAll('.jp-toast-button, .jp-Notification-Toast button'),
        function(b){ if (b.textContent.trim() === 'No') b.click(); });
      var e = [].slice.call(document.querySelectorAll(read === 'box' ? '.nbbox-ex' : '.widget-html-content')).filter(function(x){
        return !x.closest('.nbfeed, .nbcodefold, .codefold') && (read === 'box' ? x.textContent.indexOf(want) >= 0
                                                                                : /Your personal value is q/.test(x.textContent)); })[0];
      // a shut Practice section holds the box with no height: open it first
      for (var c = e; c && (c = c.parentElement && c.parentElement.closest('.jupyter-widget-Collapse'));)
        if (!c.classList.contains('jupyter-widget-Collapse-open')) { var h = c.querySelector(':scope > .jupyter-widget-Collapse-header'); if (h) h.click(); }
      if (e) setTimeout(function(){ e.scrollIntoView({block: 'start'}); }, 600); }""", [READ, t1_shown(nd)[0]])
    pg.wait_for_timeout(2500)
    pg.screenshot(path=os.environ.get("SEED_SHOT", "/home/claude/w/seed.png"))
    ctx.close(); b.close()
kill_sessions(BASE)
print("\n".join(rows))
print("\n" + ("SEED OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
