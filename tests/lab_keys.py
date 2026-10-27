"""Real-JupyterLab key measurement harness (Playwright, Chromium). 2026-09-25h.

NOT a suite: it needs a running `jupyter lab` (token off) and measures what a
key does in a context — the table in APPLIKATION.md comes from lab_table.py,
which uses this. Contexts: command mode on the document cell · an answer/code
field (the `your own cell` textarea) · a code cell of the reader's own in edit
mode · the panel (keyboard mode). Each setter returns "ok" only if the context
really holds — a row whose precondition failed is not a measurement.

    jupyter lab --no-browser --port=8899 --ServerApp.token='' \
        --ServerApp.password='' --ServerApp.disable_check_xsrf=True --ServerApp.root_dir=<LAB>
    python3 tests/lab_table.py <notebook> <out.json> [keys] [contexts]

Environment: DIGICHEM_LAB_URL (http://127.0.0.1:8899), DIGICHEM_LAB_ROOT,
DIGICHEM_CHROME. Every notebook is copied under a fresh name and every kernel
is shut down between opens, so no row inherits another row's damage."""
import os
CHROME = os.environ.get("DIGICHEM_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
import json, time
SNAP_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var nb = P && P.querySelector('.jp-Notebook');
  var cells = nb ? nb.querySelectorAll('.jp-Cell') : [];
  var act = nb ? [].indexOf.call(cells, nb.querySelector('.jp-Cell.jp-mod-active')) : -1;
  var ae = document.activeElement, aed = ae ? (ae.tagName.toLowerCase() + (ae.id ? '#' + ae.id : '') +
      (ae.className && typeof ae.className === 'string' ? '.' + ae.className.trim().split(/\s+/).slice(0,2).join('.') : '')) : null;
  var where = !ae ? 'none' : ae.closest('#nbpanel-root') ? 'panel' : ae.closest('.cm-editor') ? 'editor'
            : (ae.tagName === 'TEXTAREA' || ae.tagName === 'INPUT') ? 'field'
            : ae.closest('.jp-Notebook') ? 'notebook' : ae === document.body ? 'body' : 'other';
  var h = document.getElementById('nbpanel-root');
  var ta = document.querySelector('textarea.__probe'), cm = null;
  var eds = nb ? nb.querySelectorAll('.jp-Cell .cm-content') : [];
  var last = eds.length ? eds[eds.length-1].textContent : null;
  var ls = {}; try { ['digichemjn.theme.v1','digichemjn.skin.v1','digichemjn.guizoom.v1','digichemjn.progress.v1'].forEach(function(k){ ls[k] = /(theme|skin)\.v1$/.test(k) && window.__nbStore ? window.__nbStore.get(k) : localStorage.getItem(k); }); } catch(e) {}   // E25.o: style + light/dark are the notebook's (hw-E25.int: the comment had swallowed the catch)
  // the record's heartbeat `t` moves every second; it is not a change of state
  try { var pr = JSON.parse(ls['digichemjn.progress.v1'] || '{}'); Object.keys(pr).forEach(function(k){ if (pr[k] && typeof pr[k] === 'object') delete pr[k].t; }); ls['digichemjn.progress.v1'] = JSON.stringify(pr); } catch(e) {}
  var vis = function(sel){ var e = document.querySelector(sel); if (!e) return false; var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; };
  var sc = nb ? (nb.querySelector('.jp-WindowedPanel-outer') || nb) : null;
  return {
    cells: cells.length, active: act,
    mode: nb ? (nb.classList.contains('jp-mod-editMode') ? 'edit' : nb.classList.contains('jp-mod-commandMode') ? 'command' : '?') : null,
    focus: where, ae: aed,
    ta: ta ? ta.value : null, lastEditor: last,
    dialog: !!document.querySelector('.jp-Dialog'),
    palette: vis('.jp-ModalCommandPalette .lm-CommandPalette') || vis('#modal-command-palette .lm-CommandPalette'),
    leftbar: vis('#jp-left-stack'), fullscreen: !!document.fullscreenElement,
    simple: !!document.querySelector('.jp-mod-devMode, body[data-mode="single-document"]') || (document.querySelector('#main') || {}).dataset && document.body.getAttribute('data-mode'),
    tabs: document.querySelectorAll('.lm-DockPanel .lm-TabBar-tab').length,
    scroll: sc ? Math.round(sc.scrollTop) : null,
    keyAt: window.__nbKeyAt == null ? null : window.__nbKeyAt,
    here: h ? [].indexOf.call(h.querySelectorAll('.nbmap-node'), h.querySelector('.nbmap-node.here')) : null,
    hostCls: h ? h.className : null, page: h ? (h.classList.contains('open') ? (h.dataset.page || 'open') : '') : null,
    theme: document.body.getAttribute('data-jp-theme-light'), ls: ls,
    menu: vis('.lm-Menu'), find: vis('.jp-DocumentSearch-overlay'),
    dirty: !!document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current.jp-mod-dirty'),
    kbd: h ? h.classList.contains('nbkbd') : null, sel: h ? [].indexOf.call(h.querySelectorAll('.nbmap-node'), h.querySelector('.nbmap-node.nbsel')) : null,
    skin: document.body.getAttribute('data-nbskin') || (h && h.getAttribute('data-skin')) || null,
    gui: window.__nbGui == null ? null : window.__nbGui,
    shortcutsDlg: !!document.querySelector('.jp-ContextualShortcut, .jp-Shortcuts')
  };
}"""

def open_nb(b, base, nb, width=1400, height=900):
    ctx = b.new_context(viewport={"width": width, "height": height})
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: %s" % str(e)[:200]))
    pg.on("console", lambda m: errs.append("console.error: %s" % m.text[:200]) if m.type == "error" else None)
    pg.goto(base + "/lab/tree/" + nb + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=60000)
    pg.wait_for_timeout(1500)
    def run_all():
        # a kernel dialog on a fresh server is answered with its default
        if pg.query_selector(".jp-Dialog"):
            pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
        pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
        pg.keyboard.press("Control+Shift+C")
        # NEVER type into the notebook: if the palette is not there, the text
        # "Run All Cells" is eleven command-mode keys (A inserts a cell, …)
        try:
            pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
        except Exception:
            pg.keyboard.press("Escape"); return False
        # 2026-10-03 (E21 Rest Stufe 2) — FILLED, NOT TYPED. Typed, every key
        # that came after the palette lost the focus went to the notebook in
        # command mode: "A" of "All" put an empty code cell ABOVE the title
        # (measured: 3 of 9 opens on one CPU, cell 0 empty, then "the notebook
        # opened with 3 cells"). `fill` sets the palette's own field or fails.
        try:
            pg.fill(".lm-CommandPalette-input", "Run All Cells", timeout=5000)
        except Exception:
            pg.keyboard.press("Escape"); return False
        # under load the list filters late; Enter on a half-filtered list runs
        # whatever is on top. Wait until the top item IS "Run All Cells".
        try:
            pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === 'Run All Cells'); }", timeout=8000)
        except Exception:
            pg.keyboard.press("Escape"); return False
        pg.keyboard.press("Enter")
        return True
    run_all()
    # under load the palette can swallow the command; ask again rather than fail
    for attempt in range(3):
        try:
            pg.wait_for_selector("#nbpanel-root .nbmap", state="attached", timeout=60000)
            break
        except Exception:
            if attempt == 2: raise
            run_all()
    # a notebook that does not start with its two cells is not a starting point
    n = pg.evaluate("() => document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell').length")
    if n != 2:
        raise RuntimeError("the notebook opened with %d cells" % n)
    # wait for the kernel to go idle
    for _ in range(60):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st == "idle": break
    pg.wait_for_timeout(1500)
    cover_play(pg)                      # E24.3: the cover first, Play → the document
    return ctx, pg, errs

# 2026-10-06 (E24.3, JS) — AFTER A RUN THE COVER COMES FIRST. py-E24.3 made
# the cover the last output of the mega-cell; js-E24.3 lays it over the
# notebook after a run that ran in the page, until Play is pressed (then the
# document, no second run). A script that measures the DOCUMENT therefore
# presses Play after its Run All — what the reader does. Waits a moment for the
# cover (it comes with the pass after the run), presses it if it is there.
# Returns "play" (pressed), "none" (no cover came: a build before E24.3, or a
# panel where Play was pressed already) or "BAD …" (a cover that did not go).
COVER_UP = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var c = P && P.querySelector('.nbcover-out[data-nbcov]'), p = c && c.querySelector('.nbcover-play');
  return !!(p && p.getBoundingClientRect().width > 2); }"""
