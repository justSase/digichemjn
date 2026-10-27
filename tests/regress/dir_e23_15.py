"""E23.15 — the conductor's regress test for the JS point E23.15
(2026-10-06; Kategorie Applikation, Prüfwerkzeug). Module of tests/regress/run.py
(TESTS = [(name, fn)], fn(pg, ctx) -> (ok, detail)). Real JupyterLab, real
mouse, measured in the browser (getBoundingClientRect, getComputedStyle).

  D23.15  the chosen chapter stays on the reading line: reading height 25/50/75 %,
          a mark clicked, then 10 accordion changes above its pill, lens +3/−3,
          a hint opened: |pill − reading line| ≤ 2 px after EVERY frame (frame
          probe as js_e22: a ResizeObserver on a 1-px probe flipped in rAF —
          post-layout, pre-paint, after every observer of the page)
  D23.15b a scroll the reader did not make with his hand loosens the anchor too
          (Nach-Runde 06.10., Tor-Zeile J10 after J11): a mark clicked, 2 s later
          (after the landing's passes) a script scrolls the page 700 px on (as
          JupyterLab or a find does);
          then an accordion on screen opens and shuts: the anchor is gone and
          the page is NOT pulled back to the chosen mark (|scrollTop − where
          the script put it| ≤ 40 px, 2 s later and over both toggles).
          v1.65 + js-E23.15 (e40cd95b): the anchor held, the first size change
          pulled the page back up.

A test that cannot reach its precondition returns False ("BAD …"), never True."""
import os, sys, importlib.util
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_js_e22_for_dir", os.path.join(_HERE, "js_e22.py"))
J = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(J)

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"

# ---------------------------------------------------------------- D23.15
# per frame: the pill of the chosen mark (the first drawn accordion header after
# its anchor, as js_e22 pillOf) against the reading line (.nbreadfix, else rail
# top + railY0); and the lens, to say which step a frame belongs to
PIN_START = r"""(i) => {
  var h = document.getElementById('nbpanel-root'); window.__d15 = []; window.__d15on = true;
  var n = h.querySelectorAll('.nbmap-node')[i], A = document.getElementById(n.getAttribute('data-target'));
  var line = function(){ var fx = h.querySelector(':scope > .nbreadfix'), y = fx ? parseFloat(fx.style.top) : NaN;
    if (!(y > 0)) { var mp = h.querySelector('.nbmap'); y = mp.getBoundingClientRect().top + (parseInt(h.dataset.railY0 || '0', 10) || 0); }
    return y; };
  var pill = function(){
    var hs = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-header');
    for (var k = 0; k < hs.length; k++) if (A.compareDocumentPosition(hs[k]) & 4) { var r = hs[k].getBoundingClientRect();
      if (r.height > 0) return r.top + r.height / 2; }
    return null; };
  var tick = function(){ if (!window.__d15on) return; var p = pill(), L = line();
    window.__d15.push([performance.now(), p === null ? null : +(p - L).toFixed(2), window.__d15tag || '']); };
  var pr = document.getElementById('__d15probe');
  if (!pr) { pr = document.createElement('div'); pr.id = '__d15probe';
    pr.style.cssText = 'position:fixed;left:0;top:0;height:1px;width:1px;pointer-events:none;opacity:0'; document.body.appendChild(pr); }
  if (window.__d15RO) window.__d15RO.disconnect();
  window.__d15RO = new ResizeObserver(function(){ tick(); }); window.__d15RO.observe(pr);
  var gen = window.__d15gen = (window.__d15gen || 0) + 1;
  var flip = function(){ if (!window.__d15on || gen !== window.__d15gen) return; pr.style.width = pr.style.width === '1px' ? '2px' : '1px'; requestAnimationFrame(flip); };
  requestAnimationFrame(flip); }"""
PIN_STOP = "() => { window.__d15on = false; if (window.__d15RO) window.__d15RO.disconnect(); return window.__d15; }"
# accordion headers above the pill that are not its ancestors (toggling those
# would hide the pill): drawn, below the panel's top, nearest first
ABOVE = r"""(i) => { var h = document.getElementById('nbpanel-root'), n = h.querySelectorAll('.nbmap-node')[i];
  var A = document.getElementById(n.getAttribute('data-target'));
  var hs = [].slice.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-header'));
  var out = [];
  hs.forEach(function(x, k){ var col = x.parentElement; if (!col || col.contains(A)) return;
    if (!(x.compareDocumentPosition(A) & 4)) return;            // A follows x: x is above
    if (col.closest('.acc-title.acc-root') === col) return;     // the title folds everything
    var r = x.getBoundingClientRect(); if (!(r.height > 0)) return;
    out.push([k, (x.textContent || '').trim().slice(0, 24)]); });
  return out.reverse(); }"""
