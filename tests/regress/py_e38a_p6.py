"""E38a P6 (2026-10-26, Python) — THE ROLE "administrator" IS GONE (Python part; JS: J3).
    python3 tests/regress/py_e38a_p6.py [--nb vorlage|<file.ipynb>]

Nutzer 14.10.: series and total statistics are for everyone — no role. Python wrote, in the ⚙/👤 drawer's
"Carry your progress" cell, a row "You are [reading this notebook | teaching the course]" and the line "Teaching
adds the series list behind 📚" (de: "Sie … leiten den Kurs", "Kursleitung …"); the page script hid them (E17.2).
  R1  the code the cell runs (shortcell expand): no `nbrolerow`, no "teaching the course"/"Teaching adds", no
      "leiten den Kurs"/"Kursleitung" — en and de table (toolkit/de.txt) alike
  R2  JupyterLab, Run All: in the page 0 × .nbrolerow, the drawer's code cell (.nbdrawer .pg-code) still there with its
      slot (nbctl-code), and Python's line ("Teaching adds" / "Kursleitung") nowhere in the DOM (hidden ones count too);
      the role's options in the ⚙ settings select are the page script's (JS J3), not counted here
Gegenprobe v1.82: R1/R2 red (row present, hidden by the script). Owner: Python."""
import sys, os, re, json, time, shutil, socket, subprocess, tempfile, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
if not os.path.exists(CHROME):
    from lab_keys import CHROME
WORDS = ("nbrolerow", "teaching the course", "Teaching adds", "leiten den Kurs", "Kursleitung")

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def main():
    import nbpick, megasrc
    src = nbpick.from_argv(sys.argv); nb = json.load(open(src, encoding="utf-8")); rows, fails = [], []
    code = megasrc.expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
    hit = [w for w in WORDS if w in code]
    rows.append("R1 cell code: %s %s" % ("OK" if not hit else "RED", hit))
    if hit: fails.append("R1")
    root = tempfile.mkdtemp(prefix="e38a-p6-"); home = os.path.join(root, "home"); os.makedirs(home)
    shutil.copy(src, os.path.join(root, "nb.ipynb")); port = free_port()
    srv = subprocess.Popen([sys.executable, "-m", "jupyter", "lab", "--no-browser", "--port", str(port), "--allow-root",
                            "--IdentityProvider.token=", "--ServerApp.password=", "--notebook-dir", root], cwd=root,
                           env=dict(os.environ, HOME=home, JUPYTER_CONFIG_DIR=os.path.join(home, ".jupyter")),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from playwright.sync_api import sync_playwright
    r = None
    try:
        for _ in range(90):
            try: urllib.request.urlopen("http://127.0.0.1:%d/api" % port, timeout=2); break
            except Exception: time.sleep(1)
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            pg = b.new_page(viewport={"width": 1400, "height": 900})
            pg.goto("http://127.0.0.1:%d/lab/tree/nb.ipynb?reset" % port); pg.wait_for_timeout(8000)
            pg.click(".lm-MenuBar-itemLabel:text-is('Run')", timeout=8000); pg.wait_for_timeout(500)
            pg.click(".lm-Menu-itemLabel:text-is('Run All Cells')", timeout=8000)
            t0 = time.time()
            while time.time() - t0 < 150 and not pg.query_selector(".nbdrawer .pg-code"): pg.wait_for_timeout(1000)
            pg.wait_for_timeout(3000)
            r = pg.evaluate("""(W) => { var h = document.body.innerHTML;
              return {rows: document.querySelectorAll('.nbrolerow').length, code: document.querySelectorAll('.nbdrawer .pg-code').length,
                      slot: document.querySelectorAll('.nbdrawer [data-slot=nbctl-code]').length,
                      words: W.filter(w => h.indexOf(w) >= 0)}; }""", ["Teaching adds", "Kursleitung"])
            b.close()
    finally:
        srv.terminate(); srv.wait(10); shutil.rmtree(root, ignore_errors=True)
    ok = bool(r) and r["rows"] == 0 and r["code"] >= 1 and r["slot"] >= 1 and not r["words"]
    rows.append("R2 JupyterLab after Run All: %s %s" % ("OK" if ok else ("RED" if r and r["code"] else "BAD (no drawer)"), r))
    if not ok: fails.append("R2")
    print("\n".join(rows))
    print("PY-E38A-P6 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
