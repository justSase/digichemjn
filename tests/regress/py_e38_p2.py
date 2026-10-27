"""E38 P2 (2026-10-27, Python) — daten.json TRÄGT, WAS DAS LAB UM EINE AUFGABE HERUM TUT.
    python3 tests/regress/py_e38_p2.py <notebook.ipynb> [--dist dist]      (nach dem Bau: dist/ ist da)

Dem Lesefenster fehlten Hinweis 1/2, Überspringen, Lösung, Gating (Dirigent 27.10.); JS J1 baut sie, die Daten kommen
aus dem Paket. Geprüft wird gegen das LAB selbst: das gebaute Notebook läuft in einem echten Kernel (frisches HOME, Seed
des Baus wie paket.run_cell, je Sprache), dort werden die Lab-Knöpfe gedrückt (Button.click) und die Prüf-Funktionen
der Aufgaben aufgerufen — und mit daten.json verglichen:
  D1  Hinweise: je Aufgabe mit Hinweis-Knopf die Stufen, die der Knopf nacheinander zeigt (en und de) = daten hinweise
  D2  Lösungen: was jeder Lösungs-Knopf mit Aufgabe aufdeckt (Code als Text) = daten loesung.code, je Sprache; Warnsatz =
      daten loesung.warn
  D3  Überspringen: jede Aufgabe mit „Skip for now“ steht in daten (ueberspringen = true), der Satz nach dem Klick =
      daten texte.skip[route][Zustand]
  D4  Toleranz je Schwierigkeit: die Prüf-Funktion des Labs nimmt Antwort ± 0,9 · Toleranz an und lehnt ± 1,1 · Toleranz
      ab, für jedes Feld, jede Stufe (gentle/standard/strict) — mit der Toleranz aus daten toleranz; hat ein Feld eine
      EIGENE Toleranz (Zielaufgabe: Kreis, im Fenster je Feld r/3), nur die Annahme (Fenster ⊆ Lab)
  D5  Gating: daten regeln.answer.wartet_auf = die Schlösser des Labs (vorher zu, nach Überspringen der Aufgabe davor
      offen, wie oeffnet_bei sagt); regeln.code.wartet_auf = cguard; Schwierigkeitsstufen = die des Labs
  D6  Prüf-Code in beiden Sprachen: code[].pruef.en/de übersetzbar, und mit der Musterlösung (loesung.code) ergibt er
      ok = True, mit dem Gerüst (stub) ok = False
Gegenprobe v1.84: rot (daten.json ohne diese Felder). Besitzer: Python."""
import sys, os, re, json, tempfile, shutil, html as _h
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "toolkit"))
a = sys.argv[1:]
NB = os.path.abspath(a[0])
DIST = os.path.abspath(a[a.index("--dist") + 1] if "--dist" in a else os.path.join(ROOT, "dist"))

