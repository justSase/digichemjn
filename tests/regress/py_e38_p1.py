"""E38 P1 (2026-10-27, Python) — DIE SCHRIFTEN VON digi KOMMEN MIT DER HÜLLE.
    python3 tests/regress/py_e38_p1.py [--dist dist] [--nb vorlage]      (nach dem Bau: dist/ ist da)

Bis v1.84 war manifest.fonts leer: lesen.html zeichnete Überschriften, Text und Code in Systemschriften (Dirigent 27.10.:
„Dem Leser fehlen: Unbounded“). Jetzt: Unbounded, Instrument Sans, JetBrains Mono als woff2 (sha8 im Namen) + OFL in der Hülle.
  F1  manifest.fonts: die drei Familien, je Eintrag Datei da, woff2, sha8 = Name = Inhalt, Bytes stimmen, Lizenz-Datei da
      (SIL OFL); manifest.css beginnt mit schriften.<sha8>.css, die für jeden Eintrag ein @font-face mit dieser Datei hat
  F2  gemessen in Chromium über http (dist/ wie ein Server), en und de, Deckblatt und nach ▶ das Dokument: die Schrift,
      mit der der Browser WIRKLICH zeichnet (CDP CSS.getPlatformFontsForNode), ist für eine Überschrift (--rw-head)
      „Unbounded“, für Fließtext (--rw-font) „Instrument Sans“, für Code (--rw-mono) „JetBrains Mono“, je als Webschrift
  F3  jede Schrift-Anfrage geht an denselben Ursprung (0 fremde Hosts), keine scheitert
Gegenprobe v1.84: F1 rot (fonts = []), F2 rot (Systemschrift, z. B. DejaVu Sans). Besitzer: Python."""
import sys, os, re, json, glob, hashlib, threading, functools, http.server, socketserver
a = sys.argv[1:]
DIST = os.path.abspath(a[a.index("--dist") + 1] if "--dist" in a else "dist")
NB = a[a.index("--nb") + 1] if "--nb" in a else "vorlage"
SHOT = a[a.index("--shot") + 1] if "--shot" in a else None
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
WANT = {"head": "Unbounded", "font": "Instrument Sans", "mono": "JetBrains Mono"}


def serve(root):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *x): pass
        def end_headers(self):
            self.send_header("Cache-Control", "no-store"); super().end_headers()
    s = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Q, directory=root))
    s.daemon_threads = True
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


# drei sichtbare Elemente, deren berechnete Schrift mit der Variable des Lesers beginnt (gemessen, nicht gelesen)
PICK = r"""() => {
  var root = document.querySelector('.nbrw'); if (!root) return {err: 'kein .nbrw'};
  var cs = getComputedStyle(root), out = {};
  var first = function (v) { return (v || '').split(',')[0].trim().replace(/^["']|["']$/g, ''); };
  var want = {head: first(cs.getPropertyValue('--rw-head')), font: first(cs.getPropertyValue('--rw-font')),
              mono: first(cs.getPropertyValue('--rw-mono'))};
  var all = root.querySelectorAll('*'), n = 0;
  for (var i = 0; i < all.length; i++) {
    var e = all[i], r = e.getBoundingClientRect();
    if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > innerHeight) continue;
    var own = Array.prototype.some.call(e.childNodes, function (c) { return c.nodeType === 3 && /[A-Za-z]{3}/.test(c.textContent); });
    if (!own) continue;
    var f = first(getComputedStyle(e).fontFamily);
    for (var k in want) if (!out[k] && want[k] && f === want[k]) {
      e.setAttribute('data-e38p1', k); out[k] = {tag: e.tagName, cls: e.className && String(e.className).slice(0, 40),
        text: e.textContent.trim().slice(0, 30)}; n++;
    }
  }
  return {want: want, found: out};
}"""


def platform(pg, cdp, k):
    doc = cdp.send("DOM.getDocument", {"depth": 0})
    q = cdp.send("DOM.querySelector", {"nodeId": doc["root"]["nodeId"], "selector": "[data-e38p1='%s']" % k})
    if not q.get("nodeId"):
        return None
    f = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": q["nodeId"]})["fonts"]
    return sorted(f, key=lambda x: -x["glyphCount"])


