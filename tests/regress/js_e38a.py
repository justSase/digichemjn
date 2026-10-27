"""E38a · JS — LESEFENSTER-RESTE (Werkstatt JS, 2026-10-26).
    python3 tests/regress/js_e38a.py [<notebook.ipynb>|--nb vorlage] [--dist DIR] [--only J1,J2,J3] [--shots DIR]

plan/AUFTRAG.md J1–J3. Die Hülle: `--dist DIR`, sonst <repo>/dist (der Bau legt sie an), über http, echter Chromium.
  J1a  lesen.html volle Höhe   1366 × 900 und 390 × 844: .nbrw unten = Fensterhöhe (±1 px), die Seite scrollt nicht,
                               ↕ (rows h) nicht sichtbar; nach Play (Dokument) ebenso; Fenster auf 1366 × 700 → folgt
  J1b  Jupyter-Regel bleibt    dieselbe Lesefassung + reader.js in einer Seite OHNE Lader (wie eine Ausgabe in PyCharm/
                               VS Code/Colab): Fenster = screen.availHeight − 240 (±10), ↕ sichtbar, ↕+ → +100 px
  J2a  manifest.pyodide gesetzt  Kopie der Hülle mit "pyodide": "/pyodide/0.27.7/" → ▶ der ersten Code-Aufgabe lädt
                               <origin>/pyodide/0.27.7/pyodide.js (Stub), indexURL = diese Adresse, 0 Anfragen an jsDelivr
  J2b  manifest.pyodide null   wie heute: pyodide.js von cdn.jsdelivr.net (Anfrage abgefangen, nicht geladen)
  J3   Rolle weg               echtes JupyterLab, frisches Profil MIT altem digichemjn.role.v1.<id> = administrator:
                               __nbRole() = reader, body ohne .nbadmin, der alte Schlüssel gelöscht, 👤 → Einstellungen
                               ohne select[data-k=role], keine sichtbare Option „administrator“/„teaching the course“
v1.82 (`2bb91ab5`): rot J1a (Fenster = Bildschirm − 240), J2a (jsDelivr), J3 (administrator, nbadmin, Rolle in den
Einstellungen); grün J1b, J2b (sie wachen über „Jupyter bleibt wie es war“). Owner: JS. exit 0 = REGRESS-JS-E38A OK."""
import sys, os, re, json, glob, shutil, tempfile, threading, functools, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e38a is a stand-alone script")
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

def hull_copy(pyodide):
    """the built dist/ in a temp dir; manifest.pyodide set (J2a) or left as built"""
    t = tempfile.mkdtemp(prefix="e38a-"); shutil.copytree(DIST, os.path.join(t, "d"))
    d = os.path.join(t, "d")
    if pyodide is not False:
        for m in glob.glob(os.path.join(d, "huelle", "*", "manifest.json")):
            j = json.load(open(m, encoding="utf-8")); j["pyodide"] = pyodide
            json.dump(j, open(m, "w", encoding="utf-8"), indent=1)
    return d

def ids():
    h = glob.glob(os.path.join(DIST, "huelle", "*", "manifest.json"))
    if not h: raise SystemExit("BAD no hull under %s (build first: cd vorlage && python3 build_vorlage.py)" % DIST)
    tv = os.path.basename(os.path.dirname(sorted(h)[-1]))
    pk = sorted(glob.glob(os.path.join(DIST, "inhalt", "*", "*", "meta.json")))[0]
    meta = json.load(open(pk, encoding="utf-8"))
    return tv, meta["id"], os.path.basename(os.path.dirname(pk))

GEO = """() => { var w = document.querySelector('.nbrw'), win = document.querySelector('.nbrw-win');
  var hr = document.querySelector('.nbrw [data-act="h+"]'), r = w.getBoundingClientRect();
  var hv = !!(hr && hr.getClientRects().length && getComputedStyle(hr.parentNode).display !== 'none');
  return {ih: innerHeight, avail: screen.availHeight, top: Math.round(r.top), bottom: Math.round(r.bottom),
          win: Math.round(win.getBoundingClientRect().height), sh: document.documentElement.scrollHeight, hbtn: hv}; }"""

