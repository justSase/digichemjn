"""E35 · JS J1 — KEIN AUFBLITZEN: STIL UND THEMA VOR DEM ERSTEN BILD (Werkstatt JS, 2026-10-19).
    python3 tests/regress/js_e35.py [<notebook.ipynb>] [--only F1,S1] [--shots DIR]

plan/AUFTRAG.md J1 (zu CSS C3; Nutzer 19.10.: „helle minimal-Karte auf Schwarz, dann Wechsel“). Real JupyterLab (own
server, own HOME), each row a browser context of its own (= a fresh browser profile), 1400 × 900, the template unless a
notebook is named. Run All, then every picture the page paints (CDP screencast) until the cover (Vorschau) has stood 1 s.
Counted are the pictures from the first one in which OUR first script (02-loading) has run (`window.__nbLoading`) —
before it the front end paints the cold cell by itself (trust model: no JavaScript of ours before Run).
Region: the notebook panel below its tool bar; Lab's notifications (toasts) are hidden by the test.
A „light surface“ = a 24 × 24 px block of which ≥ 95 % of the pixels are lighter than #2a2f4a (relative luminance),
so text, rules and small marks do not count, a card or a loading view does.
Rows:
  F1  fresh, Lab light   every counted picture: body.nbskin-digi + body.nbdark + the panel data-digichem="1", and no
                         light surface (also listed: the first 5 s alone)
  F2  fresh, Lab dark    the same under a dark Lab (the app's Lite is dark: the reader's picture)
  S1  stored minimal + light (themeseen = the Lab's light) → every counted picture: no nbskin-*, no nbdark — a reader
                         who chose is not shown digi first (nobody is moved, E34)
  S2  stored fairy + dark → every counted picture: body.nbskin-fairy + body.nbdark
v1.80 (`cecc1c32`): red F1, F2, S2 (no class before the panel, ≈ 12 s; loading view in minimal's light #f8fafb resp.
#1f252c); S1 green on both (it guards „nobody is moved“).
Owner: JS. exit 0 = REGRESS-JS-E35 OK."""
import sys, os, io, json, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e35 is a stand-alone script")

args = sys.argv[1:]
ONLY = args[args.index("--only") + 1].split(",") if "--only" in args else None
want = lambda k: not ONLY or any(k.startswith(x) for x in ONLY)
shots = args[args.index("--shots") + 1] if "--shots" in args else None

ROWS, FAILS = [], []
def row(k, ok, det, count=True):
    ROWS.append((k, ok, det)); print("%-4s %s  %s" % (k, "ok " if ok else ("RED" if count else "red (info)"), det)); sys.stdout.flush()
    if not ok and count: FAILS.append(k)

