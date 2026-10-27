"""E31 · Pflichttest (STOP.md, E31 — Nutzer 12.10. zu v1.77) — Python workshop.
    python3 tests/regress/py_e31.py [<notebook.ipynb> | --nb vorlage] [--only C1,F1,W1] [--js] [--shots DIR]

Rows (je Punkt rot gegen v1.77):
  C1  THE START IS PLAIN ABOUT "DO NOT CHANGE" (static). The markdown cell:
      still ONE paragraph (E25.c), line 1 the run line en/de; then a line of
      its own with ⚠ and a bold "do not edit" in English and one in German
      — breaks/unbrauchbar, reading is fine/gelesen werden + own notebooks
      (Vorlage), hack into the solutions/Lösungen hacken + cheating yourself/
      Selbstbetrug. The code cell: the comment block one sentence per line
      (no comment line carries two sentences), the same warning in it, en
      and de; the cargo still ONE line. v1.77: the warning only in the cell,
      two sentences and more per line.
  F1  FORMULAS SCALE WITH THE TEXT (Python: the formula tags). Every formula
      the run draws (svg.imath / svg.dmath / img.nbmath, also the reading
      copy's nbr- names) is sized in em — no px in height, width or margin;
      in the reading window (real kernel, every output its own iframe, all
      folds open) every visible formula's height at text size 90 / 150 %
      is 0.9 / 1.5 × its height at 100 % ±3 %. v1.77: math_img px (k05).
  W1  THE WINDOW STAYS AFTER EVERY RUN (PyCharm Video 1, v1.77: [3] cover,
      [4] after a re-run empty).
      a  the code cell does not mark its output collapsed/hidden — nbformat's
         `collapsed` is the OUTPUT's state (PyCharm, VS Code, Notebook 6 and
         a JupyterLab opening a saved file follow it); `jupyter.outputs_hidden`
         false
      b  the cell run 5× in ONE kernel (jupyter_client, every iopub message):
         per run exactly one reading version, and after it NO message that
         changes or clears an output of the cell (update_display_data,
         clear_output) — a viewer that drops or rebuilds outputs on such a
         message cannot touch the window
      c  a PyCharm-like viewer replays the 5 runs in one page (localStorage
         kept between runs): every output a page of its own; a run clears the
         cell's outputs, display_data appends, update_display_data replaces
         the output's page (a new page, as a webview does), clear_output
         empties the cell; at the end of the run the cell's metadata applies
         (collapsed → output area hidden). 5 s after each run: exactly ONE
         visible reading window (.nbrw, ≥ 300 px high), and it is the first
         visible output.
      d  (JS, reported; red only with --js) the same 5 runs with ALL outputs
         of the cell in ONE page and the widgets drawn from the kernel's model
         states (a viewer with its own widget manager): one visible window
         after 5 s. The reading script steps back (20-reader `back()` at 1.5 /
         4 s) where it sees .acc-root/.nb-live in its page.
Owner: Python (C1, F1 formulas, W1 a–c) · JS (W1 d). exit 0 = REGRESS-PY-E31 OK."""
import sys, os, re, json, time, tempfile, shutil, html as _h
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

WMIME = "application/vnd.jupyter.widget-view+json"

