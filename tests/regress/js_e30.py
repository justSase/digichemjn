"""E30 · JS — THE TIMELINE IN THE READING WINDOW LIKE LAB (Werkstatt JS, 2026-10-12).
    python3 tests/regress/js_e30.py [<notebook.ipynb>] [--shots DIR] [--json out.json]

PyCharm, v1.75 (reader's five pictures, 12.10.): the reading window's panel was
a list of chapter dots squeezed onto a track (locked chapters bunched at the
bottom), no hover boxes, no pips, a click only scrolled the heading to the top,
contents list and panel German beside an English document, in dark the panel
cut at the right. STOP.md „NÄCHSTE RUNDE E30“ B6 (eine Panel-Logik), B2, B5,
`--nbfs` im Lesefenster. Same viewer as env_reader.py: the notebook's cell in a
real kernel, every output in an iframe of its own, no widget manager (PyCharm /
JCEF), the host page taller than the viewport, 1400 × 900, served over http.
The template (`--nb vorlage`, E28) unless a notebook is named.
Rows (en build, light, unless said):
  M1 map          every drawn mark of a chapter / part / the title stands at
                  the height of its heading in the window (|mark − heading| ≤
                  2 px, measured from the reading version's own markup: the
                  contents list's anchors, the folds' headings), with the
                  document at the top and around the locked chapters; locked
                  chapters each at their own heading (no two closer than 10 px)
  L1 land         chapter 1 folded, its mark clicked (mouse): the fold opens,
                  its heading on the reading height ±2 px, the panel names it
  P1 pin          the heading stays on the line (±2 px) while a fold above it
                  shuts and opens, the lens, the text size and the window
                  height change
  P2 let go       a script scrolls the window to 0: it stays there (the pin
                  lets go, Lab E23.15) · T1 the thumb (the window's scroll
                  bar) is not under a mark's dot and covers none
  F1 fold         a click on the chosen, open mark folds it; it stays ±2 px
  K1 locked       a click on a locked chapter's mark and on one of its pips:
                  the window does not move (≤ 1 px), a box says why (names the
                  exercise), the chapter stays locked (Lab E29 D3)
  H1 hover        the box beside the panel: the name alone in line 1, centred
                  (±1 px), what it is and its state below; a locked chapter: 🔒
                  and the reason
  X2 pips         chapter 1's mark carries one pip per exercise (calc t1, code
                  t1) with its state; t1 answered right → pip and mark solved,
                  XP 1 / n
  M2 mode         calc: no code pip or mark · plain: no pip, no exercise mark
  Y1 own cells    a mark "Your own cells"; its click brings it to the reading height ±2 px (E33 B4; was: the window to the end)
  R1 reading ht.  the marker dragged 60 px down → the line 60 px lower (±2),
                  a pinned heading goes with it; kept after reload
  N1 text size    A+ ×2 → --nbfs 1.2 on the window, the text × 1.2 (±0.15 px),
                  the lens unchanged; kept after reload; double click → 100 %
  L2 language     DE chosen on the preview, the document built English: the
                  window shows ONE language — contents list, panel words and
                  mark names English, one line (German) says why; EN → no line
  B5 too wide     dark host, the output 320 px wider than its frame (PyCharm
                  dark): the panel inside the frame (right edge ≤ frame), the
                  tools too, |title card middle − visible window middle| ≤ 1 px
v1.76: red (M1, L1, P1, F1, K1, H1, X2, Y1, R1, N1, L2, B5). Owner: JS.
exit 0 = REGRESS-JS-E30 OK."""
import sys, os, re, json, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from env_iframe import run_cell, host_page
from env_reader import serve, PLAY

FR = """() => { var f = [].slice.call(document.querySelectorAll('iframe.out')).filter(function(x){
  try { return !!x.contentDocument.querySelector('.nbrw'); } catch (e) { return false; } })[0];
  return f ? [].indexOf.call(document.querySelectorAll('iframe.out'), f) : -1; }"""

# the reading version's own headings, found WITHOUT the panel's code: a chapter
# = the contents list's anchor, whose fold follows it; a part = a fold of kind
# group; the title = the card. Returns [{kind, name, y}] in the frame's viewport.
HEADS = r"""() => { var w = document.querySelector('.nbrw-win'), out = [];
  var mid = function (e) { if (!e || !e.getClientRects().length) return null; var r = e.getBoundingClientRect(); return r.height > 0 ? r.top + r.height / 2 : null; };
  [].forEach.call(document.querySelectorAll('ol.nbread-toc a[href^="#"]'), function (a, i) {
    var t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))), d = t && t.parentElement && t.parentElement.nextElementSibling;
    var h = d && d.tagName === 'DETAILS' ? d.querySelector(':scope>summary .nbread-h') : null;
    out.push({kind: 'chap', i: i, y: mid(h)}); });
  [].forEach.call(document.querySelectorAll('details[data-kind=group]'), function (d, i) { out.push({kind: 'group', i: i, y: mid(d.querySelector(':scope>summary .nbread-h'))}); });
  var c = document.querySelector('.nbrw-doc [class*="nbtitle-card"]'); out.push({kind: 'title', i: 0, y: mid(c)});
  return out; }"""
