"""E23.3 + E23.7 — the JS workshop's regress tests (2026-10-06; Kategorie
Applikation, Prüfwerkzeug). Module of tests/regress/run.py (TESTS = [(name, fn)],
fn(pg, ctx) -> (ok, detail)). Real JupyterLab, measured in the browser.

The cover is read as the reader sees it after a run (E24.3): the last output of
the mega-cell (`.nbcover-out`), up over the notebook until Play — brought back on
the notebook under test (window.__nbCoverShow) and put away again at the end,
painted by our script from the progress the panel holds.

  J23.3  per lane (exercises, coding) exactly ONE mark is "open" (data-st), and it
         is the HIGHEST one that is unlocked and not done; the other unlocked ones
         are "free" and carry no lane colour. Progress made in the kernel: exercise
         1 solved, coding 2 unlocked while coding 1 is still open (two unlocked
         coding exercises) → coding 2 open, coding 1 free; exercise 2 open.
  J23.7  locked chapters and exercises are data-st="locked"; the figure marks of a
         locked chapter are data-st="locked" and pale (effective opacity ≤ .5), of an
         open chapter not (no state, opacity ≥ .9); quiz and BYOD are not locked.

A test that cannot reach its precondition returns False ("BAD …"), never True."""
import os, sys, json, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"
_N = itertools.count()

def _palette(pg, label):
    pg.keyboard.press("Escape"); pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=10000)
    pg.fill(".lm-CommandPalette-input", label)
    pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim().indexOf(l) === 0); }", arg=label, timeout=10000)
    pg.keyboard.press("Enter")

def _front_name(pg):
    return pg.evaluate("() => { var t = document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current .lm-TabBar-tabLabel'); return t ? t.textContent.trim() : null; }")

# 2026-10-06 (E24 Stufe 2, JS): the cover is the last output of the mega-cell
# (`.nbcover-out`, py-E24.3), up over the notebook after a run until Play
# (js-E24.3). Behauptete bisher: the cover is the cold markdown cell of a fresh,
# not run copy opened beside the notebook — that cell is one start line now, and
# both tests were red ("BAD no cover (output .nbcover-out)"). Now the cover of the notebook under
# test is brought back (window.__nbCoverShow, what Play undoes) and read where
# the reader sees it; painted by our script from the progress its panel holds,
# as before. No second copy, no second kernel.
COVER_ON = "() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var c = P && P.querySelector('.nbcover-out[data-nbcov]'); var p = c && c.querySelector('.nbcover .nbcover-play'); return !!(c && c.querySelector('.nbcover .nbcover-tl .nbtl-row') && p && p.getBoundingClientRect().width > 2); }" % FRONT

def cover_open(pg):
    pg.keyboard.press("Escape"); pg.mouse.move(700, 450)
    if not pg.evaluate("() => !!(window.__nbCoverShow && window.__nbCoverShow(true))"): return None
    for _ in range(20):
        pg.wait_for_timeout(250)
        if pg.evaluate(COVER_ON): break
    pg.wait_for_timeout(1500)
    return "cover" if pg.evaluate(COVER_ON) else None

def cover_close(pg, name):
    try:
        if name: pg.evaluate("() => { if (window.__nbCoverShow) window.__nbCoverShow(false); }")
        pg.wait_for_timeout(1200)
    except Exception:
        pass

ROWS = r"""() => { var P = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden)'); P = P[P.length - 1]; var tl = P.querySelector('.nbcover-tl');
  var kind = function(r){ var m = /nbtl-(title|group|sub|chapter|figure|task|coding|quiz|byod|end|cell)\b/.exec(r.className); return m ? m[1] : '?'; };
  var ch = null;
  return [].map.call(tl.querySelectorAll('.nbtl-row'), function(r, i){
    var k = kind(r); if (k === 'chapter') ch = r.getAttribute('data-st'); else if (/^(title|group|end|cell)$/.test(k)) ch = null;
    var m = r.querySelector('.nbtl-mk'), op = 1;
    for (var e = m; e && e.nodeType === 1; e = e.parentElement) op *= +getComputedStyle(e).opacity;
    var t = /\bnbtl-k-([a-z0-9]+)/.exec(r.className);
    return {i: i, k: k, t: t ? t[1] : null, st: r.getAttribute('data-st'), ch: ch, op: Math.round(op * 100) / 100,
            col: m ? getComputedStyle(m).color : null, shown: getComputedStyle(r).display !== 'none'}; }); }"""

def _kexec(code):
    import lab_marks
    lab_marks.BASE = os.environ.get("DIGICHEM_LAB_URL", lab_marks.BASE)
    lab_marks.KHOME = os.environ.get("DIGICHEM_KERNEL_HOME") or lab_marks.KHOME
    return lab_marks.kexec(code)

