"""E26 Teil 3 · KORREKTUR (Dirigent 19:3x UTC) — THREE NOTEBOOKS, NOTHING SHARED (Werkstatt JS, 2026-10-11).
    python3 tests/regress/env_multi.py <complex.ipynb> [<modeling.ipynb> <vorlage.ipynb>] [--json out.json]
    (one notebook given: Modeling and Vorlage of the same version are taken from the tree — build them first)

Nutzer: „Notebooks in verschiedenen Tabs sollen unabhängig laufen wie in Lab.“
Every notebook runs in a real kernel (env_iframe.run_cell); its outputs are
shown two ways, served over http (one origin = one localStorage, as in one
IDE):
  (i)  one page, every output in an iframe of its own (PyCharm, VS Code)
  (ii) one page, all outputs of all three in one document, each in its own
       container the way a front end draws text/html (innerHTML + scripts
       re-created; JupyterLab-like)
Rows per way:
  M1 one window each      per notebook exactly one .nbrw, holding its OWN
                          reading version (data-nbrw-id = the notebook id,
                          title card = its title), all on the preview
  M2 Play is per notebook Play in notebook A → A shows its document, B and C
                          stay on the preview
  M3 height/lens/style    ↕+ ×2, A+, ✿ in A → A changed; B, C unchanged
  M4 progress             A's first exercise answered right → A's t1 solved,
                          XP 1; B's and C's t1 (same key!) unchanged, XP 0
  M5 after reload         all of it kept per notebook, nothing crossed over
  M6 no shared globals    one fallback style per notebook id, __nbReaders has
                          every id, localStorage keys only digichemjn.<id>.*
v1.73: red (no preview: M1/M2; no per-id API: M6). Owner: JS.
exit 0 = REGRESS-ENV-MULTI OK."""
import sys, os, re, json, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from env_iframe import run_cell, host_page
from env_reader import serve

ST = r"""() => {
  var docs = [document].concat([].slice.call(document.querySelectorAll('iframe.out')).map(function (f) { return f.contentDocument; }).filter(Boolean));
  var out = {};
  docs.forEach(function (d) {
    [].forEach.call(d.querySelectorAll('.nbrw'), function (w) {
      var win = w.querySelector('.nbrw-win'), rd = w.querySelector('.nbreading');
      var t1 = w.querySelector('.nbrw-task[data-task=t1]'), xp = w.querySelector('.nbrw-xp-t'), card = w.querySelector('[class*="nbtitle-h"]');
      var id = w.getAttribute('data-nbrw-id') || ('title:' + (card ? card.textContent.trim() : '?'));   // v1.73: no id on the window
      (out[id] = out[id] || []).push({view: w.getAttribute('data-nbrw-view'), h: Math.round(win.getBoundingClientRect().height),
        f: parseFloat(getComputedStyle(rd).fontSize), skin: w.getAttribute('data-nbrw-skin'), t1: t1 && t1.getAttribute('data-st'),
        xp: xp ? xp.textContent : null, title: card ? card.textContent.trim() : '', own: rd.parentNode === win || win.contains(rd)});
    });
  });
  return out; }"""

GLOB = r"""() => {
  var docs = [document].concat([].slice.call(document.querySelectorAll('iframe.out')).map(function (f) { return f.contentDocument; }).filter(Boolean));
  var fb = {}, api = {};
  docs.forEach(function (d) {
    [].forEach.call(d.querySelectorAll('style[data-nbrw-fallback]'), function (s) { var k = s.getAttribute('data-nbrw-id') || '?'; fb[k] = (fb[k] || 0) + 1; });
    var w = d.defaultView; if (w && w.__nbReaders) Object.keys(w.__nbReaders).forEach(function (k) { api[k] = 1; });
  });
  var keys = []; for (var i = 0; i < localStorage.length; i++) keys.push(localStorage.key(i));
  return {fb: fb, api: Object.keys(api), keys: keys}; }"""

def frame_of(pg, nid):
    for f in pg.frames:
        try:
            if f.evaluate("id => !!document.querySelector('.nbrw[data-nbrw-id=\"' + id + '\"]')", nid): return f
        except Exception: pass
    return None

def act(pg, nid, js, arg=None):
    f = frame_of(pg, nid)
    return f.evaluate("([id, a]) => { var w = document.querySelector('.nbrw[data-nbrw-id=\"' + id + '\"]'); return (" + js + ")(w, a); }", [nid, arg])

