"""E22 — the JS workshop's regress tests for E22 (2026-10-05; Kategorie
Applikation, Prüfwerkzeug). Module of tests/regress/run.py (TESTS = [(name, fn)],
fn(pg, ctx) -> (ok, detail)). Real JupyterLab, real mouse, measured in the
browser (getBoundingClientRect, getComputedStyle, PerformanceObserver).

THE FRAME PROBE. A frame is measured AFTER every frame callback of that frame
(ours included) and after JupyterLab's own ResizeObservers: a ResizeObserver
on a 1-px probe whose width is flipped in requestAnimationFrame fires
post-layout, pre-paint. A probe that measures INSIDE its own rAF runs before
callbacks registered later in the same frame and reports a lag the reader
never sees (first sketch of this module did exactly that).

  J22.9  marks steady while zooming and dragging (E22.9)
  J22.6  rail and marker in the same frame as the page: wheel, thumb (E22.6)
  J22.4  a chapter click lands on the reading line where the reader put it
  J22.7  hovering the YOC mark shows the box under the document
  J22.1  🔖 costs nothing: 0 long tasks after a scroll stops; the place kept
  J22.3  Play in a foreign front end names the way, starts nothing

Gegenprobe v1.63 (bundle e40cd95b): every test RED (chronicle 05.10., JS).
A test that cannot reach its precondition returns False ("BAD …"), never True."""
import json

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"
SC = "document.querySelector('%s .jp-WindowedPanel-outer')" % FRONT
MK = ".nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,.nbvizmark,.nbcodemark,.nbendmark,.nbcellmark"

REC_START = r"""(MK) => {
  var h = document.getElementById('nbpanel-root'); window.__j22 = []; window.__j22on = true;
  var heads = function(){ return [].filter.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-header'),
                                  function(x){ return x.getBoundingClientRect().height > 0; }); };
  var pillOf = function(n, hs){
    var A = document.getElementById(n.getAttribute('data-target')); if (!A) return null;
    for (var i = 0; i < hs.length; i++) if (A.compareDocumentPosition(hs[i]) & 4) { var r = hs[i].getBoundingClientRect(); return r.top + r.height / 2; }
    return null; };
  var tick = function(){
    if (!window.__j22on) return;
    var hs = heads(), mp = h.querySelector('.nbmap'), mr = mp.getBoundingClientRect(), fr = {t: performance.now(), m: []};
    [].forEach.call(h.querySelectorAll('.nbmap-node'), function(n, i){
      if (n.classList.contains('nbgone')) return;
      var g = n.querySelector(MK); if (!g) return;
      var r = g.getBoundingClientRect(); if (!(r.height > 0) || r.bottom < mr.top || r.top > mr.bottom) return;
      fr.m.push([i, +r.height.toFixed(2), +(r.top + r.height / 2).toFixed(2), pillOf(n, hs), n.matches(':hover') ? 1 : 0]);
    });
    var hm = h.querySelector('.nbmap-here'); if (hm) { var q = hm.getBoundingClientRect(); fr.here = +(q.top + q.height / 2).toFixed(2); }
    fr.line = mr.top + (parseInt(h.dataset.railY0 || '0', 10) || 0);
    try { fr.z = localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'x'); } catch (e) {}
    window.__j22.push(fr); };
  var pr = document.getElementById('__j22probe');
  if (!pr) { pr = document.createElement('div'); pr.id = '__j22probe';
    pr.style.cssText = 'position:fixed;left:0;top:0;height:1px;width:1px;pointer-events:none;opacity:0'; document.body.appendChild(pr); }
  if (window.__j22RO) window.__j22RO.disconnect();
  window.__j22RO = new ResizeObserver(function(){ tick(); }); window.__j22RO.observe(pr);
  // one flip loop per recording: a loop of the previous recording still pending when this one
  // starts (a stop and a start within one frame) would flip the probe twice a frame — no change
  // of size, no observer call, a recording of one frame (gate 05.10.: 3 × "BAD 1 frames")
  var gen = window.__j22gen = (window.__j22gen || 0) + 1;
  var flip = function(){ if (!window.__j22on || gen !== window.__j22gen) return; pr.style.width = pr.style.width === '1px' ? '2px' : '1px'; requestAnimationFrame(flip); };
  requestAnimationFrame(flip); }"""
