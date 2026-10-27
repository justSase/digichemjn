"""Real-JupyterLab contrast sweep — OBERFLAECHE §6 as code. 2026-09-26b.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py) and measures,
in Chromium under Playwright, every element that draws its own text, in every
skin x brightness, against what is REALLY painted under it:

  * the background is found by hit-testing (document.elementsFromPoint at the
    text's centre), not by walking DOM ancestors — the panel is position:fixed
    on <body>, so its labels sit over the document geometrically, not in it;
  * every layer under the text is read: background-color AND every gradient
    in background-image, down to the first opaque colour, and the candidates
    are composed bottom-up — each stop of each layer over each candidate
    below. A texture of 6 % lines over a page therefore yields two
    candidates, the page and the line on the page; the WORST one is taken;
  * the text colour's own alpha is laid over each candidate too.

Why hit-testing: the earlier checker walked ancestors, and a label on a
fixed panel has <body> as its only painted ancestor. It would have compared
every timeline name with the grey of <body> (#bdbdbd) instead of the page.

    python3 tests/lab_contrast.py <notebook> [out.json] [--open-panel]

Exit 1 if any pair is under 4.5:1."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import open_nb, CHROME
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
SWEEP_JS = r"""(seen) => {
  var grounds = seen.grounds || null;   // --overlay: what can lie under the panel
  function rgba(s){ if (!s) return null; var k = s.match(/color\(srgb ([^)]+)\)/); if (k) { var q = k[1].split(/[ \/]+/).filter(Boolean).map(parseFloat); return [q[0]*255, q[1]*255, q[2]*255, q.length > 3 ? q[3] : 1]; } var m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat);
    return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function stops(img){ var out = [], re = /rgba?\([^)]+\)|color\(srgb [^)]+\)/g, m;
    while ((m = re.exec(img))) out.push(rgba(m[0])); return out; }
  function over(f, b){ var a = f[3]; return [f[0]*a + b[0]*(1-a), f[1]*a + b[1]*(1-a), f[2]*a + b[2]*(1-a), 1]; }
  function lin(v){ v /= 255; return v <= .04045 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }
  function L(c){ return .2126*lin(c[0]) + .7152*lin(c[1]) + .0722*lin(c[2]); }
  function cr(a, b){ var x = L(a), y = L(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
  function hex(c){ return '#' + c.slice(0,3).map(function(v){ return ('0' + Math.round(v).toString(16)).slice(-2); }).join(''); }
  function name(e){ return e === document.body ? 'body' : (e.id ? '#' + e.id : e.tagName.toLowerCase()) +
      (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).slice(0,3).join('.') : ''); }
  var roots = [document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), document.getElementById('nbpanel-root')].filter(Boolean);
  var res = [], W = innerWidth, H = innerHeight;
  roots.forEach(function(root){
    var all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.closest('svg, .cm-editor, .jp-InputPrompt, .jp-OutputPrompt')) continue;
      var txt = ''; for (var n = el.firstChild; n; n = n.nextSibling) if (n.nodeType === 3) txt += n.textContent;
      txt = txt.trim(); if (!txt || !/[A-Za-z0-9À-ɏ]/.test(txt)) continue;
      // the TEXT's own box, not the element's: a padded pill is wider than its words
      var tn = null; for (var n2 = el.firstChild; n2; n2 = n2.nextSibling) if (n2.nodeType === 3 && n2.textContent.trim()) { tn = n2; break; }
      var rg = document.createRange(); rg.selectNodeContents(tn);
      var rs = rg.getClientRects(), r = rs.length ? rs[0] : el.getBoundingClientRect();
      if (r.width < 2 || r.height < 2) continue;
      var cx = r.left + Math.min(r.width, 40) / 2, cy = r.top + r.height / 2;
      if (cx < 0 || cy < 0 || cx >= W || cy >= H) continue;
      var cs = getComputedStyle(el);
      if (cs.visibility !== 'visible' || +cs.opacity === 0) continue;
      var key = el.getAttribute('data-nbcr'); if (!key) { key = String(seen.n++); el.setAttribute('data-nbcr', key); }
      if (seen.done[key]) continue;
      var stack = document.elementsFromPoint(cx, cy);
      // the element itself (or its own child) must be hit at that point —
      // otherwise it is clipped away or covered there, and not drawn at all
      var k = -1;
      for (var j = 0; j < stack.length; j++) if (stack[j] === el || el.contains(stack[j])) { k = j; break; }
      if (k < 0) continue;
      while (k + 1 < stack.length && el.contains(stack[k + 1])) k++;
      if (stack[k] !== el) { var kk = stack.indexOf(el); if (kk > k) k = kk; }
      // is it really drawn? an ancestor at opacity 0 hides it
      var hid = false; for (var a = el; a; a = a.parentElement) { if (+getComputedStyle(a).opacity === 0) { hid = true; break; } }
      if (hid) continue;
      seen.done[key] = 1;
      var layers = [], opaque = null, src = [], qFirst = -1;
      for (var q = k; q < stack.length; q++) {
        var nl = layers.length;
        // pseudo-elements paint too (a pill's face can be its ::before);
        // they are read as layers above their element's own background
        ['::after', '::before'].forEach(function(ps){
          var p = getComputedStyle(stack[q], ps);
          if (!p || p.content === 'none' || p.display === 'none' || +p.opacity === 0) return;
          // only a pseudo that COVERS its element is a face under the text; a
          // thin one beside it (the rules either side of INTRODUCTION) is not
          var ob = stack[q].getBoundingClientRect();
          if (!/absolute|fixed/.test(p.position) || parseFloat(p.width) < .9 * ob.width
              || parseFloat(p.height) < .9 * ob.height) return;
          var pst = p.backgroundImage !== 'none' ? stops(p.backgroundImage) : [];
          var pbc = rgba(p.backgroundColor);
          if (pst.length) { layers.push(pst); src.push(name(stack[q]) + ps + '[img]'); }
          if (pbc && pbc[3] > 0) { layers.push([pbc]); src.push(name(stack[q]) + ps); }
        });
        var s = getComputedStyle(stack[q]);
        var st = s.backgroundImage !== 'none' ? stops(s.backgroundImage) : [];
        var bc = rgba(s.backgroundColor);
        if (st.length) { layers.push(st); src.push(name(stack[q]) + '[img]'); }
        if (bc && bc[3] > 0) {
          if (bc[3] >= 1) { if (qFirst < 0) qFirst = q; opaque = bc; src.push(name(stack[q])); break; }
          layers.push([bc]); src.push(name(stack[q]) + '[a]');
        }
        if (qFirst < 0 && layers.length > nl) qFirst = q;
        // 2026-09-27c — THE PANEL IS AN OVERLAY (STRUKTUR §4, since 27b). What
        // lies under it is whatever part of the document scrolls past, so the
        // ground under the rail is not the one point below this label but the
        // WORST of every surface the document paints (grounds, collected per
        // skin x brightness). The face of the rail has been laid on already.
        if (grounds && stack[q].classList && stack[q].classList.contains('nbrail') && stack[q].closest('#nbpanel-root')) {
          if (qFirst < 0) qFirst = q; opaque = 'grounds'; src.push(name(stack[q]) + ' < GROUNDS(' + grounds.length + ')'); break;
        }
      }
      if (!opaque) opaque = [255, 255, 255, 1];
      var cands = opaque === 'grounds' ? grounds.slice() : [opaque];
      for (var li = layers.length - 1; li >= 0; li--) {
        var nx = [];
        cands.forEach(function(c){ layers[li].forEach(function(t){ nx.push(over(t, c)); }); });
        cands = nx.slice(0, 4096);
      }
      // opacity is ink too: a label at opacity .75 is drawn 25 % lighter.
      // Multiply every opacity from the text up to the first surface under it.
      var surf = stack[qFirst] || null, op = 1;
      for (var a2 = el; a2 && a2 !== surf && !(surf && a2.contains(surf)); a2 = a2.parentElement)
        op *= +getComputedStyle(a2).opacity;
      var fg = rgba(cs.color), worst = null;
      fg = [fg[0], fg[1], fg[2], fg[3] * op];
      cands.forEach(function(c){ var f = fg[3] < 1 ? over(fg, c) : fg; var v = cr(f, c);
        if (!worst || v < worst.r) worst = {r: v, bg: hex(c), fg: hex(f)}; });
      res.push({t: txt.slice(0, 40), el: name(el), r: Math.round(worst.r * 100) / 100, fg: worst.fg, bg: worst.bg,
                on: src.slice(0, 3).join(' < '), n: cands.length});
    }
  });
  return res;
}"""
# every surface the notebook paints, as colours a panel can lie over: opaque
# backgrounds, every gradient stop, each composed over the page (and the page's
# texture stops over the page). Used by --overlay and by lab_marks.py.
GROUNDS_JS = r"""() => {
  function rgba(s){ if (!s) return null; var k = s.match(/color\(srgb ([^)]+)\)/); if (k) { var q = k[1].split(/[ \/]+/).filter(Boolean).map(parseFloat); return [q[0]*255, q[1]*255, q[2]*255, q.length > 3 ? q[3] : 1]; } var m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function stops(img){ var out = [], re = /rgba?\([^)]+\)|color\(srgb [^)]+\)/g, m; while ((m = re.exec(img))) out.push(rgba(m[0])); return out; }
  function over(f, b){ var a = f[3]; return [f[0]*a + b[0]*(1-a), f[1]*a + b[1]*(1-a), f[2]*a + b[2]*(1-a), 1]; }
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var sc = P.querySelector('.jp-WindowedPanel-outer'), scs = getComputedStyle(sc);
  var page = rgba(scs.backgroundColor); if (!page || page[3] < 1) page = rgba(getComputedStyle(P.querySelector('.jp-Notebook')).backgroundColor) || [255,255,255,1];
  if (page[3] < 1) page = over(page, [255,255,255,1]);
  var seen = {}, out = [];
  function add(c, why){ if (!c) return; if (c[3] < 1) c = over(c, page); var k = c.slice(0,3).map(Math.round).join(',');
    if (!seen[k]) { seen[k] = why; out.push(c.slice(0,3).map(Math.round).concat([1])); } }
  add(page, 'page');
  if (scs.backgroundImage !== 'none') stops(scs.backgroundImage).forEach(function(c){ add(c, 'texture'); });
  P.querySelectorAll('.jp-Notebook *').forEach(function(e){
    var cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility !== 'visible') return;
    var r = e.getBoundingClientRect(); if (r.width < 24 || r.height < 24) return;   // under the 6-px blur, anything smaller is smeared into its neighbours (a 24-px band keeps 95 % of its colour) — the grounds are what can reach the panel at full strength
    var bc = rgba(cs.backgroundColor); if (bc && bc[3] > 0.05) add(bc, 'bg');
    if (cs.backgroundImage !== 'none' && !/url\(/.test(cs.backgroundImage)) stops(cs.backgroundImage).forEach(function(c){ if (c[3] > 0.05) add(c, 'img'); });
  });
  return out;
}"""

# marks on the panel: the mark's own fill and edge against the worst ground under
# the panel face — reported, and flagged under 3:1 (a mark is not text)
MARKS_JS = r"""(grounds) => {
  function rgba(s){ if (!s) return null; var k = s.match(/color\(srgb ([^)]+)\)/); if (k) { var q = k[1].split(/[ \/]+/).filter(Boolean).map(parseFloat); return [q[0]*255, q[1]*255, q[2]*255, q.length > 3 ? q[3] : 1]; } var m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function over(f, b){ var a = f[3]; return [f[0]*a + b[0]*(1-a), f[1]*a + b[1]*(1-a), f[2]*a + b[2]*(1-a), 1]; }
  function lin(v){ v /= 255; return v <= .04045 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }
  function L(c){ return .2126*lin(c[0]) + .7152*lin(c[1]) + .0722*lin(c[2]); }
  function cr(a, b){ var x = L(a), y = L(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
  var rail = document.querySelector('#nbpanel-root .nbrail'); if (!rail) return [];
  var face = rgba(getComputedStyle(rail, '::before').backgroundColor), rb = rgba(getComputedStyle(rail).backgroundColor);
  var under = grounds.map(function(g){ var c = g; if (rb && rb[3] > 0) c = over(rb, c); if (face && face[3] > 0) c = over(face, c); return c; });
  var out = [];
  document.querySelectorAll('#nbpanel-root .nbmap-node:not(.nbgone)').forEach(function(n){
    var m = n.querySelector('.nbrail-dot,.nbcodemark,.nbchapdot,.nbvizmark,.nbsect,.nbsubdot'); if (!m) return;
    var cs = getComputedStyle(m), r = m.getBoundingClientRect(); if (cs.display === 'none' || r.width === 0) return;
    var op = 1; for (var a = m; a && a.id !== 'nbpanel-root'; a = a.parentElement) op *= +getComputedStyle(a).opacity;
    if (op === 0) return;
    var parts = [rgba(cs.backgroundColor)]; if (parseFloat(cs.borderTopWidth) >= 1) parts.push(rgba(cs.borderTopColor));
    var best = 0, worstG = null;
    parts.forEach(function(c){ if (!c || c[3] === 0) return; var w = 1e9;
      under.forEach(function(g){ var v = cr(over([c[0],c[1],c[2],c[3]*op], g), g); if (v < w) w = v; }); if (w > best) best = w; });
    out.push({mark: n.className.replace('nbjump nbmap-node ', '') + ' ' + m.className, cr: Math.round(best * 100) / 100});
  });
  return out;
}"""

SET_JS = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t);
  window.__nbApplySkin(); window.__nbApplyTheme(); }"""
SCROLL_JS = """(y) => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var sc = P.querySelector('.jp-WindowedPanel-outer'); if (y === 'max') return [sc.scrollHeight, sc.clientHeight];
  sc.scrollTop = y; return sc.scrollTop; }"""
EXPAND_JS = """() => { var n = 0; document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-contents.lm-mod-hidden').forEach(function(c){
  if (c.closest('.jupyter-widget-Collapse-contents.lm-mod-hidden') !== c) return;
  var h = c.parentElement.querySelector(':scope > .jupyter-widget-Collapse-header'); if (h) { h.click(); n++; } }); return n; }"""

def sweep_all(pg, skins, themes, open_panel=False, overlay=False, marks_out=None):
    out = {}
    for sk in skins:
        for th in themes:
            pg.evaluate(SET_JS, [sk, th]); pg.wait_for_timeout(700)
            H, ch = pg.evaluate(SCROLL_JS, 'max')
            seen = {"n": 0, "done": {}}; rows = []
            if overlay:
                seen["grounds"] = pg.evaluate(GROUNDS_JS)
                if marks_out is not None:
                    marks_out["%s/%s" % (sk, th)] = pg.evaluate(MARKS_JS, seen["grounds"])
            pg.evaluate("() => document.querySelectorAll('[data-nbcr]').forEach(function(e){ e.removeAttribute('data-nbcr'); })")
            # every element hit-testable while measuring: pointer-events:none
            # would drop a painted surface out of elementsFromPoint
            # 2026-09-27c: `*` alone LOST to `#nbpanel-root.vert .nbrail{pointer-events:none!important}`
            # (27b) — the rail fell out of the hit test and every panel name was measured
            # against the document under it. Two IDs outrank it.
            pg.evaluate("() => { var s = document.createElement('style'); s.id = 'nbcr-pe'; s.textContent = '*,#nbpanel-root#nbpanel-root,#nbpanel-root#nbpanel-root *{pointer-events:auto!important}'; document.head.appendChild(s); }")
            y = 0
            while True:
                pg.evaluate(SCROLL_JS, y); pg.wait_for_timeout(250)
                r = pg.evaluate("(s) => { var f = " + SWEEP_JS + "; var o = f(s); return [o, s]; }", seen)
                rows += r[0]; seen = r[1]
                if y >= H - ch: break
                y = min(y + int(ch * .8), H - ch)
            pg.evaluate("() => { var s = document.getElementById('nbcr-pe'); if (s) s.remove(); }")
            out["%s/%s" % (sk, th)] = rows
    return out

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    nb = sys.argv[1]; dest = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx, pg, errs = open_nb(b, BASE, nb)
        pg.evaluate(EXPAND_JS); pg.wait_for_timeout(800); pg.evaluate(EXPAND_JS); pg.wait_for_timeout(800)
        if "--open-panel" in sys.argv:
            # a click on the grip without dragging jumps to the wide end (OBERFLAECHE §4)
            pg.click("#nbpanel-root .nbgrip"); pg.wait_for_timeout(1200)
            print("panel width:", pg.evaluate("() => Math.round(document.querySelector('#nbpanel-root .nbrail, #nbpanel-root .nbmap').getBoundingClientRect().width)"))
        ov = "--overlay" in sys.argv; marks = {}
        res = sweep_all(pg, ["minimal", "cyber", "fairy"], ["light", "dark"], overlay=ov, marks_out=marks)
        if ov:
            # only the panel's own texts are the overlay case; the document's are as before
            for k, ms in marks.items():
                lo = [m for m in ms if m["cr"] < 3]
                print("%-14s marks %3d  min %.2f  under 3: %d  under 4.5: %d" % (k, len(ms), min([m["cr"] for m in ms] or [0]), len(lo), len([m for m in ms if m["cr"] < 4.5])))
                for m in sorted(ms, key=lambda m: m["cr"])[:4]: print("    %.2f  %s" % (m["cr"], m["mark"][:70]))
        bad = 0
        for k, rows in res.items():
            low = [r for r in rows if r["r"] < 4.5]; bad += len(low)
            mn = min(rows, key=lambda r: r["r"]) if rows else None
            print("%-14s %4d texts  min %.2f  under 4.5: %d" % (k, len(rows), mn["r"] if mn else 0, len(low)))
            for r in sorted(low, key=lambda r: r["r"])[:12]:
                print("    %.2f  %s on %s  %-28s %s  | %s" % (r["r"], r["fg"], r["bg"], r["el"][:28], r["t"][:30], r["on"][:90]))
        if errs: print("console:", errs[:5])
        if dest: json.dump({"texts": res, "marks": marks} if ov else res, open(dest, "w"), indent=0)
        sys.exit(1 if bad else 0)
