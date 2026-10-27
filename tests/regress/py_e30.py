"""E30 · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e30.py <notebook.ipynb> [--only A1,B2,B6,T1] [--shot DIR]
  Nutzer 12.10. (PyCharm, Complex v1.75; STOP.md "NÄCHSTE RUNDE E30"), at the Vorlage:
  A1  THE CONCLUSION IS A TEXT (all environments). The Conclusion chapter holds
      a .nbconcl box: ≥ 3 paragraphs (summary · context · outlook), an
      "Outlook"/"Ausblick" heading, no table / list inside, built by the
      building block conclusion() (vorlage/chapters/conclusion.py calls it).
      en + de run, read in the reading copy. v1.76: rules table, no .nbconcl.
  B2  ONE LANGUAGE IN THE WINDOW (PyCharm path). Real kernel, every output in
      an iframe of its own, no widget manager (env_iframe viewer, served over
      http). English run: on the window's cover DE, then Play → in the visible
      document (title card, every heading, text, task fields; folds opened)
      0 English literals of the tables (toolkit/de.txt + the notebook's de.txt,
      ≥ 12 characters, whole); the contents list and the panel's current
      chapter German too. German run → EN: 0 German literals. v1.76: the
      document stays in the run's language (Nutzer: "Titel/Dokument en,
      Inhaltsverzeichnis + Panel de").
  B6  LAB'S TIMELINE IN THE READING COPY (markup for the window's panel, JS
      uses it): one <template class="nbrw-rail"> in the reading copy with the
      panel's nodes (a chapter node per chapter, exercise pips data-kind/
      data-st, .nbmap-fill), every href / data-target names an id of the
      reading copy, every visible label both languages, every node title
      both (data-nbl-en/-de). Inert: not found by querySelector in the page.
      v1.76: none.
  T1  THE LOCK'S TOOLTIP SAYS WHAT A CLICK DOES (D3, E29): a locked chapter's
      node in Lab's panel says it opens once exercise k is answered, not
      "click it, then turn the key in the box" (en; de "· gesperrt …").
exit 0 = REGRESS-PY-E30 OK."""
import sys, os, re, json, html, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "toolkit"))
import i18n

def reading(outs):
    for o in outs:
        h = o["data"].get("text/html") or ""
        if h.startswith("<div class='nbreading'"):
            # E33 A1: behauptete bisher "the run's HTML string holds the timeline as <template>"; the static copy
            # carries it in <script type=application/json data-nbrw-put>, the page rebuilds it (py_e33 R1)
            from _nbrw_static import rebuild
            return rebuild(h)
    return ""

def literals(nbdir):
    pairs = {}
    for f in (os.path.join(ROOT, "toolkit", "de.txt"), os.path.join(nbdir, "chapters", "de.txt")):
        pairs.update(i18n.load(f))
    plain = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
    out = []
    for e, d in pairs.items():
        if "%" in e or "{" in e:
            continue
        e, d = plain(e), plain(d)
        if e != d and len(e) >= 12 and len(d) >= 12 and e not in d and d not in e:
            out.append((e, d))
    return out

def a1(h, lang, fails, rows):
    from bs4 import BeautifulSoup
    sp = BeautifulSoup(h, "html.parser")
    box = sp.select(".nbr-nbconcl")
    if len(box) != 1:
        fails.append("A1 %s: %d .nbconcl boxes in the reading copy, want 1" % (lang, len(box))); return
    b = box[0]
    for x in b.select("[data-nbrw-l]"):
        if x.get("data-nbrw-l") != lang:
            x.decompose()
    ps = [p for p in b.select("p.nbr-nbconcl-p") if len(p.get_text(" ", strip=True)) >= 40]
    hd = [x.get_text(" ", strip=True) for x in b.select(".nbr-nbconcl-h")]
    lists = b.select("table, ul, ol, li")
    rows.append("A1 %s: %d paragraphs, heading %s, lists/tables %d" % (lang, len(ps), hd, len(lists)))
    if len(ps) < 3: fails.append("A1 %s: %d paragraphs, want ≥ 3" % (lang, len(ps)))
    if hd != [{"en": "Outlook", "de": "Ausblick"}[lang]]: fails.append("A1 %s: heading %s" % (lang, hd))
    if lists: fails.append("A1 %s: %d table/list elements in the conclusion" % (lang, len(lists)))

def a1_src(nbdir, fails, rows):
    p = os.path.join(nbdir, "chapters", "conclusion.py")
    if os.path.isfile(p):
        s = open(p, encoding="utf-8").read()
        ok = "conclusion(" in s and "_rules" not in s
        rows.append("A1 source: conclusion() called %s, rules table %s" % ("conclusion(" in s, "_rules" in s))
        if not ok: fails.append("A1 source: %s does not use conclusion() (or keeps the rules table)" % p)

