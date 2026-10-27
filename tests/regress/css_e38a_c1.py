"""E38a C1 · CSS — Werkstatt CSS, 26.10. (Auftrag plan/AUFTRAG.md C1: „Stil digi im Lesefenster (15-reader kannte nur
minimal/cyber/fairy; seit E34 zeichnete es digi wie minimal) — hell + dunkel, Palette wie das Notebook“).
Gemessen im echten Chromium an lesen.html aus dem Bau-Ausgang (dist/huelle/<TOOLKIT>/lesen.html?nb=<id>&v=<NB>, E36):

    python3 tests/regress/css_e38a_c1.py [notebook.ipynb] [--dist DIR] [--sizes 1366x900,390x844] [--shots DIR] [--json out.json]

Je Breite × hell/dunkel, Stil digi als gespeicherte Wahl (digichemjn.<id>.reader.skin/.theme), Vorschau und Dokument (nach ▶):
  D1  Palette wie das Notebook (07-skins DIGI): Grund des Fensters #f6f7fb / #04050b, Panel #ffffff / #0b0e1c, Titel-Tinte
      #141826 / #e9ecf6, Kicker (Untertitel) Gold, Titelkarte 14 px, Kapitel-Pille 999 px; dunkel der Sternenhimmel am Scroller
      (genau eine SVG-Kachel 420 × 420, 68 Sterne #cfd6ff), hell keiner; und digi ≠ minimal (gleiche Seite, Stil minimal)
  D2  Seite um das Fenster = Grund des Fensters ± 2 (lesen.html, css/huelle/lesen.css)
  D3  Kontrast ≥ 4,5 : 1 für jeden sichtbaren Text im Fenster (ungünstigster Punkt des Grundes, Deckkraft eingerechnet)
  D4  VS Code: unter body.vscode-dark/-light mit --vscode-editor-background behält digi seinen Grund (minimal nimmt den Editor-Grund)
Gegenprobe v1.82 (2bb91ab5): rot D1 (digi = minimal). exit 0 = REGRESS-CSS-E38A-C1 OK."""
import sys, os, re, json, functools, threading, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from playwright.sync_api import sync_playwright
import css_e34 as E

A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
SIZES = [tuple(int(v) for v in s.split("x")) for s in opt("--sizes", "1366x900,390x844").split(",")]
SHOTS, JOUT = opt("--shots"), opt("--json")
WANT = {"light": {"bg": "#f6f7fb", "surf": "#ffffff", "title": "#141826"},
        "dark": {"bg": "#04050b", "surf": "#0b0e1c", "title": "#e9ecf6"}}
