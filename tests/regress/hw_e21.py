"""E21.0 — the Hauptwerkstatt's first regress tests (2026-10-02). Each one is
a thing the reader had accepted and reported broken in v1.60 (E21 B). They
measure in the page (getBoundingClientRect, getComputedStyle, the DOM) — never
the markup we wrote. The workshops add their own t_<werkstatt>.py and may
sharpen or replace these (say so in the chronicle: "behauptete bisher …").
Order matters: the tests that change the notebook (YOC adds a cell) run last."""

VIS = r"""window.__rvh = window.__rvh || function(e){ if (!e) return false;
  var r = e.getBoundingClientRect(), cs = getComputedStyle(e);
  return r.width > 0.5 && r.height > 0.5 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.05; };"""

def _ev(pg, js, arg=None):
    pg.evaluate("() => {" + VIS + "}")
    return pg.evaluate(js, arg) if arg is not None else pg.evaluate(js)

def to_panel(pg):
    """Command mode, pointer parked over the document, no tooltip, nothing open."""
    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
    pg.mouse.move(700, 450); pg.wait_for_timeout(300)

# ---------------------------------------------------------------- B5
STILL_JS = r"""async () => {
  var h = document.getElementById('nbpanel-root'); if (!h) return {bad: 'no panel'};
  var pick = function(){ var o = [];
    var r = h.getBoundingClientRect(); o.push(r.left, r.top, r.width, r.height);
    h.querySelectorAll('.nbmap-node').forEach(function(n){ var q = n.getBoundingClientRect(); o.push(q.left, q.top, q.width, q.height); });
    return o; };
  var a = pick(), max = 0, n = 0, at = -1;
  for (var i = 0; i < 30; i++) {
    await new Promise(function(res){ setTimeout(res, 100); });
    var b = pick(); if (b.length !== a.length) return {bad: 'node count changed ' + a.length / 4 + ' -> ' + b.length / 4};
    for (var j = 0; j < a.length; j++) { var d = Math.abs(a[j] - b[j]); if (d > max) { max = d; at = j; } }
    n++;
  }
  return {max: Math.round(max * 10) / 10, nodes: a.length / 4 - 1, samples: n, at: at};
}"""
def panel_still(pg, ctx):
    """E21.5 / Video 1: without any input, nothing in the panel moves for 3 s."""
    to_panel(pg); pg.wait_for_timeout(1500)
    r = pg.evaluate(STILL_JS)
    if "bad" in r: return False, "BAD " + r["bad"]
    return r["max"] <= 0.5, "max change %.1f px over 3 s, %d marks" % (r["max"], r["nodes"])

# ------------------------------------------------- tool windows 10/10 (+ B4)
OPEN_JS = r"""(sel) => {
  var h = document.getElementById('nbpanel-root'), b = document.querySelector('.nbcorner ' + sel);
  var d = h && h.querySelector('.nbdrawer');
  var cells = d ? [].filter.call(d.querySelectorAll('.nbcell'), window.__rvh) : [];
  var ctl = d ? (d.innerText || '').trim().length : 0;     // the window says something
  return {btn: !!b, btnVis: window.__rvh(b), open: !!(h && h.classList.contains('open')), page: h && h.dataset.page,
          drawer: window.__rvh(d), cells: cells.length, ctl: ctl,
          xy: b ? (function(r){ return [r.left + r.width / 2, r.top + r.height / 2]; })(b.getBoundingClientRect()) : null};
}"""
PAGES = [("gear", ".nbbtn.nbgear", "diff"), ("profile", ".nbbtn.nbprofile", "code"),
         ("series", ".nbbtn.nbseries", "stats"), ("keys", ".nbbtn.nbkeys", "help")]
# what "open" means: the drawer on its page — or, for ⌨, the help window (R3 · 19)
IS_OPEN = r"""(p) => { if (p === 'help') { var w = document.querySelector('.nbhelp.on');
    return !!(w && window.__rvh(w) && (w.innerText || '').trim().length > 20); }
  var h = document.getElementById('nbpanel-root'), d = h && h.querySelector('.nbdrawer');
  if (!(h && h.classList.contains('open') && h.dataset.page === p && window.__rvh(d))) return false;
  var cells = [].filter.call(d.querySelectorAll('.nbcell'), window.__rvh);
  return cells.length > 0 && cells.some(function(c){ return (c.innerText || '').trim().length > 20; }); }"""
IS_SHUT = r"""(p) => p === 'help' ? !document.querySelector('.nbhelp.on')
  : !document.getElementById('nbpanel-root').classList.contains('open')"""
