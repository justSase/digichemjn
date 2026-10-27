"""E21.0 — the JS workshop's regress tests (2026-10-02; Kategorie Applikation,
Prüfwerkzeug). Each test is a thing the reader had accepted and reported broken
in v1.60 (E21 B 1–6, C 7, 8, 10). They measure in a real JupyterLab
(getBoundingClientRect, getComputedStyle, the DOM, real mouse events) — never
the markup we wrote.

Two ways to run:
  * as a module of the Hauptwerkstatt's runner (tests/regress/run.py, contract
    of PATCH-hw-E21.0): TESTS = [(name, fn)], fn(pg, ctx) -> (ok, detail);
  * on its own:
      python3 tests/regress/js_e21.py <nb.ipynb> [<other.ipynb>]
              [--storage fresh,old,pair] [--skins minimal] [--themes light]
              [--only J1] [--json out.json]
    "pair" opens <other> first and runs it, then <nb> second, in front, in the
    SAME JupyterLab window (how the reader works: Complex and Modeling open).
    J6 (mode chosen on a cover) needs pair and runs only on its own.

Gegenprobe v1.61 (= v1.60 in every JS byte): see the chronicle 02.10., JS.
A test that cannot reach its precondition returns False ("BAD …"), never True."""
import os, sys, json, time, shutil, itertools, argparse, urllib.request

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"
VIS = r"""window.__rv = window.__rv || function(e){ if (!e) return false;
  var r = e.getBoundingClientRect(), cs = getComputedStyle(e);
  if (!(r.width > 0.5 && r.height > 0.5 && cs.visibility !== 'hidden' && cs.display !== 'none')) return false;
  for (var a = e; a && a.nodeType === 1; a = a.parentElement) if (+getComputedStyle(a).opacity <= 0.05) return false;
  return true; };
window.__rfront = function(){ var ps = document.querySelectorAll('.jp-NotebookPanel');
  for (var i = 0; i < ps.length; i++) if (!ps[i].classList.contains('lm-mod-hidden') && ps[i].getBoundingClientRect().width > 0) return ps[i];
  return null; };"""

def ev(pg, js, arg=None):
    pg.evaluate("() => {" + VIS + "}")
    return pg.evaluate(js, arg) if arg is not None else pg.evaluate(js)

def to_panel(pg):
    pg.evaluate("() => {" + VIS + "}")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
    pg.mouse.move(700, 450); pg.wait_for_timeout(300)

def hit(pg, x, y):
    """What a real click at (x, y) reaches: the topmost element there."""
    return pg.evaluate("""([x, y]) => { var e = document.elementFromPoint(x, y);
      return e ? (e.tagName + '.' + String(e.className && e.className.baseVal !== undefined ? e.className.baseVal : e.className).split(' ').slice(0, 3).join('.')) +
                 (e.closest('#nbpanel-root') ? ' (panel)' : '') : 'none'; }""", [x, y])

# ------------------------------------------------------------------ J1 title
TITLE_JS = r"""() => {
  var h = document.getElementById('nbpanel-root'), P = window.__rfront();
  var nodes = h ? [].slice.call(h.querySelectorAll('.nbmap-node')) : [];
  var keep = function(n){ return n.dataset.acc === 'title' || n.dataset.acc === 'yoc' || n.classList.contains('own'); };
  var shown = function(n){ return !n.classList.contains('nbgone') && [n].concat([].slice.call(n.querySelectorAll('*'))).some(window.__rv); };
  var t = h && h.querySelector('.nbmap-node[data-acc="title"]'), tr = t ? (t.querySelector('.nbsect') || t).getBoundingClientRect() : null;
  var at = P && P.querySelector('.acc-title.acc-root .jupyter-widget-Collapse-contents');
  var card = P && P.querySelector('.jp-OutputArea .nbtitle-card'), cr = card ? card.getBoundingClientRect() : null;
  var hid = [].filter.call(document.querySelectorAll('.jp-NotebookPanel.lm-mod-hidden .acc-title.acc-root .jupyter-widget-Collapse-contents'),
                           function(c){ return getComputedStyle(c).display === 'none'; }).length;
  return {other: nodes.filter(function(n){ return !keep(n) && shown(n); }).length, sel: !!(t && t.classList.contains('nbsel')),
          xy: tr ? [tr.left + tr.width / 2, tr.top + tr.height / 2] : null,
          body: at ? Math.round(at.getBoundingClientRect().height) : null, hiddenShut: hid,
          card: cr && cr.height > 0 ? [cr.left + cr.width / 2, cr.top + Math.min(cr.height / 2, 40)] : null};
}"""
def _title_round(pg, where):
    s0 = ev(pg, TITLE_JS)
    if s0["other"] == 0 or (s0["body"] or 0) <= 1:
        xy = s0["xy"] if where == "mark" else s0["card"]
        if xy: pg.mouse.click(*xy); pg.wait_for_timeout(1400)
        s0 = ev(pg, TITLE_JS)
        if s0["other"] == 0: return False, "BAD %s: title stays folded, cannot start" % where
    xy = s0["xy"] if where == "mark" else s0["card"]
    if not xy: return False, "BAD no %s to click" % where
    what = hit(pg, *xy)
    pg.mouse.click(*xy); pg.wait_for_timeout(1400)
    s1 = ev(pg, TITLE_JS)
    xy = s1["xy"] if where == "mark" else (s1["card"] or s0["card"])
    pg.mouse.click(*xy); pg.wait_for_timeout(1400)
    s2 = ev(pg, TITLE_JS)
    ok = (s1["other"] == 0 and (s1["body"] or 0) <= 1 and s2["other"] == s0["other"] and (s2["body"] or 0) > 1
          and s1["hiddenShut"] == s0["hiddenShut"])
    return ok, "%s (click hits %s): marks below %d -> %d -> %d · front title body %s -> %s -> %s px · hidden notebook shut %d -> %d" % (
        where, what, s0["other"], s1["other"], s2["other"], s0["body"], s1["body"], s2["body"], s0["hiddenShut"], s1["hiddenShut"])

def title_mark(pg, ctx):
    """E21.1 / E11.2: a click on the chosen title mark folds everything below it
    in the FRONT notebook and in the timeline; the next click opens it again.
    The first click on an unchosen mark only chooses it (E9.5, not counted).
    Another notebook open in the window must not be the one that folds."""
    to_panel(pg)
    # the rail is 1:1 with the document: the title's mark is on screen only near the top
    pg.evaluate("() => { var o = window.__rfront() && window.__rfront().querySelector('.jp-WindowedPanel-outer'); if (o) o.scrollTop = 0; }")
    pg.wait_for_timeout(1500)
    s = ev(pg, TITLE_JS)
    if not s["xy"] or not (0 < s["xy"][1] < 900): return False, "BAD no title mark on screen (%s)" % (s["xy"],)
    if not s["sel"]:
        pg.mouse.click(*s["xy"]); pg.wait_for_timeout(1600)
        if not ev(pg, TITLE_JS)["sel"]: return False, "BAD title mark not chosen after a click"
    ok, det = _title_round(pg, "mark")
    to_panel(pg); return ok, det

def title_card(pg, ctx):
    """E21.1: the same from the document (one click on the title card)."""
    to_panel(pg)
    pg.evaluate("() => { var c = document.querySelector('%s .jp-OutputArea .nbtitle-card'); if (c) c.scrollIntoView({block: 'center'}); }" % FRONT)
    pg.wait_for_timeout(900)
    ok, det = _title_round(pg, "card")
    to_panel(pg); return ok, det

# ------------------------------------------------------------------ J2 code colour
OPEN_CODE = r"""() => { var P = window.__rfront(); var w = P && P.querySelector('.codearea.nbedov'); if (!w) return 0;
  var c = w; while ((c = c.parentElement && c.parentElement.closest('.jupyter-widget-Collapse'))) {
    if (!c.classList.contains('jupyter-widget-Collapse-open')) { var hd = c.querySelector(':scope > .jupyter-widget-Collapse-header'); if (hd) hd.click(); } }
  w.scrollIntoView({block: 'center'}); return P.querySelectorAll('.codearea.nbedov').length; }"""
