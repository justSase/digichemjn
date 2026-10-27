"""test_regress — Werkstatt CSS, Eilauftrag E23 (2026-10-06). Real JupyterLab
under Playwright; read off the page (getBoundingClientRect, getComputedStyle,
screenshot pixels), nothing from our CSS.

    python3 tests/regress/css_e23.py <notebook.ipynb> [lab] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

The cover is measured as the reader sees it after a run (E24.3): the last
output of the mega-cell (`.nbcover-out`), up over the notebook until Play —
brought back on the notebook under test (window.__nbCoverShow, js-E24.3) and
put away again by the last cover test (C23.8), so the row's page is as it was
for the tests after it. (Until E24 Stufe 2: the cold markdown cover of a fresh
copy opened beside it — that cell is one start line now.)

  C23.2  cover timeline legible: every name that stands on the lane (not the
         hover names) has font-size ≥ 11 px, at most two lines, and no two
         names overlap (0 px² intersection; names against foreign marks
         too); one row (mark centres ±1 px); the E13 bar is shown exactly
         when the lane overflows.
  C23.4  figure marks and the sections of Introduction/Appendix are FILLED
         dots like the chapter/intro marks: fill = border colour, opaque;
         round (w = h, radius ≥ half) outside fairy (fairy keeps its own
         silhouettes, E18.5, filled too). MC and BYOD untouched.
  C23.6  Play: the ink of its sign sits on the middle of its circle
         (ink bounding box − circle middle ≤ 1 px, x and y), at rest.
  C23.7  locked chapters and tasks (chapter, exercise, coding, quiz, BYOD
         with data-st="locked") carry a closed lock: ink present, upright,
         centred on the mark ±1 px; figure marks of a locked chapter pale
         (effective opacity ≤ .5), of an open chapter not (≥ .9).
  C23.3  the highest unlocked exercise and coding mark (data-st="open",
         E18.2) carry an OPEN lock: ink present, centred ±1 px, and a
         different drawing from the closed one (ink masks IoU < .85).
         (Which marks are "open" is JS, E23.3; this checks the sign.)
  C23.9  the account's name field (`input.nbacct-name`, JS E23.9/E23.17) on
         the cover looks like the password field beside it (height, border,
         radius, left padding, font size, face). Red while JS has not made it.
  C23.8  Title folded on the cover (click on the title mark): only the
         title and the own-cell mark stay; no bar (lane line, XP) left —
         lane pixels without marks and names = background; no E13 bar;
         each name centred under its mark (|Δx| ≤ 1 px, 0–20 px below) and
         inside the lane (not cut off);
         marks keep their height on the page (±1 px), the lane its height.
         Unfolded again: all rows back.
  C23.18 the document scrollbar's thumb is never shorter than 24 px, whatever
         length JS gives it (held at 6/16/40 px), lens 100 % and the top.
  C23.10 a cell of one's own (made through the YOC mark) stands on the main
         axis and is as wide as the YOC strip beside it: |middle − middle of
         the title card| ≤ 1 px, |width − strip width| ≤ 1 px, lens 60/100/
         150 %; and the tool corner (signs, lens) lies over none of its
         points (the J3 grid, top/middle/end). Changes the notebook: last.
         Nach-Runde 06.10. (JS, E23.10): a point of the cell counts where the
         cell is DRAWN — inside the scroller and its clip-path. Behauptete
         bisher: every point of its box, also those the lens strip's cut-out
         (this very fix, css-E23.10) leaves unpainted — red at lens 151 with
         two own cells and the page at its end (tor row 1: the first own cell
         under the strip, not painted there; .nbzoomgrp correctly on top).
         Without the cut-out the corner over a drawn cell is still red.
Gegenprobe v1.63 (+ css-E22.5/6/8): see the chronicle 06.10., Werkstatt CSS."""
import sys, os, io, json, time, shutil, itertools, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import css_e21 as C
import css_e22_8 as E8
from PIL import Image

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"
_N = itertools.count()

def _palette(pg, label):
    pg.keyboard.press("Escape"); pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=10000)
    pg.fill(".lm-CommandPalette-input", label)
    pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim().indexOf(l) === 0); }", arg=label, timeout=10000)
    pg.keyboard.press("Enter")

def _front_name(pg):
    return pg.evaluate("() => { var t = document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current .lm-TabBar-tabLabel'); return t ? t.textContent.trim() : null; }")

def _root():
    return os.environ.get("DIGICHEM_LAB_ROOT") or os.environ.get("DIGICHEM_REGRESS_ROOT") or "/home/claude/lab/root"

# ------------------------------------------------------------------ the cover (E24.3)
# 2026-10-06 (E24 Stufe 2, JS): the cover is the LAST OUTPUT of the mega-cell
# (`.nbtitle.nbcover-out`, py-E24.3) and comes up over the notebook after a run
# until Play (js-E24.3). Behauptete bisher: the cold cover is the markdown cell
# of a fresh, NOT run copy opened beside the notebook — that cell is one start
# line now (E24.3), every C23 test was red against "kein kaltes Cover". Now the
# cover of the notebook under test is brought back the way a run brings it
# (window.__nbCoverShow, js-E24.3: what Play undoes) and measured where the
# reader sees it; cover_close puts the document back. Same DOM, same script,
# same stylesheet; no second copy, no second kernel. A copy opened by another
# module (css_e24_3 keeps `{"name", "back"}` without "show") is still shut.
COVER_ON = "() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var c = P && P.querySelector('.nbcover-out[data-nbcov]'); var p = c && c.querySelector('.nbcover .nbcover-play'); return !!(c && c.querySelector('.nbcover .nbcover-tl .nbtl-row') && p && p.getBoundingClientRect().width > 2); }" % FRONT
def cover_open(pg):
    """The cover of the notebook in front, up as after a run (Play undone)."""
    st = getattr(pg, "_c23", None)
    if st and st.get("show") and pg.evaluate(COVER_ON): return True
    pg.keyboard.press("Escape"); pg.mouse.move(700, 450)
    if not pg.evaluate("() => !!(window.__nbCoverShow && window.__nbCoverShow(true))"): return False
    for _ in range(20):
        pg.wait_for_timeout(250)
        if pg.evaluate(COVER_ON): break
    pg.evaluate("() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var c = P.querySelector('.nbcover-out[data-nbcov]'); if (c) c.scrollTop = 0; }" % FRONT)
    pg.wait_for_timeout(900)
    pg._c23 = {"show": True, "name": _front_name(pg)}
    return pg.evaluate(COVER_ON)