HEAD_CLICK = r"""(k) => { var hs = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-header'); hs[k].click(); }"""

def _line_to(pg, frac):
    g = J._grip(pg)
    m = pg.evaluate("()=>{var r=document.querySelector('#nbpanel-root .nbmap').getBoundingClientRect(); return [r.top, r.height];}")
    J._drag(pg, g[0], g[1], 0, m[0] + m[1] * frac - g[1], 12, 25); pg.wait_for_timeout(1300)

def pin_holds(pg, ctx):
    """E23.15: reading height 25/50/75 %; a chapter's exercise mark clicked; then 10
    accordion changes above its pill, lens +3/−3 (Ctrl+wheel) and a hint opened:
    |pill − line| ≤ 2 px in every frame from 2.5 s after the click."""
    J._calm(pg); pg.wait_for_timeout(3000)
    bad, rows = [], []
    tasks = pg.evaluate(r"""()=>[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).map(function(n,i){
        return [i, n.classList.contains('task') && !n.classList.contains('nbgone') && !n.classList.contains('locked')];})
        .filter(function(x){return x[1];}).map(function(x){return x[0];})""")
    if not tasks: return False, "BAD no open exercise mark"
    ti = tasks[0]
    for frac in (0.25, 0.5, 0.75):
        _line_to(pg, frac)
        J._click_node(pg, ti); pg.wait_for_timeout(2600)
        ab = pg.evaluate(ABOVE, ti)
        if len(ab) < 1: bad.append("%d%% BAD no accordion above the pill" % (frac * 100)); continue
        def acts():
            for k in range(10):
                pg.evaluate("(t)=>{window.__d15tag=t;}", "acc%d" % k)
                hk = ab[k % min(2, len(ab))][0]
                pg.evaluate(HEAD_CLICK, hk); pg.wait_for_timeout(700)
            pg.mouse.move(520, 450)
            for dy, tag in ((-100, "lens+"), (100, "lens-")):
                pg.evaluate("(t)=>{window.__d15tag=t;}", tag)
                pg.keyboard.down("Control")
                for _ in range(3): pg.mouse.wheel(0, dy); pg.wait_for_timeout(120)
                pg.keyboard.up("Control"); pg.wait_for_timeout(1800)
            pg.evaluate("(t)=>{window.__d15tag=t;}", "hint")
            pg.evaluate("()=>{var b=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbhint-btn'); if(b) b.click();}")
            pg.wait_for_timeout(1200)
        pg.evaluate(PIN_START, ti); pg.wait_for_timeout(150)
        acts()
        rec = pg.evaluate(PIN_STOP)
        ds = [r[1] for r in rec]
        if len(rec) < 30: bad.append("%d%% BAD %d frames" % (frac * 100, len(rec))); continue
        nul = sum(1 for d in ds if d is None)
        worst = max([abs(d) for d in ds if d is not None] or [99])
        nbad = sum(1 for d in ds if d is not None and abs(d) > 2)
        jumps = sum(1 for a, b in zip(ds, ds[1:]) if a is not None and b is not None and abs(b - a) > 2)
        tagw = {}
        for r in rec:
            if r[1] is not None: tagw[r[2][:4]] = max(tagw.get(r[2][:4], 0), abs(r[1]))
        rows.append("%d%% (above: %s): %d frames, worst %.1f px, %d frames > 2, %d jumps > 2 %s" % (
            frac * 100, "/".join(x[1][:12] for x in ab[:2]), len(rec), worst, nbad, jumps, {k: round(v, 1) for k, v in tagw.items()}))
        if nul: bad.append("%d%% pill not drawn in %d frames" % (frac * 100, nul))
        if worst > 2 or jumps: bad.append("%d%% |pill − line| up to %.1f px (%d frames, %d jumps)" % (frac * 100, worst, nbad, jumps))
    # the reader's own wheel loosens the anchor: a wheel over the document, then the
    # page is his (no pull back to the chosen mark)
    pg.mouse.move(520, 500)
    for _ in range(3): pg.mouse.wheel(0, 120); pg.wait_for_timeout(80)
    pg.wait_for_timeout(1200)
    st0 = pg.evaluate("()=>(document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')||{}).scrollTop")
    loose = pg.evaluate("()=>window.__nbPinned ? window.__nbPinned() : 'no anchor'")
    pg.wait_for_timeout(1500)
    st1 = pg.evaluate("()=>(document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')||{}).scrollTop")
    rows.append("after the wheel: anchor %s, page %s → %s" % (loose, st0, st1))
    if loose is not None or st0 != st1: bad.append("the wheel did not loosen the anchor (%s, %s → %s)" % (loose, st0, st1))
    J._reset(pg)
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(rows)

