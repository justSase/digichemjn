"""E38 P3 (2026-10-27, Python) — DIE ZELLE DER .ipynb ZEIGT DAS MITGELIEFERTE PAKET (statt das Dokument neu zu bauen).
    python3 tests/regress/py_e38_p3.py <notebook.ipynb> [--base <altes.ipynb>] [--runs 3] [--shot bild.png]

Gemessen 27.10. (Dirigent, Vorlage v1.83, JupyterLab 4.6.4): Run All → Deckblatt 6,1–6,4 s; lesen.html 0,6 s. Ziel: Kernel
+ ≤ 1,5 s; Trust-Modell bleibt (vor dem Lauf kein Skript in der Datei).
  Z1  Datei: Zelle 2 trägt `_NBP` (eine Zeile, ASCII), die Ladung `_NBZ` bleibt, ≤ 24 Zeilen; gespeicherte Ausgabe = nur die
      Vorschau (kein <script>, kein application/javascript, kein <style>); Größe .ipynb (INFO, mit --base gegen die alte)
  Z2  Kernel (frisch, ohne DIGICHEM_LAB): EINE Ausgabe; sie BEGINNT mit der Lesefassung, Zeichen für Zeichen die, die der Kernel
      auf dem Weg des Labs zeichnet (DIGICHEM_LAB=1, Seed/Bilder wie der Bau, Zeile „Notebook“) — darin als erstes Kind die
      Daten (data-nbrw-daten, VERTRAG-E38-js), danach nur Schriften und der Rahmen (Notebook-Seiten: eigene Seite für den Leser);
      die Zelle läuft ohne numpy/matplotlib/ipywidgets zu laden; Dauer der Zelle (INFO)
  Z3  pruefe("t1") in einer eigenen Zelle (Kernel): Musterlösung → ✓ + Fenster-Schlüssel digichemjn.<id>.reader.code.t1;
      falsch → ✗
  Z4  echtes JupyterLab (Chromium 1400 × 900, dunkel): Notebook öffnen, Kernel bereit, Run All → Deckblatt mit ▶ sichtbar:
      Median über --runs Läufe ≤ 1,5 s (mit --base dieselbe Messung an der alten Datei, INFO); dazu kalt: öffnen + sofort
      Run All → Deckblatt (INFO: Kernel-Start inklusive)
  Z5  im Lab: neue Zelle mit der Musterlösung + pruefe("t1") → ✓ in ihrer Ausgabe
Gegenprobe v1.84: Z1 rot (kein _NBP), Z2 rot (die Zelle baut das Dokument: viele Ausgaben/Widgets), Z4 rot (≈ 6 s).
Besitzer: Python."""
import sys, os, re, json, time, shutil, tempfile, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "..", "toolkit"))
a = sys.argv[1:]
NB = os.path.abspath(a[0])
BASE = os.path.abspath(a[a.index("--base") + 1]) if "--base" in a else None
RUNS = int(a[a.index("--runs") + 1]) if "--runs" in a else 3
SHOT = a[a.index("--shot") + 1] if "--shot" in a else None
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
os.environ.pop("DIGICHEM_LAB", None)        # gemessen wird das Paket (run.py setzt DIGICHEM_LAB=1 für die Lab-Suiten)
rows, fails = [], []


def row(n, ok, det, info=False):
    rows.append("%-30s %s  %s" % (n, "INFO" if info else ("ok  " if ok else "RED "), det))
    print(rows[-1]); sys.stdout.flush()
    if not ok and not info:
        fails.append(n)


def cell_of(path):
    nb = json.load(open(path, encoding="utf-8"))
    c = next(c for c in nb["cells"] if c["cell_type"] == "code")
    return nb, c, "".join(c["source"])


