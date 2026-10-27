"""E33 · CSS — Werkstatt CSS, 13.10. abends (Nutzer zu v1.78 in PyCharm, VS Code, Lab, Lite; Wortlaut
plan/STOP.md „E33 — GILT JETZT“). Vertrag claude/VERTRAG-E33-css.md. Real kernel + real 20-reader.js for the
window (the reading output in a page of its own, PyCharm/VS Code), real JupyterLab for C1 and the saved file.
Where the JS or Python half of the contract is not in the page yet, the test sets it in as the contract writes
it (stand-in; the row says so) — the row then measures the CSS alone.

    python3 tests/regress/css_e33.py [notebook.ipynb] [--shots DIR] [--no-lab] [--static]

Window (1400 x 900, minimal light):
  D1   ▶ Play (bottom of its circle) inside the first window view (600 px), 1400 and 1366 wide.
  B2   preview timeline: dot under the pointer (.is-hov) grows and glows; the info box (.nbrw-cv-desc[data-on],
       js contract) on the axis (±1 px), name alone and centred in line 1, text under it; showing it moves
       nothing below (0 px); without [data-on] it is not seen.
  B4   slider + value as a pair on the axis (±2 px), the value box not stretched; the figure on the axis.
  B5   GUI size (⊖/⊕, --nbgs 1.3): tool buttons x1.3; panel names / progress / chapter / hover box unchanged
       (±0.1 px; JS's inline gs sizes and gs panel width taken out as js-E33 does); --nbrw-pk 1.5 (js-E33:
       lens x panel width) → progress, chapter, hover box x1.5 (±3 %), the names' font x1 (JS scales the marks).
  B6   every tool button (also ⌨ ⚙ ✎ 👤 ✉, .nbrw-tool; stand-ins where js-E33 is not in) a square of the same size with its own surface;
       a drawer (.nbrw-drawer stand-in) with own surface, edge, shadow, checked button in the accent.
  D2   VS Code (js-E33 sets [data-nbrw-host=vscode] + theme): dark → ground = --vscode-editor-background, ink
       contrast ≥ 4.5; light likewise; ◐ chosen against the VS Code theme → our own ground.
Lab (1400 x 900, minimal light):
  C1   progress bar (.nbp-xp) at the top, chapter (.nbp-cur) at the bottom of the open panel (js-E33; stand-ins
       with its inline fallback where it is not in): own surface, text and bar in one row as in the window,
       full ink (not faded by the rail's mask: darkest pixel ≤ 140).
--static (after py-E33 is merged; the saved file, notebook NOT trusted, Lab light + dark):
  A1s  0 visible pieces of the other language; every visible text ≥ 4.5 against its ground.
Gegenprobe v1.78 (b9350b0c, Vorlage): red in D1, B2, B4, B5, B6, D2, C1 (chronicle).
exit 0 = REGRESS-CSS-E33 OK."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from env_iframe import run_cell

CHROME = os.environ.get("DIGICHEM_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
W, H = 1400, 900

def page(html, dark=False, body_cls="", body_style=""):
    return ("<!doctype html><meta charset=utf-8><body class='%s' style='margin:0;padding:8px 16px;background:%s;color:%s;%s'>%s"
            % (body_cls, "#2b2d30" if dark else "#ffffff", "#dfe1e5" if dark else "#1f2328", body_style, html))

def open_window(b, html, width=W, scheme="light", body_cls="", body_style=""):
    ctx = b.new_context(viewport={"width": width, "height": H}, color_scheme=scheme)
    body = page(html, scheme == "dark" and not body_cls, body_cls, body_style)
    ctx.route("http://nbrw.test/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=body))
    pg = ctx.new_page(); pg.goto("http://nbrw.test/"); pg.wait_for_timeout(900)
    return ctx, pg

TODOC = r"""() => { var rw = document.querySelector('.nbrw'); if (!rw) return 'no window';
  var p = rw.querySelector('.nbrw-cover [data-nbrw-act=play]'); if (p && rw.getAttribute('data-nbrw-view') === 'cover') p.click();
  return 'ok'; }"""
TOCOVER = r"""() => { var rw = document.querySelector('.nbrw'), c = rw.querySelector('[data-act=cover]');
  if (rw.getAttribute('data-nbrw-view') !== 'cover' && c) c.click(); var w = rw.querySelector('.nbrw-win'); if (w) w.scrollTop = 0; return rw.getAttribute('data-nbrw-view'); }"""

# ---- B2: the preview timeline (hover box and fold)
B2 = r"""() => { var rw = document.querySelector('.nbrw'), tl = rw.querySelector('.nbrw-cv-tl'); if (!tl) return {err: 'no timeline'};
  var w = rw.querySelector('.nbrw-win'), W0 = w.getBoundingClientRect(), mid = (W0.left + W0.right) / 2;
  var modes = rw.querySelector('.nbrw-modes'), y0 = modes.getBoundingClientRect().top, stand = [];
  var dots = [].slice.call(tl.querySelectorAll('.nbrw-cv-dot')), d = dots.filter(function(x){ return x.getAttribute('data-kind') === 'chap'; })[0] || dots[2];
  var t0 = getComputedStyle(d, '::before').transform;
  d.classList.add('is-hov');
  // js-E33: one .nbrw-cv-desc under the timeline (b name + span text), [data-on] while it speaks
  var box = tl.querySelector('.nbrw-cv-desc');
  if (!box) { box = document.createElement('div'); box.className = 'nbrw-cv-desc'; tl.appendChild(box); stand.push('desc'); }
  box.innerHTML = '<b>Chapter 1: Chapter title (placeholder)</b> <span>Chapter 1 in two sentences (placeholder).</span>';
  box.removeAttribute('hidden'); box.setAttribute('data-on', '1');
  return new Promise(function(res){ setTimeout(function(){
    var r = box.getBoundingClientRect(), b = box.querySelector('b'), s = box.querySelector('span'), cs = getComputedStyle(box);
    var t1 = getComputedStyle(d, '::before').transform, sh = getComputedStyle(d, '::before').boxShadow;
    var y1 = modes.getBoundingClientRect().top;
    var out = {stand: stand, shown: r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden', off: (r.left + r.right) / 2 - mid, w: r.width,
      bBlock: getComputedStyle(b).display, bAlign: getComputedStyle(b).textAlign, sAlign: getComputedStyle(s).textAlign,
      bLine1: b.getBoundingClientRect().bottom <= s.getBoundingClientRect().top + 1,
      ground: cs.backgroundColor, shift: y1 - y0, grow: t0 !== t1, glow: sh !== 'none', t0: t0, t1: t1};
    d.classList.remove('is-hov'); box.setAttribute('data-on', '0');
    out.offSeen = getComputedStyle(box).visibility === 'hidden' || getComputedStyle(box).display === 'none';
    out.shift2 = modes.getBoundingClientRect().top - y0;
    if (stand.length) box.remove();
    res(out); }, 450); }); }"""

PLAY = r"""() => { var rw = document.querySelector('.nbrw'), w = rw.querySelector('.nbrw-win'), p = rw.querySelector('[data-nbrw-act=play]');
  w.scrollTop = 0; var W0 = w.getBoundingClientRect(), r = p.getBoundingClientRect();
  return {bottom: r.bottom - W0.top, h: W0.height}; }"""

SLIDER = r"""() => { var rw = document.querySelector('.nbrw'), w = rw.querySelector('.nbrw-win'), W0 = w.getBoundingClientRect(), mid = (W0.left + W0.right) / 2;
  rw.querySelectorAll('.nbrw-win details').forEach(function(d){ d.open = true; });
  var s = [].filter.call(rw.querySelectorAll('.nbrw-slider'), function(x){ return x.getBoundingClientRect().width > 0; })[0];
  if (!s) return {err: 'no slider shown'};
  var rg = s.querySelector('.nbrw-range').getBoundingClientRect(), v = s.querySelector('.nbrw-val'), f = s.querySelector('.nbrw-fig');
  // the value's box (JS keeps it a fixed width so the slider does not jump while the number changes) — but a box
  // stretched over the rest of the row (v1.78: 286 px for 'a = 2.0') puts the pair's middle anywhere: not allowed
  var vb = v.getBoundingClientRect(), vRight = vb.right;
  var rng = document.createRange(); rng.selectNodeContents(v); var tw = rng.getBoundingClientRect().width;
  var stretched = vb.width > Math.max(tw, parseFloat(getComputedStyle(v).minWidth) || 0) + 1;
  var fr = f ? f.getBoundingClientRect() : null;
  return {stretched: stretched, valW: Math.round(vb.width), textW: Math.round(tw), pair: (rg.left + vRight) / 2 - mid, fig: fr ? (fr.left + fr.right) / 2 - mid : null, range: [Math.round(rg.left), Math.round(rg.right)], valEnd: Math.round(vRight)}; }"""

SIZES = r"""(strip) => { var rw = document.querySelector('.nbrw');
  // js-E33: no gs-scaled inline sizes on panel elements any more (v1.78's JS sets them: taken out here)
  if (strip) rw.querySelectorAll('.nbrw-panel, .nbrw-panel *, .nbrw-tip').forEach(function(e){ ['font-size', 'height', 'min-width', 'max-width', 'padding', 'gap'].forEach(function(k){
    e.style.removeProperty(k); }); });
  var vis = function(e){ return e && e.getBoundingClientRect().width > 0; };
  var lab = [].filter.call(rw.querySelectorAll('.nbrw-panel .nbrw-lab'), vis)[0];
  var fs = function(e){ return e ? parseFloat(getComputedStyle(e).fontSize) : null; };
  var tb = [].filter.call(rw.querySelectorAll('.nbrw-tools .nbrw-btn'), vis)[1];
  return {lab: fs(lab), xp: fs(rw.querySelector('.nbrw-panel .nbrw-xp-t')), cur: fs(rw.querySelector('.nbrw-panel .nbrw-cur')),
          tip: fs(rw.querySelector('.nbrw-tip')), btnH: tb ? tb.getBoundingClientRect().height : null, btnF: fs(tb),
          pw: rw.querySelector('.nbrw-panel').getBoundingClientRect().width}; }"""

TOOLS = r"""() => { var rw = document.querySelector('.nbrw'), t = rw.querySelector('.nbrw-tools'), stand = [];
  // js-E33 B6: ⌨ ⚙ ✎ 👤 ✉ = button.nbrw-btn.nbrw-tool[data-act=kbd|gear|mode|acct|fb] at the foot of the column
  ['kbd', 'gear', 'mode', 'acct', 'fb'].forEach(function(a, i){ if (!t.querySelector('.nbrw-tool[data-act=' + a + ']')) {
    var b = document.createElement('button'); b.type = 'button'; b.className = 'nbrw-btn nbrw-tool'; b.setAttribute('data-act', a);
    b.textContent = ['⌨', '⚙', '✎', '👤', '✉'][i]; t.appendChild(b); stand.push(a); } });
  var tr = function(c){ return /rgba\(.*, 0\)$|transparent/.test(c); };
  var bs = [].filter.call(t.querySelectorAll('.nbrw-btn:not(.nbrw-wide)'), function(e){ return e.getBoundingClientRect().width > 0; });
  var dims = bs.map(function(e){ var r = e.getBoundingClientRect(); return [Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10]; });
  var bare = bs.filter(function(e){ var s = getComputedStyle(e); return parseFloat(s.borderTopWidth) === 0 || tr(s.backgroundColor); }).length;
  // a drawer as js-E33 writes it
  var dr = rw.querySelector('.nbrw-drawer'), dst = !dr, opened = false;
  // Hauptwerkstatt E33 (merge): with js-E33 in, the real drawer exists but is closed and empty — open its mode drawer
  // (behauptete bisher: a .nbrw-drawer in the page is an open one with a checked button)
  if (dr && !dr.querySelector('[aria-checked=true]') && window.__nbReader && window.__nbReader.drawer) { window.__nbReader.drawer('mode'); opened = true; }
  if (dst) { dr = document.createElement('div'); dr.className = 'nbrw-drawer'; dr.setAttribute('data-kind', 'set');
    dr.style.cssText = 'position:absolute;left:96px;top:60px';
    dr.innerHTML = '<div class="nbrw-dr-h">Settings<button type="button" class="nbrw-dr-x">✕</button></div><div class="nbrw-dr-b">'
      + '<div class="nbrw-dr-t">Mode</div><button type="button" class="nbrw-dbtn nbrw-dr-mode" data-mode="both" aria-checked="true">Both</button>'
      + '<button type="button" class="nbrw-dbtn nbrw-dr-mode" data-mode="plain" aria-checked="false">Plain</button><p class="nbrw-fb">Feedback: mail</p></div>';
    rw.appendChild(dr); }
  var ds = getComputedStyle(dr), on = getComputedStyle(dr.querySelector('[aria-checked=true]')), off = getComputedStyle(dr.querySelector('[aria-checked=false]'));
  var D = {ground: ds.backgroundColor, edge: parseFloat(ds.borderTopWidth), shadow: ds.boxShadow, radius: ds.borderTopLeftRadius,
           onBg: on.backgroundColor, offBg: off.backgroundColor, stand: dst};
  if (dst) dr.remove();
  if (opened) window.__nbReader.drawer('');
  return {stand: stand, n: bs.length, dims: dims, bare: bare, drawer: D}; }"""

THEME = r"""() => { var rw = document.querySelector('.nbrw'), rd = rw.querySelector('.nbrw-win > .nbreading');
  var rgb = function(s){ var m = /rgba?\(([^)]+)\)/.exec(s); return m ? m[1].split(',').map(parseFloat) : [0,0,0]; };
  var lum = function(c){ var f = function(v){ v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); };
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
  var bg = rgb(getComputedStyle(rw.querySelector('.nbrw-win')).backgroundColor), fg = rgb(getComputedStyle(rd).color);
  var L1 = lum(fg), L2 = lum(bg);
  return {bg: getComputedStyle(rw.querySelector('.nbrw-win')).backgroundColor, ink: getComputedStyle(rd).color,
          dark: L2 < .2, contrast: Math.round((Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05) * 100) / 100}; }"""

def window_rows(html, shots, rows, fails):
    from playwright.sync_api import sync_playwright
    def row(tag, ok, txt, err=None):
        rows.append("%s: %s %s" % (tag, txt, "OK" if ok else "RED"))
        if not ok: fails.append("%s: %s" % (tag, err or txt))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        # ---- cover: D1, B2
        for width in (1400, 1366):
            ctx, pg = open_window(b, html, width)
            pg.evaluate(TOCOVER); pg.wait_for_timeout(400)
            # js-E33 B1b makes the window as tall as the screen (≥ 600); the user's PyCharm window was 600 — measured there
            pg.evaluate("() => { document.querySelector('.nbrw').style.setProperty('--nbrw-h', '600px'); document.querySelector('.nbrw-win').style.removeProperty('height'); }")
            pg.wait_for_timeout(200)
            r = pg.evaluate(PLAY)
            row("D1 Play in the first view %d" % width, r["bottom"] <= r["h"] - 4, "Play bottom %.0f px of %.0f" % (r["bottom"], r["h"]))
            if width == 1400:
                r = pg.evaluate(B2)
                f = []
                if r.get("err"): f.append(r["err"])
                else:
                    if not r["shown"]: f.append("info box not shown")
                    if abs(r["off"]) > 1: f.append("box %.1f px off the axis" % r["off"])
                    if not (r["bBlock"] == "block" and r["bLine1"] and r["bAlign"] in ("center", "-webkit-center") and r["sAlign"] in ("center", "-webkit-center")):
                        f.append("name not alone and centred in line 1 (%s/%s/%s/%s)" % (r["bBlock"], r["bLine1"], r["bAlign"], r["sAlign"]))
                    if abs(r["shift"]) > 0 or abs(r["shift2"]) > 0: f.append("the modes moved %.1f / %.1f px" % (r["shift"], r["shift2"]))
                    if not r["grow"] or not r["glow"]: f.append("hovered dot does not grow/glow (%s → %s)" % (r["t0"], r["t1"]))
                    if not r["offSeen"]: f.append("box still seen without [data-on]")
                row("B2 preview timeline%s" % (" (desc stand-in)" if r.get("stand") else ""), not f,
                    "box off %.1f, shift %.1f px, dot grows %s, glow %s" % (r.get("off", 0), r.get("shift", 0), r.get("grow"), r.get("glow")), "; ".join(f))
                if shots:
                    pg.evaluate("() => { var tl = document.querySelector('.nbrw-cv-tl'), d = tl.querySelector('.nbrw-cv-dot[data-kind=chap]'); d.classList.add('is-hov');"
                                " var x = tl.querySelector('.nbrw-cv-desc') || tl.appendChild(Object.assign(document.createElement('div'), {className: 'nbrw-cv-desc'}));"
                                " x.innerHTML = '<b>Chapter 1: Chapter title (placeholder)</b> <span>Chapter 1 in two sentences (placeholder).</span>'; x.setAttribute('data-on', '1'); }")
                    pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(shots, "E33-css-B2-D1-vorschau-hell.png"))
            ctx.close()
        # ---- document
        ctx, pg = open_window(b, html)
        pg.evaluate(TODOC); pg.wait_for_timeout(500)
        r = pg.evaluate(SLIDER)
        ok = not r.get("err") and abs(r["pair"]) <= 2 and (r["fig"] is None or abs(r["fig"]) <= 2) and not r["stretched"]
        row("B4 slider on the axis", ok, "pair off %s, figure off %s, value box %s px for %s px of text %s" % (r.get("pair"), r.get("fig"), r.get("valW"), r.get("textW"), r.get("err", "")))
        s0 = pg.evaluate(SIZES, True)
        pg.evaluate("() => { var R = window.__nbReader; if (R && R.gs) R.gs(130); else document.querySelector('.nbrw').style.setProperty('--nbgs', '1.3'); }")
        pg.wait_for_timeout(400)
        # js-E33 B5: the GUI size leaves the panel's width alone — v1.78's JS widens it with gs (168 → 218): put back
        pw_gs = pg.evaluate("(w) => { var R = window.__nbReader, a = document.querySelector('.nbrw-panel').offsetWidth; if (R && R.pw && a !== w) R.pw(w); return a; }", s0["pw"])
        pg.wait_for_timeout(400); s1 = pg.evaluate(SIZES, True)
        pg.evaluate("() => { var R = window.__nbReader; if (R && R.gs) R.gs(100); else document.querySelector('.nbrw').style.removeProperty('--nbgs'); }")
        pg.wait_for_timeout(300); pg.evaluate(SIZES, True)
        # Hauptwerkstatt E33 (merge): with the real js-E33 the window sets --nbrw-pk itself (place(): lens x panel width) and
        # re-places on every resize — a test-set 1.5 is overwritten before it is measured (behauptete bisher: setting
        # --nbrw-pk by hand holds). Now the real lens: A+ x5 = 150 %, JS writes --nbrw-pk 1.5, CSS sizes from it.
        real = pg.evaluate("() => !!(window.__nbReader && window.__nbReader.ks)")
        if real:
            pg.evaluate("() => { for (var i = 0; i < 5; i++) document.querySelector('.nbrw-btn[data-act=\\x22a+\\x22]').click(); }"); pg.wait_for_timeout(600)
        else:
            pg.evaluate("() => { document.querySelector('.nbrw').style.setProperty('--nbrw-pk', '1.5'); }"); pg.wait_for_timeout(300)
        pk = pg.evaluate("() => getComputedStyle(document.querySelector('.nbrw')).getPropertyValue('--nbrw-pk').trim()")
        s2 = pg.evaluate(SIZES, True)
        if real:
            pg.evaluate("() => { for (var i = 0; i < 5; i++) document.querySelector('.nbrw-btn[data-act=\\x22a-\\x22]').click(); }"); pg.wait_for_timeout(400)
        else:
            pg.evaluate("() => { document.querySelector('.nbrw').style.removeProperty('--nbrw-pk'); }")
        f = []
        if not (s0["btnH"] and s1["btnH"] and abs(s1["btnH"] / s0["btnH"] - 1.3) < 0.04): f.append("tool button %s → %s (x1.3)" % (s0["btnH"], s1["btnH"]))
        for k in ("lab", "xp", "cur", "tip"):
            if s0[k] is None:
                # js-E33 B4: the rail in the panel's middle leaves no room for names at the standard width (.nbrw-noname,
                # the hover box says them) — no name to measure is right there (behauptete bisher: names always shown)
                if k == "lab" and real: continue
                f.append("%s not in the page" % k); continue
            if abs(s1[k] - s0[k]) > 0.1: f.append("%s %s → %s with the GUI size" % (k, s0[k], s1[k]))
            # the marks' names: JS scales each mark as a whole (transform scale(ks)) — the font stays, else twice
            want = 1.0 if k == "lab" else 1.5
            if abs(s2[k] / s0[k] - want) > 0.045: f.append("%s %s → %s with --nbrw-pk %s (want x%.1f)" % (k, s0[k], s2[k], pk, want))
        row("B5 GUI size only on the tools; panel by --nbrw-pk", not f,
            "button %.1f → %.1f; names/xp/cur/tip %s → gs 1.3 %s → pk 1.5 %s (JS panel width with gs %.0f, put back)"
            % (s0["btnH"] or 0, s1["btnH"] or 0, [s0[k] for k in ("lab", "xp", "cur", "tip")], [s1[k] for k in ("lab", "xp", "cur", "tip")],
               [s2[k] for k in ("lab", "xp", "cur", "tip")], pw_gs), "; ".join(f))
        r = pg.evaluate(TOOLS)
        dims = set(tuple(x) for x in r["dims"]); D = r["drawer"]
        tr = lambda c: c.replace(" ", "").endswith(",0)") or c == "transparent"
        f = []
        if r["bare"] or len(dims) != 1: f.append("buttons %s, %d without own surface" % (sorted(dims), r["bare"]))
        if tr(D["ground"]) or D["edge"] < 1 or D["shadow"] in ("none", "") or D["radius"] in ("0px", ""): f.append("drawer %s" % D)
        if D["onBg"] == D["offBg"] or tr(D["onBg"]): f.append("checked button not marked (%s / %s)" % (D["onBg"], D["offBg"]))
        row("B6 tools and drawer%s" % (" (stand-ins %s%s)" % (",".join(r["stand"]), ", drawer" if D["stand"] else "") if r["stand"] or D["stand"] else ""), not f,
            "%d buttons %s, drawer ground %s edge %.0f radius %s" % (r["n"], sorted(dims), D["ground"], D["edge"], D["radius"]), "; ".join(f))
        if shots:
            pg.evaluate("""() => { var rw = document.querySelector('.nbrw'); if (rw.querySelector('.nbrw-drawer')) return;
              var dr = document.createElement('div'); dr.className = 'nbrw-drawer'; dr.setAttribute('data-kind', 'set'); dr.style.cssText = 'position:absolute;left:96px;top:60px';
              dr.innerHTML = '<div class="nbrw-dr-h">Settings<button type="button" class="nbrw-dr-x">✕</button></div><div class="nbrw-dr-b"><div class="nbrw-dr-t">Mode</div>'
                + '<button type="button" class="nbrw-dbtn nbrw-dr-mode" aria-checked="true">Both</button><button type="button" class="nbrw-dbtn nbrw-dr-mode" aria-checked="false">Plain</button>'
                + '<div class="nbrw-dr-t">Keys</div><table class="nbrw-keys"><tr><td><kbd>↓</kbd></td><td>next</td></tr></table><p class="nbrw-fb">Feedback by e-mail</p></div>'; rw.appendChild(dr); }""")
            pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(shots, "E33-css-B6-fenster-werkzeuge-hell.png"))
        ctx.close()
        # ---- D2: VS Code theme (js-E33 sets host + theme from the body's class)
        for cls, theme in (("vscode-dark", "dark"), ("vscode-light", "light")):
            edbg = "#1f1f1f" if theme == "dark" else "#fffffe"
            ctx, pg = open_window(b, html, scheme="light" if theme == "dark" else "dark", body_cls=cls, body_style="--vscode-editor-background:%s" % edbg)
            pg.evaluate(TODOC); pg.wait_for_timeout(400)
            pg.evaluate("(t) => { var rw = document.querySelector('.nbrw'); rw.setAttribute('data-nbrw-host', 'vscode'); rw.setAttribute('data-nbrw-theme', t); }", theme)
            pg.wait_for_timeout(200); r = pg.evaluate(THEME)
            want = "rgb(31,31,31)" if theme == "dark" else "rgb(255,255,254)"
            ok = r["dark"] == (theme == "dark") and r["contrast"] >= 4.5 and r["bg"].replace(" ", "") == want
            row("D2 VS Code %s" % cls, ok, "ground %s (editor %s), ink %s, contrast %.2f" % (r["bg"], edbg, r["ink"], r["contrast"]))
            if shots and theme == "dark":
                pg.screenshot(path=os.path.join(shots, "E33-css-D2-vscode-dunkel.png"))
            other = "light" if theme == "dark" else "dark"
            pg.evaluate("(t) => { document.querySelector('.nbrw').setAttribute('data-nbrw-theme', t); }", other)
            pg.wait_for_timeout(200); r = pg.evaluate(THEME)
            ok = r["dark"] == (other == "dark") and r["bg"].replace(" ", "") != want
            row("D2 VS Code %s, ◐ %s chosen" % (cls, other), ok, "ground %s" % r["bg"])
            ctx.close()
        b.close()

# ---- Lab: C1
C1 = r"""() => { var h = document.getElementById('nbpanel-root'), rail = h.querySelector('.nbrail'), st = [];
  var xp = rail.querySelector(':scope > .nbp-xp'), cur = rail.querySelector(':scope > .nbp-cur');
  // js-E33 C1 (19-rail-title-sync nbRailC1): first child .nbp-xp, last child .nbp-cur, with its inline fallback
  if (!xp) { xp = document.createElement('div'); xp.className = 'nbp-xp'; xp.setAttribute('data-n', '10'); xp.setAttribute('data-solved', '2');
    xp.innerHTML = '<span class="nbp-xp-t">Progress 2 / 10</span><span class="nbp-xp-bar"><span class="nbp-xp-fill"></span></span>';
    xp.style.cssText = 'position:absolute;left:8px;right:8px;top:2px;z-index:6;pointer-events:none;display:flex;flex-direction:column;gap:2px;font:600 11px/1.2 system-ui,sans-serif';
    xp.lastChild.style.cssText = 'display:block;height:5px;border-radius:3px;overflow:hidden;background:rgba(120,132,145,.3)';
    xp.lastChild.firstChild.style.cssText = 'display:block;height:100%;width:20%;background:#2f8f5f';
    rail.insertBefore(xp, rail.firstChild); st.push('xp'); }
  if (!cur) { cur = document.createElement('div'); cur.className = 'nbp-cur';
    cur.style.cssText = 'position:absolute;left:6px;right:6px;bottom:2px;z-index:6;pointer-events:none;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font:700 11px/1.3 system-ui,sans-serif';
    cur.textContent = 'Chapter 1: Chapter title (placeholder)'; rail.appendChild(cur); st.push('cur'); }
  var R = rail.getBoundingClientRect(), X = xp.getBoundingClientRect(), C = cur.getBoundingClientRect(), F = xp.querySelector('.nbp-xp-fill').getBoundingClientRect();
  var T = xp.querySelector('.nbp-xp-t').getBoundingClientRect(), Bb = xp.querySelector('.nbp-xp-bar').getBoundingClientRect();
  var tr = function(c){ return /rgba\(.*, 0\)$|transparent/.test(c); };
  return {stand: st, open: h.classList.contains('nbnames') || h.getAttribute('data-names') === '1', rail: [Math.round(R.left), Math.round(R.top), Math.round(R.right), Math.round(R.bottom)],
    xp: [Math.round(X.left), Math.round(X.top), Math.round(X.right), Math.round(X.bottom)], fillW: F.width, fillH: F.height,
    barW: Bb.width, solved: +(xp.getAttribute('data-solved') || 0), n: +(xp.getAttribute('data-n') || 0),
    oneRow: Math.abs((T.top + T.bottom) / 2 - (Bb.top + Bb.bottom) / 2) <= 2 && Bb.left >= T.right - 1,
    cur: [Math.round(C.left), Math.round(C.top), Math.round(C.right), Math.round(C.bottom)],
    xpGround: !tr(getComputedStyle(xp).backgroundColor), curGround: !tr(getComputedStyle(cur).backgroundColor)}; }"""

def lab_rows(nb, shots, rows, fails):
    import shutil
    import lab_keys as K
    import css_e21 as C
    base, root = K.ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899"))
    name = "css_e33_" + os.path.basename(nb); shutil.copy(nb, os.path.join(root, name))
    C.NB, C.LAB = name, base
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx, pg, errs = C.open_nb(b)
        pg.evaluate(C.SET, ["minimal", "light"]); pg.wait_for_timeout(900)
        gr = pg.evaluate("() => { var g = document.querySelector('#nbpanel-root .nbgrip').getBoundingClientRect(); return [g.left + g.width / 2, g.top + g.height / 2]; }")
        pg.mouse.click(gr[0], gr[1]); pg.wait_for_timeout(1500)
        op = pg.evaluate(C1)
        # the rail fades out 84 px at its top and bottom (mask): the two lines must stand in full ink
        def darkest(box):
            from PIL import Image
            import io
            if box[2] - box[0] < 2 or box[3] - box[1] < 2: return 255
            im = Image.open(io.BytesIO(pg.screenshot(clip={"x": box[0], "y": box[1], "width": box[2] - box[0], "height": box[3] - box[1]}))).convert("L")
            return min(im.getdata())
        ink = (darkest(op["xp"]), darkest(op["cur"]))
        f = []
        if not op["open"]: f.append("BAD the panel did not open")
        if max(ink) > 140: f.append("faded by the rail's mask (darkest pixel bar %d, chapter %d; want <= 140)" % ink)
        if not (op["xpGround"] and op["curGround"]): f.append("no own surface (bar %s, chapter %s)" % (op["xpGround"], op["curGround"]))
        # Hauptwerkstatt E33 (merge): with the real js-E33 the bar starts at 0 / n solved — its fill is 0 px wide by right
        # (behauptete bisher: the stand-in's 2 / 10, fill > 0). Now: bar drawn, fill = bar x solved / n (±1.5 px)
        if op["barW"] <= 0 or op["fillH"] <= 0 or abs(op["fillW"] - op["barW"] * op["solved"] / max(1, op["n"])) > 1.5:
            f.append("bar fill %.1f x %.1f, bar %.1f, %s / %s" % (op["fillW"], op["fillH"], op["barW"], op["solved"], op["n"]))
        if not op["oneRow"]: f.append("text and bar not in one row as in the window")
        rows.append("C1 Lab panel%s: bar %s chapter %s in rail %s, ink %s, fill %.0f x %.0f %s" % (" (stand-ins %s)" % ",".join(op["stand"]) if op["stand"] else "",
                    op["xp"], op["cur"], op["rail"], ink, op["fillW"], op["fillH"], "OK" if not f else "RED"))
        fails += ["C1: %s" % x for x in f]
        if shots:
            pg.screenshot(path=os.path.join(shots, "E33-css-C1-lab-panel-hell.png"))
        if errs: fails.append("Lab: page errors %s" % errs[:3])
        b.close()

# ---- --static: the saved file, not trusted (Python's half; after py-E33)
STATIC = r"""(run) => { var other = run === 'en' ? 'de' : 'en';
  var rgba = function(s){ var m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return [0,0,0,0]; var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  var lum = function(c){ var f = function(v){ v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
  var over = function(t, b){ var a = t[3]; return [t[0]*a + b[0]*(1-a), t[1]*a + b[1]*(1-a), t[2]*a + b[2]*(1-a), 1]; };
  var ground = function(e){ var L = []; for (var x = e; x; x = x.parentElement) { var s = getComputedStyle(x), c = rgba(s.backgroundColor);
      if (s.backgroundImage && s.backgroundImage !== 'none') { var g = /rgba?\([^)]+\)|#[0-9a-f]{3,6}/i.exec(s.backgroundImage); if (g) { c = rgba(g[0].charAt(0) === '#' ? 'rgb(' + [1,3,5].map(function(i){ return parseInt(g[0].substr(i, 2), 16); }) + ')' : g[0]); } }
      if (c[3] > 0) L.push(c); if (c[3] >= 1) break; }
    var b = L.length && L[L.length - 1][3] >= 1 ? L.pop() : [255,255,255,1]; while (L.length) b = over(L.pop(), b); return b; };
  var outs = document.querySelectorAll('.jp-OutputArea-output'), low = [], minC = 99, seen = 0;
  // markers of the other language: the reading version's own pieces of the build (kernel _STRUCT titles are not known here)
  var M = other === 'de' ? /Titel des Notebooks|Kapiteltitel|Einführung|So benutzen Sie|Platzhalter/ : /Notebook title|Chapter title|Introduction|How to use this notebook|placeholder/;
  var bad = [];
  outs.forEach(function(o){ o.querySelectorAll('*').forEach(function(e){
    var own = [].filter.call(e.childNodes, function(n){ return n.nodeType === 3 && n.textContent.trim(); }).map(function(n){ return n.textContent; }).join(' ').trim();
    if (!own) return; var r = e.getBoundingClientRect();
    // Hauptwerkstatt E33 (merge): a bibliography entry ([n] + source) is data, the same in both languages (vorlage BIB:
    // 'Zweite Quelle (Platzhalter) …') — not the other language (behauptete bisher: every 'Platzhalter' is German UI text)
    var fb = e.firstElementChild; if (fb && fb.tagName === 'B' && /^\[\d+\]$/.test(fb.textContent.trim())) return; if (!(r.width > 0 && r.height > 0)) return;
    var s = getComputedStyle(e); if (s.visibility === 'hidden' || +s.opacity === 0) return;
    seen++; if (M.test(own) && bad.length < 6) bad.push(own.slice(0, 40));
    var bg = ground(e), fg = over(rgba(s.color), bg), a = lum(fg), b = lum(bg), c = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    if (c < minC) minC = c; if (c < 4.5 && low.length < 6) low.push(own.slice(0, 30) + ' ' + c.toFixed(2)); }); });
  return {seen: seen, other: bad, minC: Math.round(minC * 100) / 100, low: low}; }"""

def static_rows(nb, shots, rows, fails):
    import shutil, subprocess, tempfile, urllib.request
    import lab_keys as K
    base, root = K.ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899"))
    tmp = tempfile.mkdtemp(prefix="css_e33_")
    ex = os.path.join(tmp, "css_e33_static.ipynb")
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--ExecutePreprocessor.timeout=600",
                    nb, "--output", ex], check=True, capture_output=True)
    name = "css_e33_static_%d.ipynb" % int(time.time()); shutil.copy(ex, os.path.join(root, name))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for theme in ("JupyterLab Light", "JupyterLab Dark"):
            req = urllib.request.Request(base + "/lab/api/settings/@jupyterlab/apputils-extension:themes", method="PUT",
                                         data=json.dumps({"raw": json.dumps({"theme": theme})}).encode(), headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req).read()
            ctx = b.new_context(viewport={"width": W, "height": H}); pg = ctx.new_page()
            pg.goto(base + "/lab/tree/" + name + "?reset"); pg.wait_for_selector(".jp-OutputArea-output", state="attached", timeout=120000)
            pg.wait_for_timeout(3500)
            r = pg.evaluate(STATIC, "en")
            ok = r["seen"] > 20 and not r["other"] and r["minC"] >= 4.5
            rows.append("A1s saved file, not trusted, %s: %d texts, other language %s, min contrast %.2f %s %s"
                        % (theme, r["seen"], r["other"][:3] or "none", r["minC"], r["low"][:3], "OK" if ok else "RED"))
            if not ok: fails.append("A1s %s: other %s, low %s" % (theme, r["other"][:3], r["low"][:3]))
            if shots: pg.screenshot(path=os.path.join(shots, "E33-css-A1s-%s.png" % ("hell" if "Light" in theme else "dunkel")))
            ctx.close()
        urllib.request.urlopen(urllib.request.Request(base + "/lab/api/settings/@jupyterlab/apputils-extension:themes", method="PUT",
                               data=json.dumps({"raw": json.dumps({"theme": "JupyterLab Light"})}).encode(), headers={"Content-Type": "application/json"})).read()
        b.close()

def main():
    import nbpick
    nb = nbpick.from_argv(sys.argv)
    shots = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
    if shots: os.makedirs(shots, exist_ok=True)
    rows, fails = [], []
    outs, errs, _ = run_cell(nb, {})
    if errs: print("kernel errors:", errs[:3])
    rd = [o for o in outs if "nbreading" in (o["data"].get("text/html") or "")]
    if not rd:
        print("FAIL no reading output"); print("REGRESS-CSS-E33 RED"); return 1
    window_rows(rd[0]["data"]["text/html"], shots, rows, fails)
    if "--no-lab" not in sys.argv:
        lab_rows(nb, shots, rows, fails)
    if "--static" in sys.argv:
        static_rows(nb, shots, rows, fails)
    print("\n".join(rows))
    for x in fails: print("FAIL", x)
    print("REGRESS-CSS-E33", "OK" if not fails else "RED")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.exit(main())