def cover_close(pg):
    st = getattr(pg, "_c23", None)
    if not st: return
    pg._c23 = None
    if st.get("show"):
        try:
            pg.evaluate("() => { if (window.__nbCoverShow) window.__nbCoverShow(false); }")
            pg.wait_for_timeout(1200)
        except Exception:
            pass
        return
    try:
        if _front_name(pg) == st["name"]:
            _palette(pg, "Close and Shut Down Notebook")
            pg.wait_for_timeout(800)
            if pg.query_selector(".jp-Dialog"):
                b = pg.query_selector(".jp-Dialog .jp-mod-accept") or pg.query_selector(".jp-Dialog button.jp-mod-warn")
                if b: b.click()
                else: pg.keyboard.press("Enter")
            pg.wait_for_timeout(1500)
    except Exception:
        pass

def _tl_into_view(pg):
    pg.evaluate("() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var t = P.querySelector('.nbcover-tl'); t.scrollIntoView({block: 'center'}); var l = t.querySelector('.nbtl-lane'); if (l) l.scrollLeft = 0; }" % FRONT)
    pg.mouse.move(5, 450); pg.wait_for_timeout(900)

CP = "var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var tl = P.querySelector('.nbcover-tl');" % FRONT
KIND = """function kind(r){ var c = r.className; var m = /nbtl-(title|group|sub|chapter|figure|task|coding|quiz|byod|end|cell)\\b/.exec(c); return m ? m[1] : '?'; }"""

# ------------------------------------------------------------------ C23.2
NAMES = """() => { %s %s
  var vis = function(e){ var r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
  var rows = [].slice.call(tl.querySelectorAll('.nbtl-row')).filter(vis);
  var nm = [], mk = [];
  rows.forEach(function(r){ var m = r.querySelector('.nbtl-mk'), n = r.querySelector('.nbtl-nm');
    if (m && vis(m)) { var q = m.getBoundingClientRect(); mk.push({k: kind(r), x: q.left + q.width / 2, y: q.top + q.height / 2, r: [q.left, q.top, q.right, q.bottom], row: r}); }
    if (n && vis(n)) { var b = n.getBoundingClientRect(), s = getComputedStyle(n), lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.2;
      nm.push({t: n.textContent.trim().slice(0, 28), fs: parseFloat(s.fontSize), lines: Math.round(b.height / lh), r: [b.left, b.top, b.right, b.bottom], row: r}); } });
  var ov = [];
  for (var i = 0; i < nm.length; i++) {
    for (var j = i + 1; j < nm.length; j++) { var a = nm[i].r, b = nm[j].r;
      var w = Math.min(a[2], b[2]) - Math.max(a[0], b[0]), h = Math.min(a[3], b[3]) - Math.max(a[1], b[1]);
      if (w > 0.5 && h > 0.5) ov.push([nm[i].t, nm[j].t, Math.round(w * h)]); }
    mk.forEach(function(m){ if (m.row === nm[i].row) return; var a = nm[i].r, b = m.r;
      var w = Math.min(a[2], b[2]) - Math.max(a[0], b[0]), h = Math.min(a[3], b[3]) - Math.max(a[1], b[1]);
      if (w > 0.5 && h > 0.5) ov.push([nm[i].t, 'mark ' + m.k, Math.round(w * h)]); }); }
  var ys = mk.map(function(m){ return m.y; }), lane = tl.querySelector('.nbtl-lane'), sb = tl.querySelector('.nbtl-sb');
  var sbv = !!(sb && vis(sb));
  return {n: nm.length, small: nm.filter(function(x){ return x.fs < 11; }).map(function(x){ return [x.t, x.fs]; }),
          tall: nm.filter(function(x){ return x.lines > 2; }).map(function(x){ return [x.t, x.lines]; }), ov: ov,
          dy: ys.length ? Math.max.apply(null, ys) - Math.min.apply(null, ys) : null, marks: mk.length,
          over: lane ? lane.scrollWidth > lane.clientWidth + 1 : null, sb: sbv}; }""" % (CP, KIND)

def c2(pg, ctx):
    if not cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out)"
    _tl_into_view(pg)
    d = pg.evaluate(NAMES)
    if d["n"] < 3 or d["marks"] < 10: return False, "BAD nur %d Namen / %d Marken" % (d["n"], d["marks"])
    bad = []
    if d["small"]: bad.append("%d Namen < 11 px %s" % (len(d["small"]), d["small"][:3]))
    if d["tall"]: bad.append("%d Namen > 2 Zeilen %s" % (len(d["tall"]), d["tall"][:3]))
    if d["ov"]: bad.append("%d Überlappungen %s" % (len(d["ov"]), d["ov"][:3]))
    if d["dy"] is None or d["dy"] > 1: bad.append("Marken nicht in einer Reihe (Δy %s)" % d["dy"])
    if d["over"] != d["sb"]: bad.append("Leiste %s bei Überlauf %s" % (d["sb"], d["over"]))
    return (not bad), ("; ".join(bad) + " · " if bad else "") + "%d Namen, %d Marken, Überlauf %s, Leiste %s" % (d["n"], d["marks"], d["over"], d["sb"])