FIELD = r"""() => { var P = window.__rfront();
  var w = [].filter.call(P.querySelectorAll('.codearea.nbedov'), function(e){ return window.__rv(e.querySelector('textarea')); })[0];
  if (!w) return null; var r = w.querySelector('textarea').getBoundingClientRect(); return [r.left + 30, r.top + 12]; }"""
COLOURS = r"""() => {
  var a = document.activeElement, w = a && a.closest && a.closest('.codearea.nbedov');
  if (!w) return {bad: 'focus not in a coding field'};
  var hl = w.querySelector('.nbedov-hl'), cols = {}, vis = 0;
  if (hl) hl.querySelectorAll('span').forEach(function(s){ if (s.textContent.trim() && window.__rv(s)) { vis++; cols[getComputedStyle(s).color] = 1; } });
  var tc = getComputedStyle(a).color, transparent = /rgba\(.*,\s*0\)$|transparent/.test(tc);
  return {on: w.classList.contains('on'), hl: window.__rv(hl), colours: Object.keys(cols).length, spans: vis, transparent: transparent};
}"""
TYPED = "\nif x: y = 12  # note\ns = 'abc'"
def _type_and_look(pg, xy):
    pg.mouse.click(*xy); pg.wait_for_timeout(250)
    pg.keyboard.press("Control+End")
    pg.keyboard.type(TYPED, delay=12)
    pg.wait_for_timeout(100)
    c = ev(pg, COLOURS)
    for _ in range(len(TYPED)): pg.keyboard.press("Backspace")
    return c

def code_colours(pg, ctx):
    """E21.2 / E19.3: typing in a coding field colours keyword, number, string and
    comment within 100 ms — the colour layer is on and visible with ≥ 3 colours,
    and the field's own text is never transparent while the layer is off. Tested
    twice: first focus, and again after leaving the field for 3 s (E19.3)."""
    if ctx.get("mode") == "plain": return True, "plain: no coding field"
    to_panel(pg)
    n = ev(pg, OPEN_CODE); pg.wait_for_timeout(1300)
    xy = ev(pg, FIELD)
    if not xy: return False, "BAD no visible coding field (%d in DOM)" % n
    out, ok = [], True
    for rnd in ("first", "again"):
        xy = ev(pg, FIELD)
        c = _type_and_look(pg, xy)
        if "bad" in c: return False, "BAD %s: %s (click hit %s)" % (rnd, c["bad"], hit(pg, *xy))
        good = c["on"] and c["hl"] and c["colours"] >= 3
        invisible = c["transparent"] and not (c["on"] and c["hl"])
        ok = ok and good and not invisible
        out.append("%s: on=%s layer=%s colours=%d text-transparent=%s" % (rnd, c["on"], c["hl"], c["colours"], c["transparent"]))
        pg.keyboard.press("Escape"); to_panel(pg); pg.wait_for_timeout(3000)
    return ok, " · ".join(out)

RUN_ID = r"""() => { var P = window.__rfront && window.__rfront(), f = P && P.querySelectorAll('.nbfeed[data-progress]');
  return f && f.length ? f[f.length - 1].getAttribute('data-nbid') : null; }"""
RUN_ST = r"""() => { var P = window.__rfront && window.__rfront(), f = P && P.querySelectorAll('.nbfeed[data-progress]');
  var i = P && P.querySelector('.jp-Notebook-ExecutionIndicator');
  return {run: f && f.length ? f[f.length - 1].getAttribute('data-nbid') : null,
          status: i ? i.getAttribute('data-status') : 'no indicator',
          load: !!document.querySelector('#nbload:not(.nbload-out)')}; }"""
def code_colours_rerun(pg, ctx):
    """E21.2: the same after the reader reruns the notebook (Kernel ▸ Restart
    Kernel and Run All): the new fields colour too."""
    if ctx.get("mode") == "plain": return True, "plain: no coding field"
    run0 = ev(pg, RUN_ID)
    done = False
    for attempt in range(3):
        to_panel(pg)
        # the coding field typed into before keeps the focus: let go of it first
        pg.evaluate("() => { var a = document.activeElement; if (a && a.blur) a.blur(); }")
        pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        pg.keyboard.press("Control+Shift+C")
        try:
            pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=15000)
            pg.keyboard.type("Restart Kernel and Run All", delay=30)
            pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && /^Restart Kernel and Run All/.test(a.textContent.trim())); }", timeout=15000)
            done = True; break
        except Exception:
            pg.keyboard.press("Escape"); pg.wait_for_timeout(800)
    if not done: return False, "BAD palette: no 'Restart Kernel and Run All' (3 tries)"
    pg.keyboard.press("Enter")
    try:
        pg.wait_for_selector(".jp-Dialog", timeout=5000); pg.keyboard.press("Enter")
    except Exception:
        pass
    # E21 Rest (2026-10-03) — WAIT FOR THE NEW RUN, NOT FOR AN IDLE MOMENT.
    # BEHAUPTETE BISHER „the notebook has been run again“ once the indicator
    # said idle (or was missing) after 3 s. Measured (Complex cyber dark old,
    # one CPU): restart → busy → IDLE for ~0.3 s → busy for 17 s → idle; a
    # one-second poll that hits the short idle (or the idle BEFORE the restart)
    # ends the wait at once, and the test then reads the page of no run (gate
    # 03.10. 12:2x: „0 coding fields in DOM“, and J10/J3 after it red) — or, in
    # the other case, the OLD run's fields, green for the wrong reason. Now it
    # waits until the notebook in front shows a run id it did not have before
    # the restart, its kernel is idle and no loading view is up, three seconds
    # in a row (a stored mode may rebuild once); ≤ 150 s, else BAD.
    t0, calm, st = time.time(), 0, None
    while time.time() - t0 < 150 and calm < 3:
        pg.wait_for_timeout(1000)
        st = ev(pg, RUN_ST)
        calm = calm + 1 if (st["run"] and st["run"] != run0 and st["status"] == "idle" and not st["load"]) else 0
    if calm < 3:
        return False, "BAD the rerun did not finish in 150 s (run before %s, now %s)" % (run0, st)
    pg.wait_for_timeout(1500)
    ok, det = code_colours(pg, ctx)
    return ok, "after restart + run all (new run %s, %.0f s): %s" % (st["run"], time.time() - t0, det)

# ------------------------------------------------------------------ J11 marks after a rerun
# 2026-10-04 (E21 Nachtrag R1) — every mark of the panel points at an anchor
# of THIS run (ids carry the run's token), and a click on a chapter mark
# moves the document to it. Measured v1.62 after Restart + Run All: 39 of 39
# targets of the previous run, the click did nothing. Runs after J2-rerun, so
# the page has been rerun in every row that is not plain.
ANCHORS = r"""() => { var P = window.__rfront(), h = document.getElementById('nbpanel-root');
  var feed = P && P.querySelector('.nbfeed[data-nbid]'), run = feed ? feed.getAttribute('data-nbid') : null;
  var ns = h ? h.querySelectorAll('.nbmap-node[data-target]') : [], stale = [], foreign = 0;
  // a target of THIS run may be absent (a locked chapter's content is not
  // drawn); a target of another run never resolves to this document
  [].forEach.call(ns, function(n){ var t = n.getAttribute('data-target') || '', m = /__([0-9a-f]{8})$/.exec(t);
    if (m && m[1] !== run) { if (stale.length < 99) stale.push(t); return; }
    var e = document.getElementById(t); if (e && P && !P.contains(e)) foreign++; });
  return {n: ns.length, miss: stale, foreign: foreign, run: run}; }"""
