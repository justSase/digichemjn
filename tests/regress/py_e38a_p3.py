"""E38a P3 (2026-10-26, Python) — THE CELL A READER SEES IS ASCII · PyCharm's `jetTransient` IS TOLERATED.
    python3 tests/regress/py_e38a_p3.py [--nb vorlage|<file.ipynb>] [--no-vscode] [--no-lab]
    (code-server: DIGICHEM_CODE_SERVER=<…/bin/code-server>, else on PATH)

Befund zu v1.79: VS Code drew ▶ ⚠ → — · in the code cell's comments as boxes.
  A1  file: every line of every code cell that is not the cargo (_NBZ) is ASCII — the #@title line, the comment block,
      the editor-fold, the loader
  A2  VS Code (code-server, built file opened like a reader): the text VS Code's editor shows for the code cell
      (.view-line) has no character above U+007F — what it would have to draw from a font
PyCharm writes `"jetTransient": {"display_id": null}` into an output (outside `metadata`): nbformat calls the file invalid.
Measured 26.10. (Lab 4, Notebook 7, nbconvert): it opens, nothing is refused, the server only logs; Run All replaces the
output, the saved file is valid again — so: tolerate, nothing to clean. This row keeps it that way:
  B1  JupyterLab, the built file with jetTransient in its saved output: no dialog, 2 cells, the saved preview drawn,
      Run All draws our document, Ctrl+S → the file on disk is valid nbformat and has no jetTransient
Gegenprobe v1.82: A1/A2 red (▶ ⚠ → — ü in the comments); B1 green there too (a guard, not a change). Owner: Python."""
import sys, os, re, json, time, shutil, socket, subprocess, tempfile, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
if not os.path.exists(CHROME):
    from lab_keys import CHROME

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def a1(nb):
    bad = []
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code": continue
        for n, l in enumerate("".join(c["source"]).split("\n")):
            if l.startswith("_NBZ = "): continue
            if not l.isascii(): bad.append("cell %d line %d: %r" % (i, n + 1, "".join(sorted({ch for ch in l if ord(ch) > 127}))))
    return bad

