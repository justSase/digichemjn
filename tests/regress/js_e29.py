"""E29 (2026-10-12, Werkstatt JS) — the reader's list of 12.10. (Vorlage v1.75), the JavaScript points.
Stand-alone (a stage-2 script: run.py never imports it), measured in a real JupyterLab under Playwright:

    python3 tests/regress/js_e29.py [<nb.ipynb>] [--only P1,D4] [--shots DIR] [--steps 50]

  P1m  EN|DE: the page applies py-E29's attributes (data-nbl-en/-de = JSON, a stand-in row in the
       live cover): title + data-desc German, the hover box German, back on EN the English ones;
       lang/data-nbcov-lang on the cover root
  P1   after DE on the preview: 0 English words in the visible cover and in the hover box of every
       timeline row (word list below) — needs py-E29 P1 (the texts in both languages)
  P5   no feedback link/tick of the page, no error ring, no mailto rewrite on click
  P6   Ctrl+wheel and Ctrl+plus over the preview: the lens unchanged, the event not prevented
  D2   after a lens change (Ctrl+wheel) 4 wheel notches move the page on: no step back > 2 px,
       ≥ 200 px in all
  D3   a reader's click on a locked chapter's mark: the page stays (±2 px for 1.5 s), nothing
       chosen, a hint with the lock card's words beside the mark
  D4   50 mixed clicks (timeline marks and the chosen chapter's pill in the document, 0.4–1.3 s
       apart): every time the target ±2 px on the reading line (a pill click also folds/unfolds)
  D5   full screen (⛶): marks the same size (±0.5 px) and the same place to their anchors (±1 px)
       as without — measured only (headless: the window does not grow; real screen → Dirigent)
  D7   ⚙ font size (py-E29's cell .nbfontcell, shown and filled here): A+ ×3 → 130 %, --nbfs 1.3 on
       <html>, running text ×1.30 (±0.03; the size rule: css-E29), lens and marks unchanged, kept per
       notebook
  D9   wheel: 4 notches slowly = as before (±5 %), quickly ≥ ×1.4; a touchpad (40 × 10 px) as before
Exit 0 = all red-free (P1 and D5 count; P1 waits for Python — the Hauptwerkstatt reads it after
merging). Gegenprobe v1.75 (`96f71b52`): P1m, P5, P6, D2, D3, D4, D7, D9 red."""
import sys, os, json, time, shutil, random, re, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from lab_keys import ensure_lab, kill_sessions, CHROME
from playwright.sync_api import sync_playwright
import run as R

if __name__ != "__main__":
    raise ImportError("js_e29 is a stand-alone script")
ap = argparse.ArgumentParser()
ap.add_argument("nb", nargs="?")
ap.add_argument("--only", default=None)
ap.add_argument("--shots", default=None)
ap.add_argument("--steps", type=int, default=50)
A = ap.parse_args()
if not A.nb:
    import nbpick
    A.nb = nbpick.resolve("vorlage")
want = lambda k: not A.only or any(k.startswith(x.strip()) for x in A.only.split(","))
ROWS = []
def rec(k, ok, det):
    ROWS.append((k, bool(ok), det)); print("%-4s %s  %s" % (k, "ok " if ok else "RED", det)); sys.stdout.flush()

