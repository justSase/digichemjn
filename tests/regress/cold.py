"""E24.0 — KALTSTART: the file on a stranger's machine, the first time it is opened.

    python3 tests/regress/cold.py complex/Complex_Numbers_Step_by_Step_v<X>.ipynb
        [--scenario bare,hub] [--lite-url URL] [--json out.json] [--shots DIR]

Every gate before E24 ran in OUR environment: numpy, matplotlib, ipywidgets,
jupyterquiz and the widget front end installed, the notebook trusted by the
runner's own Lab. The reader's office PC (06.10., v1.65) had none of that, and
the file did not work there — green BECAUSE of the environment (fifth time).

This script is the stranger. Per scenario a fresh virtual environment, a fresh
HOME / JUPYTER_DATA_DIR / JUPYTER_CONFIG_DIR (so the notebook is NOT trusted),
a fresh Playwright context, a fresh copy of the file:

  offline  as bare, but no package index reachable (pip points at a closed port)
  bare  venv with `jupyterlab` only — no numpy, matplotlib, ipywidgets,
        jupyterquiz, no jupyterlab_widgets front end (the office PC)
  hub   venv with jupyterlab + the four packages + the widget front end, the
        notebook still untrusted (a JupyterHub of the university, E24 Antrag)

and then what a stranger does: open the file → one start line (E24.3) → Run All
(menu, nothing typed into the notebook) → is there a document, do the widgets
draw, is there a traceback? In `bare` the run installs what is missing (E24.1)
and the widget front end cannot be in the page that was loaded before it was
installed, so after the run the script reloads the page and runs again, as the
notebook tells the reader to (E24.2) — that second run must draw the widgets.

Lite: `--lite-url` = a built JupyterLite site without preinstalled packages,
whose files/ hold the notebook under its own name. Without it the Lite row is
NOT RUN (red): this container cannot build one (Pyodide comes from
cdn.jsdelivr.net, blocked here — measured 06.10.).

Each check returns ok / detail. A check that cannot reach its precondition is
red ("BAD …"), never skipped. Exit 0 = COLD OK.
The venv templates are cached (DIGICHEM_COLD_CACHE, default /tmp/digichem-cold);
each run works on a COPY, the template is never touched.
"""
import sys, os, json, time, shutil, socket, subprocess, tempfile, argparse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from lab_keys import CHROME
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("nb")
ap.add_argument("--scenario", default="bare,hub,offline,lite")
ap.add_argument("--lite-url", default=None)
ap.add_argument("--json", default=None)
ap.add_argument("--shots", default=None)
ap.add_argument("--lab-version", default=None, help="default: the runner's own jupyterlab")
ap.add_argument("--timeout", type=int, default=600, help="seconds for one Run All (installs included)")
ap.add_argument("--skip", default="", help="comma list of check ids reported but not counted (e.g. R7 while its JS part is open)")
A = ap.parse_args()

CACHE = os.environ.get("DIGICHEM_COLD_CACHE", "/tmp/digichem-cold")
PKGS = ["numpy", "matplotlib", "ipywidgets", "jupyterquiz"]

def lab_version():
    if A.lab_version: return A.lab_version
    import jupyterlab
    return jupyterlab.__version__

def template(kind):
    """A cached venv: bare = jupyterlab only; hub = + the four packages."""
    d = os.path.join(CACHE, "%s-%s" % (kind, lab_version()))
    if os.path.exists(os.path.join(d, ".ok")): return d
    shutil.rmtree(d, ignore_errors=True)
    subprocess.check_call([sys.executable, "-m", "venv", d])
    pip = [os.path.join(d, "bin", "python"), "-m", "pip", "install", "-q", "--disable-pip-version-check"]
    subprocess.check_call(pip + ["jupyterlab==" + lab_version()])
    if kind == "hub": subprocess.check_call(pip + PKGS)
    open(os.path.join(d, ".ok"), "w").write("ok")
    return d

