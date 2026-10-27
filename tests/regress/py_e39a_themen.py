"""E39a K1–K3 (2026-10-27, Python) — THEMA UND KURSE AUS DER QUELLE.
    python3 tests/regress/py_e39a_themen.py [--dist dist]      (Bündelwurzel; nach dem Bau)

  T1  jeder Ordner mit build_*.py + chapters/ (Notebook = set_notebook in _setup*.py) nennt in set_metadata
      thema="bereich.thema"; kein thema doppelt; kurse = [("<HS> · <Vorlesung>", "<platz>"), …]
  T2  Selbsttest: ein Baum mit fehlendem bzw. doppeltem thema → T1 rot UND toolkit/katalog.alle() bricht ab
  K1  jede gebaute .ipynb mit metadata.digichemjn: thema/kurse = Quelle
  K2  dist/inhalt/<id>/<v>/meta.json: thema/kurse = Quelle · dist/kurse.json = aus den Quellen gerechnet
      (Kurs → [{platz, id, titel, version}], Platz natürlich sortiert 1.2 < 1.10, kein Platz doppelt)
Quelle gelesen ohne katalog.py (eigener ast-Leser). Gegenprobe v1.83: T1/K1/K2 rot. Owner: Python."""
import ast, glob, json, os, re, shutil, sys, tempfile
ROOT = os.getcwd()
a = sys.argv[1:]
DIST = os.path.abspath(a[a.index("--dist") + 1] if "--dist" in a else os.path.join(ROOT, "dist"))
NBV = re.search(r'^NB_VERSION = "([^"]+)"', open(os.path.join(ROOT, "toolkit", "chapter_template.py"),
                encoding="utf-8").read(), re.M).group(1)


def lies(root):
    """{ordner: {id, titel, version, thema, kurse}} aus chapters/_setup*.py (Literale + NB_VERSION)."""
    out = {}
    for b in sorted(glob.glob(os.path.join(root, "*", "build_*.py"))):
        d = os.path.dirname(b)
        for f in sorted(glob.glob(os.path.join(d, "chapters", "_setup*.py"))):
            rec, md = {}, {}
            for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
                if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "set_notebook" and not rec:
                    rec = {"id": ast.literal_eval(n.args[0]), "titel": ast.literal_eval(n.args[1])}
                if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "set_metadata":
                    for k in n.keywords:
                        if k.arg in ("thema", "kurse"):
                            md[k.arg] = ast.literal_eval(k.value)
                        if k.arg == "version" and "version" not in md:
                            md["version"] = NBV if getattr(k.value, "id", "") == "NB_VERSION" else ast.literal_eval(k.value)
            if rec:
                rec.update(version=md.get("version", NBV), thema=md.get("thema"),
                           kurse=[{"kurs": k, "platz": p} for k, p in md.get("kurse") or []])
                out[os.path.basename(d)] = rec
                break
    return out


def t1(q):
    bad, seen = [], {}
    for d, r in q.items():
        t = r["thema"]
        if not (isinstance(t, str) and re.match(r"^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+(-[a-z0-9]+)*$", t)):
            bad.append("%s: thema %r" % (d, t))
        elif t in seen:
            bad.append("%s: thema %r doppelt (%s)" % (d, t, seen[t]))
        seen.setdefault(t, d)
        for e in r["kurse"]:
            if " · " not in e["kurs"] or not re.match(r"^\d+(\.\d+)*$", e["platz"]):
                bad.append("%s: kurse %r" % (d, e))
    return bad


def soll_kurse(q):
    k = {}
    for r in q.values():
        for e in r["kurse"]:
            k.setdefault(e["kurs"], []).append({"platz": e["platz"], "id": r["id"], "titel": r["titel"],
                                                "version": r["version"]})
    return {kid: sorted(v, key=lambda x: [int(p) for p in x["platz"].split(".")]) for kid, v in sorted(k.items())}


