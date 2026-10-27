"""Real-JupyterLab print measurement (Playwright, Chromium). 2026-09-27, night shift.

NOT a suite: needs a running `jupyter lab` (token off), like lab_keys.py.
Opens a notebook, runs it, then compares the SCREEN with the PRINT view
(`page.emulate_media(media='print')` — the same stylesheet the browser's
Ctrl+P uses) and writes a JSON row plus two full-page screenshots and a PDF.

    python3 tests/lab_print.py <notebook-in-labroot> <outdir>

What is counted (every number from getBoundingClientRect / getComputedStyle):
  boxes      visible `.nbbox`          — screen default · screen with every
                                          chapter opened · print
  panel      `#nbpanel-root` visible
  furniture  visible JupyterLab cell furniture (prompts, collapsers, toolbars)
  controls   visible control buttons (`.nbbtn`, ipywidgets buttons)
  shell      visible JupyterLab shell parts (top panel, sidebars, tab bar)
  texture    background-image of the document scroller (skins: must be none)
  chapters   `.jupyter-widget-Collapse-contents`: total · visible
  clip       the last visible `.nbbox` bottom vs the printable document height
             — a box below documentElement.scrollHeight is one the printer
             never reaches (overflow:auto scrollers clip to one page)
The PDF is a second witness: pdfinfo page count and pdftotext for the last
chapter's heading.

2026-09-27a (Applikation): the dark document prints light. `page.pdf()` fires
no beforeprint/afterprint in Chromium, so the row also records what the page's
own `beforeprint` handler does when the event is dispatched by hand:
`darkBefore` → `darkInPrint` → `darkAfter` (body.nbdark present?) and the
computed page background in between."""
import os, sys, json, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.sync_api import sync_playwright
from tests.lab_keys import CHROME, kill_sessions

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")

COUNT_JS = r"""() => {
  var vis = el => { var r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'; };
  var nvis = s => [].filter.call(document.querySelectorAll(s), vis).length;
  var ntot = s => document.querySelectorAll(s).length;
  var FURN = '.jp-InputPrompt,.jp-OutputPrompt,.jp-Collapser,.jp-Cell-inputCollapser,.jp-OutputCollapser,'
           + '.jp-cell-toolbar,.jp-NotebookPanel-toolbar,.jp-Notebook-footer,.jp-Notebook-ExecutionIndicator';
  var CTRL = '#nbpanel-root .nbbtn,.nbbtn,.jupyter-button,.widget-button,.nbcover-play,.nbgrip';
  var SHELL = '#jp-top-panel,#jp-menu-panel,.jp-SideBar,#jp-left-stack,#jp-right-stack,#jp-bottom-panel,'
            + '.lm-DockPanel-tabBar,.jp-Toolbar';
  var panel = document.getElementById('nbpanel-root');
  var sc = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer');
  var boxes = [].filter.call(document.querySelectorAll('.nbbox'), vis);
  var lastBottom = boxes.length ? Math.max.apply(null, boxes.map(b => b.getBoundingClientRect().bottom + window.scrollY)) : null;
  var lastLeft = boxes.length ? Math.round(Math.min.apply(null, boxes.map(b => b.getBoundingClientRect().left))) : null;
  var box0 = boxes[0];
  return {
    boxes: boxes.length, boxesTotal: ntot('.nbbox'),
    panel: panel ? vis(panel) : false,
    furniture: nvis(FURN), furnitureTotal: ntot(FURN),
    controls: nvis(CTRL), controlsTotal: ntot(CTRL),
    shell: nvis(SHELL), shellTotal: ntot(SHELL),
    texture: sc ? getComputedStyle(sc).backgroundImage : null,
    scroller: sc ? {overflowY: getComputedStyle(sc).overflowY, position: getComputedStyle(sc).position,
                    height: Math.round(sc.getBoundingClientRect().height), scrollHeight: sc.scrollHeight} : null,
    chaptersTotal: ntot('.jupyter-widget-Collapse-contents'),
    chaptersVisible: nvis('.jupyter-widget-Collapse-contents'),
    chaptersHiddenClass: ntot('.jupyter-widget-Collapse-contents.lm-mod-hidden'),
    docHeight: document.documentElement.scrollHeight,
    bodyHeight: document.body.scrollHeight,
    lastBoxBottom: lastBottom == null ? null : Math.round(lastBottom),
    lastBoxLeft: lastLeft,
    dark: document.body.classList.contains('nbdark'),
    pageBg: sc ? getComputedStyle(sc).backgroundColor : null,
    boxBg: box0 ? getComputedStyle(box0).backgroundColor : null,
    boxInk: box0 ? getComputedStyle(box0).color : null,
    body: document.body.className,
    skin: (document.body.className.match(/nbskin-\w+/) || [null])[0]
  };
}"""

OPEN_ALL_JS = r"""() => {
  // open every collapsed accordion section by clicking its header, outermost
  // first, until nothing is left closed (nested groups need several passes)
  var n = 0;
  for (var pass = 0; pass < 6; pass++) {
    var closed = [].filter.call(document.querySelectorAll('.jupyter-widget-Collapse-contents.lm-mod-hidden'),
                   c => !c.closest('.jupyter-widget-Collapse-contents.lm-mod-hidden:not(:scope)') || true);
    if (!closed.length) break;
    closed.forEach(c => { var hd = c.parentElement.querySelector(':scope > .jupyter-widget-Collapse-header'); if (hd) { hd.click(); n++; } });
  }
  return n;
}"""

def kernel_idle(pg, secs=90):
    for _ in range(secs):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st == "idle": return True
    return False