PROBE = r'''
import json as _j, re as _r, html as _hh
from ipywidgets import Widget as _W, Button as _B
def _txt(v):
    return _hh.unescape(_r.sub(r"<[^>]+>", "", v or ""))
_o = {"hint": {}, "sol": [], "skip": [], "tol": {}, "lock": {}, "diff": {}, "lang": LANG["value"]}
for _k, (_b, _body, _steps) in list(_HINT_WIDGETS.items()):
    _seen = []
    for _i in range(len(_steps)):
        _b.click()
        _seen = [_txt(x) for x in _r.findall(r"<b>[^<]*</b>\s*(.*?)</div>", _body.value, _r.S)]
    _o["hint"][_k] = {"shown": _seen, "steps": [_txt(x) for x in _steps]}
_ws = [w for w in list(_W.widgets.values()) if isinstance(w, _B)]
for _w in _ws:
    if "sol-btn" in _w._dom_classes and "nbhint-btn" not in _w._dom_classes:
        _cb = _w._click_handlers.callbacks[0]
        _cl = dict(zip(_cb.__code__.co_freevars, [c.cell_contents for c in _cb.__closure__]))
        if not _cl.get("task"):
            continue
        _w.click()
        _o["sol"].append({"task": _cl["task"], "route": _cl.get("route"), "shown": _txt(_cl["body"].value),
                          "warn": _txt(_cl["warn"])})
# D5 vorher: wer ist zu?
_o["lock"]["vorher"] = {k: bool(_is_locked(k)) for k in _TASKS["order"]}
_o["lock"]["cvorher"] = {k: bool(_is_locked_code(k)) for k in _TASKS["order"]}
_o["guard"] = {k: v for k, v in _TASKS["guard"].items() if v}
_o["cguard"] = {k: v for k, v in _TASKS["cguard"].items() if v}
_o["diff"] = {k: {"tol": v["tol"], "hints": v["hints"]} for k, v in _DIFF.items()}
# D4: die Prüf-Funktionen des Labs je Stufe
_lvl0 = DIFFICULTY["level"]
for _r0 in list(_NBRW.values()):
    if _r0.get("kind") != "calc" or not _r0.get("task") or not _r0.get("check"):
        continue
    _ans = _r0["answer"]() if callable(_r0["answer"]) else _r0["answer"]
    _o["tol"][_r0["task"]] = {"ans": {k: (list(v) if isinstance(v, (tuple, list)) else [v]) for k, v in _ans.items()},
                               "fields": [f for f, _ in _r0["fields"]], "res": {}}
    for _lvl in list(_DIFF):
        DIFFICULTY["level"] = _lvl
        _o["tol"][_r0["task"]]["res"][_lvl] = {"tol": tol()}
    DIFFICULTY["level"] = _lvl0
print("@@P2@@" + _j.dumps(_o, ensure_ascii=False, default=str))
'''



def kernel(lang):
    import paket
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(NB, encoding="utf-8"))
    code = "".join(next(c for c in nb["cells"] if c["cell_type"] == "code" and len("".join(c["source"])) > 1000)["source"])
    home = tempfile.mkdtemp(prefix="py-e38-p2-")
    env = paket._clean_env(home, lang)
    env.pop("DIGICHEM_READ_PAGE", None)
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=home)

    def run(src, timeout=600):
        mid = kc.execute(src); txt, errs = [], []
        while True:
            m = kc.get_iopub_msg(timeout=timeout)
            if m["parent_header"].get("msg_id") != mid:
                continue
            t, c = m["msg_type"], m["content"]
            if t == "stream":
                txt.append(c["text"])
            elif t == "error":
                errs.append("%s: %s" % (c["ename"], c["evalue"]))
            elif t == "status" and c["execution_state"] == "idle":
                return "".join(txt), errs
    run("import random as _r36; _r36.seed(%d); del _r36" % paket.SEED_RUN)
    _, e = run(code)
    if e:
        raise RuntimeError("Kernel %s: %s" % (lang, e[:2]))
    return km, kc, run, home


