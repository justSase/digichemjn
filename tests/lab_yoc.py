"""E11.1 — "YOUR OWN CELL" IS NO ACCORDION, in a real JupyterLab
(2026-09-30, Struktur + Applikation, Werkstatt Python).

    python3 tests/lab_yoc.py <notebook> [out.png]

A fresh copy is opened and run (1400 x 900). Then, for 4 styles x light/dark:

  1  no `.acc-yoc`, no `button.nbyoc-add`, no `.nbyoc-note` in the notebook
  2  no visible text "Your own cell" / "Cells of your own sit" in the document
     (the panel's own YOC mark is not the document and is not counted)
  3  anchor #nbyoc and `.nbyoc-list` exist, outside `.acc-title`, in no
     accordion at all, and take no height while empty (<= 1 px)
And once (minimal light):
  4  a click on the YOC mark in the timeline makes one cell of one's own (2 -> 3)
  5  shutting the title (click on the card) hides the title accordion, while
     the own cell and #nbyoc stay on screen (height > 0 / in the layout);
     no collapse header stands between the title accordion and the own cell
  6  no page errors
  7  E9.13: a restore offer from another build shows in `.nbyoc-list` (outside
     any accordion) and "Restore" makes the kept cell
exit 0 = YOC OK."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright

BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
BASE, LAB = ensure_lab(BASE)
SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else None

PROBE_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var vis = function(e){ if (!e) return false; var r = e.getBoundingClientRect();
    var cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
  var txt = [];
  P.querySelectorAll('.jp-Notebook *').forEach(function(e){
    if (e.closest('#nbpanel-root') || e.closest('.nbrail')) return;
    if (e.children.length) return;
    var t = (e.textContent || '').trim();
    if (/Your own cell|Cells of your own sit/.test(t) && vis(e)) txt.push(t.slice(0, 50));
  });
  var anc = P.querySelector('[id^="nbyoc__"]'), list = P.querySelector('.nbyoc-list');
  var inAcc = function(e){ return !!(e && (e.closest('.acc-title') || e.closest('.jupyter-widget-Collapse') || e.closest('.acc-root'))); };
  var at = P.querySelector('.acc-title.acc-root');
  return {accYoc: P.querySelectorAll('.acc-yoc').length, add: P.querySelectorAll('button.nbyoc-add').length,
          note: P.querySelectorAll('.nbyoc-note').length, texts: txt,
          anchor: !!anc, list: !!list, anchorInAcc: inAcc(anc), listInAcc: inAcc(list),
          listH: list ? Math.round(list.getBoundingClientRect().height * 10) / 10 : null,
          titleAcc: !!at, cells: P.querySelectorAll('.jp-Cell').length,
          skin: [].filter.call(document.body.classList, function(c){ return c.indexOf('nbskin-') === 0; }).join(','),
          dark: document.body.classList.contains('nbdark')};
}"""
SET_JS = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t);
  window.__nbApplySkin(); window.__nbApplyTheme(); }"""
FOLD_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var at = P.querySelector('.acc-title.acc-root'); var cells = P.querySelectorAll('.jp-Cell');
  var own = cells[cells.length - 1]; var anc = P.querySelector('[id^="nbyoc__"]');
  var body = at && at.querySelector('.jupyter-widget-Collapse-contents');
  var h = function(e){ return e ? Math.round(e.getBoundingClientRect().height) : null; };
  var cs = function(e){ return e ? getComputedStyle(e).display : null; };
  // collapse headers between the title accordion and the own cell (the YOC pill was one)
  var hdr = 0; P.querySelectorAll('.jupyter-widget-Collapse-header').forEach(function(x){
    if (at && at.contains(x)) return;
    if (at && (at.compareDocumentPosition(x) & Node.DOCUMENT_POSITION_FOLLOWING)) hdr++; });
  var ar = anc ? anc.getBoundingClientRect() : null;
  var ownRect = own.getBoundingClientRect();
  var mark = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"] .nbsect');
  return {titleBodyH: h(body), titleBodyDisp: cs(body), titleBodyHidden: body ? body.classList.contains('lm-mod-hidden') : null,
          ownH: h(own), ownDisp: cs(own), ownTop: Math.round(ownRect.top),
          ownIsCode: own.classList.contains('jp-CodeCell'), anchorLaid: !!(anc && anc.offsetParent),
          anchorTop: ar ? Math.round(ar.top) : null, hdrAfterTitle: hdr, yocMark: !!mark,
          yocMarkVis: !!(mark && mark.getBoundingClientRect().height > 0)};
}"""