REC_STOP = "() => { window.__j22on = false; if (window.__j22RO) window.__j22RO.disconnect(); return window.__j22; }"

def _rec(pg, act, settle=1300):
    pg.evaluate(REC_START, MK); pg.wait_for_timeout(120)
    act(); pg.wait_for_timeout(settle)
    return pg.evaluate(REC_STOP)

def _judge(rec, size=True, skip_marks=()):
    """lag: |(mark - pill) - (mark - pill) at rest| over every frame, every mark with a
    pill (the rest value is the last frame: a mark pushed off its pill by a collision
    keeps its offset, it does not spring); back: the spread of a mark's size within one
    lens value (> 0.5 px = it slid or sprang); hov: frames in which a mark not hovered at
    the start is hovered."""
    ser = {}
    for fi, fr in enumerate(rec):
        for i, h, cy, pill, hov in fr["m"]:
            ser.setdefault(i, []).append((fi, h, cy, pill, hov))
    lag, nlag, back, hov = 0.0, 0, 0.0, 0
    zs = [fr.get("z") for fr in rec]
    for i, s in ser.items():
        fin = [x for x in s if x[3] is not None]
        if fin:
            rest = fin[-1][2] - fin[-1][3]
            for x in fin:
                d = abs((x[2] - x[3]) - rest)
                lag = max(lag, d); nlag += d > 2
        if size and i not in skip_marks:
            # E22.9 "no over-/undershoot, no in-between size": at each lens the mark has ONE size —
            # from the first frame that shows the lens to the last (a size that slides or springs
            # within one lens step is what the reader saw). How the size goes from one lens to the
            # next is the crowding rule's (E8.1: marks shrink where pills stand close), see detail.
            by = {}
            for x in s: by.setdefault(zs[x[0]], []).append(x[1])
            for zv, hs in by.items():
                back = max(back, max(hs) - min(hs))
        if i not in skip_marks and not s[0][4]:
            hov += sum(x[4] for x in s)
    here = max([abs(f["here"] - f["line"]) for f in rec if "here" in f] or [99])
    return {"frames": len(rec), "lag": round(lag, 1), "lagframes": nlag, "back": round(back, 2), "hover": hov, "marker": round(here, 1)}

def _grip(pg):
    return pg.evaluate("()=>{var r=document.querySelector('#nbpanel-root .nbgrip').getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}")

def _drag(pg, x, y, dx, dy, n=15, ms=16):
    pg.mouse.move(x, y); pg.mouse.down()
    for i in range(1, n + 1): pg.mouse.move(x + dx * i / n, y + dy * i / n); pg.wait_for_timeout(ms)
    pg.mouse.up()

def _calm(pg):
    # JupyterLab's toasts (bottom right; a fresh Lab asks about news) lie over the rail's lower
    # part and take the clicks meant for marks there — answered first, as a reader would
    for _ in range(3):
        try: pg.click(".jp-toast-buttonBar button:has-text('No')", timeout=600)
        except Exception: break
    pg.keyboard.press("Escape"); pg.mouse.move(5, 450); pg.wait_for_timeout(300)

STILL_JS = """() => new Promise(function(res){ var s = %s, last = null, same = 0, t0 = performance.now();
  (function f(){ var v = s.scrollTop; same = (v === last) ? same + 1 : 0; last = v;
    if (same >= 12 || performance.now() - t0 > 5000) res(Math.round(performance.now() - t0)); else requestAnimationFrame(f); })(); })"""

def _scroll_to(pg, frac):
    pg.evaluate("(f)=>{var s=%s; s.scrollTop=Math.round((s.scrollHeight-s.clientHeight)*f);}" % SC, frac); pg.wait_for_timeout(1500)

