"""test_regress — Werkstatt CSS, Eilauftrag E21 (2026-10-02). NOT a headless
suite: it drives a real JupyterLab (DIGICHEM_LAB_URL, default
http://127.0.0.1:8899, notebook in its root) or a real JupyterLite site
(DIGICHEM_LITE_URL, default http://127.0.0.1:8901, notebook in its root) under
Playwright/Chromium and reads everything off the page: getComputedStyle,
getBoundingClientRect and screenshot pixels. Nothing here reads our own CSS.

    python3 tests/regress/css_e21.py <notebook.ipynb> [lab|lite] [fresh|old] [checks]
    (also a module of tests/regress/run.py: TESTS at the end, C8 C9 C11 C12 C14)

checks (default all): R8 R9 R11 R12 R14
  R8  E21.8  the marker leaves a TRAIL behind it while the page moves (length
             grows with the speed) and it is gone ≤ 0.7 s after the page stops.
             Read from pixels on the marker's column (marks, pips and XP pieces
             hidden for the read, so only marker + light + trail are drawn).
  R9  E21.9  light theme, four styles: the marker (strich) against the panel
             ≥ 3 : 1; against the lane it stands on ≥ 3 : 1, directly or via
             a separating edge (both steps ≥ 3 : 1); its light is plainly visible
             next to the lane (ΔE2000 ≥ 25 against the bare panel; v1.61: 15–22).
  R11 E21.11 the "start again with …" buttons under End look like the mode
             cards on the cover (same radius, border, padding, column layout,
             card width) — compared with the cover's own .nbmode-opt.
  R12 E21.12 cover timeline: chapter and figure marks have no colour of their
             own (border = the neutral border of the section marks under
             Introduction/Appendix, or the grey locked one; no glow); only
             exercise marks are coloured.
  R14 E21.14 no three dots (the crest) under the heading pill.
Skins minimal + cyber × light + dark (R9: all four styles, light).
"old" = browser storage as v1.54 left it (shared lens, orient, readline,
role, a stored mode), seeded before the page loads.
Exit 1 on any failed claim. Each claim was run against v1.61 (= v1.60 in
every visible value) first and is red there where the user saw the fault
(R8, R9, R11, R12, R14) — see the chronicle 02.10., Werkstatt CSS, E21."""
import sys, os, io, json, time, math
from playwright.sync_api import sync_playwright
from PIL import Image

