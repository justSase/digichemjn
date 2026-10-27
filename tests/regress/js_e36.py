"""E36 J2 · JS — DIE HÜLLE LÄDT DAS PAKET, OHNE KERNEL (Werkstatt JS, 2026-10-19).
    python3 tests/regress/js_e36.py [<notebook.ipynb>|--nb vorlage] [--dist DIR] [--shots DIR] [--json out.json]

lesen.html?nb=<id>&v=<NB_VERSION> (toolkit/js/huelle/: lesen.html.in + lader.js, claude/VERTRAG-E36.md) über http,
echter Chromium. Das Paket: `--dist DIR`, sonst <repo>/dist (Python P3), sonst eine STAND-IN nach dem Vertrag aus dem
Lauf des Notebooks (Lesefassung = die heutige Ausgabe ohne _NBREAD_CSS und ohne Reader-<script>; CSS = _NBREAD_CSS;
reader.js = _NBRW_REHYD + 20-reader.js mit Platzhaltern) — Zeile „paket: real|stand-in“. Hashed Namen bekommen
Cache-Control immutable, lesen.html/meta/manifest no-cache (wie ein Server es soll; Hosting entscheidet der Nutzer).
  L1 laden          oben, frisches Profil: data-nbl=bereit, genau eine .nbrw auf der Vorschau, data-nbrw-id = meta.id,
                    Titel = meta.title, 0 Anfragen an fremde Adressen, 0 an /api/ (kein Jupyter), 0 Websockets, 0 Fehler
  L2 Play           → Dokument, Kapitelmarken = Kapitel des Laufs
  L3 Schlüssel      dieselben Handgriffe (◐, Modus calc, t1 falsch, t1 richtig) im Notebook-Lesefenster (Ausgabe des
                    Kernels in einem iframe, wie env_reader) und in lesen.html: dieselbe Menge Schlüssel digichemjn.*;
                    t1 im Notebook gelöst → lesen.html zeigt t1 gelöst (gemeinsamer Fortschritt, gleicher Ursprung)
  L4 Regler         ein .nbrw-range bewegt → data-frame und Bild wechseln (Reglerbilder aus dem Paket)
  L5 wie env_reader lesen.html als Ausgabe-iframe: env_reader.check (W1–W8, en + de über &lang=de), kept (W6 ohne ↕: E38a J1, W10),
                    check3 (C1, C2, A1, G1, X1, M1, D1, R1 ▶ Pyodide lokal, R2 ohne Netz)
  L6 Fehler         nb unbekannt / nb=../x → data-nbl=fehler und ein sichtbarer Satz (kein leeres Weiß)
  L7 Hüllen-Version meta.toolkit = vorhandene andere Hülle → dorthin (einmal, tk=); = fehlende → bleibt hier, bereit
  INFO              Größen Hülle/Paket roh/gzip; Ladezeit kalt/warm (CPU ×4, 150 ms; warm = neu geöffnet, nicht neu geladen):
                    erstes Bild (Ladezeile), Vorschau bedienbar (data-nbl=bereit), Antworten / aus dem Zwischenspeicher
v1.81: rot (keine Hülle, kein lader.js). exit 0 = REGRESS-JS-E36 OK."""
import sys, os, re, json, gzip, shutil, hashlib, tempfile, threading, functools
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import env_reader as ER
from env_iframe import run_cell, host_page

def sha8(b): return hashlib.sha256(b).hexdigest()[:8]

def toolkit_versions():
    s = open(os.path.join(ROOT, "toolkit", "chapter_template.py"), encoding="utf-8").read()
    return (re.search(r'^NB_VERSION = "([^"]+)"', s, re.M).group(1), re.search(r'^TOOLKIT_VERSION = "([^"]+)"', s, re.M).group(1),
            re.search(r'^_NBRW_REHYD = r"""(.*?)"""', s, re.M | re.S).group(1))

def reading_html(outs):
    for o in outs:
        h = o["data"].get("text/html") or ""
        if h.startswith("<div class='nbreading'"): return h
    raise SystemExit("BAD no reading version in the run")