# ------------------------------------------------------------------ C23.4
DOTS = """() => { %s %s
  var out = [];
  tl.querySelectorAll('.nbtl-row').forEach(function(r){ var k = kind(r); if (k !== 'figure' && k !== 'sub') return;
    var m = r.querySelector('.nbtl-mk'); if (!m) return; var s = getComputedStyle(m), b = m.getBoundingClientRect();
    out.push({k: k, bg: s.backgroundColor, bc: s.borderTopColor, w: m.offsetWidth, h: m.offsetHeight,
              rad: parseFloat(s.borderTopLeftRadius), radp: s.borderTopLeftRadius, vis: b.width > 0}); });
  return out; }""" % (CP, KIND)
def _rgba(s):
    v = [float(t) for t in s[s.index("(") + 1:s.index(")")].replace("/", ",").split(",")]
    return v + [1.0] * (4 - len(v))
def c4(pg, ctx):
    if not cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out)"
    _tl_into_view(pg)
    d = pg.evaluate(DOTS)
    if len(d) < 3: return False, "BAD nur %d Abbildungs-/Abschnittsmarken" % len(d)
    fairy = ctx.get("skin") == "fairy"
    bad = []
    for x in d:
        bg, bc = _rgba(x["bg"]), _rgba(x["bc"])
        filled = bg[3] >= 0.9 and max(abs(bg[i] - bc[i]) for i in range(3)) <= 8
        rnd = abs(x["w"] - x["h"]) <= 0.5 and (x["radp"].endswith("%") and float(x["radp"][:-1]) >= 50 or x["rad"] >= x["w"] / 2 - 0.5)
        if not filled or (not fairy and not rnd): bad.append(x)
    kinds = sorted(set(x["k"] for x in d))
    return (not bad), "%d von %d nicht gefüllt/rund %s · Arten %s" % (len(bad), len(d), json.dumps(bad[:2]), kinds)

# ------------------------------------------------------------------ pixels
def _shot(pg, clip, dsf=1):
    return Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")
HIDE = """([id, css]) => { var s = document.getElementById(id); if (css === null) { if (s) s.remove(); return; }
  if (!s) { s = document.createElement('style'); s.id = id; document.head.appendChild(s); } s.textContent = css; }"""
def _hide(pg, css): pg.evaluate(HIDE, ["__c23h", css])
def _bbox_diff(a, b, thr=40):
    w, h = a.size; pa, pb = a.load(), b.load(); xs, ys, n = [], [], 0
    pts = set()
    for y in range(h):
        for x in range(w):
            if max(abs(pa[x, y][i] - pb[x, y][i]) for i in range(3)) > thr:
                xs.append(x); ys.append(y); pts.add((x, y))
    if not xs: return None, pts
    return ((min(xs) + max(xs) + 1) / 2.0, (min(ys) + max(ys) + 1) / 2.0, max(xs) - min(xs) + 1, max(ys) - min(ys) + 1), pts

# ------------------------------------------------------------------ C23.6
PLAY = """() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var b = P.querySelector('.nbcover .nbcover-play');
  b.scrollIntoView({block: 'center'}); document.getAnimations().forEach(function(a){ try { if (b.contains(a.effect && a.effect.target)) a.finish(); } catch (e) {} });
  var r = b.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }""" % FRONT