rows = []
def row(name, ok, detail):
    rows.append({"row": name, "ok": bool(ok), "detail": detail})
    print("%s  %-30s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)

PROBE = r"""() => {""" + E.COLOR_LIB + r"""
  var w = document.querySelector('.nbrw'); if (!w) return null;
  var q = function (s) { return w.querySelector(s); }, cs = function (e) { return e ? getComputedStyle(e) : null; };
  var win = q('.nbrw-win'), pan = q('.nbrw-panel'), card = q('.nbrw-cover .nbtitle-card') || q('.nbr-nbtitle-card');
  var vis = function (e) { var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  var cardV = [].filter.call(w.querySelectorAll('.nbrw-cover .nbtitle-card,.nbr-nbtitle-card'), vis)[0] || card;
  var t = cardV && cardV.querySelector('.nbtitle-h,.nbr-nbtitle-h'), sub = cardV && cardV.querySelector('.nbtitle-sub,.nbr-nbtitle-sub');
  var pill = [].filter.call(w.querySelectorAll('.nbreading h3.nbread-h'), vis)[0] || q('.nbreading h3.nbread-h');
  var img = cs(win).backgroundImage, svg = '';
  try { svg = decodeURIComponent((/url\("?data:image\/svg\+xml,(.*?)"?\)$/.exec(img) || [])[1] || ''); } catch (e) {}
  var col = function (s) { var c = norm(s); return c ? hex(c) : null; };
  // D3 — every visible text in the window against the worst point of its ground
  var R = w.getBoundingClientRect(), low = [], n = 0;
  var ground = function (e) { var st = [], op = 1;
    for (var a = e; a && a.nodeType === 1; a = a.parentElement) { var s = getComputedStyle(a); op *= parseFloat(s.opacity) || 1;
      var bc = norm(s.backgroundColor), im = s.backgroundImage !== 'none' ? stops(s.backgroundImage).map(norm).filter(Boolean) : [];
      if ((bc && bc[3] > 0) || im.length) st.push({bc: bc, img: im}); if (bc && bc[3] >= .99) break; }
    var c = [[255, 255, 255, 1]];
    for (var i = st.length - 1; i >= 0; i--) { var L = st[i], nc = [], cover = L.img.length && L.img.every(function (g) { return g[3] >= .99; });
      c.forEach(function (b) { var b2 = L.bc && L.bc[3] > 0 ? over(L.bc, b) : b; if (!cover) nc.push(b2); L.img.forEach(function (g) { nc.push(over(g, b2)); }); });
      c = nc.slice(0, 64); }
    return {c: c, op: op}; };
  [].forEach.call(w.querySelectorAll('*'), function (e) {
    if (/^(SCRIPT|STYLE|SVG|PATH|IMG|INPUT|TEXTAREA|MJX-CONTAINER)$/i.test(e.tagName) || e.closest('svg,mjx-container,.MathJax,[aria-hidden=true]')) return;
    var own = ''; for (var x = e.firstChild; x; x = x.nextSibling) if (x.nodeType === 3) own += x.nodeValue;
    if (!/[A-Za-zÄÖÜäöüß0-9]/.test(own)) return;
    var r = e.getBoundingClientRect(); if (r.width < 1 || r.height < 1 || r.bottom < R.top || r.top > R.bottom || r.right < R.left || r.left > R.right) return;
    for (var p = e; p; p = p.parentElement) { var ps = getComputedStyle(p); if (ps.display === 'none' || ps.visibility === 'hidden') return; }
    var fg = norm(getComputedStyle(e).color); if (!fg || fg[3] < .05) return;
    var g = ground(e), worst = 99, wb = null;
    g.c.forEach(function (b) { var f = over([fg[0], fg[1], fg[2], fg[3] * g.op], b), k = ratio(f, b); if (k < worst) { worst = k; wb = b; } });
    n++; if (worst < 4.5) low.push(own.trim().slice(0, 24) + ' ' + hex(fg) + '/' + (wb ? hex(wb) : '?') + ' ' + worst.toFixed(2)); });
  return {skin: w.getAttribute('data-nbrw-skin'), bg: col(cs(w).backgroundColor), surf: col(cs(pan).backgroundColor),
          title: t ? col(cs(t).color) : null, sub: sub ? cs(sub).color : null, subGold: sub ? gold(norm(cs(sub).color)) || /^#(8a5f00|9a6b00)$/.test(col(cs(sub).color)) : false,
          cardR: cardV ? parseFloat(cs(cardV).borderTopLeftRadius) : null, pillR: pill ? parseFloat(cs(pill).borderTopLeftRadius) : null,
          tiles: (img.match(/url\(/g) || []).length, size: cs(win).backgroundSize, att: cs(win).backgroundAttachment,
          stars: (svg.match(/<circle/g) || []).length, fill: (/fill='([^']+)'/.exec(svg) || [])[1] || null,
          html: col(getComputedStyle(document.documentElement).backgroundColor), n: n, low: low}; }"""

def find_dist(nbf):
    for d in (opt("--dist"), os.environ.get("DIGICHEM_DIST"), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(nbf))), "dist"),
              os.path.join(ROOT, "dist")):
        if d and os.path.isdir(os.path.join(d, "huelle")):
            return d
    return None

def near(a, b, t=2):
    if not a or not b: return False
    x = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; y = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return max(abs(p - q) for p, q in zip(x, y)) <= t