# ---------------------------------------------------------------- C1
def c1(nb, rows, fails):
    from markdown_it import MarkdownIt
    md = [c for c in nb["cells"] if c["cell_type"] == "markdown"]
    text = "".join(md[0]["source"]) if md else ""
    toks = MarkdownIt("commonmark").parse(text)
    top = [t.type for t in toks if t.level == 0]
    html = MarkdownIt("commonmark").render(text)
    lines = [re.sub(r"<[^>]+>", "", l) for l in re.split(r"<br\s*/?>", html)]
    plain = [_h.unescape(l).strip() for l in lines if l.strip()]
    warn = [l for l in plain if "⚠" in l]
    en = [l for l in warn if re.search(r"do not (edit|change)", l, re.I) and re.search(r"breaks", l)
          and re.search(r"[Rr]eading .*fine", l) and re.search(r"own notebooks", l) and re.search(r"hack into the solutions", l)
          and re.search(r"cheating yourself", l)]
    de = [l for l in warn if re.search(r"nicht ändern", l, re.I) and "unbenutzbar" in l and "gelesen werden" in l
          and "eigener Notebooks" in l and "Lösungen hacken" in l and "Selbstbetrug" in l]
    bold = re.findall(r"<strong>([^<]*)</strong>", _h.unescape(html))
    bw = [b for b in bold if re.search(r"(?i)do not (edit|change)|nicht ändern", b)]
    rows.append("C1 markdown: %s · %d lines · ⚠ lines %d (en %d, de %d) · bold warnings %s"
                % (top, len(plain), len(warn), len(en), len(de), bw))
    if top.count("paragraph_open") != 1 or "html_block" in top: fails.append("C1 the start cell is not one paragraph: %s" % top)
    if not plain or "Run the cell below" not in plain[0] or "Zelle darunter" not in plain[0]:
        fails.append("C1 line 1 is not the run line: %r" % (plain[:1],))
    if len(warn) < 1 or len(en) != 1 or len(de) != 1 or len(bw) < 2:
        fails.append("C1 no visible warning line en+de with ⚠ and bold 'do not edit' (en %d, de %d, bold %d)" % (len(en), len(de), len(bw)))
    if warn and plain and plain[0] in warn: fails.append("C1 the warning sits in the run line, want a line of its own")
    cell = max(nb["cells"], key=lambda c: len("".join(c["source"])))
    cl = "".join(cell["source"]).rstrip("\n").split("\n")
    com = [l for l in cl if l.startswith("#") and not l.startswith(("#@title", "# <editor-fold", "# </editor-fold"))]
    multi = [l for l in com if len(re.findall(r"[.!?)](?=\s+[A-ZÄÖÜ▶⚠])", l[2:])) >= 1 or l.count(" · ") >= 1]
    cen = any(re.search(r"Do not edit|do not change", l, re.I) for l in com) and any("Selbstbetrug" in l for l in com)
    cargo = [l for l in cl if l.startswith("_NBZ = ")]
    rows.append("C1 code cell: %d lines, %d comment lines, %d with more than one sentence, warning en+de %s, cargo lines %d"
                % (len(cl), len(com), len(multi), cen, len(cargo)))
    if multi: fails.append("C1 comment lines with more than one sentence: %s" % [m[:60] for m in multi[:3]])
    if not cen: fails.append("C1 the warning is not in the code cell (en + de)")
    if len(cargo) != 1: fails.append("C1 cargo on %d lines, want 1" % len(cargo))
    if len(cl) > 30: fails.append("C1 the cell has %d lines, want ≤ 30 (the first page)" % len(cl))

# ---------------------------------------------------------------- kernel
def runs(src, n, env=None):
    """Run the cell n× in ONE kernel; per run the ordered messages + widget models."""
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(src, encoding="utf-8"))
    code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    e = {k: v for k, v in os.environ.items() if k not in ("PYCHARM_HOSTED", "DIGICHEM_STATIC_HTML", "DIGICHEM_LANG", "VSCODE_PID")}
    e.update(env or {})
    km, kc = start_new_kernel(kernel_name="python3", env=e, cwd=os.path.dirname(os.path.abspath(src)))
    out = []
    try:
        for _ in range(n):
            mid = kc.execute(code)
            msgs, models, errs = [], {}, []
            while True:
                m = kc.get_iopub_msg(timeout=600)
                if m["parent_header"].get("msg_id") != mid:
                    # a comm message of a widget of this run comes with the run's parent too
                    continue
                t, c = m["msg_type"], m["content"]
                if t == "comm_open":
                    models[c["comm_id"]] = dict((c.get("data") or {}).get("state") or {})
                elif t == "comm_msg" and (c.get("data") or {}).get("method") == "update":
                    models.setdefault(c["comm_id"], {}).update(c["data"].get("state") or {})
                elif t in ("display_data", "execute_result", "update_display_data"):
                    msgs.append((t, c["data"], (c.get("transient") or {}).get("display_id")))
                elif t == "clear_output":
                    msgs.append((t, {"wait": c.get("wait")}, None))
                elif t == "stream":
                    msgs.append((t, {"text/plain": c["text"]}, None))
                elif t == "error":
                    errs.append(c["ename"] + ": " + c["evalue"])
                elif t == "status" and c["execution_state"] == "idle":
                    break
            out.append({"msgs": msgs, "models": models, "errs": errs})
    finally:
        km.shutdown_kernel(now=True)
    return nb, out