def c6(pg, ctx):
    if not cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out)"
    pg.mouse.move(5, 450)
    r = pg.evaluate(PLAY); pg.wait_for_timeout(5200); r = pg.evaluate(PLAY); pg.wait_for_timeout(400)
    if r[2] < 20: return False, "BAD kein Play-Knopf"
    clip = {"x": int(r[0]) - 4, "y": int(r[1]) - 4, "width": int(r[2]) + 9, "height": int(r[3]) + 9}
    # 2026-10-07 (E24 Stufe 2 Rest, CSS) — THE INK IS READ FROM A STILL PICTURE.
    # Behauptete bisher: whatever differs between the two shots (with / without
    # the sign) is the sign. In one row of the v1.67 gate (cyber dark old) the
    # "ink" came out 27 × 57 px, Δy −13.6 — twice as tall as the sign (33 × 38),
    # i.e. something else in the clip moved between the shots; 8 + 3 × 6 runs
    # stand-alone were all 33 × 38, Δ 0. Now every animation on the page is held
    # for the reading, and the picture with the sign is taken again after the
    # one without: only when both agree (0 px) is the difference the sign;
    # three unquiet tries are red ("BAD"), never a pass. And the ink is what
    # differs in the colour the sign is drawn in (below).
    hold = "(on) => { document.getAnimations().forEach(function(a){ try { if (on) a.pause(); else a.play(); } catch (e) {} }); }"
    bb = None; noise = 0
    for _try in range(3):
        pg.evaluate(hold, True); pg.wait_for_timeout(120)
        try:
            a = _shot(pg, clip)
            _hide(pg, ".nbcover .nbcover-play,.nbcover .nbcover-play *{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important}"
                      ".nbcover .nbcover-play::before,.nbcover .nbcover-play::after,.nbcover .nbcover-play *::before,.nbcover .nbcover-play *::after{visibility:hidden!important}")
            pg.wait_for_timeout(300); b = _shot(pg, clip); _hide(pg, None)
            pg.wait_for_timeout(300); a2 = _shot(pg, clip)
        finally:
            pg.evaluate(hold, False)
        q, _ = _bbox_diff(a, a2)
        if q is None:
            bb, pts = _bbox_diff(a, b); break
        noise += 1; pg.wait_for_timeout(1500)
    else:
        return False, "BAD Bild nicht ruhig: %d Versuche, Unterschied ohne Zeichen %dx%d px" % (noise, q[2], q[3])
    if not bb: return False, "BAD keine Tinte im Play-Knopf"
    # the sign is drawn in the accent (currentColor of Play, 07-skins E23.6):
    # only differing pixels of that colour are its ink — anything else that
    # differs between the shots is counted and named, not taken for the sign
    acc = pg.evaluate("() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var b = P.querySelector('.nbcover .nbcover-play');"
                      " var m = getComputedStyle(b, '::before').backgroundColor.match(/[\\d.]+/g) || getComputedStyle(b).color.match(/[\\d.]+/g); return m.slice(0, 3).map(Number); }" % FRONT)
    # (an edge pixel of the sign is a blend of the accent and what is behind it:
    #  it lies on the line from the picture without the sign to the accent)
    pa_, pb_ = a.load(), b.load()
    def _blend(A, B):
        d = [acc[i] - B[i] for i in range(3)]; dd = sum(v * v for v in d) or 1
        t = max(0.0, min(1.0, sum((A[i] - B[i]) * d[i] for i in range(3)) / float(dd)))
        return max(abs(A[i] - (B[i] + t * d[i])) for i in range(3)) <= 40
    ink = [(x, y) for (x, y) in pts if _blend(pa_[x, y], pb_[x, y])]
    alien = len(pts) - len(ink)
    if not ink: return False, "BAD keine Tinte in der Akzentfarbe %s (%d andere Pixel)" % (acc, alien)
    xs, ys = [x for x, _ in ink], [y for _, y in ink]
    bb = ((min(xs) + max(xs) + 1) / 2.0, (min(ys) + max(ys) + 1) / 2.0, max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
    cx, cy = r[0] + r[2] / 2.0 - clip["x"], r[1] + r[3] / 2.0 - clip["y"]
    dx, dy = bb[0] - cx, bb[1] - cy
    ok = abs(dx) <= 1 and abs(dy) <= 1
    return ok, "Tinte − Kreismitte: Δx %+.1f, Δy %+.1f px (Tinte %dx%d, Kreis %.0f px%s)" % (dx, dy, bb[2], bb[3], r[2],
               (", %d unruhige Versuche" % noise if noise else "") + (", %d Pixel nicht in der Akzentfarbe" % alien if alien else ""))

# ------------------------------------------------------------------ C23.7 / C23.3 (the signs)
ROWS = """() => { %s %s
  var out = [], chap = null;
  tl.querySelectorAll('.nbtl-row').forEach(function(r, i){ var k = kind(r); if (k === 'chapter') chap = r.getAttribute('data-st');
    if (k === 'group' || k === 'end' || k === 'title') chap = null;
    var m = r.querySelector('.nbtl-mk'); if (!m) return; var b = m.getBoundingClientRect();
    var op = 1; for (var e = m; e && e.nodeType === 1; e = e.parentElement) op *= +getComputedStyle(e).opacity;
    out.push({i: i, k: k, st: r.getAttribute('data-st'), chap: chap, op: Math.round(op * 100) / 100,
              r: [b.left, b.top, b.width, b.height], vis: b.width > 0}); });
  return out; }""" % (CP, KIND)
SIGN_OFF = ".nbcover-tl .nbtl-row::after,.nbcover-tl .nbtl-row *::before,.nbcover-tl .nbtl-row *::after{visibility:hidden!important}"
def _sign(pg, row):
    """ink of the sign of one row's mark: bbox + mask (relative to the mark middle)"""
    pg.evaluate("(i) => { %s var r = tl.querySelectorAll('.nbtl-row')[i]; var l = tl.querySelector('.nbtl-lane'); var b = r.getBoundingClientRect(), lb = l.getBoundingClientRect();"
                " if (b.left < lb.left + 30 || b.right > lb.right - 30) l.scrollLeft += (b.left + b.width / 2) - (lb.left + lb.width / 2); }" % CP, row["i"])
    pg.wait_for_timeout(250)
    row = [x for x in pg.evaluate(ROWS) if x["i"] == row["i"]][0]
    x, y, w, h = row["r"]
    clip = {"x": int(x) - 6, "y": int(y) - 6, "width": int(w) + 13, "height": int(h) + 13}
    # only this row's sign: its neighbours (16 px away) are in the clip too
    pg.evaluate("(i) => { %s tl.querySelectorAll('.nbtl-row').forEach(function(r, j){ if (j === i) r.setAttribute('data-c23', '1'); else r.removeAttribute('data-c23'); }); }" % CP, row["i"])
    _hide(pg, SIGN_OFF.replace(".nbtl-row", ".nbtl-row:not([data-c23])")); pg.wait_for_timeout(150); a = _shot(pg, clip)
    _hide(pg, SIGN_OFF); pg.wait_for_timeout(150); b = _shot(pg, clip); _hide(pg, None)
    bb, pts = _bbox_diff(a, b, 30)
    if not bb: return None
    mx, my = x + w / 2.0 - clip["x"], y + h / 2.0 - clip["y"]
    return {"dx": bb[0] - mx, "dy": bb[1] - my, "w": bb[2], "h": bb[3],
            "mask": set((int(round(px - mx)), int(round(py - my))) for px, py in pts)}

def _iou(a, b):
    return len(a & b) / float(max(1, len(a | b)))

def c7(pg, ctx):
    if not cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out)"
    _tl_into_view(pg)
    rows = pg.evaluate(ROWS)
    locked = [r for r in rows if r["st"] == "locked" and r["k"] in ("chapter", "task", "coding", "quiz", "byod")]
    if len(locked) < 2: return False, "BAD nur %d gesperrte Marken" % len(locked)
    pick = []
    for k in ("chapter", "task", "coding", "quiz", "byod"):
        pick += [r for r in locked if r["k"] == k][:2]
    bad, got = [], []
    for r in pick:
        s = _sign(pg, r)
        if not s: bad.append("%s#%d ohne Schloss" % (r["k"], r["i"])); continue
        got.append("%s %+.1f/%+.1f" % (r["k"], s["dx"], s["dy"]))
        if abs(s["dx"]) > 1 or abs(s["dy"]) > 1: bad.append("%s#%d Schloss neben der Mitte (%+.1f, %+.1f)" % (r["k"], r["i"], s["dx"], s["dy"]))
        if s["w"] < 5 or s["h"] < 5: bad.append("%s#%d Schloss zu klein (%dx%d)" % (r["k"], r["i"], s["w"], s["h"]))
    figs_l = [r for r in rows if r["k"] == "figure" and r["chap"] == "locked"]
    figs_o = [r for r in rows if r["k"] == "figure" and r["chap"] not in ("locked", None)]
    if not figs_l: bad.append("BAD keine Abbildung in einem gesperrten Kapitel")
    bad += ["Abbildung #%d im gesperrten Kapitel nicht blass (%.2f)" % (r["i"], r["op"]) for r in figs_l if r["op"] > 0.5][:2]
    bad += ["Abbildung #%d im offenen Kapitel blass (%.2f)" % (r["i"], r["op"]) for r in figs_o if r["op"] < 0.9][:2]
    return (not bad), ("; ".join(bad[:4]) + " · " if bad else "") + "%d Schlösser %s · Abb. gesperrt %d / offen %d" % (len(pick), ", ".join(got[:6]), len(figs_l), len(figs_o))

