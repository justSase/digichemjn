"""E30 · CSS — Werkstatt CSS, 12.10. (Nutzer: PyCharm-Bilder Complex v1.75; Wortlaut plan/STOP.md
„NÄCHSTE RUNDE E30“). Real kernel + real 20-reader.js for the reading window (every output a page of
its own, PyCharm), real JupyterLab under Playwright for the Lab rows. Everything read off the page.

    python3 tests/regress/css_e30.py [notebook.ipynb] [--shots DIR] [--no-lab]

Lab reference (Vorlage v1.76, JupyterLab 4.6, 1366 x 760, minimal light, file browser open, measured
12.10.): column 912, title card 720, prose boxes <= 848 (94 % of their 902 box), code field 780,
slider row ~440 + plot 660 without frame, lock card 562 wide / 26 px padding, fold pills as wide as
their text, tables without grid; text 14.3 px (E29 D7), chapter 19.76, section 10.14, fold 9.88,
title 31.57, cover 14 px (unchanged by D7).
  A1  conclusion as prose (stand-in after claude/VERTRAG-E30-py.md where the notebook carries no
      `.nbconcl` yet; Python's inline paragraph gap .85em in the stand-in too): justified, hyphens auto,
      no gap between paragraphs, the 2nd indented (> 0), the 1st and the one after "Outlook" not,
      measure <= 40 em + padding, on the axis (<= 1 px) — Lab and window.
  A2  no accordion triangle: Lab (document + cover: pill ::before border triangle, ▸/▾ glyphs, the
      <summary> marker of "Timeline") and window (summary ::after/marker), minimal light + cyber dark.
  B1  window cover, "What you will learn" open: headings, goal list, chapter list, time on the axis
      (<= 1 px); chapters in ONE column (all items share one left edge).
  B3  window 1366: column <= 912 (+1); title card 720 (+-2); prose box <= 848 (+2); fold pill / chapter
      heading as wide as the text (< 420) and on the axis; slider without frame, range row and plot on
      the axis; task as wide as its content (< column), code field <= 780 (+2).
  B4  tables: no grid (border of a cell without own border = 0), on the axis, never cut (narrow
      window: the table rolls in itself or fits — no part outside the window).
  B5  760 / 1024 / 1366 x light / dark: the window and its panel inside the viewport, every visible
      element of the document inside the column (+-1), locked chapters not pushed together (heading
      to heading >= 150 px; the lock card >= 90 px high).
  L1  window font as Lab after E29 D7: base 14.3, box 14.3, chapter 19.76, section 10.14, fold 9.88,
      title 31.57 (+-0.3); the cover card 14 (Lab cover, +-0.3).
Gegenprobe v1.76 (961427cc, Vorlage): red in A1, A2, B1, B3, B4, L1 (chronicle 12.10., Werkstatt CSS).
exit 0 = REGRESS-CSS-E30 OK."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from env_iframe import run_cell

CHROME = os.environ.get("DIGICHEM_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

STAND = ("<div><p class='%snbconcl-p' style='margin:0 0 .85em'>Placeholder: the first paragraph sums the chapters up in prose, the way a paper closes, and "
         "says how the ideas hang together, which assumption carried the argument and where it breaks down.</p>"
         "<p class='%snbconcl-p %snbconcl-ctx' style='margin:0 0 .85em'>Placeholder: the second paragraph places the result: what it explains, what it leaves open, and "
         "how it connects with what the reader already knows from neighbouring subjects of the course.</p>"
         "<div class='%snbconcl-h' style='font-weight:700'>Outlook</div><p class='%snbconcl-p %snbconcl-out'>Placeholder: where the next notebook "
         "picks this up and which question it answers with the tools built here.</p></div>")

# ---------------------------------------------------------------- window ----
OPEN = r"""([theme, skin]) => { var rw = document.querySelector('.nbrw'); if (!rw) return 'no window';
  var p = rw.querySelector('.nbrw-cover [data-nbrw-act=play]'); if (p && rw.getAttribute('data-nbrw-view') === 'cover') p.click();
  if (theme) rw.setAttribute('data-nbrw-theme', theme); if (skin) rw.setAttribute('data-nbrw-skin', skin); return 'ok'; }"""

TRI_W = r"""() => { var rw = document.querySelector('.nbrw'), n = [];
  var re = /[▶▸▾▼▴◂]/;
  rw.querySelectorAll('summary').forEach(function(s){
    var a = getComputedStyle(s, '::after'), b = getComputedStyle(s, '::before'), m = getComputedStyle(s, '::marker');
    [a, b].forEach(function(c){ if (c.display !== 'none' && re.test(c.content || '')) n.push((s.className || 'summary') + ' ' + c.content); });
    if (getComputedStyle(s).display === 'list-item' && getComputedStyle(s).listStyleType !== 'none' && m.content !== '""') n.push((s.className || 'summary') + ' marker');
  });
  return n; }"""

GEOM = r"""() => { var rw = document.querySelector('.nbrw'), win = rw.querySelector('.nbrw-win');
  rw.querySelectorAll('details').forEach(function(d){ d.open = true; });
  var cs = getComputedStyle(win), wr = win.getBoundingClientRect(), pl = parseFloat(cs.paddingLeft), pr = parseFloat(cs.paddingRight);
  var colL = wr.left + pl, colR = wr.right - pr, rd = rw.querySelector('.nbrw-win > .nbreading'), rr = rd.getBoundingClientRect();
  var mid = (rr.left + rr.right) / 2, o = {col: Math.round(rr.width), colAvail: Math.round(colR - colL), mid: Math.round((mid - (colL + colR) / 2) * 10) / 10};
  var vis = function(e){ var r = e.getBoundingClientRect(); if (!(r.width > 0 && r.height > 0)) return false;
    for (var x = e; x && x !== rw; x = x.parentElement) { var s = getComputedStyle(x); if (s.display === 'none' || s.visibility === 'hidden') return false; } return true; };
  var W = function(sel){ var L = []; rw.querySelectorAll(sel).forEach(function(e){ if (!vis(e)) return; var r = e.getBoundingClientRect();
    L.push({w: Math.round(r.width * 10) / 10, h: Math.round(r.height), off: Math.round((r.left + r.width / 2 - mid) * 10) / 10, top: r.top, e: e}); }); return L; };
  var strip = function(L){ return L.map(function(x){ return {w: x.w, h: x.h, off: x.off}; }); };
  o.card = strip(W('.nbrw-doc .nbr-nbtitle-card, .nbrw-win > .nbreading > div > .nbr-nbtitle-card').slice(0, 1));
  o.box = strip(W('.nbr-nbbox'));
  o.pill = strip(W('details.nbrw-acc > summary > .nbread-h'));
  var sl = W('.nbrw-slider'); o.slider = sl.map(function(x){ var s = getComputedStyle(x.e), r = x.e.querySelector('.nbrw-range'), f = x.e.querySelector('.nbrw-fig img, .nbrw-fig svg');
    var rr2 = r && r.getBoundingClientRect(), v = x.e.querySelector('.nbrw-val'), vr = v && v.getBoundingClientRect(), fr = f && f.getBoundingClientRect();
    var rowMid = rr2 && vr ? (Math.min(rr2.left, vr.left) + Math.max(rr2.right, vr.right)) / 2 - mid : null;
    return {border: s.borderTopWidth + ' ' + s.borderTopStyle, rowOff: rowMid === null ? null : Math.round(rowMid * 10) / 10,
            figOff: fr ? Math.round((fr.left + fr.width / 2 - mid) * 10) / 10 : null}; });
  o.task = strip(W('.nbrw-task')); o.copy = strip(W('.nbrw-copy'));
  o.table = W('.nbreading table').map(function(x){ var t = x.e, c = t.querySelector('td');
    var own = c && /border/.test(c.getAttribute('style') || ''), b = c ? getComputedStyle(c).borderTopWidth : '0px';
    return {w: x.w, off: x.off, cellBorder: own ? 'own' : b, cut: t.getBoundingClientRect().right > colR + 1 && t.scrollWidth <= t.clientWidth + 1}; });
  var lk = W('.nbrw-lockmsg'); o.lock = lk.map(function(x){ return x.h; });
  var hs = W('h3.nbread-h').filter(function(x){ return x.e.closest('details') && x.e.closest('details').querySelector('.nbrw-lockmsg'); });
  o.lockGap = []; for (var i = 1; i < hs.length; i++) o.lockGap.push(Math.round(hs[i].top - hs[i - 1].top));
  // B5: inside the viewport, everything of the document inside the column
  var R = rw.getBoundingClientRect(), pn = rw.querySelector('.nbrw-panel'), pr2 = pn.getBoundingClientRect();
  o.vp = {right: Math.round(R.right), vw: document.documentElement.clientWidth, panelR: Math.round(pr2.right), rwR: Math.round(R.right)};
  var out = []; rd.querySelectorAll('*').forEach(function(e){ if (/^(SCRIPT|STYLE|TR|TBODY|TD|TH)$/.test(e.tagName)) return;
    if (e.closest('.nbrw-cover') || e.closest('table')) return; if (!vis(e)) return; var r = e.getBoundingClientRect();
    if (r.left < colL - 1 || r.right > colR + 1) { if (out.length < 5) out.push((e.className || e.tagName).toString().slice(0, 30) + ' ' + Math.round(r.left) + '..' + Math.round(r.right)); } });
  o.outside = out; o.colLR = [Math.round(colL), Math.round(colR)];
  return o; }"""

FONT = r"""() => { var rw = document.querySelector('.nbrw'), rd = rw.querySelector('.nbrw-win > .nbreading');
  var fs = function(s, root){ var e = (root || rd).querySelector(s); return e ? Math.round(parseFloat(getComputedStyle(e).fontSize) * 100) / 100 : -1; };
  var doc = rd.querySelector('.nbrw-doc') || rd;
  return {base: Math.round(parseFloat(getComputedStyle(rd).fontSize) * 100) / 100, box: fs('.nbr-nbbox'), chap: fs('h3.nbread-h'), sec: fs('h2.nbread-h'), fold: fs('h4.nbread-h, h5.nbread-h'),
          title: fs('.nbr-nbtitle-h', doc.querySelector('.nbr-nbtitle-card') ? doc : rd), cover: fs('.nbrw-cover .nbr-nbtitle-card')}; }"""

COVER = r"""() => { var rw = document.querySelector('.nbrw');
  if (window.__nbReader && window.__nbReader.show) window.__nbReader.show('cover'); rw.setAttribute('data-nbrw-view', 'cover');
  var cv = rw.querySelector('.nbrw-cover'); cv.querySelectorAll('details').forEach(function(d){ d.open = true; });
  var vis = function(e){ return e && e.getBoundingClientRect().width > 0 && e.offsetParent !== null; };
  var card = [].filter.call(cv.querySelectorAll('.nbr-nbtitle-card'), vis)[0]; if (!card) return {err: 'no card'};
  var c = card.getBoundingClientRect(), mid = c.left + c.width / 2;
  var ink = function(e){ var l = 1e9, r = -1e9, w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT), n;
    while ((n = w.nextNode())) { if (!n.textContent.trim()) continue; var g = document.createRange(); g.selectNodeContents(n);
      [].forEach.call(g.getClientRects(), function(q){ if (q.width > 0) { l = Math.min(l, q.left); r = Math.max(r, q.right); } }); }
    return l < r ? Math.round(((l + r) / 2 - mid) * 10) / 10 : null; };
  var o = {};
  ['.nbr-nbtitle-facts-h', '.nbr-nbtitle-goals', '.nbr-nbtitle-chaps', '.nbr-nbtitle-time'].forEach(function(s){
    var e = [].filter.call(cv.querySelectorAll(s), vis)[0]; if (!e) { o[s] = null; return; }
    var r = e.getBoundingClientRect(); o[s] = {box: Math.round((r.left + r.width / 2 - mid) * 10) / 10, ink: ink(e)}; });
  var ch = [].filter.call(cv.querySelectorAll('.nbr-nbtitle-chap'), vis).map(function(e){ return Math.round(e.getBoundingClientRect().left); });
  o.chapLefts = ch.filter(function(v, i, a){ return a.indexOf(v) === i; }).length;
  o.chapN = ch.length;
  return o; }"""

CONCL = r"""([html, pre]) => { var rw = document.querySelector('.nbrw'), rd = rw ? rw.querySelector('.nbrw-win > .nbreading') : null;
  var root = rd || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var c = root.querySelector('.' + pre + 'nbconcl'), stand = false;
  if (!c) { stand = true; var host = [].slice.call(root.querySelectorAll(rd ? '.nbr-nbbox' : '.nbbox')).filter(function(e){ return e.getBoundingClientRect().width > 0; }).pop();
    c = document.createElement('div'); c.className = pre + 'nbbox ' + pre + 'nbbox-concept ' + pre + 'nbconcl'; c.setAttribute('lang', 'en'); c.innerHTML = html;
    host.parentNode.insertBefore(c, host.nextSibling); }
  if (rd) rd.querySelectorAll('details').forEach(function(d){ d.open = true; });
  var ps = c.querySelectorAll('.' + pre + 'nbconcl-p'), cs = getComputedStyle(c), r = c.getBoundingClientRect();
  var col = (rd || c.parentElement).getBoundingClientRect(), mid = (col.left + col.right) / 2;
  if (!rd) { var t = root.querySelector('.nbtitle-card').getBoundingClientRect(); mid = t.left + t.width / 2; }
  var p0 = getComputedStyle(ps[0]), p1 = ps[1] ? getComputedStyle(ps[1]) : null;
  var p2 = ps[2] ? getComputedStyle(ps[2]) : null, gap = ps[1] ? Math.round(ps[1].getBoundingClientRect().top - ps[0].getBoundingClientRect().bottom) : -1;
  return {stand: stand, align: p0.textAlign, hyph: p0.hyphens || p0.webkitHyphens, ind0: parseFloat(p0.textIndent), ind1: p1 ? parseFloat(p1.textIndent) : -1,
          indOut: p2 ? parseFloat(p2.textIndent) : -1, gap: gap,
          w: Math.round(r.width), em: parseFloat(cs.fontSize), off: Math.round((r.left + r.width / 2 - mid) * 10) / 10}; }"""

def page(html, dark):
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:%s;color:%s'>%s"
            % ("#2b2d30" if dark else "#ffffff", "#dfe1e5" if dark else "#1f2328", html))

def concl_ok(c):
    return (c and c["align"] == "justify" and c["hyph"] == "auto" and c["ind0"] == 0 and c["ind1"] > 0 and c["indOut"] == 0
            and c["gap"] <= 1 and c["w"] <= 40 * c["em"] + 48 + 1 and abs(c["off"]) <= 1)

def window_rows(html, shots, rows, fails):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        # L1 / B3 / B4 / A2 / A1 / B1 at 1366 x 760, minimal light
        for theme, skin in (("light", "minimal"), ("dark", "cyber")):
            ctx = b.new_context(viewport={"width": 1366, "height": 760}, color_scheme=theme)
            pg = ctx.new_page(); pg.set_content(page(html, theme == "dark")); pg.wait_for_timeout(700)
            tag = "window %s %s" % (skin, theme); f = []
            st = pg.evaluate(OPEN, [theme, skin]); pg.wait_for_timeout(300)
            if st != "ok": fails.append("%s: %s" % (tag, st)); ctx.close(); continue
            tri = pg.evaluate(TRI_W)
            if tri: f.append("A2 triangles %s" % tri[:4])
            if skin == "minimal":
                F = pg.evaluate(FONT)
                want = dict(base=14.3, box=14.3, chap=19.76, sec=10.14, fold=9.88, title=31.57, cover=14.0)
                bad = {k: F[k] for k in want if abs(F[k] - want[k]) > 0.3}
                if bad: f.append("L1 font %s (Lab %s)" % (bad, {k: want[k] for k in bad}))
                g = pg.evaluate(GEOM)
                if g["col"] > 912 + 1: f.append("B3 column %d > 912" % g["col"])
                if not g["card"] or abs(g["card"][0]["w"] - 720) > 2: f.append("B3 title card %s (Lab 720)" % g["card"])
                wide = [x["w"] for x in g["box"] if x["w"] > 848 + 2]
                if wide: f.append("B3 boxes %s > 848" % wide[:4])
                pl = [x for x in g["pill"] if x["w"] >= 420 or abs(x["off"]) > 1]
                if pl: f.append("B3 fold heads %s (as wide as the text, on the axis)" % pl[:3])
                for s in g["slider"]:
                    if s["border"].split()[1] != "none" and not s["border"].startswith("0px"): f.append("B3 slider frame %s" % s["border"])
                    if s["rowOff"] is not None and abs(s["rowOff"]) > 1: f.append("B3 slider row off %.1f" % s["rowOff"])
                    if s["figOff"] is not None and abs(s["figOff"]) > 1: f.append("B3 plot off %.1f" % s["figOff"])
                tk = [x for x in g["task"] if x["w"] >= g["col"] - 2 or abs(x["off"]) > 1]
                if tk: f.append("B3 task %s (fit content, on the axis)" % tk[:3])
                cp = [x["w"] for x in g["copy"] if x["w"] > 780 + 2]
                if cp: f.append("B3 code field %s > 780" % cp)
                tb = [t for t in g["table"] if t["cellBorder"] not in ("0px", "own") or abs(t["off"]) > 1]
                if tb: f.append("B4 tables %s" % tb[:3])
                c = pg.evaluate(CONCL, [STAND % (("nbr-",) * 6), "nbr-"])
                if not concl_ok(c): f.append("A1 conclusion %s" % c)
                rows.append("%s: col %d · card %s · boxes max %s · pills max %s · task %s · code %s · tables %s · font %s · concl %s"
                            % (tag, g["col"], g["card"][0]["w"] if g["card"] else None, max([x["w"] for x in g["box"]] or [0]),
                               max([x["w"] for x in g["pill"]] or [0]), [x["w"] for x in g["task"]][:2], [x["w"] for x in g["copy"]][:2],
                               [(t["w"], t["cellBorder"]) for t in g["table"]][:3], F, {k: c[k] for k in ("stand", "align", "ind1", "indOut", "gap", "w", "off")}))
                if shots:
                    os.makedirs(shots, exist_ok=True)
                    pg.evaluate("() => { var w = document.querySelector('.nbrw-win'), s = document.querySelector('.nbrw-slider'); w.scrollTop += s.getBoundingClientRect().top - w.getBoundingClientRect().top - 140; }")
                    pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(shots, "E30-css-fenster-regler-hell.png"))
                cv = pg.evaluate(COVER); pg.wait_for_timeout(150)
                bad = {k: v for k, v in cv.items() if k.startswith(".") and (v is None or abs(v["box"]) > 1 or (v["ink"] is not None and abs(v["ink"]) > 1 and k != ".nbr-nbtitle-goals"))}
                if bad or cv.get("chapLefts") != 1: f.append("B1 cover %s, chapter columns %s" % (bad or cv, cv.get("chapLefts")))
                rows.append("%s: B1 cover %s" % (tag, cv))
                if shots:
                    pg.evaluate("() => { var w = document.querySelector('.nbrw-win'), e = document.querySelector('.nbrw-cover .nbr-nbtitle-facts'); w.scrollTop += e.getBoundingClientRect().top - w.getBoundingClientRect().top - 120; }")
                    pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(shots, "E30-css-fenster-vorschau-hell.png"))
            fails += ["%s: %s" % (tag, x) for x in f]
            if not f: rows.append("%s: A2/A1/B1/B3/B4/L1 OK" % tag)
            ctx.close()
        # B5 / B4 (not cut) — three widths x light/dark
        for vw in (760, 1024, 1366):
            for theme in ("light", "dark"):
                ctx = b.new_context(viewport={"width": vw, "height": 760}, color_scheme=theme)
                pg = ctx.new_page(); pg.set_content(page(html, theme == "dark")); pg.wait_for_timeout(700)
                pg.evaluate(OPEN, [theme, "minimal"]); pg.wait_for_timeout(300)
                g = pg.evaluate(GEOM); tag = "window %d %s" % (vw, theme); f = []
                v = g["vp"]
                if v["rwR"] > v["vw"] or v["panelR"] > v["rwR"]: f.append("B5 out of the viewport %s" % v)
                if g["outside"]: f.append("B5 outside the column %s %s" % (g["colLR"], g["outside"]))
                if abs(g["mid"]) > 1: f.append("B5 column off the axis %.1f" % g["mid"])
                cut = [t for t in g["table"] if t["cut"]]
                if cut: f.append("B4 table cut %s" % cut)
                if g["lock"] and min(g["lock"]) < 90: f.append("B5 lock card %s px high (Lab 180)" % g["lock"])
                if g["lockGap"] and min(g["lockGap"]) < 150: f.append("B5 locked chapters %s px apart" % g["lockGap"])
                rows.append("%s: col %d/%d mid %.1f · viewport %s · lock %s gap %s · outside %d %s"
                            % (tag, g["col"], g["colAvail"], g["mid"], v, g["lock"][:2], g["lockGap"][:3], len(g["outside"]), "OK" if not f else "RED"))
                if shots and vw == 1024 and theme == "dark":
                    pg.evaluate("() => { var w = document.querySelector('.nbrw-win'), e = document.querySelectorAll('.nbrw-lockmsg')[0]; if (e) w.scrollTop += e.getBoundingClientRect().top - w.getBoundingClientRect().top - 160; }")
                    pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(shots, "E30-css-fenster-gesperrt-dunkel-1024.png"))
                fails += ["%s: %s" % (tag, x) for x in f]
                ctx.close()
        b.close()

# ------------------------------------------------------------------- Lab ----
TRI_L = r"""() => { window.__nbCoverShow && window.__nbCoverShow(true);
 return new Promise(function(res){ setTimeout(function(){ var out = [], re = /[▶▸▾▼▴◂]/;
  document.querySelectorAll('.jp-NotebookPanel *').forEach(function(e){
   ['::before', '::after'].forEach(function(ps){ var c = getComputedStyle(e, ps); if (c.content === 'none' || c.display === 'none') return;
     var ch = re.test(c.content), bt = parseFloat(c.width) === 0 && parseFloat(c.borderLeftWidth) > 2 && /0, 0, 0, 0|transparent/.test(c.borderTopColor);
     if (ch || bt) out.push(String(e.className).slice(0, 40) + ps + (ch ? c.content : ' border-triangle')); });
   if (e.tagName === 'SUMMARY' && getComputedStyle(e).display === 'list-item' && getComputedStyle(e).listStyleType !== 'none'
       && getComputedStyle(e, '::marker').content !== '""') out.push(e.className + ' marker ' + getComputedStyle(e).listStyleType);
  });
  window.__nbCoverShow && window.__nbCoverShow(false); res(out); }, 1500); }); }"""

def lab_rows(nb, shots, rows, fails):
    import shutil
    import lab_keys as K
    import css_e21 as C
    base, root = K.ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899"))
    name = "css_e30_" + os.path.basename(nb); shutil.copy(nb, os.path.join(root, name))
    C.NB, C.LAB = name, base
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx, pg, errs = C.open_nb(b)
        for skin, theme in (("minimal", "light"), ("cyber", "dark"), ("fairy", "light")):
            pg.evaluate(C.SET, [skin, theme]); pg.wait_for_timeout(900)
            pg.evaluate("() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); P.querySelectorAll('.jupyter-widget-Collapse:not(.jupyter-widget-Collapse-open) > .jupyter-widget-Collapse-header').forEach(function(h){ h.click(); }); }")
            pg.wait_for_timeout(1200)
            tri = pg.evaluate(TRI_L); tag = "Lab %s %s" % (skin, theme)
            if tri: fails.append("%s: A2 triangles %s" % (tag, tri[:5]))
            rows.append("%s: A2 triangles %d %s" % (tag, len(tri), "OK" if not tri else "RED"))
        pg.evaluate(C.SET, ["minimal", "light"]); pg.wait_for_timeout(900)
        c = pg.evaluate(CONCL, [STAND % (("",) * 6), ""])
        rows.append("Lab minimal light: A1 conclusion %s %s" % (c, "OK" if concl_ok(c) else "RED"))
        if not concl_ok(c): fails.append("Lab: A1 conclusion %s" % c)
        if shots:
            pg.evaluate("() => { var c = document.querySelector('.nbconcl'), SC = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); SC.scrollTop += c.getBoundingClientRect().top - 260; }")
            pg.wait_for_timeout(600); pg.screenshot(path=os.path.join(shots, "E30-css-lab-fazit-hell.png"))
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
        print("FAIL no reading output"); print("REGRESS-CSS-E30 RED"); return 1
    window_rows(rd[0]["data"]["text/html"], shots, rows, fails)
    if "--no-lab" not in sys.argv:
        lab_rows(nb, shots, rows, fails)
    print("\n".join(rows))
    for x in fails: print("FAIL", x)
    print("REGRESS-CSS-E30", "OK" if not fails else "RED")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.exit(main())