def is_reading(d):
    h = (d or {}).get("text/html") or ""
    return isinstance(h, str) and h.lstrip().startswith("<div class='nbreading'")

# ---------------------------------------------------------------- W1
def w1b(rs, rows, fails):
    for i, r in enumerate(rs):
        idx = [k for k, (t, d, _) in enumerate(r["msgs"]) if t in ("display_data", "execute_result") and is_reading(d)]
        after = [t for t, d, _ in r["msgs"][idx[0] + 1:]] if idx else []
        touch = [t for t in after if t in ("update_display_data", "clear_output")]
        allt = [t for t, d, _ in r["msgs"] if t in ("update_display_data", "clear_output")]
        rows.append("W1b run %d: %d outputs, reading version at %s, changes in the cell %d (after the window %d) %s"
                    % (i + 1, sum(1 for t, *_ in r["msgs"] if t != "update_display_data"), idx, len(allt), len(touch), r["errs"][:1]))
        if r["errs"]: fails.append("W1b run %d raised %s" % (i + 1, r["errs"][:1]))
        if len(idx) != 1: fails.append("W1b run %d: %d reading versions, want 1" % (i + 1, len(idx)))
        if touch: fails.append("W1b run %d: %d output changes after the window (%s)" % (i + 1, len(touch), sorted(set(touch))))

HOST = """<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:#2b2d30;color:#dfe1e5'>
<div class='pyc-cell'><pre class='pyc-src'>[cell]</pre><div id='area'></div></div><div style='height:2400px'></div>
<script>
var A = document.getElementById('area'), pend = false;
function frame(doc){ var f = document.createElement('iframe'); f.className = 'out';
  f.style.cssText = 'display:block;width:100%;border:0;height:40px'; f.srcdoc = doc; return f; }
window.pyc = {
  clear: function(){ A.innerHTML = ''; A.style.display = ''; },
  add: function(id, doc){ if (pend) { A.innerHTML = ''; pend = false; } var f = frame(doc); if (id) f.setAttribute('data-did', id); A.appendChild(f); },
  upd: function(id, doc){ [].forEach.call(A.querySelectorAll('iframe[data-did="' + id + '"]'), function(o){ var f = frame(doc);
      f.setAttribute('data-did', id); o.replaceWith(f); }); },
  clearOut: function(wait){ if (wait) pend = true; else A.innerHTML = ''; },
  meta: function(collapsed){ A.style.display = collapsed ? 'none' : ''; }
};
function fit(){ document.querySelectorAll('iframe.out').forEach(function(f){ try { var d = f.contentDocument;
  if (d && d.documentElement) f.style.height = Math.max(1, d.documentElement.scrollHeight) + 'px'; } catch (e) {} }); }
setInterval(fit, 150);
</script>"""