def main():
    rows, fails = [], []
    v = json.load(open(os.path.join(DIST, "inhalt", NB, "aktuell.json")))["v"]
    meta = json.load(open(os.path.join(DIST, "inhalt", NB, v, "meta.json")))
    H = os.path.normpath(os.path.join(DIST, "inhalt", NB, v, meta["huelle"]))
    man = json.load(open(H)); H = os.path.dirname(H); tv = man["toolkit"]
    # ---- F1
    f1 = []
    fo = man.get("fonts") or []
    fams = sorted({x.get("family") for x in fo})
    if fams != sorted(set(WANT.values())):
        f1.append("Familien %s" % fams)
    css0 = (man.get("css") or [""])[0]
    ctext = open(os.path.join(H, css0), encoding="utf-8").read() if css0 and os.path.isfile(os.path.join(H, css0)) else ""
    if not re.match(r"schriften\.[0-9a-f]{8}\.css$", css0 or ""):
        f1.append("css[0] = %r" % css0)
    for x in fo:
        p = os.path.join(H, x.get("file") or "?")
        b = open(p, "rb").read() if os.path.isfile(p) else b""
        h = hashlib.sha256(b).hexdigest()
        if not b or b[:4] != b"wOF2" or h[:8] != x.get("sha8") or h[:8] not in x["file"] or len(b) != x.get("bytes"):
            f1.append("%s %s: Datei/woff2/sha8/Bytes" % (x.get("family"), x.get("weight")))
        lp = os.path.join(H, x.get("lizenz") or "?")
        if not os.path.isfile(lp) or b"SIL Open Font License" not in open(lp, "rb").read():
            f1.append("%s: Lizenz %r" % (x.get("family"), x.get("lizenz")))
        if not re.search(r"@font-face\{font-family:\"%s\";[^}]*font-weight:%s;[^}]*url\(%s\)" % (re.escape(x["family"]), x["weight"],
                                                                                         re.escape(x["file"])), ctext):
            f1.append("%s %s: kein @font-face in %s" % (x["family"], x["weight"], css0))
    rows.append("F1 manifest.fonts %d Einträge %s · css[0] %s · %s" % (len(fo), fams, css0, "; ".join(f1) or "OK"))
    if f1 or not fo:
        fails.append("F1")
    # ---- F2/F3
    s = serve(DIST); port = s.server_address[1]
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for lang in ("en", "de"):
            ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark")
            pg = ctx.new_page(); req = []
            pg.on("request", lambda r: req.append(r.url) if r.resource_type == "font" or r.url.endswith(".woff2") else None)
            bad_req = []
            pg.on("requestfailed", lambda r: bad_req.append(r.url))
            pg.goto("http://127.0.0.1:%d/huelle/%s/lesen.html?nb=%s&v=%s&lang=%s" % (port, tv, NB, v, lang))
            try:
                pg.wait_for_function("() => document.documentElement.getAttribute('data-nbl') !== 'laden'", timeout=30000)
            except Exception:
                pass
            pg.evaluate("() => document.fonts.ready")
            pg.wait_for_timeout(600)
            cdp = ctx.new_cdp_session(pg); cdp.send("DOM.enable"); cdp.send("CSS.enable")
            for stage in ("Deckblatt", "Dokument"):
                if stage == "Dokument":
                    pl = pg.query_selector(".nbrw [data-nbrw-act=play]")
                    if pl:
                        pl.click(); pg.wait_for_timeout(1200)
                    pg.evaluate("() => document.fonts.ready"); pg.wait_for_timeout(300)
                pg.evaluate("() => document.querySelectorAll('[data-e38p1]').forEach(function (e) { e.removeAttribute('data-e38p1'); })")
                got = pg.evaluate(PICK)
                if stage == "Dokument" and SHOT and lang == "en":
                    pg.screenshot(path=SHOT)
                for k, w in WANT.items():
                    if (got.get("want") or {}).get(k) != w:
                        rows.append("F2 %s %s %s: Variable --rw-%s beginnt mit %r (nicht %s) · RED" % (lang, stage, k, k,
                                    (got.get("want") or {}).get(k), w))
                        fails.append("F2 %s %s %s" % (lang, stage, k)); continue
                    if not (got.get("found") or {}).get(k):
                        if k == "mono" and stage == "Deckblatt":
                            continue                     # das Deckblatt zeigt keinen Code: nur im Dokument gefordert
                        rows.append("F2 %s %s %s: kein sichtbares Element mit %s · RED (BAD)" % (lang, stage, k, w))
                        fails.append("F2 %s %s %s" % (lang, stage, k)); continue
                    pf = platform(pg, cdp, k) or []
                    top = pf[0] if pf else {}
                    ok = top.get("familyName") == w and top.get("isCustomFont")
                    rows.append("F2 %s %s %s <%s %s> %r: gezeichnet mit %s · %s" % (
                        lang, stage, k, got["found"][k]["tag"].lower(), got["found"][k]["cls"], got["found"][k]["text"],
                        ", ".join("%s%s %d" % (x["familyName"], " (Web)" if x.get("isCustomFont") else "", x["glyphCount"]) for x in pf)
                        or "?", "OK" if ok else "RED"))
                    if not ok:
                        fails.append("F2 %s %s %s" % (lang, stage, k))
            fremd = [u for u in req if not u.startswith("http://127.0.0.1:%d/" % port) and not u.startswith("data:")]
            ok3 = req and not fremd and not bad_req
            rows.append("F3 %s Schrift-Anfragen %d, fremde Hosts %d, gescheitert %d · %s" % (lang, len(req), len(fremd), len(bad_req),
                        "OK" if ok3 else "RED"))
            if not ok3:
                fails.append("F3 %s" % lang)
            ctx.close()
        b.close()
    s.shutdown()
    print("\n".join(rows))
    print("PY-E38-P1 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
