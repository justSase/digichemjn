"""E17.5 (2026-10-02, Applikation) — THE NOTEBOOKS TALK THROUGH THE PROFILE,
AND ACROSS BROWSERS THROUGH THE ACCOUNT CODE ONLY.

    python3 tests/lab_acct.py <complex.ipynb> <modeling.ipynb> [--lite URL] [--shots DIR]

Lab: a JupyterLab of its own (or DIGICHEM_LAB_URL / DIGICHEM_LAB_ROOT);
--lite URL: a JupyterLite site whose contents hold both notebooks under these
file names (URL = the site root, …/lab/index.html is appended).

  a1  two tabs, Complex + Modeling: style, light/dark, language in Complex
      (the 👤 settings) → Modeling follows within 1 s, 0 runs, 0 loading views
  a2  lens, reading height, content, an own cell in Complex → Modeling's own
      values and cells unchanged
  b   browser 2 (own profile), fresh kernel: log in with the code of browser 1
      → favourites and progress as in browser 1 (coding 1 solved), own cells
      not carried
  c   browser 2 had skipped exercise 1 before the log-in: still skipped
      afterwards, and coding 1 solved — the merge never goes back
  d   store and code hold no answer, no cell content, no time (concept §4):
      the account code opens to states, favourites and the person id only;
      the profile keys hold no 13-digit time and no typed text

Prints one line per criterion; exit 0 = ACCT OK."""
import sys, os, re, time, json, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import *
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
LITE = None
SHOTS = None
if "--lite" in args:
    i = args.index("--lite"); LITE = args[i + 1].rstrip("/"); del args[i:i + 2]
if "--shots" in args:
    i = args.index("--shots"); SHOTS = args[i + 1]; del args[i:i + 2]
CX, MD = args[0], args[1]
if not LITE:
    BASE, LAB = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899"))
PW = "geheim-123"
rows, fails = [], []
def row(k, what, got, ok):
    rows.append("%-3s %-70s %s  %s" % (k, what, got, "ok" if ok else "ROT"))
    if not ok: fails.append(k)

def url(name, ws):
    if LITE: return "%s/lab/index.html?path=%s" % (LITE, name)
    return "%s/lab/workspaces/%s/tree/%s?reset" % (BASE, ws, name)

def kernel_home_clear():
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    for f in glob.glob(os.path.join(kh, ".digichemjn", "*")):
        try: os.remove(f)
        except Exception: pass

def put(src, name):
    if not LITE: shutil.copy(src, os.path.join(LAB, name))
    return name

def run_all(pg):
    for _ in range(3):
        if pg.query_selector(".jp-Dialog"):
            pg.keyboard.press("Enter"); pg.wait_for_timeout(800)
        pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
        pg.keyboard.press("Control+Shift+C")
        try:
            pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
        except Exception:
            pg.keyboard.press("Escape"); continue
        # filled, not typed (lab_keys.open_nb, E21 Rest Stufe 2: a typed "A"
        # in command mode puts a cell above the title)
        try:
            pg.fill(".lm-CommandPalette-input", "Run All Cells", timeout=5000)
        except Exception:
            pg.keyboard.press("Escape"); continue
        try:
            pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === 'Run All Cells'); }", timeout=8000)
        except Exception:
            pg.keyboard.press("Escape"); continue
        pg.keyboard.press("Enter")
        try:
            pg.wait_for_selector("#nbpanel-root .nbmap", state="attached", timeout=180000 if LITE else 60000)
            break
        except Exception:
            continue
    for _ in range(120):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>'idle'}).getAttribute('data-status')")
        if st == "idle": break
    pg.wait_for_timeout(2500)

def open_run(ctx, name, ws, errs):
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append("pageerror: %s" % str(e)[:160]))
    pg.goto(url(name, ws))
    pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(2000)
    run_all(pg)
    return pg

