"""E22 · test_regress — the Python workshop's part of E22 (points 2 and 3).

In the matrix (TESTS, every row, real JupyterLab after Run All):
  PY-E22.2a  the answer box takes a decimal comma. Exercise 1 is answered by
             real keystrokes with a comma ("3,0" in Complex — the answer is a
             whole number, typed as a German reader types it; Modeling the
             order of magnitude to 4 places, "6,5563"), Check → ✓.
             v1.62/v1.63: the box is an <input type=number>; Chromium drops
             the comma while it is typed ("3,0" → 30, "2,5" → 25, en-US and
             de-DE alike) → "not there yet". Owner: Python.
             Changes the progress (exercise 1 solved): the last test of the
             last module.

Stand-alone (stage 2, scripts.txt: one run per notebook):
    python3 tests/regress/py_e22.py <notebook.ipynb>
  PY-E22.2b  the German edition, in the browser: a fresh copy is run with the
             language stored as the reader stores it (~/.digichemjn/lang = de);
             the feed says data-nblang="de" (precondition). In the whole
             notebook (cover, document, every fold, hidden or not; without
             <code>, <pre>, editors, inputs, formulas and figures):
               du   0 words du/dich/dir/dein… and 0 sentences opened by a
                    du-imperative (Gib, Zieh, Schreib, Probier, Stell …)
               pt   0 decimals written with a point (2.5) in the text;
                    section numbers ("Abschnitt 1.2"), versions, dates, DOIs
                    and addresses are not decimals
               fb   exercise 1 answered wrong with a comma: the feedback names
                    the typed number with a comma (Complex "Sie haben 1,5
                    eingegeben"); then answered right with a comma → ✓ and,
                    in Modeling, the right result is said with a comma
             v1.62 + py-E17.1: du everywhere, 2.5 in the text, "1,5" → 15.
             Owner: Python (texts, kernel); JS where the text comes from a
             script (the account block, the 👤 window).
  PY-E22.3   (PyCharm output form) is tests/regress/py_e22p.py.
exit 0 = REGRESS-PY-E22 OK."""
import sys, os, re, json, time, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

FRONT = """var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"""

# the boxes of exercise 1 (by their label), their folds opened the reader's way
# (a click on each closed header, outermost first), tagged for the keyboard
BOXES_JS = r"""(rx) => { """ + FRONT + r"""
  if (!P) return {err: 'no notebook'};
  var R = rx.map(function(s){ return new RegExp(s); }), out = [];
  var ws = [].slice.call(P.querySelectorAll('.widget-text')).filter(function(w){
      var l = w.querySelector('label'); return l && R.some(function(r){ return r.test(l.textContent.trim()); }); });
  R.forEach(function(r, j){ var w = ws.filter(function(w){ return r.test(w.querySelector('label').textContent.trim()); })[0];
      if (w) { w.querySelector('input').setAttribute('data-e22', 'in' + j); out.push(j); } });
  if (out.length !== R.length) return {err: 'boxes found ' + out.length + ' of ' + R.length};
  var w0 = P.querySelector('[data-e22="in0"]'), heads = [], c = w0;
  while (c && c !== P) {
    if (c.classList && c.classList.contains('jupyter-widget-Collapse-contents') && c.classList.contains('lm-mod-hidden')) {
      var h = c.parentElement.querySelector(':scope > .jupyter-widget-Collapse-header'); if (h) heads.unshift(h); }
    c = c.parentElement; }
  heads.forEach(function(h, k){ h.setAttribute('data-e22h', String(k)); });
  var up = w0, b = null, k = 0;
  while (up && k < 12 && !b) { b = [].slice.call(up.querySelectorAll('button')).filter(function(x){
      return /Check answer|Antwort prüfen/.test(x.textContent); })[0]; up = up.parentElement; k++; }
  if (!b) return {err: 'no check button'};
  b.setAttribute('data-e22', 'chk');
  return {heads: heads.length, type: w0.getAttribute('type') || w0.type};
}"""
VERDICT_JS = r"""() => { var b = document.querySelector('button[data-e22="chk"]'); if (!b) return null;
  var up = b.parentElement, k = 0;
  while (up && k < 6) { var v = up.querySelector('.jp-OutputArea-output .nbok:not([data-e22old]), .jp-OutputArea-output .nbwarn:not([data-e22old])');
    if (v) { var a = v.closest('.jp-OutputArea') || v.parentElement;
             return [].map.call(a.querySelectorAll('.nbok, .nbwarn, .nbink, .nberr'), function(x){ return x.textContent.trim(); }); }
    up = up.parentElement; k++; }
  return null; }"""