def start_lab(venv, root, home, offline=False):
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    env = {k: v for k, v in os.environ.items() if not k.startswith(("JUPYTER", "PYTHON", "VIRTUAL_ENV", "DIGICHEM"))}
    env.update(HOME=home, JUPYTER_DATA_DIR=os.path.join(home, "data"),
               JUPYTER_CONFIG_DIR=os.path.join(home, "config"),
               JUPYTER_RUNTIME_DIR=os.path.join(home, "runtime"), IPYTHONDIR=os.path.join(home, "ipython"),
               PATH=os.path.join(venv, "bin") + os.pathsep + env.get("PATH", ""))
    if offline:      # no package index reachable: what an office PC without internet sees
        env.update(PIP_INDEX_URL="http://127.0.0.1:9/simple", PIP_CONFIG_FILE=os.devnull,
                   PIP_FIND_LINKS="", PIP_EXTRA_INDEX_URL="")
    log = open(os.path.join(home, "lab.log"), "w")
    cmd = [os.path.join(venv, "bin", "python"), "-m", "jupyterlab", "--no-browser",
           "--port=%d" % port, "--ServerApp.token=", "--ServerApp.password=",
           "--ServerApp.disable_check_xsrf=True", "--ServerApp.root_dir=" + root, "--allow-root"]
    # The machine's own data dirs (/usr/local/share/jupyter, /usr/share/jupyter)
    # are on every Jupyter's path, whatever HOME says: the runner's global
    # install put the widget front end there, and the first version of this
    # script drew every widget in the "bare" Lab because of it (measured
    # 06.10.: 238 widgets before anything was installed in the venv). They are
    # covered with an empty directory in a mount namespace of the server alone.
    hide = [d for d in ("/usr/local/share/jupyter", "/usr/share/jupyter") if os.path.isdir(d)]
    if hide:
        empty = os.path.join(home, "empty"); os.makedirs(empty, exist_ok=True)
        sh = " && ".join("mount --bind %s %s" % (empty, d) for d in hide)
        cmd = ["unshare", "-m", "sh", "-c", sh + ' && exec "$@"', "sh"] + cmd
    proc = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
    base = "http://127.0.0.1:%d" % port
    for _ in range(240):
        try:
            urllib.request.urlopen(base + "/api/status", timeout=2).read(); return proc, base
        except Exception:
            time.sleep(0.5)
    proc.terminate(); raise RuntimeError("jupyter lab did not come up (%s/lab.log)" % home)

def palette(pg, label):
    if pg.query_selector(".jp-Dialog"):
        pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
    pg.keyboard.type(label)
    pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === l); }", arg=label, timeout=8000)
    pg.keyboard.press("Enter")