def main():
    rows, fails = [], []
    def row(name, ok, det):
        rows.append("%-34s %s  %s" % (name, "ok " if ok else "RED", det))
        if not ok:
            fails.append(name)
    v = json.load(open(os.path.join(DIST, "inhalt", "vorlage" if "Vorlage" in NB else
                                    json.load(open(NB))["metadata"]["digichemjn"]["id"], "aktuell.json")))["v"]
    nid = json.load(open(NB))["metadata"]["digichemjn"]["id"]
    D = json.load(open(os.path.join(DIST, "inhalt", nid, v, "daten.json"), encoding="utf-8"))
    calc = {t["task"]: t for t in D.get("aufgaben") or []}
    code = {c["task"]: c for c in D.get("code") or []}
    lab = {}
    for lang in ("en", "de"):
        km, kc, run, home = kernel(lang)
        try:
            out, e = run(PROBE)
            if e:
                raise RuntimeError("Probe %s: %s" % (lang, e[:2]))
            lab[lang] = json.loads([l for l in out.splitlines() if l.startswith("@@P2@@")][-1][6:])
            if lang == "en":
                # D4: Prüf-Funktion je Stufe, Feld, ± 0,9/1,1 · daten-Toleranz
                spec = {}
                for t in lab["en"]["tol"]:                 # die Rechenaufgaben des Labs (Auswahl hat keine Toleranz)
                    tl = (calc.get(t) or {}).get("toleranz") or {}
                    ff = (calc.get(t) or {}).get("toleranz_felder") or []
                    spec[t] = {lvl: ([[f[0], v, f[1]] for f, v in zip(ff, tl[lvl])] if tl.get(lvl) and len(tl[lvl]) == len(ff)
                                     else None) for lvl in ("gentle", "standard", "strict")}
                src = r'''
import json as _j
_spec = _j.loads(%r); _o = {}
_lvl0 = DIFFICULTY["level"]
for _t, _lv in _spec.items():
    _r0 = next(r for r in _NBRW.values() if r.get("kind") == "calc" and r.get("task") == _t)
    _ans = _r0["answer"]() if callable(_r0["answer"]) else _r0["answer"]
    _v0 = {k: float((tuple(v) if isinstance(v, (tuple, list)) else (v,))[0]) for k, v in _ans.items()}
    _o[_t] = {}
    for _lvl, _fl in _lv.items():
        DIFFICULTY["level"] = _lvl
        _res = []
        for _f, _tl, _how in (_fl or []):     # [feld, tol, eigen|stufe] (aus toleranz + toleranz_felder)
            for _fac, _want in ((0.9, True), (-0.9, True), (1.1, False), (-1.1, False)):
                _vals = dict(_v0); _vals[_f] = _v0[_f] + _fac * _tl
                try:
                    _ok = bool(_r0["check"](_vals)[0])
                except Exception as _x:
                    _ok = repr(_x)
                _res.append([_f, _fac, _want, _ok, _how])
        _o[_t][_lvl] = _res
DIFFICULTY["level"] = _lvl0
print("@@CK@@" + _j.dumps(_o))
''' % json.dumps(spec)
                out, e = run(src)
                lab["ck"] = json.loads([l for l in out.splitlines() if l.startswith("@@CK@@")][-1][6:]) if not e else {"fehler": e}
                # D5 nachher: die Aufgabe davor überspringen (wie der Knopf), dann ist das Schloss offen?
                out, e = run(r'''
import json as _j
_o = {}
for _k, _g in list(_TASKS["guard"].items()):
    if not _g: continue
    _was = bool(_is_locked(_k))
    task_skipped(_g)
    _o[_k] = [_was, bool(_is_locked(_k)), _TASKS["state"].get(_g)]
print("@@GT@@" + _j.dumps(_o))
''')
                lab["gt"] = json.loads([l for l in out.splitlines() if l.startswith("@@GT@@")][-1][6:]) if not e else {"fehler": e}
                # D3: jeder Skip-Knopf (nach D5 — die Kette ist jetzt übersprungen: Zustand ändert sich nicht mehr bei
                # answer; code-Route ist noch offen)
                out, e = run(r'''
import json as _j, re as _r, html as _hh
from ipywidgets import Widget as _W, Button as _B
_o = []
for _w in [w for w in list(_W.widgets.values()) if isinstance(w, _B) and "nbskipnow" in w._dom_classes]:
    _cb = _w._click_handlers.callbacks[0]
    _cl = dict(zip(_cb.__code__.co_freevars, [c.cell_contents for c in _cb.__closure__]))
    _k = _cb.__defaults__[0]; _rt = _cl.get("route")
    _w.click()
    _st = (_TASKS["code"] if _rt == "code" else _TASKS["state"]).get(_k)
    _o.append({"task": _k, "route": _rt, "state": _st, "say": _hh.unescape(_r.sub(r"<[^>]+>", "", _cl["out"].value))})
print("@@SK@@" + _j.dumps(_o, ensure_ascii=False))
''')
                lab["sk"] = json.loads([l for l in out.splitlines() if l.startswith("@@SK@@")][-1][6:]) if not e else {"fehler": e}
        finally:
            km.shutdown_kernel(now=True)
            shutil.rmtree(home, ignore_errors=True)

    # ---- D1 Hinweise
    d1 = []
    n1 = 0
    for lang in ("en", "de"):
        for k, h in lab[lang]["hint"].items():
            n1 += 1
            got = ((calc.get(k) or code.get(k) or {}).get("hinweise") or {}).get(lang)
            want = h["shown"]
            if got is None or [_h.unescape(re.sub(r"<[^>]+>", "", x)) for x in got] != want or want != h["steps"]:
                d1.append("%s %s: Lab %r · daten %r" % (lang, k, want, got))
    row("D1 Hinweise = Lab-Knopf", n1 > 0 and not d1, "; ".join(d1)[:400] or "%d Hinweis-Knöpfe (en+de), Stufen gleich" % n1)
    # ---- D2 Lösungen
    d2, n2 = [], 0
    for lang in ("en", "de"):
        for s in lab[lang]["sol"]:
            n2 += 1
            ent = (calc if s["route"] == "answer" else code).get(s["task"]) or {}
            lo = ent.get("loesung") or {}
            l = {f: ((lo.get(f) or {}).get(lang) or "") for f in ("intro", "code", "warn")}
            if l["code"].strip() != s["shown"].strip() or l["warn"] != s["warn"]:
                d2.append("%s %s/%s: Lab %r · daten %r" % (lang, s["route"], s["task"], s["shown"][:50], l["code"][:50]))
    row("D2 Lösungen = Lab-Knopf", n2 > 0 and not d2, "; ".join(d2)[:400] or "%d Lösungs-Knöpfe (en+de), Code + Warnsatz gleich" % n2)
    # ---- D3 Überspringen
    d3, n3 = [], 0
    sk = lab.get("sk")
    if not isinstance(sk, list):
        d3.append("Probe: %s" % sk)
    else:
        for s in sk:
            n3 += 1
            ent = (calc if s["route"] == "answer" else code).get(s["task"])
            stmap = {"skip": "skip", "fail": "fail", "done": "done"}
            want = (((D.get("texte") or {}).get("en") or {}).get("skip") or {}).get(s["route"], {}).get(stmap.get(s["state"], "done"))
            if not ent or ent.get("ueberspringen") is not True or want != s["say"]:
                d3.append("%s/%s: daten %s, Satz Lab %r · daten %r" % (s["route"], s["task"], (ent or {}).get("ueberspringen"),
                                                                     s["say"][:40], (want or "")[:40]))
        listed = {(r, t) for r, src in (("answer", calc), ("code", code)) for t, e in src.items() if e.get("ueberspringen")}
        labset = {(s["route"], s["task"]) for s in sk}
        if listed != labset:
            d3.append("daten %s ≠ Lab %s" % (sorted(listed), sorted(labset)))
    row("D3 Überspringen = Lab", n3 > 0 and not d3, "; ".join(d3)[:400] or "%d Skip-Knöpfe, Sätze gleich" % n3)
    # ---- D4 Toleranz
    d4, n4 = [], 0
    ck = lab.get("ck") or {}
    if "fehler" in ck or not ck:
        d4.append("Probe: %s" % ck)
    for t, lv in (ck if "fehler" not in ck else {}).items():
        if not lv or not all(lv.values()):
            d4.append("%s: keine Toleranz in daten" % t); continue
        for lvl, res in lv.items():
            for f, fac, want, ok, how in res:
                # eine EIGENE Toleranz (z. B. Zielaufgabe: Kreis um das Ziel, im Fenster je Feld r/3) ist eine Teilmenge
                # dessen, was das Lab annimmt: geprüft wird nur, dass das Lab annimmt, was das Fenster annimmt
                if how == "eigen" and not want:
                    continue
                n4 += 1
                if ok is not want:
                    d4.append("%s %s %s %+.1f·tol → Lab %s" % (t, lvl, f, fac, ok))
        # die Stufen des Labs selbst
        for lvl, r in lab["en"]["tol"].get(t, {}).get("res", {}).items():
            fl = [[f[0], v, f[1]] for f, v in zip(calc[t].get("toleranz_felder") or [], (calc[t].get("toleranz") or {}).get(lvl) or [])]
            for f, tl, how in fl:
                if how == "stufe" and abs(tl - r["tol"]) > 1e-12:
                    d4.append("%s %s: daten %g, Lab tol() %g" % (t, lvl, tl, r["tol"]))
    row("D4 Toleranz je Stufe = Lab-Prüfung", n4 > 0 and not d4, "; ".join(d4)[:400] or "%d Proben (± 0,9/1,1 · tol, 3 Stufen)" % n4)
    # ---- D5 Gating
    d5 = []
    rg = D.get("regeln") or {}
    if (rg.get("answer") or {}).get("wartet_auf") != lab["en"]["guard"]:
        d5.append("answer.wartet_auf %s ≠ Lab %s" % ((rg.get("answer") or {}).get("wartet_auf"), lab["en"]["guard"]))
    if (rg.get("code") or {}).get("wartet_auf") != lab["en"]["cguard"]:
        d5.append("code.wartet_auf %s ≠ Lab %s" % ((rg.get("code") or {}).get("wartet_auf"), lab["en"]["cguard"]))
    gt = lab.get("gt") or {}
    for k, (was, now, st) in (gt.items() if "fehler" not in gt else []):
        if not was or now or "skipped" not in ((rg.get("answer") or {}).get("oeffnet_bei") or []):
            d5.append("%s: vorher zu %s, nach Überspringen zu %s" % (k, was, now))
    sd = ((D.get("schwierigkeit") or {}).get("stufen")) or {}
    if (D.get("schwierigkeit") or {}).get("gebaut") not in sd:
        d5.append("schwierigkeit.gebaut %r" % (D.get("schwierigkeit") or {}).get("gebaut"))
    if {k: {"tol": v.get("tol"), "hints": v.get("hinweise")} for k, v in sd.items()} != lab["en"]["diff"]:
        d5.append("Stufen %s ≠ Lab %s" % (sd, lab["en"]["diff"]))
    row("D5 Gating + Stufen = Lab", bool(gt) and "fehler" not in gt and not d5, "; ".join(d5)[:400] or
        "%d Schlösser: zu, nach Überspringen offen · cguard gleich · 3 Stufen" % len(gt))
    # ---- D6 Prüf-Code en/de
    d6, n6 = [], 0
    for t, c in code.items():
        pr = c.get("pruef") or {}
        sol = (((c.get("loesung") or {}).get("code")) or {}).get("en")
        for lang in ("en", "de"):
            p = pr.get(lang)
            if not p:
                d6.append("%s %s: kein Prüf-Code" % (t, lang)); continue
            n6 += 1
            for what, src, want in (("Lösung", sol, True), ("leer", "", False)):
                if src is None:
                    continue
                ns = {}
                try:
                    exec(compile(src, "<%s>" % what, "exec"), ns)
                    g = {}
                    exec(compile(p, "<pruef %s %s>" % (t, lang), "exec"), g)
                    ok = bool(g["_nbrw_check"](ns)[0])
                except Exception as e:
                    ok = repr(e)
                if ok is not want:
                    d6.append("%s %s %s → %s" % (t, lang, what, ok))
    row("D6 Prüf-Code en/de", n6 > 0 and not d6, "; ".join(d6)[:400] or "%d Prüf-Programme: Lösung ok, leer nicht" % n6)
    print("\n".join(rows))
    print("PY-E38-P2 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
