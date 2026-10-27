"""Real-JupyterLab measurement for E10.8 (2026-09-30): the formulas look the same.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). Runs the notebook,
with code at the end of its mega-cell (probe copy only) that draws every formula the build
typeset — imath at fs 16, dmath at fs 20, as the chapters do — and reads, per formula:
  box  — getBoundingClientRect of the <svg> (px)
  ink  — getBBox of its content (viewBox units; the glyphs and rules drawn)
and saves a screenshot of the sheet. Two notebooks → compared formula by formula.

    python3 tests/lab_math.py <old.ipynb> <new.ipynb> <out.json> [sheet-prefix]
Exit 1 if a formula's box differs by > 0.5 px or its ink by > 0.1 px, or the
counts differ."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
old, new, out = sys.argv[1:4]
pre = sys.argv[4] if len(sys.argv) > 4 else "math"
CELL = r"""
import re as _r
_K = %r
_h = []
for _k in _K:
    _fs, _t = _k.split("|", 1)
    _h.append(imath(_t[1:-1]) if _fs == "16" else dmath(_t))
from IPython.display import HTML as _H
display(_H('<div id="nbmathsheet" style="background:#fff;color:#33475b;padding:8px;line-height:1.6">'
           + "".join('<span style="display:inline-block;margin:0 14px 8px 0">%%s</span>' %% x for x in _h)
           + '</div>'))
"""
READ = r"""() => {
  var sh = document.getElementById('nbmathsheet');
  sh.scrollIntoView();
  return [].slice.call(sh.querySelectorAll('svg')).map(function(c){
    var r = c.getBoundingClientRect(), bb = c.getBBox();
    return {cls: c.getAttribute('class'), vb: c.getAttribute('viewBox'), w: r.width, h: r.height,
            ink: [bb.x, bb.y, bb.width, bb.height], uses: c.querySelectorAll('use').length,
            chars: c.outerHTML.length};
  });
}"""
def probe(src, keys, dst):
    nb = json.load(open(src))
    # at the END of the mega-cell: the harness opens only two-cell notebooks
    c = nb["cells"][1]
    c["source"] = "".join(c["source"]) + "\n" + CELL % (keys,)
    json.dump(nb, open(dst, "w"))
    return dst
# the formulas the NEW build typeset (not the seed-dependent ones)
_src = __import__("megasrc").expand("".join(json.load(open(new))["cells"][1]["source"]))
_blk = _src[_src.index("_MATH_PRE.update({"):]
_blk = _blk[:_blk.index("\n})")]
KEYS = [eval(m) for m in re.findall(r"^('(?:16|20)\|.*?'): \(", _blk, re.M)]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = None
    for tag, nb in (("old", old), ("new", new)):
        ctx, pg, errs = fresh(b, BASE, probe(nb, KEYS, os.path.join(os.path.dirname(os.path.abspath(out)), "probe_math_%s.ipynb" % tag)), ROOT, ctx)
        pg.wait_for_selector("#nbmathsheet", state="attached", timeout=60000)
        res[tag] = pg.evaluate(READ)
        pg.wait_for_timeout(600)
        pg.locator("#nbmathsheet").screenshot(path="%s-%s.png" % (pre, tag))
        res[tag + "_errs"] = errs
    b.close()
fails = []
o, n = res["old"], res["new"]
if len(o) != len(n):
    fails.append("formula count %d -> %d" % (len(o), len(n)))
dw = dh = di = 0.0
for i, (a, c) in enumerate(zip(o, n)):
    dw, dh = max(dw, abs(a["w"] - c["w"])), max(dh, abs(a["h"] - c["h"]))
    if a["ink"] and c["ink"]:
        # viewBox units -> px of this formula on the page
        px = c["h"] / float(c["vb"].split()[3])
        d = max(abs(x - y) for x, y in zip(a["ink"], c["ink"])) * px
        di = max(di, d)
        if d > 0.1:
            fails.append("formula %d: ink %s -> %s (%.3f px)" % (i, a["ink"], c["ink"], d))
    if abs(a["w"] - c["w"]) > 0.5 or abs(a["h"] - c["h"]) > 0.5:
        fails.append("formula %d: box %.2fx%.2f -> %.2fx%.2f" % (i, a["w"], a["h"], c["w"], c["h"]))
res["summary"] = {"n": [len(o), len(n)], "max_dw_px": round(dw, 3), "max_dh_px": round(dh, 3),
                  "max_ink_px": round(di, 3), "chars": [sum(x["chars"] for x in o), sum(x["chars"] for x in n)],
                  "fails": fails}
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res["summary"], indent=1))
sys.exit(1 if fails else 0)