def j1(b, tv, nid, v):
    srv, base = serve(DIST)
    url = base + "huelle/%s/lesen.html?nb=%s&v=%s" % (tv, nid, v)
    for w, hh in ((1366, 900), (390, 844)):
        c = b.new_context(viewport={"width": w, "height": hh}); pg = c.new_page()
        pg.goto(url); pg.wait_for_selector("html[data-nbl=bereit]", timeout=30000); pg.wait_for_timeout(1200)
        a = pg.evaluate(GEO)
        pg.evaluate("() => { var p = document.querySelector('.nbrw [data-nbrw-act=play]'); if (p) p.click(); }")
        pg.wait_for_timeout(1200); d = pg.evaluate(GEO)
        if shots and w == 1366: pg.screenshot(path=os.path.join(shots, "E38a-js-J1-lesen-volle-hoehe.png"))
        ok = all(abs(x["bottom"] - x["ih"]) <= 1 and x["sh"] <= x["ih"] + 1 and not x["hbtn"] for x in (a, d))
        if w == 1366:
            pg.set_viewport_size({"width": 1366, "height": 700}); pg.wait_for_timeout(900); r = pg.evaluate(GEO)
            ok = ok and abs(r["bottom"] - 700) <= 1 and r["sh"] <= 701
        else: r = None
        row("J1a", ok, "%d×%d cover %s · doc %s%s" % (w, hh, a, d, (" · →700: %s" % r) if r else ""))
        c.close()
    srv.shutdown()

HOST = """<!doctype html><html><head><meta charset=utf-8>%s</head><body style="margin:0">
<div style="padding:8px">an IDE's output (no shell loader)</div>%s<script>%s</script></body></html>"""
def j1b(b, tv, nid, v):
    """the reader as an output without lesen.html's loader (PyCharm/VS Code/Colab hosts): the rule screen − 240"""
    hd = os.path.join(DIST, "huelle", tv); man = json.load(open(os.path.join(hd, "manifest.json"), encoding="utf-8"))
    css = "".join("<style>%s</style>" % open(os.path.join(hd, c), encoding="utf-8").read() for c in man["css"])
    lf = open(os.path.join(DIST, "inhalt", nid, v, "lesefassung.en.html"), encoding="utf-8").read()
    lf = lf.replace("class='nbreading'", "class='nbreading' data-nbrw-id='%s' data-nbrw-v='%s'" % (nid, v), 1)
    js = open(os.path.join(hd, man["js"]["reader"]), encoding="utf-8").read().replace("__NBREADV__", tv).replace("__NBREADID__", nid)
    t = tempfile.mkdtemp(prefix="e38a-host-")
    open(os.path.join(t, "host.html"), "w", encoding="utf-8").write(HOST % (css, lf, js.replace("</script", "<\\/script")))
    srv, base = serve(t)
    c = b.new_context(viewport={"width": 1366, "height": 900}); pg = c.new_page()
    pg.goto(base + "host.html"); pg.wait_for_selector(".nbreading[data-nbrw]", state="attached", timeout=30000); pg.wait_for_timeout(1200)
    pg.evaluate("() => { var p = document.querySelector('.nbrw [data-nbrw-act=play]'); if (p) p.click(); }"); pg.wait_for_timeout(1200)
    a = pg.evaluate(GEO)
    pg.evaluate("() => document.querySelector('.nbrw [data-act=\"h+\"]').click()"); pg.wait_for_timeout(600)
    p = pg.evaluate(GEO)
    want_h = min(2400, max(300, round((a["avail"] - 240) / 10) * 10))
    row("J1b", abs(a["win"] - want_h) <= 10 and a["hbtn"] and p["win"] - a["win"] == 100,
        "host page: window %d (want %d = avail %d − 240), ↕ shown %s, after ↕+ %d" % (a["win"], want_h, a["avail"], a["hbtn"], p["win"]))
    c.close(); srv.shutdown()