def c3(pg, ctx):
    if not cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out)"
    _tl_into_view(pg)
    rows = pg.evaluate(ROWS)
    op = [r for r in rows if r["st"] == "open" and r["k"] in ("task", "coding")]
    lk = [r for r in rows if r["st"] == "locked" and r["k"] in ("task", "coding")]
    if not op: return False, "BAD keine offene Aufgabe/Coding-Marke (data-st=open)"
    bad, got = [], []
    for r in op[:4]:
        s = _sign(pg, r)
        if not s: bad.append("%s#%d ohne offenes Schloss" % (r["k"], r["i"])); continue
        got.append("%s %+.1f/%+.1f" % (r["k"], s["dx"], s["dy"]))
        if abs(s["dx"]) > 1 or abs(s["dy"]) > 1: bad.append("%s#%d neben der Mitte (%+.1f, %+.1f)" % (r["k"], r["i"], s["dx"], s["dy"]))
        twin = [x for x in lk if x["k"] == r["k"]][:1]
        if twin:
            t = _sign(pg, twin[0])
            if t and _iou(s["mask"], t["mask"]) >= 0.85: bad.append("%s#%d offen = geschlossen gezeichnet (IoU %.2f)" % (r["k"], r["i"], _iou(s["mask"], t["mask"])))
    return (not bad), ("; ".join(bad[:4]) + " · " if bad else "") + "%d offene Marken: %s" % (len(op), ", ".join(got))

# ------------------------------------------------------------------ C23.9
FIELD = """() => { var P = document.querySelectorAll('%s'); P = P[P.length - 1]; var a = P.querySelector('.nbcover .nbacct');
  if (!a) return {err: 'no account block'};
  var n = a.querySelector('input.nbacct-name'), c = a.querySelector('input.nbacct-pw') || a.querySelector('input.nbacct-code');
  var pick = function(e){ if (!e) return null; var s = getComputedStyle(e), r = e.getBoundingClientRect();
    return {h: Math.round(r.height * 10) / 10, bw: s.borderTopWidth, bs: s.borderTopStyle, rad: s.borderTopLeftRadius,
            pad: s.paddingLeft, fs: s.fontSize, bg: s.backgroundColor, vis: r.width > 0}; };
  return {name: pick(n), code: pick(c)}; }""" % FRONT
def c9(pg, ctx):
    if not cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out)"
    d = pg.evaluate(FIELD)
    if d.get("err"): return False, "BAD " + d["err"]
    if not d["name"]: return False, "BAD kein Namensfeld input.nbacct-name auf dem Cover (JS E23.9)"
    if not d["code"]: return False, "BAD kein Passwortfeld zum Vergleich"
    keys = ("h", "bw", "bs", "rad", "pad", "fs", "bg")
    diff = {k: (d["name"][k], d["code"][k]) for k in keys if d["name"][k] != d["code"][k]}
    return (not diff), ("abweichend %s" % diff if diff else "Namensfeld = Passwortfeld (%s)" % ", ".join("%s %s" % (k, d["name"][k]) for k in keys[:5]))

