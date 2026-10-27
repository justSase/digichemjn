"""E10 Teil 4 — MODELING ON THE STANDARD OF COMPLEX, in a real JupyterLab
(2026-09-30, Werkstatt Python: Inhalt + Struktur + Applikation).

    python3 tests/lab_modeling.py <Introduction_to_Modeling_v….ipynb> [out.png]

A fresh copy is opened and run (1400 × 900). Asserts:
  1  two cells; our panel is there (`#nbpanel-root .nbmap`), the notebook
     panel carries data-digichem="1"
  2  the timeline: first mark = the title, named after the card
     ("Introduction to Modeling"); 9 chapter marks, 11 exercise marks,
     9 coding marks, 9 figure marks; the end mark and the YOC mark
  3  formulas are inline SVG (`svg.imath/.dmath`, locked chapters are not
     built yet, so few), no <img> formula
  4  chapter 1 is open and its figure is drawn (inline SVG, 660 px)
  5  exercise 1 by hand: the reader's own numbers are read off the page,
     the right answer typed into "orders =", Check → ✓ verdict (.nbok),
     the mark t1 turns data-state="done", chapter 2 opens (one lock fewer)
  6  hints: "Hint 1 of 2" shows exactly one step, and it does not state the result
  7  4 styles × light/dark: switched in place, no page error
  8  own data: no figure drawn at build; "Analyse ▶" draws both and the fit
exit 0 = MODELING OK."""
import sys, os, re, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
BASE, LAB = ensure_lab(BASE)
SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else None

MAP_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var h = document.querySelector('#nbpanel-root .nbmap');
  var n = h ? [].slice.call(h.querySelectorAll('.nbmap-node')) : [];
  var cnt = function(re){ return n.filter(function(a){ return re.test(' ' + a.className + ' '); }).length; };
  var first = n[0], lab = first && first.querySelector('.nbmap-lab');
  return {cells: P.querySelectorAll('.jp-Cell').length, panel: !!h, dc: P.getAttribute('data-digichem'),
          first: first ? first.className : null, firstLab: lab ? lab.textContent.trim() : null,
          chap: cnt(/ chap /), task: cnt(/ task /), code: cnt(/ codetask /), viz: cnt(/ viztask /),
          end: cnt(/ end /), yoc: cnt(/ cell /),
          svgMath: P.querySelectorAll('svg.imath, svg.dmath').length,
          imgMath: P.querySelectorAll('img.imath, img.dmath').length,
          locked: P.querySelectorAll('.acc-locked').length,
          t1: (h && h.querySelector('.nbmap-node.task[data-task="t1"]') || {getAttribute: function(){ return null; }}).getAttribute('data-state')};
}"""
CH1_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var box = [].slice.call(P.querySelectorAll('.widget-html')).filter(function(w){
    return /receptor binding event takes about/.test(w.textContent); })[0];
  if (!box) return {err: 'no exercise 1 text'};
  var m = box.textContent.match(/takes about\s*(\d+)\s*ms.*?over about\s*(\d+)\s*h/);
  var svg = [].slice.call(P.querySelectorAll('svg')).filter(function(s){ return s.getAttribute('width') === '660px'; });
  var ch1 = box.closest('.acc-chapter');
  return {fast: m ? +m[1] : null, slow: m ? +m[2] : null, figs660: svg.length,
          ch1open: ch1 ? !!ch1.querySelector(':scope > .jupyter-widget-Collapse > .jupyter-widget-Collapse-contents:not(.lm-mod-hidden)') : null};
}"""
SET_JS = r"""([lab, v]) => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var w = [].slice.call(P.querySelectorAll('.widget-text')).filter(function(w){
    var l = w.querySelector('label'); return l && l.textContent.trim() === lab; })[0];
  if (!w) return 'no box ' + lab;
  var i = w.querySelector('input'); i.focus(); i.value = String(v);
  i.dispatchEvent(new Event('input', {bubbles: true})); i.dispatchEvent(new Event('change', {bubbles: true}));
  i.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true})); i.blur();
  var up = w, b = null, k = 0;
  while (up && k < 10 && !b) { b = [].slice.call(up.querySelectorAll('button')).filter(function(x){
      return x.textContent.indexOf('Check answer') >= 0; })[0]; up = up.parentElement; k++; }
  if (!b) return 'no check button';
  b.setAttribute('data-lm', '1'); w.setAttribute('data-lmbox', '1');
  return 'ok';
}"""
VERDICT_JS = r"""() => {
  var b = document.querySelector('button[data-lm]'); if (!b) return null;
  var box = b.parentElement, k = 0, out = null;
  while (box && k < 6 && !out) {
    var outs = box.querySelectorAll('.jupyter-widgets-output-area, .widget-output');
    for (var i = 0; i < outs.length; i++) if (b.compareDocumentPosition(outs[i]) & 4) { out = outs[i]; break; }
    box = box.parentElement; k++;
  }
  var r = out && out.querySelector('.nbok, .nbwarn');
  return r ? r.className.split(' ')[0] + ': ' + r.textContent.trim().slice(0, 70) : '';
}"""
HINT_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var box = document.querySelector('[data-lmbox]');
  var ch = box && box.closest('.acc-chapter');
  var b = ch && [].slice.call(ch.querySelectorAll('button.nbhint-btn'))[0];
  if (!b) return {err: 'no hint button'};
  var d0 = b.textContent.trim(); b.click();
  return {d0: d0};
}"""
HINT2_JS = r"""() => {
  var box = document.querySelector('[data-lmbox]'); var ch = box && box.closest('.acc-chapter');
  var hs = ch ? [].slice.call(ch.querySelectorAll('.nbhint')) : [];
  var b = ch && ch.querySelector('button.nbhint-btn');
  return {n: hs.length, first: hs[0] ? hs[0].textContent.trim().slice(0, 40) : '', text: hs.map(function(h){ return h.textContent; }).join(' '),
          d1: b ? b.textContent.trim() : null};
}"""
SKIN_JS = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t);
  window.__nbApplySkin(); window.__nbApplyTheme(); }"""
