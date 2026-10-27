"""E38 · JS — EINE DARSTELLUNG ÜBERALL: der Leser wie Lab (Werkstatt JS, 2026-10-27).
    python3 tests/regress/js_e38_j1.py [<notebook.ipynb>|--nb vorlage] [--dist DIR] [--only J1a,J1b] [--shots DIR]

plan/AUFTRAG.md J1. lesen.html aus der gebauten Hülle (`--dist DIR`, sonst <repo>/dist) über http, echter Chromium,
1400 × 900. Die Aufgaben-Daten (P2) kommen als Stand-in in eine Kopie von daten.json (Form: claude/VERTRAG-E38-js.md),
solange Python sie nicht liefert; liefert der Bau sie schon, prüft der Test mit dem echten Inhalt (Stand-in nur, wo ein
Feld fehlt — die Zeile sagt „stand-in“ oder „P2“).
  J1a Hinweis 1/2     t1: „💬 Hint 1 of 2“ sichtbar; Klick → Hinweis 1; Klick → 1+2, Knopf „Hide hints“; Klick → zu,
                      „Show hints“. Zustand bleibt open, nichts gespeichert außer hint.t1.
  J1b Überspringen    t1 „⤼ Skip for now“ → t1 skipped (gespeichert), t2 nicht mehr locked, Kapitel 2 offen, Satz wie Lab,
                      das Fenster geht zu Aufgabe 2 (deren Mitte im Fenster); Fortschritt 0 / n bleibt.
  J1c Lösung Code     Programmieraufgabe t1 „💡 Solution“ → Lösung (pre, „return a * x“) sichtbar, code.t1 = wrong (✗).
  J1d Lösung Rechnen  t2 (offen nach J1b) „💡 Solution“ → sichtbar, task.t2 = skipped; nochmal → zu, bleibt skipped.
  J1e Streng          K.diff = strict → kein Hinweis-Knopf (Lab hints_on), Überspringen bleibt.
  J1f Deutsch         lang=de → „💬 Hinweis 1 von 2“, Hinweistext deutsch, „⤼ Vorerst überspringen“.
  J1g ohne Daten      daten.json ohne Hinweise/Lösungen → kein Hinweis-/Lösungsknopf, Überspringen da.
  J1h gesperrt        t3 (gesperrt) → seine Knöpfe disabled, Klick ändert nichts.
Gegenprobe v1.84 (`390392b`): J1a–J1h rot (keine Knöpfe). Owner: JS. exit 0 = REGRESS-JS-E38-J1 OK."""
import sys, os, re, json, glob, shutil, tempfile, threading, functools, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e38_j1 is a stand-alone script")
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

args = sys.argv[1:]
ONLY = args[args.index("--only") + 1].split(",") if "--only" in args else None
want = lambda k: not ONLY or any(k.startswith(x) for x in ONLY)
shots = args[args.index("--shots") + 1] if "--shots" in args else None
DIST = args[args.index("--dist") + 1] if "--dist" in args else os.path.join(ROOT, "dist")

ROWS, FAILS = [], []
def row(k, ok, det):
    ROWS.append((k, ok, det)); print("%-4s %s  %s" % (k, "ok " if ok else "RED", det)); sys.stdout.flush()
    if not ok: FAILS.append(k)

class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve(d):
    s = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=d))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, "http://127.0.0.1:%d/" % s.server_address[1]

def ids():
    h = glob.glob(os.path.join(DIST, "huelle", "*", "manifest.json"))
    if not h: raise SystemExit("BAD no hull under %s (build first: cd vorlage && python3 build_vorlage.py)" % DIST)
    tv = os.path.basename(os.path.dirname(sorted(h)[-1]))
    pk = sorted(glob.glob(os.path.join(DIST, "inhalt", "*", "*", "meta.json")))[0]
    meta = json.load(open(pk, encoding="utf-8"))
    return tv, meta["id"], os.path.basename(os.path.dirname(pk))

# ---- the P2 stand-in (claude/VERTRAG-E38-js.md) — only where the build has no such field ----------------------
HINTS = {"t1": {"en": ["Idea: y = a·x, so just substitute.", "Working: y = a · 3 (stand-in)."],
                "de": ["Idee: y = a·x, also einsetzen.", "Rechnung: y = a · 3 (Stand-in)."]},
         "t2": {"en": ["Idea t2 (stand-in)."], "de": ["Idee t2 (Stand-in)."]}}
