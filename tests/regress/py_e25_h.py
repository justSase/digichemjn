"""E25.h · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_h.py <notebook.ipynb>
  A SAVED PREVIEW SAYS IT IS NOT RUNNING (E25.h, Lite privates Fenster 08.10.:
  the file had been run and saved with its outputs → a preview whose buttons
  are dead). The case "Datei mit gespeicherter Ausgabe, frischer Kernel":
    1  the notebook is run once (nbclient, a real kernel) and saved WITH its
       outputs, shown (collapsed: false — what a front end writes after a
       run; the cold file's "collapsed": true would keep them as a
       placeholder in JupyterLab) — what Lab/PyCharm/Lite keep;
    2  that file is opened in a real JupyterLab, fresh browser, the notebook
       NOT trusted, nothing run: (py-E26.1) the reading version's top line is
       drawn and says to run the cell, no dead Play is visible, one title;
    3  Run All in that page: reported, not judged here, whether our running
       script hides the line (JS E25.h).
  v1.67: no such line. Owner: Python (text); hiding it: JS.
exit 0 = REGRESS-PY-E25-H OK."""
import sys, os, json, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
STALE_JS = """() => { """ + FRONT + """
  if (!P) return null;
  var vis = function(e){ var b = e.getBoundingClientRect(), st = getComputedStyle(e);
    for (var x = e; x; x = x.parentElement) if (getComputedStyle(x).display === 'none') return false;
    return b.width > 0 && b.height > 0 && st.visibility !== 'hidden'; };
  var l = P.querySelector('.nbreading .nbread-line');
  if (l) l.scrollIntoView({block: 'center'});
  var plays = [].filter.call(P.querySelectorAll('.nbcover-play'), vis).length;
  var cards = [].filter.call(P.querySelectorAll('.nbtitle-h, .nbr-nbtitle-h'), vis).length;
  return {line: l && vis(l) ? l.textContent.replace(/\\s+/g, ' ').slice(0, 120) : '', plays: plays, titles: cards,
          widgets: P.querySelectorAll('.acc-root').length}; }"""

def saved_copy(src, dst):
    import nbformat
    from nbclient import NotebookClient
    nb = nbformat.read(src, as_version=4)
    env_keep = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("DIGICHEM_")}
    try:
        NotebookClient(nb, timeout=600, kernel_name="python3",
                       resources={"metadata": {"path": os.path.dirname(dst)}}).execute()
    finally:
        os.environ.update(env_keep)
    # what a front end saves after a run: the outputs it showed are not
    # collapsed (the build ships "collapsed": true for the cold file; JupyterLab
    # keeps a collapsed output area as a placeholder, Lite showed the preview)
    for c in nb.cells:
        if c.cell_type == "code":
            c.metadata["collapsed"] = False
            c.metadata.setdefault("jupyter", {})["outputs_hidden"] = False
    nbformat.write(nb, dst)
    return sum(len(c.get("outputs", [])) for c in nb.cells)

def main():
    src = os.path.abspath([a for a in sys.argv[1:] if not a.startswith("--")][0])
    sys.argv = sys.argv[:1] + ["x"]
    rows, fails = [], []
    import run as R
    from lab_keys import ensure_lab, CHROME, kill_sessions
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    name = "e25h_%d_%s" % (int(time.time() * 1000) % 10 ** 7, os.path.basename(src))
    n = saved_copy(src, os.path.join(root, name))
    rows.append("E25.h saved copy %s: %d outputs" % (name, n))
    if n < 3: fails.append("E25.h BAD the saved copy has %d outputs" % n)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            kill_sessions(base)
            ctx = b.new_context(viewport={"width": 1400, "height": 900})
            ctx.add_init_script(R.INIT_JS % json.dumps({}))
            pg = ctx.new_page(); pg.errs = []
            pg.goto(base + "/lab/tree/" + name + "?reset")
            pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
            pg.wait_for_timeout(4000)
            r = pg.evaluate(STALE_JS); pg.wait_for_timeout(600)
            if os.environ.get("E25H_SHOT"): pg.screenshot(path=os.environ["E25H_SHOT"])
            rows.append("E25.h opened, not run: %s" % r)
            # py-E26.1 (11.10.) — behauptete bisher: the saved COVER carries the line
            # "Not running yet" (.nbcover-stale). The saved preview is now the
            # reading version: its top line says what to run, no dead Play is
            # visible (cover wrapped, only our running script unwraps it), one title.
            if not r: fails.append("E25.h BAD no notebook in front")
            else:
                if not r["line"] or "run the cell" not in r["line"].lower():
                    fails.append("E25.h the saved page has no visible line that says to run the cell: %r" % r["line"])
                if r["plays"]: fails.append("E25.h %d dead Play buttons visible in the saved page" % r["plays"])
                if r["titles"] != 1: fails.append("E25.h %d visible titles in the saved page, want 1" % r["titles"])
            try:
                R.run_front(pg, R.nb_id(src)); pg.wait_for_timeout(2000)
                r2 = pg.evaluate(STALE_JS)
                rows.append("E25.h after Run All (reported only): %s" % r2)
            except Exception as e:
                rows.append("E25.h after Run All: not measured (%s)" % str(e)[:80])
            ctx.close()
        except Exception as e:
            fails.append("E25.h BAD %s" % str(e)[:200])
        finally:
            kill_sessions(base)
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E25-H OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
