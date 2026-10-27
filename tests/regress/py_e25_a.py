"""E25.a · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_a.py <notebook.ipynb>
  ONE PREVIEW WHERE NO WIDGET IS DRAWN (PyCharm, Video Nutzer 08.10.: title
  card twice, between them a box "Your progress" with a timeline). PyCharm
  itself cannot be driven here (desktop application); measured on what it
  receives, as py_e22p does: the kernel runs with PYCHARM_HOSTED=1, every
  output bundle is put together in Chromium the way such a viewer shows it
  (text/html first, else text/plain), no script runs. Counted there:
    visible title cards (.nbtitle-card with a box)      want 1, inside the cover (.nbcover-out)
    visible "Your progress" strips (.nbprog)            want 0
    the cover is there, with Play                        precondition
  and in a JupyterLab kernel (no variable) the document's own title card is
  output as before (not hidden; the first output and its display update).
  v1.67: 2 title cards (document + cover), 1 strip. Owner: Python.
exit 0 = REGRESS-PY-E25A OK."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from py_e22p import iopub

COUNT = r"""() => { var vis = function(e){ var b = e.getBoundingClientRect(), s = getComputedStyle(e);
    for (var x = e; x; x = x.parentElement) if (getComputedStyle(x).display === 'none') return false;
    return b.width > 0 && b.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
  var cards = [].filter.call(document.querySelectorAll('.nbtitle-card, .nbr-nbtitle-card'), vis);
  return {cards: cards.length, inCover: cards.filter(function(c){ return !!c.closest('.nbcover-out'); }).length,
          prog: [].filter.call(document.querySelectorAll('.nbprog'), vis).length,
          cover: !!document.querySelector('.nbcover-out .nbcover-play')}; }"""

def viewer(b, outs, tag, shot=None):
    page = "".join(o.get("text/html") or ("<pre>%s</pre>" % o["text/plain"] if o.get("text/plain") else "") for o in outs)
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "e25a_%s.html" % tag)
    open(tmp, "w", encoding="utf-8").write("<!doctype html><meta charset=utf-8><body style='font-family:sans-serif;max-width:1100px;margin:auto'>" + page)
    ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
    pg.goto("file://" + tmp); pg.wait_for_timeout(800)
    r = pg.evaluate(COUNT)
    if shot: pg.screenshot(path=shot, full_page=False)
    ctx.close()
    return r

def main():
    src = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    rows, fails = [], []
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            outs = iopub(src, {"PYCHARM_HOSTED": "1"})
            errs = [o["error"] for o in outs if "error" in o]
            if errs: fails.append("E25.a the run raised: %s" % errs[:1])
            r = viewer(b, outs, "pycharm", os.environ.get("E25A_SHOT"))
            # py-E26.1 (11.10.) — behauptete bisher: the one card is the COVER's
            # (with Play); the document's card hidden only in a PyCharm kernel.
            # Now the one card is the reading version's (first output, every
            # kernel); cover and document card go out wrapped in `.nbwarm`
            # (hidden inline) — only our page script unwraps them, next to
            # drawn widgets. Every frame on its own: tests/regress/env_iframe.py.
            rows.append("E25.a PYCHARM_HOSTED=1: %d visible title cards (%d in the cover), %d 'Your progress' strips"
                        % (r["cards"], r["inCover"], r["prog"]))
            if r["cards"] != 1 or r["inCover"]: fails.append("E25.a %d visible title cards (%d in the cover), want 1 outside it" % (r["cards"], r["inCover"]))
            if r["prog"]: fails.append("E25.a %d 'Your progress' strips visible, want 0" % r["prog"])
            outs2 = iopub(src, {})
            doc = [o["text/html"] for o in outs2 if 'nbtitle-doc' in (o.get("text/html") or "")[:600]]
            cov = [o["text/html"] for o in outs2 if 'nbcover-out' in (o.get("text/html") or "")[:600]]
            wrapped = lambda d: d.lstrip().startswith("<div class='nbwarm' style='display:none'>")
            rows.append("E25.a JupyterLab kernel: %d document title outputs, %d cover outputs, wrapped: %s"
                        % (len(doc), len(cov), [wrapped(d) for d in doc + cov]))
            if not doc or not cov: fails.append("E25.a BAD JupyterLab kernel: no document title or no cover output")
            elif not all(wrapped(d) for d in doc + cov): fails.append("E25.a JupyterLab kernel: title or cover not wrapped in .nbwarm")
        except Exception as e:
            fails.append("E25.a BAD %s" % str(e)[:200])
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E25A OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
