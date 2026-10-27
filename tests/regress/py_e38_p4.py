"""E38 P4 (2026-10-27, Python) — JEDER REGLER BRINGT SEINE RENDER-FUNKTION ALS PYTHON MIT (live).
    python3 tests/regress/py_e38_p4.py [--dist dist] [--nb vorlage] [--pyodide DIR] [--shot bild.png]

Das Lesefenster blättert bisher durch die Bilder, die der Bau gezeichnet hat (data-z, 5–6 Werte je Regler: „Regler nur
6 Stufen“, Dirigent 27.10.). Live heißt: jeder Wert — dafür braucht das Fenster die Render-Funktion selbst.
daten.json regler[].live = {code, fn, html, params, pkgs, dpi, spec, start} (toolkit `_nbrw_live`, paket.live).
  L1  je Regler: code ist eigenständig (ein frischer Python-Prozess, `python3 -I`, ohne toolkit) und gibt für JEDEN Wert,
      den der Bau vorgezeichnet hat, Zeichen für Zeichen dasselbe Bild wie data-z (Vorschaustufe = live, gleiche Quelle);
      L1s: `_nbrw_svg(fn, kw)` (der Weg des Lesers, VERTRAG-E38-js J3) gibt das <svg> desselben Bildes
  L2  je Regler: spec nennt jede Steuerung mit vollem Bereich (float/int: min, max, step, value; menu: Optionen), und ein
      Wert ZWISCHEN den Stufen (sowie min und max) zeichnet ein Bild, das keines der vorgezeichneten ist
  L3  in Chromium mit Pyodide (PYV aus 20-reader.js, lokale Kopie unter /pyodide/<PYV>/ wie manifest.pyodide): Pakete laden
      (pkgs), Programm ausführen, Startwerte + Zwischenwert zeichnen → <svg> gleicher Größe wie data-z; Zeit bis zum
      ersten Bild (INFO), Pixelabstand Start-Bild Pyodide ↔ data-z (INFO: Pyodide hat matplotlib 3.8, der Bau 3.10)
      — ohne lokale Pyodide-Kopie: NOT RUN = rot
Gegenprobe v1.84: L1/L2/L3 rot (kein live). Besitzer: Python."""
import sys, os, re, json, zlib, base64, subprocess, tempfile, threading, functools, http.server, socketserver, time, html as _h
a = sys.argv[1:]
ROOT = os.getcwd()
DIST = os.path.abspath(a[a.index("--dist") + 1] if "--dist" in a else os.path.join(ROOT, "dist"))
NB = a[a.index("--nb") + 1] if "--nb" in a else "vorlage"
PYD = a[a.index("--pyodide") + 1] if "--pyodide" in a else os.environ.get("DIGICHEM_PYODIDE_DIR", "")
# die volle Pyodide-Ausgabe (mit numpy/matplotlib) — `npm pack pyodide` (env_reader.py_dir) hat nur den Kern:
#   curl -L -o p.tar.bz2 https://github.com/pyodide/pyodide/releases/download/<PYV>/pyodide-<PYV>.tar.bz2; tar xjf p.tar.bz2
SHOT = a[a.index("--shot") + 1] if "--shot" in a else None
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
PYV = re.search(r"var PYV = '([^']+)'", open(os.path.join(ROOT, "toolkit", "js", "20-reader.js"), encoding="utf-8").read()).group(1)

RUNNER = r'''
import json, sys
spec = json.load(sys.stdin)
g = {"__name__": "_nbrw_live"}
exec(compile(spec["py"], "<live>", "exec"), g)
out = []
for v in spec["werte"]:
    try:
        out.append(g[spec.get("fn") or "_nbrw_render"](**v))
    except Exception as e:
        out.append("ERROR %r" % (e,))
print(json.dumps(out))
'''


def frames(doc):
    out = []
    for m in re.finditer(r"<div class='nbrw-slider'[^>]*>", doc):
        z = re.search(r"data-z='([^']*)'", m.group(0))
        out.append(json.loads(zlib.decompress(base64.b64decode(z.group(1)))) if z else None)
    return out


