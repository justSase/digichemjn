"""E34 · JS — STIL „digi“ ALS STANDARD (Werkstatt JS, 2026-10-19).
    python3 tests/regress/js_e34.py [<notebook.ipynb>] [--only F1,S1] [--shots DIR] [--no-reader]

plan/AUFTRAG.md J1/J2 (Nutzer 19.10.: „Standardstil“). Measured in a real JupyterLab (own server, own HOME), each row
a browser context of its own (= a browser profile), 1400 × 900; the template (`--nb vorlage`) unless a notebook is named.
Rows:
  F1  fresh, Lab light     nothing stored → body.nbskin-digi, body.nbdark (the standard is dark, also in a light Lab),
                           the style button shows digi (◉)
  F2  reload               the same profile, reloaded, run again → still digi + dark (the standard lasts; before E34
                           every reload was „new“ and took the Lab's light)
  F3  Settings → Theme     the Lab switched to dark, reload → dark; then to light, reload → light (E15.3: the front
                           end's switch wins, also while the notebook was closed)
  S1  stored fairy         a reader of a build before E34 (skin fairy, light/dark light, no `themeseen`) → stays
                           fairy and light (nobody is moved)
  S2  stored minimal       skin minimal stored → no nbskin-* class (minimal), not digi
  S3  stored retro         E24.6 (Nutzer 06.10.: retro is not offered) holds → minimal, written back once. AUFTRAG J2
                           names „retro bleibt retro“; that would undo E24.6 — S1 (fairy) is the row for „kept“.
  R1  reading window       (PyCharm/VS Code, env_iframe build; skipped with --no-reader) fresh → data-nbrw-skin=digi;
                           the reader's stored fairy → fairy; light/dark stays „as the host“ (E33 D)
v1.79 (`e5c61dbb`): red F1, F2, R1 (minimal, light); S1, S2, S3, F3 green on both (they guard „nobody is moved“).
Owner: JS. exit 0 = REGRESS-JS-E34 OK."""
import sys, os, re, json, tempfile, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e34 is a stand-alone script")

args = sys.argv[1:]
ONLY = args[args.index("--only") + 1].split(",") if "--only" in args else None
want = lambda k: not ONLY or any(k.startswith(x) for x in ONLY)
shots = args[args.index("--shots") + 1] if "--shots" in args else None
NOREADER = "--no-reader" in args

ROWS, FAILS = [], []
def row(k, ok, det, count=True):
    ROWS.append((k, ok, det)); print("%-4s %s  %s" % (k, "ok " if ok else ("RED" if count else "red (info)"), det)); sys.stdout.flush()
    if not ok and count: FAILS.append(k)

STATE = """() => { var b = document.body, s = [].filter.call(b.classList, function (c) { return c.indexOf('nbskin-') === 0; });
  var btn = document.querySelector('#nbpanel-root .nbbtn.nbskin');
  return {skin: s.join(',') || 'minimal', dark: b.classList.contains('nbdark'), lab: b.getAttribute('data-jp-theme-light'),
          face: btn ? btn.textContent : null, panel: !!document.querySelector('#nbpanel-root .nbmap')}; }"""
INIT = """(function(items){ try { if (sessionStorage.getItem('__e34')) return;
  Object.keys(items).forEach(function(k){ localStorage.setItem(k, items[k]); }); sessionStorage.setItem('__e34', '1'); } catch (e) {} })(%s);"""

