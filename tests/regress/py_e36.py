"""E36 P4 · Python — HÜLLE UND INHALT GETRENNT (Werkstatt Python, 2026-10-19; AUFTRAG E36, Plan plan/ARCHITEKTUR.md).
    python3 tests/regress/py_e36.py [--nb vorlage|<file.ipynb>] [--mit <zweites.ipynb>] [--no-browser] [--shots DIR] [--json out.json]

Der Bau schreibt neben der .ipynb Ausgang A (toolkit/paket.py, aus jedem build_*.py): dist/huelle/<TOOLKIT_VERSION>/ und
dist/inhalt/<id>/<NB_VERSION>/. Der Test baut das Paket der GEGEBENEN Datei frisch in einen leeren Ordner (zwei Kernel-Läufe,
en + de) und prüft es; liegt im Baum schon ein dist/ dieser Version, muss es dasselbe sein.
  V1  Paket vollständig: lesefassung.en.html, lesefassung.de.html, daten.json, meta.json (id, nb_version, toolkit, langs,
      lang, title en/de), inhalt/<id>/aktuell.json; meta.dateien = Bytes/sha256 der Dateien; meta.huelle führt zu
      manifest.json (toolkit, css, js.reader/js.lader, fonts, pyodide — VERTRAG-E36), jede Datei da, ihr Name trägt ihre
      sha8; lader/lesen.html genau dann, wenn toolkit/js/huelle/lader.js / lesen.html.in da sind, __LADER__ ersetzt
  H1  keine Hülle im Paket: 0 <style>, jedes <script> ist type=application/json (data-nbrw-put); kein Stück aus
      20-reader.js / _NBRW_REHYD / 15-reader.css in einer Datei des Pakets
  H2  Hülle ohne Notebook: keine Id, keine Version im Lesefenster-Skript, Platzhalter __NBREADV__/__NBREADID__ da
      (claude/VERTRAG-E36.md); Sprache egal (en = de, im Bau geprüft)
  H3  (--mit) Hülle eines zweiten Notebooks Byte für Byte gleich
  D1  daten.json: jede Rechenaufgabe der Lesefassung mit Antwort (Feld, Wert, Toleranz) bzw. Index; jede Code-Aufgabe mit
      data-check hat ihren Prüf-Code (übersetzbar); Gating (Reihenfolge, Modus), Marken, Kapitelnamen en/de gleich lang;
      Regler: Steuerung + Bilderzahl je Regler, die Bilder selbst nur einmal (in der Lesefassung)
  D0  dist/ im Baum (falls da) = frischer Bau (sonst ist es veraltet)
  R1  reproduzierbar: ein zweiter Bau gibt dieselben sha256 (Anker-Token, Seed, Radio-Namen)
  R2  Rückbau: die Ausgabe des Kernels ohne ihre <style>/<script>-Blöcke = Lesefassung (Zeichen für Zeichen), die Blöcke =
      leser.css / reader.js (bis auf Id und Version) — nichts geht verloren, nichts kommt dazu
  B1  Chromium: Ausgabe des Kernels (wie heute, eine Seite für sich) gegen Paket + Hülle (<style> im Kopf, Skript hinter dem
      Dokument) — Lesefenster gestartet, Bildschirmfotos pixelgleich: Deckblatt, nach ▶ das Dokument, 2 400 px weiter;
      1366 × 900 und 390 × 844, hell und dunkel
  S1  (INFO) Größe je Datei roh/gzip, Hülle und Paket, Kernel-Sekunden
v1.81 (Basis): rot (kein toolkit/paket.py, kein Ausgang A). Owner: Python. exit 0 = REGRESS-PY-E36 OK."""
import sys, os, re, json, gzip, hashlib, tempfile, shutil, base64
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(ROOT, "toolkit"))
sys.dont_write_bytecode = True
import nbpick

A = sys.argv[1:]
NB = nbpick.from_argv(sys.argv)
MIT = A[A.index("--mit") + 1] if "--mit" in A else None
NOBROWSER = "--no-browser" in A
SHOTS = A[A.index("--shots") + 1] if "--shots" in A else None
JOUT = A[A.index("--json") + 1] if "--json" in A else None