STUB = "window.loadPyodide = function (o) { window.__e38aIndex = o && o.indexURL; return Promise.reject(new Error('e38a stub')); };"
def j2(b, tv, nid, v):
    for key, py in (("J2a", "/pyodide/0.27.7/"), ("J2b", None)):
        d = hull_copy(py); srv, base = serve(d)
        c = b.new_context(viewport={"width": 1366, "height": 900}); pg = c.new_page(); reqs = []
        pg.on("request", lambda r: reqs.append(r.url))
        pg.route("**/cdn.jsdelivr.net/**", lambda r: r.abort())
        pg.route("**/pyodide/0.27.7/pyodide.js", lambda r: r.fulfill(status=200, content_type="text/javascript", body=STUB))
        pg.goto(base + "huelle/%s/lesen.html?nb=%s&v=%s" % (tv, nid, v)); pg.wait_for_selector("html[data-nbl=bereit]", timeout=30000)
        pg.wait_for_timeout(800)
        ns = pg.evaluate("() => (window.DIGICHEMJN || {}).pyodide || null")
        pg.evaluate("""() => { var r = [].filter.call(document.querySelectorAll('.nbrw-run'), function (b) {
            var t = b.closest('[data-st]'); return !t || t.getAttribute('data-st') !== 'locked'; })[0]; if (r) r.click(); }""")
        pg.wait_for_timeout(2500)
        py_req = [u for u in reqs if u.endswith("pyodide.js")]; cdn = [u for u in reqs if "jsdelivr" in u]
        idx = pg.evaluate("() => window.__e38aIndex || null")
        if key == "J2a":
            own = base + "pyodide/0.27.7/"
            row(key, ns == own and py_req == [own + "pyodide.js"] and idx == own and not cdn,
                "manifest %r → DIGICHEMJN.pyodide %r, pyodide.js %s, indexURL %r, jsDelivr %d" % (py, ns, py_req, idx, len(cdn)))
        else:
            row(key, ns is None and len(py_req) == 1 and "cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js" in py_req[0],
                "manifest null → DIGICHEMJN.pyodide %r, pyodide.js %s" % (ns, py_req))
        c.close(); srv.shutdown()

INIT = """(function(items){ try { if (sessionStorage.getItem('__e38a')) return;
  Object.keys(items).forEach(function(k){ localStorage.setItem(k, items[k]); }); sessionStorage.setItem('__e38a', '1'); } catch (e) {} })(%s);"""
J3S = """() => { var h = document.getElementById('nbpanel-root'), out = {};
  out.role = window.__nbRole ? window.__nbRole() : null; out.admin = document.body.classList.contains('nbadmin');
  out.keys = Object.keys(localStorage).filter(function (k) { return /role/.test(k); });
  if (h) { h.dataset.page = 'code'; h.classList.add('open'); }
  if (window.__nbAcctPanel && h) window.__nbAcctPanel(h);
  var vis = function (e) { return !!(e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden'); };
  out.prefs = [].map.call(document.querySelectorAll('#nbpanel-root .nbprefs select.nbpref'), function (s) { return s.getAttribute('data-k'); });
  out.roleSel = [].filter.call(document.querySelectorAll('#nbpanel-root select[data-k=role], #nbpanel-root select.nbrolepick'), vis).length;
  out.adminOpt = [].filter.call(document.querySelectorAll('#nbpanel-root option'), function (o) {
    return (o.value === 'administrator' || /teaching the course|ich unterrichte/.test(o.textContent)) && vis(o.parentNode); }).length;
  return out; }"""
def j3(src, b):
    from lab_keys import ensure_lab, kill_sessions
    sys.argv = [sys.argv[0]]
    import run as R
    BASE, LROOT = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    nid = R.nb_id(src); kill_sessions(BASE); R.set_lab_theme(BASE, "light")
    c = b.new_context(viewport={"width": 1400, "height": 900})
    c.add_init_script(INIT % json.dumps({"digichemjn.role.v1." + nid: "administrator", "digichemjn.role.v1": "administrator"}))
    name = "e38a_%d_%s" % (int(time.time() * 1000) % 1000000, os.path.basename(src))
    shutil.copy(src, os.path.join(LROOT, name))
    pg = c.new_page(); pg.goto(BASE + "/lab/tree/" + name + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(1500); R.run_front(pg, nid); pg.wait_for_timeout(2500)
    s = pg.evaluate(J3S); pg.wait_for_timeout(600)
    if shots: pg.screenshot(path=os.path.join(shots, "E38a-js-J3-ohne-rolle.png"))
    row("J3", s["role"] == "reader" and not s["admin"] and ("digichemjn.role.v1." + nid) not in s["keys"]
        and "role" not in s["prefs"] and s["prefs"] and not s["roleSel"] and not s["adminOpt"], "real Lab, stored administrator: %s" % s)
    c.close()

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src, "· dist:", DIST)
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    tv, nid, v = ids() if any(want(x) for x in ("J1a", "J1b", "J2")) else (None, None, None)
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    try:
        for k, fn in (("J1a", lambda: j1(b, tv, nid, v)), ("J1b", lambda: j1b(b, tv, nid, v)),
                      ("J2", lambda: j2(b, tv, nid, v)), ("J3", lambda: j3(src, b))):
            if not want(k): continue
            try: fn()
            except Exception as e: row(k, False, "BAD %s" % str(e).splitlines()[0][:200])
    finally:
        b.close(); p.stop()
    print("REGRESS-JS-E38A %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
