"""E38a C2 · CSS — Werkstatt CSS, 26.10. (Auftrag plan/AUFTRAG.md C2: „I390: bei 390 px ragen keine Kapitelnamen der Vorschau
über den Rand“; css_e36 I390 war nur INFO). Gemessen an lesen.html aus dem Bau-Ausgang (dist/, E36), echtes Chromium:

    python3 tests/regress/css_e38a_c2.py [notebook.ipynb] [--dist DIR] [--widths 390,360] [--shots DIR] [--json out.json]

Je Breite × Stil (digi, minimal, cyber, fairy) × hell/dunkel × Sprache (EN, DE über den Knopf der Vorschau), Vorschau:
  I390  kein Element mit eigenem Text im Fenster ragt über den Rand von .nbrw-win (wie css_e36 I390), UND jeder Name der
        Zeitleiste (.nbrw-cv-lab) ist waagrecht ganz zu sehen: kein Vorfahr mit overflow ≠ visible schneidet ihn ab, kein Bildlauf
        in der Leiste (scrollWidth ≤ clientWidth + 1), mindestens 5 Namen sichtbar
  W     breit (1366): die Zeitleiste bleibt die Reihe von E31 T1 (Marken absolut gesetzt, Leiste nicht senkrecht)
Gegenprobe v1.82 (2bb91ab5): rot I390 (5 Namen abgeschnitten, Leiste rollt). exit 0 = REGRESS-CSS-E38A-C2 OK."""
import sys, os, json, functools, threading, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from playwright.sync_api import sync_playwright
import css_e34 as E

A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
WIDTHS = [int(v) for v in opt("--widths", "390,360").split(",")]
SKINS = opt("--skins", "digi,minimal,cyber,fairy").split(",")
SHOTS, JOUT = opt("--shots"), opt("--json")
rows = []
def row(name, ok, detail):
    rows.append({"row": name, "ok": bool(ok), "detail": detail})
    print("%s  %-34s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)

CUT = r"""() => { var w = document.querySelector('.nbrw-win'); if (!w) return null; var R = w.getBoundingClientRect(), out = [], labs = [];
  var shown = function (e) { for (var x = e; x; x = x.parentElement) { var s = getComputedStyle(x); if (s.display === 'none' || s.visibility === 'hidden') return false; } return true; };
  [].forEach.call(w.querySelectorAll('*'), function (e) {
    var t = [].filter.call(e.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); }).length;
    if (!t) return; var b = e.getBoundingClientRect(), s = getComputedStyle(e);
    if (!(b.width > 0 && b.height > 0) || !shown(e)) return;
    if (b.bottom < R.top || b.top > R.bottom) return;
    if (b.right > R.right + 1 || b.left < R.left - 1 || e.scrollWidth > e.clientWidth + 1 && s.overflow !== 'visible')
      out.push(e.textContent.trim().slice(0, 30)); });
  [].forEach.call(w.querySelectorAll('.nbrw-cv-lab'), function (e) {
    if (!e.textContent.trim() || !shown(e)) return; var b = e.getBoundingClientRect(); if (!(b.width > 0)) return;
    if (b.bottom < R.top || b.top > R.bottom) return;   // scrolled out of the window's height: not the question here
    var cut = false;
    for (var x = e.parentElement; x && x !== w.parentElement; x = x.parentElement) { var s = getComputedStyle(x);
      if (s.overflowX !== 'visible' || s.overflowY !== 'visible') { var r = x.getBoundingClientRect();
        if (b.left < r.left - 1 || b.right > r.right + 1) cut = true; } }
    labs.push([e.textContent.trim().slice(0, 30), cut]); });
  var sc = w.querySelector('.nbrw-cv-scroll'), inn = w.querySelector('.nbrw-cv-in'), dot = w.querySelector('.nbrw-cv-dot');
  return {cut: out, labs: labs, scroll: sc ? [sc.scrollWidth, sc.clientWidth] : null, inDisp: inn ? getComputedStyle(inn).display : null,
          dotPos: dot ? getComputedStyle(dot).position : null}; }"""

def find_dist(nbf):
    for d in (opt("--dist"), os.environ.get("DIGICHEM_DIST"), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(nbf))), "dist"),
              os.path.join(ROOT, "dist")):
        if d and os.path.isdir(os.path.join(d, "huelle")):
            return d

def main():
    import nbpick
    nbf = os.path.abspath(nbpick.from_argv(sys.argv))
    m = json.load(open(nbf, encoding="utf-8")).get("metadata", {}).get("digichemjn", {})
    nid, nbv, tv = m.get("id") or "vorlage", m.get("version") or "", m.get("toolkit") or ""
    dist = find_dist(nbf)
    if not dist:
        row("I0 Bau-Ausgang", False, "BAD kein dist/ — erst bauen"); return
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=dist))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/huelle/%s/lesen.html?nb=%s&v=%s" % (srv.server_address[1], tv, nid, nbv)
    with sync_playwright() as P:
        b = P.chromium.launch(executable_path=E.CHROME if os.path.exists(E.CHROME) else None)
        def page(W, H, th, skin):
            c = b.new_context(viewport={"width": W, "height": H}, color_scheme=th)
            c.add_init_script("try{localStorage.clear();localStorage.setItem('digichemjn.%s.reader.skin','%s');"
                              "localStorage.setItem('digichemjn.%s.reader.theme','%s')}catch(e){}" % (nid, skin, nid, th))
            pg = c.new_page(); pg.goto(url); pg.locator(".nbrw").first.wait_for(timeout=30000); pg.wait_for_timeout(1300)
            return c, pg
        for W in WIDTHS:
            for sk in SKINS:
                for th in ("light", "dark"):
                    c, pg = page(W, 844, th, sk)
                    for lang in ("en", "de"):
                        tag = "I390 %d %s %s %s" % (W, sk, th, lang)
                        if lang == "de":
                            k = pg.locator(".nbrw-lang>button[data-lang=de]")
                            if not k.count():
                                row(tag, False, "BAD kein Knopf DE"); continue
                            k.first.click(); pg.wait_for_timeout(900)
                        v = pg.evaluate(CUT)
                        if not v:
                            row(tag, False, "BAD kein .nbrw-win"); continue
                        clipped = [l for l, cut in v["labs"] if cut]
                        sc = v["scroll"]
                        ok = not v["cut"] and not clipped and len(v["labs"]) >= 5 and (not sc or sc[0] <= sc[1] + 1)
                        row(tag, ok, "über den Rand %d %s · Namen %d, abgeschnitten %d %s · Leiste %s" % (
                            len(v["cut"]), v["cut"][:3], len(v["labs"]), len(clipped), clipped[:3], sc))
                        if SHOTS and sk == "minimal" and th == "light":
                            os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, "C2-%d-%s.png" % (W, lang)))
                    c.close()
        c, pg = page(1366, 900, "light", "minimal"); v = pg.evaluate(CUT); c.close()
        row("W 1366 Reihe", v and v["inDisp"] != "grid" and v["dotPos"] == "absolute", "Leiste %s · Marke %s" % (
            v and v["inDisp"], v and v["dotPos"]))
        b.close()
    srv.shutdown()

main()
if JOUT: json.dump(rows, open(JOUT, "w"), ensure_ascii=False, indent=1)
bad = [r["row"] for r in rows if not r["ok"]]
print("%d Zeilen, %d rot%s" % (len(rows), len(bad), (": " + ", ".join(bad[:10])) if bad else ""))
print("REGRESS-CSS-E38A-C2 OK" if not bad else "REGRESS-CSS-E38A-C2 RED")
sys.exit(1 if bad else 0)