rows, fails = [], []
def row(name, ok, detail):
    rows.append((name, ok, detail))
    if ok is False: fails.append("%s: %s" % (name, detail))
    print("%-24s %s  %s" % (name, {True: "ok  ", False: "RED ", None: "INFO"}[ok], detail), flush=True)

def sha(b): return hashlib.sha256(b).hexdigest()
def rd(p): return open(p, "rb").read()

def finish():
    if JOUT:
        json.dump([{"name": n, "ok": o, "detail": d} for n, o, d in rows], open(JOUT, "w"), ensure_ascii=False, indent=1)
    print("REGRESS-PY-E36 OK" if not fails else "REGRESS-PY-E36 RED " + " | ".join(f[:120] for f in fails))
    sys.exit(1 if fails else 0)

try:
    import paket
except ImportError as e:
    row("V1 Paket", False, "kein toolkit/paket.py (%s) — der Bau hat keinen Ausgang A" % e); finish()

md = json.load(open(NB, encoding="utf-8"))["metadata"].get("digichemjn") or {}
if not md.get("id"):
    row("V1 Paket", False, "die Datei hat kein metadata.digichemjn.id"); finish()
NBID, NBV, TKV = md["id"], md["version"], md["toolkit"]
os.environ.pop(paket.DIST_ENV, None)
T1, T2 = tempfile.mkdtemp(prefix="py_e36a-"), tempfile.mkdtemp(prefix="py_e36b-")
LESEN, LADER = os.path.join(ROOT, "toolkit", "js", "huelle", "lesen.html.in"), os.path.join(ROOT, "toolkit", "js", "huelle", "lader.js")
res = paket.ausgaenge(NB, md, dist=T1, lesen_html=LESEN, lader_js=LADER, log=lambda s: row("S1 Bau", None, s))
P = os.path.join(T1, "inhalt", NBID, NBV)
H = os.path.join(T1, "huelle", TKV)

# ---- V1
need = ["lesefassung.en.html", "lesefassung.de.html", "daten.json", "meta.json"]
miss = [f for f in need if not os.path.isfile(os.path.join(P, f))]
extra = sorted(set(os.listdir(P)) - set(need)) if os.path.isdir(P) else []
bad, meta, man = [], {}, {}
try:
    meta = json.load(open(os.path.join(P, "meta.json"), encoding="utf-8"))
    for f, d in (meta.get("dateien") or {}).items():
        b = rd(os.path.join(P, f))
        if len(b) != d["bytes"] or sha(b) != d["sha256"]:
            bad.append("%s: meta %d B, Datei %d B" % (f, d["bytes"], len(b)))
    if set(meta.get("dateien") or {}) != set(need) - {"meta.json"}:
        bad.append("meta.dateien %s" % sorted(meta.get("dateien") or {}))
    mp = os.path.normpath(os.path.join(P, meta.get("huelle") or "?"))
    man = json.load(open(mp, encoding="utf-8"))
    if mp != os.path.join(H, "manifest.json"):
        bad.append("meta.huelle → %s" % mp)
    for fn, d in man.get("dateien", {}).items():
        b = rd(os.path.join(H, fn))
        if sha(b) != d["sha256"] or (fn != "lesen.html" and sha(b)[:8] not in fn):
            bad.append("Hülle %s: Name/sha passen nicht" % fn)
    named = list(man.get("css") or []) + [v for v in (man.get("js") or {}).values() if v]
    if not man.get("css") or not (man.get("js") or {}).get("reader") or any(n not in man["dateien"] for n in named):
        bad.append("Manifest css %s js %s" % (man.get("css"), man.get("js")))
    if man.get("toolkit") != TKV or "fonts" not in man or "pyodide" not in man:
        bad.append("Manifest toolkit/fonts/pyodide")
    if os.path.exists(LADER) != bool((man.get("js") or {}).get("lader")) or os.path.exists(LESEN) != ("lesen.html" in man["dateien"]):
        bad.append("lader/lesen.html: Quelle da %s/%s, in der Hülle %s/%s" % (os.path.exists(LADER), os.path.exists(LESEN),
                   (man.get("js") or {}).get("lader"), "lesen.html" in man["dateien"]))
    if "lesen.html" in man["dateien"] and "__LADER__" in rd(os.path.join(H, "lesen.html")).decode("utf-8"):
        bad.append("lesen.html: __LADER__ nicht ersetzt")
    if (meta.get("id") != NBID or meta.get("nb_version") != NBV or meta.get("toolkit") != TKV
            or meta.get("langs") != ["en", "de"] or meta.get("lang") not in ("en", "de")):
        bad.append("meta id/nb_version/toolkit/langs %s/%s/%s/%s" % (meta.get("id"), meta.get("nb_version"), meta.get("toolkit"), meta.get("langs")))
    if not (meta.get("title") or {}).get("en") or not (meta.get("title") or {}).get("de"):
        bad.append("Titel en/de fehlt")
    ak = json.load(open(os.path.join(T1, "inhalt", NBID, "aktuell.json")))
    if ak != {"v": NBV}:
        bad.append("aktuell.json %r" % ak)