def lab_rows(src, b, R, BASE, ROOT, kill_sessions):
    nid = R.nb_id(src)
    def open_run(ctx, theme, name=None):
        kill_sessions(BASE); R.set_lab_theme(BASE, theme)
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        if name is None:
            name = "e34_%d_%s" % (int(time.time() * 1000) % 1000000, os.path.basename(src))
            shutil.copy(src, os.path.join(ROOT, name))
            pg.goto(BASE + "/lab/tree/" + name + "?reset")
        else:
            pg.reload()
        pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
        pg.wait_for_timeout(1500)
        R.run_front(pg, nid); pg.wait_for_timeout(1500)
        return pg, name
    def ctx_with(items):
        c = b.new_context(viewport={"width": 1400, "height": 900})
        if items: c.add_init_script(INIT % json.dumps(items))
        return c
    k = lambda key: "digichemjn.%s.v1.%s" % (key, nid)

    if want("F"):
        c = ctx_with({}); pg, name = open_run(c, "light"); a = pg.evaluate(STATE)
        if shots: pg.screenshot(path=os.path.join(shots, "E34-js-F1-frisch-lab.png"))
        row("F1", bool(a["panel"] and a["skin"] == "nbskin-digi" and a["dark"] and a["lab"] == "true" and a["face"] == "◉"),
            "fresh profile, Lab light: %s" % a)
        pg, _ = open_run(c, "light", name); a2 = pg.evaluate(STATE)
        row("F2", bool(a2["panel"] and a2["skin"] == "nbskin-digi" and a2["dark"]), "reloaded, Lab still light: %s" % a2)
        pg, _ = open_run(c, "dark", name); d = pg.evaluate(STATE)
        pg, _ = open_run(c, "light", name); l = pg.evaluate(STATE)
        row("F3", bool(d["dark"] and d["lab"] == "false" and not l["dark"] and l["lab"] == "true"),
            "Lab → dark, reload: dark=%s · Lab → light, reload: dark=%s (skin %s)" % (d["dark"], l["dark"], l["skin"]))
        c.close()
    for key, skin, want_cls, label in (("S1", "fairy", "nbskin-fairy", "stored fairy (+ light, no themeseen)"),
                                       ("S2", "minimal", "minimal", "stored minimal"),
                                       ("S3", "retro", "minimal", "stored retro (E24.6 → minimal)")):
        if not want(key): continue
        c = ctx_with({k("skin"): skin, k("theme"): "light"}); pg, _ = open_run(c, "light"); a = pg.evaluate(STATE)
        stored = pg.evaluate("(k) => localStorage.getItem(k)", k("skin"))
        if shots and key == "S1": pg.screenshot(path=os.path.join(shots, "E34-js-S1-fairy-bleibt.png"))
        ok = bool(a["panel"] and a["skin"] == want_cls and not a["dark"])
        if key == "S3": ok = ok and stored == "minimal"
        else: ok = ok and stored == skin
        row(key, ok, "%s → %s · stored now %r" % (label, a, stored))
        c.close()

def reader_rows(src, b, nid):
    from env_iframe import run_cell, host_page
    from env_reader import serve
    tmpd = tempfile.mkdtemp(prefix="jse34_"); srv = serve(tmpd)
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    outs, errs, _ = run_cell(src, {})
    open(os.path.join(tmpd, "light.html"), "w", encoding="utf-8").write(host_page(outs, False))
    FR = """() => { var f = [].find.call(document.querySelectorAll('iframe.out'), function (f) { try { return !!f.contentDocument.querySelector('.nbrw'); } catch (e) { return false; } });
      if (!f) return null; var w = f.contentDocument.querySelector('.nbrw');
      return {skin: w.getAttribute('data-nbrw-skin'), theme: w.getAttribute('data-nbrw-theme'), keys: Object.keys(localStorage).filter(function (k) { return /\\.reader\\.skin$/.test(k); })}; }"""
    res = {}
    for tag, pre in (("fresh", None), ("fairy", "fairy")):
        c = b.new_context(viewport={"width": 1400, "height": 900})
        if pre:
            # the reader's key is digichemjn.<id>.reader.skin (20-reader K: the notebook's id, „nb“ without one);
            # stored before the page loads, as a reader's earlier visit would have
            ids = [nid, "nb"]
            c.add_init_script("(function(){ try { %s } catch (e) {} })();" % " ".join(
                "localStorage.setItem('digichemjn.%s.reader.skin', 'fairy');" % i for i in ids))
        pg = c.new_page(); pg.goto(base + "light.html"); pg.wait_for_timeout(3000)
        res[tag] = pg.evaluate(FR)
        if shots and tag == "fresh":
            pg.screenshot(path=os.path.join(shots, "E34-js-R1-lesefenster-frisch.png"))
        c.close()
    srv.shutdown()
    f, g = res["fresh"], res["fairy"]
    row("R1", bool(f and g and f["skin"] == "digi" and g["skin"] == "fairy"),
        "reading window fresh: %s · with stored fairy: %s" % (f, g))

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src)
    from lab_keys import ensure_lab, kill_sessions, CHROME
    from playwright.sync_api import sync_playwright
    sys.argv = [sys.argv[0]]
    import run as R
    BASE, ROOT = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    try:
        if any(want(x) for x in ("F", "S")):
            try: lab_rows(src, b, R, BASE, ROOT, kill_sessions)
            except Exception as e: row("LAB", False, "BAD %s" % str(e).splitlines()[0][:200])
        if want("R") and not NOREADER:
            try: reader_rows(src, b, R.nb_id(src))
            except Exception as e: row("R1", False, "BAD %s" % str(e).splitlines()[0][:200])
    finally:
        b.close(); p.stop()
    print("REGRESS-JS-E34 %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