def a2(src, cs):
    root = tempfile.mkdtemp(prefix="e38a-p3-"); ws = os.path.join(root, "ws"); os.makedirs(ws)
    name = os.path.basename(src); shutil.copy(src, os.path.join(ws, name))
    ud, ext = os.path.join(root, "ud"), os.path.join(root, "ext"); os.makedirs(os.path.join(ud, "User"))
    json.dump({"security.workspace.trust.enabled": False, "workbench.startupEditor": "none", "update.mode": "none",
               "telemetry.telemetryLevel": "off", "chat.disableAIFeatures": True, "workbench.colorTheme": "Default Light Modern"},
              open(os.path.join(ud, "User", "settings.json"), "w"))
    port = free_port()
    srv = subprocess.Popen([cs, "--auth", "none", "--bind-addr", "127.0.0.1:%d" % port, "--user-data-dir", ud, "--extensions-dir", ext,
                            "--disable-telemetry", "--disable-update-check", "--disable-workspace-trust", ws],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from playwright.sync_api import sync_playwright
    try:
        time.sleep(4)
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            pg = b.new_page(viewport={"width": 1400, "height": 900})
            pg.goto("http://127.0.0.1:%d/?folder=%s" % (port, ws)); pg.wait_for_selector(".monaco-workbench", timeout=90000)
            pg.wait_for_timeout(4000); pg.keyboard.press("Control+P"); pg.wait_for_timeout(800); pg.keyboard.type(name)
            pg.wait_for_timeout(1200); pg.keyboard.press("Enter")
            pg.wait_for_selector(".notebook-editor .cell-editor-container .view-line", timeout=60000); pg.wait_for_timeout(3000)
            lines = pg.evaluate("""() => [].map.call(document.querySelectorAll('.notebook-editor .cell-editor-container .view-line'),
                                    e => e.textContent.replace(/\\u00a0/g, ' '))""")
            b.close()
    finally:
        srv.terminate(); srv.wait(10); shutil.rmtree(root, ignore_errors=True)
    shown = [l for l in lines if l.strip() and not l.startswith("_NBZ")]
    return len(shown), [l[:70] for l in shown if not l.isascii()]

def b1(src):
    import nbformat
    root = tempfile.mkdtemp(prefix="e38a-p3b-"); home = os.path.join(root, "home"); os.makedirs(home)
    nb = json.load(open(src, encoding="utf-8")); outs = [o for c in nb["cells"] for o in c.get("outputs", [])]
    if not outs: return False, "BAD the built file has no saved output to put jetTransient into"
    for o in outs: o["jetTransient"] = {"display_id": None}                 # as PyCharm writes it
    fn = "jet.ipynb"; json.dump(nb, open(os.path.join(root, fn), "w"), ensure_ascii=False, indent=1)
    try:
        nbformat.validate(nbformat.read(os.path.join(root, fn), as_version=4)); return False, "BAD the injected file is valid (not what PyCharm writes)"
    except nbformat.ValidationError: pass
    port = free_port()
    srv = subprocess.Popen([sys.executable, "-m", "jupyter", "lab", "--no-browser", "--port", str(port), "--allow-root",
                            "--IdentityProvider.token=", "--ServerApp.password=", "--notebook-dir", root], cwd=root,
                           env=dict(os.environ, HOME=home, JUPYTER_CONFIG_DIR=os.path.join(home, ".jupyter")),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from playwright.sync_api import sync_playwright
    try:
        for _ in range(90):
            try: urllib.request.urlopen("http://127.0.0.1:%d/api" % port, timeout=2); break
            except Exception: time.sleep(1)
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            pg = b.new_page(viewport={"width": 1400, "height": 900})
            pg.goto("http://127.0.0.1:%d/lab/tree/%s?reset" % (port, fn)); pg.wait_for_timeout(9000)
            dlg = pg.query_selector(".jp-Dialog"); cells = len(pg.query_selector_all(".jp-Notebook .jp-Cell"))
            still = len(pg.query_selector_all(".jp-OutputArea-output .nbstill, .jp-OutputArea-output img"))
            pg.click(".lm-MenuBar-itemLabel:text-is('Run')", timeout=8000); pg.wait_for_timeout(500)
            pg.click(".lm-Menu-itemLabel:text-is('Run All Cells')", timeout=8000)
            t0 = time.time(); ran = False
            while time.time() - t0 < 150 and not ran:
                pg.wait_for_timeout(1000); ran = bool(pg.query_selector("#nbpanel-root, .nbcover-out, .nbrw, iframe[data-digichemjn-rahmen]"))  # E38 P3: das Paket im eigenen Rahmen
            pg.wait_for_timeout(2000); pg.keyboard.press("Control+s"); pg.wait_for_timeout(4000)
            dlg2 = pg.query_selector(".jp-Dialog")
            b.close()
    finally:
        srv.terminate(); srv.wait(10)
    txt = open(os.path.join(root, fn), encoding="utf-8").read()
    try: nbformat.validate(nbformat.reads(txt, as_version=4)); valid = True
    except Exception as e: valid = str(e)[:80]
    shutil.rmtree(root, ignore_errors=True)
    ok = not dlg and cells == 2 and still >= 1 and ran and not dlg2 and valid is True and "jetTransient" not in txt
    return ok, "dialog %s · cells %d · preview %d · Run All drew the document %s · save dialog %s · saved valid %s · jetTransient left %s" % (
        bool(dlg), cells, still, ran, bool(dlg2), valid, "jetTransient" in txt)

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv); a = sys.argv[1:]
    nb = json.load(open(src, encoding="utf-8")); rows, fails = [], []
    bad = a1(nb)
    rows.append("A1 file, visible code lines ASCII: %s %s" % ("OK" if not bad else "RED", bad[:4]))
    if bad: fails.append("A1")
    if "--no-vscode" not in a:
        cs = os.environ.get("DIGICHEM_CODE_SERVER") or shutil.which("code-server")
        if not cs:
            rows.append("A2 VS Code: BAD no code-server (DIGICHEM_CODE_SERVER)"); fails.append("A2 not run")
        else:
            n, nonas = a2(src, cs)
            ok = n >= 5 and not nonas
            rows.append("A2 VS Code editor, %d shown lines: %s %s" % (n, "OK" if ok else "RED", nonas[:4]))
            if not ok: fails.append("A2")
    if "--no-lab" not in a:
        ok, d = b1(src)
        rows.append("B1 jetTransient in JupyterLab: %s · %s" % ("OK" if ok else "RED", d))
        if not ok: fails.append("B1")
    print("\n".join(rows))
    print("PY-E38A-P3 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
