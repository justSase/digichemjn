"""E32 K1 · COLAB — ALL OUTPUTS IN ONE IFRAME, WIDGETS DRAWN, THE IFRAME AS HIGH AS ITS CONTENT (Werkstatt JS, 2026-10-13).
    python3 tests/regress/env_colab.py [<notebook.ipynb> | --nb vorlage] [--shots DIR] [--json out.json] [--watch S]

Nutzer 11.10. (two videos, Vorlage v1.73 in Colab): the output area JUMPS — first high and empty, then small; for a moment our
Lab tools (lens slider, round buttons) show, then it folds again, over and over. Colab draws ALL outputs of a cell into ONE
iframe WITH a widget manager, and its resizer sets the iframe's height to the height of what is inside — whatever sizes itself
from the frame's viewport (innerHeight, vh) then chases its own tail.
Nachbau (served over http, one origin = one localStorage): the cell runs in a real kernel (env_iframe.run_cell); the host page
holds ONE iframe; inside it every output in its order, each in a container of its own the way a front end draws it —
application/javascript runs (`element` = its container), text/html is drawn and its scripts re-created so that they run,
a widget view is drawn from the kernel's model states (env_iframe.widget_html: layout styles, HTML values, boxes, buttons,
fields). The frame's resizer: a ResizeObserver + a 100 ms poll on the outputs' container post its height, the host sets the
iframe to exactly that (it grows AND shrinks, as Colab's does). No .jp-NotebookPanel, no #notebook anywhere.
Rows (1400 × 900, light; then dark):
  K1a one window        exactly one visible .nbrw, on the preview; its window (.nbrw-win) screen.availHeight − 240 px
                        (fresh storage; E33 B1b — was 600)
  K1b no Lab tools      0 visible tools outside the window (button/input/select/textarea/[role=button], #nbpanel-root,
                        .nbcorner, .nbsb, .nbgrip, .nbmap): the held widget outputs stay held
  K1c0 widgets later    from the window's first frame until every widget view is drawn (the widget manager comes
                        2500 ms late, --widgets-ms): always one window, 0 tools, frame ±2 px
  K1c height stable     iframe height watched 10 s on the preview: max − min ≤ 2 px; the window's height ±1 px
  K1d after Play        ▶ Play → the document; again 10 s: iframe ±2 px, window ±1 px, still one window, 0 tools
  K1e ↕+ is the only    ↕+ → window +100 px, iframe follows once (+100 ±4 px) and stays ±2 px for 3 s
      way to grow
v1.78: red expected (the window's height from the viewport / the frame chasing it). Lab/Lite: cold.py, lab_flow, lab_cover.
Owner: JS. exit 0 = REGRESS-ENV-COLAB OK."""
import sys, os, re, json, time, tempfile, shutil, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from env_iframe import run_cell, widget_html, WMIME
from env_reader import serve

HOST = """<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:%s'>
<div class='colab-cell'><pre style='margin:0 0 6px;color:#888'>[cell]</pre>
<iframe id='out' src='colab_out.html' style='display:block;width:100%%;border:0;height:%s'></iframe></div>
<div style='height:2400px'></div>
<script>var F = document.getElementById('out'); window.H = [];
addEventListener('message', function (e) { if (e.data && e.data.colabH != null) { var h = Math.max(1, Math.round(e.data.colabH));
  F.style.height = h + 'px'; } });
setInterval(function () { window.H.push(Math.round(F.getBoundingClientRect().height)); }, 100);</script>"""