def windows_10(pg, ctx):
    """Every tool window in the corner opens 10/10 by one click, shows content,
    and closes by Esc. A button hidden on purpose (display:none, E17.2 📚) is not
    counted; a window that needs a second click counts as a miss."""
    to_panel(pg); out, ok = [], True
    for name, sel, page in PAGES:
        s = _ev(pg, OPEN_JS, sel)
        if not s["btn"]: out.append("%s: no button" % name); ok = False; continue
        if not s["btnVis"]: out.append("%s: hidden" % name); continue
        good = 0
        for i in range(10):
            s = _ev(pg, OPEN_JS, sel)
            pg.mouse.click(*s["xy"])
            try:
                pg.evaluate("() => {" + VIS + "}")
                pg.wait_for_function(IS_OPEN, arg=page, timeout=2500); good += 1
            except Exception:
                pass
            pg.keyboard.press("Escape")
            try:
                pg.wait_for_function(IS_SHUT, arg=page, timeout=2500)
            except Exception:
                pg.mouse.click(700, 450); pg.wait_for_timeout(400)     # outside: it must shut
                if not pg.evaluate(IS_SHUT, page):
                    out.append("%s: Esc and click outside leave it open" % name); ok = False; break
        out.append("%s %d/10" % (name, good)); ok = ok and good == 10
    to_panel(pg)
    return ok, " · ".join(out)

# ---------------------------------------------------------------- B1
TITLE_JS = r"""() => {
  var h = document.getElementById('nbpanel-root');
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var nodes = h ? [].slice.call(h.querySelectorAll('.nbmap-node')) : [];
  var keep = function(n){ return n.dataset.acc === 'title' || n.dataset.acc === 'yoc' || n.classList.contains('own'); };
  // a mark is drawn by its children (the <a> itself is 0 px high); .nbgone = folded away
  var shown = function(n){ return !n.classList.contains('nbgone') && [n].concat([].slice.call(n.querySelectorAll('*'))).some(window.__rvh); };
  var other = nodes.filter(function(n){ return !keep(n) && shown(n); }).length;
  var t = h && h.querySelector('.nbmap-node[data-acc="title"]');
  var tr = t ? t.getBoundingClientRect() : null;
  var at = P && P.querySelector('.acc-title.acc-root .jupyter-widget-Collapse-contents');
  var card = P && P.querySelector('.jp-OutputArea .nbtitle-card');
  var cr = card ? card.getBoundingClientRect() : null;
  return {other: other, all: nodes.length, xy: tr ? [tr.left + tr.width / 2, tr.top + tr.height / 2] : null,
          body: at ? Math.round(at.getBoundingClientRect().height) : null,
          card: cr && cr.height > 0 ? [cr.left + cr.width / 2, cr.top + Math.min(cr.height / 2, 40)] : null};
}"""
def _title_round(pg, where):
    s0 = _ev(pg, TITLE_JS)
    if s0["other"] == 0:                       # left folded by someone: open it first (not counted)
        xy = s0["xy"] if where == "mark" else s0["card"]
        if xy: pg.mouse.click(*xy); pg.wait_for_timeout(1400)
        s0 = _ev(pg, TITLE_JS)
        if s0["other"] == 0: return False, "BAD %s: title stays folded, cannot start" % where
    xy = s0["xy"] if where == "mark" else s0["card"]
    if not xy: return False, "BAD no %s to click" % where
    pg.mouse.click(*xy); pg.wait_for_timeout(1400)          # ONE click folds …
    s1 = _ev(pg, TITLE_JS)
    xy = s1["xy"] if where == "mark" else (s1["card"] or s0["card"])
    pg.mouse.click(*xy); pg.wait_for_timeout(1400)          # … ONE click opens again
    s2 = _ev(pg, TITLE_JS)
    ok = s1["other"] == 0 and (s1["body"] or 0) <= 1 and s2["other"] == s0["other"] and (s2["body"] or 0) > 1
    return ok, "%s, one click each: marks below title %d -> %d -> %d, title body %s -> %s -> %s px" % (
        where, s0["other"], s1["other"], s2["other"], s0["body"], s1["body"], s2["body"])

def title_mark(pg, ctx):
    """E21.1 / E11.2 / E9.5: a click on the CHOSEN title mark folds everything
    below it in the document AND the timeline (only title, YOC, own cells stay);
    the next click opens it again. By design (E9.5) a first click on an unchosen
    title mark only lands on the title — that click is made first and not counted."""
    to_panel(pg)
    sel = pg.evaluate("() => { var t = document.querySelector('#nbpanel-root .nbmap-node[data-acc=\"title\"]'); return !!(t && t.classList.contains('nbsel')); }")
    if not sel:
        s = _ev(pg, TITLE_JS)
        if s["xy"]: pg.mouse.click(*s["xy"]); pg.wait_for_timeout(1600)
        if not pg.evaluate("() => { var t = document.querySelector('#nbpanel-root .nbmap-node[data-acc=\"title\"]'); return !!(t && t.classList.contains('nbsel')); }"):
            return False, "BAD title mark not chosen after a click"
    ok, det = _title_round(pg, "mark")
    return ok, det + ("" if sel else " (chosen first)")

def title_card(pg, ctx):
    """E21.1: the same from the document (click on the title card)."""
    to_panel(pg)
    pg.evaluate("() => { var c = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-OutputArea .nbtitle-card'); if (c) c.scrollIntoView({block: 'center'}); }")
    pg.wait_for_timeout(900)
    return _title_round(pg, "card")

