"""E38a P1 (2026-10-26, Python) — THE READING LINE IN lesen.html FITS THE PAGE.
    python3 tests/regress/py_e38a_p1.py [--dist dist] [--nb vorlage]      (after the build: dist/ exists)

lesen.html (Ausgang A) shows the reading version of the package; its first line said
"run the cell in JupyterLab, or open the notebook on the Lite page" — on a page without a cell.
Measured in Chromium over http (dist/ served as a server would), en and de (&lang=de):
  L1  the visible .nbread-line names no JupyterLab / Lite page / cell, and says where things work
      (en "right here" + "browser", de "hier" + "Browser")
  L2  the same line in the package file (lesefassung.<lang>.html) — what any loader shows
Gegenprobe v1.82: L1/L2 red (the line names JupyterLab). Owner: Python."""
import sys, os, re, json, threading, functools, http.server, socketserver, glob
a = sys.argv[1:]
DIST = os.path.abspath(a[a.index("--dist") + 1] if "--dist" in a else "dist")
NB = a[a.index("--nb") + 1] if "--nb" in a else "vorlage"
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
WANT = {"en": ("right here", "browser"), "de": ("hier", "Browser")}
BAD = re.compile(r"JupyterLab|Lite[- ]Seite|Lite page|run the cell|Zelle", re.I)

def serve(root):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *x): pass
    h = functools.partial(Q, directory=root)
    s = socketserver.TCPServer(("127.0.0.1", 0), h); threading.Thread(target=s.serve_forever, daemon=True).start()
    return s

def main():
    v = json.load(open(os.path.join(DIST, "inhalt", NB, "aktuell.json")))["v"]
    hull = sorted(glob.glob(os.path.join(DIST, "huelle", "*", "lesen.html")))[-1]
    tv = os.path.basename(os.path.dirname(hull))
    rows, fails = [], []
    for lang in ("en", "de"):
        f = open(os.path.join(DIST, "inhalt", NB, v, "lesefassung.%s.html" % lang), encoding="utf-8").read()
        m = re.search(r"<div class='nbread-line'>(.*?)</div>", f, re.S)
        t = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
        ok = bool(m) and not BAD.search(t) and all(w in t for w in WANT[lang])
        rows.append("L2 %s package line: %s · %r" % (lang, "OK" if ok else "RED", t[:120]))
        if not ok: fails.append("L2 %s" % lang)
    s = serve(DIST); port = s.server_address[1]
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for lang in ("en", "de"):
            pg = b.new_page(viewport={"width": 1400, "height": 900})
            pg.goto("http://127.0.0.1:%d/huelle/%s/lesen.html?nb=%s&v=%s&lang=%s" % (port, tv, NB, v, lang))
            try: pg.wait_for_function("() => document.documentElement.getAttribute('data-nbl') !== 'laden'", timeout=30000)
            except Exception: pass
            st = pg.evaluate("() => document.documentElement.getAttribute('data-nbl')")
            pg.wait_for_timeout(800)
            pl = pg.query_selector(".nbrw [data-nbrw-act=play]")      # the window opens on the cover: Play → document
            if pl: pl.click(); pg.wait_for_timeout(1200)
            t = pg.evaluate("""() => { var e = document.querySelector('.nbread-line'); if (!e) return null;
                var b = e.getBoundingClientRect(); return b.height > 0 ? e.innerText : '(hidden)'; }""")
            ok = st == "bereit" and bool(t) and t != "(hidden)" and not BAD.search(t) and all(w in t for w in WANT[lang])
            rows.append("L1 %s lesen.html (%s): %s · %r" % (lang, st, "OK" if ok else "RED", (t or "")[:120]))
            if not ok: fails.append("L1 %s" % lang)
            pg.close()
        b.close()
    s.shutdown()
    print("\n".join(rows))
    print("PY-E38A-P1 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