def _reset(pg):
    """lens 100 (Ctrl+0 over the notebook), panel shut, reading height back (double click on the knob)"""
    pg.mouse.move(500, 450); pg.keyboard.press("Control+0"); pg.wait_for_timeout(600)
    pg.evaluate("()=>{ window.__nbSetGui && window.__nbSetGui(0); }"); pg.wait_for_timeout(500)
    g = _grip(pg); pg.mouse.dblclick(g[0], g[1]); pg.wait_for_timeout(1200)
    pg.mouse.move(5, 450); pg.wait_for_timeout(300)

# ---------------------------------------------------------------- J22.9
def marks_steady(pg, ctx):
    """E22.9: per frame, while the lens goes ±5 (Ctrl+wheel with the pointer resting on a
    mark), the reading-height knob and the scroll thumb are dragged and the panel is pulled
    wider and back: every mark stays on its pill as at rest (≤ 2 px), sizes never step back
    (no over-/undershoot), no mark grows under a resting pointer, marker on the line ≤ 2 px."""
    _calm(pg); _scroll_to(pg, 0.3)
    mk = pg.evaluate("(MK)=>{var n=[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).filter(function(n){var r=n.getBoundingClientRect(); return !n.classList.contains('nbgone') && r.top>130 && r.top<760;})[0]; if(!n) return null; var g=n.querySelector(MK), r=g.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2, [].indexOf.call(document.querySelectorAll('#nbpanel-root .nbmap-node'), n)];}", MK)
    if not mk: return False, "BAD no mark in view"
    pg.mouse.move(mk[0], mk[1]); pg.wait_for_timeout(900)            # the reader's pointer rests on a mark
    out, bad = [], []
    def cw(dy):
        def f():
            pg.keyboard.down("Control")
            for _ in range(5): pg.mouse.wheel(0, dy); pg.wait_for_timeout(40)
            pg.keyboard.up("Control")
        return f
    for tag, act, size in (("lens+5", cw(-100), True), ("lens-5", cw(100), True)):
        j = _judge(_rec(pg, act), size, skip_marks=(mk[2],)); j["g"] = tag; out.append(j)
    pg.mouse.move(5, 450); pg.wait_for_timeout(400)
    g = _grip(pg)
    j = _judge(_rec(pg, lambda: _drag(pg, g[0], g[1], 0, 90)), False); j["g"] = "knob+90"; out.append(j)
    g = _grip(pg)
    j = _judge(_rec(pg, lambda: _drag(pg, g[0], g[1], 0, -90)), False); j["g"] = "knob-90"; out.append(j)
    th = pg.evaluate("()=>{var c=document.querySelector('#nbpanel-root .nbmap-cursor'); if(!c) return null; var r=c.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}")
    if th:
        j = _judge(_rec(pg, lambda: _drag(pg, th[0], th[1], 0, 120, 20)), False); j["g"] = "thumb+120"; out.append(j)
    else: bad.append("BAD no thumb")
    g = _grip(pg)
    j = _judge(_rec(pg, lambda: _drag(pg, g[0], g[1], -140, 0)), False); j["g"] = "width+140"; out.append(j)
    g = _grip(pg)
    j = _judge(_rec(pg, lambda: _drag(pg, g[0], g[1], 140, 0)), False); j["g"] = "width-140"; out.append(j)
    _reset(pg)
    for j in out:
        if j["frames"] < 10: bad.append("%s BAD %d frames" % (j["g"], j["frames"]))
        if j["lag"] > 2: bad.append("%s mark off its pill %.1f px (%d frames)" % (j["g"], j["lag"], j["lagframes"]))
        if j["back"] > 0.5: bad.append("%s size not one per lens step: spread %.2f px" % (j["g"], j["back"]))
        if j["hover"]: bad.append("%s %d hover frames" % (j["g"], j["hover"]))
        if j["marker"] > 2: bad.append("%s marker %.1f px off the line" % (j["g"], j["marker"]))
    det = " · ".join("%s lag %.1f back %.1f hov %d" % (j["g"], j["lag"], j["back"], j["hover"]) for j in out)
    return (not bad), ("; ".join(bad) + " | " if bad else "") + det

