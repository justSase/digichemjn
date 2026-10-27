"""E26.3 · Pflichttest (STOP.md, E26 Teil 3, Grundregel) — Python workshop.
    python3 tests/regress/lab_same.py <ref.ipynb> <new.ipynb> [--sizes 1920x1080,1366x768]
    DIGICHEM_LAB_SAME_REF=<ref.ipynb> python3 tests/regress/lab_same.py <new.ipynb>   (run.py, scripts.txt)
            [--themes light,dark] [--skins minimal,cyber,fairy] [--shots DIR] [--json out.json]

LAB STAYS LAB. Every change for another front end (PyCharm, VS Code, …) works
only on the reading-window path; in JupyterLab (and Lite) markup, look and
behaviour stay exactly as they were. This test compares pictures: the
reference build (v1.72 — or the base of a patch) and the new build, each run
in the SAME real JupyterLab, the same way, with the same seed, and screenshot
by screenshot:
  cover      after Run All, before Play                       (per skin)
  document   after Play: top · middle · end of the notebook,
             timeline panel shut (gui 0) and pulled out (gui max)   (per skin)
× window sizes (default 1920 × 1080 and 1366 × 768) × JupyterLab light/dark ×
skins (minimal, cyber, fairy — retro is gone since E24.6, so three, not four).
"Pixel-equal" is measured, not assumed:
  * both copies are named alike (ref/same.ipynb, new/same.ipynb: tab titles and
    the file list read the same), the file browser and the status bar are
    masked (times, kernel state), toasts are hidden, CSS animations are off,
    the text caret is hidden;
  * every picture is taken TWICE, 700 ms apart (reference and new): a pixel
    is different only when BOTH reference pictures differ from BOTH new ones
    there — what moves by itself (the marker's glow …) is never a difference;
    the pixels that move between the two reference pictures are reported;
  * a pixel counts when a channel differs by more than --tol (32/255) from
    the reference there AND from its 8 neighbours (a one-pixel raster shift of
    a glow is not a change).
    Measured 11.10. (py-E26.3, 84 views × 2): two page loads differ by 1–2/255
    in gradients and up to 21/255 in single pixels of the timeline marker's
    glow (the browser's raster, also between two loads of the same file), and
    the tab's "unsaved" dot comes and goes with autosave (the tab bar is
    masked). The pixels within the tolerance are reported as noise. Counter-
    check: one letter of the title changed → 91–131 px red per view. The version line
    is in the ⚙ drawer only, which no picture opens.
A failing pair is written to --shots (ref, new, diff) when given.
Owner: Python (STOP E26 Teil 3: „gilt künftig für jede Umgebungs-Änderung“).
exit 0 = REGRESS-LAB-SAME OK."""
import sys, os, json, time, shutil, argparse, tempfile, io
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from lab_keys import ensure_lab, kill_sessions, CHROME, cover_play          # noqa: E402
from playwright.sync_api import sync_playwright                              # noqa: E402
from PIL import Image, ImageChops                                            # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("nbs", nargs="+", help="<ref.ipynb> <new.ipynb>, or only <new.ipynb> with DIGICHEM_LAB_SAME_REF")
ap.add_argument("--sizes", default="1920x1080,1366x768")
ap.add_argument("--themes", default="light,dark")
ap.add_argument("--skins", default="minimal,cyber,fairy")
ap.add_argument("--shots", default=None)
ap.add_argument("--json", default=None)
ap.add_argument("--seed", default="4711")
ap.add_argument("--tol", type=int, default=32, help="a pixel differs when a channel differs by more than this (0..255)")
A = ap.parse_args()
if len(A.nbs) >= 2:
    A.ref, A.new = A.nbs[0], A.nbs[1]
else:
    A.ref, A.new = os.environ.get("DIGICHEM_LAB_SAME_REF", ""), A.nbs[0]
    if not A.ref or not os.path.exists(A.ref):
        # never green without a reference (run.py's scripts pass only {nb})
        print("REGRESS-LAB-SAME RED: NOT RUN — no reference build (DIGICHEM_LAB_SAME_REF=<v1.72 .ipynb>)")
        sys.exit(1)
import run as R                          # noqa: E402  (helpers only: run.py parses ["x"] when imported)

