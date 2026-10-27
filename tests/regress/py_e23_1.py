"""E23.1 · test_regress, stage 2 (scripts.txt) — Python workshop (texts).
    python3 tests/regress/py_e23_1.py <notebook.ipynb>
  LANGUAGE EVERYWHERE (E23.1, Nutzer 06.10.: "0 englische Reste in sichtbarem
  Text, title-Tooltips, Hover-Boxen, data-desc, aria-label, Platzhaltern").
  A fresh copy is run German (the language stored as the reader stores it:
  ~/.digichemjn/lang and digichemjn.lang.v1 = de); the feed says
  data-nblang="de" (precondition). Then everything OF OURS in the page is read:
    text   every text node of the notebook's cells (title cell + cover, the
           document, every fold, hidden or not) and of #nbpanel-root (marks,
           corner signs, every window: ⚙, 👤, ⌨ — opened once)
    attr   title, aria-label, placeholder, data-desc, data-nbtip, alt
    hover  the YOC mark's hover box (data-nbtip while the pointer is on it)
    css    words the stylesheet writes (::before/::after content) on the YOC
           strip and on a locked pill
  minus code, formulas, figures, inputs, and proper names (the lecture titles,
  the reference list, product names, keys). A segment is English when it
  holds a word of a list of English-only words (the, and, of, your, click …)
  and is not plainly German around a single name.
  JupyterLab's own words (its toolbar, "Click to add a cell", cell labels) are
  not ours and need its language pack — not counted.
  v1.63 (+ py-E22): ~12 per notebook — pip label "Coding", "7 Coding (+70
  min)", the end/YOC/grip/theme/style/statistics tooltips, "— click to go
  there", the ⌨ window, "＋ Add your cell", the YOC strip's
  "＋ Add your own coding cell", "Locked". Owner: Python (texts in the
  tables and in the scripts' L(en, de)); switching on the cover without a
  reload is JS (E23.1).
  2026-10-06 rebased on v1.65 (4c4e9b6f) with E23.1js.
exit 0 = REGRESS-PY-E23-1 OK."""
import sys, os, re, json, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
ENW = set("""the and of to your you is are this that with for from here click open show hide answer check chapter exercise
cell own add next back solved skipped locked unlocked try again not yet what which when where how why will would should could
cannot there their they them it its be been have has do does done did every each please press type enter value number step
time minutes reading read write written coding bring figure figures plain both restart window button timeline
progress account password login logout keep stays copy file load save saved reset zoom style light dark settings guide end
title appendix introduction content summary glossary references my our""".split())
DEW = set("der die das und ist sie ein eine mit auf für nicht zu von den dem im wird sind oder wie ihr ihre".split())
NAMES = re.compile(r"Principles of Biophysics(?: &(?:amp;)? Computational methods)?|Computational methods|Introduction to Modeling|"
                   r"Vertiefende Methoden der Bioinformatik|JupyterLab|JupyterLite|Jupyter Notebook|Jupyter|Colab|VS Code|PyCharm|"
                   r"Python|NumPy|Matplotlib|GitHub|Binder|DigiChemJN|Run All(?: Cells)?|Run|Gentle|Standard|Strict|CC BY(?:-SA)?|"
                   r"Creative Commons|OER|FAIR|Pen & paper|Plain|https?://\S+|\S+@\S+|\b\w+\(\)|\b[a-z]+_[a-z_]+\b|DCJ\S*", re.I)

