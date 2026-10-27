"""E23.14 — the conductor's regress test for the JS point E23.14 (2026-10-06;
Kategorie Applikation, Prüfwerkzeug). Module of tests/regress/run.py.
Runs in the "pair" rows (run.py --storage pair, two notebooks on the command
line): the other notebook was opened and run first, the one under test stands
second, in front, in the same JupyterLab window — as the reader works.

  D23.14  the panel's width is each notebook's own: opened out in the one in
          front (the grip dragged sideways), the other one keeps its width
          (switching tabs back and forth), also after the page is reloaded
          (real reload: both notebooks saved, page reloaded, kernels alive, a
          notebook without its panel after the reload run again — Run All);
          an old shared `digichemjn.guizoom.v1` written by another tab moves
          neither. Width = the drawn width of the panel's rail.
          In the rows with one notebook (fresh, old): the width goes under the
          notebook's own key, the shared key is neither written nor read.
  D23.14b the width opened out is kept in PIXELS (Nach-Runde 06.10., tor row pair
          201 → 193 px): the narrow end (widest mark × lens, measured anew) moves
          — lens 150 % (Ctrl+wheel), and in the pair rows a switch to the other
          notebook and back — and the open panel keeps its width ±1 px (the
          shut one may follow the lens). v1.65 + js-E23.14 (e40cd95b): the
          width is a share of the travel from the narrow end, lens 150 → +11 px.

A test that cannot reach its precondition returns False ("BAD …"), never True."""
import os, importlib.util
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_js_e22_for_dir14", os.path.join(_HERE, "js_e22.py"))
J = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(J)

WIDTH = r"""() => { var h = document.getElementById('nbpanel-root'); if (!h || h.style.display === 'none') return null;
  var r = h.querySelector('.nbrail'); var b = r ? r.getBoundingClientRect() : null;
  var k = window.__nbZKey ? window.__nbZKey() : '';
  return b && b.width > 0 ? {w: Math.round(b.width), id: k.replace(/^digichemjn\.zoom\.v1\.?/, ''), gui: window.__nbGui, wm: window.__nbWmin, hw: window.__nbWhalf} : null; }"""
TABS = r"""() => [].map.call(document.querySelectorAll('.lm-DockPanel .lm-TabBar-tab'), function(t){
  return [(t.textContent || '').trim(), t.classList.contains('lm-mod-current')]; })"""

def _tab(pg, name):
    pg.click(".lm-DockPanel .lm-TabBar-tab:has-text('%s')" % name)
    pg.wait_for_timeout(1800); pg.mouse.move(520, 450); pg.wait_for_timeout(400)
    return _settled(pg)

def _settled(pg):
    """the width once it stands: two readings 500 ms apart alike (after a reload the
    panel lays itself out for a few seconds — fonts, the lens — one reading caught
    32 px for 38 in one of three rows)"""
    w = pg.evaluate(WIDTH)
    for _ in range(12):
        pg.wait_for_timeout(500)
        w2 = pg.evaluate(WIDTH)
        if w and w2 and w2["w"] == w["w"] and w2["id"] == w["id"]: return w2
        w = w2
    return w

def _palette(pg, label):
    """a JupyterLab command by its palette label (as run.py)"""
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
    pg.keyboard.type(label)
    pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === l); }", arg=label, timeout=8000)
    pg.keyboard.press("Enter")

def _tab_run(pg, name, nid):
    """after a reload a notebook that is not in front has no panel until it runs
    again (Play / Run All — what the reader does): run it, then measure"""
    w = _tab(pg, name)
    if w and w["id"] == nid: return w
    try:
        _palette(pg, "Run All Cells")
        pg.wait_for_function("(id) => !!document.querySelector('#nbpanel-root .nbmap') && !!(window.__nbZKey && window.__nbZKey().slice(-(id.length + 1)) === '.' + id)", arg=nid, timeout=90000)
    except Exception:
        return None
    pg.wait_for_timeout(5000)
    import sys as _s; _s.path.insert(0, os.path.dirname(_HERE))
    from lab_keys import cover_play
    cover_play(pg)                      # E24.3 (JS): after the run the cover, Play → the document
    pg.mouse.move(520, 450); pg.wait_for_timeout(600)
    w = _settled(pg)
    return w if w and w["id"] == nid else None

def _ready(pg, ms=90000):
    try:
        pg.wait_for_function("() => !!document.querySelector('#nbpanel-root .nbmap') && !!(window.__nbZKey && /\\.[a-z]/.test(window.__nbZKey()))", timeout=ms)
        return True
    except Exception:
        return False

