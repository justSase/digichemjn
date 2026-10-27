"""E25 — the JS workshop's tests for the feedback on v1.67 (2026-10-08, Werkstatt JS).
Stage-2 script of tests/regress (scripts.txt), stand-alone:

    python3 tests/regress/js_e25.py <notebook.ipynb> [--other <second.ipynb>] [--only J25.e] [--shot DIR]

A FOREIGN FRONT END (PyCharm), put together as such a viewer does it — PyCharm
itself is a desktop application, not in this container. The mega-cell is run
in a kernel of its own with PYCHARM_HOSTED=1 (every iopub bundle, as
py_e22p.py); the bundles are drawn in ONE page in order (text/html first, else
application/javascript run with `element`, else text/plain), in a browser
whose user agent names JetBrains — no `.jp-NotebookPanel`, no JupyterLab app,
no widget manager (the still copy is what shows; as in the reader's video).

  J25.e1  after the run: one title card on screen — the preview (cover);
          the document's card, the still copy and the feed hidden; the
          floating tool column (#nbpanel-root) not shown (E25.b/g)
  J25.e2  Play (a pointer click at its middle) → ≤ 1 s: the cover gone, the
          document's title card shown with its top in the view (0…200 px),
          the still copy there (≥ 8 000 visible characters)
  J25.f1  one click on another content card → chosen (aria-checked) and
          stored under digichemjn.mode.<id> (≤ 400 ms); with no live widget
          to tell the kernel, a visible line under the cards says so (en/de)
  J25.f2  Play after that → the document (no dead button), the line stays honest

  J25.o1  standard first: a browser left with the OLD shared keys (skin cyber,
          German, content calc, lens 150 %, dark, an account marked on) opens a
          notebook as the standard — minimal, English, both, lens 100 % (the
          middle of the bar), not logged in
  J25.o2  each notebook its own: German + content "code" chosen in Complex →
          after a reload Complex keeps them; Modeling (same browser) stays
          English / both
  J25.o3  logged in per notebook: an account made in Complex → Complex on (also
          after a reload), Modeling not
  J25.o4  favourites at once, already on the preview: Modeling logs in with
          Complex's code + password → German and the style at once (≤ 1 s, no
          run), Complex unchanged by it
  J25.n   report a problem: a link at the foot of the preview; at the click a
          mailto: to the contact address, subject with notebook + version, the
          body with the browser filled in by the page — and the page's last
          error only when the box beside the ⚙ link is ticked (a stand-in
          `.nbfb` when the build has no py-E25.n)
  J25.k   the tidied preview (py-E25.k markup): the language buttons in the
          title card's slot, the account block stays in its fold "Sign in",
          the series shows each notebook's progress from this browser and the
          line "this notebook · the series · all notebooks"; German at once
          (needs py-E25.k: no `.nbcover-series` = BAD)
  J25.v   a too-old browser says so on the preview, with the way (en): the
          page made to lack CSS :has → one line `.nbcompat` naming the minimum
          versions; a current browser → no such line
  J25.h   the line "Not running yet" (py-E25.h `.nbcover-stale`) is on the
          page and not shown where our script runs (a stand-in with the same
          class when the build has no such line)
  (o needs a second notebook with the output cover: --other, else the same
   notebook under another id, `<id>-zwei` — Modeling has no output cover yet)

Every test returns False "BAD …" when its precondition is not met, never True.
Gegenprobe v1.67 (a6d3648c): o1 red (cyber, German, calc taken over), o2 red
(Modeling follows Complex's German), o3 red (Modeling logged in too), o4 red; e1 red (document card + still copy visible over the
cover, tool column shown), e2 red (Play leaves the cover, names a menu path),
f1 red (not stored under the id: no notebook panel → no id).
exit 0 = REGRESS-JS-E25 OK."""
import sys, os, re, json, html, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "JetBrains PyCharm/2025.2 Chrome/122.0 Safari/537.36")

def bundles(src):
    from py_e22p import iopub
    return iopub(src, {"PYCHARM_HOSTED": "1"})