fails, rows = [], []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx, pg, errs = fresh(b, BASE, SRC, LAB)
    for sk in ("minimal", "cyber", "retro", "fairy"):
        for th in ("light", "dark"):
            pg.evaluate(SET_JS, [sk, th]); pg.wait_for_timeout(500)
            r = pg.evaluate(PROBE_JS)
            v = []
            if r["accYoc"]: v.append(".acc-yoc x%d" % r["accYoc"])
            if r["add"]: v.append("＋ button x%d" % r["add"])
            if r["note"]: v.append("note x%d" % r["note"])
            if r["texts"]: v.append("visible text %s" % r["texts"][:3])
            if not r["anchor"] or not r["list"]: v.append("anchor %s / list %s missing" % (r["anchor"], r["list"]))
            if r["anchorInAcc"] or r["listInAcc"]: v.append("anchor/list inside an accordion")
            if r["listH"] is not None and r["listH"] > 1: v.append("empty list takes %s px" % r["listH"])
            rows.append("%-8s %-5s skin=%s dark=%s · acc-yoc %d · ＋ %d · note %d · texts %d · anchor/list %s/%s in acc %s/%s · list h %s · %s"
                        % (sk, th, r["skin"], r["dark"], r["accYoc"], r["add"], r["note"], len(r["texts"]), r["anchor"], r["list"],
                           r["anchorInAcc"], r["listInAcc"], r["listH"], "ok" if not v else "; ".join(v)))
            if v: fails.append("%s/%s: %s" % (sk, th, "; ".join(v)))
    pg.evaluate(SET_JS, ["minimal", "light"]); pg.wait_for_timeout(500)
    n0 = pg.evaluate(PROBE_JS)["cells"]
    mark = pg.query_selector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]')
    if not mark:
        fails.append("no YOC mark in the timeline")
    else:
        # the timeline follows the document: go to its end so the mark is on
        # screen, then a real mouse click on its bar (the <a> itself is 0 px high)
        MK = """() => { var s = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"] .nbsect');
                        var r = s.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"""
        pg.mouse.move(800, 500)
        for _ in range(60):
            bx = pg.evaluate(MK)
            if 130 < bx[1] < 800: break
            pg.mouse.wheel(0, 400); pg.wait_for_timeout(250)
        # 2026-10-04 (E21 Rest Stufe 2, Werkstatt JS — Prüfwerkzeug) — BEHAUPTETE
        # BISHER: 1.2 s after the last wheel notch the mark stands still. The
        # wheel's glide and the landing at the end of the document can run
        # longer (one CPU, Modeling): measured bar at 275/281/322/358 px right
        # before the click and a few px further on after it — 2 of 5 and 2 of
        # 6 runs clicked where the mark HAD been (hit "jp-WindowedPanel-outer",
        # cells 2 -> 2; gate 04.10. 17:xx: Modeling red). A reader clicks a mark
        # that stands: now the bar's place is read every 100 ms until it is
        # the same three times in a row (at most 4 s, the time reported), and
        # the click goes there only if the mark is what lies on top.
        hit, t_still = None, None
        for _try in range(3):
            t0s = time.time(); prev, same = None, 0
            while time.time() - t0s < 4.0:
                pg.wait_for_timeout(100); cur = pg.evaluate(MK)
                same = same + 1 if prev and abs(cur[0] - prev[0]) < 0.5 and abs(cur[1] - prev[1]) < 0.5 else 0
                prev = cur
                if same >= 2: break
            t_still = round(time.time() - t0s, 2)
            bx = pg.evaluate(MK)
            hit = pg.evaluate("([x,y]) => { var e = document.elementFromPoint(x, y); var a = e && e.closest('a'); return a ? a.className : (e ? e.className : null); }", bx)
            if hit and "nbmap-node" in hit: break
        rows.append("hit at the bar: %s (still after %s s)" % (hit, t_still))
        rows.append("YOC mark bar at %d, %d" % tuple(bx))
        pg.mouse.click(bx[0], bx[1]); pg.wait_for_timeout(2500)
        pg.keyboard.type("x = 1"); pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
    n1 = pg.evaluate(PROBE_JS)["cells"]
    rows.append("YOC mark click: cells %d -> %d" % (n0, n1))
    if n1 != n0 + 1: fails.append("YOC mark click: cells %d -> %d (want +1)" % (n0, n1))
    f0 = pg.evaluate(FOLD_JS)
    # the markdown cell's card is hidden once the notebook runs; the document's is the one
    card = pg.locator(".jp-NotebookPanel:not(.lm-mod-hidden) .nbtitle-card:visible").first
    card.click(); pg.wait_for_timeout(1800)
    f1 = pg.evaluate(FOLD_JS)
    rows.append("title open  : body h %s · own cell h %s (%s) · anchor laid %s · headers after title %d · YOC mark %s"
                % (f0["titleBodyH"], f0["ownH"], f0["ownDisp"], f0["anchorLaid"], f0["hdrAfterTitle"], f0["yocMarkVis"]))
    rows.append("title shut  : body h %s (hidden %s) · own cell h %s (%s, top %s) · anchor laid %s · YOC mark %s"
                % (f1["titleBodyH"], f1["titleBodyHidden"], f1["ownH"], f1["ownDisp"], f1["ownTop"], f1["anchorLaid"], f1["yocMarkVis"]))
    if not (f1["titleBodyHidden"] or (f1["titleBodyH"] or 0) == 0): fails.append("the title did not shut")
    if not f1["ownH"] or f1["ownDisp"] == "none": fails.append("the own cell went with the title")
    if not f1["anchorLaid"]: fails.append("#nbyoc went with the title")
    if f0["hdrAfterTitle"] or f1["hdrAfterTitle"]: fails.append("%d collapse header(s) after the title (YOC pill?)" % f0["hdrAfterTitle"])
    if not f1["yocMarkVis"]: fails.append("the YOC mark is gone with the title shut")
    if OUT:
        pg.evaluate("""() => [].forEach.call(document.querySelectorAll('.jp-toast-button, .jp-Notification-Toast button'),
            function(b){ if (b.textContent.trim() === 'No') b.click(); })""")
        pg.wait_for_timeout(400)
        pg.screenshot(path=OUT)
    card.click(); pg.wait_for_timeout(1500)
    # 7  E9.13 still has its place: cells kept by ANOTHER build are offered in
    #    `.nbyoc-list` (now outside any accordion) and "Restore" makes them.
    #    The own cell from step 4 is deleted first (a build with cells of its
    #    own offers nothing).
    # 2026-10-04 (E21 Rest Stufe 2, Werkstatt JS — Prüfwerkzeug) — BEHAUPTETE
    # BISHER: the last `.jp-Cell` in the DOM is the own cell, clicked at (5, 5).
    # Under JupyterLab 4.6's windowing only the cells near the view are in the
    # DOM; with the title open again (≈ 2000 px) the own cell can be out of it,
    # and `.last` was the MEGA cell (`data-windowed-list-index="1"`), whose
    # corner lies under `button.nbfull` — "intercepts pointer events", 30 s
    # timeout (Hauptwerkstatt 04.10.: v1.62 and v1.63 red 3 of 4 alone; had
    # the click landed, d d would have deleted the document). Now: to the end
    # of the notebook, the cell with the HIGHEST windowed index, checked to be
    # the own cell (a code cell holding "x = 1"), made active the way
    # to_command does (focus, Escape), d d; afterwards one cell fewer and the
    # document cell still there. A missed precondition is red, never skipped.
    OWN7 = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
        var n = P.querySelector('.jp-Notebook'), sc = n.querySelector('.jp-WindowedPanel-outer') || n;
        sc.scrollTop = sc.scrollHeight;
        var idx = function(c, k){ var v = c.getAttribute('data-windowed-list-index'); return v === null ? k : +v; };
        var best = null, bi = -1;
        [].forEach.call(P.querySelectorAll('.jp-Cell'), function(c, k){ var i = idx(c, k); if (i > bi) { bi = i; best = c; } });
        [].forEach.call(P.querySelectorAll('[data-yoc7]'), function(c){ c.removeAttribute('data-yoc7'); });
        if (!best) return null;
        var ed = best.querySelector('.jp-InputArea-editor'), t = ed ? ed.textContent.replace(/\s+/g, ' ').trim() : '';
        best.setAttribute('data-yoc7', '1');
        return {idx: bi, code: best.classList.contains('jp-CodeCell'), txt: t.slice(0, 40), len: t.length}; }"""
    CNT7 = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), m = -1, mega = false;
        [].forEach.call(P.querySelectorAll('.jp-Cell'), function(c, k){ var v = c.getAttribute('data-windowed-list-index');
          v = v === null ? k : +v; if (v > m) m = v;
          if (v === 1 && c.classList.contains('jp-CodeCell') && c.querySelector('.nbfeed, .jp-OutputArea-output')) mega = true; });
        return {n: m + 1, mega: mega}; }"""
    # gate 04.10. 17:xx (stage 2, Modeling): after the scroll the highest cell
    # in the DOM was still the document cell — the own cell was not drawn. So
    # when the scroll does not bring it, JupyterLab's own way down is taken:
    # the document cell made active (focus, Escape), then J (select the cell
    # below), which scrolls the windowed list to it; the new active cell is
    # checked the same way (a code cell holding "x = 1").
    ACT7 = r"""() => { var c = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell.jp-mod-active');
        if (!c) return null; [].forEach.call(document.querySelectorAll('[data-yoc7]'), function(x){ x.removeAttribute('data-yoc7'); });
        var ed = c.querySelector('.jp-InputArea-editor'), t = ed ? ed.textContent.replace(/\s+/g, ' ').trim() : '';
        c.setAttribute('data-yoc7', '1'); var v = c.getAttribute('data-windowed-list-index');
        return {idx: v === null ? -1 : +v, code: c.classList.contains('jp-CodeCell'), txt: t.slice(0, 40), len: t.length, via: 'J'}; }"""
    own7 = None
    for _ in range(6):
        own7 = pg.evaluate(OWN7); pg.wait_for_timeout(400)
        own7 = pg.evaluate(OWN7)
        if own7 and own7["code"] and own7["txt"] == "x = 1": break
        if own7:
            pg.evaluate("() => { var a = document.activeElement; if (a && a.blur) a.blur(); document.querySelector('[data-yoc7]').focus(); }")
            pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
            pg.keyboard.press("j"); pg.wait_for_timeout(700)
            own7 = pg.evaluate(ACT7)
            if own7 and own7["code"] and own7["txt"] == "x = 1": break
    rows.append("step 7, the cell to delete: %s" % own7)
    if not (own7 and own7["code"] and own7["txt"] == "x = 1"):
        fails.append("BAD step 7: the last cell is not the own cell (%s)" % own7)
    else:
        c7a = pg.evaluate(CNT7)
        pg.evaluate("() => { var a = document.activeElement; if (a && a.blur) a.blur(); document.querySelector('[data-yoc7]').focus(); }")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        act = pg.evaluate("() => { var c = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell.jp-mod-active'); return !!(c && c.hasAttribute('data-yoc7')); }")
        if not act:
            fails.append("BAD step 7: the own cell did not become the active cell")
        else:
            pg.keyboard.press("d"); pg.keyboard.press("d"); pg.wait_for_timeout(1500)
            c7b = pg.evaluate(CNT7)
            rows.append("step 7, delete: cells %d -> %d, document cell there %s" % (c7a["n"], c7b["n"], c7b["mega"]))
            if c7b["n"] != c7a["n"] - 1 or not c7b["mega"]:
                fails.append("step 7: d d gave cells %d -> %d, document cell %s" % (c7a["n"], c7b["n"], c7b["mega"]))
    pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
        var fs = P.querySelectorAll('.nbfeed[data-progress]'); var id = '';
        try { id = JSON.parse(fs[fs.length - 1].getAttribute('data-progress')).id || ''; } catch (e) {}
        id = String(id).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
        var all = {}; all[id] = {v: 'v-older', t: Date.now(), cells: ['y = 2  # kept']};
        localStorage.setItem('digichemjn.owncells.v1', JSON.stringify(all));
        var d = document.createElement('div'); P.querySelector('.jp-Notebook').appendChild(d); d.remove(); }""")
    pg.wait_for_timeout(1500)
    RS = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
        var b = P.querySelector('.nbyoc-list .nbyoc-restore'); if (!b) return null; var r = b.getBoundingClientRect();
        return {txt: b.textContent.trim().slice(0, 60), h: Math.round(r.height), inAcc: !!(b.closest('.jupyter-widget-Collapse') || b.closest('.acc-root')),
                cells: P.querySelectorAll('.jp-Cell').length}; }"""
    rs = pg.evaluate(RS)
    rows.append("after delete: cells %s, store %s" % (pg.evaluate("() => document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell').length"),
                pg.evaluate("() => localStorage.getItem('digichemjn.owncells.v1')")[:120]))
    rows.append("restore offer (other build kept 1 cell): %s" % rs)
    if not rs or rs["h"] <= 0 or rs["inAcc"]:
        fails.append("E9.13 restore offer missing/hidden/in an accordion: %s" % rs)
    else:
        n2 = rs["cells"]
        pg.locator(".jp-NotebookPanel:not(.lm-mod-hidden) .nbyoc-restore-yes").click(); pg.wait_for_timeout(3000)
        n3 = pg.evaluate("() => document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell').length")
        rows.append("restore: cells %d -> %d" % (n2, n3))
        if n3 != n2 + 1: fails.append("restore: cells %d -> %d (want +1)" % (n2, n3))
    if errs: fails.append("page errors: %s" % errs[:2])
    rows.append("page errors: %d" % len(errs))
    ctx.close(); b.close()
kill_sessions(BASE)
print("\n".join(rows))
print("\n" + ("YOC OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