SOLS = {"t2": {"en": "Worked: t2 (stand-in).", "de": "Gerechnet: t2 (Stand-in)."}}
CSOL = "def y_von(a, x):\n    return a * x\n"
def dist_copy(mode):
    """mode: 'p2' (the build's fields, stand-in where missing) | 'bare' (no hints, no solutions at all)"""
    t = tempfile.mkdtemp(prefix="e38-"); d = os.path.join(t, "d"); shutil.copytree(DIST, d)
    src = []
    for p in glob.glob(os.path.join(d, "inhalt", "*", "*", "daten.json")):
        j = json.load(open(p, encoding="utf-8"))
        for a in j.get("aufgaben", []):
            if mode == "bare":
                for k in ("hinweise", "hints", "loesung", "solution"): a.pop(k, None)
                continue
            if a.get("task") in HINTS and not (a.get("hinweise") or a.get("hints")):
                a["hinweise"] = HINTS[a["task"]]; src.append("hints " + a["task"])
            if a.get("task") in SOLS and not (a.get("loesung") or a.get("solution")):
                a["loesung"] = SOLS[a["task"]]; src.append("solution " + a["task"])
        for c in j.get("code", []):
            if mode == "bare":
                for k in ("hinweise", "hints", "loesung", "solution"): c.pop(k, None)
                continue
            if c.get("task") == "t1" and not (c.get("loesung") or c.get("solution")):
                c["loesung"] = CSOL; src.append("code solution t1")
        json.dump(j, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    return d, ("stand-in: " + ", ".join(src)) if src else ("P2" if mode == "p2" else "bare")

def page(b, base, tv, nid, v, lang="en", store=None):
    c = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark")
    init = {"digichemjn.%s.reader.skin" % nid: "digi", "digichemjn.%s.reader.theme" % nid: "dark"}
    init.update(store or {})
    c.add_init_script("(function(it){ try { if (sessionStorage.getItem('__e38')) return; Object.keys(it).forEach(function(k){"
                      " localStorage.setItem(k, it[k]); }); sessionStorage.setItem('__e38','1'); } catch (e) {} })(%s);" % json.dumps(init))
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(base + "huelle/%s/lesen.html?nb=%s&v=%s&lang=%s" % (tv, nid, v, lang))
    pg.wait_for_selector("html[data-nbl=bereit]", timeout=30000); pg.wait_for_timeout(700)
    pg.evaluate("() => { window.__nbReader.show('doc'); }"); pg.wait_for_timeout(500)
    return c, pg, errs

# state of one exercise box: its buttons, hints, solution, the stored values
BOX = """([kind, key]) => {
  var el = document.getElementById('nbr-rw-' + kind + '-' + key);
  if (!el) return {missing: true};
  for (var x = el.parentElement; x; x = x.parentElement) if (x.tagName === 'DETAILS' && !x.open) x.open = true;
  var vis = function (e) { return !!(e && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden' && getComputedStyle(e).display !== 'none'); };
  var q = function (s) { return el.querySelector(s); }, hb = q('.nbrw-hintbtn'), sb = q('.nbrw-solbtn'), kb = q('.nbrw-skipbtn');
  var ls = {}; Object.keys(localStorage).forEach(function (k) { if (/\\.reader\\.(task|code|hint)\\./.test(k)) ls[k.replace(/^.*\\.reader\\./, '')] = localStorage.getItem(k); });
  var sol = q('.nbrw-sol');
  return {st: el.getAttribute('data-st'),
          hint: vis(hb) ? hb.textContent : null, hintDis: hb ? hb.disabled : null,
          hints: [].filter.call(el.querySelectorAll('.nbrw-hint'), vis).map(function (h) { return h.textContent; }),
          sol: vis(sb) ? sb.textContent : null, solDis: sb ? sb.disabled : null, solText: vis(sol) ? sol.textContent : '',
          skip: vis(kb) ? kb.textContent : null, skipDis: kb ? kb.disabled : null,
          say: (q('.nbrw-skipsay') && vis(q('.nbrw-skipsay'))) ? q('.nbrw-skipsay').textContent : '', ls: ls}; }"""
CLICK = """([kind, key, cls]) => { var b = document.querySelector('#nbr-rw-' + kind + '-' + key + ' .' + cls); if (!b) return false; b.click(); return true; }"""
INWIN = """(id) => { var el = document.getElementById(id), w = document.querySelector('.nbrw-win');
  if (!el) return null; var r = el.getBoundingClientRect(), q = w.getBoundingClientRect();
  return {top: Math.round(r.top - q.top), bottom: Math.round(r.bottom - q.top), h: Math.round(q.height)}; }"""
XP = "() => { var x = document.querySelector('.nbrw-xp'); return x ? [x.getAttribute('data-solved'), x.getAttribute('data-n')] : null; }"
def box(pg, kind, key): return pg.evaluate(BOX, [kind, key])
def click(pg, kind, key, cls): r = pg.evaluate(CLICK, [kind, key, cls]); pg.wait_for_timeout(500); return r

def j1(b, tv, nid, v):
    d, how = dist_copy("p2"); srv, base = serve(d)
    c, pg, errs = page(b, base, tv, nid, v)
    # J1a — hints one step per click, then hide
    a0 = box(pg, "calc", "t1"); click(pg, "calc", "t1", "nbrw-hintbtn"); a1 = box(pg, "calc", "t1")
    click(pg, "calc", "t1", "nbrw-hintbtn"); a2 = box(pg, "calc", "t1")
    if shots:
        pg.evaluate("() => document.getElementById('nbr-rw-calc-t1').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(shots, "E38-js-J1-hinweise-skip-loesung.png"))
    click(pg, "calc", "t1", "nbrw-hintbtn"); a3 = box(pg, "calc", "t1")
    ok = (a0.get("hint") or "").endswith("Hint 1 of 2") and not a0["hints"] and len(a1["hints"]) == 1 and a1["hints"][0].startswith("Hint 1.") \
        and len(a2["hints"]) == 2 and (a2["hint"] or "").endswith("Hide hints") and not a3["hints"] and (a3["hint"] or "").endswith("Show hints") \
        and a3["st"] == "open" and "task.t1" not in a3["ls"]
    row("J1a", ok, "%s · %r → %d → %d %r → %d %r, st %s, stored %s" % (how, a0.get("hint"), len(a1.get("hints", [])), len(a2.get("hints", [])),
        a2.get("hint"), len(a3.get("hints", [])), a3.get("hint"), a3.get("st"), a3.get("ls")))
    # J1b — skip: t1 skipped, t2 opens, the window goes to exercise 2
    t2a = box(pg, "calc", "t2"); x0 = pg.evaluate(XP)
    pg.evaluate("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(200)
    click(pg, "calc", "t1", "nbrw-skipbtn"); pg.wait_for_timeout(1200)
    b1 = box(pg, "calc", "t1"); w2 = pg.evaluate(INWIN, "nbr-rw-calc-t2"); t2b = box(pg, "calc", "t2"); x1 = pg.evaluate(XP)
    ok = b1.get("st") == "skipped" and b1["ls"].get("task.t1") == "skipped" and t2a.get("st") == "locked" and t2b.get("st") == "open" \
        and "next chapter" in b1.get("say", "") and w2 and 0 <= w2["top"] and w2["bottom"] <= w2["h"] and x0 == x1
    row("J1b", ok, "t1 %s (%s), t2 %s → %s, say %r, t2 in window %s, xp %s → %s" % (b1.get("st"), b1.get("ls", {}).get("task.t1"), t2a.get("st"),
        t2b.get("st"), b1.get("say", "")[:40], w2, x0, x1))
    # J1c — the coding solution = given up
    c0 = box(pg, "code", "t1"); click(pg, "code", "t1", "nbrw-solbtn"); c1 = box(pg, "code", "t1")
    ok = (c0.get("sol") or "").endswith("Solution") and "return a * x" in c1.get("solText", "") and c1["ls"].get("code.t1") == "wrong" \
        and c1.get("st") == "wrong" and (c1.get("sol") or "").endswith("Hide solution")
    row("J1c", ok, "code t1: %r → %r, shown %r, code.t1 %s, st %s" % (c0.get("sol"), c1.get("sol"), c1.get("solText", "")[:40], c1["ls"].get("code.t1"), c1.get("st")))
    # J1d — the answer route's solution = skipped, nothing else
    d0 = box(pg, "calc", "t2"); click(pg, "calc", "t2", "nbrw-solbtn"); d1 = box(pg, "calc", "t2")
    click(pg, "calc", "t2", "nbrw-solbtn"); d2 = box(pg, "calc", "t2")
    ok = d0.get("st") == "open" and "t2" in d1.get("solText", "") and d1["ls"].get("task.t2") == "skipped" and not d2.get("solText") \
        and d2.get("st") == "skipped"
    row("J1d", ok, "calc t2: st %s → %s (%s), shown %r, again → %r st %s" % (d0.get("st"), d1.get("st"), d1["ls"].get("task.t2"),
        d1.get("solText", "")[:40], d2.get("solText", ""), d2.get("st")))
    # J1h — a locked exercise: buttons disabled, a click changes nothing
    h0 = box(pg, "calc", "t4"); pg.evaluate("() => { var b = document.querySelector('#nbr-rw-calc-t4 .nbrw-skipbtn'); if (b) { b.disabled = false; b.click(); } }")
    pg.wait_for_timeout(400); h1 = box(pg, "calc", "t4")
    row("J1h", h0.get("st") == "locked" and h0.get("skipDis") is True and h0.get("hintDis") in (True, None) and h1.get("st") == "locked"
        and "task.t4" not in h1["ls"], "t4 %s, disabled skip %s hint %s, after a forced click %s, stored %s" % (h0.get("st"), h0.get("skipDis"),
        h0.get("hintDis"), h1.get("st"), h1.get("ls")))
    if errs: row("J1-", False, "page errors: %s" % errs[:3])
    c.close()
    # J1e — strict: no hints
    c, pg, errs = page(b, base, tv, nid, v, store={"digichemjn.%s.reader.diff" % nid: "strict"})
    e = box(pg, "calc", "t1")
    row("J1e", e.get("hint") is None and (e.get("skip") or "").endswith("Skip for now"), "strict: hint %r, skip %r" % (e.get("hint"), e.get("skip")))
    c.close()
    # J1f — German
    c, pg, errs = page(b, base, tv, nid, v, lang="de", store={"digichemjn.%s.reader.lang" % nid: "de"})
    f0 = box(pg, "calc", "t1"); click(pg, "calc", "t1", "nbrw-hintbtn"); f1 = box(pg, "calc", "t1")
    row("J1f", (f0.get("hint") or "").endswith("Hinweis 1 von 2") and f1.get("hints") and f1["hints"][0].startswith("Hinweis 1.")
        and "einsetzen" in f1["hints"][0] and (f0.get("skip") or "").endswith("Vorerst überspringen"),
        "de: %r, %r, skip %r" % (f0.get("hint"), (f1.get("hints") or [""])[0][:40], f0.get("skip")))
    c.close(); srv.shutdown()
    # J1g — no data
    d, how = dist_copy("bare"); srv, base = serve(d)
    c, pg, errs = page(b, base, tv, nid, v)
    g = box(pg, "calc", "t1"); gc = box(pg, "code", "t1")
    row("J1g", g.get("hint") is None and g.get("sol") is None and gc.get("sol") is None and (g.get("skip") or "").endswith("Skip for now")
        and (gc.get("skip") or "").endswith("Skip for now"), "bare: hint %r, solution %r/%r, skip %r/%r" % (g.get("hint"), g.get("sol"), gc.get("sol"),
        g.get("skip"), gc.get("skip")))
    c.close(); srv.shutdown()

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src, "· dist:", DIST)
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    tv, nid, v = ids()
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    try:
        for k, fn in (("J1", lambda: j1(b, tv, nid, v)),):
            if not want(k): continue
            try: fn()
            except Exception as e: row(k, False, "BAD %s" % str(e).splitlines()[0][:200])
    finally:
        b.close(); p.stop()
    print("REGRESS-JS-E38-J1 %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