def cover_play(pg, wait_ms=3000):
    t = 0
    while t < wait_ms and not pg.evaluate(COVER_UP):
        pg.wait_for_timeout(250); t += 250
    if not pg.evaluate(COVER_UP): return "none"
    # a pointer click at its middle: Play pulses (CSS) and is never "stable" for
    # Playwright's own click
    xy = pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
      var p = P.querySelector('.nbcover-out[data-nbcov] .nbcover-play'); p.scrollIntoView({block: 'center'});
      var r = p.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }""")
    pg.wait_for_timeout(200)
    pg.mouse.click(*xy)
    for _ in range(40):
        pg.wait_for_timeout(250)
        if not pg.evaluate(COVER_UP) and not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"):
            break
    pg.wait_for_timeout(1200)
    return "play" if not pg.evaluate(COVER_UP) else "BAD the cover stayed after Play"

def snap(pg): return pg.evaluate(SNAP_JS)

def diff(a, b):
    out = {}
    for k in b:
        if a.get(k) != b.get(k):
            if k == "ls":
                d = {kk: (a[k].get(kk), b[k].get(kk)) for kk in b[k] if a[k].get(kk) != b[k].get(kk)}
                if d: out[k] = {kk: ("changed" if kk.endswith("progress.v1") else v) for kk, v in d.items()}
            else:
                out[k] = (a.get(k), b.get(k))
    return out

def to_command(pg):
    pg.evaluate("() => { var a = document.activeElement; if (a && a.blur) a.blur(); }")
    # the document cell (index 1) — focusing it makes it the active cell; the
    # title cell (index 0) is hidden once the notebook has run, and with a
    # hidden active cell JupyterLab's command-mode keys go nowhere
    pg.evaluate("() => { var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook'); var c = n.querySelectorAll('.jp-Cell')[1]; (c || n).focus(); }")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
    s = snap(pg)
    ok = s["mode"] == "command" and s["focus"] == "notebook" and s["active"] == 1 and s["ae"].startswith("div.lm-Widget.jp-Cell")
    return "ok" if ok else "BAD %s/%s/%s/active=%s" % (s["mode"], s["focus"], s["ae"], s["active"])

def to_textarea(pg):
    ok = pg.evaluate("""() => {
      var t = document.querySelector('textarea.__probe');
      if (!t) {
        var all = [].slice.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) textarea'));
        t = all.filter(function(x){ return (x.closest('.widget-textarea') || x.classList.contains('codearea') || x.closest('.codearea')); }).pop() || all.pop();
        if (!t) return 'no textarea';
        t.classList.add('__probe');
      }
      // open every collapsed ancestor, outermost first
      var chain = [], e = t;
      while (e) { if (e.classList && e.classList.contains('jupyter-widget-Collapse-contents') && e.classList.contains('lm-mod-hidden')) chain.push(e); e = e.parentElement; }
      chain.reverse().forEach(function(c){ var hd = c.parentElement.querySelector(':scope > .jupyter-widget-Collapse-header'); if (hd) hd.click(); });
      t.scrollIntoView({block: 'center'});
      return 'ok';
    }""")
    pg.wait_for_timeout(400)
    pg.evaluate("() => { var t = document.querySelector('textarea.__probe'); t.focus(); t.value = 'x = 1'; t.dispatchEvent(new Event('input', {bubbles:true})); t.setSelectionRange(5,5); }")
    pg.wait_for_timeout(150)
    s = snap(pg)
    h = pg.evaluate("() => Math.round(document.querySelector('textarea.__probe').getBoundingClientRect().height)")
    return "ok" if (ok == "ok" and s["focus"] == "field" and h > 0) else "BAD %s/%s/h=%s" % (ok, s["focus"], h)

def reset_panel(pg):
    pg.evaluate("() => { var h=document.getElementById('nbpanel-root'); if (h && h.classList.contains('open')) { h.classList.remove('open'); } }")

def press(pg, key, wait=450):
    a = snap(pg)
    pg.keyboard.press(key); pg.wait_for_timeout(wait)
    b = snap(pg)
    return a, b, diff(a, b)

import shutil, os, urllib.request, itertools
_N = itertools.count()
def kill_sessions(base):
    try:
        ss = json.loads(urllib.request.urlopen(base + "/api/sessions").read())
        for x in ss:
            req = urllib.request.Request(base + "/api/sessions/" + x["id"], method="DELETE"); urllib.request.urlopen(req)
    except Exception as e:
        print("kill_sessions:", e)

def fresh(b, base, src, labroot, ctx=None, keep_progress=False):
    """A new copy of the notebook under a new name, opened and run. Old page and
    kernels go — and, since 25h, the progress the kernel keeps in ~/.digichemjn,
    or every copy would start where the last one stopped."""
    if ctx is not None:
        try: ctx.close()
        except Exception: pass
    kill_sessions(base)
    if not keep_progress:
        import glob
        # the KERNEL's home, which is the server's: DIGICHEM_KERNEL_HOME when the
        # server was started with its own (one per parallel measurement)
        kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
        # 2026-10-03 (E21 Rest Stufe 2, JS) — AND THE STORED MODE. Since E16.10/
        # E21.6 the kernel builds the mode kept in ~/.digichemjn/<id>.mode (or
        # beside the notebook, <root>/.digichemjn/<id>.mode). The gate's last
        # row (PY-R6i) leaves "calc" there for its notebook, and the scripts of
        # stage 2 then opened Modeling with no coding exercise: lab_flow
        # ("'NoneType' object is not subscriptable") and lab_skip red in the
        # gate, green alone (gate 03.10. 17:4x and 19:1x; the file was there).
        # A fresh copy starts in the notebook's default mode.
        for f in (glob.glob(os.path.join(kh, ".digichemjn", "*.progress"))
                  + glob.glob(os.path.join(kh, ".digichemjn", "*.mode"))
                  + glob.glob(os.path.join(labroot, ".digichemjn", "*.mode"))
                  # E17.5 — and the language (a profile value, one file for all)
                  + glob.glob(os.path.join(kh, ".digichemjn", "lang"))
                  + glob.glob(os.path.join(labroot, ".digichemjn", "lang"))):
            try: os.remove(f)
            except Exception: pass
    name = "probe_%03d_%s" % (next(_N), os.path.basename(src))
    shutil.copy(src, os.path.join(labroot, name))
    return open_nb(b, base, name)

def to_editor(pg):
    """A cell of the reader's own below the document, in edit mode, with 'x = 1' typed."""
    s = snap(pg)
    if s["cells"] == 2:
        # E10 Schritt C (01.10.): an own cell comes from the "Your own cell" mark
        # (E11.1/E12.4, a click makes one on the reading line, editor focused).
        # Until v1.45 this setter pressed B in command mode — held back since
        # (D) in our notebook (13-rail-keys CELL_KEEP), so every "editor" row
        # of lab_table was a failed precondition ("BAD edit/notebook").
        to_command(pg)
        pg.evaluate("() => { var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook'); var sc = n.querySelector('.jp-WindowedPanel-outer') || n; sc.scrollTop = sc.scrollHeight; }")
        pg.wait_for_timeout(1200)
        xy = pg.evaluate("() => { var m = document.querySelector('#nbpanel-root .nbmap-node.cell .nbsect') || document.querySelector('#nbpanel-root .nbmap-node.cell'); if (!m) return null; var r = m.getBoundingClientRect(); return r.width > 0 ? [r.left + r.width / 2, r.top + r.height / 2] : null; }")
        if xy:
            pg.mouse.click(xy[0], xy[1]); pg.wait_for_timeout(1800)
        s = snap(pg)
        if s["mode"] == "edit" and s["focus"] == "editor":
            pg.keyboard.press("Control+a"); pg.keyboard.type("x = 1"); pg.wait_for_timeout(150)
            s = snap(pg)
            return "ok" if (s["mode"] == "edit" and s["focus"] == "editor") else "BAD %s/%s" % (s["mode"], s["focus"])
    # the reader's own cell is the LAST one; focus it, then edit mode
    pg.evaluate("() => { var a = document.activeElement; if (a && a.blur) a.blur(); var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook'); var cs = n.querySelectorAll('.jp-Cell'); cs[cs.length-1].focus(); }")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(120)
    pg.keyboard.press("Enter"); pg.wait_for_timeout(250)
    pg.keyboard.press("Control+a"); pg.keyboard.type("x = 1"); pg.wait_for_timeout(150)
    s = snap(pg)
    return "ok" if (s["mode"] == "edit" and s["focus"] == "editor") else "BAD %s/%s" % (s["mode"], s["focus"])