def one_page(runs):
    """All outputs of all notebooks in ONE document, each drawn the way a notebook front end draws text/html:
    its own container, innerHTML, then every <script> re-created so that it runs (document.currentScript set).
    (Concatenating the raw strings is no front end: an unclosed tag of one output would swallow the next ones.)"""
    hs = [o["data"].get("text/html") for _nid, outs in runs for o in outs if o["data"].get("text/html")]
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px'><div id='outs'></div>"
            "<div style='height:2400px'></div><script>var H = %s;"
            "H.forEach(function (h) { var d = document.createElement('div'); d.className = 'out'; d.innerHTML = h;"
            " document.getElementById('outs').appendChild(d);"
            " [].slice.call(d.querySelectorAll('script')).forEach(function (o) { var n = document.createElement('script');"
            " n.textContent = o.textContent; o.parentNode.replaceChild(n, o); }); });</script>"
            % json.dumps(hs).replace("</", "<\\/"))

def check(pg, way, ids, titles, fails, rows):
    def bad(m): fails.append("%s %s" % (way, m))
    byT = dict(("title:" + t, n) for n, t in titles.items())
    S = lambda: dict((byT.get(k, k), v) for k, v in pg.evaluate(ST).items())
    s0 = S()
    for nid in ids:
        w = s0.get(nid) or []
        if len(w) != 1: bad("M1 %s: %d windows, want 1" % (nid, len(w))); continue
        if titles.get(nid) and titles[nid] not in w[0]["title"]: bad("M1 %s holds %r, want its own title %r" % (nid, w[0]["title"][:30], titles[nid][:30]))
        if w[0]["view"] != "cover": bad("M1 %s starts on %r, want the preview" % (nid, w[0]["view"]))
    rows.append("%s M1 windows %s · views %s" % (way, {k: len(v) for k, v in s0.items()}, {k: v[0]["view"] for k, v in s0.items()}))
    if any(len(s0.get(n) or []) != 1 for n in ids): return
    A, others = ids[0], ids[1:]
    base = {n: s0[n][0] for n in ids}
    # M2
    act(pg, A, "function (w) { w.querySelector('[data-nbrw-act=play]').click(); }"); pg.wait_for_timeout(400)
    s1 = S()
    if s1[A][0]["view"] != "doc": bad("M2 Play in %s → %r" % (A, s1[A][0]["view"]))
    for n in others:
        if s1[n][0]["view"] != "cover": bad("M2 Play in %s moved %s to %r" % (A, n, s1[n][0]["view"]))
    # M3
    act(pg, A, "function (w) { ['h+', 'h+', 'a+', 'skin'].forEach(function (k) { w.querySelector('.nbrw-btn[data-act=\"' + k + '\"]').click(); }); }")
    pg.wait_for_timeout(300)
    # M4
    a = act(pg, A, "function (w) { var t = w.querySelector('.nbrw-task[data-task=t1]'); return t && t.getAttribute('data-a'); }")
    if a:
        import base64
        d = json.loads(base64.b64decode(a))
        if "f" in d:
            act(pg, A, """function (w, d) { var t = w.querySelector('.nbrw-task[data-task=t1]');
              d.f.forEach(function (x) { t.querySelector('.nbrw-input[data-f="' + x[0] + '"]').value = String(x[1]); });
              t.querySelector('.nbrw-check').click(); }""", d)
        else:
            act(pg, A, "function (w, c) { var t = w.querySelector('.nbrw-task[data-task=t1]'); t.querySelectorAll('input[type=radio]')[c].checked = true; t.querySelector('.nbrw-check').click(); }", d["c"])
        pg.wait_for_timeout(250)
    else: bad("M4 %s has no exercise t1" % A)
    s2 = S()
    a2 = s2[A][0]
    rows.append("%s M2-M4 %s: view %s, h %d, font %.1f → %.1f, skin %s, t1 %s, %r · others %s" % (
        way, A, a2["view"], a2["h"], base[A]["f"], a2["f"], a2["skin"], a2["t1"], a2["xp"],
        " ".join("%s[%s %d %.1f %s t1 %s %r]" % (n, s2[n][0]["view"], s2[n][0]["h"], s2[n][0]["f"], s2[n][0]["skin"], s2[n][0]["t1"], s2[n][0]["xp"]) for n in others)))
    if a2["h"] != base[A]["h"] + 200 or not a2["f"] > base[A]["f"] or a2["skin"] == base[A]["skin"] or a2["t1"] != "solved":
        bad("M3/M4 %s did not change: %s" % (A, a2))
    for n in others:
        for k in ("view", "h", "f", "skin", "t1", "xp"):
            if s2[n][0][k] != base[n][k]: bad("M3/M4 %s changed %s in %s: %r → %r" % (A, k, n, base[n][k], s2[n][0][k]))
    # M5
    pg.reload(); pg.wait_for_timeout(4000)
    s3 = S()
    if s3.get(A) and (s3[A][0]["h"] != a2["h"] or s3[A][0]["skin"] != a2["skin"] or s3[A][0]["t1"] != "solved"): bad("M5 %s not kept: %s" % (A, s3[A][0]))
    for n in others:
        for k in ("h", "f", "skin", "t1", "xp"):
            if s3.get(n) and s3[n][0][k] != base[n][k]: bad("M5 after reload %s's %s: %r → %r" % (n, k, base[n][k], s3[n][0][k]))
    # M6
    g = pg.evaluate(GLOB)
    rows.append("%s M5 after reload kept %s · M6 fallback styles %s · API %s · keys %d" % (way, bool(s3.get(A)), g["fb"], sorted(g["api"]), len(g["keys"])))
    for n in ids:
        if g["fb"].get(n) != 1: bad("M6 fallback style for %s: %s" % (n, g["fb"].get(n)))
        if n not in g["api"]: bad("M6 no per-notebook API for %s" % n)
    stray = [k for k in g["keys"] if k.startswith("digichemjn.") and not any(k.startswith("digichemjn.%s." % n) for n in ids)]
    if stray: bad("M6 keys without a notebook id: %s" % stray[:4])