# ---------------------------------------------------------------- D23.15b
SC = "document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')"
NEAR = r"""(i) => { var h = document.getElementById('nbpanel-root'), n = h.querySelectorAll('.nbmap-node')[i];
  var A = document.getElementById(n.getAttribute('data-target')), vh = innerHeight;
  var hs = [].slice.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-header'));
  for (var k = 0; k < hs.length; k++) { var r = hs[k].getBoundingClientRect(), col = hs[k].parentElement;
    if (!(r.height > 0) || col.contains(A) || r.top < 150 || r.bottom > vh - 150) continue;
    hs[k].setAttribute('data-d15b', '1'); return Math.round(r.top); }
  return null; }"""
SPOT = r"""() => { var e = document.querySelector('[data-d15b]'), sc = """ + SC + """;
  return {y: e ? Math.round(e.getBoundingClientRect().top) : null, st: Math.round(sc.scrollTop), pin: window.__nbPinned ? !!window.__nbPinned() : null}; }"""

def script_scroll_frees(pg, ctx):
    """E23.15 Nach-Runde: a scroll made by a script (JupyterLab, a find) loosens the anchor
    as the wheel does; the page stays where the script put it, also over size changes."""
    J._calm(pg); pg.wait_for_timeout(1500)
    tasks = pg.evaluate(r"""()=>[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).map(function(n,i){
        return [i, n.classList.contains('task') && !n.classList.contains('nbgone') && !n.classList.contains('locked')];})
        .filter(function(x){return x[1];}).map(function(x){return x[0];})""")
    if not tasks: return False, "BAD no open exercise mark"
    J._click_node(pg, tasks[0]); pg.wait_for_timeout(2000)
    if not pg.evaluate("()=>window.__nbPinned ? !!window.__nbPinned() : false"): return False, "BAD no anchor after the click"
    # 2 s after the click (the landing's last pass is at 1.4 s; before that the landing
    # itself takes the page back to the mark, E6.3 — not the anchor's business): a script scrolls
    st0, st = pg.evaluate("()=>{ var s = %s, a = s.scrollTop; s.scrollTop = a + 700; return [Math.round(a), Math.round(s.scrollTop)]; }" % SC)
    if st - st0 < 300: J._reset(pg); return False, "BAD the script could not scroll (%s → %s)" % (st0, st)
    pg.wait_for_timeout(2000)
    y = pg.evaluate(NEAR, tasks[0])
    # py-E26.1 (11.10.): where the +700 px of the script land between two
    # headings (the page is ~20 px shorter since py-E26.1: four script outputs
    # less above the document), the script scrolls on in steps of 300 px —
    # still a script's scroll, the subject of this test (behauptete bisher:
    # one fixed +700, BAD "no heading on screen" by position alone)
    for _ in range(3):
        if y is not None: break
        st = pg.evaluate("()=>{ var s = %s; s.scrollTop = s.scrollTop + 300; return Math.round(s.scrollTop); }" % SC)
        pg.wait_for_timeout(1500)
        y = pg.evaluate(NEAR, tasks[0])
    seq = [pg.evaluate(SPOT)]
    if y is not None:
        for _ in range(2):                       # an accordion on screen opens and shuts: sizes change
            pg.evaluate("()=>{ document.querySelector('[data-d15b]').click(); }"); pg.wait_for_timeout(1500)
            seq.append(pg.evaluate(SPOT))
    pg.evaluate("()=>{ var e = document.querySelector('[data-d15b]'); if (e) e.removeAttribute('data-d15b'); }")
    J._reset(pg)
    bad = []
    if y is None: bad.append("BAD no heading on screen to toggle")
    if seq[0]["pin"]: bad.append("anchor still held after the script's scroll")
    worst = max(abs(s["st"] - st) for s in seq)
    if worst > 40: bad.append("page pulled %d px (scrollTop %s)" % (worst, [s["st"] for s in seq]))
    return (not bad), ("; ".join(bad) + " | " if bad else "") + "script: scrollTop %s → %s; then %s · anchor %s" % (
        st0, st, [s["st"] for s in seq], [s["pin"] for s in seq])

TESTS = [("D23.15 chosen mark stays on the line", pin_holds),
         ("D23.15b script scroll loosens the anchor", script_scroll_frees)]