def split_reading(h):
    """today's output → (lesefassung, css): the first <style> (_NBREAD_CSS) and the reader <script> after the div go"""
    a = h.find("<style>"); b = h.find("</style>", a)
    s = h.rfind("<script>")
    if a < 0 or b < 0 or s < 0 or not h[s:].startswith("<script>(function(){var me=document.currentScript"):
        raise SystemExit("BAD reading output not as in v1.81 (no _NBREAD_CSS / reader script)")
    return h[:a] + h[b + 8:s], h[a + 7:b]

def standin(R, nb, outs_en, outs_de, nbv, tv, rehyd):
    """dist/ after claude/VERTRAG-E36.md, from the run (only where Python's P1–P3 are not merged yet)"""
    md = json.load(open(nb, encoding="utf-8"))["metadata"]["digichemjn"]
    pk = os.path.join(R, "inhalt", md["id"], nbv); os.makedirs(pk)
    css = None
    for lang, outs in (("en", outs_en), ("de", outs_de)):
        lf, css = split_reading(reading_html(outs))
        open(os.path.join(pk, "lesefassung.%s.html" % lang), "w", encoding="utf-8").write(lf)
    json.dump({"id": md["id"], "nb_version": nbv, "toolkit": tv, "langs": ["en", "de"], "lang": "en",
               "title": {"en": md.get("title"), "de": md.get("title_de")}}, open(os.path.join(pk, "meta.json"), "w"))
    json.dump({}, open(os.path.join(pk, "daten.json"), "w"))
    reader = rehyd + open(os.path.join(ROOT, "toolkit", "js", "20-reader.js"), encoding="utf-8").read()
    huelle(R, tv, {"reader.css": css}, reader)
    return md["id"]

def huelle(R, tv, cssfiles, reader):
    hd = os.path.join(R, "huelle", tv); os.makedirs(hd, exist_ok=True)
    src = os.path.join(ROOT, "toolkit", "js", "huelle")
    if not os.path.isfile(os.path.join(src, "lader.js")): raise SystemExit("BAD no lader (toolkit/js/huelle/lader.js)")
    man = {"toolkit": tv, "css": [], "js": {}, "fonts": [], "pyodide": None}
    def put(name, text):
        b = text.encode("utf-8"); stem, ext = os.path.splitext(name); n = "%s.%s%s" % (stem, sha8(b), ext)
        open(os.path.join(hd, n), "wb").write(b); return n
    for n, t in cssfiles.items(): man["css"].append(put(n, t))
    man["js"]["reader"] = put("reader.js", reader)
    man["js"]["lader"] = put("lader.js", open(os.path.join(src, "lader.js"), encoding="utf-8").read())
    open(os.path.join(hd, "lesen.html"), "w", encoding="utf-8").write(
        open(os.path.join(src, "lesen.html.in"), encoding="utf-8").read().replace("__LADER__", man["js"]["lader"]))
    json.dump(man, open(os.path.join(hd, "manifest.json"), "w"))