except Exception as e:
    bad.append(repr(e)[:160])
row("V1 Paket vollständig", not miss and not extra and not bad,
    "fehlt %s · zu viel %s · %s · Hülle %s" % (miss or "nichts", extra or "nichts", "; ".join(bad) or "meta/Manifest/aktuell stimmen",
                                              sorted(man.get("dateien", {}))))

# ---- H1
SIG = ["__nbReaders", "data-nbrw-rh", ".nbrw.nbrw{", "--nbr-fg:"]      # 20-reader.js · _NBRW_REHYD · 15-reader.css · _NBREAD_CSS
h1, h1bad = [], False
for f in need:
    t = rd(os.path.join(P, f)).decode("utf-8") if os.path.isfile(os.path.join(P, f)) else ""
    if f.endswith(".html"):
        n_style = len(re.findall(r"<style\b", t, re.I))
        scr = re.findall(r"<script\b([^>]*)>", t, re.I)
        n_code = sum(1 for a in scr if not re.search(r"type\s*=\s*['\"]application/json['\"]", a, re.I))
        if n_style or n_code:
            h1bad = True
            h1.append("%s: %d <style>, %d <script> mit Code (von %d)" % (f, n_style, n_code, len(scr)))
        else:
            h1.append("%s: 0 <style>, %d Daten-<script>" % (f, len(scr)))
    sig = [s for s in SIG if s in t]
    if sig:
        h1bad = True
        h1.append("%s trägt Hülle: %s" % (f, sig))
row("H1 keine Hülle im Paket", not h1bad, " · ".join(h1))

# ---- H2
js = rd(os.path.join(H, man["js"]["reader"])).decode("utf-8") if (man.get("js") or {}).get("reader") else ""
# E38 P1 (Python): die Hülle trägt die Schriften (schriften.<sha8>.css, @font-face → woff2, geprüft in py_e38_p1). R2
# behauptete bisher: JEDE CSS der Hülle stammt aus der Ausgabe des Kernels — die Schriften tun das nicht (der Kernel bringt
# keine mit); R2/B1/H2 vergleichen die CSS ohne sie.
css = "\n".join(rd(os.path.join(H, c)).decode("utf-8") for c in man.get("css") or [] if not c.startswith("schriften."))
# E36 Zusammenführen (Hauptwerkstatt): die Hülle-CSS endet mit toolkit/css/huelle/lesen.css (Seite von lesen.html, CSS C1,
# VERTRAG-E36 „geändert von CSS“) — R2/B1 vergleichen die Lesefassungs-CSS OHNE diesen Schluss (er gilt der Seite, nicht dem Fenster)
_SEITE_P = os.path.join(ROOT, "toolkit", "css", "huelle", "lesen.css")
SEITE = open(_SEITE_P, encoding="utf-8").read() if os.path.exists(_SEITE_P) else ""
css_ganz = css
if SEITE and css.endswith("\n" + SEITE):
    css = css[:-len("\n" + SEITE)]
row("H2s Seite von lesen.html", (not SEITE) or css_ganz.endswith("\n" + SEITE),
    "Hülle-CSS endet mit css/huelle/lesen.css (%d B)" % len(SEITE.encode()) if SEITE and css_ganz.endswith("\n" + SEITE)
    else ("keine css/huelle/lesen.css im Baum" if not SEITE else "Hülle-CSS endet NICHT mit css/huelle/lesen.css"))
