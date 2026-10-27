"""E16.8 (2026-10-02, Applikation) — WHAT THE READER TYPES IS TAKEN, LIVE.

    python3 tests/lab_inputs.py <notebook> [tag]

A fresh copy, run in a real JupyterLab, chapter 1 (Complex: t1, slider q;
Modeling: t1, first slider):

  A  slider readout: type a new value, NO Enter → the readout line under the
     plot (the kernel's answer) changes within 0.5 s
  B  slider readout: type, then leave it (Tab) → the value is taken
  C  answer box: type the right answer, NO Enter and NO blur, press Check by a
     script click (the box keeps the focus) → ✓ (the kernel had the number)
  D  answer box: type a wrong real part 5, leave it (Tab), click Check → the
     hint quotes "you entered 5" (the kernel had the number)
  E  intermediate input "-", "1.", "-0." in the box and "-", "-1." in the
     readout → no error box, no traceback
  F  no page errors

Prints one line per criterion, exit 0 = INPUTS OK. Complex only knows t1's
answer (re 0, im √q); other notebooks run A, B, E, F."""
import sys, os, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
BASE, LAB = ensure_lab(BASE)
SRC = sys.argv[1]
TAG = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(SRC)
P = ".jp-NotebookPanel:not(.lm-mod-hidden) "

def open_fold(pg, cls):
    pg.evaluate("""(cls) => { var a = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .' + cls);
       var h = a && a.querySelector('.jupyter-widget-Collapse-header, .lm-AccordionPanel-title, .p-Collapse-header');
       if (h && !a.querySelector('.jupyter-widget-Collapse-open, .lm-mod-expanded, .p-Collapse-open')) h.click(); return !!h; }""", cls)
    pg.wait_for_timeout(1500)

def readline(pg):
    return pg.evaluate("""() => { var a = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .acc-viz');
      var r = a && a.querySelector('.nbread'), im = a && a.querySelector('img');
      return (r ? r.textContent.replace(/\\s+/g, ' ').trim() : '') + '|' + (im ? im.src.length : 0); }""")

def feedback(pg):
    return pg.evaluate("""() => { var o = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .acc-practice .jp-OutputArea');
      return o ? o.textContent.replace(/\\s+/g, ' ').trim().slice(0, 160) : ''; }""")

def errors(pg):
    return pg.evaluate("""() => [].map.call(document.querySelectorAll(
      '.jp-NotebookPanel:not(.lm-mod-hidden) .nberr, .jp-NotebookPanel:not(.lm-mod-hidden) [data-mime-type="application/vnd.jupyter.stderr"]'),
      function(e){ return e.textContent.slice(0, 80); })""")

def wait_change(pg, before, limit=2.0):
    t0 = time.time()
    while time.time() - t0 < limit:
        pg.wait_for_timeout(50)
        if readline(pg) != before:
            return time.time() - t0
    return None

def typed(pg, el, text):
    el.click(); pg.keyboard.press("Control+A"); pg.keyboard.type(text, delay=40)

rows, fails = [], []
def row(k, what, got, ok):
    rows.append("%s  %-62s %s  %s" % (k, what, got, "ok" if ok else "ROT"))
    if not ok: fails.append(k)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx, pg, errs = fresh(b, BASE, SRC, LAB)
    open_fold(pg, "acc-viz")
    ro = pg.query_selector(P + ".acc-viz .widget-readout")
    v0 = float(ro.inner_text().replace("−", "-"))
    new = "%g" % (v0 - 1)
    s0 = readline(pg); typed(pg, ro, new); dt = wait_change(pg, s0)
    row("A", "Regler-Feld '%s' getippt, kein Enter: Lesezeile folgt nach" % new,
        "%.2f s" % dt if dt is not None else "nein (2 s)", dt is not None and dt <= 0.5)
    pg.keyboard.press("Tab"); pg.wait_for_timeout(1200)
    got = readline(pg)
    row("B", "… danach Tab (Blur): Wert übernommen", "ja" if got != s0 else "nein", got != s0)
    open_fold(pg, "acc-practice")
    boxes = pg.query_selector_all(P + ".acc-practice .widget-text input")
    txt = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .acc-practice') || {}).textContent || ''")
    m = re.search(r"personal value is q = (\d+)", txt)
    n0 = len(errors(pg))
    typed(pg, ro, "-"); pg.wait_for_timeout(500); pg.keyboard.type("1.", delay=40); pg.wait_for_timeout(700)
    pg.keyboard.press("Tab"); pg.wait_for_timeout(1000)
    if m and len(boxes) >= 2:
        r = "%g" % (int(m.group(1)) ** 0.5)
        typed(pg, boxes[0], "5"); pg.keyboard.press("Tab"); pg.wait_for_timeout(600)
        pg.click(P + ".acc-practice .sc-btn"); pg.wait_for_timeout(2500)
        fb = feedback(pg); ok = "entered 5" in fb
        row("D", "Re '5' getippt, Tab, Check geklickt: Hinweis nennt 5", fb[26:76], ok)
        for t_ in ("-", "1.", "-0."):
            typed(pg, boxes[1], t_); pg.wait_for_timeout(500)
        n1 = len(errors(pg))
        row("E", "Zwischeneingaben '-', '1.', '-0.' (Feld) · '-', '-1.' (Regler)", "%d neue Fehler" % (n1 - n0), n1 == n0)
        typed(pg, boxes[0], "0"); typed(pg, boxes[1], r); pg.wait_for_timeout(600)
        pg.evaluate("() => { var o = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .acc-practice .sc-btn'); if (o) o.scrollIntoView({block: 'center'}); }")
        pg.wait_for_timeout(500)
        pg.evaluate("() => document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .acc-practice .sc-btn').click()")
        for _ in range(40):                      # the answer folds soon after ✓: read it at once
            pg.wait_for_timeout(100); fb = feedback(pg)
            if fb.startswith("✓") or fb.startswith("Not"): break
        if os.environ.get("LAB_INPUTS_SHOT"):
            pg.screenshot(path=os.environ["LAB_INPUTS_SHOT"])
        pg.wait_for_timeout(2000)
        fb = feedback(pg); ok = fb.startswith("✓")
        row("C", "Antwort '0', '%s' getippt, Fokus bleibt, Check per Skript" % r, fb[:40], ok)
    else:
        rows.append("C/D  (keine Complex-t1-Aufgabe gefunden: übersprungen)")
        for t_ in ("-", "1.", "-0."):
            if boxes: typed(pg, boxes[0], t_); pg.wait_for_timeout(500)
        n1 = len(errors(pg))
        row("E", "Zwischeneingaben '-', '1.', '-0.' (Feld) · '-', '-1.' (Regler)", "%d neue Fehler" % (n1 - n0), n1 == n0)
    pe = [e for e in errs if e.startswith("pageerror")]
    row("F", "Seitenfehler", str(len(pe)), not pe)
    b.close()
for r in rows: print(TAG, r)
print(TAG, "INPUTS OK" if not fails else "INPUTS ROT: " + ", ".join(fails))
sys.exit(1 if fails else 0)