# ---------------------------------------------------------------- J22.6
def same_frame(pg, ctx):
    """E22.6: while the wheel glides over the document and while the scroll thumb is dragged,
    every mark stays on its pill in every frame (|Δ| ≤ 2 px), 0 frames late."""
    _calm(pg); _scroll_to(pg, 0.25)
    out = []
    def wheel(dy):
        def f():
            pg.mouse.move(420, 500)
            for _ in range(6): pg.mouse.wheel(0, dy); pg.wait_for_timeout(50)
        return f
    for tag, act in (("wheel down", wheel(120)), ("wheel up", wheel(-120))):
        j = _judge(_rec(pg, act), False); j["g"] = tag; out.append(j)
    for dy in (110, -110):
        th = pg.evaluate("()=>{var c=document.querySelector('#nbpanel-root .nbmap-cursor'); if(!c) return null; var r=c.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}")
        if not th: return False, "BAD no thumb"
        j = _judge(_rec(pg, lambda: _drag(pg, th[0], th[1], 0, dy, 20)), False); j["g"] = "thumb%+d" % dy; out.append(j)
    _calm(pg)
    bad = ["%s %.1f px late in %d frames" % (j["g"], j["lag"], j["lagframes"]) for j in out if j["lag"] > 2 or j["lagframes"]]
    bad += ["%s BAD %d frames" % (j["g"], j["frames"]) for j in out if j["frames"] < 10]
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join("%s %.1f" % (j["g"], j["lag"]) for j in out)

# ---------------------------------------------------------------- J22.4
LAND_JS = r"""(i)=>{ var h=document.getElementById('nbpanel-root'), n=h.querySelectorAll('.nbmap-node')[i], mp=h.querySelector('.nbmap');
  var line = mp.getBoundingClientRect().top + (parseInt(h.dataset.railY0||'0',10)||0);
  var A=document.getElementById(n.getAttribute('data-target'));
  var hs=A?[].filter.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-header'),function(x){return !!(A.compareDocumentPosition(x)&4) && x.getBoundingClientRect().height>0;}):[];
  var hr=hs[0]?hs[0].getBoundingClientRect():null;
  return {line: line, pill: hr?hr.top+hr.height/2:null, name: (n.textContent||'').trim().slice(0,22)}; }"""
CHAPS = r"""()=>[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).map(function(n,i){return [i, (n.classList.contains('chap')||n.classList.contains('sect')) && !n.classList.contains('nbgone') && !n.classList.contains('title') && !n.classList.contains('cell') && !n.classList.contains('own')];}).filter(function(x){return x[1];}).map(function(x){return x[0];})"""
def _click_node(pg, i):
    g = pg.evaluate("(i)=>{var n=document.querySelectorAll('#nbpanel-root .nbmap-node')[i]; var g=n.querySelector('%s')||n; var r=g.getBoundingClientRect(); var m=document.querySelector('#nbpanel-root .nbmap').getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2, r.top>m.top+4 && r.bottom<m.bottom-4];}" % MK, i)
    # a real click where the mark is drawn — only if the mark itself is the topmost thing there
    top = g[2] and pg.evaluate("([x, y, i])=>{var e=document.elementFromPoint(x, y); return !!(e && e.closest('.nbmap-node') === document.querySelectorAll('#nbpanel-root .nbmap-node')[i]);}", [g[0], g[1], i])
    if top: pg.mouse.click(g[0], g[1])
    else: pg.evaluate("(i)=>{document.querySelectorAll('#nbpanel-root .nbmap-node')[i].click();}", i)