def values(live, ctl):
    """Die Werte je vorgezeichnetem Bild: Start, und je Steuerung ihre Stufen (die Beschriftung der en-Fassung)."""
    sp = [s for s in live["spec"]]
    start = dict(live["start"])
    out = {0: dict(start)}
    for s, c in zip(sp, ctl):
        for j, (fi, lab) in enumerate(zip(c["i"], c["l"])):
            if fi == 0:
                continue
            if s["art"] == "menu":
                v = next(o[1] for o in s["options"] if o[0] == lab)
            elif s["art"] == "int":
                v = int(lab)
            else:
                v = float(lab)
            out[fi] = dict(start, **{s["name"]: v})
    return out


def between(live, used):
    """Ein Wert zwischen den Stufen je Steuerung (auf dem Raster des Reglers, nicht vorgezeichnet), und min/max."""
    out = []
    for s in live["spec"]:
        if s["art"] == "menu":
            continue
        lo, hi, st = float(s["min"]), float(s["max"]), float(s["step"] or 1)
        n = int(round((hi - lo) / st))
        cand = [lo + k * st for k in sorted(range(n + 1), key=lambda k: abs(k - n * 0.37))]
        cand = [int(round(x)) if s["art"] == "int" else round(x, 9) for x in cand]
        free = [x for x in cand if x not in used.get(s["name"], ())]
        if not free:
            continue
        v = free[0]
        for w in (v, s["min"], s["max"]):
            out.append(dict(live["start"], **{s["name"]: w}))
    return out


def run_py(prog, werte, fn=None):
    p = subprocess.run([sys.executable, "-I", "-c", RUNNER], input=json.dumps({"py": prog, "werte": werte, "fn": fn}),
                       capture_output=True, text=True, timeout=600, cwd=tempfile.gettempdir())
    if p.returncode:
        return ["ERROR " + p.stderr[-300:]] * len(werte)
    return json.loads(p.stdout)


def serve(dist, pyd):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *x): pass
        def translate_path(self, path):
            pre = "/pyodide/%s/" % PYV
            if path.startswith(pre):
                return os.path.join(pyd, path[len(pre):].split("?")[0])
            return super().translate_path(path)
        def guess_type(self, path):
            if path.endswith(".wasm"): return "application/wasm"
            if path.endswith(".mjs"): return "text/javascript"
            return super().guess_type(path)
    s = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Q, directory=dist))
    s.daemon_threads = True
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


PAGE = r"""<!doctype html><meta charset=utf-8><body style='margin:0;background:#04050b;color:#e9ecf6;font:14px sans-serif'>
<div id=out style='display:flex;flex-wrap:wrap;gap:12px;padding:12px'></div>
<script src='/pyodide/%s/pyodide.js'></script></body>"""

PYJS = r"""async (job) => {
  const t0 = performance.now();
  if (!window.__py) window.__py = await loadPyodide({indexURL: '/pyodide/' + job.pyv + '/'});
  const P = window.__py, t1 = performance.now();
  await P.loadPackage(job.pkgs);
  const t2 = performance.now();
  const g = P.globals.get('dict')();
  P.runPython(job.py, {globals: g});
  const r = g.get('_nbrw_render'), out = [];
  for (const v of job.werte) {
    try { out.push(r.callKwargs(v)); } catch (e) { out.push('ERROR ' + String(e).slice(-300)); }
  }
  const t3 = performance.now();
  const box = document.getElementById('out');
  out.forEach((h, i) => { const d = document.createElement('div'); d.className = 'pic'; d.setAttribute('data-i', job.nr + '-' + i);
    d.style.width = '320px'; d.innerHTML = h.startsWith('ERROR') ? '' : h;
    const c = document.createElement('div'); c.style.cssText = 'font:12px monospace;color:#ffd36b;text-align:center';
    c.textContent = 'Regler ' + job.nr + (i ? ' · live ' : ' · Start ') + JSON.stringify(job.werte[i]); d.prepend(c);
    box.appendChild(d); });
  return {out: out, ms: {pyodide: t1 - t0, pakete: t2 - t1, bilder: t3 - t2}};
}"""