JUMPTO = r"""() => { var h = document.getElementById('nbpanel-root');
  // an open exercise or section mark, not lit and not chosen (a second
  // click on the chosen mark folds instead of jumping), whose anchor is
  // drawn (after a rerun only chapter 1 is open: its sections, its exercise)
  // the mark itself has no box of its own: its drawn part does (as YOC)
  var face = function(n){ if (window.__rv(n)) return n; var d = n.querySelectorAll('*');
    for (var i = 0; i < d.length; i++) if (window.__rv(d[i])) return d[i]; return null; };
  // E29 (JS, 12.10.): only a mark the reader can click — its face on screen and
  // on top (behauptete bisher: any face; in the short template the first open
  // exercise lay below the window, y 1009 of 900, and the "click" went nowhere)
  var cs = [].filter.call(h.querySelectorAll('.nbmap-node:is(.task,.sect,.chap)[data-target]:not(.locked):not(.here):not(.nbsel)'), function(n){
    var f = face(n); if (!f || !document.getElementById(n.getAttribute('data-target'))) return false;
    var r = f.getBoundingClientRect(); if (r.top < 40 || r.bottom > innerHeight - 40) return false;
    var e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return !!(e && e.closest && e.closest('.nbmap-node') === n); });
  if (!cs.length) return null;
  cs = cs.filter(function(n){ return !/^nb(end|title)/.test(n.getAttribute('data-target')); });
  if (!cs.length) return null;
  var tk = cs.filter(function(n){ return n.classList.contains('task'); });
  var c = tk.length ? tk[0] : cs[cs.length - 1], r = face(c).getBoundingClientRect();
  return {xy: [r.left + r.width / 2, r.top + r.height / 2], target: c.getAttribute('data-target')}; }"""
def marks_after_rerun(pg, ctx):
    a = ev(pg, ANCHORS)
    if not a["n"]: return False, "BAD no marks with a target on the panel"
    if a["miss"] or a["foreign"]:
        return False, "%d of %d marks point at another run's anchors (run %s; e.g. %s), %d at another notebook" % (
            len(a["miss"]), a["n"], a["run"], a["miss"][:2], a["foreign"])
    j = ev(pg, JUMPTO)
    for _ in range(12):                 # E29: as a reader, scroll until one is in reach
        if j: break
        pg.evaluate("() => { var P = window.__rfront(), s = P && P.querySelector('.jp-WindowedPanel-outer'); if (s) s.scrollTop += 260; }")
        pg.wait_for_timeout(700); j = ev(pg, JUMPTO)
    if not j:
        dbg = ev(pg, """() => { var h = document.getElementById('nbpanel-root'), all = h.querySelectorAll('.nbmap-node[data-target]');
          return [].slice.call(all, 0, 40).map(function(n){ return (n.className.match(/\\b(task|sect|chap|grp|viz|codetask|cell|title|end)\\b/g) || ['?']).join('.')
            + (n.classList.contains('locked') ? 'L' : '') + (n.classList.contains('here') ? 'H' : '') + (window.__rv(n) ? 'v' : '-')
            + (document.getElementById(n.getAttribute('data-target')) ? 'a' : '-'); }).join(' '); }""")
        return False, "BAD no open, unlit mark with a drawn anchor to click: " + dbg
    # landing on one CPU: 0.4–0.9 s where the page does not block (E21.S2c);
    # the mark lights when its middle reaches the line — polled up to 5 s
    pg.mouse.click(j["xy"][0], j["xy"][1]); t0 = time.time(); lit = False
    while time.time() - t0 < 5 and not lit:
        pg.wait_for_timeout(250)
        lit = ev(pg, """(id) => { var h = document.getElementById('nbpanel-root'), n = h.querySelector('.nbmap-node[data-target="' + id + '"]');
          if (!n) return false; if (n.classList.contains('here')) return true;
          // in "both" the exercise and its coding mark share the line: the lit one may be the other of the pair
          var tk = n.getAttribute('data-task'), o = tk ? h.querySelector('.nbmap-node.here[data-task="' + tk + '"]') : null;
          return !!o; }""", j["target"])
    why = "" if lit else " · " + json.dumps(ev(pg, """(id) => { var h = document.getElementById('nbpanel-root'), e = document.getElementById(id);
        var here = [].map.call(h.querySelectorAll('.nbmap-node.here'), function(n){ return (n.getAttribute('data-target') || n.className).split('__')[0]; });
        var m = h.querySelector('.nbmap-here'), mr = m ? m.getBoundingClientRect() : null;
        return {here: here, anchorY: e ? Math.round(e.getBoundingClientRect().top) : null, marker: mr ? Math.round(mr.top + mr.height / 2) : null,
                hit: (function(){ var n = h.querySelector('.nbmap-node[data-target="' + id + '"]'); return n ? n.className : null; })()}; }""", j["target"]))
    return lit, "%d/%d marks on anchors of run %s; click on %s → %s%s" % (
        a["n"], a["n"], a["run"], j["target"].split("__")[0], ("lit after %.1f s" % (time.time() - t0)) if lit else "NOT lit in 5 s", why)

# ------------------------------------------------------------------ J3 YOC
YOC = r"""() => {
  var m = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]');
  var t = m && (m.querySelector('.nbsect') || m), r = t ? t.getBoundingClientRect() : null;
  var tip = document.querySelector('.nbtip'), P = window.__rfront();
  var hidden = [].reduce.call(document.querySelectorAll('.jp-NotebookPanel.lm-mod-hidden'), function(s, p){ return s + p.querySelectorAll('.jp-Cell').length; }, 0);
  return {mark: !!m, vis: window.__rv(t), xy: r ? [r.left + r.width / 2, r.top + r.height / 2] : null,
          tip: tip && tip.classList.contains('on') && window.__rv(tip) ? tip.textContent.trim() : '',
          cells: P ? P.querySelectorAll('.jp-Cell').length : -1, hidden: hidden};
}"""
def yoc(pg, ctx):
    """E21.3 / E12.4: hovering the YOC mark shows "＋ Add your cell"; one real
    click makes one own cell — in the FRONT notebook (none in another one)."""
    to_panel(pg)
    pg.evaluate("() => { var n = window.__rfront() && window.__rfront().querySelector('.jp-WindowedPanel-outer'); if (n) n.scrollTop = n.scrollHeight; }")
    pg.wait_for_timeout(1500)
    s = ev(pg, YOC)
    if not s["mark"] or not s["vis"]: return False, "BAD YOC mark %s" % ("hidden" if s["mark"] else "missing")
    pg.mouse.move(s["xy"][0] - 40, s["xy"][1] - 40); pg.wait_for_timeout(300)
    s = ev(pg, YOC); what = hit(pg, *s["xy"])
    pg.mouse.move(*s["xy"], steps=4)
    h = {"tip": ""}
    for _ in range(15):
        pg.wait_for_timeout(100); h = ev(pg, YOC)
        if h["tip"]: break
    pg.mouse.click(*s["xy"]); pg.wait_for_timeout(2200)
    c = ev(pg, YOC)
    pg.keyboard.press("Escape"); to_panel(pg)
    ok = "Add your cell" in h["tip"] and c["cells"] == s["cells"] + 1 and c["hidden"] == s["hidden"]
    return ok, "hit %s · box %r · front cells %d -> %d · other notebook %d -> %d" % (
        what, h["tip"][:24], s["cells"], c["cells"], s["hidden"], c["hidden"])

