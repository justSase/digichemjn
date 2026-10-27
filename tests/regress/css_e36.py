"""E36 C2 · CSS — Werkstatt CSS, 19.10. (Auftrag plan/AUFTRAG.md C1–C2, Plan plan/ARCHITEKTUR.md: „Hülle trennen“).
Die Lesefassung aus Hülle + Paket (lesen.html) sieht aus wie die Lesefassung im Notebook-iframe — gemessen, nicht Augenmaß:

    python3 tests/regress/css_e36.py <notebook.ipynb> [--also <zweites.ipynb>] [--dist DIR] [--strict]
                                     [--skins digi,minimal,cyber,fairy] [--themes light,dark] [--sizes 1366x900,390x844]
                                     [--shots DIR] [--json out.json]

Referenz: der echte Kernel führt die Zelle aus (env_iframe.run_cell), die Lesefassung (Ausgabe mit .nbreading) steht in
einem iframe eigener Seite (srcdoc, body margin 0 — wie env_iframe/env_reader, PyCharm/VS Code), über http; die Seite um den
iframe hat den Grund des Fensters (sonst zählten die runden Ecken die Farbe des Viewers mit).
Neu: lesen.html —
  * mit --dist DIR (oder dist/ neben dem Notebook, eine Ebene darüber, $DIGICHEM_DIST): der Bau-Ausgang von E36
    (Python P3 + JS J1): DIR/huelle/<TOOLKIT_VERSION>/lesen.html?nb=<id>&v=<NB_VERSION> (Vorlage --page),
  * sonst ein STAND-IN nach dem Vertrag in toolkit/css/huelle/lesen.css: aus derselben Ausgabe werden <style> und
    Code-<script> herausgenommen (Daten-<script type=application/json> bleiben = Paket), die Styles + css/huelle/lesen.css
    als EINE Datei huelle/lesen.css per <link>, das Skript als huelle/lesen.js per <script src> direkt hinter .nbreading.
    Ohne --strict zählt der Stand-in; mit --strict ist er rot (das Tor nach dem Zusammenführen misst den echten Bau).
Zeilen (frischer Speicher je Bild; Stil und hell/dunkel als gespeicherte Wahl digichemjn.<id>.reader.skin/.theme,
prefers-color-scheme passend):
  H1  Hülle-CSS notebookunabhängig: kein Notebook-Kennzeichen (id, nbid-, Titel) in der Hülle-CSS; mit --also: die
      Hülle-CSS beider Notebooks byte-gleich, ebenso das Stylesheet des Notebooks (<style data-nbstyle>, INFO Größe)
  H2  die Seite: Rand 0, kein waagrechter Bildlauf, Grund der Seite (html) = Grund des Fensters (.nbrw) ± 2,
      je Breite × Stil × hell/dunkel (sonst weißer Streifen unter dunklem Fenster)
  P   .nbrw pixelgleich iframe ↔ lesen.html, je Breite × Stil × hell/dunkel × Ansicht (Vorschau | Dokument nach ▶):
      wie lab_same: je zwei Bilder 700 ms auseinander, ein Pixel zählt, wenn er in einem Kanal um > 32/255 von
      allen Referenzbildern abweicht UND von seinen 8 Nachbarn (Raster-Rauschen wird berichtet, nicht gezählt)
  I390 INFO (STOP Merkpunkt 3): bei 390 px Elemente mit Text, die über den Rand des Fensters hinausragen (abgeschnitten)
       — in Referenz und neu; gleich, solange 15-reader.css unverändert bleibt (die .ipynb bleibt byte-gleich, E36)
Gegenprobe v1.81 (41a23b93, ohne css/huelle/lesen.css): rot H2 (Rand 8 px, Seite weiß unter dunklem Fenster) und
alle P (Fenster 16 px schmaler). exit 0 = REGRESS-CSS-E36 OK."""
import sys, os, re, io, json, html as _h, hashlib, threading, functools, http.server, socketserver, tempfile, shutil, gzip
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
from env_iframe import run_cell