# ------------------------------------------------------------------ C23.8
FOLD = """() => { %s %s
  var vis = function(e){ var r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
  var rows = [].slice.call(tl.querySelectorAll('.nbtl-row')), out = {rows: [], all: rows.length};
  rows.filter(vis).forEach(function(r){ var m = r.querySelector('.nbtl-mk'), n = r.querySelector('.nbtl-nm');
    var mb = m && vis(m) ? m.getBoundingClientRect() : null, nb = n && vis(n) ? n.getBoundingClientRect() : null;
    out.rows.push({k: kind(r), m: mb ? [mb.left + mb.width / 2, mb.top + mb.height / 2, mb.bottom] : null,
                   n: nb ? [nb.left + nb.width / 2, nb.top, nb.width, nb.left, nb.right] : null}); });
  var l = tl.querySelector('.nbtl-lane'), lb = l.getBoundingClientRect(), sb = tl.querySelector('.nbtl-sb');
  out.lane = [lb.left, lb.top, lb.width, lb.height]; out.sb = !!(sb && vis(sb));
  var t = tl.querySelector('.nbtl-title .nbtl-mk').getBoundingClientRect(); out.tm = [t.left + t.width / 2, t.top + t.height / 2];
  return out; }""" % (CP, KIND)
BAR_OFF = ".nbcover-tl .nbtl-mk,.nbcover-tl .nbtl-nm,.nbcover-tl .nbtl-row::after,.nbcover-tl .nbtl-desc{visibility:hidden!important}"
def _bar_px(pg, lane):
    clip = {"x": int(lane[0]) + 2, "y": int(lane[1]) + 2, "width": int(lane[2]) - 4, "height": int(lane[3]) - 4}
    _hide(pg, BAR_OFF); pg.wait_for_timeout(200); im = _shot(pg, clip); _hide(pg, None)
    px = list(im.getdata()); px.sort(key=lambda c: sum(c)); bgc = px[len(px) // 2]
    return sum(1 for c in im.getdata() if max(abs(c[i] - bgc[i]) for i in range(3)) > 30)
def c8(pg, ctx):
    if not cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out)"
    try:
        _tl_into_view(pg)
        before = pg.evaluate(FOLD)
        pg.mouse.click(*before["tm"]); pg.wait_for_timeout(1300); pg.mouse.move(5, 450); pg.wait_for_timeout(700)
        d = pg.evaluate(FOLD)
        bad = []
        kinds = sorted(r["k"] for r in d["rows"])
        if kinds != ["cell", "title"]: bad.append("sichtbar %s" % kinds)
        bar = _bar_px(pg, d["lane"])
        if bar > 20: bad.append("Leiste/Strahl sichtbar (%d px)" % bar)
        if d["sb"]: bad.append("E13-Leiste sichtbar")
        for r in d["rows"]:
            if not r["m"] or not r["n"]: bad.append("%s ohne Marke/Namen" % r["k"]); continue
            if abs(r["n"][0] - r["m"][0]) > 1: bad.append("%s-Name %+.0f px neben der Marke" % (r["k"], r["n"][0] - r["m"][0]))
            if not (0 <= r["n"][1] - r["m"][2] <= 20): bad.append("%s-Name nicht unter der Marke (%+.0f px)" % (r["k"], r["n"][1] - r["m"][2]))
            if r["n"][3] < d["lane"][0] - 0.5 or r["n"][4] > d["lane"][0] + d["lane"][2] + 0.5: bad.append("%s-Name ragt aus der Lane" % r["k"])
        tb = [r for r in before["rows"] if r["k"] == "title"][0]; ta = [r for r in d["rows"] if r["k"] == "title"]
        if ta and ta[0]["m"] and abs(ta[0]["m"][1] - tb["m"][1]) > 1: bad.append("Titelmarke springt %+.0f px" % (ta[0]["m"][1] - tb["m"][1]))
        if abs(d["lane"][3] - before["lane"][3]) > 1: bad.append("Lane-Höhe %+.0f px" % (d["lane"][3] - before["lane"][3]))
        t2 = pg.evaluate(FOLD)["tm"]
        hit = pg.evaluate("(p) => { var e = document.elementFromPoint(p[0], p[1]); var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), c = P.querySelector('.nbcover-out'), cell = c.closest('.jp-Cell'), sc = P.querySelector('.jp-WindowedPanel-outer'); var cr = c.getBoundingClientRect(), ce = cell.getBoundingClientRect(); return (e ? (e.className || e.tagName).toString().slice(0, 60) + ' in ' + ((e.closest('.nbtl-row') || {}).className || '-') : null) + ' | nbcov=' + c.getAttribute('data-nbcov') + ' cov=' + [cr.left, cr.top, cr.width, cr.height].map(Math.round) + ' disp=' + getComputedStyle(c).display + ' cv=' + getComputedStyle(cell).contentVisibility + ' cell=' + [ce.top, ce.bottom].map(Math.round) + ' sc=' + sc.scrollTop + '/' + sc.scrollHeight + ' doc=' + P.__nbDoc + ' cells=' + P.querySelectorAll('.jp-Cell').length + ' stack=' + document.elementsFromPoint(p[0], p[1]).slice(0, 5).map(function(x){ return (x.className || x.tagName).toString().slice(0, 25); }).join(','); }", t2)
        pg.mouse.click(*t2); pg.wait_for_timeout(1300); pg.mouse.move(5, 450); pg.wait_for_timeout(500)
        e = pg.evaluate(FOLD)
        if len(e["rows"]) != len(before["rows"]): bad.append("aufgeklappt %d statt %d Zeilen (Klick %s auf %s, vorher %s)" % (len(e["rows"]), len(before["rows"]), [round(v) for v in t2], hit, [round(v) for v in before["tm"]]))
        return (not bad), ("; ".join(bad) + " · " if bad else "") + "zu: %s, Strahl %d px, Leiste %s" % (kinds, bar, d["sb"])
    finally:
        cover_close(pg)

