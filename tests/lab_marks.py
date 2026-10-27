"""Real-JupyterLab measurement for OBERFLAECHE §3/§3b — marks, glyphs, pips. 2026-09-27c.
NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). It opens a
fresh copy of the notebook, puts the tasks into every state through the KERNEL
(task_solved / task_skipped / task_bypassed / task_code_*; the panel picks the
states up on its own), and then, per skin x brightness x panel width, reads:

  * GLYPHS — every visible sign inside a mark (the tick, cross, skip arrow and
    the drawn lock). Its angle on screen is the SUM of the rotations of every
    element from the glyph up to the node, plus the pseudo-element's own
    (read from getComputedStyle(...).transform, element and ::before/::after).
    Measured at rest and in each state the mark can be in — :hover (a real
    mouse), :focus, .nbsel, .nbpop, .nbkeyed — and ALSO while it gets there:
    the angle is sampled every animation frame for 450 ms after the state is
    entered. A glyph that ends level but swings round on the way is not level.
  * CONTAINMENT — the glyph's box (text: its range box; drawn lock: both
    pseudo-elements) must lie inside the mark's own shape: its corners are
    taken into the mark's frame (centre, angle, scale) and compared with the
    mark's half-size, so a diamond is a diamond and not its bounding box.
  * PIPS — the two per chapter (.ps.a written, .ps.c code): laid-out size,
    opacity, state, and contrast of the fill (or ring) against the panel.
  * THE ACTIVE-CELL BAR — JupyterLab's collapser strip on the notebook with
    the panel: width and display.

    python3 tests/lab_marks.py <notebook> <out.json> [skin,skin,...] [--quick]
Environment as lab_keys.py; the kernel's connection file is looked up under
DIGICHEM_KERNEL_HOME (or ~) /.local/share/jupyter/runtime.
Exit 1 if a criterion fails."""
import sys, json, os, glob, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from lab_contrast import GROUNDS_JS
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
KHOME = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")

STATES = """
task_solved('t1'); task_skipped('t2'); task_bypassed('t3')
task_code_solved('t1'); task_code_skipped('t2')
print('states', dict(_TASKS['state']), dict(_TASKS['code']))
"""

def kexec(code):
    from jupyter_client import BlockingKernelClient
    ss = json.load(urllib.request.urlopen(BASE + "/api/sessions"))
    kid = ss[-1]["kernel"]["id"]
    cf = glob.glob(os.path.join(KHOME, ".local/share/jupyter/runtime/kernel-%s.json" % kid))[0]
    kc = BlockingKernelClient(connection_file=cf); kc.load_connection_file(); kc.start_channels()
    out = []
    def hook(m):
        if m["msg_type"] == "stream": out.append(m["content"]["text"])
        if m["msg_type"] == "error": out.append("ERR " + m["content"]["evalue"])
    kc.execute_interactive(code, output_hook=hook, timeout=60)
    kc.stop_channels(); return "".join(out)