own = ("ID = '%s'" % NBID) in js or ("'%s'" % TKV) in js
PH = "var V = '__NBREADV__', ID = '__NBREADID__'"
row("H2 Hülle ohne Notebook", bool(js) and not own and PH in js and all(s in js + css_ganz for s in SIG),
    "Id/Version eingesetzt %s · Platzhalter (VERTRAG-E36) %s · CSS %d Zeichen · JS %d Zeichen" % (own, PH in js, len(css), len(js)))

# ---- H3
if MIT:
    md2 = json.load(open(MIT, encoding="utf-8"))["metadata"]["digichemjn"]
    T3 = tempfile.mkdtemp(prefix="py_e36c-")
    paket.ausgaenge(MIT, md2, dist=T3, lesen_html=LESEN, lader_js=LADER, log=lambda s: row("S1 Bau (--mit)", None, s))
    a = {f: sha(rd(os.path.join(H, f))) for f in sorted(os.listdir(H))}
    b = {f: sha(rd(os.path.join(T3, "huelle", md2["toolkit"], f))) for f in sorted(os.listdir(os.path.join(T3, "huelle", md2["toolkit"])))}
    row("H3 Hülle = %s" % md2["id"], a == b, "%s gegen %s" % (sorted(a), sorted(b)) if a != b else "%d Dateien gleich" % len(a))
    shutil.rmtree(T3, ignore_errors=True)

# ---- D1
d1 = []
try:
    D = json.load(open(os.path.join(P, "daten.json"), encoding="utf-8"))
    doc = rd(os.path.join(P, "lesefassung.en.html")).decode("utf-8")
    n_task, n_copy = doc.count("<div class='nbrw-task'"), doc.count("<div class='nbrw-copy'")
    n_chk, n_sl = doc.count("data-check='"), doc.count("<div class='nbrw-slider'")
    if len(D["aufgaben"]) != n_task or not all(t.get("antwort") and ("f" in t["antwort"] or "c" in t["antwort"]) for t in D["aufgaben"]):
        d1.append("Aufgaben %d/%d mit Antwort" % (sum(1 for t in D["aufgaben"] if t.get("antwort")), n_task))
    for t in D["aufgaben"]:
        for f in (t.get("antwort") or {}).get("f", []):
            if not (isinstance(f[0], str) and isinstance(f[1], (int, float)) and isinstance(f[2], (int, float))):
                d1.append("Feld %s: %r" % (t["task"], f)); break
    pc = [c for c in D["code"] if c["pruef_code"]]
    if len(D["code"]) != n_copy or len(pc) != n_chk:
        d1.append("Code %d/%d, Prüf-Code %d/%d" % (len(D["code"]), n_copy, len(pc), n_chk))
    for c in pc:
        try:
            compile(c["pruef_code"], "<%s>" % c["task"], "exec")
            if "def _nbrw_check(ns)" not in c["pruef_code"]: d1.append("%s: kein _nbrw_check" % c["task"])
        except SyntaxError as e:
            d1.append("%s: %s" % (c["task"], e))
    if len(D["regler"]) != n_sl or not all(r["bilder"] >= 1 for r in D["regler"]):
        d1.append("Regler %d/%d" % (len(D["regler"]), n_sl))
    nz = sum(1 for r in D["regler"] if r["z_bytes"])
    zdoc = len(re.findall(r"data-z='", doc))
    if nz != zdoc or '"f": [' in json.dumps(D["regler"]):
        d1.append("Reglerbilder doppelt/fehlen: daten %d, Lesefassung %d" % (nz, zdoc))
    g = D["gating"]
    if not g.get("order") or g.get("mode") != D["modus"] or not D["kapitel"]:
        d1.append("Gating order %s, Modus %s/%s, Kapitel %d" % (g.get("order"), g.get("mode"), D["modus"], len(D["kapitel"])))
    tt = D["kapitel_titel"]
    if not tt.get("en") or len(tt["en"]) != len(tt.get("de") or ()):
        d1.append("Kapitelnamen en %d / de %d" % (len(tt.get("en") or ()), len(tt.get("de") or ())))
    if not isinstance(D["marken"], list) or not D["marken"]:
        d1.append("Marken %r" % (D["marken"],)[:80])
    det = ("%d Aufgaben · %d Code (%d Prüf-Code) · %d Regler (%d Bilder, je einmal) · %d Kapitel · %d Marken · Seed %s · Modus %s"
           % (len(D["aufgaben"]), len(D["code"]), len(pc), len(D["regler"]), sum(r["bilder"] for r in D["regler"]),
              len(D["kapitel"]), len(D["marken"]), D["seed"]["value"], D["modus"]))
