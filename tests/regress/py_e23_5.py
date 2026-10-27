"""E23.5 · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e23_5.py <notebook.ipynb>
  MULTIPLE CHOICE AND OWN DATA IN EVERY CONTENT (E23.5, Nutzer 06.10.: "BYOD
  und Multiple Choice auch in den Modi plain und coding"). For "code" and
  "plain", in a real JupyterLab:
    cover  a copy run with the mode stored as the cover stores it
           (digichemjn.mode.<id>); its cover — the last output of the run,
           `.nbcover-out`, brought up again (E24.3) — shows the quiz and
           own-data marks (rows .nbtl-quiz / .nbtl-byod with a box > 0)
    run    a copy run with that mode (stored for the kernel as the page stores
           it, ~/.digichemjn/<id>.mode): the feed says the mode (precondition);
           after a click on the Appendix pill the quiz and own-data sections
           are there, drawn, not locked, and their timeline marks are shown
           (not .nbgone, opacity > 0); "I have worked through the quiz" fills
           the quiz mark (st-ans in the mark)
  v1.63: plain builds neither section (E16.11) and the cover hides both marks in
  "code" and "plain" (they carry .nbtl-calc). Owner: Python (build), the cover
  rows: js 19-rail-title-sync (one line, py-E23.5).
exit 0 = REGRESS-PY-E23-5 OK. (A stage-2 script only: no matrix tests here.)"""
import sys, os, json, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
COVER_JS = """() => { """ + FRONT + """
  if (!P) return null;
  return [].map.call(P.querySelectorAll('.nbcover-out .nbtl-row.nbtl-quiz, .nbcover-out .nbtl-row.nbtl-byod'), function(r){
    var b = r.getBoundingClientRect(); return [/nbtl-quiz/.test(r.className) ? 'quiz' : 'byod', Math.round(b.width), Math.round(b.height),
      getComputedStyle(r).display, r.getAttribute('data-st')]; }); }"""
DOC_JS = """() => { """ + FRONT + """
  if (!P) return null;
  var f = P.querySelectorAll('.nbfeed[data-nbmode]'); f = f.length ? f[f.length - 1].getAttribute('data-nbmode') : null;
  var ex = [].map.call(P.querySelectorAll('.acc-exsec'), function(a){
    var h = a.querySelector('.jupyter-widget-Collapse-header'), b = h ? h.getBoundingClientRect() : {width: 0, height: 0};
    return [h ? h.textContent.trim().slice(0, 30) : '', /acc-locked/.test(a.className), Math.round(b.width), Math.round(b.height)]; });
  var pn = [].map.call(document.querySelectorAll('#nbpanel-root a.nbmap-node'), function(a){
    var t = a.getAttribute('data-target') || '', m = /^(quiz|byod)/.exec(t); if (!m) return null;
    var st = [], all = [a].concat([].slice.call(a.querySelectorAll('*')));
    all.forEach(function(e){ var c = e.className; c = c && c.baseVal !== undefined ? c.baseVal : String(c || '');
      (c.split(/\\s+/).filter(function(x){ return /^(st|cd)-[a-z]+$/.test(x); }) || []).forEach(function(x){ if (st.indexOf(x) < 0) st.push(x); }); });
    return [m[1], /nbgone/.test(a.className), +getComputedStyle(a).opacity, st.join(' '), a.className]; }).filter(Boolean);
  return {mode: f, ex: ex, panel: pn}; }"""