# ------------------------------------------------------------------ C23.18
THUMB = """(px) => { var c = document.querySelector('#nbpanel-root .nbmap-cursor'); if (!c) return null;
  if (px === null) c.style.removeProperty('--nbsb-th'); else c.style.setProperty('--nbsb-th', px + 'px');
  var r = c.getBoundingClientRect(); return [Math.round(r.height * 10) / 10, getComputedStyle(c).display]; }"""
def c18(pg, ctx):
    """E23.18 (CSS half): the thumb never shorter than 24 px, whatever length
    JS gives it — read with JS's length held at 6/16/40 px (--nbsb-th on the
    thumb), at lens 100 and the top lens. The length itself (= visible share)
    is JS's test."""
    cover_close(pg)
    bad, got = [], []
    try:
        for z in (100, 200):
            zz = pg.evaluate(E8.ZOOM, z); pg.wait_for_timeout(1200)
            for px in (6, 16, 40):
                d = pg.evaluate(THUMB, px); pg.wait_for_timeout(150); d = pg.evaluate(THUMB, px)
                if not d: return False, "BAD kein Daumen"
                want = max(24, px)
                got.append("Lupe %s: %d → %.1f" % (zz, px, d[0]))
                if d[0] + 0.5 < 24 or (px >= 24 and abs(d[0] - px) > 1): bad.append("Lupe %s: Länge %d px gezeichnet %.1f px (soll %d)" % (zz, px, d[0], want))
    finally:
        pg.evaluate(THUMB, None); pg.evaluate(E8.ZOOM, 100)
    return (not bad), ("; ".join(bad[:3]) + " · " if bad else "") + ", ".join(got)

# ------------------------------------------------------------------ C23.10
OWN = """() => { var P = document.querySelector('%s'); var card = P.querySelector('.jp-OutputArea .nbtitle-card');
  var own = [].slice.call(P.querySelectorAll('.jp-Cell[class*="nbown-"]')).filter(function(c){ return c.getBoundingClientRect().height > 4; });
  var f = P.querySelector('.jp-Notebook-footer'), cr = card && card.getBoundingClientRect(), fr = f && f.getBoundingClientRect();
  return {card: cr && cr.width ? [cr.left + cr.width / 2, cr.width] : null, foot: fr && fr.width ? [fr.left + fr.width / 2, fr.width] : null,
          own: own.map(function(c){ var w = c.querySelector(':scope > .jp-Cell-inputWrapper') || c, r = w.getBoundingClientRect(), q = c.getBoundingClientRect();
            return [r.left + r.width / 2, r.width, q.left + q.width / 2, q.width]; })}; }""" % FRONT
CORNER = r"""() => { var P = document.querySelector('%s'), h = document.getElementById('nbpanel-root');
  var skip = [].map.call(h ? h.querySelectorAll('.nbrail, .nbgrip, .nbsb') : [], function(e){ return e.getBoundingClientRect(); })
               .filter(function(r){ return r.width > 0 && r.height > 0; });
  // E23.10 Nach-Runde: a point counts only where the cell is DRAWN — inside the
  // scroller's box and inside its clip-path (css-E23.10 cuts the lens strip out:
  // what scrolls under it is not painted there and takes no click there)
  var so = P.querySelector('.jp-WindowedPanel-outer'), sr = so.getBoundingClientRect();
  var cpv = getComputedStyle(so).clipPath || 'none', poly = null, pm = /^polygon\((.*)\)$/.exec(cpv);
  if (pm) poly = pm[1].split(',').map(function(p){ var v = p.trim().split(/\s+/);
    var f = function(s, L){ return /%%$/.test(s) ? parseFloat(s) / 100 * L : parseFloat(s); };
    return [sr.left + f(v[0], sr.width), sr.top + f(v[1], sr.height)]; });
  var drawn = function(x, y){
    if (x < sr.left || x > sr.right || y < sr.top || y > sr.bottom) return false;
    if (!poly) return true;
    var inside = false;
    for (var a = 0, b = poly.length - 1; a < poly.length; b = a++) {
      var xa = poly[a][0], ya = poly[a][1], xb = poly[b][0], yb = poly[b][1];
      if ((ya > y) !== (yb > y) && x < (xb - xa) * (y - ya) / (yb - ya) + xa) inside = !inside; }
    return inside; };
  var vh = window.innerHeight, bad = [], n = 0;
  P.querySelectorAll('.jp-Cell[class*="nbown-"]').forEach(function(c){
    var r = c.getBoundingClientRect(), t = Math.max(r.top, 60), b = Math.min(r.bottom, vh - 30);
    if (b - t < 6 || r.width < 6) return;
    for (var i = 0; i < 16; i++) for (var j = 0; j < 6; j++) {
      var x = r.left + 2 + (r.width - 4) * i / 15, y = t + 2 + (b - t - 4) * j / 5;
      if (skip.some(function(q){ return x >= q.left - 2 && x <= q.right + 2 && y >= q.top - 2 && y <= q.bottom + 2; })) continue;
      if (!drawn(x, y)) continue;
      n++; var e = document.elementFromPoint(x, y);
      if (e && e.closest('#nbpanel-root')) bad.push(e.tagName + '.' + String(e.className).split(' ')[0] + ' (' + Math.round(x) + ',' + Math.round(y) + ')'); } });
  return {n: n, bad: bad}; }""" % FRONT