def main():
    import nbpick
    nbf = os.path.abspath(nbpick.from_argv(sys.argv))
    m = json.load(open(nbf, encoding="utf-8")).get("metadata", {}).get("digichemjn", {})
    nid, nbv, tv = m.get("id") or "vorlage", m.get("version") or "", m.get("toolkit") or ""
    dist = find_dist(nbf)
    if not dist:
        row("D0 Bau-Ausgang", False, "BAD kein dist/ mit huelle/ — erst bauen"); return
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=dist))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/huelle/%s/lesen.html?nb=%s&v=%s" % (srv.server_address[1], tv, nid, nbv)
    with sync_playwright() as P:
        b = P.chromium.launch(executable_path=E.CHROME if os.path.exists(E.CHROME) else None)
        def page(W, H, th, skin, vscode=None):
            c = b.new_context(viewport={"width": W, "height": H}, color_scheme=th)
            c.add_init_script("try{localStorage.clear();localStorage.setItem('digichemjn.%s.reader.skin','%s');"
                              "localStorage.setItem('digichemjn.%s.reader.theme','%s')}catch(e){}" % (nid, skin, nid, th))
            if vscode:
                c.add_init_script("document.addEventListener('DOMContentLoaded',function(){document.body.classList.add('vscode-%s');"
                                  "document.documentElement.style.setProperty('--vscode-editor-background','%s')})" % (vscode, "#1e1e1e" if vscode == "dark" else "#fffffe"))
            pg = c.new_page(); pg.goto(url); pg.locator(".nbrw").first.wait_for(timeout=30000); pg.wait_for_timeout(1300)
            return c, pg
        for W, H in SIZES:
            for th in ("light", "dark"):
                tag = "%d %s" % (W, th)
                c, pg = page(W, H, th, "minimal"); mini = pg.evaluate(PROBE); c.close()
                c, pg = page(W, H, th, "digi")
                for view in ("Vorschau", "Dokument"):
                    if view == "Dokument":
                        pg.locator(".nbrw-play").first.click(); pg.wait_for_timeout(1300)
                    v = pg.evaluate(PROBE)
                    if not v:
                        row("D1 %s %s" % (tag, view), False, "BAD kein .nbrw"); continue
                    w = WANT[th]
                    tex = (v["tiles"] == 1 and v["stars"] == 68 and v["fill"] == "#cfd6ff" and v["size"] == "420px 420px"
                           and v["att"] == "scroll") if th == "dark" else v["tiles"] == 0
                    ok = (v["skin"] == "digi" and near(v["bg"], w["bg"]) and near(v["surf"], w["surf"]) and near(v["title"], w["title"])
                          and v["subGold"] and v["cardR"] == 14 and (v["pillR"] or 0) >= 99 if view == "Dokument" else True) \
                        and v["skin"] == "digi" and near(v["bg"], w["bg"]) and near(v["title"], w["title"]) and v["cardR"] == 14 and tex \
                        and v["bg"] != (mini or {}).get("bg")
                    row("D1 %s %s" % (tag, view), ok, "skin %s · Grund %s (minimal %s) · Panel %s · Titel %s · Kicker %s · Karte %s px · Pille %s px · "
                        "Kachel %d/%d Sterne %s %s %s" % (v["skin"], v["bg"], (mini or {}).get("bg"), v["surf"], v["title"], v["sub"], v["cardR"],
                                                          v["pillR"], v["tiles"], v["stars"], v["fill"], v["size"], v["att"]))
                    if view == "Vorschau":
                        row("D2 %s Seite" % tag, near(v["html"], v["bg"]), "Seite %s · Fenster %s" % (v["html"], v["bg"]))
                    row("D3 %s %s Kontrast" % (tag, view), not v["low"] and v["n"] > 10, "%d/%d unter 4,5 %s" % (len(v["low"]), v["n"], v["low"][:5]))
                    if SHOTS:
                        os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, "C1-%d-%s-%s.png" % (W, th, view)))
                c.close()
                if W == SIZES[0][0]:
                    ed = "#1e1e1e" if th == "dark" else "#fffffe"
                    c, pg = page(W, H, th, "digi", vscode=th); v = pg.evaluate(PROBE); c.close()
                    c, pg = page(W, H, th, "minimal", vscode=th); mv = pg.evaluate(PROBE); c.close()
                    row("D4 %s VS Code" % tag, v and near(v["bg"], WANT[th]["bg"]), "digi %s · minimal %s (Editor %s)" % (
                        v and v["bg"], mv and mv["bg"], ed))
        b.close()
    srv.shutdown()

main()
if JOUT: json.dump(rows, open(JOUT, "w"), ensure_ascii=False, indent=1)
bad = [r["row"] for r in rows if not r["ok"]]
print("%d Zeilen, %d rot%s" % (len(rows), len(bad), (": " + ", ".join(bad[:10])) if bad else ""))
print("REGRESS-CSS-E38A-C1 OK" if not bad else "REGRESS-CSS-E38A-C1 RED")
sys.exit(1 if bad else 0)
