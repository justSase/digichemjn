"""E25.k · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_k.py <notebook.ipynb>
  THE PREVIEW, TIDIED (E25.k, Nutzer 08.10. "ordentlicher", Lesart Dirigent).
  In a real JupyterLab, the cover of a run (`.nbcover-out`, brought up again
  as a run brings it, window.__nbCoverShow, js-E24.3), measured top to bottom
  where the reader sees it (getBoundingClientRect):
    title card  <  lead  <  "What you will learn" (details.nbcover-learn,
    closed)  <  timeline (.nbcover-map)  <  Play  <  "Sign in"
    (details.nbacct-fold)  <  the series (.nbcover-series)
  plus: the language slot (.nbcover-lang-slot) sits inside the title card;
  the series carries data-series (JSON: series, me = this notebook, items with
  id/name/file) and its list is visible with this notebook marked.
  Python gives markup and order; where the page puts its mode cards and the
  language row is JS (E25.k Verhalten) and is reported, not judged here.
  v1.67: timeline after Play, goals open, no fold, no series. Owner: Python.
exit 0 = REGRESS-PY-E25-K OK."""
import sys, os, json, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
ORDER_JS = """() => { """ + FRONT + """
  var C = P && P.querySelector('.nbcover-out'); if (!C) return null;
  var y = function(sel){ var e = C.querySelector(sel); if (!e) return null; var b = e.getBoundingClientRect();
    return b.height > 0 ? Math.round(b.top) : -1; };
  var lg = C.querySelector('.nbcover-learn'), ser = C.querySelector('.nbcover-series'), slot = C.querySelector('.nbcover-lang-slot');
  return {card: y('.nbtitle-card'), lead: y('.nbtitle-lead'), learn: y('.nbcover-learn'), map: y('.nbcover-map'),
          mode: y('.nbmode'), lang: y('.nblang'), play: y('.nbcover-play'), acct: y('.nbacct-fold'), series: y('.nbcover-series'),
          learnOpen: lg ? lg.open : null, slotInCard: !!(slot && slot.closest('.nbtitle-card')),
          data: ser ? ser.getAttribute('data-series') : null,
          me: ser ? [].map.call(ser.querySelectorAll('.nbser-me'), function(e){ return e.textContent.trim(); }) : [],
          items: ser ? ser.querySelectorAll('.nbser-it').length : 0,
          shown: !!(C.getAttribute('data-nbcov') !== null)}; }"""

def main():
    src = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    sys.argv = sys.argv[:1] + ["x"]          # run.py parses the command line on import
    rows, fails = [], []
    import run as R
    from lab_keys import ensure_lab, CHROME, kill_sessions
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    nid = R.nb_id(src)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            kill_sessions(base)
            ctx = b.new_context(viewport={"width": 1400, "height": 900})
            ctx.add_init_script(R.INIT_JS % json.dumps({}))
            pg = ctx.new_page(); pg.errs = []
            pg.on("pageerror", lambda e: pg.errs.append(str(e)[:160]))
            name = "e25k_%d_%s" % (int(time.time() * 1000) % 10 ** 7, os.path.basename(src))
            shutil.copy(src, os.path.join(root, name))
            pg.goto(base + "/lab/tree/" + name + "?reset")
            pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
            pg.wait_for_timeout(1500)
            R.run_front(pg, nid)
            up = pg.evaluate("() => !!(window.__nbCoverShow && window.__nbCoverShow(true))")
            o = None
            for _ in range(20):
                pg.wait_for_timeout(500)
                o = pg.evaluate(ORDER_JS)
                if o and o["play"] and o["play"] > -1: break
            if os.environ.get("E25K_SHOT"):
                pg.evaluate("() => { " + FRONT + " var c = P && P.querySelector('.nbcover-out .nbtitle-card'); if (c) c.scrollIntoView({block: 'start'}); }")
                pg.wait_for_timeout(600); pg.screenshot(path=os.environ["E25K_SHOT"])
            rows.append("E25.k cover up %s: %s" % (up, {k: v for k, v in (o or {}).items() if k != "data"}))
            if not o or not o["card"] or o["card"] < 0 or not o["play"] or o["play"] < 0:
                fails.append("E25.k BAD the cover did not come up drawn (up %s, %s)" % (up, o and {k: o[k] for k in ('card', 'play')}))
            else:
                seq = [("card", o["card"]), ("lead", o["lead"]), ("learn", o["learn"]), ("map", o["map"]),
                       ("play", o["play"]), ("acct", o["acct"]), ("series", o["series"])]
                miss = [k for k, v in seq if v is None or v < 0]
                if miss: fails.append("E25.k missing or not drawn: %s" % miss)
                got = [k for k, v in sorted([s for s in seq if s[1] is not None and s[1] >= 0], key=lambda s: s[1])]
                want = [k for k, v in seq if k in got]
                if got != want: fails.append("E25.k order top to bottom %s, want %s" % (got, want))
                if o["learnOpen"] is not False: fails.append("E25.k 'What you will learn' is not folded (%s)" % o["learnOpen"])
                if not o["slotInCard"]: fails.append("E25.k no language slot in the title card")
                try:
                    d = json.loads(o["data"] or "")
                    rows.append("E25.k series %s: %s" % (d.get("series"), [(i["id"], i["file"]) for i in d.get("items", [])]))
                    if d.get("me") != nid or not any(i.get("id") == nid and i.get("file") for i in d.get("items", [])):
                        fails.append("E25.k series data does not name this notebook (%s) %s" % (nid, d.get("me")))
                except Exception as e:
                    fails.append("E25.k series data not JSON (%s): %r" % (e, (o["data"] or "")[:80]))
                if o["items"] < 1 or len(o["me"]) != 1: fails.append("E25.k series list: %d items, marked %s" % (o["items"], o["me"]))
            if pg.errs: fails.append("E25.k page errors %s" % pg.errs[:2])
            ctx.close()
        except Exception as e:
            fails.append("E25.k BAD %s" % str(e)[:200])
        finally:
            kill_sessions(base)
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E25-K OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
