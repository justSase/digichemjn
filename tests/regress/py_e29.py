"""E29 · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e29.py <notebook.ipynb> [--only P1,D1] [--shot DIR]
  Nutzer 12.10. zu v1.75 (Vorlage; STOP.md E29). Python's points:
  P1  LANGUAGE EVERYWHERE ON THE COVER. A fresh copy, run English in JupyterLab;
      on the cover (no Play) EN|DE → DE: in the VISIBLE cover (title card,
      subtitle, lead, "what you will learn" opened, timeline names + heading,
      mode cards, Play + hint, "Sign in" opened, series, feedback) and in the
      hover box of EVERY visible timeline mark (.nbtl-desc) 0 English
      segments; title / aria-label / placeholder / alt of visible elements
      too. Then EN again: 0 German segments. (Texts: Python, both languages in
      the markup; the switch of the attributes and the page's own words: JS.)
      v1.75: lead, "What you will learn", names, Play, hint, "Sign in" stay
      English after DE (Bild Werkstatt 12.10.).
      P1 counts the visible texts (Python's markup, switched by the cover's
      stylesheet on the page's EN|DE row); P1a the tooltips and hover boxes
      (the page applies data-nbl-<lang>: JS, claude/VERTRAG-E29-py.md).
      Werkstatt Python 12.10.: P1 green, P1a red until the JS patch.
  P5  FEEDBACK IS A TEXT. Cover: a line with the contact address (en/de),
      no mailto: link, no form, no tick; ⚙ drawer (.nbfb): the same text,
      no mailto:, no data-nbfeedback. v1.75: a mailto: link in both.
  P7  Start Here is in a series of its own (card_facts.SERIES, static):
      not in "biophysics", its own series "Using the notebooks /
      Notebooks benutzen". v1.75: in biophysics.
  P8  THE ONE CELL SAYS "DO NOT CHANGE" (static): ≤ 15 lines (E31 C1: ≤ 25), a comment in
      English and one in German with: do not change / unusable, may be read /
      own notebooks (Vorlage), hack into the solutions / Selbstbetrug.
      v1.75: none.
  D1  THE TITLE PILL STAYS (Nutzer: in v1.74 it showed only the package
      install help; fine in Vorlage v1.75 — this keeps it): after Play the
      title accordion (.acc-title.acc-root) is the notebook's title, open,
      shows the subtitle first and the groups after it; no install help
      (pip / Installing / Installiere) in it.
exit 0 = REGRESS-PY-E29 OK."""
import sys, os, re, json, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
TK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "toolkit")

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
ENW = set("""the and of to your you is are this that with for from here click open show hide answer check chapter exercise
cell own add next back solved skipped locked unlocked try again not yet what which when where how why will would should could
cannot there their they them it its be been have has do does done did every each please press type enter value number step
time minutes reading read write written coding figure figures plain both restart window button timeline
progress account password login logout keep stays copy file load save saved reset zoom style light dark settings guide end
title appendix introduction content summary glossary references my our placeholder learn sign series section runs menu
able chapters exercises calculate only practise pen paper contact errors mail""".split())
DEW = set("""der die das und ist sie ein eine mit auf für nicht zu von den dem im wird sind oder wie ihr ihre einführung inhalt
anhang kapitel aufgabe aufgaben abbildung platzhalter zeitleiste anmelden reihe ende eigene zelle führt alle zellen aus menü
titel lernen können danach geführten teils beides lesen nur rechnen programmieren üben möchten stift papier
programmieraufgaben rechenaufgaben abbildungen fehler kontakt dieses abschnitt""".split())
NAMES = re.compile(r"JupyterLab|JupyterLite|Jupyter|Run All(?: Cells)?|Run ▸ Run All Cells|Run|Python|DigiChemJN|"
                   r"https?://\S+|\S+@\S+|\b\w+\(\)|\b[a-z]+_[a-z_]+\b|Feedback|Notebook|Code|E-Mail|e-mail", re.I)