def kernel(env_extra, lang="en"):
    from jupyter_client.manager import start_new_kernel
    home = tempfile.mkdtemp(prefix="py-e38-p3-")
    env = {k: v for k, v in os.environ.items() if not k.startswith("DIGICHEM")}
    env.update(HOME=home, PYTHONHASHSEED="0", DIGICHEM_LANG=lang, **env_extra)
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=home)

    def run(src, timeout=600):
        mid = kc.execute(src); outs, errs, txt = [], [], []
        t0 = time.time()
        while True:
            m = kc.get_iopub_msg(timeout=timeout)
            if m["parent_header"].get("msg_id") != mid:
                continue
            t, c = m["msg_type"], m["content"]
            if t in ("display_data", "execute_result"):
                outs.append(c["data"])
            elif t == "stream":
                txt.append(c["text"])
            elif t == "error":
                errs.append("%s: %s" % (c["ename"], c["evalue"]))
            elif t == "status" and c["execution_state"] == "idle":
                return outs, errs, "".join(txt), time.time() - t0
    return km, run, home


def z1():
    nb, c, src = cell_of(NB)
    lines = src.rstrip("\n").split("\n")
    nbp = [l for l in lines if l.startswith("_NBP = ")]
    nbz = [l for l in lines if l.startswith("_NBZ = ")]
    asc = all(l.isascii() for l in lines if not l.startswith("_NBZ = "))
    outs = c.get("outputs") or []
    blob = json.dumps(outs)
    trust = not re.search(r"<script|<style", blob, re.I) and "application/javascript" not in blob
    ok = len(nbp) == 1 and len(nbz) == 1 and asc and len(lines) <= 24 and trust and len(outs) == 1
    size = os.path.getsize(NB)
    det = "%d Zeilen · _NBP %d Zeichen · _NBZ %d · ASCII %s · gespeicherte Ausgabe %d, Skript/Style %s · .ipynb %d B" % (
        len(lines), len(nbp[0]) - 9 if nbp else 0, len(nbz[0]) - 9 if nbz else 0, asc, len(outs), not trust, size)
    if BASE:
        det += " (alt %d B)" % os.path.getsize(BASE)
    row("Z1 Datei", ok, det)
    return src


def z2(src):
    km, run, home = kernel({})
    try:
        outs, errs, txt, dt = run(src)
        _, _, mtxt, _ = run("import sys, json; print(json.dumps(sorted(m for m in ('numpy', 'matplotlib', 'ipywidgets') "
                            "if m in sys.modules)))")
    finally:
        km.shutdown_kernel(now=True); shutil.rmtree(home, ignore_errors=True)
    mods = json.loads(mtxt.strip().splitlines()[-1]) if mtxt.strip() else ["?"]
    htmls = [o.get("text/html") or "" for o in outs]
    if errs or len(outs) != 1:
        row("Z2 Kernel: eine Ausgabe", False, "%d Ausgaben, Fehler %s, Module %s, %.2f s" % (len(outs), errs[:2], mods, dt))
        return
    h = htmls[0]
    # das Paket: [Lesefassung des Kernels, darin als erstes Kind die Daten][Schriften][Rahmen] — die Ausgabe BEGINNT mit
    # der Lesefassung; die Daten (VERTRAG-E38-js: .nbreading > script[data-nbrw-daten]) werden für den Vergleich herausgenommen
    marks = [h.find(m) for m in ("<style data-digichemjn-fonts>", "<script data-digichemjn-rahmen>")]
    j = min([m for m in marks if m > 0] or [len(h)])
    head, doc = h[j:], h[:j]
    dm = re.search(r"<script type='application/json' data-nbrw-daten='[^']+'>.*?</script>", doc, re.S)
    daten_in = bool(dm) and doc.startswith("<div class='nbreading'") and doc.find(">") + 1 == dm.start()
    if dm:
        doc = doc[:dm.start()] + doc[dm.end():]
    # Referenz: der Weg des Labs im Kernel (wie der Bau: Seed, alle Bilder, Zeile „Notebook“)
    km, run, home = kernel({"DIGICHEM_LAB": "1", "DIGICHEM_READ_ALL": "1", "DIGICHEM_NBRW_BUDGET": "1e9",
                            "DIGICHEM_READ_PAGE": "ipynb", "MPLBACKEND": "module://matplotlib_inline.backend_inline"})
    try:
        import paket
        run("import random as _r36; _r36.seed(%d); del _r36" % paket.SEED_RUN)
        o2, e2, _, dt2 = run(src)
    finally:
        km.shutdown_kernel(now=True); shutil.rmtree(home, ignore_errors=True)
    ref = [o["text/html"] for o in o2 if str(o.get("text/html") or "").startswith("<div class='nbreading'")]
    same = bool(ref) and ref[0] == doc
    head_ok = h.startswith("<div class='nbreading'") and daten_in and bool(re.fullmatch(
        r"(<style data-digichemjn-fonts>[^<]*</style>)?<script data-digichemjn-rahmen>.*</script>", head, re.S))
    ok = same and head_ok and not mods
    row("Z2 Kernel: Paket = Lab-Lesefassung", ok,
        "1 Ausgabe %d Zeichen in %.2f s (Lab-Weg %d Ausgaben in %.2f s) · Dokument %s · %s · geladen %s" % (
            len(h), dt, len(o2), dt2, "Zeichen für Zeichen gleich" if same else "VERSCHIEDEN",
            "Daten als erstes Kind %s, danach Schriften %s + Rahmen" % (daten_in, "data-digichemjn-fonts" in head)
            if head_ok else "ANDERES %r" % head[:80], mods or "nichts davon"))