CHROME = os.environ.get("DIGICHEM_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
NB = [a for i, a in enumerate(A) if a.endswith(".ipynb") and (i == 0 or A[i - 1] != "--also")][0]
ALSO, STRICT = opt("--also"), "--strict" in A
SKINS = opt("--skins", "digi,minimal,cyber,fairy").split(",")
THEMES = opt("--themes", "light,dark").split(",")
SIZES = [tuple(int(v) for v in s.split("x")) for s in opt("--sizes", "1366x900,390x844").split(",")]
SHOTS, JS_OUT, TOL = opt("--shots"), opt("--json"), 32
SEITE = os.path.join(ROOT, "toolkit", "css", "huelle", "lesen.css")
rows, bad = [], []

def row(name, ok, detail, info=False):
    rows.append({"row": name, "ok": bool(ok), "info": info, "detail": detail})
    print("%-34s %s  %s" % (name, "INFO" if info else ("ok  " if ok else "RED "), detail)); sys.stdout.flush()
    if not ok and not info:
        bad.append(name)

TAG = re.compile(r"<(script|style)\b([^>]*)>", re.I)
def split(h):
    """reading output → (Lesefassung, [css], [js]): <style> und Code-<script> heraus, Daten-<script> bleiben."""
    css, js, keep, i = [], [], [], 0
    while True:
        m = TAG.search(h, i)
        if not m:
            keep.append(h[i:]); break
        t = m.group(1).lower(); end = h.find("</%s>" % t, m.end()); stop = end + len(t) + 3
        if t == "style":
            keep.append(h[i:m.start()]); css.append(h[m.end():end])
        elif "application/json" in m.group(2):
            keep.append(h[i:stop])
        else:
            keep.append(h[i:m.start()]); js.append(h[m.end():end])
        i = stop
    return "".join(keep), css, js

def reading(nbf):
    outs, errs, _ = run_cell(nbf, {})
    if errs:
        print("kernel errors:", errs[:3])
    rd = [o["data"]["text/html"] for o in outs if "class='nbreading'" in (o["data"].get("text/html") or "")]
    nbst = [m.group(1) for o in outs for m in re.finditer(r"<style data-nbstyle=[^>]*>(.*?)</style>",
                                                          o["data"].get("text/html") or "", re.S)]
    return (rd[0] if rd else None), (nbst[0] if nbst else "")

def meta(nbf):
    m = json.load(open(nbf)).get("metadata", {}).get("digichemjn", {})
    return m.get("id") or "nb", m.get("version") or "", m.get("toolkit") or "", m.get("title") or ""

def find_dist(nbf):
    for d in (opt("--dist"), os.environ.get("DIGICHEM_DIST"), os.path.join(os.path.dirname(os.path.abspath(nbf)), "dist"),
              os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(nbf))), "dist"), os.path.join(ROOT, "dist")):
        if d and os.path.isdir(os.path.join(d, "huelle")):
            return d
    return None

def serve(d):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    s = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=d))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, "http://127.0.0.1:%d/" % s.server_address[1]

def compare(ra, rb, na, nb):
    if ra.size != na.size:
        return None, 0
    def mx(a, b, t):
        r, g, bl = ImageChops.difference(a, b).split()
        return ImageChops.lighter(ImageChops.lighter(r, g), bl).point(lambda v: 255 if v > t else 0)
    still = mx(ra, na, TOL)
    for x, y in ((ra, nb), (rb, na), (rb, nb)):
        still = ImageChops.darker(still, mx(x, y, TOL))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                still = ImageChops.darker(still, mx(ImageChops.offset(ra, dx, dy), na, TOL))
    noise = mx(ra, na, 0).histogram()[255] - mx(ra, na, TOL).histogram()[255]
    return still.histogram()[255], noise