# ---- what the stranger sees, measured in the page ----------------------------
COLD_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var vis = function(e){ if (!e) return false; var r = e.getBoundingClientRect(), s = getComputedStyle(e);
                         return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  var inView = function(e){ if (!vis(e)) return false; var r = e.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; };
  var cover = P && P.querySelector('.nbcover');
  var play = P && P.querySelector('.nbcover .nbcover-play');
  var start = P && P.querySelector('.jp-MarkdownCell .nbstart');
  var mdCover = !!(P && P.querySelector('.jp-MarkdownCell .nbcover'));
  var tl = P && P.querySelector('.nbcover-tl');
  var code = P && P.querySelectorAll('.jp-CodeCell');
  var mega = code && code.length ? code[code.length - 1] : null;
  var ed = mega && mega.querySelector('.jp-InputArea-editor, .cm-editor');
  var ph = mega && mega.querySelector('.jp-InputPlaceholder, .jp-Placeholder');
  var lines = 0; if (ed && vis(ed)) lines = ed.querySelectorAll('.cm-line').length;
  return { cover: !!cover, coverInView: inView(cover),
           play: vis(play), playInView: inView(play),
           start: inView(start), startText: start ? start.innerText.replace(/\s+/g, ' ').trim().slice(0, 300) : '',
           startH: start ? Math.round(start.getBoundingClientRect().height) : 0,
           mdCover: mdCover, timeline: vis(tl),
           megaMeta: mega ? null : 'no code cell',
           editorVisible: vis(ed), editorLines: lines, placeholder: vis(ph),
           placeholderText: ph ? ph.innerText.trim().slice(0, 160) : '' };
}"""

AFTER_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var outs = P ? [].slice.call(P.querySelectorAll('.jp-OutputArea-output')) : [];
  var txt = function(e){ return (e.innerText || '').replace(/\s+/g, ' ').trim(); };
  var tb = outs.filter(function(o){ return o.getAttribute('data-mime-type') === 'application/vnd.jupyter.stderr'
                                      && /Traceback|Error/.test(txt(o)); }).map(function(o){ return txt(o).slice(0, 240); });
  var errs = outs.filter(function(o){ return o.classList.contains('jp-OutputArea-executeResult') === false
                                       && /^(\w+Error|ModuleNotFoundError)\b/.test(txt(o)); }).map(function(o){ return txt(o).slice(0, 240); });
  // a widget the page could not draw: JupyterLab falls back to the text/plain repr
  // ("VBox(children=…)") or says so ("Loading widget…", "Error displaying widget")
  var undrawn = outs.filter(function(o){ var t = txt(o);
      return /^(VBox|HBox|Box|Accordion|Tab|Output|HTML|Button|Text|FloatText|FloatSlider|IntSlider|Dropdown|Checkbox|Textarea|Label|GridBox)\(/.test(t)
          || /Loading widget|Error displaying widget|model not found/i.test(t); }).length;
  var widgets = P ? P.querySelectorAll('.jupyter-widgets.widget-container, .jupyter-widgets.widget-inline-hbox, .jupyter-widgets.widget-html, .widget-accordion, .jupyter-widget-Accordion, .lm-Widget.jupyter-widgets').length : 0;
  var hint = P && P.querySelector('.nbwidget-hint');
  var hr = hint && hint.getBoundingClientRect();
  var hv = !!(hr && hr.height > 2 && hr.top < innerHeight && hr.bottom > 0 && getComputedStyle(hint).visibility !== 'hidden');
  var fail = P && P.querySelector('.nbboot-fail'), fr = fail && fail.getBoundingClientRect();
  var fv = !!(fr && fr.height > 2 && fr.top < innerHeight && fr.bottom > 0);
  var ld = document.getElementById('nbload');
  var ldv = !!(ld && !ld.classList.contains('nbload-out') && getComputedStyle(ld).display !== 'none' && +getComputedStyle(ld).opacity > 0.1);
  var redbox = outs.filter(function(o){ return o.getAttribute('data-mime-type') === 'application/vnd.jupyter.stderr'
                                          && o.getBoundingClientRect().height > 2; }).length;
  var boot = P && P.querySelector('.nbboot');
  var cout = P && P.querySelector('.jp-CodeCell .jp-OutputArea .nbcover-out');
  var cplay = cout && cout.querySelector('.nbcover-play');
  // py-E26.1: the reading version, the cell's first output (no widgets drawn: it stays)
  var rd = P && P.querySelector('.nbreading'), rr = rd && rd.getBoundingClientRect();
  var rl = rd && rd.querySelector('.nbread-line'), rlr = rl && rl.getBoundingClientRect();
  return { read: !!(rr && rr.height > 50 && getComputedStyle(rd).display !== 'none'), readLen: rd ? txt(rd).length : 0,
           readLine: !!(rlr && rlr.height > 2 && rlr.top < innerHeight && rlr.bottom > 0) ? txt(rl).slice(0, 300) : '',
           panel: !!document.querySelector('#nbpanel-root .nbmap'), feed: !!(P && P.querySelector('.nbfeed')),
           widgets: widgets, undrawn: undrawn, tracebacks: tb.concat(errs).slice(0, 4),
           hint: hv, hintText: hv ? txt(hint).slice(0, 300) : '',
           fail: fv, failText: fail ? txt(fail).slice(0, 900) : '', loading: ldv, stderrBoxes: redbox,
           boot: boot ? txt(boot).slice(0, 200) : '',
           coverOut: !!cout, coverPlay: !!(cplay && cplay.getBoundingClientRect().width > 2 && getComputedStyle(cplay).display !== 'none'),
           coverTl: !!(cout && cout.querySelector('.nbcover-tl .nbtl-lane')),
           outputs: outs.length };
}"""