CELLS_FREE = r"""() => { var P = window.__rfront(); if (!P) return null;
  var h = document.getElementById('nbpanel-root');
  // the rail column (strip, grip, scrollbar) stands beside the text by design
  var skip = [].map.call(h ? h.querySelectorAll('.nbrail, .nbgrip, .nbsb') : [], function(e){ return e.getBoundingClientRect(); })
               .filter(function(r){ return r.width > 0 && r.height > 0; });
  var vh = window.innerHeight, bad = [], n = 0;
  [].forEach.call(P.querySelectorAll('.jp-Notebook .jp-Cell'), function(c, ci){
    var r = c.getBoundingClientRect(), t = Math.max(r.top, 60), b = Math.min(r.bottom, vh - 30);
    if (b - t < 6 || r.width < 6) return;
    for (var i = 0; i < 16; i++) for (var j = 0; j < 6; j++) {
      var x = r.left + 2 + (r.width - 4) * i / 15, y = t + 2 + (b - t - 4) * j / 5;
      if (skip.some(function(q){ return x >= q.left - 2 && x <= q.right + 2 && y >= q.top - 2 && y <= q.bottom + 2; })) continue;
      var st = document.elementsFromPoint(x, y), e = st[0];
      if (!e || !e.closest('#nbpanel-root')) { n++; continue; }
      if (e.closest('.nbdrawer') && !h.classList.contains('open')) {     // a shut window takes nothing, anywhere
        n++; bad.push('cell ' + ci + ' (' + Math.round(x) + ',' + Math.round(y) + ') shut window: ' + e.tagName + '.' + String(e.className).split(' ')[0]); continue; }
      // what the panel covers: only a loss where there is something to click or read
      var u = st.filter(function(q){ return !q.closest('#nbpanel-root'); })[0];
      if (!u) continue;
      // a cell of the reader's own = a cell without our title or our document in it
      // (E21.3c: "cells 0, 1 are ours" BEHAUPTETE BISHER the cell order — with a cell
      // the reader put above the title, the document cell counted as the reader's)
      var uc = u.closest('.jp-Cell'), own = !!(uc && !uc.querySelector('.nbtitle, .nbcover, .nbfeed, .nbrail'));
      var act = !!u.closest('button,input,textarea,select,a,label,.cm-content,.jp-InputPrompt,.widget-slider,.jupyter-widget-Collapse-header');
      var txt = [].some.call(u.childNodes, function(t){ return t.nodeType === 3 && t.textContent.trim(); });
      if (!(own || act || txt)) continue;
      n++;
      bad.push('cell ' + ci + ' (' + Math.round(x) + ',' + Math.round(y) + ') ' + e.tagName + '.' + String(e.className).split(' ')[0] + ' over ' + u.tagName + '.' + String(u.className).split(' ')[0]);
    }
  });
  return {n: n, bad: bad}; }"""
def _cells_free(pg):
    r = ev(pg, CELLS_FREE)
    if not r or not r["n"]: return None
    return r

def cells_free(pg, ctx):
    """Befund Dirigent (a) + E21.3/E21.10: nothing of the panel lies over the
    notebook's cells and takes their clicks — not the corner's buttons (v1.60:
    ⛶ over the last cell), not a closed tool window (v1.61: its borrowed
    controls stay hit-testable in the middle of the page). Every point of a
    16 × 6 grid over every cell on screen, outside the rail column, must reach
    the notebook. Measured at the top, in the middle, at the end (with an own
    cell), and after the ⚙ window was opened and shut."""
    to_panel(pg); out, bad, n = [], [], 0
    def at(where):
        nonlocal n
        pg.wait_for_timeout(1200); r = _cells_free(pg)
        if r: n += r["n"]; bad.extend("%s: %s" % (where, x) for x in r["bad"])
    for frac, where in ((0, "top"), (.5, "middle"), (1, "end")):
        pg.evaluate("(f) => { var o = window.__rfront().querySelector('.jp-WindowedPanel-outer'); o.scrollTop = f * (o.scrollHeight - o.clientHeight); }", frac)
        at(where)
    g = pg.evaluate("() => { var b = document.querySelector('.nbcorner .nbbtn.nbgear'), r = b && b.getBoundingClientRect(); return r ? [r.left + r.width / 2, r.top + r.height / 2] : null; }")
    if g:
        pg.mouse.click(*g); pg.wait_for_timeout(900); pg.keyboard.press("Escape"); pg.wait_for_timeout(600); to_panel(pg)
        pg.evaluate("() => { var o = window.__rfront().querySelector('.jp-WindowedPanel-outer'); o.scrollTop = 0.5 * (o.scrollHeight - o.clientHeight); }")
        at("middle after ⚙")
    if not n: return False, "BAD no cell on screen"
    return not bad, "%d points, %d taken by the panel%s" % (n, len(bad), (": " + "; ".join(sorted(set(b.split(" (")[0] + " " + b.split(") ")[-1] for b in bad))[:4])) if bad else "")

# ------------------------------------------------------------------ J4 profile window
PROF = r"""() => { var b = document.querySelector('.nbcorner .nbbtn.nbprofile');
  var h = document.getElementById('nbpanel-root'), d = h && h.querySelector('.nbdrawer');
  var cells = d ? [].filter.call(d.querySelectorAll('.nbcell'), window.__rv) : [];
  var txt = cells.map(function(c){ return (c.innerText || '').trim(); }).join(' ');
  var r = b && b.getBoundingClientRect();
  return {btn: window.__rv(b), xy: r ? [r.left + r.width / 2, r.top + r.height / 2] : null,
          open: !!(h && h.classList.contains('open')), page: h && h.dataset.page, drawer: window.__rv(d),
          cells: cells.length, len: txt.length, txt: txt.slice(0, 80),
          btns: d ? [].filter.call(d.querySelectorAll('.nbcell button'), window.__rv).length : 0}; }"""
def profile_window(pg, ctx):
    """E21.4: the 👤 window opens by ONE real click 10/10, shows content (cells with
    text and at least one working button), and Esc shuts it."""
    to_panel(pg)
    s = ev(pg, PROF)
    if not s["btn"]: return False, "BAD no visible 👤 button"
    good, last, what = 0, None, hit(pg, *s["xy"])
    for i in range(10):
        s = ev(pg, PROF); pg.mouse.click(*s["xy"])
        ok = False
        for _ in range(25):
            pg.wait_for_timeout(100); last = ev(pg, PROF)
            if last["open"] and last["drawer"] and last["cells"] > 0 and last["len"] > 40 and last["btns"] > 0: ok = True; break
        good += ok
        pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
        if ev(pg, PROF)["open"]:
            pg.mouse.click(700, 450); pg.wait_for_timeout(400)
    shut = not ev(pg, PROF)["open"]
    to_panel(pg)
    return good == 10 and shut, "%d/10 (click hits %s) · page %s · %d cells · %d buttons · %r · shut after Esc %s" % (
        good, what, last and last["page"], last and last["cells"], last and last["btns"], last and last["txt"][:40], shut)