except Exception as e:
    d1.append(repr(e)[:160]); det = ""
row("D1 daten.json", not d1, "; ".join(d1) or det)

# ---- D0
tree = os.path.join(ROOT, "dist", "inhalt", NBID, NBV)
if os.path.isdir(tree):
    diff = [f for f in sorted(set(os.listdir(tree)) | set(os.listdir(P)))
            if not os.path.isfile(os.path.join(tree, f)) or not os.path.isfile(os.path.join(P, f))
            or rd(os.path.join(tree, f)) != rd(os.path.join(P, f))]
    row("D0 dist/ im Baum", not diff, "verschieden: %s — neu bauen" % diff if diff else "= frischer Bau")
else:
    row("D0 dist/ im Baum", None, "keins für %s %s (nichts zu vergleichen)" % (NBID, NBV))

# ---- R1
paket.ausgaenge(NB, md, dist=T2, lesen_html=LESEN, lader_js=LADER, log=lambda s: None)
def tree_sha(r):
    o = {}
    for dp, _, fs in os.walk(r):
        for f in fs:
            o[os.path.relpath(os.path.join(dp, f), r)] = sha(rd(os.path.join(dp, f)))
    return o
s1, s2 = tree_sha(T1), tree_sha(T2)
row("R1 reproduzierbar", s1 == s2, "%d Dateien gleich" % len(s1) if s1 == s2
    else "verschieden: %s" % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)))

# ---- R2
r2 = []
for lang in paket.LANGS:
    raw = res["roh"][lang]
    doc = rd(os.path.join(P, "lesefassung.%s.html" % lang)).decode("utf-8")
    blocks = [b for b in paket._blocks(raw) if not (b[2] == "script" and paket.is_data_script(b[3]))]
    out, last = [], 0
    for a, b, kind, attrs, body in blocks:
        out.append(raw[last:a]); last = b
    out.append(raw[last:])
    cut = "".join(out)
    hull_css = "\n".join(b[4] for b in blocks if b[2] == "style")
    hull_js = "\n".join(b[4] for b in blocks if b[2] == "script").replace("var V = '%s', ID = '%s'" % (TKV, NBID), PH, 1)
    if cut != doc: r2.append("%s: Lesefassung ≠ Ausgabe ohne Hülle" % lang)
    if hull_css != css: r2.append("%s: <style> der Ausgabe ≠ leser.css" % lang)
    if hull_js != js: r2.append("%s: <script> der Ausgabe ≠ reader.js" % lang)
row("R2 Rückbau", not r2, "; ".join(r2) or "en/de: Lesefassung + leser.css + reader.js = Ausgabe des Kernels")