INNER = """<!doctype html><meta charset=utf-8><body style='margin:0;background:%s;color:%s'><div id='outs'></div>
<script>var O = %s, box = document.getElementById('outs');
// outputs arrive one after the other (40 ms apart, as the kernel sends them); the widget views are drawn only when the
// widget manager has loaded (Colab fetches it from a CDN: %d ms after the first output) — the reading window is up by then
var WD = %d, t0 = Date.now(), held = [];
function draw(o, d) {
  if (o.k === 'js') { var s = document.createElement('script'); s.textContent = 'var element = document.currentScript.parentNode;\\n' + o.v;
    d.appendChild(s); return; }
  d.innerHTML = o.v;
  if (o.k === 'html') [].slice.call(d.querySelectorAll('script')).forEach(function (x) { var n = document.createElement('script');
    n.textContent = x.textContent; x.parentNode.replaceChild(n, x); }); }
O.forEach(function (o, i) { setTimeout(function () {
  var d = document.createElement('div'); d.className = 'output_subarea'; box.appendChild(d);
  if (o.k === 'w') setTimeout(function () { draw(o, d); window.__wDrawn = (window.__wDrawn || 0) + 1; }, Math.max(0, WD - (Date.now() - t0)));
  else draw(o, d); }, 40 * i); });
function post() { parent.postMessage({colabH: box.getBoundingClientRect().height}, '*'); }
try { new ResizeObserver(post).observe(box); } catch (e) {}
setInterval(post, 100); post();</script>"""

PROBE = r"""() => {
  var f = document.getElementById('out'), d = f.contentDocument, w = d.defaultView;
  var vis = function (e) { var b = e.getBoundingClientRect(), s = w.getComputedStyle(e);
    if (!(b.width > 0 && b.height > 0) || s.visibility === 'hidden' || +s.opacity === 0) return false;
    for (var x = e; x; x = x.parentElement) { var c = w.getComputedStyle(x); if (c.display === 'none' || c.visibility === 'hidden') return false;
      if (x !== e && (c.overflow === 'hidden' || c.overflowY === 'hidden')) { var r = x.getBoundingClientRect(); if (r.height < 1 || r.width < 1) return false; } }
    return true; };
  var wins = [].filter.call(d.querySelectorAll('.nbrw'), vis);
  var tools = [].filter.call(d.querySelectorAll('button,input,select,textarea,[role=button],#nbpanel-root,.nbcorner,.nbsb,.nbgrip,.nbmap'),
    function (e) { return !e.closest('.nbrw') && vis(e); });
  var win = wins[0] && wins[0].querySelector('.nbrw-win');
  return {wins: wins.length, view: wins[0] ? wins[0].getAttribute('data-nbrw-view') : null,
          winH: win ? Math.round(win.getBoundingClientRect().height * 10) / 10 : -1,
          frameH: Math.round(f.getBoundingClientRect().height), inner: w.innerHeight, scr: w.screen.availHeight,
          tools: tools.length, toolEx: tools.slice(0, 5).map(function (e) { return e.tagName + '.' + (e.className || '').toString().slice(0, 30) + ':' + (e.textContent || e.value || '').trim().slice(0, 16); }),
          hosted: !!d.querySelector('.jp-NotebookPanel,.jp-Notebook,#notebook'), live: !!d.querySelector('.nb-live'), acc: !!d.querySelector('.acc-root')}; }"""

def H0(p):            # E33 B1b: 20-reader hDef()
    return max(300, min(2400, int(round((p["scr"] - 240) / 10.0)) * 10)) if p.get("scr") else 600

def outputs(outs):
    O = []
    for o in outs:
        d = o["data"]
        if "application/javascript" in d: O.append({"k": "js", "v": d["application/javascript"]})
        elif WMIME in d: O.append({"k": "w", "v": widget_html(o["models"], (d[WMIME] or {}).get("model_id"))})
        elif "text/html" in d: O.append({"k": "html", "v": d["text/html"]})
        elif "image/png" in d: O.append({"k": "img", "v": "<img src='data:image/png;base64,%s'>" % d["image/png"]})
    return O

def watch(pg, secs):
    """iframe height samples (host, 100 ms) and window heights over `secs` s."""
    pg.evaluate("() => { window.H = []; }")
    wh = []
    for _ in range(int(secs * 4)):
        pg.wait_for_timeout(250)
        try: wh.append(pg.evaluate(PROBE)["winH"])
        except Exception: wh.append(-1)
    hs = pg.evaluate("() => window.H.slice()")
    return hs, wh

def rng(a):
    a = [x for x in a if x is not None]
    return (min(a), max(a)) if a else (0, 0)