SCAN_JS = r"""() => { """ + FRONT + r"""
  if (!P) return null;
  var out = [], skip = 'code, pre, textarea, script, style, svg, math, mjx-container, .MathJax, .cm-editor, .CodeMirror, '
    + '.jp-InputArea, .widget-readout, .jp-InputPrompt, .jp-OutputPrompt, .jp-Toolbar, .jp-cell-toolbar, .jp-Placeholder, '
    // E29 P1 (12.10.): a cover with both languages hides the other one ([data-nbl], card_facts.cover_two)
    + '[data-nbl="en"]';
  function refs(e){                       // the reference list: bibliographic entries stay as published
    return !!(e.closest && e.closest('[id^="ref"], [data-jupyter-id^="ref"]')); }
  var roots = [].slice.call(P.querySelectorAll('.jp-MarkdownCell .jp-RenderedMarkdown, .jp-CodeCell .jp-OutputArea'));
  var host = document.getElementById('nbpanel-root'); if (host) roots.push(host);
  var help = document.querySelector('.nbhelp'); if (help && !(host && host.contains(help))) roots.push(help);
  roots.forEach(function(R, ri){
    var where = R === host || R === help ? 'panel' : 'document';
    var tw = document.createTreeWalker(R, NodeFilter.SHOW_TEXT, null), n;
    while ((n = tw.nextNode())) {
      var t = n.nodeValue.replace(/\s+/g, ' ').trim(); if (t.length < 2) continue;
      var p = n.parentElement; if (!p || p.closest(skip) || refs(p)) continue;
      out.push([where, 'text', t, String((p.closest('[class]') || p).className).slice(0, 50)]); }
    [].forEach.call(R.querySelectorAll('[title],[aria-label],[placeholder],[data-desc],[data-nbtip],[alt]'), function(e){
      if (e.closest(skip) || refs(e)) return;
      ['title', 'aria-label', 'placeholder', 'data-desc', 'data-nbtip', 'alt'].forEach(function(k){
        var v = e.getAttribute(k); if (v && v.trim().length > 1) out.push([where, k, v.replace(/\s+/g, ' ').trim(), String(e.className).slice(0, 50)]); }); });
  });
  // words of the stylesheet
  var f = P.querySelector('.jp-Notebook-footer');
  if (f) ['::before', '::after'].forEach(function(ps){ var c = getComputedStyle(f, ps).content;
    if (c && c !== 'none' && c !== 'normal' && c !== '""') out.push(['css', 'content', c.replace(/^"|"$/g, ''), 'jp-Notebook-footer' + ps]); });
  var lk = P.querySelector('.acc-locked > .jupyter-widget-Collapse > .jupyter-widget-Collapse-header, .acc-tasklock > .jupyter-widget-Collapse > .jupyter-widget-Collapse-header');
  if (lk) { var c2 = getComputedStyle(lk, '::after').content; if (c2 && c2 !== 'none' && c2 !== '""') out.push(['css', 'content', c2.replace(/^"|"$/g, ''), 'acc-locked::after']); }
  var fd = P.querySelectorAll('.nbfeed[data-nblang]');
  return {lang: fd.length ? fd[fd.length - 1].getAttribute('data-nblang') : null, segs: out, locked: !!lk, foot: !!f}; }"""

def english(seg):
    s = NAMES.sub(" ", seg)
    words = re.findall(r"[A-Za-z][a-z']+|[A-Z]{2,}", s)
    hits = [w for w in words if w.lower() in ENW]
    if not hits: return []
    de = sum(1 for w in words if w.lower() in DEW)
    if de >= 2 and len(hits) < 2: return []
    return hits