def main():
    rows, fails = [], []
    def row(n, ok, det, info=False):
        rows.append("%-28s %s  %s" % (n, "INFO" if info else ("ok  " if ok else "RED "), det))
        if not ok and not info:
            fails.append(n)
    v = json.load(open(os.path.join(DIST, "inhalt", NB, "aktuell.json")))["v"]
    P = os.path.join(DIST, "inhalt", NB, v)
    D = json.load(open(os.path.join(P, "daten.json"), encoding="utf-8"))
    doc = open(os.path.join(P, "lesefassung.en.html"), encoding="utf-8").read()
    fr = frames(doc)
    regler = D.get("regler") or []
    jobs = []
    for r in regler:
        nr, live, z = r["nr"], r.get("live"), fr[r["nr"]] if r["nr"] < len(fr) else None
        if not isinstance(live, dict) or "code" not in live:
            row("L1 Regler %d" % nr, False, "kein live-Programm (%r)" % (live if not isinstance(live, dict) else live.get("fehlt")))
            row("L2 Regler %d" % nr, False, "kein live-Programm")
            continue
        if z is None:
            row("L1 Regler %d" % nr, False, "BAD kein data-z (Budget?)"); continue
        wv = values(live, z["c"])
        idx = sorted(wv)
        got = run_py(live["code"], [wv[i] for i in idx])
        same = [i for i, g in zip(idx, got) if g == z["f"][i]]
        bad = [(i, (g[:80] if g.startswith("ERROR") else "%d Zeichen anders" % sum(1 for x, y in zip(g, z["f"][i]) if x != y)))
               for i, g in zip(idx, got) if g != z["f"][i]]
        row("L1 Regler %d" % nr, len(same) == len(z["f"]) and not bad,
            "%d/%d Bilder Zeichen für Zeichen = data-z (Werte %s)%s" % (len(same), len(z["f"]),
            ", ".join("%s" % {k: wv[i][k] for k in wv[i] if wv[i][k] != live["start"].get(k)} for i in idx[1:4]) + " …",
            (" · anders: %s" % bad[:3]) if bad else ""))
        # L1s: der Weg des Lesers (J3): _nbrw_svg(fn, kw) — Menüs kommen als Beschriftung
        lab = {s["name"]: {v_: l_ for l_, v_ in s["options"]} for s in live["spec"] if s["art"] == "menu"}
        kws = [{k: lab.get(k, {}).get(v_, v_) for k, v_ in wv[i].items()} for i in idx]
        sv = run_py(live["code"] + "\n_nbrw_svg_t = lambda **kw: _nbrw_svg(%s, kw)\n" % live["fn"], kws, fn="_nbrw_svg_t")
        want_sv = [z["f"][i][z["f"][i].find("<svg"):z["f"][i].rfind("</svg>") + 6] for i in idx]
        nsv = sum(1 for a_, b_ in zip(sv, want_sv) if a_ == b_)
        row("L1s Regler %d" % nr, nsv == len(idx) and live.get("fn") and live.get("params") is not None,
            "_nbrw_svg(%s, kw): %d/%d <svg> = data-z · params %s" % (live.get("fn"), nsv, len(idx),
            [(p_["name"], p_.get("min"), p_.get("max")) for p_ in live.get("params") or []]))
        # L2
        sp_ok = all(("min" in s and "max" in s and "step" in s and "value" in s) if s["art"] != "menu" else bool(s.get("options"))
                    for s in live["spec"]) and len(live["spec"]) == len(z["c"])
        used = {}
        for w in wv.values():
            for kk, vv in w.items():
                used.setdefault(kk, set()).add(vv)
        bw = between(live, used)
        g2 = run_py(live["code"], bw)
        err = [g for g in g2 if g.startswith("ERROR")]
        mid_new = [g for g in g2[0::3] if g not in z["f"] and "<svg" in g]
        row("L2 Regler %d" % nr, sp_ok and not err and len(mid_new) == len(g2[0::3]) and g2,
            "spec %s · Zwischenwerte %s → %d/%d neue Bilder, min/max %d Fehler" % (
                [(s["name"], s["art"], s.get("min"), s.get("max"), s.get("step")) for s in live["spec"]],
                [w for w in bw[0::3]], len(mid_new), len(g2[0::3]), len(err)))
        jobs.append({"nr": nr, "py": live["code"], "pkgs": live["pkgs"], "werte": [live["start"]] + bw[0::3],
                     "f0": z["f"][0]})
    if not regler:
        row("L1", False, "BAD keine Regler in daten.json")
    # L3 Pyodide im Browser
    if not jobs:
        row("L3 Pyodide", False, "keine Programme")
    elif not PYD or not os.path.isfile(os.path.join(PYD, "pyodide.js")):
        row("L3 Pyodide", False, "NOT RUN: keine lokale Pyodide-Kopie (--pyodide DIR / DIGICHEM_PYODIDE_DIR)")
    else:
        tmp = tempfile.mkdtemp(prefix="py-e38-p4-")
        open(os.path.join(tmp, "p4.html"), "w").write(PAGE % PYV)
        s = serve(tmp, PYD); port = s.server_address[1]
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            pg = b.new_page(viewport={"width": 1400, "height": 900})
            fremd = []
            pg.on("request", lambda r: fremd.append(r.url) if not r.url.startswith("http://127.0.0.1:%d/" % port)
                  and not r.url.startswith("data:") else None)
            pg.goto("http://127.0.0.1:%d/p4.html" % port)
            for j in jobs:
                try:
                    res = pg.evaluate(PYJS, {"pyv": PYV, "pkgs": j["pkgs"], "py": j["py"], "werte": j["werte"], "nr": j["nr"]})
                except Exception as e:
                    row("L3 Regler %d Pyodide" % j["nr"], False, "Fehler %s" % str(e)[:200]); continue
                out = res["out"]
                sz = lambda h: re.search(r'<svg[^>]*?width="(\d+)px" height="(\d+)px"', h or "")
                s0, sf = sz(out[0]), sz(j["f0"])
                errs = [o[:120] for o in out if o.startswith("ERROR")]
                ok = not errs and s0 and sf and s0.groups() == sf.groups() and all("<svg" in o for o in out)
                row("L3 Regler %d Pyodide" % j["nr"], ok, "%d Bilder · Größe %s (data-z %s) · Pyodide %.1f s, Pakete %.1f s, Bilder %.0f ms%s"
                    % (len(out), s0.groups() if s0 else None, sf.groups() if sf else None, res["ms"]["pyodide"] / 1000,
                       res["ms"]["pakete"] / 1000, res["ms"]["bilder"], (" · " + "; ".join(errs[:2])) if errs else ""))
                # Pixel: Startbild Pyodide ↔ data-z, beide im Browser gezeichnet (INFO)
                try:
                    pg.evaluate("""(h) => { const d = document.createElement('div'); d.className = 'pic'; d.setAttribute('data-i', 'ref');
                        d.innerHTML = h; document.getElementById('out').appendChild(d); }""", j["f0"])
                    from PIL import Image, ImageChops
                    import io
                    A = Image.open(io.BytesIO(pg.locator("[data-i='%d-0'] svg" % j["nr"]).screenshot())).convert("RGB")
                    B = Image.open(io.BytesIO(pg.locator("[data-i='ref'] svg").screenshot())).convert("RGB")
                    pg.evaluate("() => document.querySelector(\"[data-i='ref']\").remove()")
                    if A.size == B.size:
                        df = ImageChops.difference(A, B).convert("L").point(lambda x: 255 if x > 40 else 0)
                        n = sum(1 for x in df.getdata() if x)
                        row("L3 Regler %d Pixel" % j["nr"], True, "Startbild Pyodide ↔ data-z: %d von %d px verschieden (> 40)"
                            % (n, A.size[0] * A.size[1]), info=True)
                except Exception as e:
                    row("L3 Regler %d Pixel" % j["nr"], True, "nicht gemessen: %s" % str(e)[:100], info=True)
            if SHOT:
                pg.add_style_tag(content=".pic svg{width:320px!important;height:auto!important}")
                pg.evaluate("() => window.scrollTo(0, 0)")
                pg.screenshot(path=SHOT, full_page=False)
            row("L3 fremde Hosts", not fremd, "%d Anfragen an fremde Hosts %s" % (len(fremd), fremd[:3]))
            b.close()
        s.shutdown()
    print("\n".join(rows))
    print("PY-E38-P4 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
