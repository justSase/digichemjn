"""E38a P4 (2026-10-26, Python) — CELL 1: ONE SHORT SECOND LINE, A HINT PER PROGRAM (en/de).
    python3 tests/regress/py_e38a_p4.py [--nb vorlage|<file.ipynb>] [--shot out.png]

Befund zu v1.79: who opens the file in PyCharm or VS Code needs one step first (PyCharm: "Open in Project";
VS Code: trust the folder + the Jupyter extension). Measured in a real JupyterLab, the file opened, nothing run, 1400 × 900:
  E1  .jp-MarkdownCell .nbstart-env: exactly one, drawn, ONE line (height ≤ 1.7 × its line-height), names PyCharm +
      "Open in Project", VS Code + "Trust" + "Jupyter", en/de ("extension"/"Erweiterung"), ≤ 90 characters
  E2  it is line 2: directly under the run line .nbstart (top ≥ bottom of .nbstart − 1, nothing drawn in between),
      the run line is still line 1 and still says "Run the cell below" + "Zelle darunter"
  E3  the file: cell 1 one Markdown paragraph, no HTML entity, cell 2 a code cell (AUFTRAG: Zelle 1 Textzeile, Zelle 2 Code)
Gegenprobe v1.82: E1/E2 red (no such line). Owner: Python."""
import sys, os, re, json, time, shutil, socket, subprocess, tempfile, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
if not os.path.exists(CHROME):
    from lab_keys import CHROME
JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)') || document;
  var s = P.querySelector('.jp-MarkdownCell .nbstart'), e = P.querySelectorAll('.jp-MarkdownCell .nbstart-env');
  if (!s || e.length !== 1) return {start: !!s, n: e.length};
  var x = e[0], b = x.getBoundingClientRect(), sb = s.getBoundingClientRect(), cs = getComputedStyle(x);
  var lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
  var rects = x.getClientRects();
  return {start: true, n: 1, h: b.height, lh: lh, rects: rects.length, top: b.top, sBottom: sb.bottom, text: x.innerText,
          sText: s.innerText, w: b.width, vis: b.width > 0 && b.height > 0 && cs.visibility !== 'hidden'};
}"""

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv); nb = json.load(open(src, encoding="utf-8")); rows, fails = [], []
    c0, c1 = nb["cells"][0], nb["cells"][1]
    t0 = "".join(c0["source"])
    e3 = c0["cell_type"] == "markdown" and c1["cell_type"] == "code" and "\n\n" not in t0.strip() and not re.search(r"&#?\w+;", t0)
    rows.append("E3 file: cell 1 one paragraph, no entity, cell 2 code: %s" % ("OK" if e3 else "RED"))
    if not e3: fails.append("E3")
    root = tempfile.mkdtemp(prefix="e38a-p4-"); home = os.path.join(root, "home"); os.makedirs(home)
    shutil.copy(src, os.path.join(root, "nb.ipynb")); port = free_port()
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
            pg.goto("http://127.0.0.1:%d/lab/tree/nb.ipynb?reset" % port)
            try: pg.wait_for_selector(".jp-MarkdownCell .nbstart", timeout=60000)
            except Exception: pass
            pg.wait_for_timeout(1500); r = pg.evaluate(JS)
            if "--shot" in sys.argv: pg.screenshot(path=sys.argv[sys.argv.index("--shot") + 1])
            b.close()
    finally:
        srv.terminate(); srv.wait(10); shutil.rmtree(root, ignore_errors=True)
    if not r.get("start") or r.get("n") != 1:
        rows.append("E1 BAD run line %s · .nbstart-env %s" % (r.get("start"), r.get("n"))); fails += ["E1", "E2"]
    else:
        t = r["text"]
        words = all(w in t for w in ("PyCharm", "Open in Project", "VS Code", "Trust", "Jupyter", "extension", "Erweiterung"))
        one = r["vis"] and r["h"] <= 1.7 * r["lh"] and len(t) <= 90
        rows.append("E1 hint line: drawn %s · %.0f px high (line %.1f px) · %d chars · words %s · %s · %r"
                    % (r["vis"], r["h"], r["lh"], len(t), words, "OK" if (one and words) else "RED", t))
        if not (one and words): fails.append("E1")
        e2 = r["top"] >= r["sBottom"] - 1 and r["top"] - r["sBottom"] < r["lh"] and "Run the cell below" in r["sText"] and "Zelle darunter" in r["sText"]
        rows.append("E2 line 2: top %.0f · run line bottom %.0f · %s" % (r["top"], r["sBottom"], "OK" if e2 else "RED"))
        if not e2: fails.append("E2")
    print("\n".join(rows))
    print("PY-E38A-P4 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