def c10(pg, ctx):
    cover_close(pg)
    pg.keyboard.press("Escape"); pg.mouse.move(700, 450); pg.wait_for_timeout(300)
    pg.evaluate("() => { var n = document.querySelector('%s .jp-WindowedPanel-outer'); if (n) n.scrollTop = n.scrollHeight; }" % FRONT)
    pg.wait_for_timeout(1500)
    for _ in range(3):                    # a click may land while the panel settles: try again
        if pg.evaluate(OWN)["own"]: break
        pg.evaluate("() => { var n = document.querySelector('%s .jp-WindowedPanel-outer'); if (n) n.scrollTop = n.scrollHeight; }" % FRONT)
        pg.wait_for_timeout(1200)
        y = pg.evaluate(E8.YOC)
        if y["xy"]:
            pg.mouse.move(y["xy"][0] - 40, y["xy"][1] - 40); pg.wait_for_timeout(300)
            y = pg.evaluate(E8.YOC); pg.mouse.move(*y["xy"], steps=4); pg.wait_for_timeout(600)
            pg.mouse.click(*y["xy"]); pg.wait_for_timeout(2500); pg.keyboard.press("Escape"); pg.mouse.move(700, 450)
    if not pg.evaluate(OWN)["own"]: return False, "BAD keine eigene Zelle angelegt"
    bad, got = [], []
    try:
        for z in (100, 60, 150):
            zz = pg.evaluate(E8.ZOOM, z); pg.wait_for_timeout(1500)
            pg.evaluate("() => { var n = document.querySelector('%s .jp-WindowedPanel-outer'); if (n) n.scrollTop = n.scrollHeight; }" % FRONT)
            pg.wait_for_timeout(1000)
            d = pg.evaluate(OWN)
            for _ in range(10):                # settled: two reads 400 ms apart agree
                pg.wait_for_timeout(400); d2 = pg.evaluate(OWN)
                same = json.dumps(d2) == json.dumps(d); d = d2
                if same: break
            if not d["card"] or not d["foot"] or not d["own"]: bad.append("BAD Lupe %s: nicht gemessen %s" % (zz, d)); continue
            for o in d["own"]:
                dm, dw = o[0] - d["card"][0], o[1] - d["foot"][1]
                got.append("Lupe %s: Mitte %+.1f, Breite %.0f/%.0f" % (zz, dm, o[1], d["foot"][1]))
                if abs(dm) > 1: bad.append("Lupe %s: Mitte %+.1f px neben der Titelkarte" % (zz, dm))
                if abs(dw) > 1: bad.append("Lupe %s: Breite %.0f statt %.0f (Streifen)" % (zz, o[1], d["foot"][1]))
            for frac in (0.0, 0.5, 1.0):
                pg.evaluate("(f) => { var o = document.querySelector('%s .jp-WindowedPanel-outer'); o.scrollTop = f * (o.scrollHeight - o.clientHeight); }" % FRONT, frac)
                pg.wait_for_timeout(900)
                c = pg.evaluate(CORNER)
                if c["bad"]: bad.append("Lupe %s, Lage %.1f: Ecke über der Zelle %s" % (zz, frac, c["bad"][:2]))
            # the own cell scrolled up under the corner's top row (the lens)
            pg.evaluate("() => { var P = document.querySelector('%s'), o = P.querySelector('.jp-WindowedPanel-outer'), c = P.querySelector('.jp-Cell[class*=\"nbown-\"]');"
                        " var g = document.querySelector('#nbpanel-root .nbcorner .nbzoomgrp, #nbpanel-root .nbcorner .nbbtn'); var gy = g ? g.getBoundingClientRect().top + 6 : 110;"
                        " o.scrollTop += c.getBoundingClientRect().top - gy; }" % FRONT)
            pg.wait_for_timeout(900)
            c = pg.evaluate(CORNER)
            if c["bad"]: bad.append("Lupe %s, unter der Ecke: %s" % (zz, c["bad"][:2]))
    finally:
        pg.evaluate(E8.ZOOM, 100); pg.evaluate(C.TOP)
    return (not bad), ("; ".join(bad[:4]) + " · " if bad else "") + " · ".join(got[:3])

TESTS = [
    ("C23.2 E23.2 Cover-Timeline lesbar (≥ 11 px, keine Überlappung)", c2),
    ("C23.4 E23.4 Abbildungen + Intro/Appendix-Abschnitte gefüllte Punkte", c4),
    ("C23.6 E23.6 Play-Zeichen mittig im Kreis", c6),
    ("C23.7 E23.7 gesperrt mit Schloss, Abbildungen gesperrter Kapitel blass", c7),
    ("C23.3 E23.3 höchste freie Aufgabe/Coding mit offenem Schloss", c3),
    # ("C23.9 …", c9) ruht bis E23.9 (JS/Python nach 11:00, STOP.md TERMIN) — Hauptwerkstatt v1.65
    ("C23.8 E23.8 Title zu im Cover: keine Leiste, Namen unter den Marken", c8),
    ("C23.18 E23.18 Scrollleisten-Daumen ≥ 24 px", c18),
    ("C23.10 E23.10 eigene Zelle auf der Hauptachse, Streifenbreite, Ecke frei", c10),   # wieder an: Nach-Runde JS (PATCH-js-E23.10-76ef1b1e)
]

def main():
    nb = sys.argv[1]; C.NB = nb
    C.ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    C.STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    only = sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else None
    styles = (os.environ.get("C23_STYLES") or "minimal/light,cyber/dark,cyber/light,fairy/dark").split(",")
    from playwright.sync_api import sync_playwright
    red = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C.CHROME)
        ctx, pg, errs = C.open_nb(b)
        for i, st in enumerate(styles):
            s, t = st.split("/")
            pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
            for name, fn in TESTS:
                key = name.split()[0]
                if only and key not in only: continue
                if fn is c10 and i < len(styles) - 1: continue        # changes the notebook: once, last
                try: ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                except Exception as e: ok, d = False, "BAD exception %s" % str(e)[:200]
                red += not ok
                print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", key, s, t, d[:500])); sys.stdout.flush()
            cover_close(pg)
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e23: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