def serve(d):
    import http.server, socketserver
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def end_headers(self):
            p = self.path.split("?")[0]
            self.send_header("Cache-Control", "public, max-age=31536000, immutable" if re.search(r"\.[0-9a-f]{8}\.\w+$", p) else "no-cache")
            super().end_headers()
    class S(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True
    s = S(("127.0.0.1", 0), functools.partial(Q, directory=d))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s

def size(d, pred=lambda n: True):
    raw = gz = 0
    for r, _, fs in os.walk(d):
        for f in fs:
            if pred(f):
                b = open(os.path.join(r, f), "rb").read(); raw += len(b); gz += len(gzip.compress(b, 9))
    return raw, gz

READY = "() => ['bereit', 'fehler'].indexOf(document.documentElement.getAttribute('data-nbl')) >= 0"
# the folds' keys (.reader.acc.*) do not count: 20-reader stores a fold on its 'toggle' event, and whether the start
# state of a <details open> fires one after the reader listens is a matter of timing — measured in the NOTEBOOK's window
# itself: once 0, once 27 keys on a fresh load (the same in lesen.html)
KEYS = "() => Object.keys(localStorage).filter(function (k) { return k.indexOf('digichemjn.') === 0 && !/\\.reader\\.acc\\./.test(k); }).sort()"

def steps(S, fr, pg, play=True):
    """◐, mode calc, t1 wrong, t1 right — the same in the notebook's window and in lesen.html"""
    if play: S(ER.PLAY); pg.wait_for_timeout(300)
    S("() => document.querySelector('.nbrw-btn[data-act=\"theme\"]').click()")
    fr.click(".nbrw-btn[data-act=cover]"); pg.wait_for_timeout(150)
    fr.click('.nbrw-mode-opt[data-mode="calc"]'); fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(300)
    a = S("() => JSON.parse(atob(document.querySelector('.nbrw-task[data-task=t1]').getAttribute('data-a')))")
    for good in (False, True):
        S("() => document.querySelector('.nbrw-task[data-task=t1]').scrollIntoView({block: 'center'})")
        for x in a.get("f", []):
            fr.fill('.nbrw-task[data-task=t1] .nbrw-input[data-f="%s"]' % x[0], str(x[1] + (0 if good else 3 * x[2] + 1)))
        fr.click(".nbrw-task[data-task=t1] .nbrw-check"); pg.wait_for_timeout(250)
    return S("() => document.querySelector('.nbrw-task[data-task=t1]').getAttribute('data-st')")

def lesen_host(url):
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:#ffffff;color:#1f2328'>"
            "<iframe class='out' style='display:block;width:100%%;border:0;height:40px' src='%s'></iframe>"
            "<div style='height:2400px'></div><script>function fit(){document.querySelectorAll('iframe.out').forEach(function(f){try{"
            "var d=f.contentDocument;if(d&&d.documentElement){f.style.height=Math.max(1,d.documentElement.scrollHeight)+'px';}}catch(e){}});}"
            "setInterval(fit,150);</script>" % url)