STATE_JS = r"""() => {
  var h = document.getElementById('nbpanel-root'), A = window.__nbAcct;
  var id = (function(){ try { return JSON.parse(document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbfeed[data-progress]').getAttribute('data-progress')).id; } catch (e) { return null; } })();
  var ld = document.getElementById('nbload');
  var cells = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell').length;
  var pr = [].map.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-InputPrompt'), function(e){ return e.textContent.trim(); }).join(' ');
  var g = function(k){ try { return localStorage.getItem(k); } catch (e) { return null; } };
  return {id: id, skin: (document.body.className.match(/nbskin-(\w+)/) || [0, 'minimal'])[1],
          dark: document.body.classList.contains('nbdark'), lang: A ? A.lang() : null,
          hdr: h && h.querySelector('.pg-acct .nbcell-h') ? h.querySelector('.pg-acct .nbcell-h').textContent : null,
          loading: !!(ld && ld.isConnected && getComputedStyle(ld).display !== 'none' && !ld.classList.contains('nbload-out')),
          cells: cells, prompts: pr,
          zoom: g('digichemjn.zoom.v1.' + id), rl: g('digichemjn.readline.v1.' + id), mode: g('digichemjn.mode.' + id),
          own: (function(){ try { return (JSON.parse(g('digichemjn.owncells.v1') || '{}')[id] || {cells: []}).cells.length; } catch (e) { return -1; } })(),
          acct: g('digichemjn.account.v1')};
}"""
def state(pg): return pg.evaluate(STATE_JS)

def pref(pg, k, v):
    pg.evaluate("""([k, v]) => { var s = document.querySelector('#nbpanel-root select.nbpref[data-k="' + k + '"]');
        if (!s) throw new Error('no setting ' + k); s.value = v; s.dispatchEvent(new Event('change', {bubbles: true})); }""", [k, v])

def follow(pgB, test, limit=3.0):
    t0 = time.time(); seen_load = False
    while time.time() - t0 < limit:
        s = state(pgB); seen_load = seen_load or s["loading"]
        if test(s): return time.time() - t0, seen_load, s
        pgB.wait_for_timeout(50)
    return None, seen_load, state(pgB)

def solve_code1(pg):
    # the first coding exercise's own solution (lab_keys.solve_first)
    name = pg.evaluate("() => document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook') ? 1 : 0")
    return solve_first(pg, CX)