STALE = ("<div class='nbcover-stale' data-j25='stand-in'>Not running yet \u2014 run the cell below</div>")
FB = {"to": "samuel.wiese@gmx.de", "label": {"en": "Report a problem / feedback", "de": "Fehler melden / Feedback"},
      "subject": {"en": "[DigiChemJN] {nb} v{ver}: problem / feedback", "de": "[DigiChemJN] {nb} v{ver}: Fehler / Feedback"},
      "body": {"en": "What happened?\n\n-- filled in by the notebook --\nNotebook: {nb}\nVersion: v{ver}\nEnvironment: {env}\nBrowser: {browser}\nLanguage: {lang}\nMode: {mode}\n{errors}",
               "de": "Was ist passiert?\n\n-- vom Notebook ausgefüllt --\nNotebook: {nb}\nVersion: v{ver}\nUmgebung: {env}\nBrowser: {browser}\nSprache: {lang}\nModus: {mode}\n{errors}"},
      "errors": {"en": "Last error messages of the page:\n{list}", "de": "Letzte Fehlermeldungen der Seite:\n{list}"},
      "tick": {"en": "add the last error messages of this page", "de": "letzte Fehlermeldungen dieser Seite anhängen"},
      "nobrowser": {"en": "(please add)", "de": "(bitte ergänzen)"}, "nb": "Complex Numbers", "ver": "1.67", "env": "pycharm", "lang": "en", "mode": "both"}
def page_html(outs):
    # E25.n: py-E25.n puts `.nbfb[data-nbfeedback]` into the ⚙ drawer; on a build
    # without it the test adds a stand-in (same class, same JSON shape) to the page
    if not any("data-nbfeedback" in (o.get("text/html") or "") for o in outs):
        outs = list(outs) + [{"text/html": "<div class='nbcell pg-fb nbfb' data-j25='stand-in' data-nbfeedback='%s'>"
                              "<a class='nbfb-link' href='mailto:%s'>feedback</a></div>"
                              % (json.dumps(FB, ensure_ascii=False).replace("'", "&#39;"), FB["to"])}]
    # E25.h: py-E25.h writes `.nbcover-stale` into the cover; on a build without it
    # the test puts a stand-in there (same class) so the page's part is measured
    if not any("nbcover-stale" in (o.get("text/html") or "") for o in outs):
        outs = [dict(o) for o in outs]
        for o in outs:
            h = o.get("text/html") or ""
            m = re.search(r'<div class="[^"]*\bnbcover-out\b[^"]*"[^>]*>', h)
            i = m.start() if m else -1
            if i > -1:
                j = h.find(">", i) + 1
                o["text/html"] = h[:j] + STALE + h[j:]
                break
    parts = []
    for o in outs:
        if "error" in o: parts.append(("html", "<pre class='pyc-err'>%s</pre>" % html.escape(o["error"])))
        elif "text/html" in o: parts.append(("html", o["text/html"]))
        elif "application/javascript" in o: parts.append(("js", o["application/javascript"]))
        elif o.get("text/plain"): parts.append(("html", "<pre>%s</pre>" % html.escape(o["text/plain"])))
    # a notebook view: a markdown cell, the code cell (input + its outputs), a cell of the reader's own
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;background:#fff;font-family:sans-serif'>"
            "<div class='pyc-nb'><div class='pyc-cell pyc-md'><p>&#9654; Run the cell below</p></div>"
            "<div class='pyc-cell pyc-code'><pre class='pyc-in'>#@title DigiChemJN</pre><div class='pyc-outs' id='pycouts'></div></div>"
            "<div class='pyc-cell pyc-code'><pre class='pyc-in'>x = 1</pre></div></div>"
            "<script>window.__OUTS=" + json.dumps(parts).replace("</", "<\\/") + ";"
            "(function(){var root=document.getElementById('pycouts');"
            "__OUTS.forEach(function(p,i){var d=document.createElement('div');d.className='pyc-output';root.appendChild(d);"
            "if(p[0]==='html'){d.appendChild(document.createRange().createContextualFragment(p[1]));}"
            "else{try{(new Function('element',p[1]))(d);}catch(e){console.error('js output',i,e);}}});})();</script>")