def main():
    import nbpick
    args = sys.argv[1:]
    src = nbpick.from_argv(sys.argv)
    shots = args[args.index("--shots") + 1] if "--shots" in args else None
    jout = args[args.index("--json") + 1] if "--json" in args else None
    dist = args[args.index("--dist") + 1] if "--dist" in args else os.path.join(ROOT, "dist")
    md = json.load(open(src, encoding="utf-8"))["metadata"]["digichemjn"]
    if md["id"] in ER.CODE_T1: ER.RIGHT, ER.WRONG, ER.BROKEN, ER.FNAME = ER.CODE_T1[md["id"]]
    nbv, tv, rehyd = toolkit_versions()
    rows, fails = [], []
    def bad(m): fails.append(m)
    R = tempfile.mkdtemp(prefix="jse36_")
    outs_en, e1, ch_en = run_cell(src, {})
    outs_de, e2, ch_de = run_cell(src, {"DIGICHEM_LANG": "de"})
    if e1 or e2: bad("the run raised: %s" % (e1 + e2)[:1])
    nid = md["id"]
    real = os.path.isfile(os.path.join(dist, "huelle", tv, "manifest.json")) and os.path.isfile(os.path.join(dist, "inhalt", nid, nbv, "meta.json"))
    try:
        if real:
            shutil.copytree(os.path.join(dist, "huelle"), os.path.join(R, "huelle"))
            shutil.copytree(os.path.join(dist, "inhalt"), os.path.join(R, "inhalt"))
            if not os.path.isfile(os.path.join(R, "huelle", tv, "lesen.html")): bad("L1 dist/huelle/%s has no lesen.html" % tv)
        else:
            standin(R, src, outs_en, outs_de, nbv, tv, rehyd)
    except SystemExit as e:
        print("FAILURES:\n- %s" % e); sys.exit(1)
    rows.append("paket: %s (%s, Hülle %s, %s)" % ("real " + dist if real else "stand-in nach VERTRAG-E36", nid, tv, nbv))
    hr, hg = size(os.path.join(R, "huelle", tv)); pr, pg_ = size(os.path.join(R, "inhalt", nid, nbv))
    rows.append("INFO Größe: Hülle %d B roh / %d B gzip · Paket %d B roh / %d B gzip" % (hr, hg, pr, pg_))
    # L7 fixtures: the same package built against another shell (present) and a missing one
    pk = os.path.join(R, "inhalt", nid, nbv); man = json.load(open(os.path.join(R, "huelle", tv, "manifest.json")))
    for vv, tk in (("zz-x", "zz-huelle"), ("zz-y", "zz-fehlt")):
        d = os.path.join(R, "inhalt", nid, vv); shutil.copytree(pk, d)
        m = json.load(open(os.path.join(d, "meta.json"))); m["toolkit"] = tk; json.dump(m, open(os.path.join(d, "meta.json"), "w"))
    shutil.copytree(os.path.join(R, "huelle", tv), os.path.join(R, "huelle", "zz-huelle"))
    m2 = json.load(open(os.path.join(R, "huelle", "zz-huelle", "manifest.json"))); m2["toolkit"] = "zz-huelle"
    json.dump(m2, open(os.path.join(R, "huelle", "zz-huelle", "manifest.json"), "w"))
    meta = json.load(open(os.path.join(pk, "meta.json")))
    open(os.path.join(R, "nb.html"), "w", encoding="utf-8").write(host_page(outs_en, False).replace(
        "</iframe><script>", "</iframe><div style='height:2400px'></div><script>", 1))
    srv = serve(R); base = "http://127.0.0.1:%d/" % srv.server_address[1]
    L = "huelle/%s/lesen.html?nb=%s&v=%s" % (tv, nid, nbv)
    for n, u in (("host_en.html", L), ("host_de.html", L + "&lang=de")):
        open(os.path.join(R, n), "w", encoding="utf-8").write(lesen_host(u))
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            # L1 + L2
            ctx = b.new_context(viewport={"width": 1400, "height": 900})
            reqs, ws, errs = [], [], []
            pg = ctx.new_page()
            pg.on("request", lambda r: reqs.append(r.url)); pg.on("websocket", lambda w: ws.append(w.url))
            pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
            pg.on("console", lambda m: errs.append("console " + m.text[:120]) if m.type == "error" else None)
            pg.goto(base + L); pg.wait_for_function(READY, timeout=30000)
            r = pg.evaluate("""() => { var w = document.querySelectorAll('.nbrw'), x = w[0], rd = document.querySelector('.nbreading');
              return {nbl: document.documentElement.getAttribute('data-nbl'), n: w.length, view: x && x.getAttribute('data-nbrw-view'),
                      id: rd && rd.getAttribute('data-nbrw-id'), wid: x && x.getAttribute('data-nbrw-id'), title: document.title,
                      lang: document.documentElement.lang, z: window.DIGICHEMJN.zeit, err: window.DIGICHEMJN.fehler || ''}; }""")
            own = [u for u in reqs if not u.startswith(base) and not u.startswith("data:")]
            api = [u for u in reqs if "/api/" in u]
            files = sorted(set(re.sub(r"\?.*", "", u[len(base):]) for u in reqs if u.startswith(base)))
            rows.append("L1 lesen.html: %s, %d Fenster, Ansicht %s, id %s/%s, Titel %r, lang %s · Anfragen %d (%s) · fremd %d · /api/ %d · ws %d · Fehler %d" % (
                r["nbl"], r["n"], r["view"], r["id"], r["wid"], r["title"], r["lang"], len(reqs), ", ".join(os.path.basename(f) for f in files), len(own), len(api), len(ws), len(errs)))
            if r["nbl"] != "bereit" or r["n"] != 1 or r["view"] != "cover": bad("L1 not started: %s" % r)
            if r["id"] != meta["id"] or r["wid"] != meta["id"]: bad("L1 id %s / %s, want %s" % (r["id"], r["wid"], meta["id"]))
            mt = (meta.get("title") or meta.get("titel") or {}).get("en")
            if r["title"] != mt: bad("L1 title %r, want %r" % (r["title"], mt))
            if own or api or ws: bad("L1 requests outside the package: %s %s %s" % (own[:3], api[:3], ws[:3]))
            if errs: bad("L1 errors: %s" % errs[:3])
            v = pg.evaluate(ER.PLAY); pg.wait_for_timeout(300)
            mk = pg.evaluate("() => document.querySelectorAll('.nbrw-mark[data-kind=chap]').length")
            rows.append("L2 Play → %s, Kapitelmarken %d / %d" % (pg.evaluate("() => document.querySelector('.nbrw').getAttribute('data-nbrw-view')"), mk, len(ch_en)))
            if mk != len(ch_en) or pg.evaluate("() => document.querySelector('.nbrw').getAttribute('data-nbrw-view')") != "doc": bad("L2 Play/marks: %d of %d" % (mk, len(ch_en)))
            # L4 slider
            sl = pg.evaluate("""() => { var e = document.querySelector('.nbrw-slider[data-ready="1"]'); if (!e) return null;
              var r = e.querySelector('.nbrw-range'), f0 = e.getAttribute('data-frame'), h0 = e.querySelector('.nbrw-fig').innerHTML.length,
                  s0 = e.querySelector('.nbrw-fig').innerHTML;
              r.value = String(+r.value === +r.max ? +r.min : +r.max); r.dispatchEvent(new Event('input'));
              return {f0: f0, f1: e.getAttribute('data-frame'), changed: e.querySelector('.nbrw-fig').innerHTML !== s0, n: document.querySelectorAll('.nbrw-slider[data-ready="1"]').length}; }""")
            rows.append("L4 Regler: %s" % sl)
            if not sl or sl["f0"] == sl["f1"] or not sl["changed"]: bad("L4 slider did not change the picture: %s" % sl)
            if shots:
                os.makedirs(shots, exist_ok=True)
                pg.screenshot(path=os.path.join(shots, "E36-js-lesen-digi.png"))
            ctx.close()
            if shots:   # the screenshot of the round: style minimal, light, 1400 × 900
                ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="light")
                ctx.add_init_script("try{localStorage.setItem('digichemjn.%s.reader.skin','minimal')}catch(e){}" % nid)
                pg = ctx.new_page(); pg.goto(base + L); pg.wait_for_function(READY, timeout=30000); pg.wait_for_timeout(500)
                pg.screenshot(path=os.path.join(shots, "E36-js-lesen-minimal-hell.png")); ctx.close()
            # L3 the same keys as the notebook's window, shared progress
            ka = {}
            for tag, url in (("nb", "nb.html"), ("lesen", "host_en.html")):
                ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
                pg.goto(base + url); pg.wait_for_timeout(3000)
                fr, fe = ER.frame(pg); S = lambda js, a=None: fr.evaluate(js, a)
                st = steps(S, fr, pg)
                ka[tag] = (st, [re.sub(r"^digichemjn\.", "", k) for k in S(KEYS)])
                if tag == "nb":     # the same browser profile opens lesen.html: t1 is solved there too
                    q = ctx.new_page(); q.goto(base + L); q.wait_for_function(READY, timeout=30000); q.evaluate(ER.PLAY); q.wait_for_timeout(300)
                    ka["shared"] = q.evaluate("() => document.querySelector('.nbrw-task[data-task=t1]').getAttribute('data-st')")
                ctx.close()
            rows.append("L3 Schlüssel: Notebook t1 %s %s · lesen t1 %s %s · lesen nach Notebook: t1 %s" % (
                ka["nb"][0], ka["nb"][1], ka["lesen"][0], ka["lesen"][1], ka["shared"]))
            if ka["nb"][1] != ka["lesen"][1] or not ka["lesen"][1]: bad("L3 keys differ: notebook %s, lesen %s" % (ka["nb"][1], ka["lesen"][1]))
            if ka["lesen"][0] != "solved" or ka["shared"] != "solved": bad("L3 progress: lesen t1 %s, after the notebook %s" % (ka["lesen"][0], ka["shared"]))
            # L5 env_reader's rows on lesen.html in an output frame
            for tag, url, lang, nch in (("lesen en", "host_en.html", "en", len(ch_en)), ("lesen de", "host_de.html", "de", len(ch_de))):
                ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
                pg.goto(base + url); pg.wait_for_timeout(3000)
                n0 = len(fails); ER.check(pg, tag, nch, lang, fails, rows, None)
                if lang == "en" and len(fails) == n0:
                    # E38a J1 (JS, 26.10.): lesen.html has no ↕ — the page sets the window's height (js_e38a J1a).
                    # W6 BEHAUPTETE BISHER „↕+ ×2 = +200 px, kept“ auch hier; nun: die Höhe bleibt, A+ weiter gemerkt.
                    kf = []; ER.kept(pg, tag, kf, rows)
                    for f in kf:
                        m = re.search(r" W6 .*: \[(\d+), ([\d.]+)\], want \[(\d+), ([\d.]+)\]$", f)
                        if m and int(m.group(1)) == int(m.group(3)) - 200 and abs(float(m.group(2)) - float(m.group(4))) <= 0.05:
                            rows.append("%s W6 (E38a J1) height stays %s px in lesen.html (no ↕)" % (tag, m.group(1))); continue
                        fails.append(f)
                ctx.close()
            ER.check3(b, base, "host_en.html", "lesen en", fails, rows, None, [], ch_de)
            # L6
            ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
            for q in ("nb=gibtsnicht&v=%s" % nbv, "nb=../x"):
                pg.goto(base + "huelle/%s/lesen.html?%s" % (tv, q)); pg.wait_for_function(READY, timeout=20000)
                e = pg.evaluate("() => { var m = document.getElementById('nbl-msg'); return [document.documentElement.getAttribute('data-nbl'), m && m.getClientRects().length ? m.textContent : '']; }")
                rows.append("L6 %s → %s %r" % (q, e[0], e[1][:70]))
                if e[0] != "fehler" or len(e[1]) < 20: bad("L6 %s: %s" % (q, e))
            # L7
            for vv, want in (("zz-x", "/huelle/zz-huelle/"), ("zz-y", "/huelle/%s/" % tv)):
                pg.goto(base + "huelle/%s/lesen.html?nb=%s&v=%s" % (tv, nid, vv)); pg.wait_for_timeout(400); pg.wait_for_function(READY, timeout=30000)
                e = pg.evaluate("() => [document.documentElement.getAttribute('data-nbl'), location.pathname + location.search, window.DIGICHEMJN.andereHuelle || '', window.DIGICHEMJN.toolkit]")
                rows.append("L7 meta.toolkit von %s → %s %s %s" % (vv, e[0], e[1], e[2]))
                if e[0] != "bereit" or want not in e[1]: bad("L7 %s: %s, want %s" % (vv, e, want))
            ctx.close()
            # INFO load time: CPU ×4, 150 ms latency, cold (fresh profile) and warm (reload, HTTP cache)
            ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
            cdp = ctx.new_cdp_session(pg); cdp.send("Network.enable")
            cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": -1, "uploadThroughput": -1})
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
            net = {"n": 0, "cache": set()}       # from the cache: memory (requestServedFromCache) or disk (fromDiskCache)
            def resp(ev):
                net["n"] += 1
                if ev["response"].get("fromDiskCache"): net["cache"].add(ev["requestId"])
            cdp.on("Network.responseReceived", resp)
            cdp.on("Network.requestServedFromCache", lambda ev: net["cache"].add(ev["requestId"]))
            T = """() => { var p = performance.getEntriesByName('first-contentful-paint')[0], z = window.DIGICHEMJN.zeit;
              return [p ? Math.round(p.startTime) : null, z.bereit, z.css, z.geladen]; }"""
            for k in ("kalt", "warm"):
                net["n"] = 0; net["cache"] = set()
                pg.goto(base + L if k == "kalt" else base + "huelle/%s/lesen.html?v=%s&nb=%s" % (tv, nbv, nid))   # warm: opened again
                pg.wait_for_function(READY, timeout=60000); pg.wait_for_timeout(300)
                t = pg.evaluate(T)
                rows.append("INFO Ladezeit %s (CPU ×4, 150 ms): erstes Bild (Ladezeile) %s ms, Vorschau bedienbar %s ms (CSS %s, Paket %s) · Antworten %d, aus dem Zwischenspeicher %d" % (
                    k, t[0], t[1], t[2], t[3], net["n"], len(net["cache"])))
            ctx.close()
        except Exception as e:
            fails.append("BAD %s" % str(e)[:300])
        b.close()
    srv.shutdown(); shutil.rmtree(R, ignore_errors=True)
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-JS-E36 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