# ---------------------------------------------------------------- B2
CODE_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var w = [].filter.call(P.querySelectorAll('.codearea.nbedov'), function(e){ return window.__rvh(e.querySelector('textarea')); })[0];
  if (!w) return {n: P.querySelectorAll('.codearea.nbedov').length};
  var ta = w.querySelector('textarea'), r = ta.getBoundingClientRect();
  return {n: 1, xy: [r.left + 20, r.top + 12]};
}"""
COLOR_JS = r"""() => {
  var a = document.activeElement, w = a && a.closest && a.closest('.codearea.nbedov');
  if (!w) return {bad: 'focus not in a coding field'};
  var hl = w.querySelector('.nbedov-hl');
  var cols = {}; if (hl) hl.querySelectorAll('span').forEach(function(s){ if (window.__rvh(s) || s.textContent.trim()) cols[getComputedStyle(s).color] = 1; });
  return {on: w.classList.contains('on'), hlVis: window.__rvh(hl), colors: Object.keys(cols).length,
          taColor: getComputedStyle(a).color};
}"""
def code_colours(pg, ctx):
    """E21.2 / E19.3: typing in a coding field colours keyword, number, string and
    comment differently within 100 ms (the overlay is live and shows ≥ 3 colours)."""
    if ctx.get("mode") == "plain": return True, "plain: no coding field"
    to_panel(pg)
    # open the first chapter that holds a coding field, if it is folded
    pg.evaluate(r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
      var w = P.querySelector('.codearea.nbedov'); if (!w) return;
      var c = w; while ((c = c.parentElement && c.parentElement.closest('.jupyter-widget-Collapse'))) {
        if (!c.classList.contains('jupyter-widget-Collapse-open')) {
          var hd = c.querySelector(':scope > .jupyter-widget-Collapse-header'); if (hd) hd.click(); } }
      w.scrollIntoView({block: 'center'}); }""")
    pg.wait_for_timeout(1200)
    s = _ev(pg, CODE_JS)
    if not s.get("xy"): return False, "BAD no visible coding field (%d in DOM)" % s["n"]
    pg.mouse.click(*s["xy"]); pg.wait_for_timeout(250)
    pg.keyboard.press("End")
    pg.keyboard.type("\nif x: y = 12  # note\ns = 'abc'", delay=15)
    pg.wait_for_timeout(100)
    c = _ev(pg, COLOR_JS)
    for _ in range(len("\nif x: y = 12  # note\ns = 'abc'")):
        pg.keyboard.press("Backspace")
    pg.keyboard.press("Escape"); to_panel(pg)
    if "bad" in c: return False, "BAD " + c["bad"]
    ok = c["on"] and c["hlVis"] and c["colors"] >= 3
    return ok, "overlay on=%s visible=%s colours=%d (100 ms after typing)" % (c["on"], c["hlVis"], c["colors"])

# ---------------------------------------------------------------- B3
YOC_JS = r"""() => {
  var m = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]');
  var t = m && (m.querySelector('.nbsect') || m), r = t ? t.getBoundingClientRect() : null;
  var tip = document.querySelector('.nbtip');
  return {mark: !!m, vis: window.__rvh(t), xy: r ? [r.left + r.width / 2, r.top + r.height / 2] : null,
          tip: tip && tip.classList.contains('on') && window.__rvh(tip) ? tip.textContent.trim() : '',
          cells: document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell').length};
}"""
def yoc(pg, ctx):
    """E21.3 / E12.4: hovering the YOC mark shows the box "＋ Add your cell";
    a click makes one cell of one's own."""
    to_panel(pg)
    pg.evaluate("() => { var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); if (n) n.scrollTop = n.scrollHeight; }")
    pg.wait_for_timeout(1500)
    s = _ev(pg, YOC_JS)
    if not s["mark"] or not s["vis"]: return False, "BAD YOC mark %s" % ("hidden" if s["mark"] else "missing")
    pg.mouse.move(s["xy"][0] - 40, s["xy"][1] - 40); pg.wait_for_timeout(300)
    s = _ev(pg, YOC_JS)                                    # where it is NOW
    pg.mouse.move(*s["xy"], steps=4)
    h = {"tip": ""}
    for _ in range(15):                                    # ≤ 1.5 s for the box (delay 350 ms)
        pg.wait_for_timeout(100); h = _ev(pg, YOC_JS)
        if h["tip"]: break
    pg.mouse.click(*s["xy"]); pg.wait_for_timeout(2200)
    c = _ev(pg, YOC_JS)
    pg.keyboard.press("Escape"); to_panel(pg)
    ok = "Add your cell" in h["tip"] and c["cells"] == s["cells"] + 1
    return ok, "hover box %r · cells %d -> %d" % (h["tip"][:30], s["cells"], c["cells"])

TESTS = [("B5 panel still 3 s", panel_still),
         ("tool windows 10/10 (B4)", windows_10),
         ("B1 title mark folds", title_mark),
         ("B1 title card folds", title_card),
         ("B2 code colours live", code_colours),
         ("B3 YOC hover + cell", yoc)]