def _task1(pg, nb):
    """(labels, values right, value wrong or None, a regex the ✓ tip must match or None)"""
    # the exercise text next to ITS boxes (the page may hold an older copy
    # of the document's numbers elsewhere, e.g. before a reseed)
    txt = pg.evaluate(r"""() => { """ + FRONT + r"""
      if (!P) return '';
      var w = [].filter.call(P.querySelectorAll('.widget-text'), function(w){
          var l = w.querySelector('label'); return l && /^(Re\(z\)|orders|Größenordnungen|y) =$/.test(l.textContent.trim()); })[0];
      var up = w, k = 0, rx = /personal value is|persönlicher Wert ist|takes about|dauert etwa/;
      while (up && k < 14) { if (rx.test(up.textContent)) return up.textContent; up = up.parentElement; k++; }
      return P.textContent; }""")
    if "Modeling" in nb:
        m = re.search(r"(?:takes about|dauert etwa)\s*(\d+)\s*ms.{0,200}?(?:over about|über etwa)\s*(\d+)\s*h", txt, re.S)
        if not m: return None
        q = math.log10(int(m.group(2)) * 3600 * 1000 / int(m.group(1)))
        return ([r"^(orders|Größenordnungen) =$"], [("%.4f" % q).replace(".", ",")], ["1,5"], r"= \d+,\d")
    if "Vorlage" in nb:                      # E28: the template's exercise 1, y = a·3 (behauptete bisher: Complex/Modeling only)
        m = re.search(r"(?:personal value is|persönliche[rn]? Wert (?:ist )?)\s*a\s*=\s*(\d+)", txt)
        if not m: return None
        return ([r"^y =$"], ["%d,0" % (3 * int(m.group(1)))], ["1,5"], None)
    m = re.search(r"(?:personal value is|persönliche[rn]? Wert (?:ist )?)\s*q\s*=\s*(\d+)", txt)
    if not m: return None
    r = int(round(int(m.group(1)) ** 0.5))
    return ([r"^Re\(z\) =$", r"^Im\(z\) =$"], ["0", "%d,0" % r], ["1,5", "%d,0" % r], None)

def _retag(pg, labs):
    """tag the boxes and the closed folds above them again: JupyterLab may have
    drawn the cell anew (windowing, a re-render) since the last look"""
    for _ in range(5):
        r = pg.evaluate(BOXES_JS, labs)
        if not r.get("err", "").startswith("boxes found 0"): return r
        # windowing: the document cell went out of the page (an own cell below
        # it is in view) — scroll up as the reader does, and look again
        pg.evaluate("() => { " + FRONT + " var o = P && P.querySelector('.jp-WindowedPanel-outer'); if (o) o.scrollTop = 0; }")
        pg.wait_for_timeout(1200)
    return r

def _do(pg, labs, sel, fn, tries=4):
    """fn(locator) on a freshly found element; again when it went away under the hand"""
    err = None
    for _ in range(tries):
        r = _retag(pg, labs)
        if r.get("err"): return "BAD " + r["err"]
        try:
            loc = pg.locator(sel).first
            loc.scroll_into_view_if_needed(timeout=5000)
            fn(loc); return None
        except Exception as e:
            err = str(e).split("\n")[0][:120]; pg.wait_for_timeout(500)
    return "BAD %s: %s" % (sel, err)

