"""E23.12 — the conductor's regress test for the JS point E23.12 (2026-10-06;
Kategorie Applikation, Prüfwerkzeug). Module of tests/regress/run.py.

  D23.12  the code in a coding field stays coloured when the field loses focus:
          Coding 1 opened through its mark, code typed into the field (keyword,
          number, string, comment), then a click outside the field. Read off the
          page: the overlay (.nbedov-hl) is drawn (display, visibility, opacity,
          box) and its spans for keyword / number / string have three different
          computed colours; the field's own text is not invisible without it
          (transparent glyphs only with a drawn overlay). The same while typing
          (in focus) and after the click outside (out of focus).

A test that cannot reach its precondition returns False ("BAD …"), never True."""
import os, importlib.util
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_js_e22_for_dir12", os.path.join(_HERE, "js_e22.py"))
J = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(J)

CODE = 'if x:\n    y = 42  # note\n    s = "ab"'
READ = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var ta = window.__d12ta; if (!ta || !ta.isConnected) return {err: 'no field'};
  var wrap = ta.closest('.codearea'), pre = wrap && wrap.querySelector('.nbedov-hl');
  var tc = getComputedStyle(ta), fill = tc.webkitTextFillColor || tc.color;
  var tr = function(c){ return /rgba\(.*,\s*0\)$/.test(c) || c === 'transparent'; };
  var out = {focus: document.activeElement === ta, val: ta.value.slice(0, 40), taInk: fill, taHidden: tr(fill) || tr(tc.color),
             on: !!(wrap && wrap.classList.contains('on'))};
  if (!pre) { out.pre = null; return out; }
  var pc = getComputedStyle(pre), pr = pre.getBoundingClientRect();
  out.pre = {disp: pc.display, vis: pc.visibility, op: +pc.opacity, h: Math.round(pr.height), z: pc.zIndex};
  out.drawn = pc.display !== 'none' && pc.visibility === 'visible' && +pc.opacity > 0.5 && pr.height > 4;
  var col = {};
  [].forEach.call(pre.querySelectorAll('span'), function(s){ var t = s.textContent.trim();
    var c = getComputedStyle(s), r = s.getBoundingClientRect();
    if ((t === 'if' || t === '42' || t === '"ab"' || t === '# note') && r.width > 0 && c.visibility === 'visible') col[t] = c.color; });
  out.col = col; return out; }"""
FIND = r"""(i) => { var h = document.getElementById('nbpanel-root'), n = h.querySelectorAll('.nbmap-node')[i];
  var A = document.getElementById(n.getAttribute('data-target'));
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var tas = [].filter.call(P.querySelectorAll('.jp-OutputArea .codearea textarea'), function(t){
    return (A.compareDocumentPosition(t) & 4) && t.getBoundingClientRect().height > 10; });
  window.__d12ta = tas[0] || null; if (!tas[0]) return null;
  var r = tas[0].getBoundingClientRect(); return [r.left + 30, r.top + 12, tas[0].value.length]; }"""

def _ok(s):
    c = s.get("col") or {}
    cs = [c.get("if"), c.get("42"), c.get('"ab"')]
    colours = all(cs) and len(set(cs)) == 3
    return bool(s.get("drawn")) and colours and not (s.get("taHidden") and not s.get("drawn"))

def colour_kept(pg, ctx):
    J._calm(pg); pg.wait_for_timeout(2500)
    nodes = pg.evaluate(r"""()=>[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).map(function(n,i){
        return [i, n.classList.contains('codetask') && !n.classList.contains('nbgone') && !n.classList.contains('locked')];})
        .filter(function(x){return x[1];}).map(function(x){return x[0];})""")
    if not nodes: return False, "BAD no open coding mark"
    J._click_node(pg, nodes[0]); pg.wait_for_timeout(2600)
    xy = pg.evaluate(FIND, nodes[0])
    if not xy: return False, "BAD no code field after the coding mark"
    pg.mouse.click(xy[0], xy[1]); pg.wait_for_timeout(300)
    pg.keyboard.press("Control+a"); pg.keyboard.press("Delete")
    for line in CODE.split("\n"):
        pg.keyboard.type(line.lstrip(" "), delay=8)
        pg.keyboard.press("Enter") if line is not CODE.split("\n")[-1] else None
    pg.wait_for_timeout(800)
    typing = pg.evaluate(READ)
    # a click outside the field: on the page beside the document text
    box = pg.evaluate("() => { var r = window.__d12ta.getBoundingClientRect(); return [r.left, r.top, r.bottom]; }")
    pg.mouse.click(box[0] + 20, max(box[1] - 60, 120)); pg.wait_for_timeout(600)
    if pg.evaluate("() => document.activeElement === window.__d12ta"):
        pg.keyboard.press("Escape"); pg.evaluate("() => window.__d12ta.blur()"); pg.wait_for_timeout(400)
    blur = pg.evaluate(READ)
    pg.wait_for_timeout(2000)                       # a scan of the overlay (1.5 s) has run since
    later = pg.evaluate(READ)
    if blur.get("focus"): return False, "BAD the field kept the focus: %s" % blur
    if "x:" not in (typing.get("val") or ""): return False, "BAD typing did not reach the field: %s" % typing
    bad = []
    for tag, s in (("typing", typing), ("after blur", blur), ("2 s later", later)):
        if not _ok(s): bad.append("%s: drawn %s, colours %s, field glyphs hidden %s (pre %s)" % (
            tag, s.get("drawn"), s.get("col"), s.get("taHidden"), s.get("pre")))
    det = " · ".join("%s: drawn %s %s" % (t, s.get("drawn"), sorted(set((s.get("col") or {}).values()))) for t, s in
                     (("typing", typing), ("blur", blur), ("later", later)))
    pg.keyboard.press("Escape")
    return (not bad), ("; ".join(bad) + " | " if bad else "") + det

TESTS = [("D23.12 code stays coloured out of focus", colour_kept)]
