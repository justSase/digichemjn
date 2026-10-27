"""Paket 14 — THE COVER FILLS THE NOTEBOOK, in a real JupyterLab
(2026-09-30, E10 Teil 2; rewritten 2026-10-06 for E24.3, JS).

    python3 tests/lab_cover.py <notebook> [out.png]

E24.3 (Nutzer 06.10.): the first start is an ordinary notebook — one start line
and the code cell; the cover is the LAST OUTPUT of the mega-cell
(`.nbtitle.nbcover-out`, py-E24.3), up over the notebook after the run until
Play (js-E24.3). Behauptete bisher: a fresh copy, NOT run, shows the cover in
its markdown cell, filling the window, Play in view — there is no such cover
any more (red by design since py-E24.3). Now a fresh copy is opened and run
(Run All from the palette, what the stranger does), at 1400 × 900 and
1920 × 1080, JupyterLab light and dark:

  0  before the run: no cover, no Play (nothing of ours has run)
  1  after the run the cover (`.nbcover-out`) covers the notebook area
     (getBoundingClientRect = `.jp-Notebook` ±1 px), the timeline panel is
     not shown
  2  0 visible document or code: a grid of elementFromPoint probes (every
     12 px over the notebook area) hits only the cover — no `.jp-InputArea`,
     no prompt, no output of the mega-cell outside the cover
  3  Play (`.nbcover-play`) is reachable: brought into view inside the cover
     it lies inside the notebook view (how much of it the status bar cuts off
     is reported, not judged); content, language and login are on the cover
  4  Play shows the document: cover gone, the timeline panel there, no
     second run (the run id of the feed unchanged)
  5  no page errors

exit 0 = COVER OK."""
import sys, os, json, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
LAB = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab")
BASE, LAB = ensure_lab(BASE)
SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else None