def b6(h, lang, fails, rows):
    from bs4 import BeautifulSoup
    sp = BeautifulSoup(h, "html.parser")
    t = sp.select("template.nbrw-rail")
    if len(t) != 1:
        fails.append("B6 %s: %d <template class=nbrw-rail>, want 1" % (lang, len(t))); return
    t = t[0]
    ids = {x.get("id") for x in sp.select("[id]")}
    nodes = t.select("a.nbmap-node")
    chap = t.select("a.nbmap-node.chap")
    pips = t.select("[data-kind][data-st]")
    bad = [a.get("href") for a in t.select("a[href]") if a.get("href") not in ("#",) and a.get("href")[1:] not in ids]
    bad += [a.get("data-target") for a in t.select("[data-target]") if a.get("data-target") not in ids]
    labs = t.select(".nbmap-lab")
    one = [l.get_text() for l in labs if l.get_text(strip=True) and not l.select("[data-nbrw-l]")
           and re.search(r"[A-Za-z]{3}", l.get_text())]
    tt = [a for a in nodes if a.get("title") and re.search(r"[A-Za-z]{3}", a.get("title"))]
    two = [a for a in tt if a.get("data-nbl-en") and a.get("data-nbl-de")]
    rows.append("B6 %s: nodes %d, chapters %d, pips %d, targets missing %d, labels one-language %d, titles both %d/%d, size %d"
                % (lang, len(nodes), len(chap), len(pips), len(bad), len(one), len(two), len(tt), len(str(t))))
    if not chap or not pips: fails.append("B6 %s: no chapter nodes / pips in the rail" % lang)
    if bad: fails.append("B6 %s: targets not in the reading copy: %s" % (lang, bad[:4]))
    if one: fails.append("B6 %s: labels in one language only: %s" % (lang, one[:4]))
    if len(two) < 0.9 * len(tt): fails.append("B6 %s: titles in both languages %d of %d" % (lang, len(two), len(tt)))

def t1(outs, lang, fails, rows):
    # Lab's panel is a widget: its HTML is in the widget models of the run (not in the reading copy)
    models = (outs[0].get("models") if outs else None) or {}
    allh = "".join(str(m.get("value") or "") for m in models.values() if "nbmap-node" in str(m.get("value") or ""))
    tips = re.findall(r'<a class="nbjump nbmap-node chap locked"[^>]*\btitle="([^"]*)"', allh)
    old = [x for x in tips if "turn the key" in x or "Schlüssel" in x]
    want = "opens once" if lang == "en" else "öffnet sich, sobald"
    rows.append("T1 %s: %d locked chapter tooltips, old wording %d, e.g. %r" % (lang, len(tips), len(old), html.unescape(tips[0])[:90] if tips else ""))
    if not tips: fails.append("T1 %s: no locked chapter node found" % lang)
    if old or any(want not in x for x in tips): fails.append("T1 %s: tooltip %r" % (lang, html.unescape((old or tips)[0])[:90]))

SCAN = r"""([lang]) => {
  var f = [].slice.call(document.querySelectorAll('iframe.out')).filter(function(x){
    try { return !!x.contentDocument.querySelector('.nbrw'); } catch (e) { return false; } })[0];
  if (!f) return null;
  var d = f.contentDocument, w = d.querySelector('.nbrw'), win = w.querySelector('.nbrw-win');
  [].forEach.call(win.querySelectorAll('details'), function(x){ x.open = true; });
  var out = [], skip = 'script, style, svg, code, pre, .nbrw-cover, .nbread-line';
  function vis(e){ return e.checkVisibility ? e.checkVisibility({checkVisibilityCSS: true}) : !!(e.offsetWidth || e.offsetHeight); }
  var tw = d.createTreeWalker(win, NodeFilter.SHOW_TEXT, null), n;
  while ((n = tw.nextNode())) {
    var p = n.parentElement; if (!p || p.closest(skip) || !vis(p)) continue;
    out.push(n.nodeValue); }
  var toc = [].map.call(win.querySelectorAll('ol.nbread-toc a'), function(a){ return a.innerText.trim(); });
  var cur = w.querySelector('.nbrw-cur');
  var hs = [].map.call(win.querySelectorAll('.nbread-h'), function(x){ return vis(x) ? x.innerText.trim() : ''; }).filter(Boolean);
  return {text: out.join(' ').replace(/\s+/g, ' '), toc: toc, heads: hs, cur: cur ? cur.innerText.trim() : '',
          view: w.getAttribute('data-nbrw-view'), lang: d.querySelector('.nbreading').getAttribute('lang')};
}"""