def main():
    rows, fails = [], []
    def row(tag, ok, txt):
        rows.append("%s %s · %s" % (tag, txt, "OK" if ok else "RED"))
        if not ok: fails.append(tag)
    q = lies(ROOT)
    bad = t1(q)
    row("T1", not bad and len(q) >= 4, "%d Notebooks %s%s" % (len(q), sorted(q), (" — " + "; ".join(bad)) if bad else ""))
    # T2 Selbsttest
    sys.path.insert(0, os.path.join(ROOT, "toolkit"))
    try:
        import katalog
    except ImportError:
        katalog = None
    for fall, src in (("fehlt", 'set_notebook("b", "B")\nset_metadata(title="B")\n'),
                      ("doppelt", 'set_notebook("b", "B")\nset_metadata(thema="x.a")\n')):
        tmp = tempfile.mkdtemp(prefix="e39a-")
        try:
            for nm, s in (("a", 'set_notebook("a", "A")\nset_metadata(thema="x.a")\n'), ("b", src)):
                os.makedirs(os.path.join(tmp, nm, "chapters"))
                open(os.path.join(tmp, nm, "build_%s.py" % nm), "w").write("")
                open(os.path.join(tmp, nm, "chapters", "_setup.py"), "w").write(s)
            mine = bool(t1(lies(tmp)))
            try:
                katalog.alle(tmp); kat = False
            except Exception:
                kat = katalog is not None
            row("T2", mine and kat, "Baum mit thema %s: Test rot %s, katalog.alle bricht ab %s" % (fall, mine, kat))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    try:
        o = [r["platz"] for r in katalog.kurse_json([{"id": i, "titel": i, "version": "1", "kurse": [
            {"kurs": "X · Y", "platz": p}]} for i, p in (("a", "1.10"), ("b", "1.2"), ("c", "2"))])["X · Y"]]
    except Exception as e:
        o = repr(e)
    row("T2", o == ["1.2", "1.10", "2"], "natürliche Ordnung: %s" % (o,))
    # K1 .ipynb
    n = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "*", "*.ipynb"))):
        d = os.path.basename(os.path.dirname(p))
        md = json.load(open(p, encoding="utf-8")).get("metadata", {}).get("digichemjn")
        if d not in q or md is None:
            continue
        n += 1
        ok = (md.get("thema"), md.get("kurse")) == (q[d]["thema"], q[d]["kurse"])
        row("K1", ok, "%s: thema %r kurse %r" % (os.path.basename(p), md.get("thema"), md.get("kurse")))
    row("K1", n >= 3, "%d gebaute .ipynb mit metadata.digichemjn" % n)
    # K2 meta.json + kurse.json
    ids = {r["id"]: r for r in q.values()}
    m = 0
    for p in sorted(glob.glob(os.path.join(DIST, "inhalt", "*", "*", "meta.json"))):
        mj = json.load(open(p, encoding="utf-8"))
        r = ids.get(mj.get("id"))
        if not r or mj.get("nb_version") != NBV:
            continue
        m += 1
        ok = (mj.get("thema"), mj.get("kurse")) == (r["thema"], r["kurse"]) and "id" in mj and "oer" in mj
        row("K2", ok, "meta.json %s: thema %r kurse %r" % (mj["id"], mj.get("thema"), mj.get("kurse")))
    row("K2", m >= 1, "%d meta.json der Version %s" % (m, NBV))
    kp = os.path.join(DIST, "kurse.json")
    try:
        got = json.load(open(kp, encoding="utf-8"))
    except Exception as e:
        got = "FEHLT (%s)" % type(e).__name__
    want = soll_kurse(q)
    ok = got == want and isinstance(got, dict) and all(
        len({x["platz"] for x in v}) == len(v) for v in got.values())
    row("K2", ok, "kurse.json %s" % (json.dumps(got, ensure_ascii=False)[:300] if ok else "%r ≠ %r" % (got, want)))
    print("\n".join(rows))
    print("PY-E39A-THEMEN OK" if not fails else "FAILURES: " + ", ".join(sorted(set(fails))))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