SIZES = [tuple(int(x) for x in z.split("x")) for z in A.sizes.split(",")]
HIDE_CSS = ("*{caret-color:transparent!important}"
            ".jp-toast-container,.Toastify,.jp-Notification-Toast{display:none!important}")
SCROLL = r"""(f) => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var s = P && (P.querySelector('.jp-WindowedPanel-outer') || P.querySelector('.jp-Notebook'));
  if (!s) return null; s.scrollTop = Math.round(f * Math.max(0, s.scrollHeight - s.clientHeight));
  return [Math.round(s.scrollTop), s.scrollHeight, s.clientHeight]; }"""
SKIN = r"""(sk) => { try { window.__nbStore && window.__nbStore.set('digichemjn.skin.v1', sk);
  window.__nbApplySkin && window.__nbApplySkin(); return document.body.className.match(/nbskin-\w+/g) || []; } catch (e) { return String(e); } }"""

def shot(pg):
    masks = [pg.locator(s) for s in ("#jp-main-statusbar", "#jp-left-stack", ".jp-SideBar.lm-TabBar",
                                     ".lm-DockPanel-tabBar")]
    b = pg.screenshot(animations="disabled", caret="hide", mask=masks)
    return Image.open(io.BytesIO(b)).convert("RGB")

def views(pg, nid, tag, out):
    """The same walk for both notebooks; `out` collects (name, image, image2)."""
    def take(name):
        pg.wait_for_timeout(700)
        a = shot(pg); pg.wait_for_timeout(700); b = shot(pg)
        out.append((name, a, b))
    for (w, h) in SIZES:
        pg.set_viewport_size({"width": w, "height": h}); pg.wait_for_timeout(1800)
        for sk in A.skins.split(","):
            pg.evaluate(SKIN, sk); pg.wait_for_timeout(500)
            take("%s cover %dx%d %s" % (tag, w, h, sk))
    pg.set_viewport_size({"width": SIZES[0][0], "height": SIZES[0][1]}); pg.wait_for_timeout(1200)
    st = cover_play(pg)
    if st.startswith("BAD") or st == "none":
        out.append(("%s Play" % tag, None, st)); return
    pg.wait_for_timeout(2500)
    for (w, h) in SIZES:
        pg.set_viewport_size({"width": w, "height": h}); pg.wait_for_timeout(2200)
        for sk in A.skins.split(","):
            pg.evaluate(SKIN, sk); pg.wait_for_timeout(500)
            for gui, gname in ((0, "panel shut"), (99999, "panel out")):
                pg.evaluate("(g) => { window.__nbSetGui && window.__nbSetGui(g); }", gui); pg.wait_for_timeout(1200)
                for f, pos in ((0, "top"), (0.5, "middle"), (1, "end")):
                    pg.evaluate(SCROLL, f); pg.wait_for_timeout(900)
                    take("%s doc %dx%d %s %s %s" % (tag, w, h, sk, gname, pos))
        pg.evaluate("() => { window.__nbSetGui && window.__nbSetGui(0); }")

def one(b, base, root, src, sub, theme):
    kill_sessions(base)
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    shutil.rmtree(os.path.join(kh, ".digichemjn"), ignore_errors=True)
    nid = R.nb_id(src)
    os.makedirs(os.path.join(kh, ".digichemjn"), exist_ok=True)
    open(os.path.join(kh, ".digichemjn", nid + ".seed"), "w").write(A.seed)    # the same personal numbers
    d = os.path.join(root, sub); os.makedirs(d, exist_ok=True)
    shutil.copy(src, os.path.join(d, "same.ipynb"))
    R.set_lab_theme(base, theme)
    items = {"digichemjn.skin.v1": "minimal", "digichemjn.theme.v1": theme,
             "digichemjn.skin.v1." + nid: "minimal", "digichemjn.theme.v1." + nid: theme}
    ctx = b.new_context(viewport={"width": SIZES[0][0], "height": SIZES[0][1]}, reduced_motion="reduce")
    ctx.add_init_script(R.INIT_JS % json.dumps(items))
    ctx.add_init_script("document.addEventListener('DOMContentLoaded', function(){ var s = document.createElement('style');"
                        " s.textContent = %s; document.head.appendChild(s); });" % json.dumps(HIDE_CSS))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg.goto(base + "/lab/tree/%s/same.ipynb?reset" % sub)
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(2000)
    R.palette(pg, "Run All Cells")
    pg.wait_for_function(R.READY_JS, arg=nid, timeout=180000)
    for _ in range(120):
        pg.wait_for_timeout(1000)
        stt = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if stt == "idle": break
    for _ in range(60):
        if not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"): break
        pg.wait_for_timeout(1000)
    pg.wait_for_timeout(3000)
    out = []
    views(pg, nid, theme, out)
    ctx.close()
    return out, errs