STATE = r"""() => {
  var vis = function(e){ if (!e) return false; var r = e.getBoundingClientRect(), s = getComputedStyle(e);
    for (var x = e; x; x = x.parentElement) { var cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return false; }
    return r.width > 2 && r.height > 2; };
  var cards = [].filter.call(document.querySelectorAll('.nbtitle'), function(t){ return vis(t) && !t.closest('.nbtitle-h'); });
  var doc = document.querySelector('.nbtitle-doc'), cov = document.querySelector('.nbcover-out'), h = document.getElementById('nbpanel-root');
  var still = [].filter.call(document.querySelectorAll('.nbstatic-note'), vis).length;
  var tools = h ? [].filter.call(h.querySelectorAll('.nbbtn, .nbslider'), vis).length : 0;
  var md = document.querySelector('.pyc-md'), own = document.querySelectorAll('.pyc-in')[1];
  var txt = 0; [].forEach.call(document.querySelectorAll('.pyc-output'), function(o){ if (vis(o) && o !== (cov && cov.closest('.pyc-output'))) txt += (o.innerText || '').length; });
  return {cards: cards.length, doc: vis(doc), docTop: doc ? Math.round(doc.getBoundingClientRect().top) : null,
          cover: vis(cov), still: still, tools: tools, text: txt, md: vis(md), own: vis(own),
          env: window.__nbEnv ? window.__nbEnv().env : null}; }"""

def click_mid(pg, sel):
    pg.evaluate("(s) => { var e = document.querySelector(s); if (e) e.scrollIntoView({block: 'center'}); }", sel)
    pg.wait_for_timeout(350)
    r = pg.evaluate("(s) => { var e = document.querySelector(s); if (!e) return null; var b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }", sel)
    if not r: return False
    pg.mouse.click(r[0], r[1]); return True

def nb_id(pg):
    return pg.evaluate("() => { var f = [].filter.call(document.querySelectorAll('.nbfeed'), function(x){ return x.hasAttribute('data-progress'); }).pop();"
                       " try { return String(JSON.parse(f.getAttribute('data-progress')).id || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); } catch (e) { return null; } }")

OLD = {"digichemjn.skin.v1": "cyber", "digichemjn.lang.v1": "de", "digichemjn.defmode.v1": "calc",
       "digichemjn.zoom.v1": "150", "digichemjn.theme.v1": "dark", "digichemjn.themepick.v1": "dark",
       "digichemjn.account.v1": json.dumps({"v": 1, "id": "DCJ-0000-0000-0000", "on": True,
                                            "fav": {"skin": "cyber", "lang": "de", "mode": "calc"}, "vs": "AAAA", "vh": "x"})}
OSTATE = r"""() => { var c = document.querySelector('.nbcover-out'), A = window.__nbAcct;
  var on = function(sel){ var e = c && c.querySelector(sel); return !!(e && e.getAttribute('aria-checked') === 'true'); };
  var lens = null, k = window.__nbZKey ? window.__nbZKey() : null, sl = document.querySelector('#nbpanel-root .nbz-doc .nbslider');
  try { lens = k ? localStorage.getItem(k) : null; } catch (e) {}
  var cls = document.body.className, ac = c && c.querySelector('.nbacct');
  return {skin: /nbskin-cyber/.test(cls) ? 'cyber' : /nbskin-fairy/.test(cls) ? 'fairy' : 'minimal',
          de: on('.nblang-opt[data-lang="de"]'), en: on('.nblang-opt[data-lang="en"]'),
          mode: ([].filter.call(c ? c.querySelectorAll('.nbmode-opt') : [], function(o){ return o.getAttribute('aria-checked') === 'true'; })[0] || {getAttribute: function(){ return null; }}).getAttribute('data-mode'),
          lens: lens, thumb: sl ? sl.value : null, logged: !!(A && A.on()), acct: ac ? ac.getAttribute('data-in') : null,
          id: window.__nbZKey ? window.__nbZKey() : null}; }"""

