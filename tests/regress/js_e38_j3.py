"""E38 · JS — J3 REGLER: SOFORT VORSCHAU, DANN LIVE (Werkstatt JS, 2026-10-27).
    python3 tests/regress/js_e38_j3.py [<notebook.ipynb>|--nb vorlage] [--dist DIR] [--only J3a,J3c] [--shots DIR]

plan/AUFTRAG.md J3. lesen.html aus der gebauten Hülle über http, echter Chromium, 1400 × 900, digi dunkel. Pyodide ist ein
Stub unter <origin>/pyodide/0.27.7/pyodide.js (prüft das Protokoll, nicht matplotlib); die Render-Funktion (P4) kommt als
Stand-in in daten.json regler[0].py (claude/VERTRAG-E38-js.md), solange der Bau sie nicht liefert.
  J3a sofort        Bilder-Entpacken künstlich 2,5 s verzögert: der Regler ist ab dem Start sichtbar und bewegbar; eine
                    Bewegung davor zeigt nach dem Entpacken das Bild ihrer Stufe
  J3b Vorschau      Regler 0 ohne Live-Daten: Stufe 4 → Bild der Stufe sofort (≤ 1 Bild, data-frame), Wert „a = 7.5“
  J3c live          mit regler[0].py: Bereich = Parameter (0…10, 0,5); a = 3,5 → sofort Vorschaubild der nächsten Stufe,
                    dann data-live laedt → live, Bild = Python mit {"a": 3.5}, Wert „a = 3.5“; Pakete numpy+matplotlib
  J3d kein Python   pyodide.js 404 → data-live = aus, das Vorschaubild bleibt (kein leeres Bild)
Gegenprobe v1.84 (`390392b`): J3a, J3c, J3d rot; J3b grün (wacht über „Vorschau wie bisher“). Owner: JS.
exit 0 = REGRESS-JS-E38-J3 OK."""
import sys, os, re, json, glob, shutil, tempfile, threading, functools, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e38_j3 is a stand-alone script")
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

args = sys.argv[1:]
ONLY = args[args.index("--only") + 1].split(",") if "--only" in args else None
want = lambda k: not ONLY or any(k.startswith(x) for x in ONLY)
shots = args[args.index("--shots") + 1] if "--shots" in args else None
DIST = args[args.index("--dist") + 1] if "--dist" in args else os.path.join(ROOT, "dist")

ROWS, FAILS = [], []
def row(k, ok, det):
    ROWS.append((k, ok, det)); print("%-4s %s  %s" % (k, "ok " if ok else "RED", det)); sys.stdout.flush()
    if not ok: FAILS.append(k)

class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve(d):
    s = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=d))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, "http://127.0.0.1:%d/" % s.server_address[1]

def ids():
    h = glob.glob(os.path.join(DIST, "huelle", "*", "manifest.json"))
    if not h: raise SystemExit("BAD no hull under %s (build first: cd vorlage && python3 build_vorlage.py)" % DIST)
    tv = os.path.basename(os.path.dirname(sorted(h)[-1]))
    pk = sorted(glob.glob(os.path.join(DIST, "inhalt", "*", "*", "meta.json")))[0]
    meta = json.load(open(pk, encoding="utf-8"))
    return tv, meta["id"], os.path.basename(os.path.dirname(pk))

LIVE = {"code": "import numpy as np\ndef _render_k01(a=2.0):\n    import matplotlib.pyplot as plt\n    fig, ax = plt.subplots()\n    ax.plot([0, 10], [0, 10 * a])\n    return fig\n",
        "fn": "_render_k01", "params": [{"name": "a", "min": 0, "max": 10, "step": 0.5, "value": 2.0}], "pkgs": ["numpy", "matplotlib"]}