# ------------------------------------------------------------------ J5 panel still
STILL = r"""async () => {
  var h = document.getElementById('nbpanel-root'); if (!h) return {bad: 'no panel'};
  var pick = function(){ var o = [], r = h.getBoundingClientRect(); o.push(r.left, r.top, r.width, r.height);
    h.querySelectorAll('.nbmap-node, .nbmap-here, .nbmap-inner, .nbdock').forEach(function(n){ var q = n.getBoundingClientRect(); o.push(q.left, q.top, q.width, q.height); });
    return o; };
  // a sync pass rewrites the marks' classes: count the 100-ms slots in which that happened
  var slots = {}, t0 = performance.now(), lt = 0;
  // a full sync pass re-writes the host's own classes (nbsb-out, ready …): count the 100-ms slots with one
  var light = {};
  var mo = new MutationObserver(function(ms){ ms.forEach(function(m){ var k = Math.floor((performance.now() - t0) / 100);
    if (m.target === h) slots[k] = 1; else if (m.target.classList && m.target.classList.contains('nbmap-node')) light[k] = 1; }); });
  mo.observe(h, {attributes: true, attributeFilter: ['class'], subtree: true});
  var lts = [];
  var po = null; try { po = new PerformanceObserver(function(l){ l.getEntries().forEach(function(e){ lt++; lts.push([e.startTime, e.duration]); }); }); po.observe({entryTypes: ['longtask']}); } catch (e) {}
  // E21 Rest (2026-10-03): WHOSE long task. The long-task count above is every
  // task of the page, JupyterLab's own included (file browser poll, autosave,
  // the kernel of a notebook behind). Chromium's long-animation-frame entries
  // name the scripts of a long frame: the Lab's come from its bundles
  // (sourceURL …/static/…, …/extensions/…), the test's own from Playwright,
  // ours have no file (the toolkit runs as inline script of the output).
  var lf = {ours: 0, lab: 0, test: 0, other: 0, list: [], ok: false, notours: []};
  var who = function(u){ u = u || ''; return /playwright|__puppeteer/.test(u) ? 'test' : (u === '' || u === location.href) ? 'ours' : 'lab'; };
  var take = function(es){ es.forEach(function(e){
      if (e.duration <= 50) return;
      var t = {ours: 0, lab: 0, test: 0};
      (e.scripts || []).forEach(function(x){ t[who(x.sourceURL)] += x.duration; });
      // a frame belongs to whoever ran longest in it; one without a named
      // script (layout/paint only) is "other" (counted as ours) when we had
      // changed our DOM just before it, else "unowned" (reported only)
      var k = t.test > t.ours && t.test > t.lab ? 'test' : t.ours > 0 && t.ours >= t.lab ? 'ours' : t.lab > 0 ? 'lab'
            : mine(e) ? 'other' : 'unowned';
      if (k === 'lab' || k === 'test' || k === 'unowned') lf.notours.push([e.startTime, e.startTime + e.duration]);
      if (k === 'unowned') { lf.unowned = (lf.unowned || 0) + 1; lf.list.push('unowned ' + Math.round(e.duration) + ' ms'); return; }
      lf[k]++;
      lf.list.push(k + ' ' + Math.round(e.duration) + ' ms' + (e.scripts || []).filter(function(x){ return x.duration >= 5; }).map(function(x){
        return ' [' + who(x.sourceURL) + ':' + (x.sourceFunctionName || x.invoker || '?') + ' ' + Math.round(x.duration) + ']'; }).join(''));
    }); };
  // a frame with no named script (style, layout, paint only) was set going by
  // a DOM change in an earlier task: it is ours if WE changed something just
  // before it (our host, our outputs, an element of ours), else not counted
  var ourMut = [], mw = new MutationObserver(function(ms){ var now = performance.now();
    for (var i = 0; i < ms.length; i++) { var t = ms[i].target, e = t.nodeType === 1 ? t : t.parentElement;
      if (e && (e.closest('#nbpanel-root, .jp-OutputArea, .nbtip, #nbload') || /(^|\s)nb/.test(String(e.className || ''))))
        { ourMut.push(now); return; } } });
  mw.observe(document.body, {subtree: true, childList: true, attributes: true, characterData: true});
  var mine = function(e){ return ourMut.some(function(t){ return t >= e.startTime - 150 && t <= e.startTime + e.duration; }); };
  var pl = null; try { pl = new PerformanceObserver(function(l){ take(l.getEntries()); });
    pl.observe({type: 'long-animation-frame', buffered: false}); lf.ok = true; } catch (e) { pl = null; }
  var a = pick(), max = 0, at = -1, flips = 0, prev = a, frames = 0, go = true;
  var raf = function(){ frames++; var b = pick();
    for (var j = 0; j < a.length && j < b.length; j++) { var d = Math.abs(a[j] - b[j]); if (d > max) { max = d; at = j; } }
    if (Math.abs(b[2] - prev[2]) > 0.5) flips++; prev = b; if (go) requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
  await new Promise(function(res){ setTimeout(res, 3000); }); go = false; mo.disconnect(); if (po) po.disconnect();
  if (pl) { try { take(pl.takeRecords()); } catch (e) {} pl.disconnect(); }
  mw.disconnect();
  // a long task counts as ours unless a long frame that is plainly NOT ours
  // (the Lab's script, the test's, or layout/paint with no change of ours
  // before it) holds it; a long task no frame explains counts as ours
  lf.ltOurs = lts.filter(function(x){ return !lf.notours.some(function(w){
    return Math.min(x[0] + x[1], w[1]) - Math.max(x[0], w[0]) >= x[1] / 2; }); }).length;
  lf.dbg = JSON.stringify({lt: lts.map(function(x){ return [Math.round(x[0] - t0), Math.round(x[1])]; }),
                           not: lf.notours.map(function(w){ return [Math.round(w[0] - t0), Math.round(w[1] - t0)]; })});
  delete lf.notours;
  return {max: Math.round(max * 10) / 10, at: at, n: a.length / 4, widthChanges: flips, passes: Object.keys(slots).length,
          light: Object.keys(light).length, frames: frames, longtasks: lt, loaf: lf};
}"""
def _still_ok(r):
    # every frame for 3 s: no box moves, the width never changes, and the page
    # is not kept busy by the panel: at most 3 long frames (> 50 ms) OF OURS in
    # 3 s — the 1.5-s heartbeat and one trailing sync. v1.61 at rest: 8–13 heavy
    # self-triggered syncs, 11 long tasks, ≈ 45 frames in 3 s (the panel
    # answered its own writes).
    # E21 Rest (2026-10-03) — BEHAUPTETE BISHER „the panel keeps the page busy“
    # and counted EVERY long task of the page: JupyterLab's own (autosave, file
    # browser poll, the kernel and toolbar of the notebook behind) as ours. Gate
    # 03.10. 12:2x, Complex minimal light pair: 0.0 px, 1 sync — and 4 long
    # tasks → red. Now the long frames are told apart by their scripts
    # (long-animation-frame, Chromium): a long task inside a frame that is
    # plainly not ours (the Lab's script, the test's, or layout with no change
    # of ours before it) is reported, not counted; every other long task —
    # also one no frame explains (v1.61 at rest: 6–10 long tasks of ~400 ms,
    # Chromium reported no frame for them) — counts as ours, as before.
    # Without that API the old rule holds.
    lf = r.get("loaf") or {}
    ours = lf["ltOurs"] if lf.get("ok") else r["longtasks"]
    return r["max"] <= 0.5 and r["widthChanges"] == 0 and ours <= 3
def _still_say(r):
    lf = r.get("loaf") or {}
    who = (" · of them ours %d (≤ 3) · long frames: ours %d, layout after our change %d, Lab %d, layout without %d, test %d: %s" % (
               lf["ltOurs"], lf["ours"], lf["other"], lf["lab"], lf.get("unowned", 0), lf["test"], "; ".join(lf["list"])[:300])
           if lf.get("ok") else " · (no long-animation-frame API: all long tasks count)")
    return "max change %.1f px (value #%d) · width changes %d · full sync passes %d (light %d) · %d frames · %d long tasks%s · %d boxes" % (
        r["max"], r["at"], r["widthChanges"], r["passes"], r["light"], r["frames"], r["longtasks"], who, r["n"])
def panel_still(pg, ctx):
    """E21.5 / Video 1: without input, over 3 s measured in every frame, nothing in
    the panel moves (marks, marker, strip, dock, the panel's box: 0 px) and the
    panel does not keep re-syncing itself (v1.61: it answered its own writes).
    E21 Rest (2026-10-03) — AT REST MEANS 5 S WITHOUT INPUT. BEHAUPTETE BISHER
    „at rest“ 2.5 s after the test before it (C8 ends with a scroll): that is
    the after-event phase, in which the panel by design looks twice more (the
    beat's 3.2-s window, E21.5b) and sets the 🔖 2–3 s after the scroll rests —
    gate row Complex cyber dark old: bmTick 256 ms + beat 107 ms + 1 = 3 of 3.
    That phase is J5 after scroll's; this one waits 5 s first."""
    to_panel(pg); pg.wait_for_timeout(5000)
    r = pg.evaluate(STILL)
    if "bad" in r: return False, "BAD " + r["bad"]
    return _still_ok(r), _still_say(r)

def panel_still_after_scroll(pg, ctx):
    """E21.5: the same, once a wheel scroll has come to rest (the document's
    scrollTop unchanged for 0.5 s): the panel settles and then stays."""
    to_panel(pg); ev(pg, "() => 0")
    for _ in range(6): pg.mouse.wheel(0, 240); pg.wait_for_timeout(60)
    last, same, t0 = None, 0, time.time()
    while time.time() - t0 < 30 and same < 5:
        pg.wait_for_timeout(100)
        st = pg.evaluate("() => { var o = window.__rfront && window.__rfront(); o = o && o.querySelector('.jp-WindowedPanel-outer'); return o ? o.scrollTop : null; }")
        same = same + 1 if st == last else 0; last = st
    settle = time.time() - t0
    pg.wait_for_timeout(1500)            # the trailing sync of the last real scroll may still come
    r = pg.evaluate(STILL)
    for _ in range(6): pg.mouse.wheel(0, -240); pg.wait_for_timeout(60)
    if "bad" in r: return False, "BAD " + r["bad"]
    return _still_ok(r), "settled after %.1f s · %s" % (settle, _still_say(r))

