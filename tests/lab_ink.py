"""Real-JupyterLab measurement for E15.1 — every sign sits on the middle of its
shape, measured on the PAINTED pixels, not on boxes. 2026-10-02 (Werkstatt CSS).

NOT a suite: needs a running `jupyter lab` (see lab_keys.py). Opens a fresh copy
(device scale 2), puts the tasks into every state through the kernel, then per
skin × JupyterLab-brightness × lens (60/100/150 %) and per mark that carries a
sign (`.nbdotg` with text or a drawn ::before/::after — tick, cross, skip arrow,
lock, current) takes three clip shots of the mark:

  A  as it is · B  sign hidden (visibility) · C  mark hidden.
  ink   = pixels where A ≠ B   → its bounding box → INK MIDDLE
  shape = pixels where B ≠ C   → its bounding box → SHAPE MIDDLE (glow included;
          it is symmetric about the shape)

Criterion: |ink middle − shape middle| ≤ 1 px in x and y (CSS px), at rest, on
real mouse hover, with .nbsel and .nbkeyed, and WHILE turning: every running
animation/transition of the mark is paused at 0/33/66 % and measured.
The cover's marks (`.nbtl-mk`) are measured the same way when they carry ink.

    python3 tests/lab_ink.py <notebook> <out.json> [skins] [zooms] [themes]
Exit 1 if a criterion fails."""
import sys, os, json, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import CHROME, kill_sessions
from lab_marks import kexec
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import shutil, itertools
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
TOL = 1.0
STATES_M = os.environ.get("INK_STATES", "rest,hover,nbsel,nbkeyed").split(",")
DSF = 2
STATES = """
task_solved('t1'); task_skipped('t2'); task_bypassed('t3')
task_code_solved('t1'); task_code_skipped('t2')
"""
SET = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t); window.__nbApplySkin(); window.__nbApplyTheme(); }"""
LIB = r"""
window.__ink = (function(){
  var st = document.createElement('style');
  st.textContent = 'html.nbinkB .nbinkG,html.nbinkB .nbinkG *{visibility:hidden!important}'
    + 'html.nbinkC .nbinkM,html.nbinkC .nbinkM *{visibility:hidden!important}';
  document.head.appendChild(st);
  function vis(e){ var c = getComputedStyle(e); if (c.display === 'none' || c.visibility !== 'visible') return false;
    for (var a = e; a && a !== document.body; a = a.parentElement) if (+getComputedStyle(a).opacity === 0) return false;
    var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }
  var MARK = '.nbrail-dot,.nbcodemark,.nbchapdot,.nbvizmark,.nbsect,.nbsubdot';
  function hasInk(g){
    if (!g || !vis(g)) return false;
    if (g.classList.contains('nbchapdot')) return ['::before','::after'].some(function(ps){ var q = getComputedStyle(g, ps); return q.content !== 'none' && parseFloat(q.width) > 0; });
    if (g.textContent.trim() && parseFloat(getComputedStyle(g).fontSize) > 0) return true;
    var any = [g].concat([].slice.call(g.querySelectorAll('*')));
    return any.some(function(e){ return ['::before','::after'].some(function(ps){ var q = getComputedStyle(e, ps);
      return q.content !== 'none' && q.display !== 'none' && parseFloat(q.width) > 0 && parseFloat(q.height) > 0; }) ||
      (e !== g && e.textContent.trim() && parseFloat(getComputedStyle(e).fontSize) > 0); });
  }
  function list(){
    var out = [];
    [].forEach.call(document.querySelectorAll('#nbpanel-root .nbmap-node'), function(n){
      if (n.classList.contains('nbgone')) return;
      var m = n.querySelector(MARK); if (!m || !vis(m)) return;
      var g = m.querySelector('.nbdotg');
      if (!g && n.classList.contains('locked') && m.classList.contains('nbchapdot')) g = m;
      if (!hasInk(g)) return;
      out.push({key: 'p|' + n.getAttribute('data-target') + '|' + m.className.split(' ')[0], n: n, m: m, g: g, id: 'panel ' + m.className.replace(/\s+/g, '.') + ' | ' + ((n.querySelector('.nbmap-lab,.nbtasklab') || {}).textContent || n.getAttribute('data-task') || '').slice(0, 24)});
    });
    [].forEach.call(document.querySelectorAll('.nbcover-tl .nbtl-row'), function(r){
      var m = r.querySelector('.nbtl-mk'); if (!m || !vis(m)) return;
      var g = m.querySelector('.nbtl-g'); if (!hasInk(g)) return;
      out.push({key: 'c|' + r.className, n: r, m: m, g: g, id: 'cover ' + r.className.replace(/\s+/g, '.')});
    });
    return out;
  }
  var cur = null, keys = [];
  function byKey(k){
    var P = k.split('|');
    if (P[0] === 'c') { var rows = [].filter.call(document.querySelectorAll('.nbcover-tl .nbtl-row'), function(r){ return r.className === P.slice(1).join('|') && r.getBoundingClientRect().width > 0; });
      var r = rows[0]; if (!r) return null; var m = r.querySelector('.nbtl-mk'); return {n: r, m: m, g: m && m.querySelector('.nbtl-g')}; }
    var ns = [].filter.call(document.querySelectorAll('#nbpanel-root .nbmap-node'), function(n){
      var m = n.querySelector(MARK); return n.getAttribute('data-target') === P[1] && m && m.className.split(' ')[0] === P[2] && m.getBoundingClientRect().width > 0; });
    var n = ns[0]; if (!n) return null; var m = n.querySelector(MARK), g = m.querySelector('.nbdotg');
    if (!g && n.classList.contains('locked') && m.classList.contains('nbchapdot')) g = m;
    return {n: n, m: m, g: g};
  }
  function snap(){ keys = list().map(function(it){ return it.key; }); return keys.length; }
  function at(i){ var it = keys[i] && byKey(keys[i]); if (it) it.id = keys[i]; return it; }
  function tag(i){
    [].forEach.call(document.querySelectorAll('.nbinkG,.nbinkM'), function(e){ e.classList.remove('nbinkG', 'nbinkM'); });
    var it = at(i); if (!it) return null;
    cur = it;
    var r = it.m.getBoundingClientRect();
    return {id: it.id, r: [r.left, r.top, r.width, r.height]};
  }
  function anims(i){
    var it = at(i); if (!it) return [];
    var A = [];
    [it.n, it.m, it.g].concat([].slice.call(it.n.querySelectorAll('*'))).forEach(function(e){
      e.getAnimations({subtree: false}).forEach(function(a){ if (A.indexOf(a) < 0) A.push(a); }); });
    return A;
  }
  // hiding: an ATTRIBUTE (the panel's JS rewrites className) and a rule that
  // outranks every rule of ours, !important ones included (+3 ids), plus
  // inline !important on every element; pseudo-elements (lock, chapter lock)
  // follow the rule.
  var Z = ':not(#nbz1):not(#nbz2):not(#nbz3)';
  st.textContent += '[data-nbink]' + Z + ',[data-nbink]' + Z + ' *,[data-nbink]' + Z + '::before,[data-nbink]' + Z + '::after,'
    + '[data-nbink]' + Z + ' *::before,[data-nbink]' + Z + ' *::after{visibility:hidden!important}'
    + '[data-nbinkps]' + Z + '::before,[data-nbinkps]' + Z + '::after{visibility:hidden!important}';
  var hid = [], frozen = [];
  // hiding by a RULE built from the mark's key (its node's data-target and the
  // mark's kind): the panel re-renders marks and rewrites classes, a rule
  // survives that. +3 ids outrank every rule of ours, !important ones too.
  var hs = document.createElement('style'); document.head.appendChild(hs); var on = {};
  function sels(i){
    var P = keys[i].split('|');
    var N = P[0] === 'c' ? '.nbcover-tl .nbtl-row.' + P.slice(1).join('|').trim().split(/\s+/).join('.') + Z
                         : '#nbpanel-root .nbmap-node[data-target="' + P[1] + '"]' + Z;
    var M = P[0] === 'c' ? '.nbtl-mk' : '.' + P[2];
    return {N: N, M: M};
  }
  function css(){ var t = '', S;
    Object.keys(on).forEach(function(k){ var v = on[k]; S = v.s;
      if (k === 'o') t += S.N + ' :not(' + S.M + '):not(:has(' + S.M + ')):not(' + S.M + ' *),' + S.N + '::before,' + S.N + '::after';
      if (k === 'g') t += S.N + ' ' + S.M + ' .nbdotg,' + S.N + ' ' + S.M + ' .nbdotg *,' + S.N + ' ' + S.M + ' .nbdotg::before,' + S.N + ' ' + S.M + ' .nbdotg::after,' + S.N + ' ' + S.M + ' .nbtl-g'
                      + (v.self ? ',' + S.N + ' ' + S.M + '::before,' + S.N + ' ' + S.M + '::after' : '');
      if (k === 'm') t += S.N + ' ' + S.M + ',' + S.N + ' ' + S.M + ' *,' + S.N + ' ' + S.M + '::before,' + S.N + ' ' + S.M + '::after,' + S.N + ' ' + S.M + ' *::before,' + S.N + ' ' + S.M + ' *::after';
      t += '{visibility:hidden!important}'; });
    hs.textContent = t; }
  function hide(i, w){ var it = at(i); if (!it) return; on[w] = {s: sels(i), self: it.g === it.m}; css(); }
  function unhide(all){ if (all) on = {}; else { var o = on.o; on = {}; if (o) on.o = o; } css(); }
  function freeze(){ frozen = document.getAnimations().filter(function(a){ return a.playState === 'running'; }); frozen.forEach(function(a){ a.pause(); }); }
  function thaw(){ frozen.forEach(function(a){ try { a.play(); } catch(e){} }); frozen = []; }
  return {list: list, snap: snap, at: at, tag: tag, anims: anims, vis: vis, hide: hide, unhide: unhide, freeze: freeze, thaw: thaw};
})();
"""

def shot(pg, clip):
    b = pg.screenshot(clip=clip, animations="allow")
    return np.asarray(Image.open(io.BytesIO(b)).convert("RGB")).astype(int)

def bbox(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0: return None
    return xs.min(), xs.max() + 1, ys.min(), ys.max() + 1

def measure(pg, i, tries=6):
    """Three shots of a mark that stands still. The panel follows the document
    with its own (script) motion, so a shot series counts only when the mark's
    box is the same before and after it and two shots of the untouched mark agree."""
    for k in range(tries):
        t = pg.evaluate("(i)=>__ink.tag(i)", i)
        if not t: return None
        x, y, w, h = t["r"]; pad = 10
        clip = {"x": max(0, x - pad), "y": max(0, y - pad), "width": w + 2 * pad, "height": h + 2 * pad}
        pg.evaluate("()=>__ink.freeze()")
        pg.evaluate("(i)=>__ink.hide(i,'o')", i)
        A = shot(pg, clip)
        pg.evaluate("(i)=>__ink.hide(i,'g')", i); B = shot(pg, clip)
        pg.evaluate("(i)=>__ink.hide(i,'m')", i); C = shot(pg, clip)
        pg.evaluate("()=>__ink.unhide(false)"); A2 = shot(pg, clip)
        pg.evaluate("()=>__ink.unhide(true)")
        t2 = pg.evaluate("(i)=>__ink.tag(i)", i)
        pg.evaluate("()=>__ink.thaw()")
        moved = max(abs(u - v) for u, v in zip(t["r"], t2["r"])) if t2 else 99
        still = moved < 0.25 and A.shape == A2.shape and (np.abs(A - A2).max(axis=2) > 8).sum() == 0
        if os.environ.get("INKDBG"):
            kk = len(os.listdir(os.environ["INKDBG"]))
            Image.fromarray(np.concatenate([A, B, C, A2], axis=1).astype("uint8")).save(os.path.join(os.environ["INKDBG"], "%03d%s.png" % (kk, "" if still else "x")))
        if still: break
        pg.wait_for_timeout(400)
    else:
        return {"id": t["id"], "ink": None, "shape": None, "moving": True}
    shp = np.abs(B - C).max(axis=2) > 24
    bs = bbox(shp)
    ink = np.abs(A - B).max(axis=2) > 24
    if bs:   # a sign is inside its shape: whatever changed outside it is not the sign
        m = np.zeros_like(ink); m[bs[2]:bs[3], bs[0]:bs[1]] = True; ink &= m
    bi = bbox(ink)
    if not bi or not bs: return {"id": t["id"], "ink": bool(bi), "shape": bool(bs)}
    # the INK on screen; the SHAPE's middle is the middle of the mark's painted
    # border box — a rectangle turned and scaled about its own middle, so the
    # middle of its client rect, exactly. (The pixels of the shape carry
    # glows and drop shadows that are offset on purpose; their box is not
    # the shape.) Pixel middle of the shape for information: pdx/pdy.
    ix, iy = clip["x"] + (bi[0] + bi[1]) / 2 / DSF, clip["y"] + (bi[2] + bi[3]) / 2 / DSF
    sx, sy = x + w / 2, y + h / 2
    px, py = clip["x"] + (bs[0] + bs[1]) / 2 / DSF, clip["y"] + (bs[2] + bs[3]) / 2 / DSF
    return {"id": t["id"], "dx": round(ix - sx, 2), "dy": round(iy - sy, 2), "tries": k + 1,
            "pdx": round(ix - px, 2), "pdy": round(iy - py, 2),
            "inkwh": [float(bi[1] - bi[0]) / DSF, float(bi[3] - bi[2]) / DSF],
            "shapewh": [float(bs[1] - bs[0]) / DSF, float(bs[3] - bs[2]) / DSF]}

SHOW = """(i) => { var it = __ink.at(i); var n = it.n, t = n.getAttribute('data-target'), el = t && document.getElementById(t);
  if (it.id.indexOf('cover') === 0) { it.m.scrollIntoView({block: 'center', inline: 'center'}); return 1; }
  if (el) el.scrollIntoView({block: 'center'}); else n.scrollIntoView({block: 'center'}); return 1; }"""
WHERE = """(i) => { var it = __ink.at(i); if (!it) return null; var r = it.m.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
  if (y < 90 || y > innerHeight - 40 || x < 0 || x > innerWidth) return null;
  var e = document.elementFromPoint(x, y); return e && it.n.contains(e) ? [x, y] : null; }"""

def lens(pg, pct):
    return pg.evaluate("""(pct) => new Promise(function(res){
      var s = document.querySelector('#nbpanel-root .nbz-doc .nbslider'); if (!s) return res(null);
      var lo = +(s.min || 0), hi = +(s.max || 100), best = null, bd = 1e9;
      for (var v = lo; v <= hi; v++) { s.value = String(v); s.dispatchEvent(new Event('input', {bubbles: true}));
        var z = +localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1'); if (Math.abs(z - pct) < bd) { bd = Math.abs(z - pct); best = v; } }
      s.value = String(best); s.dispatchEvent(new Event('input', {bubbles: true})); s.dispatchEvent(new Event('change', {bubbles: true}));
      setTimeout(function(){ res(+localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1')); }, 1500); })""", pct)

def force(cdp, pg, i, states):
    """:hover held by the browser itself (DevTools CSS.forcePseudoState) on the
    sign, the mark, the node and every ancestor — what a pointer resting on the
    sign gives, but it stays while the shots hide the sign or the mark (a real
    pointer would fall through and the mark would turn back mid-measurement)."""
    pg.evaluate("(i)=>{ document.querySelectorAll('[data-nbinkh]').forEach(function(e){ e.removeAttribute('data-nbinkh'); }); var it = __ink.at(i); if (!it) return; var k = 0; for (var e = (it.g || it.m); e && e !== document.documentElement; e = e.parentElement) e.setAttribute('data-nbinkh', String(k++)); }", i)
    for _ in range(5):
        try:
            doc = cdp.send("DOM.getDocument", {"depth": -1})
            ids = cdp.send("DOM.querySelectorAll", {"nodeId": doc["root"]["nodeId"], "selector": "[data-nbinkh]"})["nodeIds"]
            for nid in ids:
                cdp.send("CSS.forcePseudoState", {"nodeId": nid, "forcedPseudoClasses": states})
            return True
        except Exception:
            pg.wait_for_timeout(200)
    return False

def run(nb, dest, skins, zooms, themes, wide=False):
    fails, res = [], {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        kill_sessions(BASE)
        name = "ink_%s" % os.path.basename(nb); shutil.copy(nb, os.path.join(ROOT, name))
        ctx = b.new_context(viewport={"width": 1400, "height": 900}, device_scale_factor=DSF)
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        from lab_keys import open_nb
        pg.goto(BASE + "/lab/tree/" + name + "?reset")
        pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=60000)
        pg.wait_for_timeout(2000)
        if pg.query_selector(".jp-Dialog"): pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
        pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
        pg.keyboard.press("Control+Shift+C")
        pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
        pg.keyboard.type("Run All Cells"); pg.wait_for_timeout(300); pg.keyboard.press("Enter")
        pg.wait_for_selector("#nbpanel-root .nbmap-node", state="attached", timeout=120000); pg.wait_for_timeout(5000)
        try: pg.click(".jp-toast-buttonBar button:has-text('No')", timeout=1500)
        except Exception: pass
        kexec(STATES); pg.wait_for_timeout(4000)
        pg.add_script_tag(content=LIB)
        cdp = ctx.new_cdp_session(pg); cdp.send("DOM.enable"); cdp.send("CSS.enable")
        if wide: pg.click("#nbpanel-root .nbgrip"); pg.wait_for_timeout(1500)
        for z in zooms:
            got = lens(pg, z); pg.wait_for_timeout(1500)
            for sk, th in itertools.product(skins, themes):
                pg.evaluate(SET, [sk, th]); pg.wait_for_timeout(900)
                key = "%s/%s/%s%s" % (sk, th, z, "/wide" if wide else ""); rows = []
                n = pg.evaluate("()=>__ink.snap()")
                for i in range(n):
                    for stt in STATES_M:
                        box = None
                        for _ in range(4):
                            pg.evaluate(SHOW, i); pg.wait_for_timeout(700)
                            box = pg.evaluate(WHERE, i)
                            if box: break
                        if not box: rows.append({"i": i, "state": stt, "skip": "not on screen"}); continue
                        pg.mouse.move(5, 450); pg.wait_for_timeout(250)
                        if stt in ("nbsel", "nbkeyed"):
                            pg.evaluate("([i,c])=>__ink.at(i).n.classList.add(c)", [i, stt])
                        if stt == "hover": force(cdp, pg, i, ["hover"])
                        # while it turns: pause every animation at 0/33/66 %, then let it end
                        fr = []
                        nA = pg.evaluate("(i)=>__ink.anims(i).length", i)
                        if nA:
                            for f in (0.0, 0.33, 0.66):
                                pg.evaluate("""([i,f])=>__ink.anims(i).forEach(function(a){ try { a.pause();
                                    var d = a.effect.getComputedTiming().duration || a.effect.getTiming().duration || 0; a.currentTime = (a.effect.getTiming().delay||0) + d * f; } catch(e){} })""", [i, f])
                                m = measure(pg, i)
                                if m: m["at"] = f; fr.append(m)
                            pg.evaluate("(i)=>__ink.anims(i).forEach(function(a){ try { a.finish(); } catch(e){ try{a.play();}catch(e2){} } })", i)
                        pg.wait_for_timeout(600)
                        m = measure(pg, i)
                        if m: m["at"] = "end"; fr.append(m)
                        if stt in ("nbsel", "nbkeyed"):
                            pg.evaluate("([i,c])=>__ink.at(i).n.classList.remove(c)", [i, stt])
                        if stt == "hover": force(cdp, pg, i, [])
                        for m in fr:
                            m["state"] = stt; rows.append(m)
                            if "dx" not in m:
                                fails.append("%s %s %s: no ink/shape %s" % (key, m["id"], stt, m)); continue
                            if abs(m["dx"]) > TOL or abs(m["dy"]) > TOL:
                                fails.append("%s %s %s@%s: ink−shape %+.1f,%+.1f px (ink %s, shape %s)" % (key, m["id"], stt, m["at"], m["dx"], m["dy"], m["inkwh"], m["shapewh"]))
                    pg.mouse.move(5, 450)
                res[key] = {"lens": got, "rows": rows}
                ok = [r for r in rows if "dx" in r]
                print("%-24s lens %s  %3d shots  worst |dx| %.1f  |dy| %.1f" % (key, got, len(ok),
                      max([abs(r["dx"]) for r in ok] or [0]), max([abs(r["dy"]) for r in ok] or [0])), flush=True)
        res["errs"] = errs
    if dest: json.dump(res, open(dest, "w"), indent=0)
    for f in fails[:80]: print("FAIL", f)
    print("%d failures" % len(fails))
    return fails

if __name__ == "__main__":
    nb, dest = sys.argv[1], sys.argv[2]
    skins = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else ["minimal", "cyber", "retro", "fairy"]
    zooms = [int(z) for z in sys.argv[4].split(",")] if len(sys.argv) > 4 and sys.argv[4] else [60, 100, 150]
    themes = sys.argv[5].split(",") if len(sys.argv) > 5 and sys.argv[5] else ["light", "dark"]
    sys.exit(1 if run(nb, dest, skins, zooms, themes, "--wide" in sys.argv) else 0)