def to_panel(pg):
    r = to_command(pg)
    pg.keyboard.press("Alt+Period"); pg.wait_for_timeout(200)
    s = snap(pg)
    return "ok" if s["focus"] == "panel" and s["kbd"] else "BAD %s/kbd=%s (%s)" % (s["focus"], s["kbd"], r)


# ---- a notebook WITH progress -------------------------------------------------
# 2026-09-25h — a fuzz that starts from an empty record cannot see a key that
# wipes the record: it is green because there is nothing to lose. So both fuzz
# suites start from one solved exercise — the first coding exercise, solved with
# its own solution, read from the notebook's source.
import ast as _ast
def first_code_solution(src):
    mega = max(json.load(open(src, encoding="utf-8"))["cells"], key=lambda c: len("".join(c["source"])))
    msrc = "\n".join(l for l in __import__("megasrc").expand("".join(mega["source"])).splitlines() if not l.strip().startswith("%pip"))
    for node in _ast.walk(_ast.parse(msrc)):
        if isinstance(node, _ast.Call) and getattr(node.func, "id", "") == "code_fold":
            kw = {k.arg: k.value for k in node.keywords}
            if "task" in kw and "solution" in kw and "locked_by" not in kw:
                try:
                    return _ast.literal_eval(kw["task"]), _ast.literal_eval(kw["solution"])
                except Exception:
                    pass
    return None, None