COUNT = r"""() => {
  var vis = function(e, w){ var b = e.getBoundingClientRect(), s = w.getComputedStyle(e);
    if (!(b.width > 0 && b.height > 0) || s.visibility === 'hidden') return false;
    for (var x = e; x; x = x.parentElement) if (w.getComputedStyle(x).display === 'none') return false;
    var fe = w.frameElement; if (fe) { var fb = fe.getBoundingClientRect(); if (!(fb.width > 0 && fb.height > 1)) return false;
      for (var y = fe; y; y = y.parentElement) if (getComputedStyle(y).display === 'none') return false; }
    return true; };
  var fr = [].slice.call(document.querySelectorAll('iframe.out')), wins = 0, firstVis = -1, winAt = -1, h = 0;
  fr.forEach(function(f, i){ var d = f.contentDocument, w = f.contentWindow; if (!d || !d.body) return;
    var any = [].some.call(d.body.querySelectorAll('*'), function(e){ return e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE'
      && (e.childNodes.length && [].some.call(e.childNodes, function(n){ return n.nodeType === 3 && n.textContent.trim(); })) && vis(e, w); });
    if (any && firstVis < 0) firstVis = i;
    [].forEach.call(d.querySelectorAll('.nbrw'), function(x){ if (vis(x, w)) { wins++; if (winAt < 0) winAt = i;
      h = Math.max(h, Math.round(x.getBoundingClientRect().height)); } }); });
  return {frames: fr.length, wins: wins, firstVis: firstVis, winAt: winAt, h: h}; }"""

def w1c(nb, rs, b, base, tmpd, rows, fails, shots):
    from env_iframe import frame_doc
    meta = max(nb["cells"], key=lambda c: len("".join(c["source"]))).get("metadata", {})
    coll = bool(meta.get("collapsed")) or bool((meta.get("jupyter") or {}).get("outputs_hidden"))
    open(os.path.join(tmpd, "pyc.html"), "w", encoding="utf-8").write(HOST)
    ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark")
    pg = ctx.new_page(); pg.goto(base + "pyc.html"); pg.wait_for_timeout(300)
    for i, r in enumerate(rs):
        pg.evaluate("() => pyc.clear()")
        for t, d, did in r["msgs"]:
            doc = "<!doctype html><meta charset=utf-8><body style='margin:0'>" + (frame_doc(d) if t != "clear_output" else "")
            if t in ("display_data", "execute_result", "stream"):
                pg.evaluate("([i, d]) => pyc.add(i, d)", [did, doc])
            elif t == "update_display_data":
                pg.evaluate("([i, d]) => pyc.upd(i, d)", [did, doc])
            elif t == "clear_output":
                pg.evaluate("w => pyc.clearOut(w)", bool(d.get("wait")))
            pg.wait_for_timeout(15)
        pg.evaluate("c => pyc.meta(c)", coll)
        pg.wait_for_timeout(5000)
        c = pg.evaluate(COUNT)
        rows.append("W1c run %d (PyCharm-like, page per output): frames %d · visible windows %d (%d px) · window in output %d · first visible output %d"
                    % (i + 1, c["frames"], c["wins"], c["h"], c["winAt"], c["firstVis"]))
        if c["wins"] != 1 or c["h"] < 300: fails.append("W1c run %d: %d visible reading windows (%d px), want 1 (≥ 300 px)" % (i + 1, c["wins"], c["h"]))
        elif c["firstVis"] != c["winAt"]: fails.append("W1c run %d: output %d is visible above the window (%d)" % (i + 1, c["firstVis"], c["winAt"]))
        if shots and i == len(rs) - 1:
            pg.screenshot(path=os.path.join(shots, "E31-W1-lauf5-pycharm-nachbau.png"))
    ctx.close()