# ---- in the page ---------------------------------------------------------
LIB = r"""
window.__nbm = (function(){
  function ang(tf){ if (!tf || tf === 'none') return 0;
    var m = tf.match(/matrix\(([^)]+)\)/); if (!m) return 0; var p = m[1].split(',').map(parseFloat);
    return Math.atan2(p[1], p[0]) * 180 / Math.PI; }
  function sc(tf){ if (!tf || tf === 'none') return 1;
    var m = tf.match(/matrix\(([^)]+)\)/); if (!m) return 1; var p = m[1].split(',').map(parseFloat);
    return Math.sqrt(p[0]*p[0] + p[1]*p[1]); }
  function norm(a){ a = a %% 360; if (a > 180) a -= 360; if (a < -180) a += 360; return a; }
  function vis(e){ var c = getComputedStyle(e); if (c.display === 'none' || c.visibility !== 'visible') return false;
    for (var a = e; a && a.id !== 'nbpanel-root'; a = a.parentElement) if (+getComputedStyle(a).opacity === 0) return false;
    var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }
  function alpha(col){ var m = col.match(/rgba?\(([^)]+)\)/); if (!m) return 1; var p = m[1].split(/[ ,\/]+/).filter(Boolean); return p.length > 3 ? +p[3] : 1; }
  // the mark: the shaped element of a node
  var MARK = '.nbrail-dot,.nbcodemark,.nbchapdot,.nbvizmark,.nbsect,.nbsubdot';
  function glyphs(node){
    var out = [], mk = node.querySelector(MARK); if (!mk || !vis(mk)) return out;
    // drawn signs: pseudo-elements with a size on the mark or its .nbdotg
    [mk].concat([].slice.call(mk.querySelectorAll('.nbdotg'))).forEach(function(e){
      if (!vis(e)) return;
      var pss = ['::before','::after'].filter(function(ps){ var q = getComputedStyle(e, ps);
        return q.content !== 'none' && q.display !== 'none' && parseFloat(q.width) > 0 && parseFloat(q.height) > 0 &&
               (alpha(q.backgroundColor) > 0 || (parseFloat(q.borderTopWidth) > 0 && alpha(q.borderTopColor) > 0)); });
      if (pss.length) out.push({kind: 'drawn', el: e, ps: pss});
      // text signs: every text node under the mark (or its .nbdotg) with a visible colour —
      // its own parent is the element that carries it
    });
    var tw = document.createTreeWalker(mk, NodeFilter.SHOW_TEXT), t;
    while ((t = tw.nextNode())) {
      var txt = t.textContent.trim(); if (!txt) continue;
      var host = t.parentElement;
      if (!vis(host) || alpha(getComputedStyle(host).color) === 0 || parseFloat(getComputedStyle(host).fontSize) === 0) continue;
      out.push({kind: 'text', el: host, node: t, txt: txt});
    }
    return out.map(function(g){ g.mark = mk; return g; });
  }
  function chainAngle(e, stop){ var a = 0; for (var x = e; x && x !== stop.parentElement; x = x.parentElement) a += ang(getComputedStyle(x).transform); return a; }
  function glyphAngle(g){
    var a = chainAngle(g.el, g.mark.closest('.nbmap-node'));
    if (g.kind === 'drawn') { var worst = 0; g.ps.forEach(function(ps){ var v = norm(a + ang(getComputedStyle(g.el, ps).transform)); if (Math.abs(v) > Math.abs(worst)) worst = v; }); return worst; }
    return norm(a);
  }
  // points of the glyph on screen
  function glyphPts(g){
    if (g.kind === 'text') {
      // the INK, not the font box: a range's box is the line's content area,
      // ascent to descent, much taller than a tick. Canvas measures the glyph
      // itself in the same computed font; the range gives where its baseline is.
      var rg = document.createRange(); rg.selectNodeContents(g.node); var r = rg.getBoundingClientRect();
      var hs = getComputedStyle(g.el), cv = (window.__nbmCv = window.__nbmCv || document.createElement('canvas')).getContext('2d');
      cv.font = hs.fontStyle + ' ' + hs.fontWeight + ' ' + hs.fontSize + ' ' + hs.fontFamily;
      var mt = cv.measureText(g.node.textContent), S = r.height / (mt.fontBoundingBoxAscent + mt.fontBoundingBoxDescent || r.height);
      var base = r.top + mt.fontBoundingBoxAscent * S;
      var L = r.left - mt.actualBoundingBoxLeft * S, R = r.left + mt.actualBoundingBoxRight * S,
          T = base - mt.actualBoundingBoxAscent * S, B = base + mt.actualBoundingBoxDescent * S;
      return [[L, T], [R, T], [L, B], [R, B]]; }
    // a pseudo-element: its box in the carrier's frame, carried to the screen
    var pts = [], e = g.el, cr = e.getBoundingClientRect(), cs = getComputedStyle(e);
    var cx = cr.left + cr.width / 2, cy = cr.top + cr.height / 2, A = chainAngle(e, g.mark.closest('.nbmap-node')) * Math.PI / 180;
    var S = 1; for (var x = e; x && !x.classList.contains('nbmap-node'); x = x.parentElement) S *= sc(getComputedStyle(x).transform);
    var w = e.offsetWidth, h = e.offsetHeight;
    g.ps.forEach(function(ps){
      var q = getComputedStyle(g.el, ps), L = parseFloat(q.left) || 0, T = parseFloat(q.top) || 0,
          W = parseFloat(q.width), H = parseFloat(q.height), ml = parseFloat(q.marginLeft) || 0, mt = parseFloat(q.marginTop) || 0;
      var bl = parseFloat(cs.borderLeftWidth) || 0, bt = parseFloat(cs.borderTopWidth) || 0;
      var ox = bl + L + ml, oy = bt + T + mt, pa = ang(q.transform) * Math.PI / 180, psc = sc(q.transform);
      var org = q.transformOrigin.split(' ').map(parseFloat);
      [[0,0],[W,0],[0,H],[W,H]].forEach(function(c){
        // own transform about its origin
        var dx = (c[0] - org[0]) * psc, dy = (c[1] - org[1]) * psc;
        var px = org[0] + dx * Math.cos(pa) - dy * Math.sin(pa), py = org[1] + dx * Math.sin(pa) + dy * Math.cos(pa);
        // into the carrier: relative to its centre, then the carrier's turn and scale
        var lx = (ox + px - w / 2) * S, ly = (oy + py - h / 2) * S;
        pts.push([cx + lx * Math.cos(A) - ly * Math.sin(A), cy + lx * Math.sin(A) + ly * Math.cos(A)]);
      });
    });
    return pts;
  }
  function inside(g){
    var mk = g.mark, r = mk.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    var A = chainAngle(mk, mk.closest('.nbmap-node')) * Math.PI / 180, S = sc(getComputedStyle(mk).transform);
    var hw = mk.offsetWidth / 2 * S, hh = mk.offsetHeight / 2 * S, worst = 1e9;
    glyphPts(g).forEach(function(p){
      var dx = p[0] - cx, dy = p[1] - cy;
      var lx = dx * Math.cos(-A) - dy * Math.sin(-A), ly = dx * Math.sin(-A) + dy * Math.cos(-A);
      worst = Math.min(worst, hw - Math.abs(lx), hh - Math.abs(ly));
    });
    return Math.round(worst * 10) / 10;   // >= -0.5 px: inside (sub-pixel)
  }
  function id(node){ return node.className.replace('nbjump nbmap-node ', '') + ' | ' + ((node.querySelector('.nbmap-lab') || {}).textContent || (node.querySelector('.nbtasklab') || {}).textContent || ''); }
  function nodes(){ return [].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).filter(function(n){ return !n.classList.contains('nbgone') && glyphs(n).length; }); }
  return {glyphs: glyphs, glyphAngle: glyphAngle, inside: inside, id: id, nodes: nodes, vis: vis, alpha: alpha};
})();
"""