_BOX_JS = r"""(task) => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var h = document.getElementById('nbpanel-root');
  var n = h && h.querySelector('.nbmap-node.codetask[data-task="' + task + '"]');
  var sp = n && document.getElementById(n.getAttribute('data-target'));
  if (!sp) return false;
  var ta = null, ts = P.querySelectorAll('textarea.widget-input');
  for (var i = 0; i < ts.length; i++) if (sp.compareDocumentPosition(ts[i]) & 4) { ta = ts[i]; break; }
  if (!ta) return false;
  var chain = [], e = ta;
  while (e) { if (e.classList && e.classList.contains('jupyter-widget-Collapse-contents') && e.classList.contains('lm-mod-hidden')) chain.push(e); e = e.parentElement; }
  chain.reverse().forEach(function(c){ var hd = c.parentElement.querySelector(':scope > .jupyter-widget-Collapse-header'); if (hd) hd.click(); });
  var b = null, up = ta.parentElement, k = 0;
  while (up && k < 12 && !b) { b = up.querySelector('button.sc-btn'); up = up.parentElement; k++; }
  document.querySelectorAll('[data-fz]').forEach(function(x){ x.removeAttribute('data-fz'); });
  ta.setAttribute('data-fz', 'ta'); if (b) b.setAttribute('data-fz', 'btn');
  return !!b;
}"""