def check(b, base, root, src, rows, fails):
    import run as R
    from lab_keys import kill_sessions
    nid = R.nb_id(src)
    kill_sessions(base)
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    for d in (kh, root):
        shutil.rmtree(os.path.join(d, ".digichemjn"), ignore_errors=True)
    os.makedirs(os.path.join(kh, ".digichemjn"), exist_ok=True)
    open(os.path.join(kh, ".digichemjn", "lang"), "w").write("de")
    # hw-E25.int (08.10.): py-E25.o reads only this notebook's file (behauptete
    # bisher: the shared ~/.digichemjn/lang makes the run German)
    open(os.path.join(kh, ".digichemjn", nid + ".lang"), "w").write("de")
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    # E29 (12.10.): + this notebook's own id (the Vorlage, "vorlage", was missing → the page
    # rebuilt the German run in English: "the run is not German", also at v1.75)
    ctx.add_init_script("try{['v1', 'complex-numbers', 'intro-modeling', %s].forEach(function(i){ localStorage.setItem('digichemjn.lang.' + i, 'de'); });}catch(e){}" % json.dumps(nid))   # E25.o: the notebook's key (py-E25.o)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    name = "e231_%d_%s" % (int(time.time()), os.path.basename(src))
    shutil.copy(src, os.path.join(root, name))
    try:
        pg.goto(base + "/lab/tree/" + name + "?reset")
        pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
        pg.wait_for_timeout(1500)
        R.run_front(pg, nid)
        for _ in range(90):
            l = pg.evaluate("() => { " + FRONT + " var f = P && P.querySelectorAll('.nbfeed[data-nblang]'); return f && f.length ? f[f.length-1].getAttribute('data-nblang') : null; }")
            if l == "de" and not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"): break
            pg.wait_for_timeout(1000)
        pg.wait_for_timeout(1500)
        pg.evaluate("() => { " + FRONT + " var o = P && P.querySelector('.jp-WindowedPanel-outer'); if (o) o.scrollTop = 0; }")
        pg.wait_for_timeout(1500)
        # the ⌨ window, opened once (its words exist only while it is open)
        try:
            pg.click("#nbpanel-root .nbbtn.nbkeys", timeout=5000); pg.wait_for_timeout(1000)
        except Exception:
            fails.append("E23.1 BAD the ⌨ window did not open")
        r = pg.evaluate(SCAN_JS)
        pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
        # the YOC mark's hover box
        pg.evaluate("() => { " + FRONT + " var o = P && P.querySelector('.jp-WindowedPanel-outer'); if (o) o.scrollTop = o.scrollHeight; }")
        pg.wait_for_timeout(1800)
        y = pg.evaluate("() => { var n = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc=\"yoc\"]'); var g = n && (n.querySelector('.nbsect') || n); if (!g) return null; var q = g.getBoundingClientRect(); return q.height > 0 ? [q.left + q.width / 2, q.top + q.height / 2] : null; }")
        tip = None
        if y:
            pg.mouse.move(y[0] - 50, y[1] - 50); pg.wait_for_timeout(300); pg.mouse.move(y[0], y[1], steps=4); pg.wait_for_timeout(700)
            tip = pg.evaluate("() => { var n = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc=\"yoc\"]'); var t = document.querySelector('.nbtip'); return [n && n.getAttribute('data-nbtip'), t ? t.textContent : null]; }")
            pg.mouse.move(5, 450)
    finally:
        ctx.close(); kill_sessions(base)
        try: os.remove(os.path.join(kh, ".digichemjn", "lang"))
        except OSError: pass
    if not r or r["lang"] != "de":
        fails.append("E23.1 BAD the run is not German (data-nblang=%s)" % (r and r["lang"])); return
    segs = list(r["segs"])
    if tip:
        for t in tip:
            if t: segs.append(["panel", "hover", t, "yoc mark"])
    else:
        fails.append("E23.1 BAD no hover box on the YOC mark")
    seen, eng = set(), []
    for where, kind, t, cls in segs:
        if (kind, t) in seen: continue
        seen.add((kind, t))
        h = english(t)
        if h: eng.append((where, kind, t, cls, h))
    by = {}
    for e in eng: by.setdefault(e[0], []).append(e)
    rows.append("E23.1 de: %d segments read (document, panel with ⌨ window, hover, stylesheet; locked pill %s, strip %s) · English: %s"
                % (len(seen), r["locked"], r["foot"], {k: len(v) for k, v in by.items()} or 0))
    for where, kind, t, cls, h in eng[:40]:
        rows.append("   EN %-8s %-10s %-26s %s   %s" % (where, kind, cls[:26], t[:120], h[:4]))
    if eng:
        fails.append("E23.1 %d English segments in a German run: %s" % (len(eng), "; ".join("%s %s %r" % (e[0], e[1], e[2][:50]) for e in eng[:6])))
    if errs: fails.append("E23.1 page errors: %s" % errs[:2])

def main():
    src = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    sys.argv = sys.argv[:1] + ["x"]
    rows, fails = [], []
    from lab_keys import ensure_lab, CHROME
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try: check(b, base, root, src, rows, fails)
        except Exception as e: fails.append("E23.1 BAD %s" % str(e)[:200])
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E23-1 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
