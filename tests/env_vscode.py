"""E32 K2 · Python — VS CODE (code-server) MEASURED (Werkstatt Python, 2026-10-13). NOT a suite.
    DIGICHEM_CODE_SERVER=<…/bin/code-server> python3 tests/env_vscode.py [--nb vorlage|<file.ipynb>] [--shots DIR] [--json out.json]

Starts code-server (auth none, own user-data/extension dirs, workspace trust off) on a scratch folder with
two copies of the notebook: as built (0 outputs) and executed by nbconvert (the outputs a kernel gives —
VS Code shows SAVED outputs the same way it shows outputs of its own run). Playwright opens each like a
reader (Quick Open), and measures inside VS Code's output webview (all outputs of the notebook in ONE
webview iframe, each output in its own container, VS Code's built-in renderers):
  V0 extensions     which notebook extensions are installed (ms-toolsai.jupyter? → widgets drawable)
  V1 Run All        on the built file: what VS Code does (kernel picker text) — no kernel without the
                    Jupyter extension
  V2 layer          executed file: reading versions / windows (.nbrw) / widget views (.jupyter-widgets) /
                    .acc-root / Lab tools (#nbpanel-root) / raw widget reprs in the visible text
  V3 preview        the window on the preview: its height, Play inside the window's first screen?
  V4 Play           a mouse click on Play → data-nbrw-view=doc, panel visible
  V5 wheel          wheel over the window: the window scrolls, the editor does not move (window top ±2 px)
  V6 theme          light and dark VS Code theme × light/dark OS scheme: the window's background
                    against the editor's
  V7 console        errors of the workbench + webview (code-server's own vsda 404 listed apart)
Light/dark VS Code theme by the user settings file. Rows are a report, exit 0 unless a step could not run.
Without network to open-vsx.org / the Marketplace the Jupyter extension cannot be installed — then V0
says so and the widget layer (B) is NOT measured; this is the layer-C view of VS Code (the reading window).
Owner: Python."""
import sys, os, re, json, time, shutil, socket, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lab_keys import CHROME

INSPECT = r"""() => {
  var vis = function(e){ if (!e) return false; var b = e.getBoundingClientRect(), s = getComputedStyle(e);
    return b.width > 0 && b.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity !== 0; };
  var q = function(s){ return [].filter.call(document.querySelectorAll(s), vis).length; };
  var rw = document.querySelector('.nbrw'), win = rw && rw.querySelector('.nbrw-win');
  var body = document.body ? document.body.innerText : '';
  var bg = function(e){ return e ? getComputedStyle(e).backgroundColor : null; };
  return { reading: q('.nbreading'), windows: q('.nbrw'), view: rw && rw.getAttribute('data-nbrw-view'),
    winH: win ? Math.round(win.getBoundingClientRect().height) : null, winTop: rw ? rw.getBoundingClientRect().top : null,
    scroll: win ? Math.round(win.scrollTop) : null, panel: q('.nbrw-panel'),
    widgets: q('.jupyter-widgets'), acc: document.querySelectorAll('.acc-root').length, labTools: q('#nbpanel-root'),
    reprs: (body.match(/Accordion\(children|VBox\(children|<IPython\.core\.display/g) || []).length,
    titleCards: [].filter.call(document.querySelectorAll('[class*="nbtitle-card"]'), vis).length,
    vscodeDark: document.body.classList.contains('vscode-dark'),
    winBg: bg(win || rw), pageBg: getComputedStyle(document.body).backgroundColor,
    edBg: getComputedStyle(document.documentElement).getPropertyValue('--vscode-editor-background').trim() };
}"""

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def wframe(pg):
    for f in pg.frames:
        try:
            if f.evaluate("() => !!document.querySelector('.nbrw, .nbreading')"): return f
        except Exception: pass
    return None