def solve_first(pg, src):
    task, sol = first_code_solution(src)
    if not task: return None
    if not pg.evaluate(_BOX_JS, task): return None
    pg.wait_for_timeout(600)
    pg.evaluate("(c) => { var t = document.querySelector('[data-fz=ta]'); t.focus(); t.value = c;"
                " t.dispatchEvent(new Event('input', {bubbles: true})); t.blur(); }", sol)
    pg.wait_for_timeout(400)
    pg.evaluate("() => { var b = document.querySelector('button[data-fz=btn]'); if (b) b.click(); }")
    for _ in range(60):
        pg.wait_for_timeout(500)
        st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st == "idle": break
    pg.wait_for_timeout(1500)
    rec = pg.evaluate("() => localStorage.getItem('digichemjn.progress.v1') || ''")
    return task if '"c":[1,' in rec else None


# ---- panel = source = document, after every run ------------------------------
# 2026-09-28 (Nacht, D-Rest) — two invariants the fuzz did not have. 27a found
# that in about one run of three the panel kept 43 marks from a half-rendered
# mirror while the source had 46, skipped the class sync, and showed chapter 2
# padlocked for good while the document and the kernel had it open. No suite
# covered it. After every run (Run All on open, a key that runs the notebook,
# a hostile payload, Restart + Run All) the suites now ask:
#   7  panel mark count = source mark count  (.nbmap-node / .nbcodemark)
#   8  panel chapter locks = document chapter locks  (the `data-lock` of every
#      `.nbmap-node.chap.locked` on the panel = the `nblocked-<key>` of every
#      lock notice in the document outside the feeds) — and = the source's
# "Source" is the feed the panel itself reads (`srcIn` in the panel script):
# the first connected `.nbfeed[data-final]` with a rail, else the first with a
# rail. The panel syncs itself for seconds after the kernel goes idle, so a
# difference only counts if it is still there after `wait` seconds.
CONSIST_JS = r"""() => {
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var h = document.getElementById('nbpanel-root');
  if (!P || !h || !h.querySelector('.nbrail')) return {ok: null, why: 'no panel'};
  var feeds = [].slice.call(P.querySelectorAll('.nbfeed')).filter(function(f){
      return f.isConnected && f.querySelector('.nbrail'); });
  var src = feeds.filter(function(f){ return f.hasAttribute('data-final'); })[0] || feeds[0] || null;
  var marks = function(r){ return r.querySelectorAll('.nbmap-node').length + '/' +
                                  r.querySelectorAll('.nbcodemark').length; };
  var chapLocks = function(r){ return [].map.call(r.querySelectorAll('.nbmap-node.chap.locked'),
      function(n){ return n.getAttribute('data-lock') || '?'; }).sort().join(','); };
  var doc = [].slice.call(P.querySelectorAll('.nblocked-note')).filter(function(n){
      return !n.closest('.nbfeed') && !n.classList.contains('nbexlock'); }).map(function(n){
      return (String(n.className).match(/\bnblocked-(?!note\b)([\w-]+)/) || ['', '?'])[1]; }).sort();
  // a notice can be rendered twice while a chapter re-renders; the SET counts
  doc = doc.filter(function(k, i){ return doc.indexOf(k) === i; }).join(',');
  var out = {panelMarks: marks(h), srcMarks: src ? marks(src) : null,
             panelLocks: chapLocks(h), srcLocks: src ? chapLocks(src) : null, docLocks: doc};
  out.ok = !!src && out.panelMarks === out.srcMarks &&
           out.panelLocks === out.docLocks && out.panelLocks === out.srcLocks;
  return out;
}"""

