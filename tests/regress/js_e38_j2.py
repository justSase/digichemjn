"""E38 · JS — J2 ⚙ WIE LAB im Leser (Werkstatt JS, 2026-10-27).
    python3 tests/regress/js_e38_j2.py [<notebook.ipynb>|--nb vorlage] [--dist DIR] [--only J2a,J2b] [--shots DIR]

plan/AUFTRAG.md J2. lesen.html aus der gebauten Hülle (`--dist DIR`, sonst <repo>/dist) über http, echter Chromium, 1400 × 900,
Stil digi dunkel. Schlüssel digichemjn.<id>.reader.*.
  J2a Zeilen        ⚙ zeigt: Schwierigkeit (3) · Inhalt/Startmodus (4) · Stil (4) · hell/dunkel (3) · Seed (= daten.json) ·
                    Fortschrittscode (zeigen, einfügen, wiederherstellen) · Von vorn · Neu aufbauen; alles im Fenster
  J2b Schwierigkeit Sanft → K.diff = gentle, 9 + 0,015 bei t1 (Toleranz des Baus 0,005) = gelöst; Streng → 9 + 0,004 = falsch
                    (Lab tol(): 2e-2 / 5e-3 / 1e-3); Standard → Schlüssel weg
  J2c Stil/hell     ⚙ cyber + hell → K.skin = cyber, K.theme = light, .nbrw data-nbrw-skin/-theme folgen
  J2d Startmodus    ⚙ „Stift & Papier“ → K.mode = calc, .nbrw data-nbrw-mode = calc, Programmieraufgaben weg
  J2e Code = Lab    t1 gelöst → „Fortschrittscode zeigen“ = base64url("<id>|doooo|ooooo|s----|hmac8") mit Labs Schlüssel
                    (in Python nachgerechnet); ein in Python signierter Code „dsf..“ stellt in einem frischen Browser t1–t3 her;
                    ein von Hand geänderter → „does not check out“, nichts geändert
  J2f Von vorn      fragt zuerst (nichts gelöscht); „Ja“ → task./code. weg, t2 wieder gesperrt, Stil bleibt
  J2g Neu aufbauen  lesen.html lädt neu (Navigation), Stand bleibt
Gegenprobe v1.84 (`390392b`): J2a–J2g rot (⚙ = Sprache + Feedback). Owner: JS. exit 0 = REGRESS-JS-E38-J2 OK."""
import sys, os, re, json, glob, shutil, tempfile, threading, functools, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e38_j2 is a stand-alone script")
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

import base64, hmac, hashlib
KEY = b"digichemjn/progress-code/2026-09"
def lab_code(body): return base64.urlsafe_b64encode((body + "|" + hmac.new(KEY, body.encode(), hashlib.sha256).hexdigest()[:8]).encode()).decode().rstrip("=")
def lab_open(code):
    s = base64.urlsafe_b64decode(code + "=" * (-len(code) % 4)).decode(); body, tag = s.rsplit("|", 1)
    return body, tag == hmac.new(KEY, body.encode(), hashlib.sha256).hexdigest()[:8]

GEAR = """() => { var R = window.__nbReader; R.show('doc'); R.drawer('gear');
  var d = document.querySelector('.nbrw-drawer'), w = document.querySelector('.nbrw').getBoundingClientRect();
  var vis = function (e) { return !!(e && e.getClientRects().length && getComputedStyle(e).display !== 'none'); };
  var n = function (k) { var r = d.querySelector('[data-k=' + k + ']'); return r && vis(r) ? r.querySelectorAll('button').length : 0; };
  var r = d.getBoundingClientRect(), seed = d.querySelector('[data-seed]');
  return {diff: n('diff'), mode: n('mode'), skin: n('skin'), theme: n('theme'), code: n('code'), reset: n('reset'), rebuild: n('rebuild'),
          input: vis(d.querySelector('input.nbrw-dr-in')), seed: seed ? seed.getAttribute('data-seed') : null,
          inside: r.left >= w.left - 1 && r.right <= w.right + 1 && r.top >= w.top - 1 && r.bottom <= w.bottom + 1,
          text: d.textContent.slice(0, 400)}; }"""
TAP = """(sel) => { var b = document.querySelector('.nbrw-drawer ' + sel); if (!b) return false; b.click(); return true; }"""
LS = """() => { var o = {}; Object.keys(localStorage).forEach(function (k) { if (k.indexOf('.reader.') > 0 && !/\\.reader\\.acc\\./.test(k)) o[k.replace(/^.*\\.reader\\./, '')] = localStorage.getItem(k); }); return o; }"""
ATTR = """() => { var w = document.querySelector('.nbrw'); return {skin: w.getAttribute('data-nbrw-skin'), theme: w.getAttribute('data-nbrw-theme'),
  mode: w.getAttribute('data-nbrw-mode'), diff: w.getAttribute('data-nbrw-diff'),
  code: [].filter.call(document.querySelectorAll('.nbrw-copy'), function (e) { return e.getClientRects().length > 0 && getComputedStyle(e).display !== 'none'; }).length}; }"""