PROBE_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var nb = P && P.querySelector('.jp-Notebook');
  var cov = P && P.querySelector('.nbcover-out');
  var play = cov && cov.querySelector('.nbcover-play');
  var W = innerWidth, H = innerHeight;
  var area = nb ? nb.getBoundingClientRect() : {left: 0, top: 0, right: W, bottom: H, width: W, height: H};
  var hits = new Set(), doc = 0, n = 0;
  for (var y = Math.max(0, area.top) + 2; y < Math.min(H, area.bottom); y += 12)
    for (var x = Math.max(0, area.left) + 2; x < Math.min(W, area.right); x += 12) {
      var e = document.elementFromPoint(x, y); n++;
      if (!e || (cov && cov.contains(e))) continue;
      var cc = e.closest('.jp-CodeCell');
      if (cc && (e.closest('.jp-InputArea') || e.closest('.jp-OutputArea') || e.closest('.jp-InputPrompt'))) {
        doc++; hits.add((e.className || e.tagName).toString().slice(0, 40));
      }
    }
  var sc = nb ? (nb.closest('.jp-WindowedPanel-outer') || nb.querySelector('.jp-WindowedPanel-outer') || nb) : null;
  var scb = sc ? Math.round(Math.min(H, sc.getBoundingClientRect().bottom)) : H;
  var cr = cov ? cov.getBoundingClientRect() : null, pr = play ? play.getBoundingClientRect() : null;
  var host = document.getElementById('nbpanel-root'), f = P && P.querySelector('.nbfeed[data-nbid]');
  return {W: W, H: H, cover: !!(cr && cr.width > 2 && getComputedStyle(cov).display !== 'none'),
          coverBox: cr ? [cr.left, cr.top, cr.width, cr.height].map(Math.round) : null,
          area: [area.left, area.top, area.width, area.height].map(Math.round),
          play: pr && pr.width > 2 ? [Math.round(pr.left), Math.round(pr.top), Math.round(pr.right), Math.round(pr.bottom)] : null,
          viewBottom: scb, probes: n, docHits: doc, lines: Array.from(hits),
          rail: !!(host && getComputedStyle(host).display !== 'none' && host.querySelector('.nbmap')),
          forms: !!(cov && cov.querySelector('.nbmode .nbmode-opt') && cov.querySelector('.nblang .nblang-opt') && cov.querySelector('.nbacct')),
          run: f ? f.getAttribute('data-nbid') : null,
          theme: document.body.getAttribute('data-jp-theme-light')};
}"""

def run_all(pg):
    if pg.query_selector(".jp-Dialog"):
        pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
    pg.fill(".lm-CommandPalette-input", "Run All Cells", timeout=5000)     # filled, not typed (lab_keys.open_nb)
    pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === 'Run All Cells'); }", timeout=8000)
    pg.keyboard.press("Enter")
    pg.wait_for_selector("#nbpanel-root .nbmap", state="attached", timeout=120000)
    for _ in range(90):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st == "idle": break
    for _ in range(60):
        if not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"): break
        pg.wait_for_timeout(1000)
    pg.wait_for_timeout(2500)

fails, rows = [], []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    SIZES = [tuple(int(x) for x in z.split("x")) for z in os.environ.get("COVER_SIZES", "1400x900,1920x1080").split(",")]
    for (w, h) in SIZES:
        for theme in ("JupyterLab Light", "JupyterLab Dark"):
            kill_sessions(BASE)
            name = "cover_%d_%s_%d_%s" % (w, theme.split()[-1].lower(), os.getpid() % 1000, os.path.basename(SRC))
            shutil.copy(SRC, os.path.join(LAB, name))
            # the theme is a user setting of the server: set it before the page loads
            import urllib.request
            req = urllib.request.Request(BASE + "/lab/api/settings/@jupyterlab/apputils-extension:themes",
                                         data=json.dumps({"raw": json.dumps({"theme": theme})}).encode(),
                                         method="PUT", headers={"Content-Type": "application/json"})
            try: urllib.request.urlopen(req).read()
            except Exception as e: rows.append("(theme %s not set: %s)" % (theme, str(e)[:60]))
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page(); perrs = []
            pg.on("pageerror", lambda e: perrs.append(str(e)))
            pg.goto(BASE + "/lab/tree/" + name + "?reset")
            pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=60000)
            pg.wait_for_timeout(2500)
            if pg.query_selector(".jp-Dialog"):          # "select kernel" on a fresh server: accept
                pg.keyboard.press("Enter"); pg.wait_for_timeout(1500)
            tag = "%d × %d %s" % (w, h, theme.split()[-1].lower())
            v = []
            r0 = pg.evaluate(PROBE_JS)
            if r0["cover"] or r0["play"]: v.append("0 before the run: cover %s, Play %s" % (r0["cover"], r0["play"]))
            try:
                run_all(pg)
            except Exception as e:
                v.append("BAD Run All: %s" % str(e)[:80])
            r = pg.evaluate(PROBE_JS)
            if not r["cover"]: v.append("1 no cover after the run")
            elif any(abs(a - c) > 1 for a, c in zip(r["coverBox"], r["area"])): v.append("1 cover %s ≠ notebook %s" % (r["coverBox"], r["area"]))
            if r["rail"]: v.append("1 the timeline panel shows over the cover")
            if r["docHits"]: v.append("2 %d probes on code/document (%s)" % (r["docHits"], "; ".join(r["lines"])[:80]))
            if not r["forms"]: v.append("3 content/language/login not on the cover")
            if OUT and (w, h) == (1400, 900) and theme.endswith("Light"):
                pg.evaluate("""() => [].forEach.call(document.querySelectorAll('.jp-toast-button, .jp-Notification-Toast button'),
                    function(b){ if (b.textContent.trim() === 'No') b.click(); })""")
                pg.wait_for_timeout(600)
                pg.screenshot(path=OUT)
            pg.evaluate("() => { var p = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out .nbcover-play'); if (p) p.scrollIntoView({block: 'center'}); }")
            pg.wait_for_timeout(500)
            r3 = pg.evaluate(PROBE_JS)
            if not r3["play"] or r3["play"][1] > r3["viewBottom"] or r3["play"][3] < r3["area"][1]: v.append("3 Play not reachable %s" % r3["play"])
            cut = max(0, r3["play"][3] - r3["viewBottom"]) if r3["play"] else None
            run0 = r["run"]
            try:
                pg.mouse.click((r3["play"][0] + r3["play"][2]) / 2, (r3["play"][1] + r3["play"][3]) / 2)   # Play pulses: a pointer click at its middle
            except Exception as e:
                v.append("4 Play not clickable: %s" % str(e)[:60])
            pg.wait_for_timeout(3000)
            r4 = pg.evaluate(PROBE_JS)
            if r4["cover"] or not r4["rail"]: v.append("4 after Play: cover %s, timeline panel %s" % (r4["cover"], r4["rail"]))
            if r4["run"] != run0: v.append("4 Play ran again (run %s → %s)" % (run0, r4["run"]))
            if perrs: v.append("5 page error: %s" % perrs[0][:80])
            rows.append("%-24s theme-light=%s · cover %s on notebook %s · probes %d, on the document %d · Play %s, view bottom %d (cut %s px) · after Play cover %s rail %s · %s"
                        % (tag, r["theme"], r["coverBox"], r["area"], r["probes"], r["docHits"], r3["play"], r3["viewBottom"], cut,
                           r4["cover"], r4["rail"], "ok" if not v else "; ".join(v)))
            if v: fails.append(tag + ": " + "; ".join(v))
            ctx.close()
    b.close()
kill_sessions(BASE)
print("\n".join(rows))
print("\n" + ("COVER OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