def land_on_line(pg, ctx):
    """E22.4: the reading height dragged to 50 % (lens 100 %) and 70 % (lens 150 %) of the
    rail's window; 3 chapter clicks each: pill − reading line ≤ 2 px after the landing."""
    # right after Run All the spawn on the title holds the page for a few seconds
    # (E12.2, lab_flow E) — a click before that is pulled back to the top
    _calm(pg); pg.wait_for_timeout(4000); bad, rows = [], []
    for frac, lens in ((0.5, 100), (0.7, 150)):
        if lens != 100:
            pg.mouse.move(500, 450); pg.keyboard.down("Control")
            for _ in range((lens - 100) // 5): pg.mouse.wheel(0, -100); pg.wait_for_timeout(110)
            pg.keyboard.up("Control"); pg.wait_for_timeout(2600)
        g = _grip(pg)
        m = pg.evaluate("()=>{var r=document.querySelector('#nbpanel-root .nbmap').getBoundingClientRect(); return [r.top, r.height];}")
        _drag(pg, g[0], g[1], 0, m[0] + m[1] * frac - g[1], 12, 25); pg.wait_for_timeout(1300)
        chs = pg.evaluate(CHAPS)
        if len(chs) < 4: return False, "BAD %d chapter marks" % len(chs)
        for ci in (chs[2], chs[-2], chs[1]):
            # the landing glides (≤ 1.5 s, FINAL 11); read every 100 ms up to 4 s: where it comes to
            # rest, and when (a landing that ends off the line and one that is only slow look apart)
            _click_node(pg, ci); t, d, seen = 0, None, []
            while t < 4000:
                pg.wait_for_timeout(100); t += 100
                s = pg.evaluate(LAND_JS, ci)
                d = None if s["pill"] is None else round(s["pill"] - s["line"], 1)
                seen.append(d)
                if t >= 1500 and len(seen) >= 4 and all(x is not None and abs(x - d) < 0.6 for x in seen[-4:]): break
            onl = next((i for i, x in enumerate(seen) if x is not None and abs(x) <= 2
                        and all(y is not None and abs(y) <= 2 for y in seen[i:])), None)
            when = (onl + 1) * 100 if onl is not None else None
            rows.append("%d%%/%d%% %s %s (%s ms)" % (frac * 100, lens, s["name"][:12], d, when))
            if d is None or abs(d) > 2:
                bad.append("%d%%/%d%% %s: pill − line %s at rest (trace %s)" % (frac * 100, lens, s["name"], d, seen[::3][:12]))
    _reset(pg)
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(rows)

# ---------------------------------------------------------------- J22.7
YOC7 = r"""()=>{ var P=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); var f=P&&P.querySelector('.jp-Notebook-footer');
  var n=document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]'); var g=n&&(n.querySelector('.nbsect')||n);
  if(!f||!g) return null; var r=f.getBoundingClientRect(), cs=getComputedStyle(f), q=g.getBoundingClientRect();
  return {op: +cs.opacity, bs: cs.borderTopStyle, fy: [r.top, r.bottom], vis: r.top>=0 && r.bottom<=innerHeight, m: [q.left+q.width/2, q.top+q.height/2], mvis: q.top>0 && q.bottom<innerHeight}; }"""
def yoc_box(pg, ctx):
    """E22.7: hovering the YOC mark of the timeline shows the strip "＋ Add your own coding
    cell" in the document as its own hover does (opacity 1, solid edge, in view), and it
    goes again when the pointer leaves the mark. Title open (scrolled to the end)."""
    _calm(pg)
    pg.evaluate("()=>{var s=%s; s.scrollTop=s.scrollHeight;}" % SC); pg.wait_for_timeout(1800)
    s = pg.evaluate(YOC7)
    if not s or not s["mvis"]: return False, "BAD YOC mark %s" % ("missing" if not s else "not in view")
    pg.mouse.move(s["m"][0] - 60, s["m"][1] - 60); pg.wait_for_timeout(300)
    s = pg.evaluate(YOC7); pg.mouse.move(s["m"][0], s["m"][1], steps=4); pg.wait_for_timeout(600)
    on = pg.evaluate(YOC7)
    pg.mouse.move(5, 450); pg.wait_for_timeout(500)
    off = pg.evaluate(YOC7)
    ok = on["op"] >= 0.99 and on["bs"] == "solid" and on["vis"] and off["op"] <= 0.01
    return ok, "on mark: opacity %.2f %s in view %s · off: opacity %.2f" % (on["op"], on["bs"], on["vis"], off["op"])

# ---------------------------------------------------------------- J22.1
LT_ON = """()=>{ window.__j22lt=[]; if(window.__j22ltO) window.__j22ltO.disconnect();
  window.__j22ltO=new PerformanceObserver(function(l){ l.getEntries().forEach(function(e){ window.__j22lt.push([e.startTime, e.duration]); }); });
  window.__j22ltO.observe({entryTypes:['longtask']}); return performance.now(); }"""
SYS = ("(root)", "(program)", "(idle)", "(garbage collector)")
def _ours(prof, t0, pf0, lts):
    """Each long task > 50 ms with the share of its CPU samples that run OUR script (the toolkit
    is injected by the notebook's output: its frames have no URL; JupyterLab's own code comes
    from /static/ files). A task of the Lab's (a file-browser poll, a kernel message) is not the
    bookmark's and is reported, not counted."""
    nodes = {n["id"]: n for n in prof["nodes"]}; parent = {}
    for n in prof["nodes"]:
        for c in n.get("children", []): parent[c] = n["id"]
    def ours(sid):
        x = sid
        while x in nodes:
            cf = nodes[x]["callFrame"]
            if not cf["url"] and cf["functionName"] not in SYS and cf["functionName"]: return True
            x = parent.get(x)
        return False
    def top(sid):
        """the outermost frame of ours on the stack (which pass of ours ran)"""
        x, best = sid, None
        while x in nodes:
            cf = nodes[x]["callFrame"]
            if not cf["url"] and cf["functionName"] not in SYS and cf["functionName"]: best = "%s:%d" % (cf["functionName"], cf["lineNumber"])
            x = parent.get(x)
        return best
    res = []
    for a, d in lts:
        if d <= 50: continue
        tcur, n, m, who = prof["startTime"], 0, 0, {}
        for sid, dt in zip(prof["samples"], prof["timeDeltas"]):
            tcur += dt; rel = (tcur - prof["startTime"]) / 1000.0
            if a - pf0 <= rel <= a - pf0 + d:
                n += 1; o = ours(sid); m += o
                if o: w = top(sid); who[w] = who.get(w, 0) + 1
        res.append((round(a - t0), round(d), round(m / n, 2) if n else None,
                    sorted(who, key=lambda k: -who[k])[:2]))
    return res

def bookmark_cheap(pg, ctx):
    """E22.1: after the wheel stops, 4 s without a long task > 50 ms of our script (two stops;
    tasks of JupyterLab's own code are listed, not counted — CPU profile per task); the 🔖
    place (digichemjn.bookmark.<id>) is the lit mark within 8 s of the stop."""
    _calm(pg); _scroll_to(pg, 0.1)
    key = "digichemjn.bookmark." + ctx.get("id", "")
    cdp = pg.context.new_cdp_session(pg); cdp.send("Profiler.enable"); cdp.send("Profiler.setSamplingInterval", {"interval": 500})
    stops, bm, here = [], None, None
    for k in range(2):
        cdp.send("Profiler.start"); pf0 = pg.evaluate("()=>performance.now()"); pg.wait_for_timeout(300)   # warm: its own start is no task of ours
        pg.mouse.move(420, 500)
        for _ in range(4): pg.mouse.wheel(0, 150); pg.wait_for_timeout(60)
        # the stop: the page has not moved for 12 frames (the glide is over) — what comes after
        # it is what E22.1 is about; the glide's own frames are E18.6's
        stopped = pg.evaluate(STILL_JS % SC)
        t0 = pg.evaluate(LT_ON); pg.wait_for_timeout(4000)
        prof = cdp.send("Profiler.stop")["profile"]
        stops.append(_ours(prof, t0, pf0, pg.evaluate("()=>window.__j22lt")))
        here = pg.evaluate("()=>{var n=document.querySelector('#nbpanel-root .nbmap-node.here'); return n?n.getAttribute('data-target'):null;}")
        for _ in range(40):
            bm = pg.evaluate("(k)=>localStorage.getItem(k)", key)
            if here and bm == here: break
            pg.wait_for_timeout(100)
    pg.evaluate("()=>{ if(window.__j22ltO) window.__j22ltO.disconnect(); }")
    try: cdp.detach()
    except Exception: pass
    mine = [t for s in stops for t in s if t[2] is None or t[2] >= 0.5]
    ok = not mine and here is not None and bm == here
    return ok, "long tasks > 50 ms after the stops (ms, ms, share ours) %s · 🔖 %s (lit %s)" % (stops, bm, here)

# ---------------------------------------------------------------- J22.3
def play_foreign(pg, ctx):
    """E22.3: in PyCharm (the kernel's word, `.nbfeed[data-nbenv]`) Play (clicked as a DOM
    click: after Run All the cover's Play is folded away) starts no run and
    names the way ("Run All") at once; nothing loads. The attribute is put back after."""
    _calm(pg)
    # every feed in the page (with two notebooks open the page reads the first one: one Lab, one
    # front end — PyCharm runs one notebook per view anyway)
    st = pg.evaluate("""()=>{ var P=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); var f=P&&P.querySelector('.nbfeed[data-nbenv]');
      var pl=P&&P.querySelector('.nbcover-play'); if(!f||!pl) return null; window.__j22env=f.getAttribute('data-nbenv');
      document.querySelectorAll('.nbfeed[data-nbenv]').forEach(function(x){ x.setAttribute('data-nbenv','pycharm'); });
      window.__nbEnvV=null; return {run: f.getAttribute('data-nbid'), env: window.__nbEnv ? window.__nbEnv().env : null}; }""")
    if st and st.get("env") != "pycharm":
        pg.evaluate("()=>{ document.querySelectorAll('.nbfeed[data-nbenv]').forEach(function(x){ x.setAttribute('data-nbenv', window.__j22env || 'server'); }); window.__nbEnvV=null; }")
        return False, "BAD the page did not take the kernel's word pycharm (%s)" % st
    if not st: return False, "BAD no .nbfeed[data-nbenv] or no Play"
    # after Run All the cover's Play is folded away (display:none) — the click goes to the
    # element itself (a DOM click, caught by the page's capture listener like a real one)
    pg.wait_for_timeout(300)
    pg.evaluate("()=>{ document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-play').click(); }"); pg.wait_for_timeout(1500)
    r = pg.evaluate("""()=>{ var P=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); var pl=P.querySelector('.nbcover-play');
      var m=pl.parentNode.querySelector('.nbrunall-msg'); var L=document.getElementById('nbload');
      var f=P.querySelector('.nbfeed[data-nbenv]'); var out={msg: m?m.textContent:'', load: !!(L && !L.classList.contains('nbload-out')), run: f?f.getAttribute('data-nbid'):null,
        busy: (P.querySelector('.jp-Notebook-ExecutionIndicator')||{getAttribute:function(){return null;}}).getAttribute('data-status')};
      document.querySelectorAll('.nbfeed[data-nbenv]').forEach(function(x){ x.setAttribute('data-nbenv', window.__j22env || 'server'); }); window.__nbEnvV=null; return out; }""")
    pg.keyboard.press("Escape")
    ok = "Run All" in r["msg"] and not r["load"] and r["run"] == st["run"]
    return ok, "message %r · loading %s · run %s → %s" % (r["msg"][:90], r["load"], st["run"], r["run"])

TESTS = [("J22.7 YOC hover shows the box", yoc_box),
         ("J22.6 rail in the same frame", same_frame),
         ("J22.9 marks steady zoom/drag", marks_steady),
         ("J22.4 click lands on moved line", land_on_line),
         ("J22.1 bookmark costs nothing", bookmark_cheap),
         ("J22.3 Play in PyCharm names way", play_foreign)]