MARKS = r"""() => { var by = {}; [].forEach.call(document.querySelectorAll('.nbrw-mark'), function (m) {
    var k = m.getAttribute('data-kind'), r = m.getBoundingClientRect(), on = !!m.getClientRects().length && getComputedStyle(m).display !== 'none';
    (by[k] = by[k] || []).push({y: on ? r.top + r.height / 2 : null, st: m.getAttribute('data-st'), name: (m.querySelector('.nbrw-lab') || m).textContent.trim()}); });
  return by; }"""
LINE = """() => { var w = document.querySelector('.nbrw-win'), R = window.__nbReader; return w.getBoundingClientRect().top + (R && R.line ? R.line() : NaN); }"""
HEAD_OF = """(i) => { var a = document.querySelectorAll('ol.nbread-toc a[href^="#"]')[i], t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
  var d = t.parentElement.nextElementSibling, h = d.querySelector(':scope>summary .nbread-h'); if (!h.getClientRects().length) return {y: null, open: d.open};
  var r = h.getBoundingClientRect(); return {y: r.top + r.height / 2, open: d.open, locked: !!d.querySelector('[data-nbrw-gate][data-st=locked]')}; }"""

def frame(pg):
    fi = pg.evaluate(FR)
    if fi < 0: return None, None
    return [f for f in pg.frames if f != pg.main_frame][fi], pg.query_selector_all("iframe.out")[fi]