def main():
    args = sys.argv[1:]
    nbs = [a for a in args if a.endswith(".ipynb")]
    if len(nbs) == 1:      # scripts.txt gives one notebook: the others are the builds next to it in the tree
        import glob
        top = os.path.dirname(os.path.dirname(HERE))
        v = re.search(r"_v([\d.]+)\.ipynb$", nbs[0])
        for pat in ("modeling/Introduction_to_Modeling_v%s.ipynb", "vorlage/Vorlage_v%s.ipynb"):
            f = os.path.join(top, pat % (v.group(1) if v else "*"))
            g = sorted(glob.glob(f), key=os.path.getmtime)
            if g: nbs.append(g[-1])
            else: print("BAD no %s (build it first)" % f); sys.exit(1)
    jout = args[args.index("--json") + 1] if "--json" in args else None
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    rows, fails, runs, titles = [], [], [], {}
    for nb in nbs:
        outs, errs, _ch = run_cell(nb, {})
        if errs: fails.append("%s the run raised: %s" % (os.path.basename(nb), errs[:1]))
        rd = [o["data"].get("text/html") for o in outs if (o["data"].get("text/html") or "").startswith("<div class='nbreading'")]
        m = re.search(r"__NBREADID__|digichemjn\.([\w.-]+?)\.reader", rd[0] if rd else "")
        nid = re.search(r"var V = '[^']*', ID = '([^']*)'", rd[0] if rd else "")
        nid = nid.group(1) if nid else (m.group(1) if m and m.group(1) else os.path.basename(nb))
        t = re.search(r"nbr-nbtitle-h\"[^>]*>(.*?)</div>", rd[0] if rd else "")
        titles[nid] = re.sub(r"<[^>]+>", "", t.group(1)).strip() if t else ""
        runs.append((nid, outs))
    ids = [n for n, _ in runs]
    rows.append("notebooks: %s" % ", ".join("%s (%s)" % (n, titles[n][:24]) for n in ids))
    if len(set(ids)) != len(ids): fails.append("two notebooks share an id: %s" % ids)
    tmpd = tempfile.mkdtemp(prefix="envmu_"); srv = serve(tmpd)
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    allouts = [o for _n, outs in runs for o in outs]
    open(os.path.join(tmpd, "frames.html"), "w", encoding="utf-8").write(
        host_page(allouts, False).replace("</iframe><script>", "</iframe><div style='height:2400px'></div><script>", 1))
    open(os.path.join(tmpd, "one.html"), "w", encoding="utf-8").write(one_page(runs))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            for way, page in (("(i) frames", "frames.html"), ("(ii) one page", "one.html")):
                ctx = b.new_context(viewport={"width": 1400, "height": 900})
                pg = ctx.new_page(); pg.goto(base + page); pg.wait_for_timeout(4000)
                check(pg, way, ids, titles, fails, rows)
                ctx.close()
        except Exception as e:
            fails.append("BAD %s" % str(e)[:300])
        b.close()
    srv.shutdown(); shutil.rmtree(tmpd, ignore_errors=True)
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-ENV-MULTI OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