def run_o(b, tmp, tmp2, rec, shot):
    """E25.o on two notebooks in one browser (same origin, as Lab/Lite)."""
    ctx = b.new_context(viewport={"width": 1400, "height": 900}, user_agent=UA)
    ctx.add_init_script("(function(o){ try { if (!localStorage.getItem('j25.seeded')) { for (var k in o) localStorage.setItem(k, o[k]); localStorage.setItem('j25.seeded', '1'); } } catch (e) {} })(%s);" % json.dumps(OLD))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg.goto(tmp); pg.wait_for_timeout(3500)
    s = pg.evaluate(OSTATE)
    if s["acct"] is None and s["mode"] is None: rec("J25.o1", False, "BAD no cover (%s)" % s); ctx.close(); return
    ok = s["skin"] == "minimal" and s["en"] and not s["de"] and s["mode"] == "both" and s["lens"] is None and str(s["thumb"]) == "50" and not s["logged"]
    rec("J25.o1", ok, "old shared keys present → skin %s, English %s, content %s, lens stored %s, thumb %s (middle 50), logged in %s"
        % (s["skin"], s["en"], s["mode"], s["lens"], s["thumb"], s["logged"]))
    # o2: this notebook's own choices
    # a pointer click each; the cover may still move under the pointer (the
    # account box draws late) — the choice is checked and clicked once more if
    # it did not land; not landing twice is a BAD precondition, not a result
    for sel, key in (('.nblang-opt[data-lang="de"]', "de"), ('.nbmode-opt[data-mode="code"]', "mode")):
        for _ in range(2):
            click_mid(pg, '.nbcover-out ' + sel); pg.wait_for_timeout(900)
            s0 = pg.evaluate(OSTATE)
            if (s0["de"] if key == "de" else s0["mode"] == "code"): break
    s0 = pg.evaluate(OSTATE)
    if not (s0["de"] and s0["mode"] == "code"):
        rec("J25.o2", False, "BAD the choices did not land on the cover (%s)" % s0); ctx.close(); return
    pg.reload(); pg.wait_for_timeout(3500)
    s1 = pg.evaluate(OSTATE)
    pg2 = ctx.new_page(); pg2.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg2.goto(tmp2); pg2.wait_for_timeout(3500)
    s2 = pg2.evaluate(OSTATE)
    ok = s1["de"] and s1["mode"] == "code" and s2["en"] and not s2["de"] and s2["mode"] == "both" and s1["id"] != s2["id"]
    rec("J25.o2", ok, "first after reload: German %s, content %s · second: English %s, content %s" % (s1["de"], s1["mode"], s2["en"], s2["mode"]))
    # o3: an account made in Complex is on in Complex only
    pg.evaluate("() => window.__nbStore.set('digichemjn.skin.v1', 'cyber')")
    r = pg.evaluate("() => window.__nbAcct.create('j25-passwort').then(function(r){ return r; })")
    pg.wait_for_timeout(300)
    pg2.reload(); pg2.wait_for_timeout(3500)
    a1 = pg.evaluate(OSTATE); a2 = pg2.evaluate(OSTATE)
    pg.reload(); pg.wait_for_timeout(3500); a1r = pg.evaluate(OSTATE)
    ok = bool(r and r.get("ok")) and a1["logged"] and a1r["logged"] and not a2["logged"] and a2["acct"] == "0"
    rec("J25.o3", ok, "account %s: first on %s (after reload %s) · second on %s (cover data-in %s)"
        % (r and r.get("id"), a1["logged"], a1r["logged"], a2["logged"], a2["acct"]))
    # o4: Modeling logs in with Complex's code → German + style at once, on the preview
    code = pg.evaluate("() => window.__nbAcct.code('j25-passwort').then(function(r){ return r.code || null; })")
    if not code: rec("J25.o4", False, "BAD no code from Complex"); ctx.close(); return
    before = pg2.evaluate(OSTATE)
    lr = pg2.evaluate("(c) => window.__nbAcct.login(c, 'j25-passwort').then(function(r){ if (window.__nbAcctAll) window.__nbAcctAll(); return r; })", code)
    pg2.wait_for_timeout(1000)
    after = pg2.evaluate(OSTATE); cx = pg.evaluate(OSTATE)
    if shot: pg2.screenshot(path=os.path.join(shot, "j25o_login.png"))
    ok = bool(lr and lr.get("ok")) and after["logged"] and after["de"] and after["skin"] == "cyber" and before["skin"] == "minimal" and cx["de"] and cx["logged"]
    rec("J25.o4", ok, "second before: %s/%s → after login: on %s, German %s, style %s · first: on %s, German %s · page errors %d"
        % (before["skin"], "de" if before["de"] else "en", after["logged"], after["de"], after["skin"], cx["logged"], cx["de"], len(errs)))
    ctx.close()