def one(b, base, theme, tag, fails, rows, shots, secs, nwid):
    ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme=theme)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
    pg.goto(base + ("host_%s.html" % theme))
    t0 = time.time(); nw = pg.evaluate("n => n", nwid)
    while time.time() - t0 < 25:                       # the window or 25 s
        pg.wait_for_timeout(100)
        try:
            if pg.evaluate(PROBE)["wins"]: break
        except Exception: pass
    pg.evaluate("() => { window.H = []; }")             # from the window's first frame on: the widgets come later
    wsteps = []
    while time.time() - t0 < 30:
        pg.wait_for_timeout(250)
        try:
            q = pg.evaluate(PROBE); wsteps.append((q["wins"], q["tools"], q["frameH"]))
            if pg.evaluate("() => document.getElementById('out').contentWindow.__wDrawn || 0") >= nw: break
        except Exception: pass
    pg.wait_for_timeout(1500)
    h0 = pg.evaluate("() => window.H.slice()")
    a0, z0 = rng(h0)
    rows.append("K1c0 %s while the widgets come (%d views): frame %d … %d px · windows/tools seen %s"
                % (tag, nw, a0, z0, sorted(set((w, t) for w, t, _ in wsteps))))
    if z0 - a0 > 2: fails.append("K1c0 %s: the frame jumps %d … %d px while the widgets are drawn, want ±2" % (tag, a0, z0))
    if any(t for _w, t, _f in wsteps) or any(w != 1 for w, _t, _f in wsteps):
        fails.append("K1c0 %s: on the way windows/tools %s, want always (1, 0)" % (tag, sorted(set((w, t) for w, t, _ in wsteps))))
    p = pg.evaluate(PROBE)
    rows.append("K1a %s: windows %d · view %s · window %.1f px · frame %d px (inner %d) · hosted %s · .acc-root %s · nb-live %s"
                % (tag, p["wins"], p["view"], p["winH"], p["frameH"], p["inner"], p["hosted"], p["acc"], p["live"]))
    if p["wins"] != 1: fails.append("K1a %s: %d visible windows, want 1" % (tag, p["wins"]))
    # E33 B1b (Werkstatt JS): the fresh window is the screen's height less the IDE's bars — a number of the display,
    # never of the frame (behauptete bisher: 600 px). Still no feedback with the frame: K1c/K1d hold it ±1 px
    elif abs(p["winH"] - H0(p)) > 1: fails.append("K1a %s: window %.1f px, want %d (screen.availHeight %d − 240, fresh storage)" % (tag, p["winH"], H0(p), p["scr"]))
    if p["acc"] is False: fails.append("K1a %s: BAD no widget drawn (.acc-root) — the Nachbau is no Colab" % tag)
    rows.append("K1b %s: tools outside the window %d %s" % (tag, p["tools"], p["toolEx"]))
    if p["tools"]: fails.append("K1b %s: %d Lab tools visible %s" % (tag, p["tools"], p["toolEx"]))
    if shots: pg.screenshot(path=os.path.join(shots, "E32-K1-colab-%s-vorschau.png" % tag))
    hs, wh = watch(pg, secs)
    a, z = rng(hs); wa, wz = rng(wh)
    rows.append("K1c %s preview %d s: frame %d … %d px (%d samples) · window %.1f … %.1f px" % (tag, secs, a, z, len(hs), wa, wz))
    if not hs or z - a > 2: fails.append("K1c %s: frame height %d … %d px over %d s, want ±2" % (tag, a, z, secs))
    if wz - wa > 1: fails.append("K1c %s: window %.1f … %.1f px, want ±1" % (tag, wa, wz))
    f = pg.frame_locator("#out")
    try:
        pg.evaluate("() => { var d = document.getElementById('out').contentDocument, w = d.querySelector('.nbrw'),"
                    " p = w && w.querySelector('[data-nbrw-act=play]'); if (p) p.click(); }")
    except Exception: pass
    pg.wait_for_timeout(1500)
    p = pg.evaluate(PROBE)
    hs, wh = watch(pg, secs)
    a, z = rng(hs); wa, wz = rng(wh)
    q = pg.evaluate(PROBE)
    rows.append("K1d %s document %d s: view %s · windows %d · tools %d · frame %d … %d px · window %.1f … %.1f px"
                % (tag, secs, q["view"], q["wins"], q["tools"], a, z, wa, wz))
    if q["view"] != "doc" and q["view"] != "document": fails.append("K1d %s: view %s after Play, want the document" % (tag, q["view"]))
    if q["wins"] != 1 or q["tools"]: fails.append("K1d %s: windows %d, tools %d %s" % (tag, q["wins"], q["tools"], q["toolEx"]))
    if not hs or z - a > 2: fails.append("K1d %s: frame height %d … %d px over %d s, want ±2" % (tag, a, z, secs))
    if wz - wa > 1: fails.append("K1d %s: window %.1f … %.1f px, want ±1" % (tag, wa, wz))
    if shots: pg.screenshot(path=os.path.join(shots, "E32-K1-colab-%s-dokument.png" % tag))
    f0 = q["frameH"]
    pg.evaluate("() => { var d = document.getElementById('out').contentDocument, b = d.querySelector('.nbrw [data-act=\"h+\"]');"
                " if (b) b.click(); }")
    pg.wait_for_timeout(800)
    hs, wh = watch(pg, 3)
    a, z = rng(hs); r = pg.evaluate(PROBE)
    rows.append("K1e %s ↕+: window %.1f px · frame %d → %d … %d px" % (tag, r["winH"], f0, a, z))
    if abs(r["winH"] - H0(r) - 100) > 1: fails.append("K1e %s: window %.1f px after ↕+, want %d" % (tag, r["winH"], H0(r) + 100))
    if z - a > 2 or abs((a - f0) - 100) > 4: fails.append("K1e %s: frame %d → %d … %d px, want +100 ±4 and stable" % (tag, f0, a, z))
    pg.evaluate("() => { var d = document.getElementById('out').contentDocument, b = d.querySelector('.nbrw [data-act=\"h-\"]');"
                " if (b) b.click(); }")
    if errs: rows.append("K1 %s page errors: %s" % (tag, errs[:3]))
    ctx.close()