def b2(b, base, name, run, to, lits, titles, fails, rows, shot):
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    pg = ctx.new_page(); pg.goto(base + name); pg.wait_for_timeout(2500)
    fr = None
    for f in pg.frames:
        try:
            if f.evaluate("() => !!document.querySelector('.nbrw')"): fr = f; break
        except Exception:
            pass
    if fr is None:
        fails.append("B2 %s→%s: no reading window" % (run, to)); ctx.close(); return
    fr.evaluate("""([lg]) => { var w = document.querySelector('.nbrw');
      var b = w.querySelector('.nbrw-cover [data-lang="' + lg + '"]'); if (b) b.click();
      var p = w.querySelector('[data-nbrw-act=play]'); if (p && w.getAttribute('data-nbrw-view') === 'cover') p.click(); }""", [to])
    pg.wait_for_timeout(800)
    r = pg.evaluate(SCAN, [to])
    if not r:
        fails.append("B2 %s→%s: nothing scanned" % (run, to)); ctx.close(); return
    txt = r["text"]
    wrong = [a for e, d in lits for a, c in [((e, d) if to == "de" else (d, e))] if a in txt and c not in txt]
    right = [c for e, d in lits for a, c in [((e, d) if to == "de" else (d, e))] if c in txt]
    # the scan must SEE the document (a scan that sees nothing finds nothing wrong):
    # every chapter heading in the chosen language, and ≥ 20 literals of it
    heads = " | ".join(r["heads"])
    miss = [t for t in titles[to] if t not in heads]
    rows.append("B2 %s→%s: visible text %d chars, literals of the chosen language %d, headings %d (missing %s)"
                % (run, to, len(txt), len(right), len(r["heads"]), miss[:2]))
    if len(right) < 20 or miss:
        fails.append("B2 %s→%s: the document is not seen in %s (literals %d, headings missing %s)" % (run, to, to, len(right), miss[:2]))
    want = titles[to]
    toc_ok = r["toc"] == want
    cur_ok = (not r["cur"]) or any(r["cur"].startswith(t[:12]) or t.startswith(r["cur"][:12]) for t in want) or r["cur"] in ("Start", "Anfang")
    rows.append("B2 %s→%s: view %s, lang %s, wrong-language literals %d %s, contents %s, panel %r"
                % (run, to, r["view"], r["lang"], len(wrong), [w[:40] for w in wrong[:3]], "ok" if toc_ok else r["toc"][:2], r["cur"][:40]))
    if wrong: fails.append("B2 %s→%s: %d literals of the other language visible: %s" % (run, to, len(wrong), [w[:50] for w in wrong[:4]]))
    if not toc_ok: fails.append("B2 %s→%s: contents %s, want %s" % (run, to, r["toc"][:2], want[:2]))
    if not cur_ok: fails.append("B2 %s→%s: panel names %r" % (run, to, r["cur"]))
    if shot:
        fr.evaluate("() => { var w = document.querySelector('.nbrw-win'); var h = w.querySelector('.nbread-h'); if (h) h.scrollIntoView(); }")
        pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(shot, "E30-B2-%s-%s.png" % (run, to)))
    ctx.close()

def main():
    import nbpick
    args = sys.argv[1:]
    only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else None
    shot = args[args.index("--shot") + 1] if "--shot" in args else None
    src = nbpick.from_argv(sys.argv)
    nbdir = os.path.dirname(os.path.abspath(src))
    want = lambda k: only is None or k in only
    from env_iframe import run_cell, host_page
    from env_reader import serve
    rows, fails, runs = [], [], {}
    for lang in ("en", "de"):
        outs, errs, chapters = run_cell(src, {"DIGICHEM_LANG": lang})
        if errs: fails.append("%s run raised: %s" % (lang, errs[:1]))
        runs[lang] = (outs, chapters)
        h = reading(outs)
        if not h:
            fails.append("%s: no reading copy" % lang); continue
        if want("A1"): a1(h, lang, fails, rows)
        if want("B6"): b6(h, lang, fails, rows)
        if want("T1"): t1(outs, lang, fails, rows)
    if want("A1"): a1_src(nbdir, fails, rows)
    if want("B2") and all(runs.get(l) for l in ("en", "de")):
        from lab_keys import CHROME
        from playwright.sync_api import sync_playwright
        lits = literals(nbdir)
        titles = {l: runs[l][1] for l in ("en", "de")}
        tmpd = tempfile.mkdtemp(prefix="pye30_"); srv = serve(tmpd)
        base = "http://127.0.0.1:%d/" % srv.server_address[1]
        try:
            with sync_playwright() as p:
                b = p.chromium.launch(executable_path=CHROME)
                for run, to in (("en", "de"), ("de", "en")):
                    name = "%s.html" % run
                    open(os.path.join(tmpd, name), "w", encoding="utf-8").write(host_page(runs[run][0], False))
                    b2(b, base, name, run, to, lits, titles, fails, rows, shot)
                b.close()
        finally:
            srv.shutdown(); shutil.rmtree(tmpd, ignore_errors=True)
    for r in rows: print("  " + r)
    if fails:
        for f in fails: print("FAIL " + f)
        print("REGRESS-PY-E30 RED (%d)" % len(fails)); sys.exit(1)
    print("REGRESS-PY-E30 OK")

if __name__ == "__main__":
    main()