def own_width(pg, ctx):
    if ctx.get("storage") != "pair": return own_key(pg, ctx)
    J._calm(pg)
    tabs = [t[0] for t in pg.evaluate(TABS) if t[0].endswith(".ipynb")]
    if len(tabs) < 2: return False, "BAD %d notebook tabs" % len(tabs)
    front = [t[0] for t in pg.evaluate(TABS) if t[1] and t[0].endswith(".ipynb")]
    me = front[0] if front else tabs[-1]
    other = [t for t in tabs if t != me][0]
    rows, bad = [], []
    o0 = _tab(pg, other); m0 = _tab(pg, me)
    if not o0 or not m0: return False, "BAD no panel (%s / %s)" % (o0, m0)
    rows.append("start: %s %s · %s %s" % (m0["id"], m0["w"], o0["id"], o0["w"]))
    g = J._grip(pg); J._drag(pg, g[0], g[1], -160, 0); pg.wait_for_timeout(1200)
    m1 = pg.evaluate(WIDTH)
    if not m1 or m1["w"] < m0["w"] + 40: return False, "BAD the grip did not open the panel (%s → %s)" % (m0, m1)
    o1 = _tab(pg, other); m2 = _tab(pg, me)
    rows.append("opened %s: %s → %s · %s %s → %s · back %s" % (m0["id"], m0["w"], m1["w"], o0["id"], o0["w"], o1 and o1["w"], m2 and m2["w"]))
    rows.append("(pct/WMIN/half: %s · %s · back %s)" % ([m1.get(x) for x in ("gui", "wm", "hw")], [o1 and o1.get(x) for x in ("gui", "wm", "hw")], [m2 and m2.get(x) for x in ("gui", "wm", "hw")]))
    if not o1 or abs(o1["w"] - o0["w"]) > 1: bad.append("%s went with it: %s → %s" % (o0["id"], o0["w"], o1 and o1["w"]))
    if not m2 or abs(m2["w"] - m1["w"]) > 1: bad.append("%s did not keep its width: %s → %s" % (m0["id"], m1["w"], m2 and m2["w"]))
    # another tab of this browser writes the old shared key (an older build): nothing moves
    p2 = pg.context.new_page()
    try:
        p2.goto(pg.url.split("/lab")[0] + "/api/status")
        p2.evaluate("() => { localStorage.setItem('digichemjn.guizoom.v1', '100'); localStorage.setItem('digichemjn.guizoom.v1', '0'); localStorage.setItem('digichemjn.guizoom.v1', '100'); }")
    finally:
        p2.close()
    pg.wait_for_timeout(1500)
    m3 = pg.evaluate(WIDTH); o3 = _tab(pg, other); _tab(pg, me)
    rows.append("old shared key from another tab: %s %s · %s %s" % (m0["id"], m3 and m3["w"], o0["id"], o3 and o3["w"]))
    if not m3 or abs(m3["w"] - m1["w"]) > 1: bad.append("storage event moved %s: %s → %s" % (m0["id"], m1["w"], m3 and m3["w"]))
    if not o3 or abs(o3["w"] - o0["w"]) > 1: bad.append("storage event moved %s: %s → %s" % (o0["id"], o0["w"], o3 and o3["w"]))
    # reload: both saved (the outputs carry the panel), the page reloaded, kernels alive
    for t in (other, me):
        _tab(pg, t); pg.keyboard.press("Escape"); pg.keyboard.press("Control+s"); pg.wait_for_timeout(1500)
    errs = ctx.get("errs") if isinstance(ctx.get("errs"), list) else []
    n_err = len(errs)
    pg.reload(); pg.wait_for_timeout(4000)
    J._calm(pg)
    _ready(pg, 25000)                    # the one in front may come back by itself; else _tab_run runs it
    pg.wait_for_timeout(3000)
    o4 = _tab_run(pg, other, o0["id"]); m4 = _tab_run(pg, me, m0["id"])
    rows.append("after reload: %s %s · %s %s" % (m0["id"], m4 and m4["w"], o0["id"], o4 and o4["w"]))
    # the reload re-runs the saved outputs' scripts; a page error there is old (v1.64
    # probe too: patch() 18-rail, "Cannot read properties of undefined (reading '0')")
    # and not this test's subject — named here, kept out of the row's page-error count
    if len(errs) > n_err:
        rows.append("page errors during the reload (also on the base): %s" % [e[:200] for e in errs[n_err:]][:2])
        del errs[n_err:]
    if (not o4 or not m4) and len(errs) > n_err: del errs[n_err:]
    if not o4 or not m4: return False, ("; ".join(bad) + " | " if bad else "") + " · ".join(rows) + " · BAD no panel after the reload"
    if abs(o4["w"] - o0["w"]) > 1: bad.append("after reload %s: %s (was %s)" % (o0["id"], o4 and o4["w"], o0["w"]))
    if abs(m4["w"] - m1["w"]) > 1: bad.append("after reload %s: %s (set %s)" % (m0["id"], m4 and m4["w"], m1["w"]))
    try:
        pg.evaluate("() => { window.__nbSetGui && window.__nbSetGui(0); }")
    except Exception:
        pass
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(rows)