def answer(pg, nb, wrong=False):
    """Exercise 1 typed with a comma, Check clicked. Returns (verdict lines, detail) or (None, BAD …)."""
    # a rebuild may still be under way (a test before this one changed the
    # stored mode, py_e21 R6i): wait until the kernel is idle, no loading view
    # is up and the run id on the feed has stood for 3 s (≤ 120 s)
    last, since, t0 = None, time.time(), time.time()
    while time.time() - t0 < 120:
        st = pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
            var i = P && P.querySelector('.jp-Notebook-ExecutionIndicator'), f = P && P.querySelectorAll('.nbfeed[data-nbid]');
            return [i ? i.getAttribute('data-status') : 'idle', !!document.querySelector('#nbload:not(.nbload-out)'),
                    f && f.length ? f[f.length - 1].getAttribute('data-nbid') : null]; }""")
        if st[2] != last: last, since = st[2], time.time()
        if st[0] == "idle" and not st[1] and st[2] and time.time() - since >= 3: break
        pg.wait_for_timeout(500)
    # JupyterLab draws only the cells near the view (windowing): after an own
    # cell at the end the document cell may not be in the page at all. The
    # reader scrolls up; so does the test, until the boxes are there.
    for _ in range(6):
        if pg.evaluate("() => { " + FRONT + " return P ? P.querySelectorAll('.widget-text input').length : 0; }"): break
        pg.evaluate("() => { " + FRONT + " var o = P && P.querySelector('.jp-WindowedPanel-outer'); if (o) o.scrollTop = 0; }")
        pg.wait_for_timeout(1200)
    t = _task1(pg, nb)
    if not t: return None, "BAD exercise 1 text not found"
    labs, right, bad, _ = t
    vals = bad if wrong else right
    for _ in range(8):                       # open the folds above the boxes, outermost first
        r = _retag(pg, labs)
        if r.get("err"): return None, "BAD " + r["err"]
        if not r["heads"]: break
        e = _do(pg, labs, '[data-e22h="0"]', lambda l: l.click(timeout=5000))
        if e: return None, e
        pg.wait_for_timeout(700)
    for j, v in enumerate(vals):
        def typ(l, v=v):
            l.click(click_count=3, timeout=5000)
            pg.keyboard.press("Control+a"); pg.keyboard.press("Backspace")
            pg.keyboard.type(v, delay=50)
        e = _do(pg, labs, '[data-e22="in%d"]' % j, typ)
        if e: return None, e
        pg.wait_for_timeout(300)
    pg.wait_for_timeout(600)
    _retag(pg, labs)
    got = [pg.locator('[data-e22="in%d"]' % j).first.input_value() for j in range(len(vals))]
    pg.evaluate("() => document.querySelectorAll('.nbok, .nbwarn').forEach(function(e){ e.setAttribute('data-e22old', '1'); })")
    e = _do(pg, labs, 'button[data-e22="chk"]', lambda l: l.click(timeout=5000))
    if e: return None, e
    v = None
    for _ in range(80):                      # a right answer folds soon after ✓: read at once
        pg.wait_for_timeout(100); v = pg.evaluate(VERDICT_JS)
        if v: break
    return v, "typed %s, box shows %s (%s)" % (vals, got, r.get("type"))

def t_e22_2a(pg, ctx):
    # E24 Stufe 2 Rest 2: a page that lost widget models on a reload has no
    # exercise 1 to answer — say so (BAD with the cause), not "not found"
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _py_page import page_whole
    ok0, s0 = page_whole(pg)
    if not ok0: return False, s0
    v, det = answer(pg, ctx["nb"])
    if v is None: return False, det if det.startswith("BAD") else "BAD no verdict · " + det
    return v[0].startswith("✓"), "%s → %r" % (det, " | ".join(v)[:90])

TESTS = [("PY-E22.2a answer box takes 3,0 / 6,5563", t_e22_2a)]


# ---------------------------------------------------------------- stage 2
DU = re.compile(r"\b(du|Du|dich|Dich|dir|Dir|dein\w*|Dein\w*)\b")
IMP = re.compile(r"(?:^|[.!?:;]\s+|\n\s*)(Gib|Zieh|Nimm|Schreib|Probier|Stell|Schau|Lies|Prüfe|Klick|Wähle|Tippe|Drücke|"
                 r"Setz|Rechne|Addiere|Teile|Zähle|Multipliziere|Berechne|Beweg|Bewege|Achte|Denk|Fang|Vergiss|Antworte|"
                 r"Füge|Bewahre|Nenne|Definiere|Versuch|Lass|Halte|Mach|Ändere|Öffne|Starte|Geh|Sieh|Trag|Merk|Vergleiche|"
                 r"Erweitere|Quadriere|Löse|Arbeite|Bleib|Führe|Schreibe|Wähl|Klicke|Drück)\b(?!\s+Sie\b)")
PT = re.compile(r"(?<![\w.,/:\-])\d+\.\d+(?![\w.]|/)")
NOT_DEC = re.compile(r"(Abschnitt|Abschnitte|[Ss]ection|Kapitel|v|Version|build|BY|BY-SA|BY-NC|CC0|Python|JupyterLab)\s*$")

TEXT_JS = r"""(sel) => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); if (!P) return null;
  var root = sel ? document.querySelector(sel) : P; if (!root) return {lang: null, text: ''};
  var c = root.cloneNode(true);
  c.querySelectorAll('code, pre, textarea, input, select, script, style, svg, math, mjx-container, .MathJax, .CodeMirror, .cm-editor, .jp-InputArea, img, .widget-readout').forEach(function(e){ e.remove(); });
  var f = P.querySelectorAll('.nbfeed[data-nblang]'); f = f.length ? f[f.length-1].getAttribute('data-nblang') : null;
  c.querySelectorAll('div, p, li, td, br, summary, h1, h2, h3, h4, button, label').forEach(function(e){ e.appendChild(document.createTextNode('\n')); });
  [].forEach.call(root.querySelectorAll('[aria-label],[title],[placeholder]'), function(e){
    ['aria-label', 'title', 'placeholder'].forEach(function(k){ var v = e.getAttribute(k); if (v) c.appendChild(document.createTextNode('\n' + v + '.\n')); }); });
  return {lang: f, text: c.textContent}; }"""

def _hits(txt):
    du = sorted(set(m.group(0) for m in DU.finditer(txt)))
    imp = sorted(set(m.group(1) for m in IMP.finditer(txt)))
    pts = []
    for m in PT.finditer(txt):
        pre = txt[max(0, m.start() - 14):m.start()]
        if NOT_DEC.search(pre) or re.match(r"\d+\.\d+\s+des\s+Skripts", txt[m.start():m.start() + 20]):
            continue
        pts.append(txt[max(0, m.start() - 24):m.end() + 12].replace("\n", " "))
    return du, imp, pts

def german(b, base, root, src, rows, fails):
    import run as R
    from lab_keys import kill_sessions
    nid = R.nb_id(src)
    kill_sessions(base)
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    for d in (kh, root):
        shutil.rmtree(os.path.join(d, ".digichemjn"), ignore_errors=True)
    os.makedirs(os.path.join(kh, ".digichemjn"), exist_ok=True)
    open(os.path.join(kh, ".digichemjn", "lang"), "w").write("de")
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    # and in the page's profile, as the cover / 👤 store it (js-E17.1:
    # digichemjn.lang.v1) — since v1.63 the page tells the kernel its language
    # E28: the notebook under test by its id (the template: 'vorlage') — behauptete bisher: Complex/Modeling keys only
    ctx.add_init_script("try{['v1', 'complex-numbers', 'intro-modeling', %s].forEach(function(i){ localStorage.setItem('digichemjn.lang.' + i, 'de'); });}catch(e){}"
                        % json.dumps(nid))   # E25.o: the notebook's key (py-E25.o)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    name = "e22de_%d_%s" % (int(time.time()), os.path.basename(src))
    shutil.copy(src, os.path.join(root, name))
    pg.goto(base + "/lab/tree/" + name + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(1500)
    t = R.run_front(pg, nid)
    for _ in range(120):                     # a rebuild for the language may follow
        r = pg.evaluate(TEXT_JS)
        if r and r["lang"] == "de" and not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"): break
        pg.wait_for_timeout(1000)
    pg.wait_for_timeout(1500)
    # the cover is part of the text too: scroll up so JupyterLab draws it
    pg.evaluate("() => { " + FRONT + " var o = P && P.querySelector('.jp-WindowedPanel-outer'); if (o) o.scrollTop = 0; }")
    pg.wait_for_timeout(1500)
    r = pg.evaluate(TEXT_JS, None)
    if not r or r["lang"] != "de":
        fails.append("E22.2b precondition: the run is not German (data-nblang=%s)" % (r and r["lang"]))
        ctx.close(); return
    # the page's own words: the panel with the 👤 window open (JS writes them)
    try:
        pg.click("#nbpanel-root .nbbtn.nbprofile", timeout=5000); pg.wait_for_timeout(1200)
    except Exception:
        pass
    rp = pg.evaluate(TEXT_JS, "#nbpanel-root") or {"text": ""}
    pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
    rows.append("E22.2b de · run %.1f s · %d characters in the notebook, %d in the panel" % (t, len(r["text"]), len(rp["text"])))
    for where, owner, txt in (("notebook (document + cover)", "Python; cover words from JS", r["text"]),
                              ("panel + 👤 window", "JS", rp["text"])):
        du, imp, pts = _hits(txt)
        rows.append("E22.2b %s: du %d %s · imperatives %d %s · decimal points %d %s"
                    % (where, len(du), du[:6], len(imp), imp[:6], len(pts), pts[:3]))
        if du or imp: fails.append("E22.2b du-forms in the %s (%s): %s %s" % (where, owner, du[:8], imp[:8]))
        if pts: fails.append("E22.2b %d decimals with a point in the %s (%s): %s" % (len(pts), where, owner, pts[:3]))
    v, det = answer(pg, src, wrong=True)
    rows.append("E22.2b wrong with a comma: %s → %r" % (det, v and " | ".join(v)[:120]))
    if "Modeling" in src:
        okw = bool(v) and not v[0].startswith("✓")
    else:
        okw = bool(v) and any("1,5" in x for x in v) and not any(re.search(r"\b15\b|1\.5", x) for x in v)
    if not okw: fails.append("E22.2b a wrong answer typed with a comma: %s" % (v,))
    pg.evaluate("() => document.querySelectorAll('[data-e22],[data-e22h]').forEach(function(e){ e.removeAttribute('data-e22'); e.removeAttribute('data-e22h'); })")
    v, det = answer(pg, src)
    want_tip = _task1(pg, src)
    rows.append("E22.2b right with a comma: %s → %r" % (det, v and " | ".join(v)[:120]))
    ok = bool(v) and v[0].startswith("✓") and (not want_tip or not want_tip[3] or any(re.search(want_tip[3], x) for x in v))
    if not ok: fails.append("E22.2b the right answer typed with a comma: %s" % (v,))
    if errs: fails.append("E22.2b page errors: %s" % errs[:2])
    ctx.close()
    kill_sessions(base)
    try: os.remove(os.path.join(kh, ".digichemjn", "lang"))
    except OSError: pass

def main():
    src = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    rows, fails = [], []
    from lab_keys import ensure_lab, CHROME
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try: german(b, base, root, src, rows, fails)
        except Exception as e: fails.append("E22.2b BAD %s" % str(e)[:200])
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E22 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
