"""E25.l · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_l.py <notebook.ipynb> [--modes=both,code,plain]
  MULTIPLE CHOICE AND OWN DATA OUT, IN EVERY MODE (E25.l, Nutzer 08.10.:
  "MCQ und BYOD vorerst ganz raus … Timeline, Cover, Dokument, Gating,
  Fortschritt"; replaces E23.5, whose test py_e23_5 asserted the opposite).
  For each mode, in a real JupyterLab:
    cover  a copy run with the mode stored as the cover stores it; its cover
           (`.nbcover-out`, brought up again) is painted by our script
           (precondition: rows with data-st) and has NO quiz / own-data row
    run    a copy run with that mode: the feed says the mode, the Appendix
           opened as the reader opens it (precondition: it opens, the panel
           has marks); no quiz / own-data section in the document, no quiz /
           own-data mark in the panel, the progress record (data-progress)
           counts no q1 / b1
  v1.67: both/code/plain show both marks and both sections (E23.5). Owner: Python.
exit 0 = REGRESS-PY-E25-L OK. (A stage-2 script only: no matrix tests here.)"""
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
  var sec = [].filter.call(P.querySelectorAll('.jupyter-widget-Collapse-header'), function(h){
    return /multiple.choice|quiz|own data|eigene daten|bring your own/i.test(h.textContent); }).map(function(h){ return h.textContent.trim().slice(0, 40); });
  var nodes = document.querySelectorAll('#nbpanel-root a.nbmap-node').length;
  var pr = [].map.call(P.querySelectorAll('.nbfeed[data-progress]'), function(e){ return e.getAttribute('data-progress'); }).pop() || null;
  return {mode: f, ex: ex, panel: pn, sec: sec, nodes: nodes, prog: pr}; }"""

def _open(b, base, root, src, items, tag):
    import run as R
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    ctx.add_init_script(R.INIT_JS % json.dumps(items))
    pg = ctx.new_page(); pg.errs = []
    pg.on("pageerror", lambda e: pg.errs.append(str(e)[:160]))
    name = "e25l_%s_%d_%s" % (tag, int(time.time() * 1000) % 10 ** 7, os.path.basename(src))
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
        rows.append("E25.l %s cover (output of the run, up again): %s" % (mode, cv))
        kinds = sorted(r[0] for r in (cv or []) if r[1] > 0 and r[2] > 0 and r[3] != "none")
        if not up or not pg.evaluate("() => { " + FRONT + " return !!(P && P.querySelector('.nbcover-out[data-nbcov] .nbtl-row[data-st]')); }"):
            fails.append("E25.l %s BAD the cover (.nbcover-out) did not come up, painted by our script (up %s, no data-st)" % (mode, up))
        elif cv:
            fails.append("E25.l %s: the cover has quiz / own-data rows %s (visible %s)" % (mode, [r[0] for r in cv], kinds))
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
            fails.append("E25.l %s BAD the run built %s" % (mode, d and d["mode"])); return
        # the Appendix pill, as the reader opens it
        ap = pg.evaluate("""() => { """ + FRONT + """
          var h = [].filter.call(P.querySelectorAll('.acc-group > .jupyter-widget-Collapse-header, .jupyter-widget-Collapse-header'),
              function(h){ return /^\\W*(Appendix|Anhang)\\s*$/.test(h.textContent.trim()); })[0];
          if (!h) return null; h.setAttribute('data-e235', 'app');
          return /lm-mod-hidden/.test((h.parentElement.querySelector(':scope > .jupyter-widget-Collapse-contents') || {}).className || ''); }""")
        if ap is None:
            fails.append("E25.l %s BAD no Appendix pill" % mode); return
        if ap:
            pg.locator('[data-e235="app"]').first.scroll_into_view_if_needed(timeout=5000)
            pg.locator('[data-e235="app"]').first.click(timeout=5000); pg.wait_for_timeout(2500)
        d = pg.evaluate(DOC_JS)
        rows.append("E25.l %s run: exercise sections %s · quiz/own-data headers %s · panel %d marks, quiz/own-data %s · progress %s"
                    % (mode, [e[0] for e in d["ex"]], d["sec"], d["nodes"], [p[:2] for p in d["panel"]], (d["prog"] or "")[:120]))
        if d["nodes"] < 10: fails.append("E25.l %s BAD the panel has %d marks" % (mode, d["nodes"]))
        if not d["prog"]: fails.append("E25.l %s BAD no progress record (data-progress)" % mode)
        if d["sec"]: fails.append("E25.l %s: quiz / own-data sections in the document %s" % (mode, d["sec"]))
        if d["panel"]: fails.append("E25.l %s: quiz / own-data marks in the timeline %s" % (mode, d["panel"]))
        try:
            pj = json.loads(d["prog"] or "{}"); tot = (pj.get("a") or [0, 0])[1]
        except Exception:
            pj, tot = {}, None
        want = {"both": 7}.get(mode) if "complex" in os.path.basename(src).lower() else None
        rows.append("E25.l %s progress: exercises counted %s (want %s)" % (mode, tot, want))
        if want is not None and tot != want: fails.append("E25.l %s: the progress counts %s exercises, want %s (no q1/b1)" % (mode, tot, want))
        if pg.errs: fails.append("E25.l %s page errors %s" % (mode, pg.errs[:2]))
    finally:
        ctx.close()
        kill_sessions(base)
        try: os.remove(os.path.join(kh, ".digichemjn", nid + ".mode"))
        except OSError: pass

def main():
    src = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    modes = ["both", "code", "plain"]
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
            except Exception as e: fails.append("E25.l %s BAD %s" % (m, str(e)[:200]))
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E25-L OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