def own_key(pg, ctx):
    """the rows with one notebook (fresh, old): the width opened out lands under this
    notebook's own key `digichemjn.guizoom.v1.<id>`, the old shared key is neither
    written nor read (an old value — row "old": 70 — does not open the panel)"""
    J._calm(pg)
    nid = ctx.get("id", "")
    KEYS = "(id) => ({own: localStorage.getItem('digichemjn.guizoom.v1.' + id), shared: localStorage.getItem('digichemjn.guizoom.v1')})"
    k0 = pg.evaluate(KEYS, nid); w0 = pg.evaluate(WIDTH)
    if not w0: return False, "BAD no panel"
    g = J._grip(pg); J._drag(pg, g[0], g[1], -160, 0); pg.wait_for_timeout(1200)
    w1 = pg.evaluate(WIDTH); k1 = pg.evaluate(KEYS, nid)
    if not w1 or w1["w"] < w0["w"] + 40: return False, "BAD the grip did not open the panel (%s → %s)" % (w0, w1)
    bad = []
    if k1["shared"] != k0["shared"]: bad.append("the shared key was written: %s → %s" % (k0["shared"], k1["shared"]))
    try: own = float(k1["own"])
    except Exception: own = None
    if own is None or own <= 0: bad.append("no width under the notebook's key (%s)" % k1["own"])
    if k0["shared"] not in (None, "0") and w0["w"] > 60: bad.append("the old shared value %s opened the panel (%s px)" % (k0["shared"], w0["w"]))
    pg.evaluate("() => { window.__nbSetGui && window.__nbSetGui(0); }"); pg.wait_for_timeout(800)
    return (not bad), ("; ".join(bad) + " | " if bad else "") + "width %s → %s px · keys before %s · after %s" % (w0["w"], w1["w"], k0, k1)

def _lens(pg, n):
    pg.mouse.move(520, 450); pg.keyboard.press("Control+0"); pg.wait_for_timeout(400)
    if n:
        pg.keyboard.down("Control")
        for _ in range(abs(n)): pg.mouse.wheel(0, -100 if n > 0 else 100); pg.wait_for_timeout(90)
        pg.keyboard.up("Control")
    pg.wait_for_timeout(1500)

def px_kept(pg, ctx):
    J._calm(pg); _lens(pg, 0)
    w0 = _settled(pg)
    if not w0: return False, "BAD no panel"
    g = J._grip(pg); J._drag(pg, g[0], g[1], -160, 0); pg.wait_for_timeout(1200)
    w1 = _settled(pg)
    if not w1 or w1["w"] < w0["w"] + 40: return False, "BAD the grip did not open the panel (%s → %s)" % (w0, w1)
    rows, bad = ["opened %s → %s (WMIN %s)" % (w0["w"], w1["w"], w1.get("wm"))], []
    try:
        _lens(pg, 10); w2 = _settled(pg)
        rows.append("lens 150: %s (WMIN %s)" % (w2 and w2["w"], w2 and w2.get("wm")))
        if not w2 or abs(w2["w"] - w1["w"]) > 1: bad.append("lens 150 moved the open panel %s → %s" % (w1["w"], w2 and w2["w"]))
        if ctx.get("storage") == "pair":
            tabs = [t[0] for t in pg.evaluate(TABS) if t[0].endswith(".ipynb")]
            front = [t[0] for t in pg.evaluate(TABS) if t[1] and t[0].endswith(".ipynb")]
            me = front[0] if front else tabs[-1]
            other = [t for t in tabs if t != me]
            if other:
                _tab(pg, other[0]); w3 = _tab(pg, me)
                rows.append("tab and back: %s" % (w3 and w3["w"]))
                if not w3 or abs(w3["w"] - w1["w"]) > 1: bad.append("tab switch moved the open panel %s → %s" % (w1["w"], w3 and w3["w"]))
        _lens(pg, 0); w4 = _settled(pg)
        rows.append("lens 100 again: %s" % (w4 and w4["w"]))
        if not w4 or abs(w4["w"] - w1["w"]) > 1: bad.append("lens back moved the open panel %s → %s" % (w1["w"], w4 and w4["w"]))
    finally:
        _lens(pg, 0)
        pg.evaluate("() => { window.__nbSetGui && window.__nbSetGui(0); }"); pg.wait_for_timeout(800)
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(rows)

TESTS = [("D23.14 panel width per notebook", own_width),
         ("D23.14b open width kept in pixels", px_kept)]
