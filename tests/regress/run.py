"""E21.0 — test_regress: what the reader has already accepted must keep working.
(2026-10-02, Hauptwerkstatt; Kategorie Applikation — Prüfwerkzeug)

    python3 tests/regress/run.py [<nb.ipynb> …] [--nb vorlage|complex|modeling]   (E28: default the template)
            [--skins minimal,cyber] [--themes light,dark] [--storage fresh,old]
            [--only <text>] [--lite-url URL] [--json out.json] [--quick]

Every combination (notebook × skin × light/dark × fresh/old browser storage)
gets its OWN browser context, a fresh copy of the notebook in a real
JupyterLab (own server, own HOME, so ~/.digichemjn starts empty), Run All,
and then every test of every test module (below), hw_ first, then by name.

  fresh  empty localStorage
  pair   empty storage, but the OTHER notebook (the next one on the command
         line) is opened and run first in the same JupyterLab window; the one
         under test is opened second, stands in front, and is tested there
         (E16.10/E21.6: one notebook must not change another)
  old    fixtures/storage_old.json preloaded BEFORE the page loads — keys as a
         browser left them that used the notebooks before the per-notebook keys
         (E15.7, E16.10): shared zoom/readline/orient, a kept own cell from an
         older build, a stored mode. The reader tests with a used browser.

Every tests/regress/<werkstatt>_e<n>.py that defines TESTS is a test module
(hw_e21.py Hauptwerkstatt, js_e21.py, css_e21.py, py_e21.py …; a module
without TESTS is skipped with a note). TESTS = [(name, fn), …]; fn(pg, ctx) returns
(ok: bool, detail: str). ctx: nb, id, skin, theme, storage, env, errs.
A test that cannot reach its precondition returns False ("BAD …") — never
True: a skipped check is how a suite turns green because of the error.
Every test must be run once against the version the reader saw failing
(v1.60/v1.61) and be RED there where the reader saw the fault.

Exit 0 = every row green. THE GATE (E21): the Hauptwerkstatt runs this after
every merge and before every write-back of the bundle; one red row = no
write-back, the patch goes back to its workshop. Each workshop runs it before
delivering.

JupyterLite: --lite-url points at a built Lite site whose files/ hold the
notebooks under their own names (the runner cannot build Lite: Pyodide comes
from a CDN). Without it the Lite rows are reported as NOT RUN (red)."""
import sys, os, json, glob, shutil, time, importlib.util, itertools, argparse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))           # tests/ (lab_keys)
from lab_keys import ensure_lab, kill_sessions, CHROME, cover_play
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("nbs", nargs="*")
# E28 (2026-10-12, Python) — "nur die Vorlage": without notebooks on the command line the
# runner tests the template (newest vorlage/Vorlage_v*.ipynb); Complex on request:
# --nb complex (or a comma list: --nb vorlage,complex — the second is the pair partner)
ap.add_argument("--nb", default="vorlage", help="vorlage | complex | modeling | comma list, when no notebook is given")
ap.add_argument("--skins", default="minimal,cyber")
ap.add_argument("--themes", default="light,dark")
ap.add_argument("--storage", default="fresh,old,pair")
ap.add_argument("--env", default="lab", help="lab | lite | lab,lite")
ap.add_argument("--lite-url", default=None)
ap.add_argument("--only", default=None, help="run only tests whose name contains this")
ap.add_argument("--json", default=None)
ap.add_argument("--quick", action="store_true", help="minimal · light · fresh only")
ap.add_argument("--scripts", default="all", help="all | none | comma list: stand-alone lab_*.py from scripts.txt")
ap.add_argument("--width", type=int, default=1400)
ap.add_argument("--height", type=int, default=900)
# 2026-10-07 (E24 Stufe 2, Hauptwerkstatt) — the notebooks UNDER TEST (default: all on the
# command line); the others only serve as the partner of a "pair" row. "Nur Complex" with a
# Modeling build that has not taken over E24.3 yet (NACHZIEHEN): run.py C M --under Complex
ap.add_argument("--under", default=None, help="comma list of file-name parts: rows and scripts only for these notebooks")
A = ap.parse_args(sys.argv[1:] if __name__ == "__main__" else ["x"])
# E38 P3 (2026-10-27, Python) — DIE ZELLE DER VORLAGE ZEIGT DAS PAKET (toolkit/paketzelle.py); das Lab-Dokument (Rail,
# Panel, Widgets) baut der Kernel nur mit DIGICHEM_LAB=1. Die Matrix und die Skripte aus scripts.txt messen das
# Lab-Dokument (behaupteten bisher: jeder Lauf baut es) — sie bekommen DIGICHEM_LAB=1 (Server, Kernel, Skripte erben
# es), außer es ist ausdrücklich gesetzt (DIGICHEM_LAB=0: alles gegen das Paket). Das Paket misst py_e38_p3 (setzt
# es selbst zurück) und, über lesen.html, jedes E36/E38-Skript des Lesers.
if __name__ == "__main__":
    os.environ.setdefault("DIGICHEM_LAB", "1")
