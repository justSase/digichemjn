"""Real-JupyterLab measurement for STRUKTUR K2.4 — what an exercise GENERATES
is centred like the rest of it. 2026-09-28b.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). A fresh copy
of the notebook; every exercise is opened through the kernel (t1…t7 solved on
both routes by a second kernel client, so no fold waits), every exercise part
is unfolded by a click on its header, and what the parts generate is made to
appear: every "Check" button pressed (empty or stub answer → feedback), every
hint button pressed once, one option of every quiz question clicked, the
"bring your own data" runner run.

Then, in every exercise part — the practice folds, the coding folds, the quiz
and "bring your own data" — its CENTRE is the middle of the fold's content
column (the column every exercise text is centred on), and every one of these
is measured against it (getBoundingClientRect):

  B  a box: an element with a visible border or a background of its own, or
     a form control (text area, field, button, select) — not inline, not
     spanning the whole column;
  R  a row: a flex row with two or more visible children (a pair of answer
     fields, a row of buttons) — the middle of what the children cover;
  T  a text block: a block element with text of its own — the middle of the
     lines its text covers (Range rectangles).

Criterion: |middle − centre| <= 2 px for every one, in every exercise part.

    python3 tests/lab_center.py <notebook> <out.json> [skin,...]
Exit 1 if a criterion fails."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from lab_marks import kexec
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
nb, out = sys.argv[1], sys.argv[2]
skins = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else [None]
TOL = 2.0
OPEN_ALL = r"""() => {
  var HDR = '.jupyter-widget-Collapse-header';
  var n = 0;
  [].forEach.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse'), function(c){
    if (c.classList.contains('jupyter-widget-Collapse-open')) return;
    if (c.closest('.acc-viz')) return;                 // figures are not exercise parts
    var h = c.querySelector(HDR); if (!h || h.getBoundingClientRect().height < 2) return;
    h.click(); n++; });
  return n; }"""
PARTS = r"""() => {
  // the exercise parts: practice folds, coding folds, and the two sections that
  // ARE exercises (their anchors are the targets of the q1 / b1 marks)
  var P = [];
  [].forEach.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .acc-practice > .jupyter-widget-Collapse, .jp-NotebookPanel:not(.lm-mod-hidden) .acc-code > .jupyter-widget-Collapse'),
    function(c){ P.push(c); });
  ['q1', 'b1'].forEach(function(k){
    var nd = document.querySelector('#nbpanel-root .nbmap-node.task[data-task="' + k + '"]');
    var id = nd && nd.getAttribute('data-target'); var s = id && document.getElementById(id);
    if (!s) return;
    var host = s; while (host.parentElement && !(host.parentElement.classList.contains('widget-vbox') ||
           host.parentElement.classList.contains('jupyter-widget-vbox'))) host = host.parentElement;
    var sib = host.nextElementSibling, j = 0;
    while (sib && j++ < 8) { var c = sib.classList.contains('jupyter-widget-Collapse') ? sib
             : sib.querySelector('.jupyter-widget-Collapse'); if (c) { P.push(c); break; } sib = sib.nextElementSibling; }
  });
  return P; }"""
TRIGGER = r"""() => {
  var parts = (%s)(), n = {check: 0, hint: 0, quiz: 0, run: 0};
  parts.forEach(function(c){
    [].forEach.call(c.querySelectorAll('button'), function(b){
      var t = (b.textContent || '').trim();
      if (b.getBoundingClientRect().width < 2) return;
      if (/^\W*check/i.test(t)) { b.click(); n.check++; }
      else if (b.classList.contains('nbhint-btn') || /hint/i.test(t)) { b.click(); n.hint++; }
      else if (/^run/i.test(t)) { b.click(); n.run++; }
    });
    // jupyterquiz: the first option of each question
    [].forEach.call(c.querySelectorAll('.Quiz .Answer'), function(q){
      var o = q.querySelector('.MCButton');
      if (o && !q.__nbClicked) { q.__nbClicked = true; o.click(); n.quiz++; }
    });
  });
  return n; }""" % PARTS
MEASURE = r"""(tol) => {
  var parts = (%s)(), res = [];
  var clear = function(c){ return /rgba\(0, 0, 0, 0\)|transparent/.test(c); };
  parts.forEach(function(c){
    var body = c.querySelector('.jupyter-widget-Collapse-contents'); if (!body) return;
    var br = body.getBoundingClientRect(); if (br.width < 10 || br.height < 4) return;
    var mid = (br.left + br.right) / 2;
    var hd = c.querySelector('.jupyter-widget-Collapse-header');
    var name = (hd && hd.textContent || '').trim().slice(0, 30);
    var chap = c.closest('.acc-chapter'); var ch = chap && chap.querySelector('.jupyter-widget-Collapse-header');
    name = (ch ? ch.textContent.trim().slice(0, 22) + ' / ' : '') + name;
    var row = {part: name, mid: +mid.toFixed(1), n: {B: 0, R: 0, T: 0}, off: []};
    var own = function(e){ return e.closest('.jupyter-widget-Collapse') === c; };
    var vis = function(e){ var cs = getComputedStyle(e); if (cs.visibility !== 'visible' || cs.display === 'none') return false;
      var r = e.getBoundingClientRect(); return r.width >= 4 && r.height >= 4; };
    var note = function(kind, e, m, w){
      row.n[kind]++;
      var d = m - mid;
      if (Math.abs(d) > tol) row.off.push(kind + ' ' + (e.tagName + '.' + String(e.className).split(' ').slice(0, 2).join('.')).slice(0, 48)
          + ' d=' + d.toFixed(1) + ' w=' + Math.round(w) + ' "' + (e.textContent || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 28) + '"');
    };
    // a row stands for what is in it: the answer pair, a label with its
    // field and readout, a row of buttons — its parts are not centred one by
    // one, the row is. So only the OUTERMOST rows are measured, and nothing
    // inside one.
    // …and so does a GROUP of options: a list of radio options, the quiz's
    // grid of answers. The group is centred as a whole (the options stay
    // left-aligned under one another); its middle is the middle of what the
    // reader sees in it — the words and the controls, not the stretched box.
    var isRow = function(e){ var cs = getComputedStyle(e);
      if (e.classList.contains('widget-radio-box')) return true;
      if (/grid/.test(cs.display) && [].filter.call(e.children, vis).length > 1) return true;
      return /flex/.test(cs.display) && !/column/.test(cs.flexDirection) && [].filter.call(e.children, vis).length > 1; };
    var seen = function(g){
      var L = 1e9, R = -1e9;
      var take = function(q){ if (q.width > 0.5 && q.height > 0.5) { L = Math.min(L, q.left); R = Math.max(R, q.right); } };
      if (!g.classList.contains('widget-radio-box')) {
        [].filter.call(g.children, vis).forEach(function(k){ take(k.getBoundingClientRect()); });
      } else {
        [].forEach.call(g.querySelectorAll('input, button'), function(k){ if (vis(k)) take(k.getBoundingClientRect()); });
        var rg = document.createRange(); rg.selectNodeContents(g); [].forEach.call(rg.getClientRects(), take);
      }
      return [L, R];
    };
    var rows = [].filter.call(body.querySelectorAll('*'), function(e){ return own(e) && vis(e) && isRow(e); });
    var inRowOf = function(e){ for (var i = 0; i < rows.length; i++) if (rows[i] !== e && rows[i].contains(e)) return true; return false; };
    [].forEach.call(body.querySelectorAll('*'), function(e){
      if (!own(e) || !vis(e)) return;
      if (inRowOf(e)) return;
      if (e.closest('mjx-container, .MathJax, svg, .jp-RenderedLatex math')) return;
      var cs = getComputedStyle(e), r = e.getBoundingClientRect();
      if (/^inline/.test(cs.display) && !/^(TEXTAREA|INPUT|BUTTON|SELECT)$/.test(e.tagName)) return;
      var full = r.width > br.width - 4;
      // B — boxes and controls
      var boxy = /^(TEXTAREA|INPUT|BUTTON|SELECT|IMG|CANVAS)$/.test(e.tagName)
        || (parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none' && !clear(cs.borderTopColor))
        || (parseFloat(cs.borderLeftWidth) > 0 && cs.borderLeftStyle !== 'none' && !clear(cs.borderLeftColor))
        || !clear(cs.backgroundColor);
      var inRow = function(){ var p = e.parentElement; if (!p) return false; var ps = getComputedStyle(p);
        if (!/flex/.test(ps.display) || /column/.test(ps.flexDirection)) return false;
        return [].filter.call(p.children, vis).length > 1; };
      if (boxy && !full && !inRow()) note('B', e, (r.left + r.right) / 2, r.width);
      // R — rows and groups (only the outermost: the others were skipped)
      if (isRow(e)) {
        var lr = seen(e);
        if (lr[1] > lr[0] && lr[1] - lr[0] < br.width - 4) note('R', e, (lr[0] + lr[1]) / 2, lr[1] - lr[0]);
        return;
      }
      // T — text of its own
      var txt = [].some.call(e.childNodes, function(t){ return t.nodeType === 3 && t.textContent.trim().length > 1; });
      if (txt && !/^(TEXTAREA|INPUT|BUTTON|SELECT|OPTION)$/.test(e.tagName) && !e.closest('button, textarea, select')) {
        var rg = document.createRange(); rg.selectNodeContents(e);
        var rs = [].filter.call(rg.getClientRects(), function(q){ return q.width > 0.5 && q.height > 0.5; });
        if (rs.length) {
          var L2 = 1e9, R2 = -1e9; rs.forEach(function(q){ L2 = Math.min(L2, q.left); R2 = Math.max(R2, q.right); });
          // a code block is set flush left on purpose: only its box counts
          if (!/^(PRE|CODE)$/.test(e.tagName) && !e.closest('pre, .cm-editor')) note('T', e, (L2 + R2) / 2, R2 - L2);
        }
      }
    });
    res.push(row);
  });
  return res; }""" % PARTS
res = {}; fails = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = None; errs = []
    for sk in skins:
        ctx, pg, e1 = fresh(b, BASE, nb, ROOT, ctx)
        pg.set_viewport_size({"width": 1400, "height": int(os.environ.get("DIGICHEM_H", "900"))})
        pg.wait_for_timeout(1500)
        try: pg.click(".jp-toast-buttonBar button:has-text('No')", timeout=1500)
        except Exception: pass
        if sk:
            pg.evaluate("(s)=>{ window.__nbStore.set('digichemjn.skin.v1', s); window.__nbApplySkin && window.__nbApplySkin(); }", sk)
            pg.wait_for_timeout(1500)
        kexec("for _k in ['t1','t2','t3','t4','t5','t6','t7']:\n    task_solved(_k); task_code_solved(_k)\n")
        pg.wait_for_timeout(3000)
        for _ in range(6):
            if not pg.evaluate(OPEN_ALL): break
            pg.wait_for_timeout(1500)
        pg.wait_for_timeout(2000)
        trig = pg.evaluate(TRIGGER); pg.wait_for_timeout(4000)
        # a second pass: a fold rendered late (the quiz) gets its clicks too
        t2 = pg.evaluate(TRIGGER); pg.wait_for_timeout(3000)
        trig = {k: [trig[k], t2[k]] for k in trig}
        key = sk or "default"
        rows = pg.evaluate(MEASURE, TOL)
        res[key] = {"trigger": trig, "parts": rows}
        if len(rows) < 14:                     # E25.l: no quiz, no own data (behauptete bisher: 16)
            fails.append("%s: only %d exercise parts found (7 practice + 7 coding)" % (key, len(rows)))
        for r in rows:
            if sum(r["n"].values()) == 0:
                fails.append("%s %s: nothing measured" % (key, r["part"]))
            for o in r["off"]:
                fails.append("%s %s: %s" % (key, r["part"], o))
        errs += e1
    res["errs"] = errs
    if errs: fails.append("console: %s" % errs[:3])
    ctx.close(); b.close()
res["fails"] = fails
json.dump(res, open(out, "w"), indent=1)
for k, v in res.items():
    if isinstance(v, dict) and "parts" in v:
        tot = {"B": 0, "R": 0, "T": 0}
        for r in v["parts"]:
            for kk in tot: tot[kk] += r["n"][kk]
        print("%-8s parts %d | measured boxes %d, rows %d, texts %d | off centre %d | triggered %s"
              % (k, len(v["parts"]), tot["B"], tot["R"], tot["T"], sum(len(r["off"]) for r in v["parts"]), v["trigger"]))
for f in fails[:80]: print("FAIL", f)
if len(fails) > 80: print("… and %d more" % (len(fails) - 80))
print("CENTRE OK" if not fails else "CENTRE: %d failures" % len(fails))
sys.exit(1 if fails else 0)