def open_run(b, nb, width=1400, height=900):
    ctx = b.new_context(viewport={"width": width, "height": height})
    # DIGICHEM_SKIN / DIGICHEM_THEME: the reader's stored choices, so the print
    # view of a skin (texture!) and of the dark document can be measured
    skin, theme = os.environ.get("DIGICHEM_SKIN"), os.environ.get("DIGICHEM_THEME")
    if skin or theme:
        # E25.o: style and light/dark are the notebook's (`<key>.<id>`) — set for both of the series
        ctx.add_init_script("try{%s.forEach(function(i){%s%s});}catch(e){}" % ("['', '.complex-numbers', '.intro-modeling']",
            "localStorage.setItem('digichemjn.skin.v1'+i,%r);" % skin if skin else "",
            "localStorage.setItem('digichemjn.theme.v1'+i,%r);" % theme if theme else ""))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: %s" % str(e)[:200]))
    pg.on("console", lambda m: errs.append("console.error: %s" % m.text[:200]) if m.type == "error" else None)
    pg.goto(BASE + "/lab/tree/" + nb + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=60000)
    pg.wait_for_timeout(1500)
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C"); pg.wait_for_timeout(300)
    pg.keyboard.type("Run All Cells"); pg.wait_for_timeout(300); pg.keyboard.press("Enter")
    pg.wait_for_timeout(3000)
    kernel_idle(pg, 120)
    pg.wait_for_timeout(2000)
    return ctx, pg, errs

def measure(nb, outdir):
    os.makedirs(outdir, exist_ok=True)
    tag = os.path.basename(nb).split("_")[0]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        kill_sessions(BASE)
        t0 = time.time()
        ctx, pg, errs = open_run(b, nb)
        row = {"notebook": nb, "labVersion": pg.evaluate("() => (window.jupyterapp && window.jupyterapp.version) || null"),
               "chromium": b.version, "openRunSeconds": round(time.time() - t0, 1)}
        row["screen"] = pg.evaluate(COUNT_JS)
        # the page's own print hooks: dispatched by hand, because page.pdf()
        # and emulate_media fire neither beforeprint nor afterprint
        pg.evaluate("() => window.dispatchEvent(new Event('beforeprint'))")
        pg.emulate_media(media="print"); pg.wait_for_timeout(1500)
        row["print"] = pg.evaluate(COUNT_JS)
        pg.screenshot(path=os.path.join(outdir, tag + "-print-viewport.png"))
        pdf = os.path.join(outdir, tag + "-print.pdf")
        pg.pdf(path=pdf, format="A4", print_background=True)
        try:
            info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
            row["pdfPages"] = int([l for l in info.splitlines() if l.startswith("Pages:")][0].split()[1])
            txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
            row["pdfChars"] = len(txt)
            heads = pg.evaluate("() => [].map.call(document.querySelectorAll('.jupyter-widget-Collapse-header'), h => h.textContent.trim().replace(/^\\S+\\s+/, ''))")
            row["pdfHeadingsFound"] = sum(1 for h in heads if h and h[:24] in txt)
            row["headings"] = len(heads)
            open(os.path.join(outdir, tag + "-print.txt"), "w").write(txt)
        except Exception as e:
            row["pdfError"] = str(e)[:200]
        pg.emulate_media(media="screen")
        pg.evaluate("() => window.dispatchEvent(new Event('afterprint'))")
        pg.wait_for_timeout(800)
        row["screenBack"] = pg.evaluate(COUNT_JS)
        # open every chapter on screen — the honest comparison for a handout
        # that unfolds everything (measured AFTER print, so print had to open
        # them by itself)
        row["opened"] = pg.evaluate(OPEN_ALL_JS); pg.wait_for_timeout(800)
        row["screenAllOpen"] = pg.evaluate(COUNT_JS)
        # does this browser fire the events itself on window.print()? (a headless
        # one may not open a dialog at all; recorded, not assumed)
        row["nativePrint"] = pg.evaluate("""() => new Promise(function(res){
            var ev = [], dark = [];
            var a = function(){ ev.push('before'); dark.push(document.body.classList.contains('nbdark')); };
            var z = function(){ ev.push('after'); dark.push(document.body.classList.contains('nbdark')); };
            window.addEventListener('beforeprint', a); window.addEventListener('afterprint', z);
            try { window.print(); } catch (e) { ev.push('threw ' + e); }
            setTimeout(function(){ window.removeEventListener('beforeprint', a);
                window.removeEventListener('afterprint', z); res({events: ev, darkAtEvents: dark,
                darkAfter1500ms: document.body.classList.contains('nbdark')}); }, 1500); })""")
        # headless Chromium fires no afterprint here; the real dialog does
        pg.evaluate("() => window.dispatchEvent(new Event('afterprint'))"); pg.wait_for_timeout(300)
        row["nativePrint"]["darkAfterAfterprint"] = pg.evaluate("() => document.body.classList.contains('nbdark')")

        pg.screenshot(path=os.path.join(outdir, tag + "-screen.png"))
        # last, because a full-page screenshot resizes the viewport and the
        # Lumino layout keeps the size until the next resize (measured)
        try:
            pg.emulate_media(media="print"); pg.wait_for_timeout(800)
            pg.screenshot(path=os.path.join(outdir, tag + "-print-full.png"), full_page=True)
        except Exception as e:
            row["fullPageError"] = str(e)[:200]
        row["errors"] = errs
        ctx.close(); b.close()
    json.dump(row, open(os.path.join(outdir, tag + ".json"), "w"), indent=1)
    return row

if __name__ == "__main__":
    r = measure(sys.argv[1], sys.argv[2])
    print(json.dumps(r, indent=1))