def open_file(pg, url, name):
    pg.goto(url); pg.wait_for_selector(".monaco-workbench", timeout=90000); pg.wait_for_timeout(4000)
    pg.keyboard.press("Control+P"); pg.wait_for_timeout(800); pg.keyboard.type(name); pg.wait_for_timeout(1200)
    pg.keyboard.press("Enter")
    pg.wait_for_selector(".notebook-editor .monaco-list", state="attached", timeout=60000)

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv); a = sys.argv[1:]
    shots = a[a.index("--shots") + 1] if "--shots" in a else None
    jout = a[a.index("--json") + 1] if "--json" in a else None
    cs = os.environ.get("DIGICHEM_CODE_SERVER") or shutil.which("code-server")
    if not cs: print("BAD no code-server (DIGICHEM_CODE_SERVER)"); sys.exit(2)
    if shots: os.makedirs(shots, exist_ok=True)
    root = tempfile.mkdtemp(prefix="envvsc_"); ws = os.path.join(root, "ws"); os.makedirs(ws)
    base = os.path.splitext(os.path.basename(src))[0]
    built, ran = base + ".ipynb", base + "_ausgefuehrt.ipynb"
    shutil.copy(src, os.path.join(ws, built)); shutil.copy(src, os.path.join(ws, ran))
    t = time.time()
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", ran],
                   cwd=ws, check=True, capture_output=True)
    rows, fails = ["notebook %s · nbconvert run %.1f s · %s" % (base, time.time() - t,
                   subprocess.run([cs, "--version"], capture_output=True, text=True).stdout.split("\n")[0])], []
    ud, ext = os.path.join(root, "ud"), os.path.join(root, "ext"); os.makedirs(os.path.join(ud, "User"))
    sfile = os.path.join(ud, "User", "settings.json")
    def settings(theme):
        json.dump({"security.workspace.trust.enabled": False, "workbench.startupEditor": "none", "workbench.colorTheme": theme,
                   "update.mode": "none", "extensions.autoCheckUpdates": False, "telemetry.telemetryLevel": "off",
                   "chat.disableAIFeatures": True}, open(sfile, "w"))
    settings("Default Light Modern")
    exts = subprocess.run([cs, "--extensions-dir", ext, "--user-data-dir", ud, "--list-extensions"], capture_output=True, text=True).stdout.split()
    rows.append("V0 extensions: %s · Jupyter extension %s" % (exts or "none", "yes" if "ms-toolsai.jupyter" in exts else "NO (widgets not drawable here)"))
    port = free_port(); url = "http://127.0.0.1:%d/?folder=%s" % (port, ws)
    srv = subprocess.Popen([cs, "--auth", "none", "--bind-addr", "127.0.0.1:%d" % port, "--user-data-dir", ud, "--extensions-dir", ext,
                            "--disable-telemetry", "--disable-update-check", "--disable-workspace-trust", ws],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from playwright.sync_api import sync_playwright
    try:
        time.sleep(4)
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            # V1 Run All on the built file
            ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
            open_file(pg, url, built); pg.wait_for_timeout(4000)
            btn = pg.query_selector('.notebook-editor a[aria-label^="Run All"], .action-label[aria-label^="Run All"]')
            msg = None
            if btn:
                btn.click(); pg.wait_for_timeout(3000)
                qi = pg.query_selector(".quick-input-widget:not([style*='display: none'])")
                msg = qi.inner_text().replace("\n", " | ")[:200] if qi else None
                if shots: pg.screenshot(path=os.path.join(shots, "E32-K2-vscode-runall.png"))
            rows.append("V1 Run All (built file): button %s · VS Code shows: %s" % ("yes" if btn else "NO", msg))
            ctx.close()
            for theme, scheme, tag in (("Default Light Modern", "light", "hell"), ("Default Dark Modern", "dark", "dunkel"),
                                       ("Default Dark Modern", "light", "dunkel-os-hell")):
                settings(theme); time.sleep(1.5)
                ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme=scheme); pg = ctx.new_page(); logs = []
                pg.on("console", lambda m: logs.append(m.text[:140]) if m.type == "error" else None)
                pg.on("pageerror", lambda e: logs.append("pageerror " + str(e)[:140]))
                t0 = time.time(); open_file(pg, url, ran)
                wf = None
                while time.time() - t0 < 60 and not wf:
                    pg.wait_for_timeout(500); wf = wframe(pg)
                if not wf:
                    fails.append("V2 %s: no reading output in any frame" % tag); ctx.close(); continue
                pg.wait_for_timeout(2500); s = wf.evaluate(INSPECT)
                rows.append("V2 %s layer: reading %d · windows %d · view %s · widget views %d · .acc-root %d · Lab tools %d · raw reprs %d · title cards %d · %.1f s to the window"
                            % (tag, s["reading"], s["windows"], s["view"], s["widgets"], s["acc"], s["labTools"], s["reprs"], s["titleCards"], time.time() - t0))
                # bring the window to the top of the editor (wheel over the gutter, VS Code scrolls)
                for _ in range(80):
                    top = wf.frame_element().bounding_box()["y"] + wf.evaluate("() => document.querySelector('.nbrw').getBoundingClientRect().top")
                    if top < 160: break
                    pg.mouse.move(372, 700); pg.mouse.wheel(0, 60 if top < 400 else 120); pg.wait_for_timeout(200)
                pg.wait_for_timeout(800)
                fb = wf.frame_element().bounding_box()
                r = wf.evaluate("() => { var w = document.querySelector('.nbrw .nbrw-win').getBoundingClientRect(), p = document.querySelector('.nbrw [data-nbrw-act=play]').getBoundingClientRect(); return [w.top, w.bottom, w.left + w.width/2, p.top, p.bottom, p.left + p.width/2]; }")
                inside = r[4] <= r[1] + 1
                rows.append("V3 %s preview: window %d px · Play %s the window's first screen (Play bottom %d, window bottom %d)"
                            % (tag, s["winH"] or -1, "inside" if inside else "BELOW", round(r[4] - r[0]), round(r[1] - r[0])))
                if shots: pg.screenshot(path=os.path.join(shots, "E32-K2-vscode-%s-vorschau.png" % tag))
                if not inside:      # the reader scrolls the window first (wheel over it)
                    pg.mouse.move(fb["x"] + r[2], fb["y"] + r[0] + 150)
                    for _ in range(4): pg.mouse.wheel(0, 200); pg.wait_for_timeout(200)
                    pg.wait_for_timeout(500)
                    r = wf.evaluate("() => { var w = document.querySelector('.nbrw .nbrw-win').getBoundingClientRect(), p = document.querySelector('.nbrw [data-nbrw-act=play]').getBoundingClientRect(); return [w.top, w.bottom, w.left + w.width/2, p.top, p.bottom, p.left + p.width/2]; }")
                fb = wf.frame_element().bounding_box()      # the wheel at the window's end moves the editor (as wanted)
                pg.mouse.click(fb["x"] + r[5], fb["y"] + (r[3] + r[4]) / 2); pg.wait_for_timeout(2000)
                s2 = wf.evaluate(INSPECT)
                rows.append("V4 %s Play (mouse): view %s · panel %d" % (tag, s2["view"], s2["panel"]))
                if s2["view"] != "doc": fails.append("V4 %s: view %s after Play" % (tag, s2["view"]))
                if shots: pg.screenshot(path=os.path.join(shots, "E32-K2-vscode-%s-dokument.png" % tag))
                top0 = fb["y"] + s2["winTop"]; sc0 = s2["scroll"]
                pg.mouse.move(fb["x"] + r[2], fb["y"] + r[0] + 200)
                for _ in range(5): pg.mouse.wheel(0, 300); pg.wait_for_timeout(200)
                pg.wait_for_timeout(700); s3 = wf.evaluate(INSPECT)
                top_mid = wf.frame_element().bounding_box()["y"] + s3["winTop"]
                pg.evaluate("() => 0"); wf.evaluate("() => { var w = document.querySelector('.nbrw .nbrw-win'); w.scrollTop = w.scrollHeight; }")
                pg.wait_for_timeout(400)
                for _ in range(3): pg.mouse.wheel(0, 200); pg.wait_for_timeout(200)
                pg.wait_for_timeout(500)
                end_moved = wf.frame_element().bounding_box()["y"] + wf.evaluate(INSPECT)["winTop"] - top_mid; top1 = top_mid
                rows.append("V5 %s wheel over the window: window scroll %s → %s · editor moved %+d px · at the window's end the wheel moves the editor %+d px"
                            % (tag, sc0, s3["scroll"], round(top1 - top0), round(end_moved)))
                if abs(top1 - top0) > 2: fails.append("V5 %s: the editor moved %+d px while the window could scroll" % (tag, round(top1 - top0)))
                rows.append("V6 %s theme: VS Code dark %s · OS %s · window bg %s · editor bg %s" % (tag, s3["vscodeDark"], scheme, s3["winBg"], s3["edBg"]))
                own = [l for l in logs if "vsda" not in l and "Failed to load resource" not in l]
                rows.append("V7 %s console errors: %d (%d of code-server's own 404 vsda) %s" % (tag, len(logs), len(logs) - len(own), own[:3]))
                ctx.close()
            b.close()
    finally:
        srv.terminate()
        try: srv.wait(10)
        except Exception: srv.kill()
        shutil.rmtree(root, ignore_errors=True)
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("ENV-VSCODE DONE" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