def z3(src):
    import paket  # noqa
    sol = "def y_von(a, x):\n    return a * x\n"
    km, run, home = kernel({})
    try:
        run(src)
        o1, e1, _, _ = run(sol + 'pruefe("t1")')
        o2, e2, _, _ = run("def y_von(a, x):\n    return a + x\n" + 'pruefe("t1")')
    finally:
        km.shutdown_kernel(now=True); shutil.rmtree(home, ignore_errors=True)
    t1 = [o.get("text/plain", "") for o in o1]; h1 = "".join(o.get("text/html", "") for o in o1)
    t2 = [o.get("text/plain", "") for o in o2]
    ok = (not e1 and not e2 and t1 and t1[0].startswith("✓") and "reader.code.t1','solved'" in h1
          and t2 and t2[0].startswith("✗"))
    row("Z3 pruefe() im Kernel", ok, "richtig → %r · falsch → %r%s" % (t1[:1], t2[:1], (" · Fehler %s" % (e1 + e2)) if e1 or e2 else ""))


COVER = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); if (!P) return false;
  var doc = document, f = P.querySelector('.jp-OutputArea iframe[data-digichemjn-rahmen]');
  var sel = '.nbrw-cover [data-nbrw-act=play], .nbcover-out .nbcover-play';
  var b = f ? (f.contentDocument && f.contentDocument.querySelector(sel)) : P.querySelector('.jp-OutputArea ' + sel.replace(', ', ', .jp-OutputArea '));
  if (!b) return false;
  var r = b.getBoundingClientRect(), s = b.ownerDocument.defaultView.getComputedStyle(b);
  var fr = f ? f.getBoundingClientRect() : {top: 0};
  return r.width > 2 && r.height > 2 && s.display !== 'none' && s.visibility !== 'hidden' && fr.top + r.bottom > 0;
}"""
IDLE = r"""() => { var i = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator');
  var k = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-KernelStatus, .jp-NotebookPanel:not(.lm-mod-hidden) [data-status]');
  return !!(i && i.getAttribute('data-status') === 'idle'); }"""


def palette_run_all(pg):
    """Run ▸ Run All Cells über das Menü (wie ein Leser); → performance.now() beim Klick."""
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.click(".lm-MenuBar-item:has(.lm-MenuBar-itemLabel:text-is('Run'))")
    it = pg.locator(".lm-Menu-item:has(.lm-Menu-itemLabel:text-is('Run All Cells'))").first
    it.wait_for(state="visible", timeout=8000)
    it.hover()
    t0 = pg.evaluate("() => performance.now()")
    it.click()
    return t0


def lab_measure(b, base, root, path, tag, warm=True, shot=None):
    name = "%s_%s.ipynb" % (tag, int(time.time() * 1000) % 100000)
    shutil.copy(path, os.path.join(root, name))
    ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
    t_open = time.time()
    pg.goto(base + "/lab/tree/" + name + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=90000)
    if pg.query_selector(".jp-Dialog"):
        pg.keyboard.press("Enter"); pg.wait_for_timeout(500)
    k_ms = None
    if warm:
        pg.wait_for_function(IDLE, timeout=90000)
        k_ms = (time.time() - t_open) * 1000
        pg.wait_for_timeout(800)
    t0 = palette_run_all(pg)
    try:
        pg.wait_for_function(COVER, timeout=60000, polling=25)
        ms = pg.evaluate("() => performance.now()") - t0
    except Exception:
        ms = None
    total = (time.time() - t_open) * 1000
    if shot:
        pg.wait_for_timeout(1500); pg.screenshot(path=shot)
    ctx.close()
    try:
        import urllib.request
        for s in json.loads(urllib.request.urlopen(base + "/api/sessions").read()):
            req = urllib.request.Request(base + "/api/sessions/" + s["id"], method="DELETE"); urllib.request.urlopen(req)
    except Exception:
        pass
    return ms, k_ms, total, errs


def z4_z5():
    from playwright.sync_api import sync_playwright
    from lab_keys import ensure_lab
    base, root = ensure_lab("http://127.0.0.1:1")     # ein eigener Server: der von run.py hat DIGICHEM_LAB=1
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        lab_measure(b, base, root, NB, "warmup")              # Lab baut seine Seite einmal (Erweiterungen, Schriften)
        res = [lab_measure(b, base, root, NB, "neu", shot=SHOT if i == RUNS - 1 else None) for i in range(RUNS)]
        ms = [r[0] for r in res]
        good = [m for m in ms if m is not None]
        med = statistics.median(good) if len(good) == len(ms) else None
        row("Z4 Lab Run All → Deckblatt", med is not None and med <= 1500,
            "Median %s ms (Läufe %s) · Kernel bereit nach %s ms · Seitenfehler %d" % (
                "%.0f" % med if med is not None else "—", ["%.0f" % m if m is not None else "—" for m in ms],
                ["%.0f" % r[1] for r in res], sum(len(r[3]) for r in res)))
        cold = lab_measure(b, base, root, NB, "kalt", warm=False)
        row("Z4k kalt: öffnen + Run All", True, "Run All → Deckblatt %s ms (Kernel-Start inklusive), öffnen → Deckblatt %.0f ms"
            % ("%.0f" % cold[0] if cold[0] else "—", cold[2]), info=True)
        if BASE:
            rb = [lab_measure(b, base, root, BASE, "alt") for _ in range(RUNS)]
            mb = [r[0] for r in rb]
            row("Z4b alt: Run All → Deckblatt", True, "Median %s ms (Läufe %s)" % (
                "%.0f" % statistics.median([m for m in mb if m]) if any(mb) else "—", ["%.0f" % m if m else "—" for m in mb]),
                info=True)
        # Z5: eigene Zelle mit pruefe im Lab
        name = "z5_%d.ipynb" % (int(time.time()) % 100000)
        nb = json.load(open(NB, encoding="utf-8"))
        nb["cells"].append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                            "source": ["def y_von(a, x):\n", "    return a * x\n", "\n", "pruefe(\"t1\")\n"]})
        json.dump(nb, open(os.path.join(root, name), "w"), ensure_ascii=False)
        ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark"); pg = ctx.new_page()
        pg.goto(base + "/lab/tree/" + name + "?reset")
        pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=90000)
        if pg.query_selector(".jp-Dialog"):
            pg.keyboard.press("Enter")
        pg.wait_for_function(IDLE, timeout=90000)
        palette_run_all(pg)
        try:
            pg.wait_for_function("""() => { var c = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-CodeCell');
                var l = c[c.length - 1]; return !!(l && /\\u2713|\\u2717|\\u2139/.test(l.querySelector('.jp-OutputArea') ? l.querySelector('.jp-OutputArea').innerText : '')); }""",
                                 timeout=60000)
            t = pg.evaluate("""() => { var c = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-CodeCell');
                return c[c.length - 1].querySelector('.jp-OutputArea').innerText.trim(); }""")
            st = pg.evaluate("() => localStorage.getItem('digichemjn.vorlage.reader.code.t1')")
        except Exception as e:
            t, st = "Fehler %s" % str(e)[:80], None
        ctx.close()
        row("Z5 Lab: pruefe in eigener Zelle", t.startswith("✓") and st == "solved", "%r · Fenster-Schlüssel %r" % (t[:60], st))
        b.close()


def main():
    src = z1()
    z2(src)
    z3(src)
    z4_z5()
    print("PY-E38-P3 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
