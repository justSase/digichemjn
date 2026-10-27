"""Real-JupyterLab measurement for E10.9 (2026-09-30): the knob's tooltip.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). An init script
counts the titles every knob (.nbgrip) is born with (the Python markup, before
the panel script touches it) and every later change of its title.
Pass: every knob is born with the panel script's text (19-rail-title-sync GT),
nothing swaps it, and the knob on screen carries it.

    python3 tests/lab_griptitle.py <notebook.ipynb> <out.json>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
nb, out = sys.argv[1:3]
GT = "drag up or down to move the reading height, left or right to widen or narrow the timeline"
HOOK = r"""
window.__gt = {born: {}, swaps: 0, swapTo: {}};
new MutationObserver(function(ms){
  var G = window.__gt;
  ms.forEach(function(m){
    if (m.type === 'attributes') {
      if (m.target.classList && m.target.classList.contains('nbgrip')) {
        G.swaps++; var t = m.target.getAttribute('title'); G.swapTo[t] = (G.swapTo[t] || 0) + 1; }
      return;
    }
    [].forEach.call(m.addedNodes || [], function(n){
      if (n.nodeType !== 1) return;
      var gs = n.matches('.nbgrip') ? [n] : [].slice.call(n.querySelectorAll('.nbgrip'));
      gs.forEach(function(g){ var t = g.getAttribute('title'); G.born[t] = (G.born[t] || 0) + 1; });
    });
  });
}).observe(document, {subtree: true, childList: true, attributes: true, attributeFilter: ['title']});
"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    # every context the harness opens gets the hook before the page loads
    _nc = b.new_context
    b.new_context = lambda **kw: (lambda c: (c.add_init_script(HOOK), c)[1])(_nc(**kw))
    ctx, pg, errs = fresh(b, BASE, nb, ROOT)
    seq = pg.evaluate("() => window.__gt")
    now = pg.evaluate("() => { var g = document.querySelector('#nbpanel-root .nbgrip') || document.querySelector('.nbgrip'); return g ? g.getAttribute('title') : null; }")
    pg.screenshot(path=os.path.splitext(out)[0] + ".png")
    b.close()
res = {"born_with": seq["born"], "swaps": seq["swaps"], "swapped_to": seq["swapTo"], "title_now": now}
res["pass"] = list(seq["born"]) == [GT] and seq["swaps"] == 0 and now == GT
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res, indent=1))
sys.exit(0 if res["pass"] else 1)
