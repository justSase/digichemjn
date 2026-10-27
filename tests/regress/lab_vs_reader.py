"""E38 Tor (Hauptwerkstatt, 2026-10-27) — LAB NEBEN DEM LESER: wie weit ist „eine Darstellung überall“?
    python3 tests/regress/lab_vs_reader.py <notebook.ipynb> [--dist dist] [--themes dark,light] [--shots DIR]
                                           [--max 0.10] [--json out.json]

plan/AUFTRAG.md E38, Tor zusätzlich: „lab_vs_reader: Deckblatt + Dokument oben/mitte/ende, Lab vs. Leser, gleicher Seed,
Pixelvergleich wie lab_same (Toleranz, Doppelbild)“. Lab = das Lab-Dokument (Kernel mit DIGICHEM_LAB=1, seit E38 P3 sonst
das Paket), Stil digi; Leser = lesen.html aus dist/ (gleicher Bau, gleicher Seed), beide 1400 × 900, echter Chromium.
Verglichen wird je Ansicht die MITTLERE SPALTE (680 px breit um die Mitte der Kapitel-Pillen, die Rail/Werkzeuge links und die
Zeitleiste rechts liegen außerhalb: J4 ist offen), oben bündig an der Titelkarte (Deckblatt) bzw. am Fensterinhalt:
  V1  Deckblatt (nach Run All bzw. Laden, vor ▶)
  V2  Dokument: Kapitel 1 · V3 Kapitel 2 · V4 Ende (nach ▶; die Kapitel-Pille je 120 px unter dem Fensterrand, 600 px
      hoch; Ende = ganz gerollt, 600 px ab Fensteroberkante)
Ein Pixel zählt wie in lab_same, wenn ein Kanal um mehr als --tol (32/255) von der Gegenseite UND von ihren 8 Nachbarn
abweicht; jede Seite zweimal (700 ms) — nur was in BEIDEN Bildern abweicht, zählt. Zeile grün, wenn der Anteil ≤ --max.
Doppelbild (Lab | Leser | Unterschied) je Ansicht nach --shots. Owner: Hauptwerkstatt. exit 0 = LAB-VS-READER OK."""
import sys, os, io, json, time, shutil, tempfile, subprocess, urllib.request, socket, functools, threading
import http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from PIL import Image, ImageChops, ImageFilter
from playwright.sync_api import sync_playwright
import css_e34 as E

A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
NB = os.path.abspath(A[0])
DIST = os.path.abspath(opt("--dist", os.path.join(ROOT, "dist")))
THEMES = opt("--themes", "dark,light").split(",")
SHOTS, JOUT = opt("--shots"), opt("--json")
TOL, MAX = int(opt("--tol", "32")), float(opt("--max", "0.10"))
W, H, COL, SPAN = 1400, 900, 680, 600
rows = []


def row(n, ok, det):
    rows.append({"row": n, "ok": bool(ok), "detail": det})
    print("%-26s %s  %s" % (n, "ok " if ok else "RED", det), flush=True)


def mask_diff(a, b):
    """lab_same's count: a pixel of b differs from a when it differs from a there AND from a's 8 neighbours."""
    a, b = a.convert("RGB"), b.convert("RGB")
    lo = a.filter(ImageFilter.MinFilter(3)); hi = a.filter(ImageFilter.MaxFilter(3))
    d0 = ImageChops.difference(a, b).convert("L").point(lambda x: 255 if x > TOL else 0)
    below = ImageChops.subtract(lo, b).convert("L").point(lambda x: 255 if x > TOL else 0)
    above = ImageChops.subtract(b, hi).convert("L").point(lambda x: 255 if x > TOL else 0)
    out = ImageChops.multiply(d0, ImageChops.lighter(below, above))
    return out


def crop(img, cx, top, h):
    x0 = max(0, int(cx - COL / 2))
    return img.crop((x0, int(top), x0 + COL, int(top) + h))


def ends(img, g):
    """V2/V3: from the window's top (the chapter pill 120 px below it); V4 (end): the last SPAN px above the window's bottom."""
    return crop(img, g["cx"], g["top"], SPAN)