PAGE = r"""() => { var w = document.querySelector('.nbrw'); if (!w) return null;
  var cs = getComputedStyle(document.documentElement), b = getComputedStyle(document.body), r = w.getBoundingClientRect();
  return {html: cs.backgroundColor, win: getComputedStyle(w).backgroundColor, m: [b.marginTop, b.marginLeft, b.marginRight].join(' '),
          left: r.left, sw: document.scrollingElement.scrollWidth, iw: innerWidth}; }"""
CUT = r"""() => { var w = document.querySelector('.nbrw-win') || document.querySelector('.nbrw'); if (!w) return [];
  var R = w.getBoundingClientRect(), out = [];
  [].forEach.call(w.querySelectorAll('*'), function (e) {
    var t = [].filter.call(e.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); }).length;
    if (!t) return; var b = e.getBoundingClientRect(), s = getComputedStyle(e);
    if (!(b.width > 0 && b.height > 0) || s.visibility === 'hidden') return;
    for (var x = e; x; x = x.parentElement) if (getComputedStyle(x).display === 'none') return;
    if (b.bottom < R.top || b.top > R.bottom) return;
    if (b.right > R.right + 1 || b.left < R.left - 1 || e.scrollWidth > e.clientWidth + 1 && s.overflow !== 'visible')
      out.push(e.textContent.trim().slice(0, 40));
  }); return out; }"""
def rgb(s):
    m = re.findall(r"[\d.]+", s or ""); return [float(v) for v in m[:3]] if len(m) >= 3 else None