BASE = ROOT = None
def start(play=True, w=1400, h=900):
    global BASE, ROOT
    if not BASE: BASE, ROOT = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    ctx = b.new_context(viewport={"width": w, "height": h}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    kill_sessions(BASE); R.set_lab_theme(BASE, "light")
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    shutil.rmtree(os.path.join(kh, ".digichemjn"), ignore_errors=True)
    name = "e29_%d_%s" % (int(time.time() * 1000) % 1000000, os.path.basename(A.nb))
    shutil.copy(A.nb, os.path.join(ROOT, name))
    pg.goto(BASE + "/lab/tree/" + name + "?reset")
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(1500)
    if play: R.run_front(pg, R.nb_id(A.nb))
    else:
        R.palette(pg, "Run All Cells")
        pg.wait_for_function("() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); var c = P && P.querySelector('.nbcover-out[data-nbcov] .nbcover-play'); return !!(c && c.getBoundingClientRect().width > 2); }", timeout=90000)
        pg.wait_for_timeout(2500)
    return p, b, pg, errs
def stop(p, b):
    try: b.close()
    finally: p.stop()
def shot(pg, name, **kw):
    if A.shots: os.makedirs(A.shots, exist_ok=True); pg.screenshot(path=os.path.join(A.shots, name), **kw)

SC = "(v) => { var s = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); if (v !== null && v !== undefined) s.scrollTop = v; return s.scrollTop; }"
COV = "document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out[data-nbcov]')"
ZOOM = "() => localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'x') || '100'"

# ------------------------------------------------------------------ the preview: P1m P1 P5 P6
EN_WORDS = set("""the you your what which this that these with and of to for from how use
chapter chapters exercise exercises figure figures coding appendix introduction content contents
sign play runs run every cell cells series placeholder learn able own end guided part route
through title conclusion references licence license solved notebooks browser knows timeline
calculate only figures pen paper both plain report problem practise practice want do here
click add new account password log goes belongs carry working ideas below above""".split())
VIS_TEXT = """() => { var c = %s; var out = [];
  var w = document.createTreeWalker(c, NodeFilter.SHOW_TEXT); var n;
  while ((n = w.nextNode())) { var e = n.parentElement, t = n.textContent.trim(); if (!t) continue;
    var r = e.getBoundingClientRect(), s = getComputedStyle(e); if (!(r.width > 0 && r.height > 0) || s.visibility === 'hidden') continue;
    var hid = false; for (var x = e; x && x !== c; x = x.parentElement) { if (getComputedStyle(x).display === 'none') { hid = true; break; } }
    if (!hid) out.push(t); }
  return out; }""" % COV
ROWS_JS = """() => { var c = %s; return [].map.call(c.querySelectorAll('.nbcover-tl .nbtl-row'), function(r, i){
  var e = r.querySelector('.nbtl-dot,.nbtl-mk,*') || r; var b = r.getBoundingClientRect();
  return {i: i, xy: [b.left + b.width / 2, b.top + Math.min(b.height / 2, 14)], vis: b.width > 0 && b.height > 0}; }); }""" % COV
# Hauptwerkstatt 12.10. (Zusammenführen E29) — behauptete bisher: kein "notebooks", "run", "cells" im deutschen
# Cover. Aber "Notebooks" ist auch deutsch („Titel des Notebooks“), und „Run ▸ Run All Cells“ ist JupyterLabs
# Menüpfad (bleibt englisch, wie py_e29 NAMES): beide sind keine englischen Reste des Covers.
EN_WORDS.difference_update({"notebooks", "browser"})   # „Browser“ ist auch deutsch („in diesem Browser“)
LAB_NAMES = re.compile(r"Run ▸ Run All Cells|Run All(?: Cells)?|JupyterLab|JupyterLite")
def english(ts):
    bad = []
    for t in ts:
        ws = re.findall(r"[A-Za-z]+", LAB_NAMES.sub(" ", t))
        hit = [x for x in ws if x.lower() in EN_WORDS]
        if hit: bad.append("%s [%s]" % (t[:50], ",".join(hit[:3])))
    return bad

def preview():
    p, b, pg, errs = start(play=False)
    try:
        if want("P1m"):
            # a stand-in row in py-E29's format (claude/VERTRAG-E29-py.md): data-nbl-en/-de = JSON {attr: value}
            pg.evaluate("""() => { var c = %s;
              var r = c.querySelector('.nbcover-tl .nbtl-row:not(.nbtl-title):not(.nbtl-group)');
              if (!r) return false; r.classList.add('e29-row');
              var nm = r.getAttribute('title') || r.getAttribute('data-nm') || 'x', ds = r.getAttribute('data-desc') || 'y';
              r.setAttribute('data-nbl-en', JSON.stringify({title: nm, 'data-desc': ds}));
              r.setAttribute('data-nbl-de', JSON.stringify({title: 'E29 Name', 'data-desc': 'E29 deutsche Karte'}));
              return true; }""" % COV)
            pg.wait_for_timeout(2200)
            st = lambda: pg.evaluate("""() => { var c = %s, root = c.closest('.nbtitle') || c, r = c.querySelector('.e29-row');
               return {desc: r ? r.getAttribute('data-desc') : null, nm: r ? (r.getAttribute('title') || r.getAttribute('data-nm')) : null,
                       lang: root.getAttribute('data-nbcov-lang')}; }""" % COV)
            s0 = st()
            pg.evaluate("() => { var b = %s.closest('.nbtitle').querySelector('.nblang-opt[data-lang=de]') || %s.querySelector('.nblang-opt[data-lang=de]'); b.click(); }" % (COV, COV))
            pg.wait_for_timeout(1500); s1 = st()
            xy = pg.evaluate("() => { var r = %s.querySelector('.e29-row'); r.scrollIntoView({block: 'center'}); var b = r.getBoundingClientRect(); return [b.left + b.width / 2, b.top + Math.min(b.height / 2, 12)]; }" % COV)
            pg.mouse.move(*xy); pg.wait_for_timeout(500)
            box = pg.evaluate("() => { var d = %s.querySelector('.nbtl-desc'); return d && !d.hidden ? d.textContent : ''; }" % COV)
            pg.mouse.move(5, 5); pg.wait_for_timeout(300)
            pg.evaluate("() => { var b = %s.closest('.nbtitle').querySelector('.nblang-opt[data-lang=en]') || %s.querySelector('.nblang-opt[data-lang=en]'); b.click(); }" % (COV, COV))
            pg.wait_for_timeout(1500); s2 = st()
            ok = (s0["lang"] == "en" and s1["desc"] == "E29 deutsche Karte" and s1["nm"] == "E29 Name" and "E29 deutsche Karte" in box
                  and s1["lang"] == "de" and s2["desc"] == s0["desc"] and s2["nm"] == s0["nm"] and s2["lang"] == "en")
            rec("P1m", ok, "EN %s → DE %s (hover box %r) → EN %s" % (s0, s1, box[:60], s2))
        if want("P1"):
            pg.evaluate("() => { var b = %s.closest('.nbtitle').querySelector('.nblang-opt[data-lang=de]') || %s.querySelector('.nblang-opt[data-lang=de]'); b.click(); }" % (COV, COV))
            pg.wait_for_timeout(1500)
            vis = [t for t in pg.evaluate(VIS_TEXT) if not t.startswith("E29")]
            bad = english(vis)
            hov = []
            for r in pg.evaluate(ROWS_JS):
                if not r["vis"]: continue
                pg.evaluate("(i) => { var r = %s.querySelectorAll('.nbcover-tl .nbtl-row')[i]; r.scrollIntoView({block: 'center'}); }" % COV, r["i"])
                xy = pg.evaluate("(i) => { var r = %s.querySelectorAll('.nbcover-tl .nbtl-row')[i], b = r.getBoundingClientRect(); return [b.left + b.width / 2, b.top + Math.min(b.height / 2, 12)]; }" % COV, r["i"])
                pg.mouse.move(*xy); pg.wait_for_timeout(120)
                t = pg.evaluate("() => { var d = %s.querySelector('.nbtl-desc'); return d && !d.hidden ? d.textContent.trim() : ''; }" % COV)
                if t: hov.append(t)
            pg.mouse.move(5, 5)
            hb = english(hov)
            shot(pg, "P1_cover_de.png")
            rec("P1", not bad and not hb, "visible: %d texts, %d English %s · hover boxes: %d, %d English %s" % (len(vis), len(bad), bad[:4], len(hov), len(hb), hb[:2]))
            pg.evaluate("() => { var b = %s.closest('.nbtitle').querySelector('.nblang-opt[data-lang=en]') || %s.querySelector('.nblang-opt[data-lang=en]'); b.click(); }" % (COV, COV))
            pg.wait_for_timeout(800)
        if want("P5"):
            pg.wait_for_timeout(1500)
            r = pg.evaluate("""() => ({cover: document.querySelectorAll('.nbfb-cover').length, tick: document.querySelectorAll('.nbfb-tick,.nbfb-err').length,
               mailto: [].filter.call(%s.querySelectorAll('a[href^="mailto:"]'), function(a){ return a.getBoundingClientRect().height > 0; }).length,
               ring: Array.isArray(window.__nbErrs), off: typeof window.__nbFbOff === 'function'})""" % COV)
            rec("P5", not any(r.values()), "page's feedback link on the preview %d, tick %d, visible mailto on the preview %d, error ring %s, click rewrite %s" % (r["cover"], r["tick"], r["mailto"], r["ring"], r["off"]))
        if want("P6"):
            z0 = pg.evaluate(ZOOM)
            pg.evaluate("() => { window.__e29p = []; window.addEventListener('wheel', function(e){ if (e.ctrlKey) window.__e29p.push(e.defaultPrevented); }, false); window.addEventListener('keydown', function(e){ if (e.ctrlKey) window.__e29p.push(e.defaultPrevented); }, false); }")
            xy = pg.evaluate("() => { var r = %s.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }" % COV)
            pg.mouse.move(*xy)
            pg.keyboard.down("Control"); pg.mouse.wheel(0, -100); pg.wait_for_timeout(120); pg.mouse.wheel(0, -100); pg.keyboard.up("Control")
            pg.wait_for_timeout(300)
            pg.evaluate("() => { var e = new KeyboardEvent('keydown', {key: '+', ctrlKey: true, bubbles: true, cancelable: true}); (%s.querySelector('.nbcover-play') || document.body).dispatchEvent(e); }" % COV)
            pg.wait_for_timeout(500)
            z1 = pg.evaluate(ZOOM); pv = pg.evaluate("() => window.__e29p")
            rec("P6", z0 == z1 and pv and not any(pv), "lens %s → %s; prevented: %s (want all False)" % (z0, z1, pv))
    finally:
        stop(p, b)
    return errs

# ------------------------------------------------------------------ the document: D2 D3 D7 D9 D5
FACE = """var rv = function(e){ var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; };
  var face = function(n){ if (rv(n)) return n; var d = n.querySelectorAll('*'); for (var i = 0; i < d.length; i++) if (rv(d[i])) return d[i]; return null; };"""
def document():
    p, b, pg, errs = start(play=True)
    try:
        pg.mouse.move(800, 500)
        if want("D3"):
            pg.evaluate(SC, 0); pg.wait_for_timeout(800)
            j = None
            for _ in range(14):
                j = pg.evaluate("""() => { %s var h = document.getElementById('nbpanel-root');
                  var n = [].filter.call(h.querySelectorAll('.nbmap-node.chap.locked'), function(n){ var f = face(n); if (!f) return false; var r = f.getBoundingClientRect();
                    if (r.top < 40 || r.bottom > innerHeight - 40) return false; var e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !!(e && e.closest('.nbmap-node') === n); })[0];
                  if (!n) return null; var r = face(n).getBoundingClientRect();
                  return {xy: [r.left + r.width / 2, r.top + r.height / 2], t: n.getAttribute('data-target'), lock: n.getAttribute('data-lock')}; }""" % FACE)
                if j: break
                pg.evaluate("() => { var s = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); s.scrollTop += 200; }"); pg.wait_for_timeout(600)
            if not j: rec("D3", False, "BAD no locked chapter mark in reach")
            else:
                s0 = pg.evaluate(SC); pg.mouse.click(*j["xy"]); seq = []
                for _ in range(15): pg.wait_for_timeout(100); seq.append(pg.evaluate(SC))
                r = pg.evaluate("""(t) => { var h = document.getElementById('nbpanel-root'), n = h.querySelector('.nbmap-node[data-target="' + t + '"]'), b = h.querySelector('.nblockhint');
                  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), card = P.querySelector('.nblocked-note .nblocked-head');
                  return {sel: n.classList.contains('nbsel'), hint: b && getComputedStyle(b).display !== 'none' && b.getBoundingClientRect().height > 0 ? b.textContent : '',
                          head: card ? card.textContent.trim() : ''}; }""", j["t"])
                shot(pg, "D3_hint.png")
                mv = max(abs(x - s0) for x in seq)
                ok = mv <= 2 and not r["sel"] and r["hint"] and (not r["head"] or r["head"] in r["hint"])
                rec("D3", ok, "click on %s (lock %s): page moved %.0f px, chosen %s, hint %r" % (j["t"].split("__")[0], j["lock"], mv, r["sel"], r["hint"][:90]))
        if want("D2"):
            pg.evaluate(SC, 0); pg.wait_for_timeout(500)
            for i in range(3): pg.mouse.wheel(0, 100); pg.wait_for_timeout(120)
            pg.wait_for_timeout(1500)
            pg.keyboard.down("Control"); pg.mouse.wheel(0, -100); pg.wait_for_timeout(80); pg.mouse.wheel(0, -100); pg.keyboard.up("Control")
            pg.wait_for_timeout(150)
            s0 = pg.evaluate(SC); seq = [s0]
            for i in range(4): pg.mouse.wheel(0, 100); pg.wait_for_timeout(100); seq.append(pg.evaluate(SC))
            for i in range(40): pg.wait_for_timeout(50); seq.append(pg.evaluate(SC))
            drops = [round(seq[i] - seq[i + 1]) for i in range(len(seq) - 1) if seq[i + 1] < seq[i] - 2]
            rec("D2", not drops and seq[-1] - s0 >= 200, "lens %s: 4 notches after Ctrl+wheel %d → %d px, steps back %s" % (pg.evaluate(ZOOM), s0, seq[-1], drops[:6]))
            # the lens back to 100 for what follows
            pg.keyboard.down("Control"); pg.mouse.wheel(0, 100); pg.wait_for_timeout(80); pg.mouse.wheel(0, 100); pg.keyboard.up("Control"); pg.wait_for_timeout(1500)
        if want("D9"):
            def run(n, gap, dy=100):
                pg.evaluate(SC, 0); pg.wait_for_timeout(700); a = pg.evaluate(SC)
                for i in range(n): pg.mouse.wheel(0, dy); pg.wait_for_timeout(gap)
                pg.wait_for_timeout(1600); return pg.evaluate(SC) - a
            slow, fast, pad = run(4, 450), run(4, 25), run(40, 16, 10)
            base = 4 * 100 / 1.0       # lens 100 %: one notch = its delta (E11.3, E19.2 at 100 %: ×1)
            ok = abs(slow - base) <= 0.05 * base and fast >= 1.4 * slow and abs(pad - base) <= 0.05 * base
            rec("D9", ok, "lens %s: 4 notches slowly %d px, quickly %d px (×%.2f), touchpad 40×10 %d px (as before: %d)" % (pg.evaluate(ZOOM), slow, fast, fast / max(1, slow), pad, base))
        if want("D7"):
            Q = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), h = document.getElementById('nbpanel-root');
              var w = document.createTreeWalker(P, NodeFilter.SHOW_TEXT), n, e = null; while ((n = w.nextNode())) { if (/idea of this chapter|Idee dieses Kapitels/.test(n.textContent)) { e = n.parentElement; break; } }
              var d = h.querySelector('.nbmap-node.chap .nbchapdot'), cell = P.querySelector('.jp-Cell .jp-Cell-outputWrapper');
              return {text: e ? parseFloat(getComputedStyle(e).fontSize) : null, zoom: cell ? (cell.style.zoom || '1') : null, dot: d ? Math.round(d.getBoundingClientRect().width * 10) / 10 : null,
                      fs: document.documentElement.style.getPropertyValue('--nbfs') || null, val: (h.querySelector('.nbfs-val') || {}).textContent || null,
                      key: Object.keys(localStorage).filter(function(k){ return /^digichemjn\\.fontsize\\.v1\\./.test(k); }).map(function(k){ return k + '=' + localStorage.getItem(k); })}; }"""
            a = pg.evaluate(Q)
            pg.click("#nbpanel-root .nbbtn.nbgear"); pg.wait_for_timeout(1200)
            if not pg.query_selector("#nbpanel-root .nbfontcell .nbfs-plus"): rec("D7", False, "BAD no font-size control in the ⚙ drawer")
            else:
                vis = pg.evaluate("() => { var c = document.querySelector('#nbpanel-root .nbfontcell'); return c.getBoundingClientRect().height > 0; }")
                for i in range(3): pg.click("#nbpanel-root .nbfontcell .nbfs-plus"); pg.wait_for_timeout(150)
                shot(pg, "D7_gear.png")
                pg.click("#nbpanel-root .nbdrawer-x"); pg.wait_for_timeout(1200)
                c = pg.evaluate(Q)
                # the size itself is the stylesheet's (css-E29 reads --nbfs): checked where a rule reads it
                css = pg.evaluate("""() => [].some.call(document.styleSheets, function(sh){ try { return [].some.call(sh.cssRules, function(r){ return r.cssText.indexOf('var(--nbfs') > -1; }); } catch (e) { return false; } })""")
                txt = (a["text"] and c["text"] and abs(c["text"] / a["text"] - 1.3) <= 0.03) if css else True
                ok = vis and txt and c["fs"] == "1.3" and a["zoom"] == c["zoom"] and a["dot"] == c["dot"] and any(k.endswith("=130") for k in c["key"])
                rec("D7", ok, "cell shown %s; A+ ×3 → %s, --nbfs %s; text %s → %s px (×%.2f%s), lens zoom %s → %s, chapter mark %s → %s px, stored %s"
                    % (vis, c["val"], c["fs"], a["text"], c["text"], (c["text"] or 0) / (a["text"] or 1), "" if css else "; no rule reads --nbfs (css-E29 not in this build): size not checked", a["zoom"], c["zoom"], a["dot"], c["dot"], c["key"]))
                pg.evaluate("() => window.__nbFontSize && window.__nbFontSize(100)"); pg.wait_for_timeout(500)
        if want("D5"):
            M = """() => { var h = document.getElementById('nbpanel-root'), out = {};
              [].forEach.call(h.querySelectorAll('.nbmap-node:not(.nbgone)'), function(n, i){
                var best = null; [n].concat([].slice.call(n.querySelectorAll('*'))).forEach(function(e){ var r = e.getBoundingClientRect();
                  if (r.width > 0 && r.height > 0 && (!best || r.width * r.height > best.width * best.height)) best = r; });
                if (!best) return; var t = n.getAttribute('data-target') || n.getAttribute('data-sel') || ('#' + i);
                var a = document.getElementById(t) || (n.classList.contains('own') ? document.querySelector('.' + (n.getAttribute('data-sel') || 'zz')) : null), rr = a ? a.getBoundingClientRect() : null;
                out[(n.className.match(/\\b(title|sect|chap|task|codetask|viztask|sub|cell|own|end)\\b/g) || ['?']).join('.') + ':' + String(t).split('__')[0]] =
                  [best.width, best.height, rr ? best.top + best.height / 2 - rr.top : 0]; });
              return out; }"""
            pg.evaluate(SC, 0); pg.wait_for_timeout(600)
            a = pg.evaluate(M)
            pg.click("#nbpanel-root .nbbtn.nbfull"); pg.wait_for_timeout(2500)
            fs = pg.evaluate("() => !!document.fullscreenElement")
            c = pg.evaluate(M); shot(pg, "D5_full.png")
            bad = []
            for k, x in a.items():
                y = c.get(k)
                if not y: bad.append(k + " missing"); continue
                if abs(y[0] - x[0]) > 0.5 or abs(y[1] - x[1]) > 0.5 or abs(y[2] - x[2]) > 1: bad.append("%s %s→%s" % (k, [round(v, 1) for v in x], [round(v, 1) for v in y]))
            pg.evaluate("() => document.fullscreenElement && document.exitFullscreen()"); pg.wait_for_timeout(800)
            rec("D5", fs and not bad, "full screen %s; %d marks compared, %d differ %s (headless: same window size)" % (fs, len(a), len(bad), bad[:4]))
    finally:
        stop(p, b)
    return errs

# ------------------------------------------------------------------ D4 mixed clicks
D4_CANDS = """() => { %s var h = document.getElementById('nbpanel-root'), H = innerHeight;
  return [].filter.call(h.querySelectorAll('.nbmap-node[data-target]:not(.locked):not(.nbgone)'), function(n){
     var t = n.getAttribute('data-target'); if (/^nb(end|title)|^sec_/.test(t) || n.classList.contains('cell') || n.classList.contains('title')) return false;
     var f = face(n); if (!f) return false; var r = f.getBoundingClientRect(); if (!(r.top > 30 && r.bottom < H - 30 && document.getElementById(t))) return false;
     var e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !!(e && e.closest && e.closest('.nbmap-node') === n); })
   .map(function(n){ var r = face(n).getBoundingClientRect(); return {t: n.getAttribute('data-target'), xy: [r.left + r.width / 2, r.top + r.height / 2]}; }); }""" % FACE
D4_STATE = """(t) => { var h = document.getElementById('nbpanel-root'), n = t ? h.querySelector('.nbmap-node[data-target="' + t + '"]') : null;
  var fx = h.querySelector(':scope > .nbreadfix'), line = fx ? parseFloat(fx.style.top) : null;
  if (!(line > 0)) { var mp = h.querySelector('.nbmap'), y0 = parseInt(h.dataset.railY0 || '0', 10) || 0; if (mp && y0 > 0) line = mp.getBoundingClientRect().top + y0; }
  var aim = n && n.__nbAim, ae = aim && aim[0] && aim[0].isConnected ? aim[0] : null, ar = ae ? ae.getBoundingClientRect() : null;
  var y = ar && ar.height > 0 ? (aim[1] ? ar.top + ar.height / 2 : ar.top + 56) : null;
  var hd = null; if (t) { var sp = document.getElementById(t); var col = sp && sp.closest('.jupyter-widget-Collapse,.lm-Collapse'); hd = col && col.querySelector(':scope > .jupyter-widget-Collapse-header, :scope > .lm-Collapse-header'); }
  var hr = hd ? hd.getBoundingClientRect() : null;
  if (y === null && hr && hr.height > 2) y = hr.top + hr.height / 2;          // as the anchor (pinY): folded → its pill
  var pill = !!(n && (n.classList.contains('chap') || n.classList.contains('sect')));
  var hx = hr ? hr.left + Math.min(60, hr.width / 2) : 0, hy = hr ? hr.top + hr.height / 2 : 0, he = hr ? document.elementFromPoint(hx, hy) : null;
  var open = hd ? !!(hd.nextElementSibling && hd.nextElementSibling.getBoundingClientRect().height > 2) : null;
  return {d: (y !== null && line) ? Math.round((y - line) * 10) / 10 : null, hd: pill && he && hd.contains(he) && hr.top > 20 && hr.bottom < innerHeight - 20 ? [hx, hy] : null,
          open: open, lit: !!(n && n.classList.contains('here'))}; }"""
def mixed():
    p, b, pg, errs = start(play=True)
    try:
        random.seed(29); cur = None; bad = []; n_m = n_p = 0
        for k in range(A.steps):
            st = pg.evaluate(D4_STATE, cur) if cur else None
            if cur and st["hd"] and random.random() < 0.45:
                o0 = st["open"]; pg.mouse.click(*st["hd"]); pg.wait_for_timeout(random.choice([400, 800, 1300])); n_p += 1
                pg.wait_for_timeout(700); s = pg.evaluate(D4_STATE, cur)
                if not (s["d"] is not None and abs(s["d"]) <= 2 and s["open"] != o0): bad.append("pill %s %s→%s d=%s" % (cur.split("__")[0], o0, s["open"], s["d"]))
                continue
            cs = pg.evaluate(D4_CANDS)
            if not cs: bad.append("no mark in reach"); continue
            c = random.choice(cs); cur = c["t"]; n_m += 1
            pg.mouse.click(*c["xy"]); pg.wait_for_timeout(random.choice([400, 700, 1100])); pg.wait_for_timeout(1500)
            s = pg.evaluate(D4_STATE, cur)
            if not (s["d"] is not None and abs(s["d"]) <= 2): bad.append("mark %s d=%s lit=%s" % (cur.split("__")[0], s["d"], s["lit"]))
        rec("D4", not bad, "%d clicks (%d marks, %d pills): %d off the line %s" % (n_m + n_p, n_m, n_p, len(bad), bad[:5]))
    finally:
        stop(p, b)
    return errs

errs = []
if any(want(k) for k in ("P1m", "P1", "P5", "P6")): errs += preview()
if any(want(k) for k in ("D2", "D3", "D5", "D7", "D9")): errs += document()
if want("D4"): errs += mixed()
rec("err", not errs, "page errors %d %s" % (len(errs), errs[:2]))
red = [r for r in ROWS if not r[1]]
print("\n%d rows, %d red: %s" % (len(ROWS), len(red), " ".join(r[0] for r in red)))
print("JS-E29 OK" if not red else "JS-E29 RED")
sys.exit(1 if red else 0)