def _progress(pg):
    """exercise 1 solved; the coding lock in front of coding 2 opened while coding 1 is
    still open (two unlocked coding exercises) — in the kernel of the notebook under test"""
    if getattr(pg, "_j23p", False): return "kept"
    out = _kexec("task_solved('t1')\n"
                 "g = _TASKS['cguard'].get('t2')\n"
                 "_LOCKS[('code', g)]['open'] = True\n"
                 "_refresh_progress()\n"
                 "print(g, _code_class('t1'), _code_class('t2'), _dot_class('t2'))")
    pg._j23p = True
    pg.wait_for_timeout(3500)
    return out.strip()

def _sentinel(pg):
    # the panel of the notebook under test must show the progress before the cover is read
    return pg.evaluate("""() => { var h = document.getElementById('nbpanel-root'); if (!h) return null;
      var c = function(t, s){ var n = h.querySelector('.nbmap-node' + s + '[data-task="' + t + '"]'); var m = n && n.querySelector('.nbrail-dot,.nbcodemark'); return m ? m.className : null; };
      return {c1: c('t1', '.codetask'), c2: c('t2', '.codetask'), t2: c('t2', '.task')}; }""")

def open_highest(pg, ctx):
    k = _progress(pg)
    s = _sentinel(pg)
    if not s or "cd-open" not in (s["c1"] or "") or "cd-open" not in (s["c2"] or ""):
        return False, "BAD kernel progress did not reach the panel (%s · %s)" % (k, s)
    name = cover_open(pg)
    if not name: return False, "BAD no cover (output .nbcover-out)"
    try:
        rows = [r for r in pg.evaluate(ROWS) if r["shown"]]
    finally:
        cover_close(pg, name)
    bad, det = [], []
    for kind in ("task", "coding"):
        ln = [r for r in rows if r["k"] == kind]
        op = [r for r in ln if r["st"] == "open"]
        un = [r for r in ln if r["st"] in ("open", "free")]
        det.append("%s open %s free %s" % (kind, [r["t"] for r in op], [r["t"] for r in un if r["st"] == "free"]))
        if len(op) != 1: bad.append("%s: %d open marks (want 1)" % (kind, len(op)))
        elif un and op[0]["i"] != un[-1]["i"]: bad.append("%s: open is %s, highest unlocked %s" % (kind, op[0]["t"], un[-1]["t"]))
        purple_or_green = [r["t"] for r in un if r["st"] == "free" and r["col"] in ("rgb(107, 63, 209)", "rgb(30, 122, 76)", "rgb(124, 58, 237)")]
        if purple_or_green: bad.append("%s: free marks in lane colour %s" % (kind, purple_or_green))
    want = {"coding": "t2", "task": "t2"}
    for kind, t in want.items():
        op = [r["t"] for r in rows if r["k"] == kind and r["st"] == "open"]
        if op != [t]: bad.append("%s: open %s, want [%s]" % (kind, op, t))
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(det) + " (kernel: %s)" % k

def locked_pale(pg, ctx):
    name = cover_open(pg)
    if not name: return False, "BAD no cover (output .nbcover-out)"
    try:
        pg.evaluate("() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; P.querySelector('.nbcover-tl').scrollIntoView({block: 'center'}); }" % FRONT)
        pg.mouse.move(5, 450); pg.wait_for_timeout(900)
        rows = [r for r in pg.evaluate(ROWS) if r["shown"]]
    finally:
        cover_close(pg, name)
    bad = []
    chs = [r for r in rows if r["k"] == "chapter"]
    lch = [r for r in chs if r["st"] == "locked"]
    if not lch or len(lch) == len(chs): return False, "BAD %d of %d chapters locked" % (len(lch), len(chs))
    ex = [r for r in rows if r["k"] in ("task", "coding") and r["ch"] == "locked"]
    bad += ["%s %s in a locked chapter is %s" % (r["k"], r["t"], r["st"]) for r in ex if r["st"] != "locked"][:3]
    fl = [r for r in rows if r["k"] == "figure" and r["ch"] == "locked"]
    fo = [r for r in rows if r["k"] == "figure" and r["ch"] not in ("locked", None)]
    if not fl or not fo: return False, "BAD figures in locked %d / open %d chapters" % (len(fl), len(fo))
    bad += ["figure #%d of a locked chapter: state %s, opacity %.2f" % (r["i"], r["st"], r["op"]) for r in fl if r["st"] != "locked" or r["op"] > 0.5][:3]
    bad += ["figure #%d of an open chapter: state %s, opacity %.2f" % (r["i"], r["st"], r["op"]) for r in fo if r["st"] or r["op"] < 0.9][:3]
    bad += ["%s locked" % r["k"] for r in rows if r["k"] in ("quiz", "byod") and r["st"] == "locked"]
    return (not bad), ("; ".join(bad) + " | " if bad else "") + "chapters locked %d/%d · figures locked %d (op %s) · open %d (op %s)" % (
        len(lch), len(chs), len(fl), sorted(set(r["op"] for r in fl)), len(fo), sorted(set(r["op"] for r in fo)))

# J23.7 first (fresh progress), then J23.3 (changes the progress in the kernel)
TESTS = [("J23.7 cover: locked chapters, pale figures", locked_pale),
         ("J23.3 cover: open = highest unlocked", open_highest)]