# sample every frame for `ms` after the state is entered: the worst angle, and the end
SAMPLE_JS = r"""([i, ms]) => new Promise(function(res){
  var n = __nbm.nodes()[i]; if (!n) return res(null);
  var t0 = performance.now(), worst = 0, frames = 0;
  (function tick(){
    __nbm.glyphs(n).forEach(function(g){ var a = __nbm.glyphAngle(g); if (Math.abs(a) > Math.abs(worst)) worst = a; });
    frames++;
    if (performance.now() - t0 < ms) return requestAnimationFrame(tick);
    var gs = __nbm.glyphs(n);
    res({id: __nbm.id(n), worst: Math.round(worst * 10) / 10, frames: frames,
         end: gs.map(function(g){ return Math.round(__nbm.glyphAngle(g) * 10) / 10; }),
         inside: gs.map(function(g){ return __nbm.inside(g); }),
         kinds: gs.map(function(g){ return g.kind + (g.txt ? ':' + g.txt : ''); })});
  })();
})"""

PIPS_JS = r"""(grounds) => {
  function rgba(s){ if (!s) return null; var k = s.match(/color\(srgb ([^)]+)\)/); if (k) { var q = k[1].split(/[ \/]+/).filter(Boolean).map(parseFloat); return [q[0]*255, q[1]*255, q[2]*255, q.length > 3 ? q[3] : 1]; } var m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0],p[1],p[2],p.length>3?p[3]:1]; }
  function over(f,b){ var a=f[3]; return [f[0]*a+b[0]*(1-a),f[1]*a+b[1]*(1-a),f[2]*a+b[2]*(1-a),1]; }
  function lin(v){ v/=255; return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4); }
  function L(c){ return .2126*lin(c[0])+.7152*lin(c[1])+.0722*lin(c[2]); }
  function cr(a,b){ var x=L(a),y=L(b); return (Math.max(x,y)+.05)/(Math.min(x,y)+.05); }
  // the panel's face over every surface the document paints (lab_contrast GROUNDS_JS):
  // the pip is judged against the worst of them — the same grounds as the overlay contrast
  var rail = document.querySelector('#nbpanel-root .nbrail'), rb = rgba(getComputedStyle(rail).backgroundColor),
      face = rgba(getComputedStyle(rail, '::before').backgroundColor);
  grounds = grounds.map(function(g){ var c = g; if (rb && rb[3] > 0) c = over(rb, c); if (face && face[3] > 0) c = over(face, c); return c; });
  var out = [];
  document.querySelectorAll('#nbpanel-root .nbmap-node.chap:not(.nbgone) .ps').forEach(function(p){
    var cs = getComputedStyle(p), r = p.getBoundingClientRect();
    if (cs.display === 'none' || r.width === 0) { out.push({cls: p.className, size: 0}); return; }
    var op = 1; for (var a = p; a && a.id !== 'nbpanel-root'; a = a.parentElement) op *= +getComputedStyle(a).opacity;
    var fill = rgba(cs.backgroundColor), ring = rgba(cs.borderTopColor), bw = parseFloat(cs.borderTopWidth) || 0;
    var ink = (fill && fill[3] > 0.05) ? fill : ring;           // an open pip is a ring
    ink = [ink[0], ink[1], ink[2], ink[3] * op];
    var worst = 1e9; grounds.forEach(function(g){ var v = cr(over(ink, g), g); if (v < worst) worst = v; });
    out.push({cls: p.className, chap: (p.closest('.nbmap-node').querySelector('.nbmap-lab') || {}).textContent,
              size: Math.round(Math.min(p.offsetWidth, p.offsetHeight) * 10) / 10, box: [Math.round(r.width), Math.round(r.height)],
              opacity: Math.round(op * 100) / 100, fill: cs.backgroundColor, ring: cs.borderTopColor + ' ' + bw + 'px',
              cr: Math.round(worst * 100) / 100});
  });
  return out;
}"""

