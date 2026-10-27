"""E39a K1/K2 (2026-10-27, Python) — THEMA UND KURSE AUS DER QUELLE.

Katalog-Kette „Ort › Hochschule › Fachbereich › Kurs › Notebook“ (Nutzer 27.10.). Jedes Notebook
nennt in `chapters/_setup*.py` in `set_metadata(...)`:
  thema="bereich.thema"            Pflicht, eindeutig über alle Notebooks (keine Doppelungen im Katalog)
  kurse=[("<HS> · <Vorlesung>", "<platz>"), …]   optional; platz „1“, „1.2“, „1.10“ (natürliche Ordnung)
Gelesen wird die Quelle ohne sie auszuführen (ast, nur Literale) — eine Quelle für die .ipynb
(metadata.digichemjn), das Inhaltspaket (meta.json) und dist/kurse.json.
"""
import ast, glob, json, os, re

THEMA = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*$")
KURS = re.compile(r"^\S.* · \S.*$")
PLATZ = re.compile(r"^\d+(?:\.\d+)*$")
HERE = os.path.dirname(os.path.abspath(__file__))


def _nbv():
    t = open(os.path.join(HERE, "chapter_template.py"), encoding="utf-8").read()
    return re.search(r'^NB_VERSION = "([^"]+)"', t, re.M).group(1)


def pruefe(thema, kurse, wo="?"):
    """Form prüfen → kurse als [{"kurs", "platz"}]. Fehler → ValueError mit Ort."""
    if not isinstance(thema, str) or not THEMA.match(thema):
        raise ValueError("%s: thema fehlt oder hat nicht die Form bereich.thema: %r" % (wo, thema))
    out = []
    for k in kurse or []:
        if not (isinstance(k, (list, tuple)) and len(k) == 2 and all(isinstance(x, str) for x in k)
                and KURS.match(k[0]) and PLATZ.match(k[1])):
            raise ValueError("%s: kurse-Eintrag nicht (\"<HS> · <Vorlesung>\", \"<platz>\"): %r" % (wo, k))
        out.append({"kurs": k[0], "platz": k[1]})
    if len({o["kurs"] for o in out}) != len(out):
        raise ValueError("%s: ein Kurs steht zweimal in kurse" % wo)
    return out


def _calls(path):
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            yield n.func.id, n


def quelle(setup):
    """Eine Setup-Datei → {id, titel, version, thema, kurse} (kurse geprüft). Ohne set_notebook → None."""
    nb, kw = None, {}
    for name, c in _calls(setup):
        if name == "set_notebook" and nb is None:
            nb = [ast.literal_eval(a) for a in c.args[:2]]
        elif name == "set_metadata":
            for k in c.keywords:
                if k.arg in ("thema", "kurse"):
                    kw[k.arg] = ast.literal_eval(k.value)
                elif k.arg == "version" and "version" not in kw:
                    kw["version"] = (ast.literal_eval(k.value) if isinstance(k.value, ast.Constant)
                                     else _nbv() if isinstance(k.value, ast.Name) and k.value.id == "NB_VERSION"
                                     else None)
    if nb is None:
        return None
    wo = os.path.relpath(setup)
    return {"id": nb[0], "titel": nb[1] if len(nb) > 1 else nb[0], "version": kw.get("version") or _nbv(),
            "thema": kw.get("thema"), "kurse_roh": kw.get("kurse"), "wo": wo}


def notebook(chapters_dir):
    """Das Notebook eines Ordners (chapters/_setup*.py mit set_notebook) — geprüft."""
    for f in sorted(glob.glob(os.path.join(chapters_dir, "_setup*.py"))):
        q = quelle(f)
        if q:
            q["kurse"] = pruefe(q["thema"], q.pop("kurse_roh"), q["wo"])
            return q
    raise ValueError("%s: kein set_notebook in _setup*.py" % chapters_dir)


def alle(root=None):
    """Alle Notebooks der Bündelwurzel: jeder Ordner mit build_*.py und chapters/. Thema eindeutig."""
    root = root or os.path.dirname(HERE)
    out, seen = [], {}
    for b in sorted(glob.glob(os.path.join(root, "*", "build_*.py"))):
        ch = os.path.join(os.path.dirname(b), "chapters")
        if not os.path.isdir(ch):
            continue
        q = notebook(ch)
        if q["thema"] in seen:
            raise ValueError("thema %r doppelt: %s und %s" % (q["thema"], seen[q["thema"]], q["wo"]))
        seen[q["thema"]] = q["wo"]
        out.append(q)
    return out


def _nat(p):
    return tuple(int(x) for x in p.split("."))


def kurse_json(nbs):
    """{kurs-id: [{platz, id, titel, version}, …]} nach Platz (1.2 < 1.10). Platz doppelt → Fehler."""
    k = {}
    for q in nbs:
        for e in q["kurse"]:
            k.setdefault(e["kurs"], []).append({"platz": e["platz"], "id": q["id"], "titel": q["titel"],
                                                "version": q["version"]})
    for kid, rows in k.items():
        rows.sort(key=lambda r: _nat(r["platz"]))
        pl = [r["platz"] for r in rows]
        if len(set(pl)) != len(pl):
            raise ValueError("Kurs %r: ein Platz ist doppelt belegt: %s" % (kid, pl))
    return {kid: k[kid] for kid in sorted(k)}


def write_kurse(dist, root=None):
    p = os.path.join(dist, "kurse.json")
    os.makedirs(dist, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(kurse_json(alle(root)), f, ensure_ascii=False, indent=1)
    return p
