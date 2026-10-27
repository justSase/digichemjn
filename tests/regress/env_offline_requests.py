"""E32 K3 · Python — REQUESTS TO FOREIGN HOSTS (Werkstatt Python, 2026-10-13).
    python3 tests/regress/env_offline_requests.py [--nb vorlage|complex|<file.ipynb>] [--json out.json]

The notebook should work offline after the first load (Antrag, Lite) and must
not call out by itself (privacy, DSB): fonts, CDNs, analytics. Pyodide may be
fetched only after a click on ▶ in the reading window (E26.3 R1). This script
opens the notebook the two ways that matter and counts EVERY request the
browser makes (context-wide: pages, iframes, workers, CSS @import/url(),
fonts, images, fetch/XHR, WebSocket) to a host that is not the local server:

  L  JupyterLab   real `jupyter lab` (token off), fresh copy, Run All from the
                  palette (lab_keys.open_nb), then ▶ Play on the cover; counted
                  from the page load, then 10 s more after Play
  R  reading      the PyCharm viewer of env_reader.py (real kernel, every
     window       output in an iframe of its own, served over http): 10 s on
                  the preview, Play, 10 s in the document — no ▶ pressed
                  anywhere (so Pyodide must not be asked for)

Local = 127.0.0.1 / localhost / data: / blob: / about: / chrome-extension:.
Counter self-test per row (after the count, not counted): a foreign <img>
put into the page / the reading frame must be seen, else the row is red.
Every foreign request is listed (host, resource type, URL head). Want 0 in
each row. Measuring only — nothing is changed by this script (STOP E32 K3).
Owner: Python. exit 0 = REGRESS-ENV-OFFLINE-REQUESTS OK."""
import sys, os, re, json, time, shutil, socket, subprocess, tempfile
from urllib.parse import urlparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

LOCAL = ("127.0.0.1", "localhost", "", "::1")
WAIT_S = 10

def foreign(url):
    u = urlparse(url)
    if u.scheme in ("data", "blob", "about", "chrome-extension", "chrome", "devtools"): return False
    return (u.hostname or "") not in LOCAL