BAR_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); var out = [];
  P.querySelectorAll('.jp-Cell .jp-Collapser').forEach(function(c){
    var cell = c.closest('.jp-Cell'), ch = c.querySelector('.jp-Collapser-child') || c;
    var cs = getComputedStyle(c), chs = getComputedStyle(ch), r = c.getBoundingClientRect();
    out.push({cls: c.className.split(' ').slice(-1)[0], active: cell.classList.contains('jp-mod-active'),
              display: cs.display, w: Math.round(r.width * 10) / 10, h: Math.round(r.height), bg: chs.backgroundColor, childW: chs.width});
  });
  return out;
}"""

# the document is scrolled to what the mark stands for; the timeline follows it
SHOW_JS = """(i) => { var n = __nbm.nodes()[i], t = n.getAttribute('data-target'), el = t && document.getElementById(t);
  if (el) el.scrollIntoView({block: 'center'}); else n.scrollIntoView({block: 'center'}); return 1; }"""
WHERE_JS = """(i) => { var m = __nbm.nodes()[i].querySelector('.nbrail-dot,.nbcodemark,.nbchapdot,.nbvizmark,.nbsect,.nbsubdot');
  var r = m.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
  if (y < 100 || y > innerHeight - 40) return null;
  var e = document.elementFromPoint(x, y); return e && __nbm.nodes()[i].contains(e) ? [x, y] : null; }"""

SET = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t); window.__nbApplySkin(); window.__nbApplyTheme(); }"""