def run(src, only=None, shot=None, other=None):
    from playwright.sync_api import sync_playwright
    from lab_keys import CHROME
    outs = bundles(src)
    tmp = os.path.join(tempfile.mkdtemp(prefix="j25_"), "pycharm.html")
    open(tmp, "w", encoding="utf-8").write(page_html(outs))
    # served from 127.0.0.1 (one origin for both pages, a secure context for
    # the account's WebCrypto): file:// pages lost their localStorage across a
    # reload now and then (measured 1 in 3), which no browser of a reader does
    import http.server, threading, functools
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=os.path.dirname(tmp)))
    srv.RequestHandlerClass.log_message = lambda *a, **k: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    rows, fails = [], []
    def rec(name, ok, det):
        rows.append("%-7s %s  %s" % (name, "ok " if ok else "RED", det))
        if not ok: fails.append(name + ": " + det)
    want = lambda n: not only or only in n
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        def fresh():
            ctx = b.new_context(viewport={"width": 1400, "height": 900}, user_agent=UA)
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
            pg.goto(base + "pycharm.html"); pg.wait_for_timeout(3500)
            return ctx, pg, errs
        # e: preview and Play
        if want("J25.e"):
            ctx, pg, errs = fresh()
            s0 = pg.evaluate(STATE)
            if s0["env"] != "pycharm": rec("J25.e1", False, "BAD the page did not take PyCharm (%s)" % s0["env"])
            elif not s0["cover"]: rec("J25.e1", False, "BAD no cover after the run (%s)" % s0)
            else:
                ok = s0["cards"] == 1 and not s0["doc"] and s0["still"] == 0 and s0["tools"] == 0 and s0["md"] and s0["own"]
                rec("J25.e1", ok, "cards on screen %d (want 1), document card %s, still copies %d, tool controls %d, other cells %s/%s"
                    % (s0["cards"], s0["doc"], s0["still"], s0["tools"], s0["md"], s0["own"]))
            if shot: pg.screenshot(path=os.path.join(shot, "j25e_preview.png"))
            if not click_mid(pg, ".nbcover-out .nbcover-play"): rec("J25.e2", False, "BAD no Play on the cover")
            else:
                pg.wait_for_timeout(1000)
                s1 = pg.evaluate(STATE)
                ok = (not s1["cover"]) and s1["doc"] and s1["docTop"] is not None and 0 <= s1["docTop"] <= 200 and s1["text"] >= 8000
                rec("J25.e2", ok, "after Play: cover %s, document card %s at %s px, visible text %d (want ≥ 8000), page errors %d"
                    % (s1["cover"], s1["doc"], s1["docTop"], s1["text"], len(errs)))
                if shot: pg.screenshot(path=os.path.join(shot, "j25e_document.png"))
            ctx.close()
        if want("J25.v"):
            ctx, pg, errs = fresh()
            n0 = pg.evaluate("() => document.querySelectorAll('.nbcover-out .nbcompat').length")
            ctx.close()
            ctx = b.new_context(viewport={"width": 1400, "height": 900}, user_agent=UA)
            ctx.add_init_script("(function(){ var s = CSS.supports.bind(CSS); CSS.supports = function(a, b){ return /:has/.test(String(a)) ? false : s.apply(null, arguments); }; })();")
            pg = ctx.new_page(); pg.goto(base + "pycharm.html"); pg.wait_for_timeout(3500)
            t = pg.evaluate("() => { var x = document.querySelector('.nbcover-out .nbcompat'); return x && x.getBoundingClientRect().height > 2 ? x.textContent : null; }")
            rec("J25.v", n0 == 0 and bool(t) and "105" in (t or "") and "update" in (t or ""),
                "current browser: %d line(s) · without :has: %r" % (n0, (t or "")[:110]))
            ctx.close()
        if want("J25.h"):
            ctx, pg, errs = fresh()
            r = pg.evaluate("""() => { var ls = document.querySelectorAll('.nbcover-stale');
                var vis = [].filter.call(ls, function(e){ var b = e.getBoundingClientRect(); return b.height > 1 && getComputedStyle(e).display !== 'none'; });
                return {n: ls.length, vis: vis.length, stand: !!document.querySelector('.nbcover-stale[data-j25]'), cover: !!document.querySelector('.nbcover-out .nbcover-play')}; }""")
            if not r["n"] or not r["cover"]: rec("J25.h", False, "BAD no line / no cover on the page (%s)" % r)
            else: rec("J25.h", r["vis"] == 0, "%d line(s) %s, %d shown where the script runs (want 0)" % (r["n"], "(stand-in)" if r["stand"] else "(py-E25.h)", r["vis"]))
            ctx.close()
        if want("J25.k"):
            ctx = b.new_context(viewport={"width": 1400, "height": 900}, user_agent=UA)
            prog = {"complex-numbers": {"title": "Complex Numbers", "a": [3, 9]}, "sets": {"title": "Sets", "a": [2, 5]},
                    "intro-modeling": {"title": "Introduction to Modeling", "a": [1, 11]}}
            ctx.add_init_script("try { if (!localStorage.getItem('j25k')) { localStorage.setItem('digichemjn.progress.v1', %r); localStorage.setItem('j25k', '1'); } } catch (e) {}" % json.dumps(prog))
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
            pg.goto(base + "pycharm.html"); pg.wait_for_timeout(3500)
            K = """() => { var c = document.querySelector('.nbcover-out'); if (!c || !c.querySelector('.nbcover-series')) return null;
              var row = c.querySelector('.nblang'), ac = c.querySelector('.nbacct'), ser = c.querySelector('.nbcover-series');
              var li = function(id){ var e = ser.querySelector('li.nbser-it[data-nbid="' + id + '"]'); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; };
              var sm = ser.querySelector('.nbser-sum');
              return {slot: !!(row && row.parentNode && row.parentNode.classList.contains('nbcover-lang-slot')),
                      fold: !!(ac && ac.closest('details.nbacct-fold')), cx: li('complex-numbers'), sets: li('sets'), start: li('start-here'),
                      sum: sm ? sm.textContent : null}; }"""
            k0 = pg.evaluate(K)
            if not k0: rec("J25.k", False, "BAD no series on the preview (build without py-E25.k)")
            else:
                click_mid(pg, '.nbcover-out .nblang-opt[data-lang="de"]'); pg.wait_for_timeout(900)
                k1 = pg.evaluate(K)
                # this notebook's own record is the run's (it overwrites the seed); the others are the seed
                me = pg.evaluate("() => { try { return JSON.parse(localStorage.getItem('digichemjn.progress.v1'))['complex-numbers'].a; } catch (e) { return null; } }") or [0, 0]
                se, al = [me[0] + 2, me[1] + 5], [me[0] + 3, me[1] + 16]
                ok = (k0["slot"] and k0["fold"] and ("%d/%d" % tuple(me)) in (k0["cx"] or "") and "2/5" in (k0["sets"] or "")
                      and ("this notebook %d/%d" % tuple(me)) in (k0["sum"] or "") and ("series %d/%d" % tuple(se)) in (k0["sum"] or "")
                      and ("all notebooks %d/%d" % tuple(al)) in (k0["sum"] or "")
                      and "Mengen" in (k1["sets"] or "") and ("dieses Notebook %d/%d" % tuple(me)) in (k1["sum"] or ""))
                rec("J25.k", ok, "language in the card slot %s · account in its fold %s · %r · %r · %r · %r → de %r · %r"
                    % (k0["slot"], k0["fold"], k0["cx"], k0["sets"], k0["start"], k0["sum"], k1["sets"], k1["sum"]))
                if shot:
                    pg.evaluate("() => { var c = document.querySelector('.nbcover-out .nbtitle-card'); if (c) c.scrollIntoView({block: 'start'}); }")
                    pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(shot, "j25k_preview.png"))
                    pg.evaluate("() => { var c = document.querySelector('.nbcover-out .nbcover-series'); if (c) c.scrollIntoView({block: 'end'}); }")
                    pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(shot, "j25k_series.png"))
            ctx.close()
        if want("J25.n"):
            # E29 P5 (JS, 12.10.) — behauptete bisher: a mailto link at the foot of the preview, a tick
            # "add the last error messages", the click filling the e-mail, a ring of the page's errors.
            # The reader took that back (STOP E29 P5: no form, no mailto, no error buffer — only a line of
            # text, Python's). Now: none of it is made by the page, and an error is kept nowhere.
            ctx, pg, errs = fresh()
            pg.evaluate("() => { setTimeout(function(){ throw new Error('j25-probe'); }, 0); }")
            pg.wait_for_timeout(1800)
            a = pg.evaluate("""() => ({cover: document.querySelectorAll('.nbfb-cover').length, tick: document.querySelectorAll('.nbfb-tick,.nbfb-err').length,
                ring: Array.isArray(window.__nbErrs), off: typeof window.__nbFbOff === 'function', last: window.__nbFbLast || null})""")
            rec("J25.n", not any(a.values()), "page-made feedback link %d, tick %d, error ring %s, click rewrite %s, filled mailto %s (want none)"
                % (a["cover"], a["tick"], a["ring"], a["off"], a["last"]))
            ctx.close()
        if want("J25.f"):
            ctx, pg, errs = fresh()
            nid = nb_id(pg)
            if not nid: rec("J25.f1", False, "BAD no notebook id on the feed")
            else:
                pg.evaluate("() => { var c = document.querySelector('.nbcover-out'); if (c) c.scrollIntoView(); }")
                pg.wait_for_timeout(200)
                pg.evaluate("""() => { window.__j25 = null; document.addEventListener('click', function h(ev){
                    if (ev.target.closest && ev.target.closest('.nbmode-opt[data-mode="calc"]')) { window.__j25 = performance.now(); document.removeEventListener('click', h, true); } }, true); }""")
                if not click_mid(pg, '.nbcover-out .nbmode-opt[data-mode="calc"]'): rec("J25.f1", False, "BAD no card calc")
                else:
                    pg.wait_for_timeout(400)
                    r = pg.evaluate("""(id) => { var o = document.querySelector('.nbcover-out .nbmode-opt[data-mode="calc"]'), n = document.querySelector('.nbcover-out .nbmode-note');
                        var vis = n && n.getBoundingClientRect().height > 2 && getComputedStyle(n).display !== 'none';
                        return {on: o && o.getAttribute('aria-checked'), st: localStorage.getItem('digichemjn.mode.' + id),
                                pend: localStorage.getItem('digichemjn.mode.__pending'), note: vis ? n.textContent : null}; }""", nid)
                    ok = r["on"] == "true" and r["st"] == "calc" and bool(r["note"])
                    rec("J25.f1", ok, "card %s, stored mode.%s=%s (pending %r), note %r" % (r["on"], nid, r["st"], r["pend"], (r["note"] or "")[:90]))
                    if shot: pg.screenshot(path=os.path.join(shot, "j25f_card.png"))
                    click_mid(pg, ".nbcover-out .nbcover-play"); pg.wait_for_timeout(1000)
                    s = pg.evaluate(STATE)
                    rec("J25.f2", (not s["cover"]) and s["doc"], "after Play: cover %s, document %s, page errors %d" % (s["cover"], s["doc"], len(errs)))
            ctx.close()
        if want("J25.o"):
            # the second notebook: --other (it needs the output cover, E24.3), else the
            # same notebook under another id — Modeling has no output cover yet (NACHZIEHEN)
            tmp2 = os.path.join(os.path.dirname(tmp), "pycharm2.html")
            if other: page2 = page_html(bundles(other))
            else:
                nid = json.loads(re.search(r'data-progress=\'(\{.*?\})\'', "".join(o.get("text/html", "") for o in outs)).group(1))["id"]
                page2 = page_html(outs).replace(nid, nid + "-zwei")
            open(tmp2, "w", encoding="utf-8").write(page2)
            run_o(b, base + "pycharm.html", base + "pycharm2.html", rec, shot)
        b.close()
    srv.shutdown()
    return rows, fails

def main():
    a = sys.argv[1:]
    only = a[a.index("--only") + 1] if "--only" in a else None
    shot = a[a.index("--shot") + 1] if "--shot" in a else None
    other = a[a.index("--other") + 1] if "--other" in a else None
    src = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--only", "--shot", "--other"))][0]
    rows, fails = run(src, only, shot, other)
    print("\n".join(rows))
    print("REGRESS-JS-E25 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