def shot(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert("RGB")


LAB_GEOM = r"""(what) => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var o = P.querySelector('.jp-OutputArea-output') || P; var r = o.getBoundingClientRect();
  var card = P.querySelector('.nbcover-out .nbtitle-card'); var c = card ? card.getBoundingClientRect() : null;
  var sc = P.querySelector('.jp-WindowedPanel-outer') || P.querySelector('.jp-Notebook');
  return {cx: c ? c.left + c.width / 2 : r.left + r.width / 2, top: c ? c.top : r.top, sc: sc ? [sc.scrollTop, sc.scrollHeight - sc.clientHeight] : [0, 0],
          wtop: sc ? sc.getBoundingClientRect().top : 0}; }"""
LAB_SCROLL = r"""(f) => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var sc = P.querySelector('.jp-WindowedPanel-outer') || P.querySelector('.jp-Notebook'); if (!sc) return null;
  var hs = [].filter.call(P.querySelectorAll('.jupyter-widget-Collapse-header'), function (h) { return h.getBoundingClientRect().height > 40; });
  var q = sc.getBoundingClientRect();
  if (f >= 9) { sc.scrollTop = sc.scrollHeight; } else { var h = hs[f]; if (!h) return null; sc.scrollTop += h.getBoundingClientRect().top - q.top - 120; }
  var a = (f >= 9 ? hs[hs.length - 1] : hs[f]).getBoundingClientRect();
  return {cx: a.left + a.width / 2, top: q.top, end: q.bottom}; }"""
RD_GEOM = r"""() => { var w = document.querySelector('.nbrw-win'), card = document.querySelector('.nbrw-cover .nbr-nbtitle-card');
  var r = (card || w).getBoundingClientRect(), q = w.getBoundingClientRect();
  return {cx: r.left + r.width / 2, top: r.top, wtop: q.top}; }"""
RD_SCROLL = r"""(f) => { var w = document.querySelector('.nbrw-win'), q = w.getBoundingClientRect();
  var hs = [].slice.call(document.querySelectorAll('.nbrw-doc details[data-kind=chapter]>summary>.nbread-h'));
  if (f >= 9) { w.scrollTop = w.scrollHeight; } else { var h = hs[f]; if (!h) return null; w.scrollTop += h.getBoundingClientRect().top - q.top - 120; }
  var a = (f >= 9 ? hs[hs.length - 1] : hs[f]).getBoundingClientRect();
  return {cx: a.left + a.width / 2, top: q.top, end: q.bottom}; }"""


def twice(pg):
    a = shot(pg); pg.wait_for_timeout(700); b = shot(pg)
    return a, b


def compare(name, la, ra):
    """la/ra: two crops each (Lab, Leser) → share of pixels that differ in both pairs."""
    h = min(la[0].size[1], ra[0].size[1])
    la = [x.crop((0, 0, COL, h)) for x in la]; ra = [x.crop((0, 0, COL, h)) for x in ra]
    m = ImageChops.multiply(mask_diff(la[0], ra[0]), mask_diff(la[1], ra[1]))
    n = sum(1 for v in m.getdata() if v)
    share = n / float(COL * h)
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
        d = Image.new("RGB", (COL * 3 + 20, h), (128, 128, 128))
        d.paste(la[0], (0, 0)); d.paste(ra[0], (COL + 10, 0))
        red = Image.new("RGB", (COL, h), (255, 0, 0)); base = la[0].convert("L").convert("RGB")
        d.paste(Image.composite(red, base, m), (2 * COL + 20, 0))
        d.save(os.path.join(SHOTS, "lab_vs_reader-%s.png" % name.replace(" ", "-")))
    return share, n, h


def main():
    md = json.load(open(NB, encoding="utf-8"))["metadata"]["digichemjn"]
    nid, v, tv = md["id"], md["version"], md["toolkit"]

    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Q, directory=DIST))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/huelle/%s/lesen.html?nb=%s&v=%s" % (srv.server_address[1], tv, nid, v)
    os.environ["DIGICHEM_LAB"] = "1"
    with sync_playwright() as P:
        b = P.chromium.launch(executable_path=E.CHROME if os.path.exists(E.CHROME) else None)
        for th in THEMES:
            tmp = tempfile.mkdtemp(prefix="lvr_"); shutil.copy(NB, os.path.join(tmp, "nb.ipynb"))
            # css_e34.start_server drops DIGICHEM_* from the server's env: the kernel would show the package. Here the
            # kernel must build the Lab document → a kernel-spec-free way: the notebook's first line sets the variable.
            nbj = json.load(open(os.path.join(tmp, "nb.ipynb"), encoding="utf-8"))
            c0 = next(c for c in nbj["cells"] if c["cell_type"] == "code")
            c0["source"] = ["import os as _o; _o.environ['DIGICHEM_LAB'] = '1'; del _o\n"] + list(c0["source"])
            json.dump(nbj, open(os.path.join(tmp, "nb.ipynb"), "w", encoding="utf-8"), ensure_ascii=False)
            p, base = E.start_server("lab", tmp, th)
            lab = {}
            try:
                c = b.new_context(viewport={"width": W, "height": H}, color_scheme=th)
                c.add_init_script("try{localStorage.clear();localStorage.setItem('digichemjn.theme.v1.%s','%s');"
                                  "localStorage.setItem('digichemjn.skin.v1.%s','digi')}catch(e){}" % (nid, th, nid))
                pg = c.new_page(); pg.goto(base + "/lab/tree/nb.ipynb")
                pg.wait_for_selector(".jp-NotebookPanel", timeout=90000); pg.wait_for_timeout(3000)
                st = E.run_and_play(pg)
                pg.add_style_tag(content="*{animation:none!important;transition:none!important;caret-color:transparent!important}")
                if st == "ok":
                    g = pg.evaluate(LAB_GEOM, "cover")
                    lab["V1"] = [crop(x, g["cx"], g["top"], SPAN) for x in twice(pg)]
                    if E.play(pg) == "play":
                        for k, f in (("V2", 0), ("V3", 1), ("V4", 9)):
                            g = pg.evaluate(LAB_SCROLL, f); pg.wait_for_timeout(1200)
                            g = pg.evaluate(LAB_SCROLL, f) if f < 9 else g     # the second call settles a virtualised list
                            if g:
                                lab[k] = [ends(x, g) for x in twice(pg)]
                else:
                    row("V0 %s Lab" % th, False, "BAD %s" % st)
                c.close()
            finally:
                p.terminate()
            c = b.new_context(viewport={"width": W, "height": H}, color_scheme=th)
            c.add_init_script("try{localStorage.clear();localStorage.setItem('digichemjn.%s.reader.skin','digi');"
                              "localStorage.setItem('digichemjn.%s.reader.theme','%s')}catch(e){}" % (nid, nid, th))
            pg = c.new_page(); pg.goto(url); pg.wait_for_selector("html[data-nbl=bereit]", timeout=30000)
            pg.add_style_tag(content="*{animation:none!important;transition:none!important;caret-color:transparent!important}")
            pg.evaluate("() => document.fonts.ready"); pg.wait_for_timeout(1500)
            rd = {}
            g = pg.evaluate(RD_GEOM)
            rd["V1"] = [crop(x, g["cx"], g["top"], SPAN) for x in twice(pg)]
            pg.locator("[data-nbrw-act=play]").first.click(); pg.wait_for_timeout(1500)
            for k, f in (("V2", 0), ("V3", 1), ("V4", 9)):
                g = pg.evaluate(RD_SCROLL, f); pg.wait_for_timeout(900)
                if g:
                    rd[k] = [ends(x, g) for x in twice(pg)]
            c.close()
            for k, nm in (("V1", "Deckblatt"), ("V2", "Kapitel 1"), ("V3", "Kapitel 2"), ("V4", "Ende")):
                if k not in lab or k not in rd:
                    row("%s %s %s" % (k, th, nm), False, "BAD keine Ansicht (Lab %s, Leser %s)" % (k in lab, k in rd)); continue
                share, n, h = compare("%s-%s" % (k, th), lab[k], rd[k])
                row("%s %s %s" % (k, th, nm), share <= MAX, "%.1f %% der Spalte verschieden (%d px von %d × %d, Grenze %.0f %%)"
                    % (share * 100, n, COL, h, MAX * 100))
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
    if JOUT:
        json.dump(rows, open(JOUT, "w"), indent=1, ensure_ascii=False)
    red = [r for r in rows if not r["ok"]]
    print("LAB-VS-READER %s (%d Zeilen, %d rot)" % ("OK" if rows and not red else "FAIL", len(rows), len(red)))
    sys.exit(0 if rows and not red else 1)
