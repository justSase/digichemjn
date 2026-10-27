"""E31 · CSS — Werkstatt CSS, 12.10. abends (Nutzer zu v1.77: PyCharm Vorlage, Lite cyber; Wortlaut
plan/STOP.md „E31 — GILT JETZT“). Real kernel + real 20-reader.js for the reading window (every output a
page of its own, PyCharm), real JupyterLab under Playwright for the Lab rows. Everything read off the page.
Vertrag JS: claude/VERTRAG-E31-js.md (--nbgs, .nbrw-grip, .nbrw-marker, .nbrw-cv-*): where the JS half is
not in the page yet, the element is set in as the contract writes it (stand-in, row says so).

    python3 tests/regress/css_e31.py [notebook.ipynb] [--shots DIR] [--no-lab]

Window (1400 x 900, minimal light):
  F1w  A± (the window's A−/A+ buttons, 90 / 100 / 150 %): every kind of text keeps its ratio to the body
       text (±3 %): heading, check/run button, input, code field, inline code, table cell, slider value,
       formula (svg height).
  G1w  --nbgs 1.3 on .nbrw (contract): tool button font + height x 1.3 (±3 %); the document text unchanged
       (±0.1 px). E33 B5: the hover box no longer (panel: width and lens, css_e33).
  T2   the tool column has no ground and no edge; each tool button its own surface and edge.
  V1w  panel open: no edge line on its left side (alpha 0) — it may lie over the text.
  P1   the grip (.nbrw-grip): round (w = h, radius 50 %), ring in the accent colour.
  M1   the marker (.nbrw-marker): round, glowing; .is-moving shows a trail (::after opacity >= .9),
       0.7 s after it stops the trail is gone (<= .1).
  Z1   on the main axis (<= 1 px): table of contents, title card, headings, boxes, tasks — panel open and shut.
  T1   preview timeline: ONE row (all dots on one line, ±1 px), every name in one line, no two names
       overlap, neighbouring chapter names on opposite sides of the line.
Lab (1400 x 900, minimal light; V1 cyber dark):
  N1   no fade at the top/bottom of the document (scroller mask none).
  V1   mouse on the lens slider (focus in the panel → .nbkbd), panel pulled open: no line down the panel's
       left edge (outline none, border transparent, no inset on the left).
  F1   window.__nbFontSize 90 / 100 / 150: text, Check, Skip, inline code, code field, chapter / section /
       fold heads, table cell, slider readout, formula, hover box keep their ratio to the text (±3 %);
       at 100 % Skip = Check.
  G1   --nbgs 1.3 (contract: <html>, #nbpanel-root): tool buttons 34 → 44.2 px, the ⚙ drawer's content
       zoom 1.3, the document text unchanged.
Gegenprobe v1.77 (859cf890, Vorlage): red in F1w, G1w, T2, V1w, P1, M1, Z1, T1, N1, V1, F1, G1 (chronicle).
exit 0 = REGRESS-CSS-E31 OK."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from env_iframe import run_cell

CHROME = os.environ.get("DIGICHEM_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
W, H = 1400, 900

def page(html, dark):
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:%s;color:%s'>%s"
            % ("#2b2d30" if dark else "#ffffff", "#dfe1e5" if dark else "#1f2328", html))

OPEN = r"""() => { var rw = document.querySelector('.nbrw'); if (!rw) return 'no window';
  var p = rw.querySelector('.nbrw-cover [data-nbrw-act=play]'); if (p && rw.getAttribute('data-nbrw-view') === 'cover') p.click();
  rw.setAttribute('data-nbrw-theme', 'light'); rw.setAttribute('data-nbrw-skin', 'minimal');
  rw.querySelectorAll('.nbrw-win details').forEach(function(d){ d.open = true; }); return 'ok'; }"""

# sizes of the kinds of text in the window's document (first visible of each)
WSIZE = r"""() => { var rw = document.querySelector('.nbrw'), rd = rw.querySelector('.nbrw-win > .nbreading');
  var vis = function(e){ var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  var first = function(s){ return [].filter.call(rd.querySelectorAll(s), vis)[0] || null; };
  var fs = function(s){ var e = first(s); return e ? parseFloat(getComputedStyle(e).fontSize) : null; };
  var hh = function(s){ var e = first(s); return e ? e.getBoundingClientRect().height : null; };
  var v = rw.querySelector('output.nbfs-val, .nbfs-val');
  return {val: v ? v.textContent.trim() : null, text: fs('.nbr-nbbox p, .nbr-nbbox'), h3: fs('h3.nbread-h'), h2: fs('h2.nbread-h'),
          check: fs('.nbrw-check'), run: fs('.nbrw-run'), input: fs('.nbrw-input'), code: fs('.nbrw-code .nbrw-ta'),
          icode: fs('.nbrw-doc code:not(.nbrw-copy code)'), td: fs('.nbrw-doc td'), val2: fs('.nbrw-val'), formula: hh('svg.nbr-dmath')}; }"""

AXIS = r"""() => { var rw = document.querySelector('.nbrw'), win = rw.querySelector('.nbrw-win'), R = win.getBoundingClientRect();
  var mid = (R.left + R.right) / 2, out = [];
  var vis = function(e){ var r = e.getBoundingClientRect(); if (!(r.width > 0 && r.height > 0)) return false;
    for (var x = e; x && x !== rw; x = x.parentElement) { var s = getComputedStyle(x); if (s.display === 'none' || s.visibility === 'hidden') return false; } return true; };
  ['ol.nbread-toc', '.nbrw-doc .nbr-nbtitle-card', 'h3.nbread-h', 'h2.nbread-h', '.nbr-nbbox', '.nbrw-task', '.nbrw-win > .nbreading'].forEach(function(s){
    [].filter.call(rw.querySelectorAll(s), vis).slice(0, 4).forEach(function(e){ var r = e.getBoundingClientRect();
      var o = (r.left + r.right) / 2 - mid; if (Math.abs(o) > 1) out.push(s + ' ' + o.toFixed(1)); }); });
  // the table of contents: its INK on the axis too (a full-width list is centred as a box, its text is not);
  // the numbers stand in the list's left padding, so the text alone sits half of that to the right
  var toc = rw.querySelector('ol.nbread-toc');
  if (toc && vis(toc)) { var l = 1e9, r2 = -1e9, w = document.createTreeWalker(toc, NodeFilter.SHOW_TEXT), n;
    while ((n = w.nextNode())) { if (!n.textContent.trim()) continue; var g = document.createRange(); g.selectNodeContents(n);
      [].forEach.call(g.getClientRects(), function(q){ if (q.width > 0) { l = Math.min(l, q.left); r2 = Math.max(r2, q.right); } }); }
    var pad = parseFloat(getComputedStyle(toc).paddingLeft) || 0, io = (l + r2) / 2 - mid;
    if (Math.abs(io - pad / 2) > 2) out.push('toc ink ' + io.toFixed(1) + ' (pad ' + pad.toFixed(1) + ')'); }
  return out; }"""

TOOLS = r"""() => { var rw = document.querySelector('.nbrw'), t = rw.querySelector('.nbrw-tools'); if (!t) return {err: 'no tools'};
  var cs = getComputedStyle(t), b = [].filter.call(t.querySelectorAll('.nbrw-btn'), function(e){ return e.getBoundingClientRect().width > 0; });
  var tr = function(c){ return /rgba\(.*, 0\)$|transparent/.test(c); };
  var bad = b.filter(function(e){ var s = getComputedStyle(e); return parseFloat(s.borderTopWidth) === 0 || tr(s.backgroundColor); }).length;
  return {bg: cs.backgroundColor, bgTr: tr(cs.backgroundColor) && cs.backgroundImage === 'none',
          edge: ['Top', 'Right', 'Bottom', 'Left'].map(function(k){ return parseFloat(cs['border' + k + 'Width']); }).reduce(function(a, x){ return a + x; }, 0),
          shadow: cs.boxShadow, buttons: b.length, bare: bad}; }"""

GS = r"""(gs) => { var rw = document.querySelector('.nbrw'), R = window.__nbReader;
  // with js-E31 the window's own control (it also draws the geometry inline); without it the contract's variable
  if (R && R.gs) R.gs(gs === null ? 100 : Math.round(gs * 100));
  else if (gs === null) rw.style.removeProperty('--nbgs'); else rw.style.setProperty('--nbgs', String(gs));
  var vis = function(e){ return e && e.getBoundingClientRect().width > 0; };
  var btn = [].filter.call(rw.querySelectorAll('.nbrw-tools .nbrw-btn'), vis)[1];
  var lab = [].filter.call(rw.querySelectorAll('.nbrw-panel .nbrw-lab'), vis)[0], mk = lab ? lab.closest('.nbrw-mark') : null;
  var tip = rw.querySelector('.nbrw-tip'), rd = rw.querySelector('.nbrw-win > .nbreading');
  return {btnF: btn ? parseFloat(getComputedStyle(btn).fontSize) : null, btnH: btn ? btn.getBoundingClientRect().height : null,
          lab: lab ? parseFloat(getComputedStyle(lab).fontSize) : null, dot: mk ? parseFloat(getComputedStyle(mk, '::before').width) : null,
          tip: tip ? parseFloat(getComputedStyle(tip).fontSize) : null, text: parseFloat(getComputedStyle(rd).fontSize)}; }"""

PANEL = r"""() => { var rw = document.querySelector('.nbrw'), p = rw.querySelector('.nbrw-panel'), cs = getComputedStyle(p);
  return {state: rw.getAttribute('data-nbrw-panel'), left: cs.borderLeftColor, lw: parseFloat(cs.borderLeftWidth)}; }"""

STAND = r"""() => { var rw = document.querySelector('.nbrw'), p = rw.querySelector('.nbrw-panel'), tr = rw.querySelector('.nbrw-track') || p;
  var g = rw.querySelector('.nbrw-grip'), m = rw.querySelector('.nbrw-marker'), st = [];
  if (!g) { g = document.createElement('button'); g.className = 'nbrw-grip'; g.type = 'button'; g.textContent = '‹';
    g.style.cssText = 'position:absolute;left:-14px;top:200px'; p.appendChild(g); st.push('grip'); }
  if (!m) { m = document.createElement('div'); m.className = 'nbrw-marker';
    m.style.cssText = 'position:absolute;left:-4px;top:160px'; tr.appendChild(m); st.push('marker'); }
  var acc = getComputedStyle(rw).getPropertyValue('--rw-acc').trim();
  var gs = getComputedStyle(g), gr = g.getBoundingClientRect(), ms = getComputedStyle(m), mr = m.getBoundingClientRect();
  var probe = document.createElement('i'); probe.style.color = acc; rw.appendChild(probe); var accRGB = getComputedStyle(probe).color; probe.remove();
  return {stand: st, grip: {w: gr.width, h: gr.height, rad: gs.borderTopLeftRadius, ring: gs.borderTopColor, accent: accRGB, bw: parseFloat(gs.borderTopWidth)},
          marker: {w: mr.width, h: mr.height, rad: ms.borderTopLeftRadius, glow: ms.boxShadow, after: getComputedStyle(m, '::after').content,
                   a0: parseFloat(getComputedStyle(m, '::after').opacity)}}; }"""

COVER = r"""() => { var rw = document.querySelector('.nbrw'); var c = rw.querySelector('[data-act=cover]'); if (c) c.click();
  return new Promise(function(res){ setTimeout(function(){
    // Hauptwerkstatt 12.10. (E31 merge): js-E31 draws a dot as a 0 x 0 anchor (its ::before is the dot) — shown, not
    // measured by its box (behauptete bisher: a dot has a box wider than 0)
    var dots = [].filter.call(rw.querySelectorAll('.nbrw-cover .nbrw-cv-dot'), function(e){ return e.getBoundingClientRect().width > 0
      || (e.getClientRects().length && getComputedStyle(e).display !== 'none' && parseFloat(getComputedStyle(e, '::before').width) > 0); });
    // the dot's centre: its ::before in the flow (v1.77 DOM) or, js-E31, a 0 x 0 anchor the ::before is centred on
    var ys = dots.map(function(d){ var r = d.getBoundingClientRect(), b = getComputedStyle(d, '::before');
      return r.height < 1 ? r.top : r.top + parseFloat(b.marginTop || 0) + parseFloat(b.height || 0) / 2; });
    var labs = [].filter.call(rw.querySelectorAll('.nbrw-cover .nbrw-cv-lab'), function(e){ return e.getBoundingClientRect().width > 0; });
    var L = labs.map(function(l){ var r = l.getBoundingClientRect(), d = l.closest('.nbrw-cv-dot').getBoundingClientRect(), s = getComputedStyle(l);
      return {l: r.left, r: r.right, t: r.top, b: r.bottom, h: r.height, fs: parseFloat(s.fontSize), lh: parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.25,
              up: r.bottom <= d.top + 1, text: l.textContent.trim().slice(0, 24)}; });
    var ov = 0; for (var i = 0; i < L.length; i++) for (var j = i + 1; j < L.length; j++) {
      var a = L[i], b2 = L[j]; if (a.l < b2.r - .5 && b2.l < a.r - .5 && a.t < b2.b - .5 && b2.t < a.b - .5) ov++; }
    var alt = 0; for (var k = 1; k < L.length; k++) if (L[k].up === L[k - 1].up) alt++;
    res({n: dots.length, spread: ys.length ? Math.max.apply(null, ys) - Math.min.apply(null, ys) : 0,
         multi: L.filter(function(x){ return x.h > x.lh * 1.5; }).map(function(x){ return x.text + ' ' + x.h.toFixed(0); }),
         overlap: ov, sameSide: alt, labs: L.length});
    if (c) { var p = rw.querySelector('.nbrw-cover [data-nbrw-act=play]'); if (p) p.click(); }
  }, 400); }); }"""

def ratio_rows(tag, base, got, rows, fails, keys):
    """got: {pct: sizes}; ratio to the text at the same A, relative to 100 %."""
    bad = []
    for k in keys:
        if base.get(k) is None or not base.get("text"): continue
        r0 = base[k] / base["text"]
        for pct, g in got.items():
            if g.get(k) is None or not g.get("text"): continue
            q = (g[k] / g["text"]) / r0
            if abs(q - 1) > 0.03: bad.append("%s@%d %.3f (%.2f→%.2f px)" % (k, pct, q, base[k], g[k]))
    rows.append("%s: A 100 %s · %s" % (tag, {k: (round(base[k], 2) if base.get(k) else None) for k in keys},
                                           "ratios constant" if not bad else "RED " + "; ".join(bad[:6])))
    if bad: fails.append("%s ratio %s" % (tag, bad[:6]))

def window_rows(html, shots, rows, fails):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx = b.new_context(viewport={"width": W, "height": H}, color_scheme="light")
        # an http origin (route, no network): the window keeps A±, height, panel in localStorage — on
        # about:blank (set_content) storage throws and A± stays at 100 %
        body = page(html, False)
        ctx.route("http://nbrw.test/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=body))
        pg = ctx.new_page(); pg.goto("http://nbrw.test/"); pg.wait_for_timeout(800)
        st = pg.evaluate(OPEN); pg.wait_for_timeout(400)
        if st != "ok":
            fails.append("window: %s" % st); b.close(); return
        # T1 first (the cover), then the document
        cv = pg.evaluate(COVER); pg.wait_for_timeout(400)
        f = []
        if cv["n"] < 3: f.append("no dots %s" % cv)
        if cv["spread"] > 1: f.append("dots on %.1f px of height (one row: <= 1)" % cv["spread"])
        if cv["multi"]: f.append("names over two lines %s" % cv["multi"][:3])
        if cv["overlap"]: f.append("%d names overlap" % cv["overlap"])
        if cv["labs"] > 1 and cv["sameSide"]: f.append("%d neighbouring names on the same side" % cv["sameSide"])
        rows.append("T1 window cover: %d dots, spread %.1f px, names %d, two-line %d, overlap %d, same side %d %s"
                    % (cv["n"], cv["spread"], cv["labs"], len(cv["multi"]), cv["overlap"], cv["sameSide"], "OK" if not f else "RED"))
        fails += ["T1: %s" % x for x in f]
        if shots:
            os.makedirs(shots, exist_ok=True)
            pg.evaluate("() => { document.querySelector('.nbrw [data-act=cover]').click(); }"); pg.wait_for_timeout(400)
            pg.evaluate("() => { var w = document.querySelector('.nbrw-win'), e = document.querySelector('.nbrw-cv-tl'); w.scrollTop += e.getBoundingClientRect().top - w.getBoundingClientRect().top - 260; }")
            pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(shots, "E31-css-T1-fenster-vorschau-hell.png"))
            pg.evaluate("() => { var p = document.querySelector('.nbrw-cover [data-nbrw-act=play]'); if (p) p.click(); }"); pg.wait_for_timeout(400)
        pg.evaluate(OPEN); pg.wait_for_timeout(300)
        # F1w — through the window's own A−/A+ buttons
        click = lambda act, n: [pg.click(".nbrw [data-act='%s']" % act) for _ in range(n)]
        base = pg.evaluate(WSIZE)
        got = {}
        click("f-", 1); pg.wait_for_timeout(300); g = pg.evaluate(WSIZE); got[90] = g
        click("f+", 6); pg.wait_for_timeout(300); g = pg.evaluate(WSIZE); got[150] = g
        rows.append("F1w window A: 100 → %s / %s (shown)" % (got[90]["val"], got[150]["val"]))
        if shots:
            pg.evaluate("() => { var w = document.querySelector('.nbrw-win'), e = document.querySelector('.nbrw-task'); w.scrollTop += e.getBoundingClientRect().top - w.getBoundingClientRect().top - 120; }")
            pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(shots, "E31-css-F1-fenster-A150-hell.png"))
        click("f-", 5); pg.wait_for_timeout(300)
        ratio_rows("F1w window", base, got, rows, fails, ["h3", "h2", "check", "run", "input", "code", "icode", "td", "val2", "formula"])
        # T2
        t = pg.evaluate(TOOLS)
        f = []
        if t.get("err"): f.append(t["err"])
        else:
            if not t["bgTr"]: f.append("tool column has a ground %s" % t["bg"])
            if t["edge"] > 0: f.append("tool column has an edge %.0f px" % t["edge"])
            if t["bare"]: f.append("%d tool buttons without own surface/edge" % t["bare"])
        rows.append("T2 window tools: %s %s" % (t, "OK" if not f else "RED"))
        fails += ["T2: %s" % x for x in f]
        # G1w
        pg.evaluate("() => { var m = document.querySelector('.nbrw-panel .nbrw-mark'); if (m) m.dispatchEvent(new MouseEvent('mouseover', {bubbles: true})); }")
        g0 = pg.evaluate(GS, None); g1 = pg.evaluate(GS, 1.3); pg.evaluate(GS, None)
        f = []
        # the marks (dot, name, pips) JS scales as a whole (transform scale(gs) from the rail, js-E31) — not CSS
        # E33 B5 (Werkstatt CSS, 13.10.): the GUI size acts on the tools on the left only; the hover box belongs to the
        # panel and follows its width and the lens (css_e33 B5) — behauptete bisher: hover box x --nbgs (E31 G1)
        for k in ("btnF", "btnH"):
            if g0.get(k) and g1.get(k) and abs(g1[k] / g0[k] - 1.3) > 0.039: f.append("%s %.2f → %.2f (x %.3f, soll 1.3)" % (k, g0[k], g1[k], g1[k] / g0[k]))
            if not g0.get(k): rows.append("G1w: %s not in the page" % k)
        if abs(g1["text"] - g0["text"]) > 0.1: f.append("document text %.2f → %.2f" % (g0["text"], g1["text"]))
        rows.append("G1w window --nbgs 1.3: %s → %s %s" % (g0, g1, "OK" if not f else "RED"))
        fails += ["G1w: %s" % x for x in f]
        # Z1 — panel as it is, then the other way
        a1 = pg.evaluate(AXIS)
        # E33 B4 (Werkstatt CSS, 13.10.): the fold button under the timeline is gone from sight (the grip folds the
        # panel) — a DOM click on it, not Playwright's (behauptete bisher: the foot button is visible and clickable)
        PANEL_TOGGLE = "() => { document.querySelector('.nbrw [data-act=panel]').click(); }"
        pg.evaluate(PANEL_TOGGLE); pg.wait_for_timeout(500)
        a2 = pg.evaluate(AXIS); ps2 = pg.evaluate(PANEL)
        pg.evaluate(PANEL_TOGGLE); pg.wait_for_timeout(500)
        ps1 = pg.evaluate(PANEL)
        rows.append("Z1 window axis: panel %s %s · panel %s %s" % (ps1["state"], a1 or "all on the axis", ps2["state"], a2 or "all on the axis"))
        if a1 or a2: fails.append("Z1 off the axis %s %s" % (a1[:4], a2[:4]))
        # V1w — the open panel without an edge line on its left
        po = ps1 if ps1["state"] == "open" else ps2
        v1 = po["lw"] == 0 or po["left"].replace(" ", "").endswith(",0)") or po["left"] == "transparent"
        rows.append("V1w window panel open: left edge %s %.0f px %s" % (po["left"], po["lw"], "OK" if v1 else "RED"))
        if not v1: fails.append("V1w open panel keeps its left edge line %s" % po["left"])
        # P1 / M1 (stand-in after the contract where JS has not drawn them)
        s = pg.evaluate(STAND)
        gp, mk = s["grip"], s["marker"]
        f = []
        if abs(gp["w"] - gp["h"]) > 0.5 or gp["rad"] not in ("50%",) and not (gp["rad"].endswith("px") and float(gp["rad"][:-2]) >= gp["w"] / 2 - 0.5):
            f.append("grip not round %s" % gp)
        if gp["ring"] != gp["accent"] or gp["bw"] < 1: f.append("grip ring %s (accent %s)" % (gp["ring"], gp["accent"]))
        if not (8 <= gp["w"] <= 40): f.append("grip size %.1f" % gp["w"])
        rows.append("P1 window grip%s: %s %s" % (" (stand-in)" if "grip" in s["stand"] else "", gp, "OK" if not f else "RED"))
        fails += ["P1: %s" % x for x in f]
        f = []
        if abs(mk["w"] - mk["h"]) > 0.5 or mk["w"] < 6: f.append("marker not round %s" % mk)
        if mk["glow"] in ("none", ""): f.append("marker without glow")
        if mk["after"] in ("none", "normal"): f.append("marker without trail (::after)")
        if mk["a0"] > 0.1: f.append("trail visible at rest (%.2f)" % mk["a0"])
        pg.evaluate("() => { document.querySelector('.nbrw-marker').classList.add('is-moving'); }"); pg.wait_for_timeout(250)
        a_on = pg.evaluate("() => parseFloat(getComputedStyle(document.querySelector('.nbrw-marker'), '::after').opacity)")
        pg.evaluate("() => { document.querySelector('.nbrw-marker').classList.remove('is-moving'); }"); pg.wait_for_timeout(750)
        a_off = pg.evaluate("() => parseFloat(getComputedStyle(document.querySelector('.nbrw-marker'), '::after').opacity)")
        if a_on < 0.9: f.append("trail while moving %.2f" % a_on)
        if a_off > 0.1: f.append("trail 0.7 s after %.2f" % a_off)
        rows.append("M1 window marker%s: %.1f x %.1f, glow %s, trail on %.2f / after %.2f %s"
                    % (" (stand-in)" if "marker" in s["stand"] else "", mk["w"], mk["h"], "yes" if mk["glow"] not in ("none", "") else "no",
                       a_on, a_off, "OK" if not f else "RED"))
        fails += ["M1: %s" % x for x in f]
        if shots:
            pg.evaluate("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = 0; }"); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(shots, "E31-css-T2-fenster-dokument-hell.png"))
        b.close()

# ------------------------------------------------------------------- Lab ----
FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
LSIZE = r"""() => { """ + FRONT + r"""
  var Z = function(e){ var z = 1; for (var x = e; x; x = x.parentElement) z *= parseFloat(getComputedStyle(x).zoom) || 1; return z; };
  var vis = function(e){ var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  var first = function(s, f){ return [].filter.call(P.querySelectorAll(s), function(e){ return vis(e) && (!f || f(e)); })[0] || null; };
  var fs = function(e){ return e ? parseFloat(getComputedStyle(e).fontSize) * Z(e) : null; };
  var hd = function(c){ return first('.' + c + ' > .jupyter-widget-Collapse > .jupyter-widget-Collapse-header, .' + c + ' > .lm-Collapse > .lm-Collapse-header'); };
  var fm = first('svg.dmath');
  var tip = document.querySelector('.nbtip');
  return {fsv: window.__nbFontSize ? window.__nbFontSize() : null,
    text: fs(first('.nbbox-concept')), check: fs(first('button.jupyter-button', function(e){ return /Check/.test(e.textContent) && !e.classList.contains('nbskipnow'); })),
    skip: fs(first('button.nbskipnow')), icode: fs(first('.nbbox code')), code: fs(first('.codearea textarea')),
    chap: fs(hd('acc-chapter')), sect: fs(hd('acc-group')), fold: fs(hd('acc-viz') || hd('acc-practice')),
    td: fs(first('.jp-OutputArea-output td')), readout: fs(first('.widget-readout')),
    formula: fm ? fm.getBoundingClientRect().height : null, tip: tip ? parseFloat(getComputedStyle(tip).fontSize) : null}; }"""

def lab_rows(nb, shots, rows, fails):
    import shutil
    import lab_keys as K
    import css_e21 as C
    import css_e22_8 as E8
    base, root = K.ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899"))
    name = "css_e31_" + os.path.basename(nb); shutil.copy(nb, os.path.join(root, name))
    C.NB, C.LAB = name, base
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx, pg, errs = C.open_nb(b)
        pg.evaluate(C.SET, ["minimal", "light"]); pg.wait_for_timeout(900)
        pg.evaluate("() => { " + FRONT + " P.querySelectorAll('.jupyter-widget-Collapse:not(.jupyter-widget-Collapse-open) > .jupyter-widget-Collapse-header').forEach(function(h){ h.click(); }); }")
        pg.wait_for_timeout(1500)
        # N1
        m = pg.evaluate("() => { " + FRONT + " var s = P.querySelector('.jp-WindowedPanel-outer'), c = getComputedStyle(s); return [c.maskImage || 'none', c.webkitMaskImage || 'none']; }")
        ok = all(x == "none" for x in m)
        rows.append("N1 Lab scroller mask %s %s" % (m[0][:60], "OK" if ok else "RED"))
        if not ok: fails.append("N1 fade mask on the document %s" % m[0][:80])
        # F1 — hover a titled element of the document once, so the hover box exists
        pg.evaluate("() => { " + FRONT + " var e = P.querySelector('.jp-OutputArea-output [title]'); if (e) { e.dispatchEvent(new MouseEvent('mouseover', {bubbles: true})); e.dispatchEvent(new MouseEvent('mouseout', {bubbles: true})); } }")
        pg.wait_for_timeout(300)
        FS = "(v) => { window.__nbFontSize(v); }"
        pg.evaluate(FS, 100); pg.wait_for_timeout(900)
        b100 = pg.evaluate(LSIZE)
        got = {}
        for v in (90, 150):
            pg.evaluate(FS, v); pg.wait_for_timeout(900); got[v] = pg.evaluate(LSIZE)
        if shots:
            os.makedirs(shots, exist_ok=True)
            pg.evaluate("() => { " + FRONT + " var b = P.querySelector('button.nbskipnow'), SC = P.querySelector('.jp-WindowedPanel-outer'); if (b) SC.scrollTop += b.getBoundingClientRect().top - 420; }")
            pg.wait_for_timeout(700); pg.screenshot(path=os.path.join(shots, "E31-css-F1-lab-A150-hell.png"))
        pg.evaluate(FS, 100); pg.wait_for_timeout(900)
        ratio_rows("F1 Lab", b100, got, rows, fails, ["check", "skip", "icode", "code", "chap", "sect", "fold", "td", "readout", "formula", "tip"])
        if b100.get("skip") and b100.get("check") and abs(b100["skip"] - b100["check"]) > 0.05:
            fails.append("F1 Lab Skip %.2f px beside Check %.2f px" % (b100["skip"], b100["check"]))
        # G1
        # with js-E31 its own control (it keeps --nbgs and puts it back every pass); without it the contract's variable
        GSJ = ("(v) => { if (window.__nbGuiSize) { window.__nbGuiSize(v === null ? 100 : Math.round(v * 100)); return; }"
               " [document.documentElement, document.getElementById('nbpanel-root')].forEach(function(e){ if (v === null) e.style.removeProperty('--nbgs'); else e.style.setProperty('--nbgs', String(v)); }); }")
        Q = "() => { " + FRONT + " var t = document.querySelector('#nbpanel-root .nbcorner .nbbtn.nbtheme'), r = t.getBoundingClientRect(); return {w: r.width, h: r.height, text: parseFloat(getComputedStyle(P.querySelector('.nbbox-concept')).fontSize)}; }"
        g0 = pg.evaluate(Q); pg.evaluate(GSJ, 1.3); pg.wait_for_timeout(1800); g1 = pg.evaluate(Q)
        pg.click("#nbpanel-root .nbcorner .nbbtn.nbgear"); pg.wait_for_timeout(900)
        dz = pg.evaluate("() => { var d = document.querySelector('#nbpanel-root .nbdrawer > .nbdrawer-grid') || document.querySelector('#nbpanel-root .nbdrawer > *'); return d ? parseFloat(getComputedStyle(d).zoom) : null; }")
        if shots:
            pg.screenshot(path=os.path.join(shots, "E31-css-G1-lab-130-hell.png"))
        pg.click("#nbpanel-root .nbcorner .nbbtn.nbgear"); pg.wait_for_timeout(600)
        pg.evaluate(GSJ, None); pg.wait_for_timeout(400)
        f = []
        if abs(g1["h"] - g0["h"] * 1.3) > 1 or abs(g1["w"] - g0["w"] * 1.3) > 1: f.append("tool button %.1fx%.1f → %.1fx%.1f (x1.3)" % (g0["w"], g0["h"], g1["w"], g1["h"]))
        if abs(g1["text"] - g0["text"]) > 0.05: f.append("document text %.2f → %.2f" % (g0["text"], g1["text"]))
        if dz is None or abs(dz - 1.3) > 0.01: f.append("drawer content zoom %s" % dz)
        rows.append("G1 Lab --nbgs 1.3: button %.1fx%.1f → %.1fx%.1f, text %.2f → %.2f, drawer zoom %s %s"
                    % (g0["w"], g0["h"], g1["w"], g1["h"], g0["text"], g1["text"], dz, "OK" if not f else "RED"))
        fails += ["G1 Lab: %s" % x for x in f]
        # V1 — cyber dark, lens 200, mouse on the lens slider, panel pulled open
        pg.evaluate(C.SET, ["cyber", "dark"]); pg.evaluate(E8.ZOOM, 200); pg.wait_for_timeout(1500)
        r = pg.evaluate("() => { var s = document.querySelector('#nbpanel-root .nbzoomgrp .nbslider').getBoundingClientRect(); return [s.right - 6, s.top + s.height / 2]; }")
        pg.mouse.click(r[0], r[1]); pg.wait_for_timeout(700)
        gr = pg.evaluate("() => { var g = document.querySelector('#nbpanel-root .nbgrip').getBoundingClientRect(); return [g.left + g.width / 2, g.top + g.height / 2]; }")
        pg.mouse.click(gr[0], gr[1]); pg.wait_for_timeout(1500)
        v = pg.evaluate("""() => { var h = document.getElementById('nbpanel-root'), r = h.querySelector('.nbrail'), cs = getComputedStyle(r), rr = r.getBoundingClientRect();
          var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), t = P.querySelector('.nbtitle-card').getBoundingClientRect();
          return {kbd: h.classList.contains('nbkbd'), open: h.classList.contains('nbnames') || h.getAttribute('data-names') === '1',
                  outline: cs.outlineStyle === 'none' ? 'none' : cs.outlineWidth + ' ' + cs.outlineColor, left: cs.borderLeftColor, lw: parseFloat(cs.borderLeftWidth),
                  inset: /inset/.test(cs.boxShadow) && /inset -?2px 0px 0px/.test(cs.boxShadow.replace(/rgba?\\([^)]*\\)|color\\([^)]*\\)/g, '')) ? 'side' : 'none',
                  edge: Math.round(rr.left), axis: Math.round(t.left + t.width / 2)}; }""")
        line = v["outline"] != "none" or not (v["lw"] == 0 or v["left"].replace(" ", "").endswith(",0)"))
        rows.append("V1 Lab cyber dark, lens 200, slider clicked, panel open: %s %s" % (v, "OK" if not line else "RED"))
        if line: fails.append("V1 a line down the open panel's left edge (x %d, axis %d): outline %s, border %s" % (v["edge"], v["axis"], v["outline"], v["left"]))
        if not v["open"]: fails.append("V1 panel did not open (test)")
        if shots:
            pg.screenshot(path=os.path.join(shots, "E31-css-V1-lab-cyber-dunkel.png"))
        pg.mouse.click(gr[0], gr[1]); pg.wait_for_timeout(800)
        pg.evaluate(E8.ZOOM, 100); pg.evaluate(C.SET, ["minimal", "light"]); pg.wait_for_timeout(800)
        if errs: fails.append("Lab: page errors %s" % errs[:3])
        b.close()

def main():
    import nbpick
    nb = nbpick.from_argv(sys.argv)
    shots = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
    rows, fails = [], []
    outs, errs, _ = run_cell(nb, {})
    if errs: print("kernel errors:", errs[:3])
    rd = [o for o in outs if "nbreading" in (o["data"].get("text/html") or "")]
    if not rd:
        print("FAIL no reading output"); print("REGRESS-CSS-E31 RED"); return 1
    window_rows(rd[0]["data"]["text/html"], shots, rows, fails)
    if "--no-lab" not in sys.argv:
        lab_rows(nb, shots, rows, fails)
    print("\n".join(rows))
    for x in fails: print("FAIL", x)
    print("REGRESS-CSS-E31", "OK" if not fails else "RED")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.exit(main())