# standalone: set in main() from argv; inside the runner (TESTS below) unused
NB, ENV, STORE, CHECKS = "", "lab", "fresh", ["R8", "R9", "R11", "R12", "R14"]
CHROME = os.environ.get("DIGICHEM_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
LAB = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
LITE = os.environ.get("DIGICHEM_LITE_URL", "http://127.0.0.1:8901")
SHOTS = os.environ.get("DIGICHEM_REGRESS_SHOTS", "")
# Only for a workshop measuring a CSS patch BEFORE the JS half exists: copy the
# marker's inline `top` into --nbm-y (the E21.8 contract). Never in the gate.
SIM_Y = os.environ.get("DIGICHEM_SIM_NBM_Y") == "1"

OLD = {"digichemjn.skin.v1": "cyber", "digichemjn.theme.v1": "dark",
       "digichemjn.zoom.v1": "130", "digichemjn.guizoom.v1": "100",
       "digichemjn.orient.v1": "vert", "digichemjn.readline.v1": "40",
       "digichemjn.role.v1": "student", "digichemjn.mode.complex-numbers": "both",
       "digichemjn.mode.introduction-to-modeling": "both"}
SEED = """(o) => { try { if (!localStorage.getItem('__nbregress_seeded')) {
  Object.keys(o).forEach(function(k){ localStorage.setItem(k, o[k]); });
  localStorage.setItem('__nbregress_seeded', '1'); } } catch (e) {} }"""
SET = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t);
  window.__nbApplySkin(); window.__nbApplyTheme(); }"""
SIM = """() => { var m = document.querySelector('#nbpanel-root .nbmap-here'); if (!m) return;
  var f = function(){ var t = m.style.top || '0px'; if (m.style.getPropertyValue('--nbm-y') !== t) m.style.setProperty('--nbm-y', t); };
  f(); new MutationObserver(f).observe(m, {attributes: true, attributeFilter: ['style']}); }"""

fails, rows = [], []
def claim(name, ok, got):
    rows.append((name, "ok" if ok else "ROT", got))
    if not ok: fails.append("%s: %s" % (name, got))

def status(pg):
    return pg.evaluate("""() => { var e = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')
        || document.querySelector('.jp-Notebook-ExecutionIndicator'); return e ? e.getAttribute('data-status') : null; }""")

def run_all(pg):
    if pg.query_selector(".jp-Dialog"):
        pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
    # command mode on the notebook without clicking into a cell (a saved run
    # hides the title cell; a click there is "not visible")
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current", timeout=15000)
    pg.evaluate("() => { var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook'); if (n) n.focus(); }")
    pg.keyboard.press("Escape"); pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=10000)
    pg.keyboard.type("Run All Cells")
    pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === 'Run All Cells'); }", timeout=10000)
    pg.keyboard.press("Enter")

def open_nb(b):
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    if STORE == "old":
        ctx.add_init_script("(%s)(%s)" % (SEED, json.dumps(OLD)))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    url = (LAB + "/lab/tree/" + NB + "?reset") if ENV == "lab" else (LITE + "/lab/index.html?path=" + NB)
    pg.goto(url)
    pg.wait_for_selector(".jp-NotebookPanel .jp-Cell", state="attached", timeout=120000)
    t0 = time.time()
    while status(pg) != "idle" and time.time() - t0 < 120: pg.wait_for_timeout(500)
    pg.wait_for_timeout(1500)
    run_all(pg)
    pg.wait_for_selector("#nbpanel-root .nbmap", state="attached", timeout=300000)
    t0 = time.time()
    while status(pg) != "idle" and time.time() - t0 < 300: pg.wait_for_timeout(1000)
    pg.wait_for_timeout(2500)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lab_keys import cover_play
    cover_play(pg)                      # E24.3 (JS): after the run the cover, Play → the document
    if SIM_Y: pg.evaluate(SIM)
    return ctx, pg, errs

def shot(pg, clip):
    return Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")

def lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)
def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
def lab(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = [ch(v) for v in c[:3]]
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return (116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z)))
def de2000(c1, c2):
    L1, a1, b1 = lab(c1); L2, a2, b2 = lab(c2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360; h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dhp = 0 if C1p * C2p == 0 else (h2p - h1p if abs(h2p - h1p) <= 180 else (h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360))
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hbp = (h1p + h2p) / 2 if abs(h1p - h2p) <= 180 else (h1p + h2p + 360) / 2
    if C1p * C2p == 0: hbp = h1p + h2p
    T = 1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp)) \
        + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63))
    SL = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2); SC = 1 + 0.045 * Cbp; SH = 1 + 0.015 * Cbp * T
    RT = -2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hbp - 275) / 25) ** 2)))
    return math.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2 + RT * (dCp / SC) * (dHp / SH))

# marks, pips, XP pieces and labels out of the way for a pixel read: what is
# left on the rail is the lane, the marker, its light and its trail
BARE = """(on) => { var id = '__nbregress_bare', s = document.getElementById(id);
  if (!on) { if (s) s.remove(); return; }
  if (!s) { s = document.createElement('style'); s.id = id; document.head.appendChild(s); }
  s.textContent = '#nbpanel-root .nbmap-node, #nbpanel-root .nbseg, #nbpanel-root .nbmap-fill, #nbpanel-root .nbmap-cursor, #nbpanel-root .nbgrip{visibility:hidden!important}'; }"""
MARK = """() => { var m = document.querySelector('#nbpanel-root .nbmap-here'); if (!m) return null;
  var r = m.getBoundingClientRect(), b = getComputedStyle(m, '::before');
  var hy = r.top + m.clientTop + (parseFloat(b.top) || 0) + (parseFloat(b.marginTop) || 0) + (parseFloat(b.height) || 0) / 2;
  return {x: r.left + r.width / 2, y: hy, h: parseFloat(b.height) || 0, w: parseFloat(b.width) || 0}; }"""
SCROLL = """([px, ms]) => { if (window.__nbLandStop) window.__nbLandStop();
  var s = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')
       || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook');
  // time-based: px per 1/60 s, whatever the frame rate (a loaded page draws ~15 fps)
  var t0 = performance.now(), y0 = s.scrollTop; window.__nbRegMove = true;
  (function f(){ var t = performance.now() - t0; if (t > ms) { window.__nbRegMove = false; return; }
    s.scrollTop = y0 + px * 60 * t / 1000; s.dispatchEvent(new Event('scroll', {bubbles: true})); requestAnimationFrame(f); })(); }"""
TOP = """() => { var s = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')
       || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook');
  if (window.__nbLandStop) window.__nbLandStop(); s.scrollTop = 400; s.dispatchEvent(new Event('scroll', {bubbles: true})); }"""

def trail_px(im, ref):
    """Pixels on the marker's column above it that differ from the rest frame."""
    n = 0
    for yy in range(im.height):
        d = max(max(abs(a - b) for a, b in zip(im.getpixel((xx, yy)), ref.getpixel((xx, yy)))) for xx in range(2, 6))
        if d > 14: n += 1
    return n