LUM = lambda r, g, b: 0.2126 * r + 0.7152 * g + 0.0722 * b
TH = LUM(0x2a, 0x2f, 0x4a)
ST = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); if (!P) return null;
  var r = P.getBoundingClientRect(), tb = P.querySelector('.jp-NotebookPanel-toolbar'), top = tb ? tb.getBoundingClientRect().bottom : r.top;
  var b = document.body, sk = [].filter.call(b.classList, function (c) { return c.indexOf('nbskin-') === 0; }).join(',');
  return {box: [r.left, top, r.width, r.bottom - top], ours: !!window.__nbLoading, skin: sk || 'minimal', dark: b.classList.contains('nbdark'),
          dc: P.getAttribute('data-digichem'), cov: !!P.querySelector('.nbcover-out[data-nbcov]'),
          load: !!document.querySelector('#nbload:not(.nbload-out)')}; }"""
INIT = """(function(items){ try { if (sessionStorage.getItem('__e35')) return;
  Object.keys(items).forEach(function(k){ localStorage.setItem(k, items[k]); }); sessionStorage.setItem('__e35', '1'); } catch (e) {} })(%s);"""
NOTOAST = ".Toastify, .jp-toast-container, .jp-Notification-Toast { display: none !important; }"

def light_blocks(png):
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"), dtype=float)
    L = (a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722) > TH
    H, W = L.shape; H -= H % 24; W -= W % 24
    if H < 24 or W < 24: return 0
    return int((L[:H, :W].reshape(H // 24, 24, W // 24, 24).mean(axis=(1, 3)) >= 0.95).sum())

def film(b, R, BASE, ROOT, kill_sessions, src, theme, items, tag):
    """Run All in a fresh profile and take the pictures. Returns the counted frames [(t, light, state)]."""
    kill_sessions(BASE); R.set_lab_theme(BASE, theme)
    c = b.new_context(viewport={"width": 1400, "height": 900})
    if items: c.add_init_script(INIT % json.dumps(items))
    pg = c.new_page()
    name = "e35_%s_%d_%s" % (tag, int(time.time() * 1000) % 1000000, os.path.basename(src))
    shutil.copy(src, os.path.join(ROOT, name))
    pg.goto(BASE + "/lab/tree/" + name + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.add_style_tag(content=NOTOAST); pg.wait_for_timeout(2000)
    if not R.palette(pg, "Run All Cells"):
        c.close(); raise RuntimeError("Run All Cells not reached")
    # every picture the page paints (CDP screencast: a frame per paint, ≈ 30–60 per s while it changes), and
    # beside it the page's state every ≈ 50 ms; a picture counts with the last state read before it
    cdp = c.new_cdp_session(pg); pics, states = [], []
    def on_frame(ev):
        pics.append((time.time(), ev["data"]))
        try: cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception: pass
    cdp.on("Page.screencastFrame", on_frame)
    cdp.send("Page.startScreencast", {"format": "png", "everyNthFrame": 1, "maxWidth": 1400, "maxHeight": 900})
    t0 = time.time(); cov_at = None
    while time.time() - t0 < 150:
        s = pg.evaluate(ST); t = time.time()
        if s: states.append((t, s))
        if s and s["cov"] and not s["load"] and cov_at is None: cov_at = round(t - t0, 2)
        if cov_at is not None and t - t0 - cov_at >= 1.0: break
        pg.wait_for_timeout(50)
    try: cdp.send("Page.stopScreencast")
    except Exception: pass
    import base64
    frames, before, saved, j = [], 0, 0, -1
    for tp, data in pics:
        while j + 1 < len(states) and states[j + 1][0] <= tp: j += 1
        if j < 0: before += 1; continue
        s = states[j][1]
        if not s["ours"]: before += 1; continue
        png = base64.b64decode(data)
        x, y, w, h = [int(v) for v in s["box"]]
        from PIL import Image
        im = Image.open(io.BytesIO(png)).convert("RGB")
        if im.size != (1400, 900): im = im.resize((1400, 900))
        buf = io.BytesIO(); im.crop((x, y, x + w, y + h)).save(buf, "PNG"); crop = buf.getvalue()
        n = light_blocks(crop); t = round(tp - t0, 2); frames.append((t, n, s))
        if shots and n and saved < 3:
            open(os.path.join(shots, "E35-js-%s-hell-%05.2f.png" % (tag, t)), "wb").write(crop); saved += 1
    if shots: pg.screenshot(path=os.path.join(shots, "E35-js-%s-ende.png" % tag))
    c.close()
    return frames, before, cov_at

def summary(frames, before, cov_at):
    if not frames: return "BAD no picture after our first script"
    t1 = frames[0][0]
    return "%d pictures counted (first at %.2f s, %d before it), cover at %s s" % (len(frames), t1, before, cov_at)

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src)
    from lab_keys import ensure_lab, kill_sessions, CHROME
    from playwright.sync_api import sync_playwright
    sys.argv = [sys.argv[0]]
    import run as R
    nid = R.nb_id(src)
    BASE, ROOT = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    k = lambda key: "digichemjn.%s.v1.%s" % (key, nid)
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    try:
        for key, theme in (("F1", "light"), ("F2", "dark")):
            if not want(key): continue
            try:
                fr, bf, cv = film(b, R, BASE, ROOT, kill_sessions, src, theme, {}, key)
                bad_cls = [f for f in fr if not (f[2]["skin"] == "nbskin-digi" and f[2]["dark"] and f[2]["dc"] == "1")]
                bad_lit = [f for f in fr if f[1]]
                five = [f for f in bad_lit if f[0] - (fr[0][0] if fr else 0) <= 5]
                ok = bool(fr and cv is not None and not bad_cls and not bad_lit)
                det = "Lab %s: %s · not digi+dark: %d%s · with a light surface: %d (first 5 s: %d)%s" % (
                    theme, summary(fr, bf, cv), len(bad_cls),
                    (" (first at %.2f s: %s)" % (bad_cls[0][0], {x: bad_cls[0][2][x] for x in ("skin", "dark", "dc")})) if bad_cls else "",
                    len(bad_lit), len(five), (" (first at %.2f s, %d blocks)" % bad_lit[0][:2]) if bad_lit else "")
                row(key, ok, det)
            except Exception as e:
                row(key, False, "BAD %s" % str(e).splitlines()[0][:200])
        for key, items, want_skin, want_dark, label in (
                ("S1", {k("skin"): "minimal", k("theme"): "light", k("themeseen"): "true"}, "minimal", False, "stored minimal + light"),
                ("S2", {k("skin"): "fairy", k("theme"): "dark", k("themeseen"): "true"}, "nbskin-fairy", True, "stored fairy + dark")):
            if not want(key): continue
            try:
                fr, bf, cv = film(b, R, BASE, ROOT, kill_sessions, src, "light", items, key)
                bad = [f for f in fr if not (f[2]["skin"] == want_skin and f[2]["dark"] == want_dark)]
                ok = bool(fr and cv is not None and not bad)
                row(key, ok, "%s, Lab light: %s · other look: %d%s" % (label, summary(fr, bf, cv), len(bad),
                    (" (first at %.2f s: %s/%s)" % (bad[0][0], bad[0][2]["skin"], bad[0][2]["dark"])) if bad else ""))
            except Exception as e:
                row(key, False, "BAD %s" % str(e).splitlines()[0][:200])
    finally:
        b.close(); p.stop()
    print("REGRESS-JS-E35 %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