def wait_run(pg, timeout, watch=None):
    """Run All, then wait until the kernel is idle again (installs included).
    `watch` samples the boot status line while the cell runs."""
    t0 = time.time(); seen = []
    P0 = "() => { var c = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-CodeCell .jp-InputPrompt'); return c.length ? c[c.length-1].textContent : ''; }"
    before = pg.evaluate(P0)
    # a run that ends inside a second (no internet: pip refuses at once) is
    # never seen as "busy" by sampling — an observer in the page records it
    pg.evaluate("""() => { window.__coldBusy = false;
      var hit = function(){ var e = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator');
        if ((e && e.getAttribute('data-status') === 'busy') || /\\bBusy\\b/.test((document.querySelector('.jp-StatusBar-Widget, #jp-main-statusbar') || {}).textContent || ''))
          window.__coldBusy = true; };
      if (window.__coldObs) window.__coldObs.disconnect();
      window.__coldObs = new MutationObserver(hit);
      window.__coldObs.observe(document.body, {subtree: true, attributes: true, attributeFilter: ['data-status'], childList: true, characterData: true}); }""")
    palette(pg, "Run All Cells")
    pg.wait_for_timeout(1500)
    busy_seen = False
    while time.time() - t0 < timeout:
        st = pg.evaluate("() => { var e = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator'); return e ? e.getAttribute('data-status') : null; }")
        prompt = pg.evaluate("() => { var c = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-CodeCell .jp-InputPrompt'); return c.length ? c[c.length-1].textContent : ''; }")
        if watch:
            b = pg.evaluate("() => { var b = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbboot'); if (!b) return ''; var r = b.getBoundingClientRect(); return (r.height > 2 && r.top < innerHeight && r.bottom > 0) ? (b.innerText || '').replace(/\\s+/g,' ').trim().slice(0,200) : ''; }")
            if b and b not in seen: seen.append(b)
        if (st == "busy" or "*" in (prompt or "") or (prompt and prompt != before and any(ch.isdigit() for ch in prompt))
                or pg.evaluate("() => !!window.__coldBusy")):
            busy_seen = True
        if busy_seen and st == "idle" and "*" not in (prompt or ""): break
        pg.wait_for_timeout(500)
    pg.wait_for_timeout(4000)
    for _ in range(60):
        if not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"): break
        pg.wait_for_timeout(1000)
    return round(time.time() - t0, 1), seen

def shot(pg, name):
    if not A.shots: return
    os.makedirs(A.shots, exist_ok=True)
    pg.screenshot(path=os.path.join(A.shots, name))