if not A.nbs:
    import nbpick
    A.nbs = [nbpick.resolve(n.strip()) for n in A.nb.split(",") if n.strip()]
if A.quick:
    A.skins, A.themes, A.storage = "minimal", "light", "fresh"
    if "--scripts" not in sys.argv: A.scripts = "none"

def _under(src):
    return not A.under or any(u and u in os.path.basename(src) for u in A.under.split(","))

def load_tests():
    out = []
    order = lambda f: (not os.path.basename(f).startswith("hw_"), os.path.basename(f))
    for f in sorted(glob.glob(os.path.join(HERE, "*.py")), key=order):
        if os.path.basename(f) in ("run.py",) or os.path.basename(f).startswith("_"): continue
        if "TESTS" not in open(f, encoding="utf-8").read():      # a stand-alone script: never import-run it
            print("(skipped %s: no TESTS)" % os.path.basename(f)); continue
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        if not hasattr(m, "TESTS"):
            print("(skipped %s: no TESTS)" % os.path.basename(f)); continue
        for name, fn in m.TESTS:
            if A.only and A.only not in name: continue
            out.append(("%s:%s" % (os.path.basename(f)[:-3], name), fn))
    return out

def nb_id(path):
    """The notebook id the toolkit uses (set_notebook in the build's setup chapter).
    E28.1 (2026-10-12): first the notebook's metadata (digichemjn.id, since E26.3) —
    the template ("vorlage") was "unnamed" here, so every Lab script waited 180 s
    for a panel id that could never match (lab_same on the Vorlage: timeout)."""
    src = open(path, encoding="utf-8").read()
    try:
        i = json.loads(src).get("metadata", {}).get("digichemjn", {}).get("id")
        if i:
            return i
    except ValueError:
        pass
    for i in ("complex-numbers", "intro-modeling", "vorlage"):
        if '\\"%s\\"' % i in src or '"%s"' % i in src: return i
    return "unnamed"

LAB_THEME = {"light": "JupyterLab Light", "dark": "JupyterLab Dark"}
def set_lab_theme(base, theme):
    """JupyterLab's own theme (server setting). Since E15.3 the Lab's state IS the
    reader's choice, so dark is made the way a reader makes it: in the Lab."""
    url = base + "/lab/api/settings/@jupyterlab/apputils-extension:themes"
    body = json.dumps({"raw": json.dumps({"theme": LAB_THEME[theme]})}).encode()
    req = urllib.request.Request(url, data=body, method="PUT", headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10).read()

def storage_items(kind, nid):
    if kind in ("fresh", "pair"): return {}
    fx = json.load(open(os.path.join(HERE, "fixtures", "storage_old.json"), encoding="utf-8"))
    return {k.replace("{id}", nid): (v if isinstance(v, str) else json.dumps(v)).replace("{id}", nid)
            for k, v in fx["items"].items()}

INIT_JS = """(function(items){
  try { if (sessionStorage.getItem('__nbregInit')) return;
        Object.keys(items).forEach(function(k){ localStorage.setItem(k, items[k]); });
        sessionStorage.setItem('__nbregInit', '1'); } catch (e) {}
})(%s);"""