# ------------------------------------------------------------------ J7 version
VER = r"""() => { var re = /v\d+\.\d+\s*·\s*build|build \d{4}-\d\d-\d\d[a-z]+/;
  var out = [];
  document.querySelectorAll('#nbpanel-root *, .jp-NotebookPanel:not(.lm-mod-hidden) .jp-OutputArea *').forEach(function(e){
    if (e.children.length === 0 && re.test(e.textContent || '') && window.__rv(e)) out.push('text:' + (e.closest('.nbcell') ? [].filter.call(e.closest('.nbcell').classList, function(c){ return /^pg-|nbctl/.test(c); }).join('.') : e.className));
    var t = e.getAttribute && e.getAttribute('title'); if (t && re.test(t)) out.push('title:' + (e.className || e.tagName));
  });
  return out; }"""
def version_once(pg, ctx):
    """E21.7: the line "v1.6x · build …" is nowhere visible and in no tooltip
    outside the ⚙ window; with ⚙ open it stands there once."""
    to_panel(pg)
    shut = ev(pg, VER)
    g = pg.evaluate("() => { var b = document.querySelector('.nbcorner .nbbtn.nbgear'), r = b && b.getBoundingClientRect(); return r ? [r.left + r.width / 2, r.top + r.height / 2] : null; }")
    inside = []
    if g:
        # E21.7c (2026-10-03): wait for the window, up to 2.5 s as B4/J4 do, then read
        # once more 0.3 s later (a second line would show by then). BEHAUPTETE BISHER
        # that ⚙ is open 0.9 s after the click — on one CPU it was not, in 1 of 48
        # gate rows (Modeling minimal light fresh: "in ⚙: 0"; green in 2 reruns).
        pg.mouse.click(*g)
        for _ in range(25):
            pg.wait_for_timeout(100)
            if [x for x in ev(pg, VER) if x.startswith("text:")]: break
        pg.wait_for_timeout(300)
        inside = [x for x in ev(pg, VER) if x.startswith("text:")]
        pg.keyboard.press("Escape"); pg.wait_for_timeout(400)
    to_panel(pg)
    titles = [x for x in shut if x.startswith("title:")]
    texts = [x for x in shut if x.startswith("text:")]
    return not titles and not texts and len(inside) == 1, "closed: %d visible, %d tooltips %s · in ⚙: %d" % (
        len(texts), len(titles), (titles + texts)[:3], len(inside))

# ------------------------------------------------------------------ J8 trail contract
TRAIL = r"""() => { var m = document.querySelector('#nbpanel-root .nbmap-here'); if (!m) return null;
  return {top: m.style.top, y: m.style.getPropertyValue('--nbm-y'), cy: getComputedStyle(m).getPropertyValue('--nbm-y').trim()}; }"""
def trail_contract(pg, ctx):
    """E21.8 (contract with css-E21.8): the marker carries `--nbm-y` = its `top`,
    at rest and after every move, so CSS can draw the fading trail behind it."""
    to_panel(pg)
    a = pg.evaluate(TRAIL)
    if not a: return False, "BAD no marker"
    seen = []
    for k in range(4):
        pg.mouse.wheel(0, 300); pg.wait_for_timeout(90)
        seen.append(pg.evaluate(TRAIL))
    pg.wait_for_timeout(900); b = pg.evaluate(TRAIL)
    for k in range(4): pg.mouse.wheel(0, -300); pg.wait_for_timeout(60)
    pg.wait_for_timeout(600)
    good = lambda s: s and s["top"] and s["y"] == s["top"]
    ok = good(a) and good(b) and all(good(s) for s in seen)
    return ok, "rest %s/%s · moving %s · after %s/%s" % (a["top"], a["y"] or "-", ["%s/%s" % (s["top"], s["y"] or "-") for s in seen][:2], b["top"], b["y"] or "-")

# ------------------------------------------------------------------ J10 locked chapter heading
LOCKED = r"""() => { var P = window.__rfront(); if (!P) return null;
  var notes = [].slice.call(P.querySelectorAll('.nblocked-note:not(.nbexlock)'));
  var out = notes.map(function(n){ var c = n.closest('.jupyter-widget-Collapse');
    var hd = c && c.querySelector(':scope > .jupyter-widget-Collapse-header');
    var r = hd ? hd.getBoundingClientRect() : null;
    return {vis: window.__rv(n), open: !!(c && c.classList.contains('jupyter-widget-Collapse-open')),
            hd: r && r.height > 0 ? [r.left + Math.min(60, r.width / 3), r.top + r.height / 2] : null,
            hdTop: r ? r.top : null, txt: (n.innerText || '').trim().slice(0, 30)}; });
  return out; }"""
def locked_heading(pg, ctx):
    """E21.10: one click on the heading of a locked chapter in the document opens
    its lock box (padlock, "This chapter is locked …"), the next click shuts it."""
    if ctx.get("mode") == "plain": return True, "plain: nothing is locked"
    to_panel(pg)
    L = ev(pg, LOCKED)
    if not L: return False, "BAD no locked chapter in the front notebook"
    pg.evaluate(r"""() => { var P = window.__rfront(), n = P.querySelector('.nblocked-note:not(.nbexlock)');
      var c = n.closest('.jupyter-widget-Collapse'), hd = c.querySelector(':scope > .jupyter-widget-Collapse-header');
      var o = c; while ((o = o.parentElement && o.parentElement.closest('.jupyter-widget-Collapse'))) {
        if (!o.classList.contains('jupyter-widget-Collapse-open')) { var h = o.querySelector(':scope > .jupyter-widget-Collapse-header'); if (h) h.click(); } }
      setTimeout(function(){ hd.scrollIntoView({block: 'center'}); }, 500); }""")
    pg.wait_for_timeout(1500)
    s0 = ev(pg, LOCKED)[0]
    if not s0["hd"]: return False, "BAD heading of %r not on screen" % s0["txt"]
    what = hit(pg, *s0["hd"])
    seq = [s0["vis"]]
    for k in range(2):
        cur = ev(pg, LOCKED)[0]
        pg.mouse.click(*cur["hd"]); pg.wait_for_timeout(1300)
        seq.append(ev(pg, LOCKED)[0]["vis"])
    to_panel(pg)
    ok = seq[1] != seq[0] and seq[2] == seq[0] and (seq[1] or seq[2])
    return ok, "click hits %s · box visible %s -> %s -> %s" % (what, seq[0], seq[1], seq[2])

# ------------------------------------------------------------------ J1L title opens late
# 2026-10-07 (E24 Stufe 2 Rest 2, JS) — THE TIMELINE FOLLOWS A BOX THAT COMES
# LATE. Tor 07.10., minimal light pair: J1 "title card folds front" red, marks
# below the title 17 → 0 → 0 while the title body was back at 4085 px 1.4 s
# after the click (flickering: green in the other rows). The rail looked at the
# opened accordion 0.06, 0.45 and 1 s after the click; in a loaded page (two
# notebooks, their kernels) the box came after that, and the marks waited for a
# beat. Here the late box is made on purpose: the title is shut (card click),
# its contents are held at display:none by a stylesheet in <head> (no node of
# the body changes) while the card is clicked again, released 1.3 s later. The
# first full pass of the panel must START ≤ 300 ms after the release (read in
# the page: every write of window.__nbrailFullAt, which the pass sets as it
# begins), and the marks must be back after it (≤ 3 s). The start, not the end:
# the pass that brings them is itself one long task (0.3–0.6 s on a revealed
# book of 2000 px, more on 4000 px — measured), the bound is the box, not the
# size of the book; before, the first pass came with the next beat (up to
# 1.5 s). While held the marks must be 0 (else the hold did not work: BAD).
# Gegenprobe: chronicle 07.10., Werkstatt JS (Rest 2).
TRAP = """(on) => { if (on) { var v = window.__nbrailFullAt; window.__j1l = {t0: Date.now(), at: []};
    Object.defineProperty(window, '__nbrailFullAt', {configurable: true, get: function(){ return v; },
      set: function(x){ v = x; if (window.__j1l && window.__j1l.at.length < 20) window.__j1l.at.push(Date.now() - window.__j1l.t0); }});
    return null; }
  var cur = window.__nbrailFullAt, r = window.__j1l; delete window.__nbrailFullAt; window.__nbrailFullAt = cur; window.__j1l = null; return r; }"""