def words(seg):
    return re.findall(r"[A-Za-zÄÖÜäöüß][a-zäöüß']+|[A-Z]{2,}", NAMES.sub(" ", seg))

def english(seg):
    w = words(seg); hits = [x for x in w if x.lower() in ENW]
    if not hits: return []
    de = sum(1 for x in w if x.lower() in DEW)
    return [] if de >= 2 and len(hits) < 2 else hits

def german(seg):
    w = words(seg); hits = [x for x in w if x.lower() in DEW]
    if not hits: return []
    en = sum(1 for x in w if x.lower() in ENW)
    return [] if en >= 2 and len(hits) < 2 else hits

COV = FRONT + " var C = P && P.querySelector('.nbtitle.nbcover-out');"
OPEN_FOLDS = "() => { " + COV + """ if (!C) return false;
  [].forEach.call(C.querySelectorAll('details.nbcover-learn, details.nbacct-fold, details.nbcover-tl'), function(d){ d.open = true; });
  return true; }"""
SCAN = "() => { " + COV + r""" if (!C) return null;
  var out = [], skip = 'script, style, svg, code, .nbtl-desc';
  function vis(e){ return e.checkVisibility ? e.checkVisibility({checkVisibilityCSS: true}) : !!(e.offsetWidth || e.offsetHeight); }
  var tw = document.createTreeWalker(C, NodeFilter.SHOW_TEXT, null), n;
  while ((n = tw.nextNode())) {
    var t = n.nodeValue.replace(/\s+/g, ' ').trim(); if (t.length < 2) continue;
    var p = n.parentElement; if (!p || p.closest(skip) || !vis(p)) continue;
    out.push(['text', t, String((p.closest('[class]') || p).className).slice(0, 40)]); }
  [].forEach.call(C.querySelectorAll('[title],[aria-label],[placeholder],[alt]'), function(e){
    if (e.closest('script, style') || !vis(e)) return;
    ['title', 'aria-label', 'placeholder', 'alt'].forEach(function(k){ var v = e.getAttribute(k);
      if (v && v.trim().length > 1) out.push([k, v.replace(/\s+/g, ' ').trim(), String(e.className).slice(0, 40)]); }); });
  var fb = C.querySelector('.nbfb-note, .nbfb-cover');
  return {segs: out, mailto: C.querySelectorAll('a[href^="mailto:"]').length, form: C.querySelectorAll('.nbfb input, .nbfb-tick').length,
          fb: fb && vis(fb) ? fb.innerText.replace(/\s+/g, ' ').trim() : null,
          row: (C.querySelector('.nblang') || {getAttribute: function(){ return null; }}).getAttribute('data-lang')}; }"""
ROWS = "() => { " + COV + r""" if (!C) return [];
  return [].filter.call(C.querySelectorAll('.nbcover-tl .nbtl-row'), function(r){
      var b = r.getBoundingClientRect(); return b.width > 0 && b.height > 0 && getComputedStyle(r).display !== 'none'; })
    .map(function(r, i){ r.setAttribute('data-e29', i); return i; }); }"""
HOVER = "(i) => { " + COV + r""" var r = C.querySelector('.nbtl-row[data-e29="' + i + '"]'); if (!r) return null;
  r.scrollIntoView({block: 'center', inline: 'center'}); var m = r.querySelector('.nbtl-mk') || r, b = m.getBoundingClientRect();
  if (b.width < 1) b = r.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }"""
TIP = "() => { " + COV + r""" var d = C && C.querySelector('.nbcover-tl > .nbtl-desc');
  return d && !d.hidden ? d.textContent.replace(/\s+/g, ' ').trim() : ''; }"""

def click_lang(pg, lg):
    xy = pg.evaluate("(lg) => { " + COV + " var o = C && C.querySelector('.nblang-opt[data-lang=\"' + lg + '\"]'); if (!o) return null;"
                     " o.scrollIntoView({block: 'center'}); var b = o.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }", lg)
    if not xy: return False
    pg.mouse.click(*xy); pg.wait_for_timeout(1800)
    return True