# A screenshot takes ~1 s on a loaded page — longer than the trail lives, and
# a paused transition is overtaken by the next position the panel sets. So the
# page is FILMED: Chrome's screencast hands over every frame it paints with
# the time it was painted; the trail is read off the frames painted while the
# page moves, and off the frames painted ≥ 0.7 s after it stopped.
POS = """() => { var s = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')
       || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook');
  var m = document.querySelector('#nbpanel-root .nbmap-here'), r = document.querySelector('#nbpanel-root .nbmap');
  return [Math.round(s.scrollTop), m ? m.style.top : '', r ? Math.round(r.scrollTop) : 0]; }"""

POKE = """() => new Promise(function(res){ var d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:0;top:0;width:2px;height:2px;z-index:2147483647;pointer-events:none;background:rgb(0,0,1)';
  document.body.appendChild(d); var n = 0, t0 = performance.now();
  (function f(){ d.style.background = n++ % 2 ? 'rgb(0,0,1)' : 'rgb(0,0,2)';
    if (performance.now() - t0 < 400) requestAnimationFrame(f); else { d.remove(); res(n); } })(); })"""

# 2026-10-03 (E21 Rest C8, Tor 12:2x) — WHEN DID THE PAGE STOP? Until now the
# stop was read from Python by polling POS every 50 ms and taking the first
# 300 ms without change. On one loaded CPU the page paints 4–5 frames a
# second and a long task can hold it > 300 ms IN THE MIDDLE of the scroll —
# then "stopped" was declared too early, the marker moved on, and its fresh
# trail was read as a trail standing "0,7 s after the stop". Now the page
# itself logs every move of the marker (style top / --nbm-y) and of the lane
# (.nbmap scroll) with its own clock; the stop is the LAST logged move after
# the scroll loop has ended, re-checked after the frames are in. A move after
# the declared stop is reported (`late_moves`, `last_move`) and the stop is
# moved there. A trail that truly stands is still red: a screenshot 2,5 s
# after the (last) stop must show none either (`after2.5s`).
LOGJS = """() => { window.__c8log = []; var m = document.querySelector('#nbpanel-root .nbmap-here'),
  r = document.querySelector('#nbpanel-root .nbmap');
  var push = function(k){ window.__c8log.push([Date.now() / 1000, k, m.style.top, Math.round(r.scrollTop)]); };
  if (window.__c8off) window.__c8off();
  var o = new MutationObserver(function(){ push('m'); }), f = function(){ push('r'); };
  o.observe(m, {attributes: true, attributeFilter: ['style']}); r.addEventListener('scroll', f);
  window.__c8off = function(){ o.disconnect(); r.removeEventListener('scroll', f); window.__c8off = null; }; }"""
LOGGED = """() => ({moving: !!window.__nbRegMove, now: Date.now() / 1000,
  last: (window.__c8log || []).slice(-1)[0] || null})"""