class Rec:
    def __init__(self, ctx):
        self.all, self.out = 0, []
        ctx.on("request", self._r)
        ctx.on("websocket", lambda ws: None)
    def _r(self, req):
        self.all += 1
        if foreign(req.url):
            self.out.append((urlparse(req.url).hostname, req.resource_type, req.url[:110]))
    def mark(self): return len(self.out)
    def probe(self, pg, frame_js="document"):
        """Counter self-test: one foreign image from inside the page (not counted)."""
        n = len(self.out)
        pg.evaluate("() => { var d = %s; var i = d.createElement('img'); i.src = 'https://probe.invalid/x.png?' + Date.now(); d.body.appendChild(i); }" % frame_js)
        pg.wait_for_timeout(1500)
        hit = len(self.out) > n
        del self.out[n:]
        return hit

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def lab_row(b, src, rows, fails):
    from lab_keys import open_nb
    root = tempfile.mkdtemp(prefix="offreq_lab_")
    name = "nb_offreq.ipynb"; shutil.copy(src, os.path.join(root, name))
    port = free_port(); base = "http://127.0.0.1:%d" % port
    env = dict(os.environ, JUPYTER_DATA_DIR=os.path.join(root, ".jd"), JUPYTER_RUNTIME_DIR=os.path.join(root, ".jr"))
    lab = subprocess.Popen([sys.executable, "-m", "jupyter", "lab", "--no-browser", "--port=%d" % port,
                            "--ServerApp.token=", "--ServerApp.password=", "--ServerApp.disable_check_xsrf=True",
                            "--ServerApp.root_dir=" + root, "--allow-root", "--LabApp.news_url=", "--LabApp.check_for_updates_class=jupyterlab.NeverCheckForUpdate"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    try:
        import urllib.request
        for _ in range(120):
            try: urllib.request.urlopen(base + "/api", timeout=1); break
            except Exception: time.sleep(0.5)
        # open_nb makes its own context; record on the browser's contexts as they come
        orig = b.new_context
        holder = {}
        def nc(**kw):
            c = orig(**kw); holder["rec"] = Rec(c); return c
        b.new_context = nc
        try:
            t0 = time.time()
            ctx, pg, errs = open_nb(b, base, name)
        finally:
            b.new_context = orig
        rec = holder["rec"]; n_run = rec.mark()
        pg.wait_for_timeout(WAIT_S * 1000)
        if not rec.probe(pg): fails.append("L counter self-test: a foreign <img> in the Lab page was not seen")
        doc = pg.evaluate("() => !!document.querySelector('#nbpanel-root .nbmap')")
        rows.append("L  Lab: %d requests in all, %d foreign (%d up to Run All + Play, %d in the %d s after) · document %s · %.0f s"
                    % (rec.all, len(rec.out), n_run, len(rec.out) - n_run, WAIT_S, "yes" if doc else "NO", time.time() - t0))
        for h, t, u in rec.out: rows.append("     · %s [%s] %s" % (h, t, u))
        if rec.out: fails.append("L Lab: %d requests to foreign hosts (%s)" % (len(rec.out), ", ".join(sorted({h for h, _, _ in rec.out}))))
        if not doc: fails.append("L Lab: no document after Run All + Play")
        ctx.close()
    finally:
        lab.terminate()
        try: lab.wait(10)
        except Exception: lab.kill()
        shutil.rmtree(root, ignore_errors=True)

def reader_row(b, src, rows, fails):
    from env_iframe import run_cell, host_page
    from env_reader import serve, PLAY
    tmpd = tempfile.mkdtemp(prefix="offreq_rd_"); srv = serve(tmpd)
    try:
        outs, errs, chapters = run_cell(src, {})
        if errs: fails.append("R the run raised: %s" % errs[:1])
        open(os.path.join(tmpd, "r.html"), "w", encoding="utf-8").write(host_page(outs, False))
        ctx = b.new_context(viewport={"width": 1400, "height": 900}); rec = Rec(ctx)
        pg = ctx.new_page(); pg.goto("http://127.0.0.1:%d/r.html" % srv.server_address[1])
        pg.wait_for_timeout(WAIT_S * 1000); n_cover = rec.mark()
        fi = pg.evaluate("""() => [].slice.call(document.querySelectorAll('iframe.out')).findIndex(function(f){
              try { return !!f.contentDocument.querySelector('.nbrw'); } catch (e) { return false; } })""")
        played = False
        if fi >= 0:
            fr = pg.frames[fi + 1] if len(pg.frames) > fi + 1 else None
            try:
                fr = pg.frame_locator("iframe.out >> nth=%d" % fi)
                fr.locator("[data-nbrw-act=play]").first.click(timeout=5000); played = True
            except Exception as e:
                fails.append("R Play in the window: %s" % str(e)[:120])
        else:
            fails.append("R no reading window (.nbrw) in any output")
        pg.wait_for_timeout(WAIT_S * 1000)
        view = None
        if fi >= 0:
            view = pg.evaluate("(i) => { var w = document.querySelectorAll('iframe.out')[i].contentDocument.querySelector('.nbrw'); return w && w.getAttribute('data-nbrw-view'); }", fi)
        if fi >= 0 and not rec.probe(pg, "document.querySelectorAll('iframe.out')[%d].contentDocument" % fi):
            fails.append("R counter self-test: a foreign <img> in the reading frame was not seen")
        py = [x for x in rec.out if "pyodide" in x[2].lower()]
        rows.append("R  reading window: %d requests in all, %d foreign (%d on the preview in %d s, %d after Play in %d s) · view %s · Pyodide asked %d×"
                    % (rec.all, len(rec.out), n_cover, WAIT_S, len(rec.out) - n_cover, WAIT_S, view, len(py)))
        for h, t, u in rec.out: rows.append("     · %s [%s] %s" % (h, t, u))
        if rec.out: fails.append("R reading window: %d requests to foreign hosts (%s)" % (len(rec.out), ", ".join(sorted({h for h, _, _ in rec.out}))))
        if played and view != "doc": fails.append("R Play → view %r, want 'doc'" % view)
        ctx.close()
    finally:
        srv.shutdown(); shutil.rmtree(tmpd, ignore_errors=True)

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    args = sys.argv[1:]
    jout = args[args.index("--json") + 1] if "--json" in args else None
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    rows, fails = ["notebook: %s" % os.path.basename(src)], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for f in (lab_row, reader_row):
            try: f(b, src, rows, fails)
            except Exception as e: fails.append("BAD %s: %s" % (f.__name__, str(e)[:300]))
        b.close()
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-ENV-OFFLINE-REQUESTS OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