def main():
    import nbpick
    args = sys.argv[1:]
    src = nbpick.from_argv(sys.argv)
    shots = args[args.index("--shots") + 1] if "--shots" in args else None
    jout = args[args.index("--json") + 1] if "--json" in args else None
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    rows, fails = [], []
    def bad(m): fails.append(m)
    tmpd = tempfile.mkdtemp(prefix="jse30_"); srv = serve(tmpd)
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    outs, errs, chapters = run_cell(src, {})
    if errs: bad("the run raised: %s" % errs[:1])
    def page(name, oo, dark):
        h = host_page(oo, dark).replace("</iframe><script>", "</iframe><div style='height:2400px'></div><script>", 1)
        if "height:2400px" not in h: h = h.replace("<script>function fit", "<div style='height:2400px'></div><script>function fit", 1)
        open(os.path.join(tmpd, name), "w", encoding="utf-8").write(h)
    # B6 markup (claude/VERTRAG-E30-py.md): Python ships Lab's panel as <template class="nbrw-rail"> in the reading
    # version; before py-E30 is merged, a STAND-IN from the same run: the panel's HTML of the kernel's own widget
    # (the progress feed), targets put on the reading version's ids (nbr-…) as the contract says
    used = "real"
    for o in outs:
        hh = o["data"].get("text/html") or ""
        # E33 A1 (Python): the static copy carries the template in <script type=application/json data-nbrw-put>
        if hh.startswith("<div class='nbreading'") and not re.search(r"<template class=[\"']nbrw-rail|data-nbrw-put>[^<]*nbrw-rail", hh.split("<script>")[0]):
            feeds = [m.get("value") for m in (o.get("models") or {}).values() if isinstance(m.get("value"), str) and "nbmap-node" in m.get("value")]
            if feeds:
                f = min(feeds, key=len)
                f = re.sub(r'(data-target|href)="#?([^"#][^"]*)"', lambda m: '%s="%snbr-%s"' % (m.group(1), "#" if m.group(1) == "href" else "", m.group(2)), f)
                k = hh.find("</div><script>")
                o["data"] = dict(o["data"]); o["data"]["text/html"] = hh[:k] + "<template class='nbrw-rail' data-lang='en'>" + f + "</template>" + hh[k:]
                used = "stand-in"
    rows.append("B6 markup: %s" % used)
    page("light.html", outs, False)
    wide = [dict(o, data=dict(o["data"])) for o in outs]
    for o in wide:
        hh = o["data"].get("text/html") or ""
        if hh.startswith("<div class='nbreading'"):
            o["data"]["text/html"] = "<div style='width:calc(100% + 320px)'>" + hh + "</div>"
    page("wide.html", wide, True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            ctx = b.new_context(viewport={"width": 1400, "height": 900})
            pg = ctx.new_page(); pg.goto(base + "light.html"); pg.wait_for_timeout(3000)
            fr, fe = frame(pg)
            if not fr: raise RuntimeError("no reading window")
            S = lambda js, a=None: fr.evaluate(js, a)
            def onscreen():
                pg.evaluate("y => window.scrollTo(0, y)", int(fe.bounding_box()["y"] + pg.evaluate("window.scrollY") - 10)); pg.wait_for_timeout(150)
            def at(sel_js, a=None):   # page coordinates of an element of the frame (its middle)
                r = S("([s, a]) => { var e = (new Function('a', 'return ' + s))(a); if (!e) return null; var r = e.getBoundingClientRect(); return [r.left + Math.min(8, r.width / 2), r.top + r.height / 2]; }", [sel_js, a])
                if not r: return None
                bx = fe.bounding_box(); return bx["x"] + r[0], bx["y"] + r[1]
            def click(sel_js, a=None):
                xy = at(sel_js, a)
                if not xy: return False
                pg.mouse.click(*xy); return True
            def wtop(): return S("() => document.querySelector('.nbrw-win').scrollTop")
            def setTop(y): S("y => { document.querySelector('.nbrw-win').scrollTop = y; }", y); pg.wait_for_timeout(200)
            def pinned(i):  # |heading of chapter i − reading line|
                h = S(HEAD_OF, i); ln = S(LINE)
                return None if h["y"] is None or ln != ln else h["y"] - ln
            S(PLAY); pg.wait_for_timeout(500); onscreen()
            # ---- M1 map
            def mapcheck(tag):
                hs, ms = S(HEADS), S(MARKS); n, worst, miss = 0, 0.0, []
                for h in hs:
                    if h["y"] is None: continue
                    lst = ms.get(h["kind"]) or []
                    m = lst[h["i"]] if h["i"] < len(lst) else None
                    tr = S("() => { var r = document.querySelector('.nbrw-track').getBoundingClientRect(); return [r.top, r.bottom]; }")
                    if not (tr[0] + 2 <= h["y"] <= tr[1] - 2): continue          # outside the timeline's height: no mark
                    if not m or m["y"] is None: miss.append("%s %d" % (h["kind"], h["i"] + 1)); continue
                    n += 1; worst = max(worst, abs(m["y"] - h["y"]))
                rows.append("M1 map %s: %d marks at their headings, worst %.1f px, missing %s" % (tag, n, worst, miss or "none"))
                if n < 2: bad("M1 %s: only %d marks beside headings (missing %s)" % (tag, n, miss))
                if worst > 2: bad("M1 %s: a mark %.1f px off its heading" % (tag, worst))
                if miss: bad("M1 %s: headings in view without a mark: %s" % (tag, miss))
            # E33 B4 (Werkstatt JS): room to scroll above the title — the document's top is below it (behauptete bisher: scrollTop 0)
            setTop(S("() => { var p = document.querySelector('.nbrw-pad[data-at=top]'); return p ? p.offsetHeight : 0; }")); mapcheck("top")
            y2 = S("() => { var a = document.querySelectorAll('ol.nbread-toc a[href^=\"#\"]')[1], t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));"
                   " var w = document.querySelector('.nbrw-win'); return t.parentElement.nextElementSibling.getBoundingClientRect().top - w.getBoundingClientRect().top + w.scrollTop; }")
            setTop(max(0, y2 - 120)); mapcheck("locked chapters")
            lk = [m["y"] for m in (S(MARKS).get("chap") or []) if m["st"] == "locked" and m["y"] is not None]
            gaps = [b2 - a2 for a2, b2 in zip(lk, lk[1:])]
            rows.append("M1 locked chapter marks drawn %d, gaps %s px" % (len(lk), [round(g) for g in gaps]))
            if len(lk) < 2: bad("M1 fewer than two locked chapter marks drawn around the locked chapters (%d)" % len(lk))
            if gaps and min(gaps) < 10: bad("M1 locked chapters bunched: gaps %s" % gaps)
            if shots: pg.screenshot(path=os.path.join(shots, "E30-js-B6-gesperrt-hell.png"))
            # ---- L1 land
            S("() => { var a = document.querySelectorAll('ol.nbread-toc a[href^=\"#\"]')[0], t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))); t.parentElement.nextElementSibling.open = false; }")
            y1 = S("() => { var a = document.querySelectorAll('ol.nbread-toc a[href^=\"#\"]')[0], t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));"
                   " var w = document.querySelector('.nbrw-win'); return t.parentElement.nextElementSibling.getBoundingClientRect().top - w.getBoundingClientRect().top + w.scrollTop; }")
            setTop(max(0, y1 - 380))
            M0 = "document.querySelectorAll('.nbrw-mark[data-kind=chap]')[0]"
            ok = click(M0); pg.wait_for_timeout(800)
            h = S(HEAD_OF, 0); d = pinned(0)
            cur = S("() => document.querySelector('.nbrw-cur').textContent.trim()")
            want = S("() => document.querySelectorAll('ol.nbread-toc a')[0].innerText.replace(/\\s+/g, ' ').trim()")
            rows.append("L1 click chapter 1 (folded): clicked %s, open %s, heading %s px from the line, panel %r" % (ok, h["open"], None if d is None else round(d, 1), cur))
            if not ok or not h["open"] or d is None or abs(d) > 2 or cur != want:
                bad("L1 chapter 1: clicked %s, open %s, %s px off the line, panel %r (want %r)" % (ok, h["open"], d, cur, want))
            # ---- P1 pin
            pw = []
            for what, js in (("intro shut", "() => { document.querySelector('details[data-kind=group]').open = false; }"),
                             ("intro open", "() => { document.querySelector('details[data-kind=group]').open = true; }"),
                             ("lens +", "() => document.querySelector('.nbrw-btn[data-act=\"a+\"]').click()"),
                             ("text +", "() => { var b = document.querySelector('.nbrw-btn[data-act=\"f+\"]'); if (b) b.click(); return !!b; }"),
                             ("window ↕+", "() => document.querySelector('.nbrw-btn[data-act=\"h+\"]').click()"),
                             ("lens −", "() => document.querySelector('.nbrw-btn[data-act=\"a-\"]').click()"),
                             ("text −", "() => { var b = document.querySelector('.nbrw-btn[data-act=\"f-\"]'); if (b) b.click(); }"),
                             ("window ↕−", "() => document.querySelector('.nbrw-btn[data-act=\"h-\"]').click()")):
                S(js); pg.wait_for_timeout(450); d = pinned(0); pw.append((what, None if d is None else round(d, 1)))
            rows.append("P1 pinned through: %s" % " · ".join("%s %s" % x for x in pw))
            for what, d in pw:
                if d is None or abs(d) > 2: bad("P1 after %s chapter 1 is %s px off the line" % (what, d))
            # ---- P2 a script's scroll lets the anchor go (Lab E23.15 Nach-Runde; env_reader W7 dragged against it)
            S("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(700)
            p2 = wtop()
            rows.append("P2 a script scrolls to 0 while chapter 1 is pinned: window at %d px after 0.7 s" % p2)
            if p2 > 1: bad("P2 the pin pulled the window back to %d px after a script's scroll to 0" % p2)
            S("() => document.querySelectorAll('ol.nbread-toc a')[0].click()"); pg.wait_for_timeout(600)
            # ---- T1 the thumb is not under a mark, no mark under the thumb
            t1r = S("""() => { var t = document.querySelector('.nbrw-thumb').getBoundingClientRect(), hit = document.elementFromPoint(t.left + t.width / 2, t.top + t.height / 2);
              var bad = [].filter.call(document.querySelectorAll('.nbrw-mark'), function (m) { if (!m.getClientRects().length) return false;
                var r = m.getBoundingClientRect(), e = document.elementFromPoint(r.left + 4, r.top + r.height / 2); return !(e && e.closest('.nbrw-mark') === m); }).length;
              return [hit ? hit.className : null, bad]; }""")
            rows.append("T1 at the thumb's middle: %s · marks whose dot is covered: %d" % tuple(t1r))
            # E31 S1 (js-E31; nachgetragen von der Hauptwerkstatt beim Zusammenführen — der Patch nannte es, trug es nicht):
            # the thumb is `.nbrw-thumb.nbrw-sb-th` in the tool column (behauptete bisher: className exactly "nbrw-thumb")
            if "nbrw-thumb" not in (t1r[0] or "").split() or t1r[1]: bad("T1 thumb/marks overlap: %s" % t1r)
            # ---- F1 fold
            t0 = wtop(); ok = click(M0); pg.wait_for_timeout(600); h = S(HEAD_OF, 0); d = pinned(0)
            rows.append("F1 second click: open %s, %s px from the line" % (h["open"], None if d is None else round(d, 1)))
            if h["open"] or d is None or abs(d) > 2: bad("F1 chosen mark clicked again: open %s, %s px off the line" % (h["open"], d))
            # ---- H1 hover (chapter 1)
            xy = at(M0); pg.mouse.move(xy[0] + 3, xy[1]); pg.wait_for_timeout(300)
            tip = S("""() => { var t = document.querySelector('.nbrw-tip'); if (!t || !t.getClientRects().length || getComputedStyle(t).display === 'none') return null;
              var hd = t.firstElementChild, tb = t.getBoundingClientRect(), rg = document.createRange(); rg.selectNodeContents(hd); var ir = rg.getBoundingClientRect();
              var r2 = t.lastElementChild.getBoundingClientRect();
              return {head: hd.textContent, text: t.lastElementChild.textContent, dx: (ir.left + ir.width / 2) - (tb.left + tb.width / 2), below: r2.top >= ir.bottom - 0.5,
                      name: document.querySelectorAll('.nbrw-mark[data-kind=chap]')[0].querySelector('.nbrw-lab').textContent}; }""")
            rows.append("H1 hover chapter 1: %s" % (tip and {k: (v[:60] if isinstance(v, str) else round(v, 1) if isinstance(v, float) else v) for k, v in tip.items()}))
            if not tip: bad("H1 no hover box over the chapter mark")
            elif tip["head"] != tip["name"] or abs(tip["dx"]) > 1 or not tip["text"].strip() or not tip["below"]:
                bad("H1 hover box: head %r (name %r), off-centre %.1f px, text %r, below %s" % (tip["head"], tip["name"], tip["dx"], tip["text"][:40], tip["below"]))
            pg.mouse.move(5, 5); pg.wait_for_timeout(200)
            # H1 c: Lab's names and words from Python's template (VERTRAG-E30-py B6)
            nm = S("() => [].map.call(document.querySelectorAll('.nbrw-mark'), function (m) { return [m.getAttribute('data-kind'), (m.querySelector('.nbrw-lab') || m).textContent]; })")
            labn = {k: v for k, v in nm if k in ("chap", "viz", "code") and k not in {}}
            first = {}
            for k, v in nm: first.setdefault(k, v)
            rows.append("H1 names from Lab's markup: chapter %r · figure %r · coding %r" % (first.get("chap"), first.get("viz"), first.get("code")))
            if not re.match(r"(Chapter|Kapitel) 1\b", first.get("chap") or "") or not re.match(r"(Figure|Abbildung) 1\b", first.get("viz") or "") \
               or not re.match(r"(Coding|Programmier\w*) 1\b", first.get("code") or ""):
                bad("H1 the marks do not carry Lab's names: %s" % first)
            # ---- X2 pips
            px = S("() => [].map.call(document.querySelectorAll('.nbrw-mark[data-kind=chap]')[0].querySelectorAll('.nbrw-pip'), function (p) { return [p.getAttribute('data-kind'), p.getAttribute('data-task'), p.getAttribute('data-st')]; })")
            S("() => { document.querySelectorAll('ol.nbread-toc a')[0].click(); }"); pg.wait_for_timeout(300)
            S("() => { var t = document.querySelector('.nbrw-task[data-task=t1]'); for (var x = t.parentElement; x; x = x.parentElement) if (x.tagName === 'DETAILS') x.open = true; t.scrollIntoView({block: 'center'}); }"); pg.wait_for_timeout(150)
            a = S("() => JSON.parse(atob(document.querySelector('.nbrw-task[data-task=t1]').getAttribute('data-a')))")
            if "c" in a: fr.click('.nbrw-task[data-task=t1] input[type=radio][value="%d"]' % a["c"])
            for x in a.get("f", []): fr.fill('.nbrw-task[data-task=t1] .nbrw-input[data-f="%s"]' % x[0], str(x[1]))
            fr.click(".nbrw-task[data-task=t1] .nbrw-check"); pg.wait_for_timeout(400)
            px2 = S("() => [].map.call(document.querySelectorAll('.nbrw-mark[data-kind=chap]')[0].querySelectorAll('.nbrw-pip'), function (p) { return [p.getAttribute('data-kind'), p.getAttribute('data-task'), p.getAttribute('data-st')]; })")
            mk1 = S("() => { var m = document.querySelector('.nbrw-mark[data-kind=calc][data-task=t1]'); return m && m.getAttribute('data-st'); }")
            xpt = S("() => document.querySelector('.nbrw-xp-t').textContent")
            rows.append("X2 pips of chapter 1: %s → t1 right: %s, mark %s, XP %r" % (px, px2, mk1, xpt))
            if [x[:2] for x in px] != [["calc", "t1"], ["code", "t1"]] or any(x[2] != "open" for x in px): bad("X2 pips of chapter 1 %s, want calc t1 + code t1 open" % px)
            if not any(x[:3] == ["calc", "t1", "solved"] for x in px2) or mk1 != "solved" or not re.search(r"\b1 / \d+", xpt): bad("X2 after t1 right: pips %s, mark %s, XP %r" % (px2, mk1, xpt))
            # ---- K1 locked (chapter 3 — chapter 2 opened with t1)
            y3 = S("() => { var a = document.querySelectorAll('ol.nbread-toc a[href^=\"#\"]')[2], t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));"
                   " var w = document.querySelector('.nbrw-win'); return t.parentElement.nextElementSibling.getBoundingClientRect().top - w.getBoundingClientRect().top + w.scrollTop; }")
            setTop(max(0, y3 - 300)); onscreen()
            M2_ = "document.querySelectorAll('.nbrw-mark[data-kind=chap]')[2]"
            st3 = S("() => document.querySelectorAll('.nbrw-mark[data-kind=chap]')[2].getAttribute('data-st')")
            t0 = wtop(); ok = click(M2_); pg.wait_for_timeout(500); t1 = wtop()
            box = S("() => { var t = document.querySelector('.nbrw-tip'); return t && getComputedStyle(t).display !== 'none' ? t.textContent : null; }")
            st3b = S("() => document.querySelectorAll('.nbrw-mark[data-kind=chap]')[2].getAttribute('data-st')")
            pip = S("() => !!document.querySelectorAll('.nbrw-mark[data-kind=chap]')[2].querySelector('.nbrw-pip')")
            ok2, t2 = None, t1
            if pip:
                pg.mouse.click(5, 5); pg.wait_for_timeout(150)
                ok2 = click("document.querySelectorAll('.nbrw-mark[data-kind=chap]')[2].querySelector('.nbrw-pip')"); pg.wait_for_timeout(500); t2 = wtop()
            rows.append("K1 locked chapter 3 (%s): mark clicked %s → window %+d px, box %r · pip clicked %s → %+d px, still %s" % (st3, ok, t1 - t0, (box or "")[:70], ok2, t2 - t0, st3b))
            if st3 != "locked": bad("K1 chapter 3 is %s, want locked" % st3)
            if not ok or abs(t1 - t0) > 1 or not box or not re.search(r"(Exercise|Aufgabe) 2", box): bad("K1 locked mark: clicked %s, window %+d px, box %r" % (ok, t1 - t0, box))
            if pip and abs(t2 - t0) > 1: bad("K1 a locked chapter's pip moved the window %+d px" % (t2 - t0))
            if st3b != "locked": bad("K1 chapter 3 unlocked by a click")
            # H1 b: hover over the locked mark
            pg.mouse.click(5, 5); pg.wait_for_timeout(150)
            xy = at(M2_); pg.mouse.move(xy[0] + 3, xy[1]); pg.wait_for_timeout(300)
            tl = S("() => { var t = document.querySelector('.nbrw-tip'); return t && getComputedStyle(t).display !== 'none' ? [t.firstElementChild.textContent, t.lastElementChild.textContent] : null; }")
            rows.append("H1 hover locked chapter 3: %s" % tl)
            if not tl or not tl[0].startswith("\U0001F512") or not re.search(r"(Exercise|Aufgabe) 2", tl[1]): bad("H1 locked chapter's box %s" % tl)
            if shots:
                pg.screenshot(path=os.path.join(shots, "E30-js-B6-hover-hell.png"))
            pg.mouse.move(5, 5)
            # ---- Y1 own cells
            ny = S("() => document.querySelectorAll('.nbrw-mark[data-kind=yoc]').length")
            setTop(10 ** 6); pg.wait_for_timeout(200); setTop(wtop() - 200)
            S("() => { var m = document.querySelector('.nbrw-mark[data-kind=yoc]'); if (m) m.click(); }"); pg.wait_for_timeout(500)
            # E33 B4 (Werkstatt JS): with room below the end the own cells come to the reading height like every mark
            # (behauptete bisher: the window at its end, 0 px left)
            end = S("""() => { var w = document.querySelector('.nbrw-win'), e = document.querySelector('.nbrw-doc [id^="nbr-nbyoc"]'), R = window.__nbReader;
              if (!e) return 1e9; var r = e.getBoundingClientRect(); return Math.abs(r.top + r.height / 2 - (w.getBoundingClientRect().top + R.line())); }""")
            rows.append("Y1 own-cells marks %d, after its click %.1f px from the reading height" % (ny, end))
            if ny != 1 or end > 2: bad("Y1 own cells: %d marks, %.1f px from the reading height" % (ny, end))
            # ---- M2 mode
            res = {}
            for m in ("calc", "plain", "both"):
                fr.click(".nbrw-btn[data-act=cover]"); pg.wait_for_timeout(150)
                fr.click('.nbrw-mode-opt[data-mode="%s"]' % m); fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(350)
                res[m] = S("() => [document.querySelectorAll('.nbrw-pip[data-kind=calc]').length, document.querySelectorAll('.nbrw-pip[data-kind=code]').length,"
                           " document.querySelectorAll('.nbrw-mark[data-kind=calc]').length, document.querySelectorAll('.nbrw-mark[data-kind=code]').length]")
            rows.append("M2 mode [pips calc, code, marks calc, code]: %s" % res)
            if res["calc"][1] or res["calc"][3] or not res["calc"][0]: bad("M2 calc: %s" % res["calc"])
            if any(res["plain"]): bad("M2 plain: %s" % res["plain"])
            if not (res["both"][0] and res["both"][1]): bad("M2 both: %s" % res["both"])
            # ---- R1 reading height
            onscreen()
            l0 = S("() => window.__nbReader.line ? window.__nbReader.line() : null")
            S("() => document.querySelectorAll('ol.nbread-toc a')[0].click()"); pg.wait_for_timeout(500)
            rl = at("document.querySelector('.nbrw-rl')")
            if rl and l0 is not None:
                pg.mouse.move(*rl); pg.mouse.down(); pg.mouse.move(rl[0], rl[1] + 30, steps=5); pg.mouse.move(rl[0], rl[1] + 60, steps=5); pg.mouse.up()
                pg.wait_for_timeout(400)
            l1 = S("() => window.__nbReader.line ? window.__nbReader.line() : null"); d = pinned(0)
            pg.reload(); pg.wait_for_timeout(3000); fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a); S(PLAY); pg.wait_for_timeout(300)
            l2 = S("() => window.__nbReader.line ? window.__nbReader.line() : null")
            rows.append("R1 reading height %s → dragged %s (chapter 1 %s px off) → after reload %s" % (l0, l1, None if d is None else round(d, 1), l2))
            if l0 is None or l1 is None or abs(l1 - l0 - 60) > 2 or l2 != l1 or d is None or abs(d) > 2:
                bad("R1 reading height %s → %s → %s, chapter %s px off the line" % (l0, l1, l2, d))
            onscreen()
            # ---- N1 text size
            G = "() => [getComputedStyle(document.querySelector('.nbrw')).getPropertyValue('--nbfs').trim(), parseFloat(getComputedStyle(document.querySelector('.nbreading')).fontSize), window.__nbReader.zoom()]"
            n0 = S(G)
            has = S("() => !!document.querySelector('.nbrw-btn[data-act=\"f+\"]')")
            if has:
                fr.click('.nbrw-btn[data-act="f+"]'); fr.click('.nbrw-btn[data-act="f+"]'); pg.wait_for_timeout(200)
            n1 = S(G)
            pg.reload(); pg.wait_for_timeout(3000); fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a); S(PLAY); pg.wait_for_timeout(300)
            n2 = S(G)
            if has: fr.dblclick(".nbrw-fs .nbfs-val"); pg.wait_for_timeout(200)
            n3 = S(G)
            rows.append("N1 text size %s → A+ ×2 %s → reload %s → double click %s" % (n0, n1, n2, n3))
            if not has or n1[0] != "1.2" or abs(n1[1] - n0[1] * 1.2) > 0.15 or n1[2] != n0[2] or n2[:2] != n1[:2] or abs(n3[1] - n0[1]) > 0.05:
                bad("N1 text size: %s → %s → %s → %s" % (n0, n1, n2, n3))
            # ---- L2 language
            fr.click(".nbrw-btn[data-act=cover]"); pg.wait_for_timeout(150)
            hasde = S("() => !!document.querySelector('.nbrw-cover [data-lang=de]')")
            if hasde: fr.click(".nbrw-cover [data-lang=de]"); pg.wait_for_timeout(200)
            fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(400)
            lg = S("""() => { var vis = function (e) { return !!e.getClientRects().length && getComputedStyle(e).display !== 'none'; };
              var toc = [].filter.call(document.querySelectorAll('ol.nbread-toc span[data-nbrw-l]'), vis).map(function (e) { return e.getAttribute('data-nbrw-l'); });
              var n = document.querySelector('.nbrw-langnote');
              return {doc: document.querySelector('.nbreading').getAttribute('data-nbread') && (window.__nbReader.shown ? window.__nbReader.shown() : document.querySelector('.nbrw').getAttribute('data-nbrw-lang')),
                      toc: toc.filter(function (x, i, a) { return a.indexOf(x) === i; }), btn: document.querySelector('.nbrw-btn[data-act="h+"]').title,
                      chap: document.querySelectorAll('.nbrw-mark[data-kind=chap]')[0].querySelector('.nbrw-lab').textContent, note: n && vis(n) ? n.textContent : null,
                      toc0: document.querySelectorAll('ol.nbread-toc a')[0].innerText.replace(/\\s+/g, ' ').trim(),
                      built: document.querySelector('.nbrw-doc .nbread-end') ? document.querySelector('.nbrw-doc .nbread-end').textContent : ''}; }""")
            rows.append("L2 DE chosen, document built %r: TOC %s, panel %r, chapter mark %r, line %r" % (lg["built"][:24], lg["toc"], lg["btn"], lg["chap"][:30], (lg["note"] or "")[:80]))
            if shots and hasde: onscreen(); pg.screenshot(path=os.path.join(shots, "E30-js-B2-sprache-de-hell.png"))
            de_doc = bool(re.search(r"Ende|geführt", lg["built"]))
            if lg["toc0"] not in lg["chap"]: bad("L2 chapter mark %r, contents list %r — two languages" % (lg["chap"], lg["toc0"]))
            if not hasde: bad("L2 no DE on the preview")
            elif de_doc:
                if lg["toc"] != ["de"] or lg["btn"] != "Fenster höher" or lg["note"]: bad("L2 German document, window %s" % lg)
            else:
                if lg["toc"] != ["en"] or lg["btn"] != "Taller window" or not lg["note"] or "Englisch" not in lg["note"]:
                    bad("L2 English document with DE chosen: TOC %s, panel %r, line %r — not one language" % (lg["toc"], lg["btn"], lg["note"]))
            fr.click(".nbrw-btn[data-act=cover]"); pg.wait_for_timeout(150)
            if hasde: fr.click(".nbrw-cover [data-lang=en]"); pg.wait_for_timeout(150)
            fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(300)
            nn = S("() => { var n = document.querySelector('.nbrw-langnote'); return n && n.getClientRects().length ? n.textContent : null; }")
            if nn: bad("L2 EN chosen, English document: the line is still there %r" % nn)
            if shots:
                S("() => document.querySelectorAll('ol.nbread-toc a')[0].click()"); pg.wait_for_timeout(500); onscreen()
                pg.screenshot(path=os.path.join(shots, "E30-js-B6-panel-hell.png"))
            ctx.close()
            # ---- B5 too wide (dark)
            ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark")
            pg = ctx.new_page(); pg.goto(base + "wide.html"); pg.wait_for_timeout(3000)
            fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a)
            S(PLAY); pg.wait_for_timeout(600); onscreen()
            g = S("""() => { var vw = document.documentElement.clientWidth, p = document.querySelector('.nbrw-panel').getBoundingClientRect(),
                t = document.querySelector('.nbrw-tools'), tb = t ? t.getBoundingClientRect() : null, w = document.querySelector('.nbrw-win').getBoundingClientRect(),
                c = document.querySelector('.nbrw-doc [class*="nbtitle-card"]').getBoundingClientRect();
              var vl = Math.max(0, w.left), vr = Math.min(vw, w.right);
              return {vw: vw, pr: p.right, pl: p.left, tl: tb ? tb.left : null, card: c.left + c.width / 2, mid: (vl + vr) / 2}; }""")
            rows.append("B5 output 320 px wider than its frame (dark): frame %d px, panel %.0f–%.0f, tools from %s, card middle %.1f, visible middle %.1f" % (
                g["vw"], g["pl"], g["pr"], g["tl"], g["card"], g["mid"]))
            if g["pr"] > g["vw"] + 0.5 or (g["tl"] is not None and g["tl"] < -0.5) or abs(g["card"] - g["mid"]) > 1:
                bad("B5 panel to %.0f of %d px, tools from %s, card %.1f px off the visible middle" % (g["pr"], g["vw"], g["tl"], g["card"] - g["mid"]))
            if shots: pg.screenshot(path=os.path.join(shots, "E30-js-B5-breit-dunkel.png"))
            ctx.close()
        except Exception as e:
            import traceback; traceback.print_exc()
            fails.append("BAD %s" % str(e)[:300])
        b.close()
    srv.shutdown(); shutil.rmtree(tmpd, ignore_errors=True)
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-JS-E30 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