def film(pg, px, ms, after):
    import base64, time as _t
    cdp = pg.context.new_cdp_session(pg); frames = []
    def onf(ev):
        frames.append((ev["metadata"].get("timestamp", _t.time()), ev["data"]))
        try: cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception: pass
    cdp.on("Page.screencastFrame", onf)
    cdp.send("Page.startScreencast", {"format": "png", "everyNthFrame": 1})
    pg.wait_for_timeout(300)
    pg.evaluate(LOGJS)
    t0 = _t.time(); pg.evaluate(SCROLL, [px, ms])
    pg.wait_for_timeout(ms)
    def settled(limit):
        """Wait until the scroll loop is over and nothing logged for 300 ms
        (page clock). Returns the last logged move, relative to t0."""
        while _t.time() - t0 < limit:
            g = pg.evaluate(LOGGED)
            lt = g["last"][0] if g["last"] else t0
            if not g["moving"] and g["now"] - lt >= 0.3: return lt - t0
            pg.wait_for_timeout(50)
        g = pg.evaluate(LOGGED)
        return (g["last"][0] if g["last"] else _t.time()) - t0
    # A STILL PAGE SENDS NO FRAME (E21 Rest C8, 03.10. 00:xx): from
    # t_stop + 0,75 s a dot of 2 × 2 px in the top left corner (far from the
    # panel) changes for ~0,4 s, so the screencast sends frames of the page
    # as it is THEN; a screenshot stands in if still none came.
    t_stop, t_first, late, poked = settled(ms / 1000 + 6), None, 0, -1
    t_first = t_stop
    for _ in range(4):
        wait = t_stop + 0.75 - (_t.time() - t0)
        if wait > 0: pg.wait_for_timeout(int(wait * 1000))
        if poked < t_stop:
            pg.evaluate(POKE); poked = t_stop
        pg.wait_for_timeout(max(0, int((t_stop + after / 1000 - (_t.time() - t0)) * 1000)))
        t2 = settled(t_stop + after / 1000 + 6)
        if t2 <= t_stop + 0.02: break
        late += 1; t_stop = t2              # it moved after "stopped": the stop is later
    tail = []
    pg.wait_for_timeout(max(0, int((t_stop + 2.5 - (_t.time() - t0)) * 1000)))
    tail.append((_t.time() - t0, Image.open(io.BytesIO(pg.screenshot())).convert("RGB")))
    log = pg.evaluate("() => { var l = window.__c8log || []; if (window.__c8off) window.__c8off(); return l; }")
    cdp.send("Page.stopScreencast"); cdp.detach()
    out = []
    for ts, data in frames:
        out.append((ts - t0, Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")))
    if not any(t >= t_stop + 0.7 for t, _ in out):
        out.append(tail[0])
    film.log = [[round(e[0] - t0 - t_stop, 3)] + e[1:] for e in log]
    # when the page began to move, on its own clock: a loaded page may start
    # the scroll a second after Python asked for it (measured 1,3 s)
    t_go = (log[0][0] - t0) if log else 0.0
    return out, t_stop, {"late": late, "first_stop": round(t_first, 2), "tail": tail[0], "go": t_go}

def r8(pg, tag):
    pg.evaluate(BARE, True)
    # the reference: the bare lane above the marker, at rest, mid-document
    pg.evaluate(TOP); pg.wait_for_timeout(1500)
    m = pg.evaluate(MARK)
    box = (int(m["x"]) - 4, int(m["y"]) - 200, int(m["x"]) + 4, int(m["y"]) - 15)
    ref = shot(pg, {"x": box[0], "y": box[1], "width": 8, "height": 185})
    res = {}; drift = 0
    # 1-s runs from 400 px down: slow 60 px/s, fast 840 px/s — they end
    # ≤ 1 240 px, well before End (the shortest document, chapters locked,
    # scrolls ~2 000 px; past End the lane stops, E16.6, and the column
    # above the marker is no longer the bare lane of the reference). The
    # page paints 4–15 frames a second here, so the speeds are far apart:
    # slow moves 4–15 px between two frames, fast 55–210 px.
    # two runs per speed (a loaded page paints only 2–6 frames in one run)
    for name, px in (("slow", 1), ("fast", 14)):
        mv, st, tl, late, t_stops = [], [], [], 0, []
        for rep in range(2):
            pg.evaluate(TOP); pg.wait_for_timeout(1200)
            fr, t_stop, ex = film(pg, px, 1000, 1000)
            mv += [trail_px(im.crop(box), ref) for t, im in fr if ex["go"] + 0.2 <= t <= min(ex["go"] + 1.0, t_stop)]
            st += [trail_px(im.crop(box), ref) for t, im in fr if t >= t_stop + 0.7]
            tl.append(trail_px(ex["tail"][1].crop(box), ref))
            late += ex["late"]; t_stops.append(round(t_stop, 2))
            m2 = pg.evaluate(MARK)       # the column read must still be the marker's
            drift = max(drift, abs(m2["x"] - m["x"]), abs(m2["y"] - m["y"])) if m2 else 999
            if os.environ.get("DIGICHEM_C8_DUMP"):
                d = os.path.join(os.environ["DIGICHEM_C8_DUMP"], tag.replace("/", "-").replace(" ", "_"))
                os.makedirs(d, exist_ok=True); ref.save(os.path.join(d, "ref.png"))
                for i, (t, im) in enumerate(fr):
                    im.save(os.path.join(d, "%s%d_%02d_%+.2f_%d.png" % (name, rep, i, t - t_stop, trail_px(im.crop(box), ref))))
                json.dump({"box": box, "m": m, "t_stop": t_stop, "first_stop": ex["first_stop"], "late": ex["late"],
                           "log": film.log}, open(os.path.join(d, "%s%d.json" % (name, rep)), "w"))
        res[name] = dict(after=max(st) if st else None, after_n=len(st), tail=max(tl), late=late,
                         move=max(mv) if mv else None, frames=len(mv), stop=t_stops)
    pg.evaluate(BARE, False)
    s, f = res["slow"], res["fast"]
    # the claim's numbers first: the runner keeps the first 160 characters
    out = {"fast_after0.7s": f["after"], "slow_after0.7s": s["after"], "after2.5s": [s["tail"], f["tail"]],
           "drift": round(drift, 1), "late_moves": [s["late"], f["late"]],
           "fast": f["move"], "slow": s["move"], "frames": [s["frames"], f["frames"]],
           "after_n": [s["after_n"], f["after_n"]], "stop": s["stop"] + f["stop"]}
    claim("R8 %s Spur in Bewegung (schnell) ≥ 15 px" % tag, (f["move"] or 0) >= 15, out)
    claim("R8 %s Spur schnell länger als langsam (≥ 1,5 ×)" % tag, (f["move"] or 0) >= 1.5 * (s["move"] or 0) and f["frames"] >= 3, out)
    claim("R8 %s 0,7 s nach Stillstand keine Spur" % tag, s["after"] is not None and f["after"] is not None
          and s["after"] <= 2 and f["after"] <= 2 and max(s["tail"], f["tail"]) <= 2 and drift <= 2, out)

def r9(pg, tag):
    pg.evaluate(TOP); pg.wait_for_timeout(1500)
    pg.evaluate(BARE, True); pg.wait_for_timeout(300)
    m = pg.evaluate(MARK)
    im = shot(pg, {"x": 0, "y": 0, "width": 1400, "height": 900})
    x, y = int(round(m["x"])), int(round(m["y"]))
    head = im.getpixel((x, y))
    lane = im.getpixel((x, y - 70))
    panel = im.getpixel((x - 16, y - 70))
    edge = im.getpixel((x, int(math.floor(y - m["h"] / 2 - 1))))
    glow = im.getpixel((x - 9, y))
    glow_ref = im.getpixel((x - 9, y - 70))
    pg.evaluate(BARE, False)
    c_panel = contrast(head, panel)
    c_lane = max(contrast(head, lane), min(contrast(head, edge), contrast(edge, lane)))
    dg = de2000(glow, glow_ref)
    got = {"head": head, "lane": lane, "panel": panel, "edge": edge, "c_panel": round(c_panel, 2),
           "c_lane": round(c_lane, 2), "glow": glow, "dE_glow": round(dg, 1)}
    claim("R9 %s Marker ↔ Panel ≥ 3:1" % tag, c_panel >= 3, got)
    claim("R9 %s Marker ↔ Leiste ≥ 3:1" % tag, c_lane >= 3, got)
    claim("R9 %s Leuchten sichtbar (ΔE ≥ 25)" % tag, dg >= 25, got)

CARDS = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var pick = function(e){ if (!e) return null; var c = getComputedStyle(e);
    return {r: c.borderTopLeftRadius, bw: c.borderTopWidth, bs: c.borderTopStyle, pad: c.paddingTop + ' ' + c.paddingLeft,
            dir: c.flexDirection, minw: c.minWidth, maxw: c.maxWidth, w: e.getBoundingClientRect().width,
            fw: c.fontWeight}; };
  var card = P.querySelector('.nbmode .nbmode-opt');
  var btns = [].slice.call(P.querySelectorAll('.nbend button.nbend-mode'));
  return {card: pick(card), btns: btns.map(pick), n: btns.length}; }"""
def r11(pg, tag):
    d = pg.evaluate(CARDS)
    if not d["card"] or not d["n"]:
        claim("R11 %s Ende-Knöpfe + Cover-Karte da" % tag, False, d); return
    c = d["card"]
    bad = [b for b in d["btns"] if not (b["r"] == c["r"] and b["bw"] == c["bw"] and b["bs"] == c["bs"]
                                        and b["pad"] == c["pad"] and b["dir"] == c["dir"]
                                        and b["minw"] == c["minw"] and b["maxw"] == c["maxw"])]
    claim("R11 %s „neu starten mit …“ = Modus-Karte (Radius, Rand, Innenabstand, Spalte, Breite)" % tag, not bad,
          {"card": c, "abweichend": bad[:1], "n": d["n"]})

COVER = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var out = {sub: null, rows: []};
  P.querySelectorAll('.nbcover-tl .nbtl-row').forEach(function(r){
    var m = r.querySelector('.nbtl-mk'); if (!m) return; var c = getComputedStyle(m);
    var k = r.classList.contains('nbtl-chapter') ? 'chapter' : r.classList.contains('nbtl-figure') ? 'figure'
          : r.classList.contains('nbtl-sub') ? 'sub' : /nbtl-(task|coding|quiz|byod)/.test(r.className) ? 'task' : 'other';
    var o = {k: k, st: r.getAttribute('data-st'), bc: c.borderTopColor, sh: c.boxShadow};
    if (k === 'sub' && !out.sub) out.sub = o.bc;
    out.rows.push(o); });
  return out; }"""
def rgb(s):
    v = [float(t) for t in s[s.index("(") + 1:s.index(")")].replace("/", ",").split(",")[:3]]
    return v
def hue_sat(s):
    r, g, b = [v / 255 for v in rgb(s)]
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn: return 0, 0
    d = mx - mn
    h = (60 * ((g - b) / d) % 360) if mx == r else (60 * ((b - r) / d + 2)) if mx == g else (60 * ((r - g) / d + 4))
    return h, d / (1 - abs(mx + mn - 1)) if (1 - abs(mx + mn - 1)) else 0
def r12(pg, tag):
    d = pg.evaluate(COVER)
    if not d["rows"]:
        claim("R12 %s Cover-Timeline da" % tag, False, d); return
    grey = "rgb(138, 150, 163)"
    bad = [r for r in d["rows"] if r["k"] in ("chapter", "figure")
           and not ((r["bc"] == d["sub"] or (r["st"] == "locked" and r["bc"] == grey)) and r["sh"] == "none")]
    claim("R12 %s Kapitel/Abbildungen neutral wie die Abschnitte (Rand, kein Leuchten)" % tag, not bad,
          {"neutral": d["sub"], "abweichend": len(bad), "z.B.": bad[:2]})
    col = [r for r in d["rows"] if r["k"] == "task" and r["st"] in ("open", "solved", "wrong", "skipped")
           and hue_sat(r["bc"])[1] > 0.3]
    claim("R12 %s Aufgaben bleiben farbig" % tag, len(col) >= 1, {"farbige Aufgaben": len(col)})

CREST = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  return [].slice.call(P.querySelectorAll('.nborn-crest')).map(function(e){ var r = e.getBoundingClientRect();
    return [Math.round(r.width), Math.round(r.height), getComputedStyle(e).display]; }); }"""
def r14(pg, tag):
    d = pg.evaluate(CREST)
    vis = [x for x in d if x[0] * x[1] > 0 and x[2] != "none"]
    claim("R14 %s keine drei Punkte unter der Überschriftspille" % tag, not vis, d)

def main():
    global NB, ENV, STORE, CHECKS
    NB = sys.argv[1]
    ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    if len(sys.argv) > 4 and sys.argv[4]: CHECKS = sys.argv[4].split(",")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx, pg, errs = open_nb(b)
        for s, t in (("minimal", "light"), ("cyber", "light"), ("minimal", "dark"), ("cyber", "dark")):
            pg.evaluate(SET, [s, t]); pg.wait_for_timeout(800)
            tag = "%s/%s/%s/%s %s" % (ENV, STORE, s, t, NB.split("_")[0])
            if "R8" in CHECKS: r8(pg, tag)
            if "R11" in CHECKS: r11(pg, tag)
            if "R12" in CHECKS: r12(pg, tag)
            if "R14" in CHECKS: r14(pg, tag)
            if SHOTS: pg.screenshot(path=os.path.join(SHOTS, "regress-%s-%s-%s-%s.png" % (ENV, STORE, s, t)))
        if "R9" in CHECKS:
            for s in ("minimal", "cyber", "fairy"):
                pg.evaluate(SET, [s, "light"]); pg.wait_for_timeout(800)
                r9(pg, "%s/%s/%s/light %s" % (ENV, STORE, s, NB.split("_")[0]))
        claim("Seitenfehler %s/%s" % (ENV, STORE), not errs, errs[:3])
        b.close()
    for r in rows:
        print("%-4s %s · %s" % (r[1], r[0], json.dumps(r[2], ensure_ascii=False)[:300]))
    print("css_e21: %d Zusicherungen, %d rot" % (len(rows), len(fails)))
    sys.exit(1 if fails else 0)

# ---- the runner's contract (tests/regress/README.md, Hauptwerkstatt E21.0):
# TESTS = [(name, fn)], fn(pg, ctx) -> (ok, detail); pg is the page after Run
# All with the row's style and brightness already set.
def _row(fn, ctx, *a):
    n0 = len(rows); fn(*a)
    new = rows[n0:]
    bad = [r for r in new if r[1] != "ok"]
    return (not bad, "; ".join("%s %s %s" % (r[1], r[0], json.dumps(r[2], ensure_ascii=False)[:160]) for r in (bad or new)))

def _tag(ctx):
    return "%s/%s/%s/%s %s" % (ctx.get("env"), ctx.get("storage"), ctx.get("skin"), ctx.get("theme"), ctx.get("id") or ctx.get("nb"))

def _t8(pg, ctx):
    if SIM_Y: pg.evaluate(SIM)       # workshop measurement only, never in the gate
    try: return _row(r8, ctx, pg, _tag(ctx))
    finally: pg.evaluate(TOP)

def _t9(pg, ctx):
    if ctx.get("theme") != "light":
        return True, "nicht anwendbar in einer dunklen Zeile: E21.9 gilt hell (die helle Zeile prüft alle vier Stile)"
    n0 = len(rows)
    try:
        for s in ("minimal", "cyber", "fairy"):
            pg.evaluate(SET, [s, "light"]); pg.wait_for_timeout(800)
            r9(pg, "%s → %s" % (_tag(ctx), s))
    finally:
        pg.evaluate(SET, [ctx.get("skin", "minimal"), "light"]); pg.wait_for_timeout(600)
    new = rows[n0:]; bad = [r for r in new if r[1] != "ok"]
    return (not bad, "; ".join("%s %s %s" % (r[1], r[0], json.dumps(r[2], ensure_ascii=False)[:160]) for r in (bad or new[:2])))

TESTS = [
    ("C11 E21.11 Ende-Knöpfe sehen aus wie die Modus-Karten", lambda pg, ctx: _row(r11, ctx, pg, _tag(ctx))),
    ("C12 E21.12 Cover: Kapitel/Abbildungen neutral, Aufgaben farbig", lambda pg, ctx: _row(r12, ctx, pg, _tag(ctx))),
    ("C14 E21.14 keine drei Punkte unter der Überschriftspille", lambda pg, ctx: _row(r14, ctx, pg, _tag(ctx))),
    ("C9 E21.9 Marker + Leuchten hell sichtbar (4 Stile)", _t9),
    ("C8 E21.8 Leuchtspur in Bewegung, weg 0,7 s nach Stillstand", _t8),
]

if __name__ == "__main__":
    main()