def run(nb, dest, skins, quick=False):
    from playwright.sync_api import sync_playwright
    fails, res = [], {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx, pg, errs = fresh(b, BASE, nb, ROOT)
        print(kexec(STATES).strip())
        pg.wait_for_timeout(4000)
        pg.add_script_tag(content=LIB % ())
        widths = ["wide"] if quick else ["narrow", "wide"]
        for wd in widths:
            if wd == "wide":
                pg.click("#nbpanel-root .nbgrip"); pg.wait_for_timeout(1400)
            for sk in skins:
                for th in (["light"] if quick else ["light", "dark"]):
                    pg.evaluate(SET, [sk, th]); pg.wait_for_timeout(800)
                    key = "%s/%s/%s" % (wd, sk, th); rows = []
                    n = pg.evaluate("() => __nbm.nodes().length")
                    for i in range(n):
                        for st in ["rest", "hover", "focus", "nbsel", "nbpop", "nbkeyed"]:
                            # enter the state, then sample from that moment
                            ok = pg.evaluate("""([i, st]) => { var n = __nbm.nodes()[i]; if (!n) return false;
                                if (st === 'focus') { n.focus({preventScroll: true}); return document.activeElement === n; }
                                if (st === 'nbsel' || st === 'nbpop' || st === 'nbkeyed') { n.classList.add(st); return true; }
                                return true; }""", [i, st])
                            if st == "hover":
                                # the timeline follows the document and can pull the mark
                                # away again: bring it into view until it stays there
                                box = None
                                for _ in range(4):
                                    box = pg.evaluate(SHOW_JS, i); pg.wait_for_timeout(900)
                                    box = pg.evaluate(WHERE_JS, i)
                                    if box: break
                                if box: pg.mouse.move(box[0], box[1])
                                ok = bool(box) and pg.evaluate("(i) => __nbm.nodes()[i].matches(':hover')", i)
                            r = pg.evaluate(SAMPLE_JS, [i, 450])
                            pg.evaluate("""([i, st]) => { var n = __nbm.nodes()[i]; if (!n) return; n.classList.remove(st); if (st === 'focus') n.blur(); }""", [i, st])
                            if st == "hover": pg.mouse.move(5, 450)
                            pg.wait_for_timeout(300)
                            if r is None: continue
                            r["state"] = st; r["entered"] = ok; rows.append(r)
                            if not ok: fails.append("%s %s %s: state not entered (not a measurement)" % (key, r["id"], st))
                            if abs(r["worst"]) > 0.5:
                                fails.append("%s %s %s: glyph turned %.1f° (end %s)" % (key, r["id"], st, r["worst"], r["end"]))
                            if any(v < -0.5 for v in r["inside"]):
                                fails.append("%s %s %s: glyph sticks out %s px (%s)" % (key, r["id"], st, r["inside"], r["kinds"]))
                    pips = pg.evaluate(PIPS_JS, pg.evaluate(GROUNDS_JS)) if wd == "wide" else []
                    for q in pips:
                        if q["size"] < 8: fails.append("%s pip %s %s: %.1f px < 8" % (key, q.get("chap"), q["cls"], q["size"]))
                        elif q["opacity"] < 1: fails.append("%s pip %s %s: opacity %.2f" % (key, q.get("chap"), q["cls"], q["opacity"]))
                        elif q["cr"] < 3: fails.append("%s pip %s %s: %.2f:1 < 3" % (key, q.get("chap"), q["cls"], q["cr"]))
                    bar = pg.evaluate(BAR_JS)
                    for c in bar:
                        if c["active"] and c["display"] != "none" and c["w"] > 0:
                            fails.append("%s active-cell bar %s: %s px, %s" % (key, c["cls"], c["w"], c["display"]))
                    res[key] = {"glyphs": rows, "pips": pips, "bar": bar}
                    print("%-22s %3d glyph states  worst %5.1f°  min inside %5.1f px  pips %s  bar %s" % (key, len(rows),
                          max([abs(r["worst"]) for r in rows] or [0]), min([min(r["inside"] or [99]) for r in rows] or [99]),
                          ("%d, min %.1f px, min %.2f:1" % (len(pips), min(q["size"] for q in pips), min(q.get("cr", 0) for q in pips))) if pips else "-",
                          ",".join("%s:%s/%s" % (c["cls"][-14:], c["display"], c["w"]) for c in bar if c["active"])))
        if errs: print("console:", errs[:5])
    if dest: json.dump(res, open(dest, "w"), indent=0)
    for f in fails[:60]: print("FAIL", f)
    print("%d failures" % len(fails))
    return fails

if __name__ == "__main__":
    nb, dest = sys.argv[1], sys.argv[2]
    skins = sys.argv[3].split(",") if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else ["minimal", "cyber", "fairy"]
    sys.exit(1 if run(nb, dest, skins, "--quick" in sys.argv) else 0)