def scenario(b, kind):
    rows = []
    def chk(name, ok, detail):
        rows.append((kind, name, bool(ok), detail)); print("%-6s %-44s %s  %s" % (kind, name, "ok " if ok else "RED", detail))
    tmp = tempfile.mkdtemp(prefix="digichem-cold-%s-" % kind)
    venv = os.path.join(tmp, "venv")
    shutil.copytree(template("bare" if kind == "offline" else kind), venv, symlinks=True)
    root, home = os.path.join(tmp, "root"), os.path.join(tmp, "home")
    os.makedirs(root); os.makedirs(home)
    name = os.path.basename(A.nb)
    shutil.copy(A.nb, os.path.join(root, name))
    proc, base = start_lab(venv, root, home, offline=(kind == "offline"))
    try:
        ctx = b.new_context(viewport={"width": 1400, "height": 900})
        pg = ctx.new_page(); perr = []
        pg.on("pageerror", lambda e: perr.append(str(e)[:160]))
        pg.goto(base + "/lab/tree/" + name + "?reset")
        pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
        pg.wait_for_timeout(4000)
        if pg.query_selector(".jp-Dialog"):
            chk("K0 no kernel dialog on opening", False, "dialog: " + pg.inner_text(".jp-Dialog")[:120].replace("\n", " "))
            pg.keyboard.press("Enter"); pg.wait_for_timeout(1500)
        else:
            ks = pg.evaluate("() => { var k = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-KernelName, .jp-NotebookPanel:not(.lm-mod-hidden) [data-jp-item-name=\"kernelName\"]'); return k ? k.textContent.trim() : ''; }")
            chk("K0 no kernel dialog on opening", True, "kernel: %s" % (ks or "?"))
        fed = pg.evaluate("() => { try { var c = JSON.parse(document.getElementById('jupyter-config-data').textContent); return (c.federated_extensions || []).map(function(e){ return e.name; }); } catch (e) { return null; } }")
        wfe = fed is not None and any("jupyter-widgets" in n for n in fed)
        chk("I0 environment is what it claims", fed is not None and (wfe if kind == "hub" else not wfe),
            "widget front end in the page: %s · extensions: %s" % (wfe, ", ".join(fed or [])[:160]))
        c = pg.evaluate(COLD_JS)
        shot(pg, "cold-%s-1-opened.png" % kind)
        # E24.3 (Nutzer 06.10.): the first start is an ordinary notebook — one line
        # (en/de) over the code cell; no preview, no Play, no timeline before the run
        chk("C1 one start line in view (en/de), nothing else", c["start"] and c["startH"] <= 60
            and "Run the cell below" in c["startText"] and "Zelle darunter" in c["startText"] and not c["mdCover"],
            "line=%s h=%dpx %r · cover in the markdown cell=%s" % (c["start"], c["startH"], c["startText"][:110], c["mdCover"]))
        chk("C2 no dead Play, no timeline before the first run", not c["play"] and not c["timeline"],
            "play visible=%s · timeline visible=%s" % (c["play"], c["timeline"]))
        chk("C3 mega-cell source not open", not c["editorVisible"],
            "editor visible=%s (%d lines) · placeholder=%s %r" % (c["editorVisible"], c["editorLines"], c["placeholder"], c["placeholderText"][:80]))
        t, seen = wait_run(pg, A.timeout, watch=True)
        a = pg.evaluate(AFTER_JS)
        shot(pg, "cold-%s-2-after-run.png" % kind)
        if kind == "offline":
            chk("O1 no internet: one plain box in view (en/de)", a["fail"] and "internet" in a["failText"] and "Internet" in a["failText"],
                "box=%s %r" % (a["fail"], a["failText"][:160]))
            chk("O2 no traceback, no red stderr box", not a["tracebacks"] and not a["stderrBoxes"],
                "tb=%s stderr boxes=%d" % (a["tracebacks"][:1], a["stderrBoxes"]))
            chk("O3 loading view not left over the page", not a["loading"], "loading view visible=%s · %.0f s" % (a["loading"], t))
            chk("P0 page errors", not perr, "; ".join(perr)[:200] or "none")
            ctx.close()
            return rows
        # py-E26.1 (11.10.) — behauptete bisher: panel + feed after one run, also
        # without the widget front end (the panel was drawn from the still copy
        # of E22.3). Now the document is EITHER the live one (panel + feed) OR,
        # where no widget can be drawn, the reading version (`.nbreading`, whole text).
        # E28: the template's placeholder text is short (≈ 6 500 characters) — behauptete
        # bisher: > 8 000 (Complex's text); the template is held to > 3 000
        _rmin = 3000 if "Vorlage" in os.path.basename(A.nb) else 8000
        chk("R1 document after one Run All", (a["panel"] and a["feed"]) or (a["read"] and a["readLen"] > _rmin),
            "panel=%s feed=%s · reading version %s (%d chars) · %.0f s" % (a["panel"], a["feed"], a["read"], a["readLen"], t))
        chk("R2 no traceback", not a["tracebacks"], "; ".join(a["tracebacks"])[:300] or "none")
        if kind == "hub":
            chk("R7 the cover is an output of the run (Play, timeline)", a["coverOut"] and a["coverPlay"] and a["coverTl"],
                "cover output=%s play drawn=%s timeline=%s" % (a["coverOut"], a["coverPlay"], a["coverTl"]))
        if kind == "bare":
            chk("R3 install status line seen (en/de)", any(("Install" in s or "install" in s) for s in seen),
                "seen: %s" % (" | ".join(seen)[:300] or "nothing"))
        drawn = a["widgets"] > 0 and a["undrawn"] == 0
        # py-E26.1 — behauptete bisher: the way is in the fixed box `.nbwidget-hint`
        # (it lay over the preview in PyCharm). Now it is the reading version's
        # top line, in the flow and in view.
        chk("R4 widgets drawn, or a hint with the way in view",
            drawn or (bool(a["readLine"]) and "reload" in a["readLine"] and not a["loading"]),
            "widgets=%d undrawn=%d line=%r loading=%s" % (a["widgets"], a["undrawn"], a["readLine"][:160], a["loading"]))
        if kind == "hub":
            chk("R5 widgets drawn (front end present)", drawn, "widgets=%d undrawn=%d" % (a["widgets"], a["undrawn"]))
        else:
            # the way the hint names: reload the page, Run All again
            pg.reload(); pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
            pg.wait_for_timeout(4000)
            if pg.query_selector(".jp-Dialog"): pg.keyboard.press("Enter"); pg.wait_for_timeout(1500)
            t2, _ = wait_run(pg, A.timeout)
            a2 = pg.evaluate(AFTER_JS)
            shot(pg, "cold-%s-3-after-reload.png" % kind)
            d2 = a2["widgets"] > 0 and a2["undrawn"] == 0
            chk("R6 after reload + Run All: widgets drawn", d2 and a2["panel"] and not a2["tracebacks"],
                "widgets=%d undrawn=%d panel=%s hint=%s tb=%s · %.0f s" % (a2["widgets"], a2["undrawn"], a2["panel"], a2["hint"], a2["tracebacks"][:1], t2))
        chk("P0 page errors", not perr, "; ".join(perr)[:200] or "none")
        ctx.close()
    finally:
        proc.terminate()
        try: proc.wait(20)
        except Exception: proc.kill()
    return rows

def main():
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for kind in [k for k in A.scenario.split(",") if k != "lite"]:
            try:
                rows += scenario(b, kind)
            except Exception as e:
                rows.append((kind, "*", False, "BAD %s: %s" % (type(e).__name__, str(e)[:200])))
                print(kind, "BAD", e)
        b.close()
    if "lite" in A.scenario.split(",") and A.lite_url is None:
        rows.append(("lite", "*", False, "NOT RUN: no --lite-url (no Lite site; Pyodide CDN not reachable here)"))
        print("lite   NOT RUN (no --lite-url)")
    skip = [k for k in A.skip.split(",") if k]
    red = [r for r in rows if not r[2] and not any(r[1].startswith(k + " ") for k in skip)]
    if skip: print("not counted: %s" % ", ".join(skip))
    if A.json:
        json.dump([dict(scenario=r[0], check=r[1], ok=r[2], detail=r[3]) for r in rows], open(A.json, "w"), indent=1)
    print("COLD OK" if not red else "COLD RED: %d of %d" % (len(red), len(rows)))
    sys.exit(0 if not red else 1)

if __name__ == "__main__":
    main()
