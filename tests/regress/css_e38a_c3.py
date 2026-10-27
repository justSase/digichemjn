"""E38a C3 · CSS — Werkstatt CSS, 26.10. (Auftrag plan/AUFTRAG.md C3: „Cover-Kontrast (C2c) ≥ 4,5 in jedem Stil × hell/dunkel
(gesperrte Kapitel, K3/Ziele, „Timeline · …“, Modus „Both“)“). Im echten JupyterLab, 1400 × 900, frisches Profil je Zeile, Run All:

    python3 tests/regress/css_e38a_c3.py [notebook.ipynb] [--skins digi,minimal,cyber,fairy] [--themes light,dark]
                                         [--env lab,nb7] [--shots DIR] [--json out.json]

  C3   jeder sichtbare Text des Covers (.nbcover-out) ≥ 4,5 : 1 gegen den ungünstigsten Punkt seines Grundes (css_e34 MEASURE R4,
       wie css_e35 C2c — dort nur INFO), je Umgebung × Stil × hell/dunkel, in drei Lagen:
         a  wie geladen (Modus „Both“ gewählt, gesperrte Kapitel auf der Zeitleiste)
         b  „What you will learn“ aufgeklappt (Ziele K3, Kapitel, Zeit)
         c  Zeiger über einem gesperrten Kapitel (Hover-Box)
Gegenprobe v1.82 (2bb91ab5): rot (Chronik). exit 0 = REGRESS-CSS-E38A-C3 OK."""
import sys, os, json, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from playwright.sync_api import sync_playwright
import css_e34 as E

A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
SKINS = opt("--skins", "digi,minimal,cyber,fairy").split(",")
THEMES = opt("--themes", "light,dark").split(",")
ENVS = opt("--env", "lab").split(",")
SHOTS, JOUT = opt("--shots"), opt("--json")
W, H = 1400, 900

OPEN = r"""() => { var c = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out');
  if (!c) return 'no cover'; var s = c.querySelector('details:not([open]) > summary');
  if (!s) return c.querySelector('details[open]') ? 'open' : 'no details'; s.click(); return 'clicked'; }"""
LOCKED = r"""() => { var c = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out');
  var d = c && [].slice.call(c.querySelectorAll('[class*=locked], [data-st=locked], .is-locked')).filter(function (e) {
    var r = e.getBoundingClientRect(); return r.width > 2 && r.height > 2; })[0];
  if (!d) return null; d.scrollIntoView({block: 'center'}); var r = d.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"""

def main():
    import nbpick
    src = os.path.abspath(nbpick.from_argv(sys.argv))
    nid = (json.load(open(src, encoding="utf-8")).get("metadata", {}).get("digichemjn", {}) or {}).get("id") or "vorlage"
    rows = []
    def row(name, ok, detail=""):
        rows.append({"row": name, "ok": bool(ok), "detail": detail})
        print("%s  %-36s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)
    with sync_playwright() as P:
        b = P.chromium.launch(executable_path=E.CHROME if os.path.exists(E.CHROME) else None)
        for env in ENVS:
            for theme in THEMES:
                tmp = tempfile.mkdtemp(prefix="e38c3_"); shutil.copy(src, os.path.join(tmp, "v.ipynb"))
                srv, base = E.start_server(env, tmp, theme)
                try:
                    for sk in SKINS:
                        tag = "%s %s %s" % (env, sk, theme)
                        ctx = b.new_context(viewport={"width": W, "height": H}, color_scheme=theme)
                        items = {"digichemjn.theme.v1." + nid: theme, "digichemjn.skin.v1." + nid: sk}
                        ctx.add_init_script("try{if(!sessionStorage.getItem('__e38')){var o=%s;for(var k in o)localStorage.setItem(k,o[k]);"
                                            "sessionStorage.setItem('__e38','1');}}catch(e){}" % json.dumps(items))
                        pg = ctx.new_page()
                        pg.goto(base + ("/lab/tree/v.ipynb?reset" if env == "lab" else "/notebooks/v.ipynb"))
                        pg.wait_for_selector(".jp-NotebookPanel .jp-Cell", state="attached", timeout=180000); pg.wait_for_timeout(3000)
                        st = E.run_and_play(pg)
                        cls = pg.evaluate("() => document.body.className").split()
                        good = st == "ok" and (("nbskin-" + sk) in cls if sk != "minimal" else not any(c.startswith("nbskin-") for c in cls)) \
                            and (("nbdark" in cls) == (theme == "dark")) and pg.evaluate(E.COVER_UP)
                        if not good:
                            row("C3 " + tag, False, "BAD %s · body %s" % (st, " ".join(cls)[:120])); ctx.close(); continue
                        res = []
                        k = pg.evaluate(E.MEASURE, ".nbcover-out")["r4"]; res.append(("a", k))
                        if SHOTS: os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, "C3-%s-a.png" % tag.replace(" ", "-")))
                        o = pg.evaluate(OPEN); pg.wait_for_timeout(900)
                        k = pg.evaluate(E.MEASURE, ".nbcover-out")["r4"]; res.append(("b(%s)" % o, k))
                        if SHOTS: pg.screenshot(path=os.path.join(SHOTS, "C3-%s-b.png" % tag.replace(" ", "-")))
                        xy = pg.evaluate(LOCKED)
                        if xy:
                            pg.mouse.move(*xy); pg.wait_for_timeout(900)
                            k = pg.evaluate(E.MEASURE, ".nbcover-out")["r4"]; res.append(("c", k))
                        else:
                            res.append(("c(BAD kein gesperrtes Kapitel)", {"n": 0, "low": 1, "worst": []}))
                        low = sum(r["low"] for _, r in res); n = sum(r["n"] for _, r in res)
                        worst = [w for _, r in res for w in r["worst"]]
                        uniq, wl = set(), []
                        for w in sorted(worst, key=lambda w: w["c"]):
                            key = (w["t"], w["fg"], w["bg"])
                            if key not in uniq: uniq.add(key); wl.append("%s %s/%s %.2f" % (w["t"][:24], w["fg"], w["bg"], w["c"]))
                        row("C3 " + tag, low == 0 and n > 20 and all(r["n"] > 5 for _, r in res),
                            "%d/%d unter 4,5 · %s · %s" % (low, n, " ".join("%s %d/%d" % (nm, r["low"], r["n"]) for nm, r in res), wl[:6]))
                        ctx.close()
                finally:
                    srv.terminate(); shutil.rmtree(tmp, ignore_errors=True)
        b.close()
    if JOUT: json.dump(rows, open(JOUT, "w"), ensure_ascii=False, indent=1)
    bad = [r["row"] for r in rows if not r["ok"]]
    print("%d Zeilen, %d rot%s" % (len(rows), len(bad), (": " + ", ".join(bad[:10])) if bad else ""))
    print("REGRESS-CSS-E38A-C3 OK" if not bad else "REGRESS-CSS-E38A-C3 RED")
    sys.exit(1 if bad else 0)

main()