def main():
    a = sys.argv[1:]
    def opt(k, d=None):
        if k in a: i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
        return d
    shots, js_out, secs = opt("--shots"), opt("--json"), float(opt("--watch", "10"))
    wdelay = int(opt("--widgets-ms", "2500"))
    nbk = opt("--nb", None)
    src = a[0] if a else None
    if not src:
        root = os.path.dirname(os.path.dirname(HERE))
        c = sorted(glob.glob(os.path.join(root, nbk or "vorlage", "*_v*.ipynb")))
        src = c[-1] if c else None
    if not src: print("BAD no notebook"); sys.exit(2)
    if shots: os.makedirs(shots, exist_ok=True)
    outs, errs, _ch = run_cell(src, {})
    rows, fails = ["notebook %s · kernel errors %s · outputs %d (widget views %d)"
                   % (os.path.basename(src), errs[:2], len(outs), sum(1 for o in outs if WMIME in o["data"]))], []
    if errs: fails.append("kernel errors: %s" % errs[:2])
    O = outputs(outs)
    tmpd = tempfile.mkdtemp(prefix="envcolab")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as P:
        b = P.chromium.launch()
        for theme, bg, fg in (("light", "#ffffff", "#1f2328"), ("dark", "#383838", "#e0e0e0")):
            d = os.path.join(tmpd, theme); os.makedirs(d)
            open(os.path.join(d, "host_%s.html" % theme), "w", encoding="utf-8").write(HOST % (bg, "120px"))
            open(os.path.join(d, "colab_out.html"), "w", encoding="utf-8").write(
                INNER % (bg, fg, json.dumps(O).replace("</", "<\\/"), wdelay, wdelay))
            s = serve(d)
            try: one(b, "http://127.0.0.1:%d/" % s.server_address[1], theme, theme, fails, rows, shots, secs, sum(1 for o in O if o["k"] == "w"))
            finally: s.shutdown(); s.server_close()
        b.close()
    shutil.rmtree(tmpd, ignore_errors=True)
    for r in rows: print("  " + r)
    if js_out: json.dump({"rows": rows, "fails": fails}, open(js_out, "w"), indent=1)
    if fails:
        for f in fails: print("FAIL " + f)
        print("REGRESS-ENV-COLAB RED (%d)" % len(fails)); sys.exit(1)
    print("REGRESS-ENV-COLAB OK")

if __name__ == "__main__":
    main()