def w1d(nb, rs, b, base, tmpd, rows, fails, strict):
    """All outputs of the cell in ONE page, widgets drawn (models) — JS step-back."""
    from env_iframe import frame_doc
    out_rows = []
    open(os.path.join(tmpd, "pyc1.html"), "w", encoding="utf-8").write(HOST)
    ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark")
    pg = ctx.new_page(); pg.goto(base + "pyc1.html"); pg.wait_for_timeout(300)
    bad = 0
    for i, r in enumerate(rs):
        outs = []
        for t, d, did in r["msgs"]:
            if t in ("display_data", "execute_result"): outs.append([did, d])
            elif t == "update_display_data":
                for o in outs:
                    if did and o[0] == did: o[1] = d
        body = "".join("<div class='pyc-out'>%s</div>" % frame_doc(d, r["models"]) for _, d in outs)
        pg.evaluate("() => pyc.clear()")
        pg.evaluate("([i, d]) => pyc.add(i, d)", [None, "<!doctype html><meta charset=utf-8><body style='margin:0'>" + body])
        pg.wait_for_timeout(5000)
        c = pg.evaluate(COUNT)
        rows.append("W1d run %d (JS; one page, widgets drawn): visible windows %d (%d px)" % (i + 1, c["wins"], c["h"]))
        if c["wins"] != 1: bad += 1
    if bad and strict: fails.append("W1d %d of %d runs without exactly one visible window (JS: 20-reader back())" % (bad, len(rs)))
    ctx.close()

# ---------------------------------------------------------------- F1
F_SEL = "svg.imath,svg.dmath,svg.nbr-imath,svg.nbr-dmath,img.nbmath,img.nbr-nbmath"
F_STATIC_RE = re.compile(r"<(svg|img)\b[^>]*class=\"(?:nbr-)?(imath|dmath|nbmath)\"[^>]*>")

def f1_static(rs, rows, fails):
    tags, px = 0, []
    for t, d, _ in rs[0]["msgs"]:
        h = (d or {}).get("text/html") or ""
        for m in F_STATIC_RE.finditer(h if isinstance(h, str) else ""):
            tags += 1
            st = re.search(r"style=\"([^\"]*)\"", m.group(0))
            st = st.group(1) if st else ""
            if re.search(r"(height|width|margin)[^;]*\d(\.\d+)?px", st): px.append(st[:70])
    for mid, m in rs[0]["models"].items():
        v = m.get("value")
        if isinstance(v, str):
            for mm in F_STATIC_RE.finditer(v):
                tags += 1
                st = re.search(r"style=\"([^\"]*)\"", mm.group(0))
                st = st.group(1) if st else ""
                if re.search(r"(height|width|margin)[^;]*\d(\.\d+)?px", st): px.append(st[:70])
    rows.append("F1 formula tags in the run (outputs + widgets): %d, with px sizes %d %s" % (tags, len(px), sorted(set(px))[:3]))
    if not tags: fails.append("F1 BAD no formula tag found in the run")
    if px: fails.append("F1 %d formula tags sized in px: %s" % (len(px), sorted(set(px))[:3]))

F_MEASURE = """(sel) => { var w = document.querySelector('.nbrw'); var o = [];
  // gated / folded content: shown for the measurement (the ratio is what counts, not the layout)
  w.querySelectorAll(sel).forEach(function (e) { for (var x = e; x && x !== w; x = x.parentElement) {
    if (x.tagName === 'DETAILS') x.open = true; if (x.hasAttribute('hidden')) x.removeAttribute('hidden');
    if (getComputedStyle(x).display === 'none') x.style.setProperty('display', 'block', 'important'); } });
  w.querySelectorAll(sel).forEach(function (e) { if (!e.getClientRects().length) return;
    o.push(Math.round(e.getBoundingClientRect().height * 100) / 100); });
  var p = w.querySelector('.nbreading p'); return {h: o, base: p ? parseFloat(getComputedStyle(p).fontSize) : 0}; }"""