HOLD = """(on) => { var s = document.getElementById('j1late');
  if (on && !s) { s = document.createElement('style'); s.id = 'j1late';
    s.textContent = '.jp-NotebookPanel:not(.lm-mod-hidden) .acc-title.acc-root .jupyter-widget-Collapse-contents{display:none!important}';
    document.head.appendChild(s); }
  if (!on && s) s.remove(); }"""
def title_late(pg, ctx):
    to_panel(pg)
    pg.evaluate("() => { var c = document.querySelector('%s .jp-OutputArea .nbtitle-card'); if (c) c.scrollIntoView({block: 'center'}); }" % FRONT)
    pg.wait_for_timeout(900)
    s0 = ev(pg, TITLE_JS)
    if s0["other"] == 0 or (s0["body"] or 0) <= 1:
        if s0["card"]: pg.mouse.click(*s0["card"]); pg.wait_for_timeout(1400)
        s0 = ev(pg, TITLE_JS)
    if s0["other"] == 0 or not s0["card"]: return False, "BAD title not open / no card (%s)" % s0
    try:
        pg.mouse.click(*s0["card"]); pg.wait_for_timeout(1400)
        s1 = ev(pg, TITLE_JS)
        if s1["other"] != 0: return False, "BAD the title did not shut (marks %d)" % s1["other"]
        pg.evaluate(HOLD, True)
        pg.mouse.click(*(s1["card"] or s0["card"])); pg.wait_for_timeout(1300)
        s2 = ev(pg, TITLE_JS)
        if s2["other"] != 0 or (s2["body"] or 0) > 1:
            return False, "BAD the hold did not hold (marks %d, body %s)" % (s2["other"], s2["body"])
        pg.evaluate(TRAP, True); pg.evaluate(HOLD, False)
        t0 = time.time(); back = None; s3 = None
        while time.time() - t0 < 3.0:
            s3 = ev(pg, TITLE_JS)
            if s3["other"] == s0["other"]: back = int((time.time() - t0) * 1000); break
            pg.wait_for_timeout(50)
        tr = pg.evaluate(TRAP, False) or {"at": []}
    finally:
        pg.evaluate(HOLD, False)
        try: pg.evaluate("() => { if (window.__j1l) { var c = window.__nbrailFullAt; delete window.__nbrailFullAt; window.__nbrailFullAt = c; window.__j1l = null; } }")
        except Exception: pass
    to_panel(pg)
    first = tr["at"][0] if tr["at"] else None
    ok = back is not None and first is not None and first <= 300
    return ok, "marks below %d -> %d -> held %d (body %s) -> released: first pass %s, marks back %s · body %s px" % (
        s0["other"], s1["other"], s2["other"], s2["body"],
        ("+%d ms (want ≤ 300)" % first) if first is not None else "NONE in 3 s",
        ("after %d ms" % back) if back is not None else "NOT within 3 s (%d)" % s3["other"], s3["body"])

TESTS = [("J5 panel still 3 s", panel_still),
         ("J5 panel still after scroll", panel_still_after_scroll),
         ("J4 profile window 10/10", profile_window),
         ("J7 version only in gear (Py: py-E21.7)", version_once),
         ("J8 marker carries --nbm-y", trail_contract),
         ("J3 nothing over the cells", cells_free),
         ("J1 title mark folds front", title_mark),
         ("J1 title card folds front", title_card),
         ("J1L title opens late: marks follow the box", title_late),
         ("J2 code colours live", code_colours),
         ("J2 code colours after rerun", code_colours_rerun),
         ("J11 marks on this run's anchors (after rerun)", marks_after_rerun),
         ("J10 locked heading toggles box", locked_heading),
         ("J3 YOC hover + cell in front", yoc),
         ("J3 nothing over the cells (own cell)", cells_free)]

# ------------------------------------------------------------------ J6 mode (own runner)
MODE_ST = r"""(ids) => { var P = window.__rfront(), out = {};
  var o = P && P.querySelector('.nbcover .nbmode .nbmode-opt[data-mode="calc"]'), r = o && o.getBoundingClientRect();
  out.card = r && r.width > 0 ? [r.left + r.width / 2, r.top + r.height / 2] : null;
  out.checked = [].map.call(P ? P.querySelectorAll('.nbcover .nbmode .nbmode-opt[aria-checked="true"]') : [], function(x){ return x.getAttribute('data-mode'); });
  out.order = [].map.call(P ? P.querySelectorAll('.nbcover .nbmode .nbmode-opt') : [], function(x){ return x.getAttribute('data-mode'); });
  ids.forEach(function(i){ out['k_' + i] = localStorage.getItem('digichemjn.mode.' + i); });
  out.pending = localStorage.getItem('digichemjn.mode.__pending');
  var f = P && P.querySelectorAll('.nbfeed[data-progress]'); out.built = f && f.length ? (f[f.length - 1].getAttribute('data-nbmode') || 'both') : null;
  return out; }"""
def mode_pair(b, base, root, nb, other, skin, theme):
    """E21.6: with another notebook open and run in the same window, the cover of
    this one (reopened cold, before Play) takes ONE click: the card shows the
    choice at once and it is stored under `digichemjn.mode.<this id>`; Play
    builds exactly that mode; the other notebook's key and built mode stay.
    Returns (ok, detail)."""
    ida, idb = nb_id(nb), nb_id(other)
    ctx, pg, errs, names = session(b, base, root, nb, other, "pair", skin, theme, run=False)
    try:
        ev(pg, "() => 0")
        s0 = None
        for _ in range(40):
            pg.wait_for_timeout(500); s0 = ev(pg, MODE_ST, [ida, idb])
            if s0["card"]: break
        if not s0 or not s0["card"]: return False, "BAD no mode cards on the cold cover"
        pg.evaluate("() => { var P = window.__rfront(); var c = P.querySelector('.nbcover .nbmode'); if (c) c.scrollIntoView({block: 'center'}); }")
        pg.wait_for_timeout(600); s0 = ev(pg, MODE_ST, [ida, idb])
        b_built = None
        what = hit(pg, *s0["card"])
        pg.mouse.click(*s0["card"]); pg.wait_for_timeout(500)
        s1 = ev(pg, MODE_ST, [ida, idb])
        one = s1["checked"] == ["calc"] and s1["k_" + ida] == "calc" and s1["k_" + idb] == s0["k_" + idb]
        # Play, as the reader does
        pg.evaluate("() => { var P = window.__rfront(); var p = P.querySelector('.nbcover .nbcover-play'); if (p) p.scrollIntoView({block: 'center'}); }")
        pg.wait_for_timeout(500)
        pr = pg.evaluate("() => { var p = window.__rfront().querySelector('.nbcover .nbcover-play'), r = p && p.getBoundingClientRect(); return r ? [r.left + r.width / 2, r.top + r.height / 2] : null; }")
        t0 = time.time(); runs = 0
        if pr: pg.mouse.click(*pr)
        try: pg.wait_for_function(READY, arg=ida, timeout=90000)
        except Exception: return False, "BAD Play did not run this notebook (%s)" % s1
        last, stable = None, 0
        for _ in range(60):
            pg.wait_for_timeout(1000)
            cur = ev(pg, MODE_ST, [ida, idb])["built"]
            busy = pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')")
            if cur != last: runs += 1; last = cur
            stable = stable + 1 if not busy else 0
            if stable >= 8: break
        s2 = ev(pg, MODE_ST, [ida, idb])
        # the other notebook, in front again
        pg.click(".lm-DockPanel .lm-TabBar-tab:not(.lm-mod-current)"); pg.wait_for_timeout(2500)
        s3 = ev(pg, MODE_ST, [ida, idb])
        ok = (one and s2["built"] == "calc" and s3["built"] == "both" and s3["k_" + idb] == s0["k_" + idb]
              and s0["order"][:1] == ["plain"])                   # E21.11: plain first
        return ok, ("1 click (hits %s): checked %s · key %s=%s, %s=%s → %s=%s, %s=%s · pending %r · Play: %s built %s (%.0f s) · "
                    "other notebook built %s, key %s · cards %s") % (
            what, s1["checked"], ida, s0["k_" + ida], idb, s0["k_" + idb], ida, s1["k_" + ida], idb, s1["k_" + idb], s1["pending"],
            ida, s2["built"], time.time() - t0, s3["built"], s3["k_" + idb], s0["order"])
    finally:
        ctx.close()