def dist_copy(live):
    t = tempfile.mkdtemp(prefix="e38j3-"); d = os.path.join(t, "d"); shutil.copytree(DIST, d); how = "no live data"
    for m in glob.glob(os.path.join(d, "huelle", "*", "manifest.json")):
        j = json.load(open(m, encoding="utf-8")); j["pyodide"] = "/pyodide/0.27.7/"; json.dump(j, open(m, "w", encoding="utf-8"))
    for p in glob.glob(os.path.join(d, "inhalt", "*", "*", "daten.json")):
        j = json.load(open(p, encoding="utf-8"))
        for r in j.get("regler", []):
            if not live:
                r.pop("py", None); r.pop("live", None)
            elif r.get("nr") == 0:
                how = "P4" if r.get("py") else "stand-in regler[0].py"
                r.setdefault("py", LIVE)
        json.dump(j, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    return d, how

STUB = r"""window.loadPyodide = function (o) { window.__j3idx = o && o.indexURL; var calls = window.__j3calls = [];
  var P = { loadPackage: function (p) { calls.push(['pkg', p]); return Promise.resolve(); },
    loadPackagesFromImports: function () { return Promise.resolve(); }, setStdout: function () {}, setStderr: function () {},
    globals: { get: function () { return function () { return { get: function () { return null; } }; }; } },
    runPythonAsync: function (code) { calls.push(['run', code.slice(0, 120)]);
      var m = /json"\)\.loads\(("(?:[^"\\]|\\.)*")\)\)$/.exec(code);
      if (m) { var kw = JSON.parse(JSON.parse(m[1])); return new Promise(function (r) { setTimeout(function () {
        r('<svg xmlns="http://www.w3.org/2000/svg" class="j3-live" width="660" height="390" data-kw=\'' + JSON.stringify(kw) + '\'><rect width="660" height="390" fill="#123"/><text x="20" y="40" fill="#fc6" font-size="28">live ' + JSON.stringify(kw) + '</text></svg>'); }, 60); }); }
      return Promise.resolve(); } };
  return new Promise(function (r) { setTimeout(function () { r(P); }, 400); }); };"""
SLOW = r"""(function () { var D0 = window.DecompressionStream; if (!D0) return;
  window.DecompressionStream = function (f) { var d = new D0(f), ts = new TransformStream({ transform: function (c, k) { return new Promise(function (r) { setTimeout(function () { k.enqueue(c); r(); }, 2500); }); } });
    return { writable: d.writable, readable: d.readable.pipeThrough(ts) }; }; })();"""
SL = """(nr) => { var el = document.querySelectorAll('.nbrw-slider[data-z]')[nr];
  for (var x = el.parentElement; x; x = x.parentElement) if (x.tagName === 'DETAILS' && !x.open) x.open = true;
  var r = el.querySelector('.nbrw-range'), o = el.querySelector('.nbrw-val'), f = el.querySelector('.nbrw-fig');
  return {vis: !!(r.getClientRects().length && getComputedStyle(r).display !== 'none'), min: r.min, max: r.max, step: r.step, value: r.value,
          out: o ? o.textContent : '', frame: el.getAttribute('data-frame'), live: el.getAttribute('data-live'), ready: el.getAttribute('data-ready'),
          svg: !!f.querySelector('svg'), liveSvg: (f.querySelector('svg.j3-live') || {getAttribute: function () { return null; }}).getAttribute('data-kw')}; }"""
MOVE = """([nr, v]) => { var el = document.querySelectorAll('.nbrw-slider[data-z]')[nr], r = el.querySelector('.nbrw-range');
  var f0 = el.getAttribute('data-frame'); r.value = String(v); r.dispatchEvent(new Event('input', {bubbles: true}));
  return {before: f0, after: el.getAttribute('data-frame'), out: (el.querySelector('.nbrw-val') || {}).textContent}; }"""

def pg_for(b, base, tv, nid, v, init="", py=True):
    c = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark")
    c.add_init_script("try { localStorage.setItem('digichemjn.%s.reader.skin', 'digi'); localStorage.setItem('digichemjn.%s.reader.theme', 'dark'); } catch (e) {}" % (nid, nid))
    if init: c.add_init_script(init)
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/cdn.jsdelivr.net/**", lambda r: r.abort())
    if py: pg.route("**/pyodide/0.27.7/pyodide.js", lambda r: r.fulfill(status=200, content_type="text/javascript", body=STUB))
    else: pg.route("**/pyodide/0.27.7/pyodide.js", lambda r: r.fulfill(status=404, body="no"))
    pg.goto(base + "huelle/%s/lesen.html?nb=%s&v=%s" % (tv, nid, v)); pg.wait_for_selector("html[data-nbl=bereit]", timeout=30000)
    pg.evaluate("() => window.__nbReader.show('doc')")
    return c, pg, errs

def j3(b, tv, nid, v):
    d, how = dist_copy(False); srv, base = serve(d)
    # J3a — at once, before the pictures are unpacked
    c, pg, errs = pg_for(b, base, tv, nid, v, init=SLOW); pg.wait_for_timeout(300)
    a0 = pg.evaluate(SL, 0); m = pg.evaluate(MOVE, [0, 4]); pg.wait_for_timeout(3500); a1 = pg.evaluate(SL, 0)
    row("J3a", a0["vis"] and not a0["ready"] and a1["ready"] == "1" and a1["frame"] is not None and a1["value"] == "4" and "7.5" in a1["out"],
        "at start: visible %s, ready %s · moved to stage 4 · unpacked: ready %s frame %s value %s %r" % (a0["vis"], a0["ready"], a1["ready"], a1["frame"], a1["value"], a1["out"]))
    c.close()
    # J3b — the preview at once (no live data)
    c, pg, errs = pg_for(b, base, tv, nid, v); pg.wait_for_timeout(900)
    b0 = pg.evaluate(SL, 0); m = pg.evaluate(MOVE, [0, 4]); b1 = pg.evaluate(SL, 0)
    row("J3b", b0["ready"] == "1" and m["after"] != m["before"] and "7.5" in (m["out"] or "") and b1["svg"],
        "stage 4: frame %s → %s in the same task, %r" % (m["before"], m["after"], m["out"]))
    c.close(); srv.shutdown()
    # J3c — live by Python in the browser
    d, how = dist_copy(True); srv, base = serve(d)
    c, pg, errs = pg_for(b, base, tv, nid, v); pg.wait_for_timeout(900)
    c0 = pg.evaluate(SL, 0); m = pg.evaluate(MOVE, [0, 3.5]); c1 = pg.evaluate(SL, 0)
    pg.wait_for_function("() => { var e = document.querySelectorAll('.nbrw-slider[data-z]')[0]; return e.getAttribute('data-live') === 'live' && e.querySelector('svg.j3-live'); }", timeout=15000)
    pg.wait_for_timeout(300); c2 = pg.evaluate(SL, 0); calls = pg.evaluate("() => window.__j3calls || []")
    if shots:
        pg.evaluate("() => document.querySelectorAll('.nbrw-slider[data-z]')[0].scrollIntoView({block: 'center'})"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(shots, "E38-js-J3-regler-live.png"))
    pk = [x[1] for x in calls if x[0] == "pkg"]
    row("J3c", c0["min"] == "0" and c0["max"] == "10" and c0["step"] == "0.5" and c0["live"] == "vorschau" and m["after"] not in (None, "live")
        and c1["live"] in ("laedt", "live") and c2["live"] == "live" and c2["liveSvg"] == '{"a":3.5}' and "3.5" in c2["out"] and pk and "matplotlib" in pk[0],
        "%s · range %s…%s step %s, %s → move 3.5: preview frame %s, %s → %s, picture kw %s, %r, packages %s" % (how, c0["min"], c0["max"], c0["step"],
        c0["live"], m["after"], c1["live"], c2["live"], c2["liveSvg"], c2["out"], pk))
    if errs: row("J3-", False, "page errors: %s" % errs[:3])
    c.close()
    # J3d — no Python: the preview stays
    c, pg, errs = pg_for(b, base, tv, nid, v, py=False); pg.wait_for_timeout(900)
    m = pg.evaluate(MOVE, [0, 3.5]); pg.wait_for_timeout(2500); e = pg.evaluate(SL, 0)
    row("J3d", e["live"] == "aus" and e["svg"] and e["frame"] not in (None, "live"), "pyodide.js 404: data-live %s, picture %s, frame %s" % (e["live"], e["svg"], e["frame"]))
    c.close(); srv.shutdown()

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src, "· dist:", DIST)
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    tv, nid, v = ids()
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    try:
        for k, fn in (("J3", lambda: j3(b, tv, nid, v)),):
            if not want(k): continue
            try: fn()
            except Exception as e: row(k, False, "BAD %s" % str(e).splitlines()[0][:200])
    finally:
        b.close(); p.stop()
    print("REGRESS-JS-E38-J3 %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