def f1_window(rs, b, base, tmpd, rows, fails, shots):
    from env_iframe import host_page
    from env_reader import FR, PLAY
    outs = []
    for t, d, did in rs[0]["msgs"]:
        if t in ("display_data", "execute_result"): outs.append({"data": d, "id": did, "raw": d})
        elif t == "update_display_data":
            for o in outs:
                if did and o["id"] == did: o["data"] = d
    open(os.path.join(tmpd, "f1.html"), "w", encoding="utf-8").write(host_page(outs, False))
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    pg = ctx.new_page(); pg.goto(base + "f1.html"); pg.wait_for_timeout(3000)
    fi = pg.evaluate(FR)
    if fi < 0: fails.append("F1 BAD no reading frame"); ctx.close(); return
    fr = [f for f in pg.frames if f != pg.main_frame][fi]
    fr.evaluate(PLAY); pg.wait_for_timeout(400)
    fr.evaluate("() => document.querySelectorAll('.nbrw details').forEach(function (d) { d.open = true; })")
    res = {}
    for v in (100, 90, 150):
        fr.evaluate("v => window.__nbReader.fs(v)", v); pg.wait_for_timeout(500)
        res[v] = fr.evaluate(F_MEASURE, F_SEL)
    n = len(res[100]["h"])
    bad = []
    for v in (90, 150):
        want = v / 100.0
        if len(res[v]["h"]) != n: bad.append("count %d at %d %% vs %d" % (len(res[v]["h"]), v, n)); continue
        for k, (a, c) in enumerate(zip(res[v]["h"], res[100]["h"])):
            if c and abs(a / c - want) > 0.03 * want: bad.append("formula %d: %.1f→%.1f px at %d %% (×%.2f)" % (k, c, a, v, a / c))
    tr = (res[150]["base"] / res[100]["base"]) if res[100]["base"] else 0
    rows.append("F1 window: %d visible formulas · text 100 %% %.1f px, ×%.2f at 150 %% · off %d %s"
                % (n, res[100]["base"], tr, len(bad), bad[:3]))
    if n < 3: fails.append("F1 only %d formulas visible in the window (folds open), want ≥ 3" % n)
    if bad: fails.append("F1 %d formulas do not scale with the text: %s" % (len(bad), bad[:4]))
    if shots: pg.screenshot(path=os.path.join(shots, "E31-F1-fenster-150.png"))
    fr.evaluate("() => window.__nbReader.fs(100)")
    ctx.close()

def main():
    import nbpick
    args = sys.argv[1:]
    src = nbpick.from_argv(sys.argv)
    only = ("C1", "F1", "W1")
    if "--only" in args: only = tuple(args[args.index("--only") + 1].split(","))
    shots = args[args.index("--shots") + 1] if "--shots" in args else None
    strict_js = "--js" in args
    nb = json.load(open(src, encoding="utf-8"))
    rows, fails = ["notebook %s" % os.path.basename(src)], []
    if "C1" in only: c1(nb, rows, fails)
    if "W1" in only:
        meta = max(nb["cells"], key=lambda c: len("".join(c["source"]))).get("metadata", {})
        oh = (meta.get("jupyter") or {}).get("outputs_hidden")
        rows.append("W1a code cell metadata: collapsed %r · jupyter.outputs_hidden %r" % (meta.get("collapsed"), oh))
        if meta.get("collapsed") is not False or oh is not False:
            fails.append("W1a the cell's output is marked collapsed/hidden or left to the front end (collapsed %r, outputs_hidden %r), want False/False"
                         % (meta.get("collapsed"), oh))
    if not ({"F1", "W1"} & set(only)):
        return finish(rows, fails)
    nb, rs = runs(src, 5 if "W1" in only else 1)
    if "W1" in only: w1b(rs, rows, fails)
    from env_reader import serve
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    tmpd = tempfile.mkdtemp(prefix="pye31_"); srv = serve(tmpd)
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            try:
                if "F1" in only:
                    f1_static(rs, rows, fails)
                    f1_window(rs, b, base, tmpd, rows, fails, shots)
                if "W1" in only:
                    w1c(nb, rs, b, base, tmpd, rows, fails, shots)
                    w1d(nb, rs, b, base, tmpd, rows, fails, strict_js)
            except Exception as e:
                fails.append("BAD %s" % str(e)[:300])
            b.close()
    finally:
        srv.shutdown(); shutil.rmtree(tmpd, ignore_errors=True)
    finish(rows, fails)

def finish(rows, fails):
    print("\n".join(rows))
    print("REGRESS-PY-E31 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