# ====================================================================== on its own
OLD = {"digichemjn.zoom.v1": "130", "digichemjn.guizoom.v1": "70", "digichemjn.readline.v1": "60",
       "digichemjn.orient.v1": "v", "digichemjn.role.v1": "student", "digichemjn.mode.{id}": "both",
       "digichemjn.bookmark.{id}": "ch2",
       "digichemjn.owncells.v1": {"{id}": {"v": "1.54", "t": 1790900000000, "cells": ["x = 1 + 1j\nabs(x)"]}},
       "digichemjn.cover.v1": {"{id}": {"t": 1790900000000, "title": "old build", "k": {"t1": {"calc": "solved", "code": "open"}}}}}

def nb_id(path):
    src = open(path, encoding="utf-8").read()
    for i in ("complex-numbers", "intro-modeling"):
        if '\\"%s\\"' % i in src or '"%s"' % i in src: return i
    return "unnamed"

def old_items(nid):
    fx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "storage_old.json")
    items = json.load(open(fx, encoding="utf-8"))["items"] if os.path.exists(fx) else OLD
    return {k.replace("{id}", nid): (v if isinstance(v, str) else json.dumps(v)).replace("{id}", nid) for k, v in items.items()}

def palette(pg, label):
    if pg.query_selector(".jp-Dialog"): pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
    pg.keyboard.type(label)
    pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === l); }", arg=label, timeout=8000)
    pg.keyboard.press("Enter")

READY = """(id) => { var k = ''; try { k = window.__nbZKey ? window.__nbZKey() : ''; } catch (e) {}
  return !!(document.querySelector('#nbpanel-root .nbmap') && k.slice(-(id.length + 1)) === '.' + id); }"""
def run_front(pg, nid):
    for attempt in range(3):
        palette(pg, "Run All Cells")
        try: pg.wait_for_function(READY, arg=nid, timeout=60000); break
        except Exception:
            if attempt == 2: raise
    for _ in range(90):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('%s .jp-Notebook-ExecutionIndicator, .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')" % FRONT)
        if st == "idle": break
    pg.wait_for_timeout(2500)
    for _ in range(60):
        if not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"): break
        pg.wait_for_timeout(1000)
    from lab_keys import cover_play
    cover_play(pg)                      # E24.3: after the run the cover, Play → the document

_N = itertools.count()
def copy_in(root, src):
    name = "js_%03d_%d_%s" % (next(_N), os.getpid() % 1000, os.path.basename(src))
    shutil.copy(src, os.path.join(root, name)); return name

def open_path(pg, name):
    palette(pg, "Open from Path…")
    pg.wait_for_selector(".jp-Dialog input", timeout=10000)
    pg.fill(".jp-Dialog input", name); pg.keyboard.press("Enter")
    pg.wait_for_function("(n) => { var t = document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current'); return !!(t && t.textContent.indexOf(n) >= 0); }", arg=name, timeout=30000)
    pg.wait_for_timeout(2500)

def set_lab_theme(base, theme):
    url = base + "/lab/api/settings/@jupyterlab/apputils-extension:themes"
    body = json.dumps({"raw": json.dumps({"theme": {"light": "JupyterLab Light", "dark": "JupyterLab Dark"}[theme]})}).encode()
    urllib.request.urlopen(urllib.request.Request(url, data=body, method="PUT", headers={"Content-Type": "application/json"}), timeout=10).read()

INIT = """(function(items){ try { if (sessionStorage.getItem('__nbjsInit')) return;
  Object.keys(items).forEach(function(k){ localStorage.setItem(k, items[k]); }); sessionStorage.setItem('__nbjsInit', '1'); } catch (e) {} })(%s);"""

def session(b, base, root, nb, other, storage, skin, theme, W=1400, H=900, run=True):
    """A browser context on a fresh copy of nb (and in pair: other first). Returns (ctx, pg, errs, names)."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lab_keys import kill_sessions
    kill_sessions(base)
    shutil.rmtree(os.path.join(os.environ.get("DIGICHEM_KERNEL_HOME", os.path.expanduser("~")), ".digichemjn"), ignore_errors=True)
    set_lab_theme(base, theme)
    nid = nb_id(nb)
    items = old_items(nid) if storage == "old" else {}
    items["digichemjn.skin.v1"] = skin; items["digichemjn.theme.v1"] = theme
    for _id in {nid, nb_id(other) if other else nid}:     # E25.o: the notebook's own keys
        items["digichemjn.skin.v1." + _id] = skin; items["digichemjn.theme.v1." + _id] = theme
    ctx = b.new_context(viewport={"width": W, "height": H}); ctx.add_init_script(INIT % json.dumps(items))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    names = []
    first = other if storage == "pair" else nb
    names.append(copy_in(root, first))
    pg.goto(base + "/lab/tree/" + names[0] + "?reset")
    pg.wait_for_selector(FRONT + " .jp-Cell", state="attached", timeout=120000); pg.wait_for_timeout(1500)
    if storage == "pair":
        run_front(pg, nb_id(other))
        names.append(copy_in(root, nb)); open_path(pg, names[1])
    if run: run_front(pg, nid)
    return ctx, pg, errs, names

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nb"); ap.add_argument("other", nargs="?")
    ap.add_argument("--storage", default="fresh,old,pair"); ap.add_argument("--skins", default="minimal")
    ap.add_argument("--themes", default="light"); ap.add_argument("--only", default=None)
    ap.add_argument("--json", default=None)
    A = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lab_keys import ensure_lab, CHROME
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    rows, red = [], 0
    sel = [(n, f) for n, f in TESTS if not A.only or any(o in n for o in A.only.split(","))]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        if "pair" in A.storage and A.other and (not A.only or "J6" in A.only):
            for skin, theme in itertools.product(A.skins.split(","), A.themes.split(",")):
                tag = "%s · %s %s · pair, cold cover" % (os.path.basename(A.nb)[:24], skin, theme)
                try: ok, det = mode_pair(b, base, root, A.nb, A.other, skin, theme)
                except Exception as e: ok, det = False, "BAD exception %s" % str(e)[:160]
                rows.append((tag, "J6 mode: one click, this notebook", ok, det)); red += 0 if ok else 1
                print(tag); print("   %-32s %s  %s" % ("J6 mode one click", "ok " if ok else "RED", det[:400])); sys.stdout.flush()
        for sto, skin, theme in itertools.product(A.storage.split(","), A.skins.split(","), A.themes.split(",")):
            tag = "%s · %s %s · %s" % (os.path.basename(A.nb)[:24], skin, theme, sto)
            if sto == "pair" and not A.other:
                rows.append((tag, "*", False, "NOT RUN: pair needs <other>")); red += 1; continue
            try:
                ctx, pg, errs, _ = session(b, base, root, A.nb, A.other, sto, skin, theme)
            except Exception as e:
                rows.append((tag, "open+run", False, "BAD %s" % str(e)[:160])); red += 1; print(tag, "BAD", e); continue
            print(tag); sys.stdout.flush()
            c = dict(nb=os.path.basename(A.nb), id=nb_id(A.nb), env="lab", skin=skin, theme=theme, storage=sto, errs=errs)
            for name, fn in sel:
                try: ok, det = fn(pg, c)
                except Exception as e: ok, det = False, "BAD exception %s" % str(e)[:160]
                rows.append((tag, name, bool(ok), det)); red += 0 if ok else 1
                print("   %-32s %s  %s" % (name, "ok " if ok else "RED", det[:170])); sys.stdout.flush()
            rows.append((tag, "pageerrors", not errs, "%d %s" % (len(errs), errs[:1]))); red += 1 if errs else 0
            print("   %-32s %s  %d" % ("pageerrors", "ok " if not errs else "RED", len(errs)))
            ctx.close()
        b.close()
    print("\n%d rows, %d red\n%s" % (len(rows), red, "JS_E21 OK" if not red else "JS_E21 RED"))
    if A.json: json.dump([dict(combo=r[0], test=r[1], ok=r[2], detail=r[3]) for r in rows], open(A.json, "w"), ensure_ascii=False, indent=1)
    sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