def palette(pg, label):
    """A JupyterLab command by its palette label. Never types into the notebook."""
    if pg.query_selector(".jp-Dialog"):
        pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C")
    try:
        pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
    except Exception:
        pg.keyboard.press("Escape"); return False
    pg.keyboard.type(label)
    try:
        pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === l); }", arg=label, timeout=8000)
    except Exception:
        pg.keyboard.press("Escape"); return False
    pg.keyboard.press("Enter"); return True

# the notebook in front has run when the page names IT (nbId of the visible panel,
# read through __nbZKey; .nbfeed[data-nbid] is a run id, not the notebook id)
READY_JS = """(id) => { var k = ''; try { k = window.__nbZKey ? window.__nbZKey() : ''; } catch (e) {}
  return !!(document.querySelector('#nbpanel-root .nbmap') && k.slice(-(id.length + 1)) === '.' + id); }"""
def run_front(pg, nid, lite=False):
    """Run All in the notebook in front and wait until IT (not another) has its panel."""
    t0 = time.time()
    for attempt in range(3):
        palette(pg, "Run All Cells")
        try:
            pg.wait_for_function(READY_JS, arg=nid, timeout=180000 if lite else 40000); break
        except Exception:
            if attempt == 2: raise
    for _ in range(120):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator, .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st == "idle": break
    pg.wait_for_timeout(2500)
    for _ in range(60):                 # wait out a rebuild a stored mode asks for
        busy = pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')")
        if not busy: break
        pg.wait_for_timeout(1000)
    cover_play(pg)                      # E24.3: after the run the cover, Play → the document
    return round(time.time() - t0, 1)

_N = itertools.count()
def open_and_run(b, base, root, src, combo):
    nid = nb_id(src)                    # the notebook opened FIRST (in pair: the other one)
    items = storage_items(combo["storage"], nid)
    items["digichemjn.skin.v1"] = combo["skin"]
    items["digichemjn.theme.v1"] = combo["theme"]
    # E25.o (js, 08.10.): style and light/dark are the NOTEBOOK's now
    # (`<key>.<id>`, the shared key is not read) — the row's style for every
    # notebook the row opens
    for _id in {nid, combo.get("partner") or nid}:
        items["digichemjn.skin.v1." + _id] = combo["skin"]
        items["digichemjn.theme.v1." + _id] = combo["theme"]
    ctx = b.new_context(viewport={"width": A.width, "height": A.height})
    ctx.add_init_script(INIT_JS % json.dumps(items))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: %s" % str(e)[:200]))
    if combo["env"] == "lab":
        kill_sessions(base)
        kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
        shutil.rmtree(os.path.join(kh, ".digichemjn"), ignore_errors=True)
        set_lab_theme(base, combo["theme"])
        name = "reg_%03d_%s" % (next(_N), os.path.basename(src))
        shutil.copy(src, os.path.join(root, name))
        pg.goto(base + "/lab/tree/" + name + "?reset")
    else:
        pg.goto(A.lite_url.rstrip("/") + "/lab/index.html?path=" + os.path.basename(src))
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(1500)
    t = run_front(pg, nid, combo["env"] == "lite")
    if combo.get("partner"):
        # the one under test second, in the same window: Open from Path, run, in front
        pname = "reg_%03d_%s" % (next(_N), os.path.basename(combo["partner_src"]))
        shutil.copy(combo["partner_src"], os.path.join(root, pname))
        palette(pg, "Open from Path…")
        pg.wait_for_selector(".jp-Dialog input", timeout=10000)
        pg.fill(".jp-Dialog input", pname); pg.keyboard.press("Enter")
        pg.wait_for_function("(n) => { var t = document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current'); return !!(t && t.textContent.indexOf(n) >= 0); }", arg=pname, timeout=30000)
        pg.wait_for_timeout(2000)
        t += run_front(pg, combo["partner"], combo["env"] == "lite")
    return ctx, pg, errs, t