def compare(ra, rb, na, nb):
    """Two pictures of each, 700 ms apart. A pixel is DIFFERENT when every
    reference picture differs from every new one there by more than --tol in a
    channel (so a glow that moves by itself is never a difference); `moving`
    = pixels that differ between the two reference pictures."""
    if ra.size != na.size:
        return None, None, "size %s vs %s" % (ra.size, na.size)
    def mx(a, b, t):            # per pixel: largest channel difference > t
        r, g, bl = ImageChops.difference(a, b).split()
        return ImageChops.lighter(ImageChops.lighter(r, g), bl).point(lambda v: 255 if v > t else 0)
    still = mx(ra, na, A.tol)
    for x, y in ((ra, nb), (rb, na), (rb, nb)):
        still = ImageChops.darker(still, mx(x, y, A.tol))
    # … and when no reference pixel of its 3 × 3 neighbourhood matches it: a glow
    # rasterised one pixel apart between two loads is not a change (measured: single
    # pixels, ≤ 34/255, at the timeline marker) — a changed letter still is
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                still = ImageChops.darker(still, mx(ImageChops.offset(ra, dx, dy), na, A.tol))
    n_move = mx(ra, rb, A.tol).histogram()[255]
    n_bad = still.histogram()[255]
    noise = mx(ra, na, 0).histogram()[255] - mx(ra, na, A.tol).histogram()[255]
    return n_bad, (n_move, noise), still

rows, bad = [], []
base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
t0 = time.time()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    for theme in A.themes.split(","):
        ref, e1 = one(b, base, root, A.ref, "ref", theme)
        new, e2 = one(b, base, root, A.new, "new", theme)
        if [x[0] for x in ref] != [x[0] for x in new]:
            bad.append("%s: walks differ (%d vs %d views)" % (theme, len(ref), len(new)))
        for (name, ra, rb), (_, nw, nw2) in zip(ref, new):
            if ra is None or nw is None:
                rows.append({"view": name, "ok": False, "detail": "not taken: %s / %s" % (rb, nw2)}); bad.append(name); continue
            n_bad, mv, still = compare(ra, rb, nw, nw2)
            n_move, noise = mv if isinstance(mv, tuple) else (0, 0)
            ok = n_bad == 0
            rows.append({"view": name, "ok": ok, "diff": n_bad, "moving": n_move, "noise": noise})
            print("%-58s %s  %s px differ%s%s" % (name, "ok " if ok else "RED", n_bad if n_bad is not None else "-",
                                                  "" if not n_move else " (moving by itself: %d px, left out)" % n_move,
                                                  "" if not noise else " · %d px within ±%d (raster noise)" % (noise, A.tol)))
            sys.stdout.flush()
            if not ok:
                bad.append(name)
                if A.shots:
                    os.makedirs(A.shots, exist_ok=True)
                    k = name.replace(" ", "_")
                    ra.save(os.path.join(A.shots, k + "_ref.png")); nw.save(os.path.join(A.shots, k + "_new.png"))
                    if hasattr(still, "save"): still.save(os.path.join(A.shots, k + "_diff.png"))
        if e1 != e2:
            print("page errors differ: ref %s · new %s" % (e1[:2], e2[:2]))
            if len(e2) > len(e1): bad.append("%s page errors %s" % (theme, e2[:2]))
    b.close()
print("%d views compared in %.0f s" % (len(rows), time.time() - t0))
if A.json:
    json.dump(rows, open(A.json, "w"), indent=1)
print("REGRESS-LAB-SAME", "OK" if not bad else "RED %d: %s" % (len(bad), "; ".join(bad[:6])))
sys.exit(0 if not bad else 1)