BUSY_JS = "() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')"

fails, rows = [], []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx, pg, errs = fresh(b, BASE, SRC, LAB)
    perrs = []; pg.on("pageerror", lambda e: perrs.append(str(e)))
    pg.wait_for_timeout(1500)
    m = pg.evaluate(MAP_JS)
    rows.append("1 cells %d · panel %s · data-digichem %s" % (m["cells"], m["panel"], m["dc"]))
    if m["cells"] != 2 or not m["panel"] or m["dc"] != "1": fails.append("1: %s" % m)
    rows.append("2 first mark %r %r · chapters %d · exercises %d · coding %d · figures %d · end %d · YOC %d"
                % (m["first"], m["firstLab"], m["chap"], m["task"], m["code"], m["viz"], m["end"], m["yoc"]))
    if not m["first"] or " title" not in " " + m["first"] or m["firstLab"] != "Introduction to Modeling":
        fails.append("2: first mark %r %r, want the title 'Introduction to Modeling'" % (m["first"], m["firstLab"]))
    for k, want in (("chap", 9), ("task", 11), ("code", 9), ("viz", 9), ("end", 1), ("yoc", 1)):
        if m[k] != want: fails.append("2: %s marks %d, want %d" % (k, m[k], want))
    rows.append("3 formulas: svg %d · img %d" % (m["svgMath"], m["imgMath"]))
    if m["svgMath"] < 1 or m["imgMath"]: fails.append("3: formulas svg %d / img %d" % (m["svgMath"], m["imgMath"]))
    c = pg.evaluate(CH1_JS)
    rows.append("4 chapter 1 open %s · figures drawn (660 px SVG) %s · reader's numbers %s ms / %s h"
                % (c.get("ch1open"), c.get("figs660"), c.get("fast"), c.get("slow")))
    if c.get("err") or not c.get("ch1open") or not c.get("figs660"): fails.append("4: %s" % c)
    if c.get("fast") and c.get("slow"):
        want = math.log10(c["slow"] * 3.6e6 / c["fast"])
        lk0 = m["locked"]
        r = pg.evaluate(SET_JS, ["orders =", round(want, 3)])
        if r != "ok": fails.append("5: %s" % r)
        else:
            pg.evaluate("() => document.querySelector('button[data-lm]').click()")
            res = None
            for _ in range(60):
                pg.wait_for_timeout(250); res = pg.evaluate(VERDICT_JS)
                if res and pg.evaluate(BUSY_JS) == "idle": break
            pg.wait_for_timeout(2500)
            m2 = pg.evaluate(MAP_JS)
            rows.append("5 t1 = %.3f -> %s · mark t1 %s · locks %d -> %d" % (want, res, m2["t1"], lk0, m2["locked"]))
            if not res or not res.startswith("nbok"): fails.append("5: verdict %r" % res)
            if m2["t1"] != "done": fails.append("5: mark t1 data-state %r" % m2["t1"])
            if not m2["locked"] < lk0: fails.append("5: no lock opened (%d -> %d)" % (lk0, m2["locked"]))
            h = pg.evaluate(HINT_JS)
            pg.wait_for_timeout(1500)
            h2 = pg.evaluate(HINT2_JS)
            leak = ("%.2f" % want) in h2.get("text", "") or ("%.3f" % want) in h2.get("text", "")
            rows.append("6 hint button %r -> %d step(s) %r, next %r, states the result: %s"
                        % (h.get("d0"), h2["n"], h2["first"], h2["d1"], leak))
            if h.get("err") or h2["n"] != 1 or not h2["first"].startswith("Hint 1.") or leak:
                fails.append("6: hints %s %s" % (h, {k: v for k, v in h2.items() if k != "text"}))
    # 8  own data: nothing drawn at build; Analyse ▶ draws both figures and the fit
    r8 = pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
        var b = [].slice.call(P.querySelectorAll('button')).filter(function(x){ return /Analyse/.test(x.textContent); })[0];
        if (!b) return null; var ch = b.closest('.acc-chapter'); b.setAttribute('data-lm8', '1');
        return {before: ch.querySelectorAll('svg').length}; }""")
    if not r8: fails.append("8: no Analyse button")
    else:
        pg.evaluate("() => document.querySelector('button[data-lm8]').click()")
        for _ in range(60):
            pg.wait_for_timeout(250)
            if pg.evaluate(BUSY_JS) == "idle": break
        pg.wait_for_timeout(800)
        a8 = pg.evaluate("""() => { var ch = document.querySelector('button[data-lm8]').closest('.acc-chapter');
            return {svg: ch.querySelectorAll('svg').length, fit: /half-life = [0-9.]+ h/.test(ch.textContent)}; }""")
        rows.append("8 own data: figures before Analyse %d, after %d · fit line %s" % (r8["before"], a8["svg"], a8["fit"]))
        if r8["before"] != 0 or a8["svg"] < 2 or not a8["fit"]: fails.append("8: own data %s -> %s" % (r8, a8))
    for sk in ("minimal", "cyber", "retro", "fairy"):
        for th in ("light", "dark"):
            n0 = len(perrs)
            pg.evaluate(SKIN_JS, [sk, th]); pg.wait_for_timeout(500)
            if len(perrs) > n0: fails.append("7: %s/%s page error %s" % (sk, th, perrs[n0][:80]))
    rows.append("7 styles 4 × 2 switched · page errors %d · console errors %d" % (len(perrs), len([e for e in errs if e.startswith("console")])))
    if perrs: fails.append("page errors: %s" % perrs[:2])
    if OUT:
        pg.evaluate(SKIN_JS, ["minimal", "light"]); pg.wait_for_timeout(500)
        pg.evaluate("""() => [].forEach.call(document.querySelectorAll('.jp-toast-button, .jp-Notification-Toast button'),
            function(b){ if (b.textContent.trim() === 'No') b.click(); })""")
        pg.evaluate("() => { var w = document.querySelector('[data-lmbox]'); if (w) w.scrollIntoView({block: 'center'}); }")
        pg.wait_for_timeout(1500)
        pg.screenshot(path=OUT)
    ctx.close(); b.close()
kill_sessions(BASE)
print("\n".join(rows))
print("\n" + ("MODELING OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