def main():
    tests = load_tests()
    envs = A.env.split(",")
    base = root = None
    if "lab" in envs:
        base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    rows, red = [], 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for src, env, skin, theme, sto in itertools.product(A.nbs, envs, A.skins.split(","),
                                                            A.themes.split(","), A.storage.split(",")):
            if not _under(src): continue
            combo = dict(nb=os.path.basename(src), id=nb_id(src), env=env, skin=skin, theme=theme, storage=sto)
            if sto == "pair":
                others = [o for o in A.nbs if o != src]
                if not others:
                    rows.append(("%s · pair" % combo["nb"][:22], "*", False, "NOT RUN: pair needs a second notebook")); red += 1; continue
                # open the OTHER first, the one under test second (in front)
                combo.update(partner=combo["id"], partner_src=src, storage="pair")
                first = others[0]
            else:
                first = src
            tag = "%s · %s · %s %s · %s" % (combo["nb"][:22], env, skin, theme, sto)
            if env == "lite" and not A.lite_url:
                rows.append((tag, "*", False, "NOT RUN: no --lite-url (Lite site not built)")); red += 1
                print("%-60s NOT RUN (no Lite site)" % tag); continue
            try:
                ctx, pg, errs, t = open_and_run(b, base, root, first, combo)
            except Exception as e:
                rows.append((tag, "open+run", False, "BAD %s" % str(e)[:160])); red += 1
                print("%-60s BAD open+run: %s" % (tag, str(e)[:120])); continue
            combo["errs"] = errs
            print("%-60s run %.1f s" % (tag, t)); sys.stdout.flush()
            for name, fn in tests:
                try:
                    ok, det = fn(pg, combo)
                except Exception as e:
                    ok, det = False, "BAD exception %s" % str(e)[:160]
                rows.append((tag, name, bool(ok), det)); red += 0 if ok else 1
                print("   %-34s %s  %s" % (name, "ok " if ok else "RED", det[:150])); sys.stdout.flush()
            pe = [e for e in errs if e.startswith("pageerror")]
            rows.append((tag, "pageerrors", not pe, "%d %s" % (len(pe), pe[:2] if pe else ""))); red += 1 if pe else 0
            print("   %-34s %s  %d" % ("pageerrors", "ok " if not pe else "RED", len(pe)))
            ctx.close()
        b.close()
    # stage 2: the workshops' stand-alone measuring scripts (scripts.txt), on the same server
    import subprocess
    want = None if A.scripts == "all" else ([] if A.scripts == "none" else A.scripts.split(","))
    for line in open(os.path.join(HERE, "scripts.txt"), encoding="utf-8"):
        line = line.split("#")[0].split()
        if not line or (want is not None and line[0] not in want): continue
        script, tmo, which = line[0], int(line[1]) if len(line) > 1 else 600, line[2] if len(line) > 2 else "both"
        targs = line[3:] or ["{nb}"]
        for src in A.nbs:
            if not _under(src): continue
            kind = "modeling" if "Modeling" in os.path.basename(src) else "complex"
            if which not in ("both", kind): continue
            tag = "%s · script" % os.path.basename(src)[:22]
            t0 = time.time()
            try:
                out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "regress_%s_%s.json" % (script[:-3], kind))
                args = [a.replace("{nb}", src).replace("{out}", out) for a in targs]
                r = subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), script)] + args,
                                   capture_output=True, text=True, timeout=tmo, env=dict(os.environ))
                ok = r.returncode == 0
                last = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip()][-1:] or [""]
                det = "exit %d in %.0f s · %s" % (r.returncode, time.time() - t0, last[0][:120])
            except subprocess.TimeoutExpired:
                ok, det = False, "TIMEOUT after %d s (hangs)" % tmo
            rows.append((tag, script, ok, det)); red += 0 if ok else 1
            print("%-60s %-18s %s  %s" % (tag, script, "ok " if ok else "RED", det)); sys.stdout.flush()
    print("\n%d rows, %d red" % (len(rows), red))
    print("REGRESS OK" if not red else "REGRESS RED")
    if A.json:
        json.dump([dict(combo=r[0], test=r[1], ok=r[2], detail=r[3]) for r in rows], open(A.json, "w"), ensure_ascii=False, indent=1)
    sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