ANSWER = """([key, delta]) => { var el = document.getElementById('nbr-rw-calc-' + key);
  for (var x = el.parentElement; x; x = x.parentElement) if (x.tagName === 'DETAILS' && !x.open) x.open = true;
  var a = JSON.parse(atob(el.getAttribute('data-a'))), f = a.f[0], inp = el.querySelector('.nbrw-input[data-f="' + f[0] + '"]');
  inp.value = String(f[1] + delta); el.querySelector('.nbrw-check').click();
  return {want: f[1], tol: f[2], st: el.getAttribute('data-st')}; }"""
ST = """(key) => { var a = document.getElementById('nbr-rw-calc-' + key), c = document.getElementById('nbr-rw-code-' + key);
  return [a && a.getAttribute('data-st'), c && c.getAttribute('data-st')]; }"""
def tap(pg, sel): r = pg.evaluate(TAP, sel); pg.wait_for_timeout(400); return r
def gear(pg): return pg.evaluate(GEAR)

def j2(b, tv, nid, v):
    srv, base = serve(DIST)
    seed = json.load(open(os.path.join(DIST, "inhalt", nid, v, "daten.json"), encoding="utf-8")).get("seed", {}).get("value")
    # J2a — the rows
    c, pg, errs = page(b, base, tv, nid, v); g = gear(pg)
    if shots: pg.screenshot(path=os.path.join(shots, "E38-js-J2-zahnrad-wie-lab.png"))
    row("J2a", g["diff"] == 3 and g["mode"] == 4 and g["skin"] == 4 and g["theme"] == 3 and g["code"] >= 1 and g["input"] and g["reset"] == 1
        and g["rebuild"] == 1 and g["seed"] == str(seed) and g["inside"], "rows %s, seed %s (daten %s), in the window %s" % (
        {k: g[k] for k in ("diff", "mode", "skin", "theme", "code", "input", "reset", "rebuild")}, g["seed"], seed, g["inside"]))
    # J2c — style + light/dark
    tap(pg, "[data-skin=cyber]"); gear(pg); tap(pg, "[data-theme=light]"); a = pg.evaluate(ATTR); ls = pg.evaluate(LS)
    row("J2c", ls.get("skin") == "cyber" and ls.get("theme") == "light" and a["skin"] == "cyber" and a["theme"] == "light",
        "stored %s/%s, .nbrw %s/%s" % (ls.get("skin"), ls.get("theme"), a["skin"], a["theme"]))
    # J2d — the start mode
    c0 = pg.evaluate(ATTR)["code"]; gear(pg); tap(pg, "[data-k=mode] [data-mode=calc]"); a = pg.evaluate(ATTR); ls = pg.evaluate(LS)
    row("J2d", ls.get("mode") == "calc" and a["mode"] == "calc" and c0 > 0 and a["code"] == 0, "stored %s, .nbrw %s, coding boxes %d → %d" % (
        ls.get("mode"), a["mode"], c0, a["code"]))
    if errs: row("J2-", False, "page errors: %s" % errs[:3])
    c.close()
    # J2b — difficulty = tolerance
    c, pg, errs = page(b, base, tv, nid, v); gear(pg); tap(pg, "[data-diff=gentle]"); ls1 = pg.evaluate(LS); dg = pg.evaluate(ATTR)["diff"]
    r1 = pg.evaluate(ANSWER, ["t1", 0.015]); pg.wait_for_timeout(300); s1 = pg.evaluate(ST, "t1")
    gear(pg); tap(pg, "[data-diff=standard]"); ls2 = pg.evaluate(LS); c.close()
    c, pg, errs = page(b, base, tv, nid, v, store={"digichemjn.%s.reader.diff" % nid: "strict"})
    r2 = pg.evaluate(ANSWER, ["t1", 0.004]); pg.wait_for_timeout(300); s2 = pg.evaluate(ST, "t1"); c.close()
    c, pg, errs = page(b, base, tv, nid, v)
    r3 = pg.evaluate(ANSWER, ["t1", 0.004]); pg.wait_for_timeout(300); s3 = pg.evaluate(ST, "t1"); c.close()
    row("J2b", ls1.get("diff") == "gentle" and dg == "gentle" and s1[0] == "solved" and "diff" not in ls2 and s2[0] == "wrong" and s3[0] == "solved"
        and abs(r1["tol"] - 0.005) < 1e-9, "built tol %s · gentle +0.015 → %s · strict +0.004 → %s · standard +0.004 → %s · back to standard: key %s" % (
        r1["tol"], s1[0], s2[0], s3[0], ls2.get("diff")))
    # J2e — Lab's progress code, both ways
    c, pg, errs = page(b, base, tv, nid, v)
    pg.evaluate(ANSWER, ["t1", 0]); pg.wait_for_timeout(300); gear(pg); tap(pg, ".nbrw-dr-show"); pg.wait_for_timeout(500)
    code = pg.evaluate("() => { var p = document.querySelector('.nbrw-drawer .nbrw-dr-code'); return p ? p.textContent.trim() : null; }")
    body, good = lab_open(code) if code else ("", False)
    c.close()
    n = len(json.load(open(os.path.join(DIST, "inhalt", nid, v, "daten.json"), encoding="utf-8"))["gating"]["order"])
    want = "%s|d%s|%s|s%s" % (nid, "o" * (n - 1), "o" * n, "-" * (n - 1))
    py = lab_code("%s|dsf%s|d%s|sst%s" % (nid, "o" * (n - 3), "o" * (n - 1), "-" * (n - 3)))
    c, pg, errs = page(b, base, tv, nid, v); gear(pg)
    bad = py[:-3] + ("A" if py[-3] != "A" else "B") + py[-2:]
    pg.fill(".nbrw-drawer input.nbrw-dr-in", bad); tap(pg, ".nbrw-dr-load"); pg.wait_for_timeout(500)
    m1 = pg.evaluate("() => (document.querySelector('.nbrw-drawer .nbrw-dr-msg') || {}).textContent || ''"); ls1 = pg.evaluate(LS)
    pg.fill(".nbrw-drawer input.nbrw-dr-in", py); tap(pg, ".nbrw-dr-load"); pg.wait_for_timeout(600)
    m2 = pg.evaluate("() => (document.querySelector('.nbrw-drawer .nbrw-dr-msg') || {}).textContent || ''")
    sts = [pg.evaluate(ST, k) for k in ("t1", "t2", "t3", "t4")]
    row("J2e", good and body == want and not any(k.startswith(("task.", "code.")) for k in ls1) and ("check out" in m1 or "does not" in m1)
        and sts[0] == ["solved", "solved"] and sts[1][0] == "skipped" and sts[2][0] == "wrong" and sts[3][0] == "open",
        "shown %r → %r (hmac %s, want %r) · tampered: %r, stored %s · Lab-signed → %r, states %s" % (code, body, good, want, m1[:50],
        sorted(ls1), m2[:40], sts))
    # J2f — start over asks first
    gear(pg); tap(pg, ".nbrw-dr-reset"); ask = pg.evaluate(LS); asked = pg.evaluate("() => !!document.querySelector('.nbrw-drawer .nbrw-dr-yes')")
    tap(pg, ".nbrw-dr-yes"); after = pg.evaluate(LS); s2 = pg.evaluate(ST, "t2")
    row("J2f", asked and "task.t1" in ask and not any(k.startswith(("task.", "code.")) for k in after) and s2[0] == "locked" and after.get("skin") == "digi",
        "asked %s (still stored %s) → yes: %s, t2 %s" % (asked, sorted(k for k in ask if "." in k), sorted(after), s2[0]))
    c.close()
    # J2g — rebuild = reload in lesen.html, the state stays
    c, pg, errs = page(b, base, tv, nid, v); pg.evaluate(ANSWER, ["t1", 0]); pg.wait_for_timeout(300); gear(pg)
    navs = []; pg.on("framenavigated", lambda f: navs.append(f.url) if f == pg.main_frame else None)
    tap(pg, ".nbrw-dr-rebuild"); pg.wait_for_selector("html[data-nbl=bereit]", timeout=30000); pg.wait_for_timeout(800)
    s = pg.evaluate(ST, "t1")
    row("J2g", len(navs) >= 1 and s[0] == "solved", "navigations %d, t1 after %s" % (len(navs), s[0]))
    c.close(); srv.shutdown()

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

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src, "· dist:", DIST)
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    tv, nid, v = ids()
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    try:
        for k, fn in (("J2", lambda: j2(b, tv, nid, v)),):
            if not want(k): continue
            try: fn()
            except Exception as e: row(k, False, "BAD %s" % str(e).splitlines()[0][:200])
    finally:
        b.close(); p.stop()
    print("REGRESS-JS-E38-J2 %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