def _open(b, base, root, src, items, tag):
    import run as R
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    ctx.add_init_script(R.INIT_JS % json.dumps(items))
    pg = ctx.new_page(); pg.errs = []
    pg.on("pageerror", lambda e: pg.errs.append(str(e)[:160]))
    name = "e235_%s_%d_%s" % (tag, int(time.time() * 1000) % 10 ** 7, os.path.basename(src))
    shutil.copy(src, os.path.join(root, name))
    pg.goto(base + "/lab/tree/" + name + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(1500)
    return ctx, pg, name

def one_mode(b, base, root, src, mode, rows, fails):
    import run as R
    from lab_keys import kill_sessions
    nid = R.nb_id(src)
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    kill_sessions(base)
    for d in (kh, root):
        shutil.rmtree(os.path.join(d, ".digichemjn"), ignore_errors=True)
    os.makedirs(os.path.join(kh, ".digichemjn"), exist_ok=True)
    open(os.path.join(kh, ".digichemjn", nid + ".mode"), "w").write(mode)
    items = {"digichemjn.mode." + nid: mode}
    # --- the cover (E24.3: the last output of the mega-cell, `.nbcover-out`)
    # Behauptete bisher: the cover is the cold markdown cell of a second copy
    # opened beside a run one ("the cold cover was not taken up", red since
    # py-E24.3: that cell is one start line). Now the cover of the run copy,
    # built with the stored mode, brought back over the notebook as a run
    # brings it (window.__nbCoverShow, js-E24.3) and read where the reader sees
    # it; put away again afterwards.
    ctx, pg, _ = _open(b, base, root, src, items, "host")
    try:
        R.run_front(pg, nid)
        up = pg.evaluate("() => !!(window.__nbCoverShow && window.__nbCoverShow(true))")
        cv = None
        for _ in range(30):
            pg.wait_for_timeout(500)
            pg.evaluate("() => { " + FRONT + " var l = P && P.querySelector('.nbcover-out .nbtl-lane, .nbcover-out .nbcover-map'); if (l) l.scrollIntoView({block: 'center'}); }")
            cv = pg.evaluate(COVER_JS)
            if cv and any(r[3] for r in cv) and pg.evaluate("() => { " + FRONT + " return !!(P && P.querySelector('.nbcover-out[data-nbcov] .nbtl-row[data-st]')); }"): break
        rows.append("E23.5 %s cover (output of the run, up again): %s" % (mode, cv))
        kinds = sorted(r[0] for r in (cv or []) if r[1] > 0 and r[2] > 0 and r[3] != "none")
        if not up or not pg.evaluate("() => { " + FRONT + " return !!(P && P.querySelector('.nbcover-out[data-nbcov] .nbtl-row[data-st]')); }"):
            fails.append("E23.5 %s BAD the cover (.nbcover-out) did not come up, painted by our script (up %s, no data-st)" % (mode, up))
        elif kinds != ["byod", "quiz"]:
            fails.append("E23.5 %s: the cover shows %s of the quiz / own-data marks" % (mode, kinds or "none"))
        pg.evaluate("() => { if (window.__nbCoverShow) window.__nbCoverShow(false); }")
    finally:
        ctx.close()
    # --- a run with that mode
    kill_sessions(base)
    ctx, pg, _ = _open(b, base, root, src, items, "run")
    try:
        R.run_front(pg, nid)
        d = pg.evaluate(DOC_JS)
        if not d or d["mode"] != mode:
            fails.append("E23.5 %s BAD the run built %s" % (mode, d and d["mode"])); return
        # the Appendix pill, as the reader opens it
        ap = pg.evaluate("""() => { """ + FRONT + """
          var h = [].filter.call(P.querySelectorAll('.acc-group > .jupyter-widget-Collapse-header, .jupyter-widget-Collapse-header'),
              function(h){ return /^\\W*(Appendix|Anhang)\\s*$/.test(h.textContent.trim()); })[0];
          if (!h) return null; h.setAttribute('data-e235', 'app');
          return /lm-mod-hidden/.test((h.parentElement.querySelector(':scope > .jupyter-widget-Collapse-contents') || {}).className || ''); }""")
        if ap is None:
            fails.append("E23.5 %s BAD no Appendix pill" % mode); return
        if ap:
            pg.locator('[data-e235="app"]').first.scroll_into_view_if_needed(timeout=5000)
            pg.locator('[data-e235="app"]').first.click(timeout=5000); pg.wait_for_timeout(2500)
        d = pg.evaluate(DOC_JS)
        rows.append("E23.5 %s run: sections %s · panel %s" % (mode, d["ex"], [p[:4] for p in d["panel"]]))
        secs = [e for e in d["ex"] if e[2] > 0 and e[3] > 0]
        if len(secs) < 2: fails.append("E23.5 %s: %d of 2 quiz / own-data sections drawn %s" % (mode, len(secs), d["ex"]))
        if any(e[1] for e in d["ex"]): fails.append("E23.5 %s: a quiz / own-data section is locked %s" % (mode, d["ex"]))
        shown = sorted(p[0] for p in d["panel"] if not p[1] and p[2] > 0)
        if shown != ["byod", "quiz"]: fails.append("E23.5 %s: timeline shows %s of the quiz / own-data marks %s" % (mode, shown or "none", d["panel"]))
        # mark the quiz done, as the reader does
        btn = pg.evaluate("""() => { """ + FRONT + """
          var b = [].filter.call(P.querySelectorAll('.acc-exsec button'), function(b){ return /worked through the quiz|Quiz durchgearbeitet/.test(b.textContent); })[0];
          if (!b) return false; b.setAttribute('data-e235', 'done'); return true; }""")
        if not btn:
            fails.append("E23.5 %s BAD no 'worked through the quiz' button" % mode)
        else:
            hd = pg.evaluate("""() => { var b = document.querySelector('[data-e235="done"]'); var a = b.closest('.acc-exsec');
                var h = a.querySelector('.jupyter-widget-Collapse-header'); var c = a.querySelector('.jupyter-widget-Collapse-contents');
                if (c && /lm-mod-hidden/.test(c.className)) { h.setAttribute('data-e235', 'qh'); return true; } return false; }""")
            if hd:
                pg.locator('[data-e235="qh"]').first.click(timeout=5000); pg.wait_for_timeout(1200)
            pg.locator('[data-e235="done"]').first.scroll_into_view_if_needed(timeout=5000)
            pg.locator('[data-e235="done"]').first.click(timeout=5000); pg.wait_for_timeout(2500)
            q = [p for p in pg.evaluate(DOC_JS)["panel"] if p[0] == "quiz"]
            rows.append("E23.5 %s quiz marked done: %s" % (mode, [p[3:] for p in q]))
            if not q or not any("st-ans" in p[3].split() for p in q):
                fails.append("E23.5 %s: the quiz mark does not fill after 'worked through' %s" % (mode, q))
        if pg.errs: fails.append("E23.5 %s page errors %s" % (mode, pg.errs[:2]))
    finally:
        ctx.close()
        kill_sessions(base)
        try: os.remove(os.path.join(kh, ".digichemjn", nid + ".mode"))
        except OSError: pass

def main():
    src = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    modes = ["code", "plain"]
    for a in sys.argv[1:]:
        if a.startswith("--modes="): modes = a.split("=", 1)[1].split(",")
    sys.argv = sys.argv[:1] + ["x"]          # run.py parses the command line on import
    rows, fails = [], []
    from lab_keys import ensure_lab, CHROME
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for m in modes:
            try: one_mode(b, base, root, src, m, rows, fails)
            except Exception as e: fails.append("E23.5 %s BAD %s" % (m, str(e)[:200]))
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E23-5 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