def main():
    nid, nbv, tv, title = meta(NB)
    h, nbst = reading(NB)
    if not h:
        row("H0 Lesefassung", False, "keine Ausgabe mit .nbreading"); return
    les, css, js = split(h)
    seite = open(SEITE, encoding="utf-8").read() if os.path.exists(SEITE) else ""
    hcss = "\n".join(css) + ("\n" + seite if seite else "")
    tmp = tempfile.mkdtemp(prefix="css_e36_")
    dist = find_dist(NB)
    # H1 — the Hülle CSS knows no notebook
    marks = [m for m in (nid, "nbid-" + nid, title) if m and m in hcss]
    det = "Hülle-CSS %d B (gzip %d) · Seite %s · Stylesheet Notebook %d B (gzip %d)%s" % (
        len(hcss.encode()), len(gzip.compress(hcss.encode(), 9)), "%d B" % len(seite.encode()) if seite else "FEHLT",
        len(nbst.encode()), len(gzip.compress(nbst.encode(), 9)), " · Kennzeichen: %s" % marks if marks else "")
    ok1 = not marks and bool(seite)
    if ALSO:
        h2, nbst2 = reading(ALSO)
        _, css2, _ = split(h2 or "")
        same = css2 == css and nbst2 == nbst
        det += " · %s: Hülle-CSS %s, Stylesheet %s" % (os.path.basename(ALSO), "gleich" if css2 == css else "VERSCHIEDEN",
                                                       "gleich" if nbst2 == nbst else "VERSCHIEDEN")
        ok1 = ok1 and same
    row("H1 Hülle-CSS notebookunabhängig", ok1, det)
    # the two pages
    doc = "<!doctype html><meta charset=utf-8><body style='margin:0'>" + h
    open(os.path.join(tmp, "ref.html"), "w", encoding="utf-8").write(
        "<!doctype html><meta charset=utf-8><body style='margin:0'><iframe class='out' style='display:block;width:100%%;"
        "border:0;height:40px' srcdoc=\"%s\"></iframe><script>setInterval(function(){var f=document.querySelector('iframe');"
        "try{f.style.height=f.contentDocument.documentElement.scrollHeight+'px'}catch(e){}},150)</script>" % _h.escape(doc, quote=True))
    if dist and not opt("--standin"):
        root, page = dist, opt("--page", "huelle/{tv}/lesen.html?nb={id}&v={nbv}").format(tv=tv, id=nid, nbv=nbv)
        shutil.copy(os.path.join(tmp, "ref.html"), os.path.join(dist, "_css_e36_ref.html")); refp = "_css_e36_ref.html"
        row("H0 Bau-Ausgang", True, "dist %s · %s" % (dist, page), info=True)
    else:
        os.makedirs(os.path.join(tmp, "huelle"))
        open(os.path.join(tmp, "huelle", "lesen.css"), "w", encoding="utf-8").write(hcss)
        open(os.path.join(tmp, "huelle", "lesen.js"), "w", encoding="utf-8").write("\n".join(js))
        open(os.path.join(tmp, "lesen.html"), "w", encoding="utf-8").write(
            "<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s</title><link rel=stylesheet href='huelle/lesen.css'></head><body>%s<script src='huelle/lesen.js'></script>"
            "</body></html>" % (_h.escape(title), les))
        root, page, refp = tmp, "lesen.html", "ref.html"
        row("H0 Bau-Ausgang", not STRICT, "STAND-IN (kein dist/ mit huelle/)%s · Lesefassung %d B, %d <style>, %d Code-<script>" % (
            " — mit --strict rot" if STRICT else "", len(les.encode()), les.count("<style"),
            len(re.findall(r"<script(?![^>]*application/json)", les))), info=not STRICT)
    srv, base = serve(root)
    ns_page = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        REFH, REFLINE = {}, {}
        def open_(W, H, th, skin, kind):
            # E38a J1 (JS, 26.10.): lesen.html fills its viewport (js_e38a J1a); the reference window is screen − 240.
            # P BEHAUPTETE BISHER gleiche Größe bei gleichem Viewport — nun: lesen.html in einem Viewport so hoch wie
            # das Referenzfenster (.nbrw), dann pixelgleich wie bisher.
            if kind == "new" and REFH.get(W): H = REFH[W]
            c = b.new_context(viewport={"width": W, "height": H}, color_scheme=th)
            c.add_init_script("try{localStorage.clear();localStorage.setItem('digichemjn.%s.reader.skin','%s');"
                              "localStorage.setItem('digichemjn.%s.reader.theme','%s')}catch(e){}" % (nid, skin, nid, th))
            pg = c.new_page(); pg.goto(base + (refp if kind == "ref" else page))
            fr = pg.frame_locator("iframe.out") if kind == "ref" else pg
            fr.locator(".nbrw").first.wait_for(timeout=30000); pg.wait_for_timeout(1500)
            if kind == "ref":       # the frame on a page of the window's own colour: only the window counts (round corners)
                REFH[W] = int(round(fr.locator(".nbrw").first.evaluate("e => e.getBoundingClientRect().height")))
                # … and lesen.html has no ↕ row (E38a J1): the reference without it, the rest of the column as drawn
                fr.locator(".nbrw").first.evaluate("e => { var h = e.querySelector('[data-act=\\'h+\\']'); if (h) h.parentNode.remove(); window.dispatchEvent(new Event('resize')); }")
                pg.wait_for_timeout(600)
                # E38a P1 (Hauptwerkstatt, 26.10.): P BEHAUPTETE BISHER dieselbe Lesezeile in lesen.html und im Notebook.
                # Seit P1 sagt sie in lesen.html, was dort geht (py_e38a_p1 prüft den Text) — verglichen wird der Rest:
                # der Text der Referenzzeile wird in lesen.html eingesetzt (gegengeprüft: ohne P1-Text 0 px).
                REFLINE[W] = fr.locator(".nbrw").first.evaluate("e => [].map.call(e.querySelectorAll('.nbread-line'), x => x.innerHTML)")
                pg.evaluate("bg => document.body.style.background = bg",
                            fr.locator(".nbrw").first.evaluate("e => getComputedStyle(e).backgroundColor"))
            return c, pg, fr
        def two(pg, fr):
            el = fr.locator(".nbrw").first
            a = Image.open(io.BytesIO(el.screenshot(animations="disabled"))).convert("RGB"); pg.wait_for_timeout(700)
            return a, Image.open(io.BytesIO(el.screenshot(animations="disabled"))).convert("RGB")
        for W, H in SIZES:
            for skin in SKINS:
                for th in THEMES:
                    shots = {}
                    for kind in ("ref", "new"):
                        c, pg, fr = open_(W, H, th, skin, kind)
                        if kind == "new":
                            pv = pg.evaluate(PAGE)
                            if pv:
                                hb, wb = rgb(pv["html"]), rgb(pv["win"])
                                okp = (pv["m"] == "0px 0px 0px" and pv["sw"] <= pv["iw"] and hb and wb
                                       and max(abs(x - y) for x, y in zip(hb, wb)) <= 2)
                                row("H2 Seite %d %s %s" % (W, skin, th), okp, "Rand %s · Seite %s · Fenster %s · Breite %d/%d" % (
                                    pv["m"], pv["html"], pv["win"], pv["sw"], pv["iw"]))
                            else:
                                row("H2 Seite %d %s %s" % (W, skin, th), False, "kein .nbrw in lesen.html")
                        shots[kind, "cover"] = two(pg, fr)
                        cut_c = fr.locator(".nbrw").first.evaluate("e => (%s)()" % CUT) if W < 600 else None
                        fr.locator(".nbrw-play").first.click(); pg.wait_for_timeout(1500)
                        if kind == "new" and REFLINE.get(W) is not None:
                            fr.locator(".nbrw").first.evaluate("(e, L) => { [].forEach.call(e.querySelectorAll('.nbread-line'), (x, i) => { if (L[i] != null) x.innerHTML = L[i]; }); window.dispatchEvent(new Event('resize')); }", REFLINE[W])
                            pg.wait_for_timeout(700)
                        shots[kind, "doc"] = two(pg, fr)
                        cut_d = fr.locator(".nbrw").first.evaluate("e => (%s)()" % CUT) if W < 600 else None
                        if cut_c is not None and skin == SKINS[0] and th == THEMES[0]:
                            row("I390 %s %d %s" % (kind, W, skin), True, "abgeschnitten Vorschau %d %s · Dokument %d %s" % (
                                len(cut_c), cut_c[:4], len(cut_d), cut_d[:4]), info=True)
                        c.close()
                    for view in ("cover", "doc"):
                        (ra, rb), (na, nb2) = shots["ref", view], shots["new", view]
                        n_bad, noise = compare(ra, rb, na, nb2)
                        name = "P %d %s %s %s" % (W, skin, th, "Vorschau" if view == "cover" else "Dokument")
                        ok = n_bad == 0
                        row(name, ok, ("%d px verschieden" % n_bad if n_bad is not None else "Größe %s ↔ %s" % (ra.size, na.size))
                            + (" · %d px Rauschen ≤ %d" % (noise, TOL) if noise else ""))
                        if SHOTS and (not ok or (W, skin, th) == (SIZES[0][0], SKINS[0], THEMES[0])):
                            os.makedirs(SHOTS, exist_ok=True); k = name.replace(" ", "_")
                            ra.save(os.path.join(SHOTS, k + "_ref.png")); na.save(os.path.join(SHOTS, k + "_new.png"))
        b.close()
    srv.shutdown()
    if not (dist and not opt("--standin")):
        shutil.rmtree(tmp, ignore_errors=True)

main()
if JS_OUT:
    json.dump(rows, open(JS_OUT, "w"), ensure_ascii=False, indent=1)
print("%d Zeilen, %d rot%s" % (len(rows), len(bad), (": " + ", ".join(bad[:12])) if bad else ""))
print("REGRESS-CSS-E36 OK" if not bad else "REGRESS-CSS-E36 RED")
sys.exit(1 if bad else 0)