def consistency(pg, wait=20):
    """[] when panel, source and document agree (within `wait` s), else the
    violations with the numbers that differ."""
    c = None
    for _ in range(int(wait * 2) + 1):
        c = pg.evaluate(CONSIST_JS)
        if c.get("ok") is not False: break
        pg.wait_for_timeout(500)
    if c.get("ok") is None: return []            # no panel: invariant 2 speaks for that
    v = []
    if c["srcMarks"] is None: v.append("panel has no source feed")
    elif c["panelMarks"] != c["srcMarks"]:
        v.append("panel marks %s != source marks %s" % (c["panelMarks"], c["srcMarks"]))
    if c["panelLocks"] != c["docLocks"]:
        v.append("panel locks [%s] != document locks [%s]" % (c["panelLocks"], c["docLocks"]))
    if c["srcLocks"] is not None and c["panelLocks"] != c["srcLocks"]:
        v.append("panel locks [%s] != source locks [%s]" % (c["panelLocks"], c["srcLocks"]))
    return v


# ---- a server of its own, so the fuzz runs as a suite -------------------------
# 2026-09-28 (Nacht) — until now both fuzz scripts needed a `jupyter lab`
# started by hand, which is why they were "not one of the seven". If nothing
# answers at DIGICHEM_LAB_URL, `ensure_lab()` starts one on a free port with a
# throw-away root and a throw-away HOME (so the kernel's ~/.digichemjn is its
# own), points DIGICHEM_LAB_URL/ROOT/KERNEL_HOME at it, and stops it at exit.
def ensure_lab(base):
    import socket, subprocess, tempfile, atexit, urllib.request, sys as _sys
    try:
        urllib.request.urlopen(base + "/api/status", timeout=3).read()
        return base, os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab")
    except Exception:
        pass
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    tmp = tempfile.mkdtemp(prefix="digichem-lab-")
    root, home = os.path.join(tmp, "root"), os.path.join(tmp, "home")
    os.makedirs(root); os.makedirs(home)
    env = dict(os.environ, HOME=home)
    log = open(os.path.join(tmp, "lab.log"), "w")
    proc = subprocess.Popen([_sys.executable, "-m", "jupyterlab", "--no-browser", "--port=%d" % port,
                             "--ServerApp.token=", "--ServerApp.password=",
                             "--ServerApp.disable_check_xsrf=True", "--ServerApp.root_dir=" + root,
                             "--allow-root"], env=env, stdout=log, stderr=subprocess.STDOUT)
    atexit.register(lambda: (proc.terminate(), proc.wait(20)))
    base = "http://127.0.0.1:%d" % port
    for _ in range(120):
        try:
            urllib.request.urlopen(base + "/api/status", timeout=2).read(); break
        except Exception:
            time.sleep(0.5)
    else:
        raise RuntimeError("jupyter lab did not come up (%s)" % os.path.join(tmp, "lab.log"))
    os.environ.update(DIGICHEM_LAB_URL=base, DIGICHEM_LAB_ROOT=root, DIGICHEM_KERNEL_HOME=home)
    print("(own jupyter lab at %s, root %s)" % (base, root)); _sys.stdout.flush()
    return base, root


def restart_run_all(pg):
    """Kernel ▸ Restart Kernel and Run All Cells… through the palette, dialog
    accepted — what a reader does. Returns the dialog's title (the proof that
    it WAS a restart) or None."""
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C")
    try:
        pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
        pg.fill(".lm-CommandPalette-input", "Restart Kernel and Run All", timeout=5000)   # filled, not typed (open_nb)
        pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && /^Restart Kernel and Run All Cells/.test(a.textContent.trim())); }", timeout=8000)
    except Exception:
        pg.keyboard.press("Escape"); return None
    pg.keyboard.press("Enter")
    try:
        pg.wait_for_selector(".jp-Dialog", timeout=8000)
    except Exception:
        return None
    title = pg.evaluate("() => (document.querySelector('.jp-Dialog-header')||{}).textContent || ''").strip()
    pg.keyboard.press("Enter")
    return title or "?"
