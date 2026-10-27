"""E38a P2 (2026-10-26, Python) — manifest.pyodide IS FILLED: Python from our own server.
    python3 tests/regress/py_e38a_p2.py [--dist dist]        (after the build: dist/ exists)

claude/VERTRAG-E36.md: manifest.json {…, "pyodide": "<url>"|null}. Until v1.82 always null (the reader then
loads Pyodide from jsDelivr). AUFTRAG E38a P2: default relative to the site root, "/pyodide/<version>/"; another
address via DIGICHEM_PYODIDE_URL; null only when switched off on purpose.
  M1  the built manifest(s) in dist/huelle/*/: pyodide == "/pyodide/<PYV>/", PYV = `var PYV` in toolkit/js/20-reader.js
      (the version the reader is written for) — and the same version in the shipped reader.<sha8>.js
  M2  paket.write_huelle into a scratch folder with DIGICHEM_PYODIDE_URL = https://example.org/py/{v} → that address
      with the version and a final / ; = "off" → null; = "" → the default; the hull files are the same in all three
      (only manifest.json differs: the reader is not rebuilt per address)
Gegenprobe v1.82: M1/M2 red (null). Owner: Python."""
import sys, os, re, json, glob, tempfile, shutil
ROOT = os.getcwd()      # run from the bundle root (the tree under test)
sys.path.insert(0, os.path.join(ROOT, "toolkit"))
a = sys.argv[1:]
DIST = os.path.abspath(a[a.index("--dist") + 1] if "--dist" in a else os.path.join(ROOT, "dist"))

def main():
    import paket
    global ENVN; ENVN = getattr(paket, "PYODIDE_ENV", "DIGICHEM_PYODIDE_URL")
    rows, fails = [], []
    pyv = re.search(r"var PYV = '([^']+)'", open(os.path.join(ROOT, "toolkit", "js", "20-reader.js"), encoding="utf-8").read()).group(1)
    want = "/pyodide/%s/" % pyv
    mans = sorted(glob.glob(os.path.join(DIST, "huelle", "*", "manifest.json")))
    if not mans:
        fails.append("M1 no dist/huelle/*/manifest.json (build first)")
    for m in mans:
        man = json.load(open(m, encoding="utf-8")); d = os.path.dirname(m)
        rj = open(os.path.join(d, man["js"]["reader"]), encoding="utf-8").read()
        ok = man.get("pyodide") == want and ("var PYV = '%s'" % pyv) in rj
        rows.append("M1 %s: pyodide %r (want %r) · reader PYV %s · %s" % (os.path.basename(d), man.get("pyodide"), want,
                    "same" if ("var PYV = '%s'" % pyv) in rj else "OTHER", "OK" if ok else "RED"))
        if not ok: fails.append("M1 %s" % os.path.basename(d))
    js = [open(os.path.join(ROOT, "toolkit", "js", "20-reader.js"), encoding="utf-8").read()]
    got, files = {}, {}
    for tag, val in (("url", "https://example.org/py/{v}"), ("off", "off"), ("leer", "")):
        tmp = tempfile.mkdtemp(prefix="e38a-p2-"); old = os.environ.get(ENVN)
        os.environ[ENVN] = val
        try:
            d, man = paket.write_huelle(tmp, "tv-test", ["a{}"], js)
            got[tag] = man.get("pyodide")
            files[tag] = {k: v["sha256"] for k, v in man["dateien"].items()}
        except Exception as e:
            got[tag] = "ERROR %r" % e
        finally:
            if old is None: os.environ.pop(ENVN, None)
            else: os.environ[ENVN] = old
            shutil.rmtree(tmp, ignore_errors=True)
    exp = {"url": "https://example.org/py/%s/" % pyv, "off": None, "leer": want}
    for k in exp:
        ok = got.get(k) == exp[k]
        rows.append("M2 DIGICHEM_PYODIDE_URL %s: %r (want %r) · %s" % (k, got.get(k), exp[k], "OK" if ok else "RED"))
        if not ok: fails.append("M2 %s" % k)
    same = len({json.dumps(v, sort_keys=True) for v in files.values()}) == 1 and len(files) == 3
    rows.append("M2 hull files equal for all three addresses: %s" % ("OK" if same else "RED"))
    if not same: fails.append("M2 files")
    print("\n".join(rows))
    print("PY-E38A-P2 OK" if not fails else "FAILURES: " + ", ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