def _unused_skip2(pg):
    ok = pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
        var bs = [].filter.call(P.querySelectorAll('button'), function(b){ return /Skip for now/.test(b.textContent) && b.offsetParent; });
        if (!bs.length) return false; bs[0].click(); return true; }""")
    pg.wait_for_timeout(4000)
    return ok

def wait_built(pg, limit=150):
    """no loading view, kernel idle, no dialog — 3 s in a row"""
    ok = 0
    for _ in range(limit * 2):
        pg.wait_for_timeout(500)
        if pg.query_selector(".jp-Dialog"):
            ok = 0; continue
        s = state(pg)
        st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>'idle'}).getAttribute('data-status')")
        ok = ok + 1 if (not s["loading"] and st == "idle") else 0
        if ok >= 6: return True
    return False

def open_me(pg):
    """the 👤 window as a reader opens it: a click on 👤, then wait until it
    takes input (rebase 03.10.: opened by setting `open` from the test, the
    drawer stayed inert until the next full sync — since E21.5b up to 6 s —
    and Playwright's fill went nowhere: no input event, empty field)"""
    shut = pg.evaluate("() => { var h = document.getElementById('nbpanel-root'); return !(h.classList.contains('open') && h.dataset.page === 'code'); }")
    if shut:
        pg.evaluate("() => document.querySelector('#nbpanel-root .nbcorner .nbbtn.nbprofile').click()")
    pg.wait_for_function("""() => { var h = document.getElementById('nbpanel-root'), d = h && h.querySelector('.nbdrawer');
        return !!(d && h.classList.contains('open') && h.dataset.page === 'code' && !d.inert && h.querySelector('.nbacct[data-where="panel"] .nbacct-btn')); }""", timeout=15000)
    pg.wait_for_timeout(400)

def marks(pg):
    return pg.evaluate("""() => { var o = {}; [].forEach.call(document.querySelectorAll('#nbpanel-root .nbmap-node.task[data-task]'), function(a){
        o[a.getAttribute('data-task')] = (a.getAttribute('data-state') || '?') + '/' + (a.getAttribute('data-cstate') || '?'); }); return o; }""")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    errs = []
    if not LITE: kill_sessions(BASE); kernel_home_clear()
    nc = put(CX, "acct_a_" + os.path.basename(CX)); nm = put(MD, "acct_b_" + os.path.basename(MD))
    if LITE: nc, nm = os.path.basename(CX), os.path.basename(MD)
    ctx1 = b.new_context(viewport={"width": 1400, "height": 900})
    A = open_run(ctx1, nc, "wa", errs)
    B = open_run(ctx1, nm, "wb", errs)
    A.bring_to_front()
    s0 = state(B); a0 = state(A)
    # ---- a1: the profile follows -------------------------------------------
    # B in front (the reader looks at it), A changed by script in the back
    B.bring_to_front()
    for k, v, test in (("skin", "cyber", lambda s: s["skin"] == "cyber"),
                       ("theme", "light" if s0["dark"] else "dark", lambda s, d=s0["dark"]: s["dark"] != d),
                       ("lang", "de", lambda s: s["lang"] == "de" and s["hdr"] == "Konto")):
        before = state(B)
        try: pref(A, k, v)
        except Exception as e:
            row("a1", "%s → %s in Complex: kein 👤-Feld" % (k, v), str(e)[:60], False); continue
        dt, ld, s = follow(B, test)
        same_run = s["prompts"] == before["prompts"]
        row("a1", "%s → %s in Complex: Modeling folgt nach · Läufe · Ladeansicht" % (k, v),
            "%s · %s · %s" % ("%.2f s" % dt if dt is not None else "nie (3 s)", "0" if same_run else "NEU", "ja" if ld else "nein"),
            dt is not None and dt <= 1.0 and same_run and not ld)
    # rebase 03.10.: and LATER — a rebuild of Modeling would come with its
    # next sync, after the 3-s window above (measured with py-E17.5: the
    # language rebuilt the open Modeling ~5 s later). 8 s more, no run.
    pb = state(B)["prompts"]
    seen_ld = False
    for _ in range(16):
        B.wait_for_timeout(500); seen_ld = seen_ld or state(B)["loading"]
    pb2 = state(B)["prompts"]
    row("a1", "8 s danach: Modeling ohne Lauf · ohne Ladeansicht", "%s · %s" % ("0" if pb2 == pb else "NEU", "ja" if seen_ld else "nein"),
        pb2 == pb and not seen_ld)
    # Complex itself may rebuild for the language (👤 = like the content
    # choice, E17.1): wait until it is done before the next step — in front,
    # as a reader would come back to it (a tab in the back is throttled and
    # its restart question waited there for minutes)
    A.bring_to_front()
    wait_built(A)
    B.bring_to_front()
    # ---- a2: the notebook's own values stay its own --------------------------
    sB = state(B)
    A.evaluate("""() => { var z = document.querySelector('#nbpanel-root .nbzoom-lab'); if (z) { z.value = '80'; z.dispatchEvent(new Event('input', {bubbles: true})); z.dispatchEvent(new Event('change', {bubbles: true})); } }""")
    A.evaluate("() => { try { localStorage.setItem(window.__nbOKey ? window.__nbOKey().replace('orient', 'readline') : 'x', '-60'); } catch (e) {} }")
    A.evaluate("""() => { var sels = document.querySelectorAll('.nbctl-difficulty select'); for (var i = 0; i < sels.length; i++)
        for (var j = 0; j < sels[i].options.length; j++) if (/Only calculating/.test(sels[i].options[j].textContent)) {
          sels[i].selectedIndex = j; sels[i].dispatchEvent(new Event('change', {bubbles: true})); return true; } return false; }""")
    A.evaluate("() => { var y = document.querySelector('#nbpanel-root .nbmap-node.cell'); if (y) y.click(); }")
    A.wait_for_timeout(2500)
    aN = state(A); sB2 = state(B)
    changedA = [k for k in ("zoom", "mode", "cells") if aN[k] != a0[k]]
    keptB = all(sB2[k] == sB[k] for k in ("zoom", "rl", "mode", "own", "cells", "prompts"))
    row("a2", "Lupe/Lesehöhe/Inhalt/eigene Zelle in Complex (%s geändert) → Modeling unverändert" % ",".join(changedA),
        "ja" if keptB else "nein: %s" % {k: (sB[k], sB2[k]) for k in ("zoom", "rl", "mode", "own", "cells") if sB[k] != sB2[k]},
        keptB and len(changedA) >= 2)
    # rebase 03.10.: a2 chose "Only calculating" for Complex, and a choice of
    # content holds AT ONCE for this notebook (E21 B6: it is rebuilt without
    # coding). The coding exercise below needs it back: "Both", rebuilt.
    # (BEHAUPTETE BISHER, by its timing: the solve ran before that rebuild.)
    A.bring_to_front()
    A.evaluate("""() => { var sels = document.querySelectorAll('.nbctl-difficulty select'); for (var i = 0; i < sels.length; i++)
        for (var j = 0; j < sels[i].options.length; j++) if (/^Both/.test(sels[i].options[j].textContent.trim())) {
          sels[i].selectedIndex = j; sels[i].dispatchEvent(new Event('change', {bubbles: true})); return true; } return false; }""")
    for _ in range(240):
        A.wait_for_timeout(500)
        if A.evaluate("() => { var f = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbfeed[data-nbmode]'); return !!(f && f.getAttribute('data-nbmode') === 'both'); }"):
            break
    wait_built(A)
    # progress in browser 1: coding 1 solved, then the code
    t = solve_first(A, CX)
    A.wait_for_timeout(3000)
    open_me(A)
    A.click('#nbpanel-root .nbacct-btn[data-do="new"]'); A.wait_for_timeout(300)
    A.fill("#nbpanel-root .nbacct-pw1", PW); A.fill("#nbpanel-root .nbacct-pw2", PW)
    A.click('#nbpanel-root .nbacct-btn[data-do="create"]')
    A.wait_for_function("() => !!document.querySelector('#nbpanel-root .nbacct-codetext')", timeout=20000)
    code = A.evaluate("() => document.querySelector('#nbpanel-root .nbacct-codetext').textContent")
    fav1 = json.loads(A.evaluate("() => localStorage.getItem('digichemjn.account.v1')"))["fav"]
    own1 = A.evaluate("() => localStorage.getItem('digichemjn.owncells.v1')")
    if SHOTS:
        A.evaluate("() => { var c = document.querySelector('#nbpanel-root .nbacct-btn[data-do=\"qr\"]'); if (c) c.click(); }")
        A.wait_for_timeout(600); A.screenshot(path=os.path.join(SHOTS, "acct-b1-%s.png" % ("lite" if LITE else "lab")))
    m1 = marks(A)
    # ---- b, c: browser 2 ------------------------------------------------------
    if not LITE: kill_sessions(BASE); kernel_home_clear()
    nc2 = put(CX, "acct_c_" + os.path.basename(CX)) if not LITE else nc
    ctx2 = b.new_context(viewport={"width": 1400, "height": 900})
    C = open_run(ctx2, nc2, "wc", errs)
    # rebase 03.10.: browser 2 to the front — typed text goes to the page
    # that has the focus (measured: 2 of 3 runs the code was "filled" into
    # browser 2 while browser 1 had the focus: no input event, field empty,
    # the log-in never started; c red for the TEST, not the page)
    C.bring_to_front()
    # an OLDER single-notebook code first (E17.4: still taken, through the
    # same field): exercise 2 skipped — the toolkit's own format and checksum
    import hmac, hashlib, base64
    n_ex = len((m1 or {}) ) or 9
    body = "complex-numbers|o" + "s" + "o" * (n_ex - 2) + "|" + "o" * n_ex + "|" + "-" * n_ex
    old = base64.urlsafe_b64encode((body + "|" + hmac.new(b"digichemjn/progress-code/2026-09", body.encode(), hashlib.sha256).hexdigest()[:8]).encode()).decode().rstrip("=")
    open_me(C)
    C.fill("#nbpanel-root .nbacct-code", old); C.fill("#nbpanel-root .nbacct-pw", "")
    C.click('#nbpanel-root .nbacct-btn[data-do="in"]')
    # the kernel's own record (a locked exercise draws "open" on the panel)
    kern = lambda: C.evaluate("async () => { var k = await window.__nbKernelProgress(); return k ? k.body : null; }")
    for _ in range(30):
        C.wait_for_timeout(500)
        if "Restored" in C.evaluate("() => document.querySelector('#nbpanel-root .nbacct-msg').textContent"): break
    C.wait_for_timeout(1500)
    oldmsg = C.evaluate("() => document.querySelector('#nbpanel-root .nbacct-msg').textContent")
    k2a = kern() or ""
    skipped = k2a[1:2] == "s"
    row("c", "älterer Einzel-Code im Konto-Feld → an den Kernel: Aufgabe 2 übersprungen",
        "%s · Kernel %s" % (oldmsg[:44], k2a), skipped)
    C.fill("#nbpanel-root .nbacct-code", code); C.fill("#nbpanel-root .nbacct-pw", PW)
    C.click('#nbpanel-root .nbacct-btn[data-do="in"]')
    for _ in range(40):
        C.wait_for_timeout(500)
        m2 = marks(C)
        if m2.get("t1", "").endswith("/done"): break
    C.wait_for_timeout(2000)
    m2 = marks(C); s2 = state(C); k2 = kern() or ""
    fav2 = json.loads(s2["acct"] or "{}").get("fav") if s2["acct"] else None
    own2 = C.evaluate("() => localStorage.getItem('digichemjn.owncells.v1')")
    row("b", "Browser 2 eingeloggt: Favoriten = Browser 1 · Stil/Sprache/hell-dunkel angewandt",
        "%s · %s/%s/%s" % ("gleich" if {k: v for k, v in (fav2 or {}).items() if v} == {k: v for k, v in fav1.items() if v} else "%s ≠ %s" % (fav2, fav1), s2["skin"], s2["lang"], "dunkel" if s2["dark"] else "hell"),
        {k: v for k, v in (fav2 or {}).items() if v} == {k: v for k, v in fav1.items() if v} and s2["skin"] == fav1.get("skin") and s2["lang"] == fav1.get("lang"))
    row("b", "Browser 2: Coding 1 gelöst wie in Browser 1 (Kernel, Panel)",
        "B1 t1=%s · B2 t1=%s" % (m1.get("t1"), m2.get("t1")), m2.get("t1", "").endswith("/done") and m1.get("t1", "").endswith("/done"))
    row("b", "eigene Zellen nicht übertragen (owncells in Browser 2; der Code trägt keine, s. d)",
        "B1 %s · B2 %s" % ("da" if own1 and own1 != "{}" else "leer", own2 or "leer"),
        not own2 or own2 == "{}" or "acct_" not in (own2 or ""))
    row("c", "Browser 2: Aufgabe 2 vor dem Login übersprungen (Code: offen) → danach noch, + Coding 1",
        "Kernel vorher %s · nachher %s" % (k2a, k2), skipped and k2[1:2] == "s" and k2.split("|")[1][:1] == "d")
    # ---- d: what is in the store and in the code --------------------------------
    opened = C.evaluate("""async ([code, pw]) => {
        var c = code.replace(/\\s+/g, ''), m = /^DCJ1\\.([A-Za-z0-9_-]+)\\.([0-9A-Z]{2})$/.exec(c);
        var s = m[1].replace(/-/g, '+').replace(/_/g, '/'); s = atob(s + '==='.slice((s.length + 3) % 4));
        var u = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) u[i] = s.charCodeAt(i);
        var E = new TextEncoder(), k0 = await crypto.subtle.importKey('raw', E.encode(pw), 'PBKDF2', false, ['deriveKey']);
        var k = await crypto.subtle.deriveKey({name: 'PBKDF2', salt: u.slice(1, 17), iterations: 300000, hash: 'SHA-256'}, k0,
                                              {name: 'AES-GCM', length: 256}, false, ['decrypt']);
        var z = new Uint8Array(await crypto.subtle.decrypt({name: 'AES-GCM', iv: u.slice(17, 29)}, k, u.slice(29)));
        if (u[0] === 0x11) z = new Uint8Array(await new Response(new Blob([z]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer());
        return new TextDecoder().decode(z); }""", [code, PW])
    parts = opened.split("~")
    clean = (parts[0] == "1" and re.match(r"^[0-9A-Z]{12}$", parts[1]) and re.match(r"^[mcrfa-][ald-][ed-][ra-][bckp-]$", parts[2])
             and all(re.match(r"^[a-z0-9-]+(\.[a-z]+)?=[odsf]*\|[odsf]*\|[gst-]*$", e) for e in parts[3:]))
    row("d", "Code (%d Zeichen) geöffnet: nur Version, Person-Id, Favoriten, Zustände" % len(code), opened[:90], bool(clean) and len(code) <= 300)
    store = C.evaluate("""() => { var o = {}; for (var i = 0; i < localStorage.length; i++) { var k = localStorage.key(i);
        if (/^digichemjn\\./.test(k)) o[k] = localStorage.getItem(k); } return o; }""")
    acc_keys = {k: v for k, v in store.items() if re.search(r"\.(account|progress|cover|lang|skin|theme|role|defmode|guizoom)\.v1$|acct\.push", k)}
    times = [k for k, v in acc_keys.items() if re.search(r"(?<!\d)1[6-9]\d{11}(?!\d)", v)]
    typed = [k for k, v in acc_keys.items() if re.search(r"roots_of|def |geheim|return ", v)]
    row("d", "Profil-/Konto-Schlüssel (%d): keine Zeit (13 Ziffern) · keine Antwort/Zellinhalt/Passwort" % len(acc_keys),
        "Zeit in %s · Text in %s" % (times or "keinem", typed or "keinem"), not times and not typed)
    if SHOTS:
        C.screenshot(path=os.path.join(SHOTS, "acct-b2-%s.png" % ("lite" if LITE else "lab")))
    row("–", "Seitenfehler", str(len(errs)), not errs)
    for r in rows: print(r)
    if errs: print("\n".join(errs[:6]))
    print("ACCT OK" if not fails else "ACCT RED: " + ", ".join(fails))
    sys.exit(0 if not fails else 1)