def cover_read(pg):
    pg.evaluate(OPEN_FOLDS); pg.wait_for_timeout(600)
    r = pg.evaluate(SCAN)
    tips = []
    for i in pg.evaluate(ROWS):
        xy = pg.evaluate(HOVER, i)
        if not xy: continue
        pg.mouse.move(xy[0] - 40, xy[1] - 60); pg.wait_for_timeout(60)
        pg.mouse.move(xy[0], xy[1], steps=3); pg.wait_for_timeout(220)
        t = pg.evaluate(TIP)
        if t: tips.append(t)
    pg.mouse.move(5, 450)
    return r, tips

def lab_part(src, only, shot, rows, fails):
    import run as R
    from lab_keys import ensure_lab, CHROME, kill_sessions, cover_play
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    nid = R.nb_id(src)
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    for d in (kh, root):
        shutil.rmtree(os.path.join(d, ".digichemjn"), ignore_errors=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx = b.new_context(viewport={"width": 1400, "height": 900})
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
        name = "e29_%d_%s" % (int(time.time()), os.path.basename(src))
        shutil.copy(src, os.path.join(root, name))
        try:
            pg.goto(base + "/lab/tree/" + name + "?reset")
            pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
            pg.wait_for_timeout(1500)
            R.palette(pg, "Run All Cells")
            pg.wait_for_function(R.READY_JS, arg=nid, timeout=90000)
            for _ in range(90):
                st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
                if st == "idle": break
                pg.wait_for_timeout(1000)
            pg.wait_for_timeout(2500)
            if not pg.evaluate("() => { " + COV + " return !!(C && C.querySelector('.nbcover-play')); }"):
                fails.append("E29 BAD no cover after Run All"); return
            if set(only) & {"P1", "P1a", "P5"}:
                r0, t0 = cover_read(pg)
                if shot: pg.evaluate("() => { " + COV + " C.querySelector('.nbtitle-card').scrollIntoView({block: 'start'}); }"); pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(shot, "e29_P1_cover_en.png"))
                if not click_lang(pg, "de"):
                    fails.append("E29.P1 BAD no EN|DE on the cover")
                else:
                    r1, t1 = cover_read(pg)
                    if shot:
                        pg.evaluate("() => { " + COV + " C.querySelector('.nbtitle-card').scrollIntoView({block: 'start'}); }"); pg.wait_for_timeout(300)
                        pg.screenshot(path=os.path.join(shot, "e29_P1_cover_de.png"))
                        pg.evaluate("() => { " + COV + " C.querySelector('.nbcover-play').scrollIntoView({block: 'start'}); }"); pg.wait_for_timeout(300)
                        pg.screenshot(path=os.path.join(shot, "e29_P1_cover_de_unten.png"))
                    click_lang(pg, "en")
                    r2, t2 = cover_read(pg)
                    if set(only) & {"P1", "P1a"}:
                        for tag, r, tips, fn, lg in (("en→de", r1, t1, english, "de"), ("de→en", r2, t2, german, "en")):
                            if r["row"] != lg:
                                fails.append("E29.P1 BAD %s: the language row says %s" % (tag, r["row"])); continue
                            segs = [s for s in r["segs"]] + [["hover", t, "nbtl-desc"] for t in tips]
                            bad, seen = [], set()
                            for k, t, cls in segs:
                                if (k, t) in seen: continue
                                seen.add((k, t)); h = fn(t)
                                if h: bad.append((k, t, cls, h))
                            # P1 = the visible texts (markup: Python; the switch rides on the
                            # page's EN|DE row) · P1a = tooltips + hover boxes (the page sets
                            # them from data-nbl-<lang>: JS) — one criterion of the Nutzer, two owners
                            bt = [x for x in bad if x[0] == "text"]
                            ba = [x for x in bad if x[0] != "text"]
                            rows.append("E29.P1 %s: %d segments + %d hover boxes read · other language: %d texts, %d tooltips/hover"
                                        % (tag, len(r["segs"]), len(tips), len(bt), len(ba)))
                            for k, t, cls, h in (bt + ba)[:12]:
                                rows.append("   %-6s %-10s %-28s %s   %s" % (lg, k, cls[:28], t[:110], h[:4]))
                            if not tips: fails.append("E29.P1a BAD %s: no hover box on the cover's timeline" % tag)
                            if bt and "P1" in only:
                                fails.append("E29.P1 %s: %d visible texts of the other language: %s" % (tag, len(bt), "; ".join(
                                    "%r" % x[1][:40] for x in bt[:6])))
                            if ba and "P1a" in only:
                                fails.append("E29.P1a %s: %d tooltips/hover boxes of the other language (JS: data-nbl-%s): %s"
                                             % (tag, len(ba), lg, "; ".join("%s %r" % (x[0], x[1][:40]) for x in ba[:6])))
                    if "P5" in only:
                        for tag, r in (("en", r0), ("de", r1)):
                            want = "Feedback, Fehler und Kontakt" if tag == "de" else "Feedback, errors and contact"
                            ok = bool(r["fb"]) and "samuel.wiese@gmx.de" in r["fb"] and want in r["fb"] and not r["mailto"] and not r["form"]
                            rows.append("E29.P5 cover %s: line %r · mailto links %d · form/tick %d" % (tag, r["fb"], r["mailto"], r["form"]))
                            if not ok: fails.append("E29.P5 cover %s: line %r, mailto %d, form %d" % (tag, r["fb"], r["mailto"], r["form"]))
            if "D1" in only or "P5" in only:
                cp = cover_play(pg)
                if cp.startswith("BAD"): fails.append("E29 " + cp); return
                pg.wait_for_timeout(1500)
            if "D1" in only:
                meta = json.load(open(src)).get("metadata", {}).get("digichemjn", {})
                d = pg.evaluate("() => { " + FRONT + r""" var a = P && P.querySelector('.acc-title.acc-root'); if (!a) return null;
                  var h = a.querySelector('.jupyter-widget-Collapse-header, .lm-AccordionPanel-title, .widget-collapse-header');
                  var c = a.querySelector('.jupyter-widget-Collapse-contents, .lm-AccordionPanel > :not(.lm-AccordionPanel-title), .widget-collapse-contents');
                  var vis = function(e){ return !!e && e.checkVisibility({checkVisibilityCSS: true}); };
                  var lead = a.querySelector('.nbtitle-leadbox .nbtitle-lead');
                  var txt = c ? (c.innerText || '') : '';
                  var first = c ? [].filter.call(c.querySelectorAll('.nbtitle-leadbox, .acc-group, .acc-root, .jupyter-widget-Accordion'), vis).map(function(e){ return e.className.slice(0, 30); }).slice(0, 4) : [];
                  return {head: h ? h.textContent.replace(/\s+/g, ' ').trim() : null, open: vis(c), lead: lead && vis(lead) ? lead.textContent.trim() : null,
                          pip: /pip install|piplite|Installing|Installiere|%pip/.test(txt), n: txt.length, first: first,
                          leadFirst: !!(c && lead && c.querySelector('.nbtitle-leadbox') && txt.trim().indexOf(lead.textContent.trim()) === 0)}; }""")
                if not d:
                    fails.append("E29.D1 BAD no title accordion (.acc-title.acc-root) after Play")
                else:
                    rows.append("E29.D1 title pill %r · open %s · subtitle %r first %s · %d chars inside · install help %s · %s"
                                % (d["head"], d["open"], d["lead"], d["leadFirst"], d["n"], d["pip"], d["first"]))
                    if (d["head"] or "").strip() != meta.get("title") or not d["open"] or not d["lead"] or not d["leadFirst"] \
                            or d["pip"] or d["n"] < 1000:
                        fails.append("E29.D1 the title pill: %s" % d)
                    if shot:
                        pg.evaluate("() => { " + FRONT + " var a = P.querySelector('.nbtitle-doc'); if (a) a.scrollIntoView({block: 'start'}); }")
                        pg.wait_for_timeout(500); pg.screenshot(path=os.path.join(shot, "e29_D1_titelpille.png"))
            if "P5" in only:
                # the ⚙ drawer's cell (.nbfb) — anywhere on the page once the document is up
                f = pg.evaluate(r"""() => { var x = [].slice.call(document.querySelectorAll('.nbfb:not(.nbfb-note)'));
                  return x.map(function(e){ return {t: e.textContent.replace(/\s+/g, ' ').trim(), m: e.querySelectorAll('a[href^="mailto:"]').length,
                    j: e.hasAttribute('data-nbfeedback'), tick: e.querySelectorAll('input, .nbfb-tick').length}; }); }""")
                rows.append("E29.P5 ⚙ drawer: %s" % (f[:2],))
                if not f or any(x["m"] or x["j"] or x["tick"] or "samuel.wiese@gmx.de" not in x["t"] for x in f):
                    fails.append("E29.P5 ⚙ drawer: %s" % (f[:2],))
        finally:
            if errs: fails.append("E29 page errors: %s" % errs[:2])
            ctx.close(); kill_sessions(base); b.close()