# ---- B1
if not NOBROWSER:
    from playwright.sync_api import sync_playwright
    def page_now(raw, dark):
        bg = "#2b2d30" if dark else "#ffffff"
        return ("<!doctype html><html><head><meta charset=utf-8></head><body style='margin:0;padding:8px;background:%s;color:%s'>%s</body></html>"
                % (bg, "#dfe1e5" if dark else "#1f2328", raw))
    def page_pkg(doc, dark):
        bg = "#2b2d30" if dark else "#ffffff"
        return ("<!doctype html><html><head><meta charset=utf-8><style>%s</style></head>"
                "<body style='margin:0;padding:8px;background:%s;color:%s'>%s<script>%s</script></body></html>"
                % (css, bg, "#dfe1e5" if dark else "#1f2328", doc, js.replace(PH, "var V = '%s', ID = '%s'" % (TKV, NBID), 1)))
    raw = res["roh"]["en"]
    doc = rd(os.path.join(P, "lesefassung.en.html")).decode("utf-8")
    try:
        from PIL import Image, ImageChops
        import io
    except ImportError:
        Image = None
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h in ((1366, 900), (390, 844)):
            for dark in (False, True):
                shots, info = [], []
                for name, html in (("heute", page_now(raw, dark)), ("paket", page_pkg(doc, dark))):
                    ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme="dark" if dark else "light")
                    pg = ctx.new_page(); errs = []
                    pg.on("pageerror", lambda e: errs.append(str(e)[:80]))
                    pg.set_content(html)
                    try:
                        pg.wait_for_selector(".nbrw", timeout=15000)
                    except Exception:
                        pass
                    pg.wait_for_timeout(1500)
                    # Bewegung aus, auf BEIDEN Seiten gleich (der leuchtende Marker der Zeitleiste pulsiert: gemessen
                    # 10 Pixel verschieden je nach Phase, 1 von 4 Läufen) — verglichen wird Hülle gegen heute, nicht die Zeit
                    pg.add_style_tag(content="*,*::before,*::after{animation:none!important;transition:none!important}")
                    pg.wait_for_timeout(100)
                    st = pg.evaluate("() => ({w: !!document.querySelector('.nbrw'), rh: !!document.querySelector('[data-nbrw-rh]'), "
                                     "H: document.documentElement.scrollHeight})")
                    seq = [pg.screenshot()]                      # Deckblatt des Fensters
                    try:                                         # ▶: das Dokument, dann 2 400 px weiter im Fenster
                        pg.click("[data-nbrw-act=play]", timeout=5000); pg.wait_for_timeout(1200)
                        st["doc"] = pg.evaluate("() => !!document.querySelector('.nbrw-win .nbread-h')")
                        seq.append(pg.screenshot())
                        pg.evaluate("() => { var w = document.querySelector('.nbrw-win'); if (w) w.scrollTop = 2400; }")
                        pg.wait_for_timeout(900); seq.append(pg.screenshot())
                    except Exception as e:
                        st["doc"] = False; errs.append("Play: " + str(e)[:60])
                    shots.append(seq); info.append((name, st, errs[:2]))
                    if SHOTS:
                        os.makedirs(SHOTS, exist_ok=True)
                        for i, im in enumerate(seq):
                            open(os.path.join(SHOTS, "py-E36-B1-%s-%d-%s-%d.png" % (name, w, "dunkel" if dark else "hell", i)), "wb").write(im)
                    ctx.close()
                npx = []
                for x, y in zip(shots[0], shots[1]):
                    if x == y or not Image:
                        npx.append(0 if x == y else -1); continue
                    d = ImageChops.difference(Image.open(io.BytesIO(x)).convert("RGB"), Image.open(io.BytesIO(y)).convert("RGB"))
                    npx.append(sum(1 for px in (d.get_flattened_data() if hasattr(d, 'get_flattened_data') else d.getdata()) if px != (0, 0, 0)))
                same = len(shots[0]) == len(shots[1]) == 3 and not any(npx)
                started = all(i[1]["w"] and i[1]["rh"] and i[1].get("doc") for i in info)
                row("B1 %d %s" % (w, "dunkel" if dark else "hell"), same and started and not any(i[2] for i in info),
                    ("pixelgleich (Deckblatt, Dokument, +2400 px)" if same else "Pixel verschieden je Bild %s" % npx)
                    + ("" if started and not any(i[2] for i in info) else " · " + "; ".join(
                        "%s Fenster %s rehyd %s Dokument %s Fehler %s" % (n, s["w"], s["rh"], s.get("doc"), e or "-") for n, s, e in info)))
        b.close()

# ---- S1
for f, d in sorted((meta.get("dateien") or {}).items()) + [("meta.json", {"bytes": len(rd(os.path.join(P, "meta.json"))),
        "gzip": len(gzip.compress(rd(os.path.join(P, "meta.json")), 9, mtime=0))})]:
    row("S1 inhalt/%s" % f, None, "%d B · gzip %d B" % (d["bytes"], d["gzip"]))
for k, d in sorted((man.get("dateien") or {}).items()):
    row("S1 huelle/%s" % k, None, "%d B · gzip %d B" % (d["bytes"], d["gzip"]))
shutil.rmtree(T1, ignore_errors=True); shutil.rmtree(T2, ignore_errors=True)
finish()