def static_part(src, only, rows, fails):
    if "P7" in only:
        sys.path.insert(0, TK)
        import card_facts as CF
        bio = [it["id"] for it in CF.SERIES.get("biophysics", {}).get("items", [])]
        own = [(sid, s) for sid, s in CF.SERIES.items() if any(it["id"] == "start-here" for it in s["items"])]
        rows.append("E29.P7 biophysics: %s · Start Here in: %s" % (bio, [(sid, s["name"]) for sid, s in own]))
        if "start-here" in bio or len(own) != 1 or [it["id"] for it in own[0][1]["items"]] != ["start-here"] \
                or tuple(own[0][1]["name"]) != ("Using the notebooks", "Notebooks benutzen"):
            fails.append("E29.P7 Start Here: biophysics %s, series %s" % (bio, [(sid, s["name"]) for sid, s in own]))
    if "P8" in only:
        nb = json.load(open(src))
        cell = max(nb["cells"], key=lambda c: len("".join(c["source"])))
        lines = "".join(cell["source"]).rstrip("\n").split("\n")
        com = [l for l in lines if l.startswith("#")]
        # E31 C1 (12.10.): one sentence per line — the warning is a block of lines, en and de
        # (behauptete bisher: all of it in ONE line each, cell ≤ 15 lines; now ≤ 25)
        _en, _de = " ".join(com), " ".join(com)
        en = [1] if (re.search(r"Do not edit|do not change", _en, re.I) and "breaks the notebook" in _en
              and re.search(r"Reading the code is fine", _en) and "Vorlage" in _en and re.search(r"hack into the solutions", _en)) else []
        de = [1] if ("Nicht ändern" in _de and "unbenutzbar" in _de and "gelesen werden" in _de and "Vorlage" in _de
              and "Lösungen hacken" in _de and "Selbstbetrug" in _de) else []
        rows.append("E29.P8 cell: %d lines · warning en %d · de %d" % (len(lines), len(en), len(de)))
        if len(lines) > 25 or len(en) != 1 or len(de) != 1:
            fails.append("E29.P8 cell %d lines, warning en %d de %d" % (len(lines), len(en), len(de)))

def main():
    args = [a for a in sys.argv[1:]]
    src = os.path.abspath([a for a in args if not a.startswith("--") and a.endswith(".ipynb")][0])
    only = ("P1", "P1a", "P5", "P7", "P8", "D1")
    if "--only" in args: only = tuple(args[args.index("--only") + 1].split(","))
    shot = args[args.index("--shot") + 1] if "--shot" in args else None
    sys.argv = sys.argv[:1] + ["x"]
    rows, fails = [], []
    static_part(src, only, rows, fails)
    if set(only) & {"P1", "P1a", "P5", "D1"}:
        try: lab_part(src, only, shot, rows, fails)
        except Exception as e: fails.append("E29 BAD %s" % str(e)[:300])
    print("\n".join(rows))
    print("REGRESS-PY-E29 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
