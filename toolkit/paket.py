"""E36 (2026-10-19, Python) — HÜLLE UND INHALT GETRENNT: zwei neue Bau-Ausgänge.

Plan: plan/ARCHITEKTUR.md (Ausgang A), Auftrag plan/AUFTRAG.md (P1–P3). Die `.ipynb`
(Ausgang C) bleibt, wie sie ist — dieses Modul liest sie nur.

Heute macht der Kernel bei jedem Lauf die Lesefassung (`.nbreading`, E26): Dokument,
Aufgaben, Regler, Prüf-Code, und hängt die Hülle an (`_NBREAD_CSS` als <style>,
`_NBRW_REHYD` + 20-reader.js als <script>). Der Bau führt die gebaute Zelle jetzt
EINMAL je Sprache in einem echten Kernel aus (frisches HOME: kein gespeicherter
Seed, kein Fortschritt; `random.seed(SEED_RUN)` vorher: Anker-Token und Zufalls-Seed
sind bei jedem Bau gleich → das Paket ist byte-gleich reproduzierbar) und schreibt:

  dist/huelle/<TOOLKIT_VERSION>/   was für alle Notebooks gleich ist
      leser.<sha8>.css             die <style>-Blöcke der Lesefassung, in ihrer Reihenfolge
                                   (15-reader.css & Co., die Ornament-Regeln aus dem Dokument)
      reader.<sha8>.js             _NBRW_REHYD + 20-reader.js, Platzhalter __NBREADV__/__NBREADID__ (der Lader setzt
                                   data-nbrw-v/-id; claude/VERTRAG-E36.md)
      lader.<sha8>.js, lesen.html  aus toolkit/js/huelle/lader.js und lesen.html.in (JS J1, __LADER__ ersetzt), falls da
      manifest.json                {toolkit, css: [...], js: {lader, reader}, fonts, pyodide} + Bytes/gzip/sha256
                                   (pyodide: E38a P2, Standard "/pyodide/<PYV>/", DIGICHEM_PYODIDE_URL, "off" → null)
  dist/inhalt/<id>/<NB_VERSION>/   nur das Notebook-Eigene
      lesefassung.<lang>.html      die Lesefassung ohne Hülle (0 <style>, <script> nur
                                   type=application/json data-nbrw-put)
      daten.json                   Kapitel, Aufgaben + Antworten/Toleranzen, Code-Aufgaben +
                                   Prüf-Code, Regler (Steuerung; Bilder siehe unten), Gating,
                                   Marken der Zeitleiste, Seed und Modus des Baus
      meta.json                    id, nb_version, toolkit, langs, lang, title en/de, OER-Felder (META), Dateien
  dist/inhalt/<id>/aktuell.json    {"v": NB_VERSION} (lesen.html?nb=<id> ohne v)
  dist/kurse.json                  E39a K2: {kurs-id: [{platz, id, titel, version}, …]} aus allen chapters/_setup*.py

Reglerbilder stehen EINMAL im Paket: in der Lesefassung (`data-z`, das liest 20-reader.js
aus dem DOM); daten.json nennt je Regler Element-Id, Zahl der Bilder, Bytes und sha8 —
„let's not bloat“ (sie doppelt zu tragen hieße Complex ≈ +60 % Paket).

Antworten gelten für den Seed des Baus (SEED_RUN → daten.json "seed"). Einen anderen Seed
zieht nur ein Kernel (E37: Python beim Klick).

Ohne Kernel (ipykernel fehlt) bricht der Bau ab; `DIGICHEM_DIST=0` lässt die Ausgänge weg.
"""
import base64, gzip, hashlib, html as _html, json, os, re, shutil, tempfile, time, zlib

SEED_RUN = 36
LANGS = ("en", "de")
DIST_ENV = "DIGICHEM_DIST"

# was der Kernel nach dem Lauf meldet (eine Zeile JSON)
_DUMP = r'''
import json as _j36
def _e36_tl():
    try:
        return [list(r) for r in card_facts()["timeline"]]
    except Exception as _x:
        return {"fehler": repr(_x)}
print("@@E36@@" + _j36.dumps({
    "id": NOTEBOOK.get("id"), "title": NOTEBOOK.get("title"),
    "lang": LANG["value"], "mode": MODE["value"],
    "seed": {"value": SEED.get("value"), "fixed": SEED.get("fixed")},
    "toolkit": TOOLKIT_VERSION, "nb_version": NB_VERSION,
    "gate": _nbrw_gate(), "timeline": _e36_tl(),
    "titles": globals().get("_NBRW_TITLES") or {},
    "meta": {k: v for k, v in META.items()},
    "env": kernel_env()}, ensure_ascii=False, default=str))
'''


def wanted():
    return (os.environ.get(DIST_ENV) or "1").strip() != "0"


def _clean_env(home, lang):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("PYCHARM", "JETBRAINS", "IDEA_", "VSCODE", "DIGICHEM", "BINDER", "JUPYTERHUB"))}
    env.update(HOME=home, DIGICHEM_LANG=lang, PYTHONHASHSEED="0",   # hash() der Optionen → Namen der Radio-Gruppen
               DIGICHEM_READ_ALL="1",            # die Bilder gesperrter Kapitel jetzt (sonst erst beim Entsperren)
               DIGICHEM_READ_PAGE="1",           # E38a P1: die Lesezeile spricht von lesen.html, nicht von JupyterLab
               DIGICHEM_NBRW_BUDGET="1e9",       # jeder Regler bekommt seine Bilder (kein Zeitbudget im Bau)
               MPLBACKEND="module://matplotlib_inline.backend_inline")
    return env


def run_cell(nb_path, lang, timeout=1200):
    """Führt die Code-Zelle der gebauten .ipynb in einem frischen Kernel aus.
    → (Lesefassung als HTML, Daten des Kernels, Sekunden)."""
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(nb_path, encoding="utf-8"))
    code = "".join(next(c for c in nb["cells"] if c["cell_type"] == "code")["source"])
    home = tempfile.mkdtemp(prefix="digichem-e36-")
    t0 = time.time()
    km, kc = start_new_kernel(kernel_name="python3", env=_clean_env(home, lang), cwd=home)
    try:
        def drain(mid):
            outs, errs, txt = [], [], []
            while True:
                m = kc.get_iopub_msg(timeout=timeout)
                if m["parent_header"].get("msg_id") != mid:
                    continue
                t, c = m["msg_type"], m["content"]
                if t in ("display_data", "execute_result"):
                    outs.append(c["data"])
                elif t == "stream":
                    txt.append(c["text"])
                elif t == "error":
                    errs.append("%s: %s" % (c["ename"], c["evalue"]))
                elif t == "status" and c["execution_state"] == "idle":
                    return outs, errs, "".join(txt)
        _, e0, _ = drain(kc.execute("import random as _r36; _r36.seed(%d); del _r36" % SEED_RUN))
        outs, errs, _ = drain(kc.execute(code))
        _, e2, txt = drain(kc.execute(_DUMP))
        errs = e0 + errs + e2
        if errs:
            raise RuntimeError("E36: Fehler im Kernel (%s): %s" % (lang, "; ".join(errs[:3])))
        rd = [o["text/html"] for o in outs if str(o.get("text/html") or "").startswith("<div class='nbreading'")]
        if len(rd) != 1:
            raise RuntimeError("E36: %d Lesefassungen in der Ausgabe (%s), erwartet 1" % (len(rd), lang))
        line = [l for l in txt.splitlines() if l.startswith("@@E36@@")]
        if not line:
            raise RuntimeError("E36: der Kernel hat keine Daten gemeldet (%s)" % lang)
        return rd[0], json.loads(line[-1][len("@@E36@@"):]), time.time() - t0
    finally:
        km.shutdown_kernel(now=True)
        shutil.rmtree(home, ignore_errors=True)


# ---------------------------------------------------------------------------
# P1 — die Lesefassung ohne Hülle
# ---------------------------------------------------------------------------
_TAG = re.compile(r"<(style|script)\b([^>]*)>", re.I)


def _blocks(h):
    """Jeder <style>/<script>-Block der obersten Ebene: (start, ende, art, attribute, inhalt).
    Blöcke INNERHALB eines Blocks (CSS-Kommentar „<style>“, Text in JS) zählen nicht."""
    out, i = [], 0
    while True:
        m = _TAG.search(h, i)
        if not m:
            return out
        kind = m.group(1).lower()
        end = h.find("</%s>" % kind, m.end())
        if end < 0:
            raise ValueError("E36: <%s> ohne Ende bei %d" % (kind, m.start()))
        out.append((m.start(), end + len(kind) + 3, kind, m.group(2), h[m.end():end]))
        i = end + len(kind) + 3


def is_data_script(attrs):
    return bool(re.search(r"type\s*=\s*['\"]application/json['\"]", attrs or "", re.I))


def split_huelle(h, nb_id, tkv):
    """→ (lesefassung, css-Stücke, js-Stücke). Die Hülle wird herausgenommen, sonst bleibt
    jedes Zeichen, wie der Kernel es geschrieben hat."""
    css, js, keep, last = [], [], [], 0
    for a, b, kind, attrs, body in _blocks(h):
        if kind == "script" and is_data_script(attrs):
            continue                                  # Daten des Dokuments: bleiben
        keep.append(h[last:a])
        last = b
        if kind == "style":
            css.append(body)
        else:
            js.append(body)
    keep.append(h[last:])
    doc = "".join(keep)
    # Version und Id wieder als Platzhalter (claude/VERTRAG-E36.md: 20-reader liest sie aus data-nbrw-v/-id,
    # die der Lader setzt) — die Hülle ist für alle Notebooks dieselbe
    js2 = []
    for s in js:
        s = s.replace("var V = '%s', ID = '%s'" % (tkv, nb_id), "var V = '__NBREADV__', ID = '__NBREADID__'")
        js2.append(s)
    return doc, css, js2


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _size(b):
    return {"bytes": len(b), "gzip": len(gzip.compress(b, 9, mtime=0)), "sha256": _sha(b)}


# ---------------------------------------------------------------------------
# P2 — daten.json, meta.json
# ---------------------------------------------------------------------------
_ATTR = re.compile(r"""\s([a-zA-Z_:][-a-zA-Z0-9_:.]*)(?:=(?:'([^']*)'|"([^"]*)"))?""")


def _attrs(tag):
    return {m.group(1): _html.unescape(m.group(2) if m.group(2) is not None else (m.group(3) or ""))
            for m in _ATTR.finditer(tag)}


def _b64json(s, z=False):
    b = base64.b64decode(s)
    return json.loads(zlib.decompress(b) if z else b)


def daten(doc, k, k_other=None):
    """Was das Paket an Daten trägt — aus dem Markup der Lesefassung (das, was 20-reader.js
    liest) und aus dem Kernel (Gating, Marken, Seed, Modus)."""
    calc, code, sliders = [], [], []
    for m in re.finditer(r"<div class='nbrw-task'[^>]*>", doc):
        a = _attrs(m.group(0))
        calc.append({"task": a.get("data-task", ""), "id": a.get("id", ""), "st": a.get("data-st", ""),
                     "antwort": _b64json(a["data-a"]) if a.get("data-a") else None})
    for m in re.finditer(r"<div class='nbrw-copy'[^>]*>", doc):
        a = _attrs(m.group(0))
        code.append({"task": a.get("data-task", ""), "id": a.get("id", ""), "st": a.get("data-st", ""),
                     "guard": a.get("data-guard", ""), "cname": a.get("data-cname", ""),
                     "pkgs": [p for p in a.get("data-pkgs", "").split(",") if p],
                     "pruef_code": base64.b64decode(a["data-check"]).decode("utf-8") if a.get("data-check") else ""})
    for i, m in enumerate(re.finditer(r"<div class='nbrw-slider'[^>]*>", doc)):
        a = _attrs(m.group(0))
        z = a.get("data-z", "")
        d = _b64json(z, z=True) if z else {"c": [], "f": []}
        sliders.append({"nr": i, "steuerung": d["c"], "bilder": len(d["f"]) or 1,
                        "z_bytes": len(z), "z_sha8": _sha(z.encode())[:8] if z else "",
                        "in": "lesefassung (data-z)" if z else "lesefassung (nur Startbild)"})
    titles = k.get("titles") or {}
    return {"format": "digichemjn-daten/1", "id": k["id"], "version": k["nb_version"], "toolkit": k["toolkit"],
            "seed": k["seed"], "modus": k["mode"], "sprache_des_laufs": k["lang"],
            "kapitel": k["gate"]["chap"], "kapitel_titel": {l: titles.get(l) or [] for l in LANGS}, "gating": {x: y for x, y in k["gate"].items() if x != "chap"}, "aufgaben": calc, "code": code, "regler": sliders,
            "marken": k["timeline"]}


def meta(k, md, files, huelle_rel):
    m = k.get("meta") or {}
    oer = {f: m.get(f) for f in ("title", "subtitle", "authors", "institution", "licence", "licence_url",
                                 "version", "date", "doi", "repo", "keywords", "audience", "prerequisites",
                                 "duration", "source", "objectives") if m.get(f) not in (None, "", [])}
    return {"format": "digichemjn-meta/1", "id": k["id"], "nb_version": k["nb_version"], "toolkit": k["toolkit"],
            "langs": list(LANGS), "lang": LANGS[0],
            "title": {"en": k.get("title"), "de": (md or {}).get("title_de") or k.get("title")},
            "huelle": huelle_rel, "seed": k["seed"], "modus": k["mode"], "oer": oer, "dateien": files,
            # E39a K2 — Katalog (Felder ergänzt, claude/VERTRAG-E36.md): aus dem Lauf, gleich der .ipynb
            "thema": m.get("thema"), "kurse": m.get("kurse") or []}


# ---------------------------------------------------------------------------
# P3 — die Ausgänge schreiben
# ---------------------------------------------------------------------------
def _write(path, b):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b)


PYODIDE_ENV = "DIGICHEM_PYODIDE_URL"
_PYV = re.compile(r"var PYV = '([0-9][0-9A-Za-z.]*)'")


def pyodide_url(js, env=None):
    """E38a P2 (2026-10-26, Python) — manifest.pyodide: where Python for the coding exercises comes from.
    Default: OUR server, relative to the site root, `/pyodide/<version>/` (the version the reader was
    written for: `var PYV = '…'` in 20-reader.js, read from the hull — one place to keep it). Set
    DIGICHEM_PYODIDE_URL to another address (absolute or relative; a missing final / is added), or to
    `off`/`none`/`null`/`0` for null: then the reader keeps its own default (jsDelivr) — only on purpose."""
    v = (os.environ if env is None else env).get(PYODIDE_ENV)
    if v is not None and v.strip().lower() in ("off", "none", "null", "0", "aus"):
        return None
    m = _PYV.search("\n".join(js) if isinstance(js, (list, tuple)) else (js or ""))
    if not m:
        raise RuntimeError("E38a P2: keine Pyodide-Version (var PYV = '…') im Lesefenster-Skript")
    u = (v or "").strip() or "/pyodide/%s/" % m.group(1)
    return u.replace("{v}", m.group(1)) if u.endswith("/") else u.replace("{v}", m.group(1)) + "/"


def write_huelle(root, tkv, css, js, lesen_html=None, lader_js=None):
    """claude/VERTRAG-E36.md: manifest {toolkit, css: [Lade-Reihenfolge], js: {lader, reader}, fonts, pyodide};
    lesen.html = toolkit/js/huelle/lesen.html.in mit __LADER__ → js.lader (einziger Name ohne Prüfsumme)."""
    d = os.path.join(root, "huelle", tkv)
    if os.path.isdir(d):
        shutil.rmtree(d)
    man = {"format": "digichemjn-huelle/1", "toolkit": tkv, "css": [], "js": {"lader": None, "reader": None},
           "fonts": [], "pyodide": pyodide_url(js), "dateien": {},
           "platzhalter": {"__NBREADV__": "data-nbrw-v", "__NBREADID__": "data-nbrw-id"}}
    def put(name, ext, b):
        fn = "%s.%s.%s" % (name, _sha(b)[:8], ext)
        _write(os.path.join(d, fn), b)
        man["dateien"][fn] = _size(b)
        return fn
    # E36 Zusammenführen (Hauptwerkstatt, claude/VERTRAG-E36.md „geändert von CSS“): als LETZTE die Seite von lesen.html
    # (toolkit/css/huelle/lesen.css, CSS C1: html/body Rand 0, Grund der Seite = Grund des Fensters; nicht in der .ipynb)
    _s = os.path.join(os.path.dirname(os.path.abspath(__file__)), "css", "huelle", "lesen.css")
    css = list(css) + ([open(_s, encoding="utf-8").read()] if os.path.exists(_s) else [])
    man["css"].append(put("leser", "css", "\n".join(css).encode("utf-8")))
    man["js"]["reader"] = put("reader", "js", "\n".join(js).encode("utf-8"))
    if lader_js and os.path.exists(lader_js):
        man["js"]["lader"] = put("lader", "js", open(lader_js, "rb").read())
    if lesen_html and os.path.exists(lesen_html):
        b = open(lesen_html, "rb").read()
        if man["js"]["lader"]:
            b = b.replace(b"__LADER__", man["js"]["lader"].encode())
        _write(os.path.join(d, "lesen.html"), b)
        man["dateien"]["lesen.html"] = _size(b)
    _write(os.path.join(d, "manifest.json"), json.dumps(man, ensure_ascii=False, indent=1).encode("utf-8"))
    return d, man


def ausgaenge(nb_path, md, dist="../dist", lesen_html="../toolkit/js/huelle/lesen.html.in",
              lader_js="../toolkit/js/huelle/lader.js", log=print):
    """Ausgang A neben der .ipynb: Hülle + Inhaltspaket. `md` = nb.metadata.digichemjn."""
    if not wanted():
        log("dist: übersprungen (%s=0)" % DIST_ENV)
        return None
    nb_id, nbv, tkv = md["id"], md["version"], md["toolkit"]
    runs, hull = {}, None
    for lang in LANGS:
        h, k, sec = run_cell(nb_path, lang)
        doc, css, js = split_huelle(h, nb_id, tkv)
        if hull is None:
            hull = (css, js)
        elif (css, js) != hull:
            raise RuntimeError("E36: die Hülle hängt von der Sprache ab (%s) — gehört nicht in die Hülle" % lang)
        runs[lang] = (doc, k, sec, h)
    out = os.path.join(dist, "inhalt", nb_id, nbv)
    if os.path.isdir(out):
        shutil.rmtree(out)
    files = {}
    for lang in LANGS:
        b = runs[lang][0].encode("utf-8")
        _write(os.path.join(out, "lesefassung.%s.html" % lang), b)
        files["lesefassung.%s.html" % lang] = _size(b)
    k_en = runs["en"][1]
    for lang in LANGS:                     # E39a K2: Lauf und .ipynb nennen dasselbe Thema, dieselben Kurse
        km = runs[lang][1].get("meta") or {}
        if (km.get("thema"), km.get("kurse") or []) != (md.get("thema"), md.get("kurse") or []):
            raise RuntimeError("E39a: thema/kurse im Lauf (%s) ≠ metadata.digichemjn" % lang)
    b = json.dumps(daten(runs["en"][0], k_en), ensure_ascii=False, indent=1).encode("utf-8")
    _write(os.path.join(out, "daten.json"), b)
    files["daten.json"] = _size(b)
    hd, man = write_huelle(dist, tkv, *hull, lesen_html=lesen_html, lader_js=lader_js)
    _write(os.path.join(dist, "inhalt", nb_id, "aktuell.json"), json.dumps({"v": nbv}).encode("utf-8"))
    rel = os.path.relpath(os.path.join(hd, "manifest.json"), out).replace(os.sep, "/")
    b = json.dumps(meta(k_en, md, files, rel), ensure_ascii=False, indent=1).encode("utf-8")
    _write(os.path.join(out, "meta.json"), b)
    files["meta.json"] = _size(b)
    import katalog                         # E39a K2: dist/kurse.json aus ALLEN Quellen (auch ohne eigenes Paket)
    katalog.write_kurse(dist)
    pk = sum(f["bytes"] for f in files.values()), sum(f["gzip"] for f in files.values())
    hk = sum(f["bytes"] for f in man["dateien"].values()), sum(f["gzip"] for f in man["dateien"].values())
    log("dist: inhalt/%s/%s %d B (gzip %d) · huelle/%s %d B (gzip %d) · Kernel %s"
        % (nb_id, nbv, pk[0], pk[1], tkv, hk[0], hk[1],
           " + ".join("%s %.1f s" % (l, runs[l][2]) for l in LANGS)))
    return {"inhalt": out, "huelle": hd, "dateien": files, "manifest": man,
            "roh": {l: runs[l][3] for l in LANGS},          # die Ausgabe des Kernels (Tests: Rückbau, Pixel)
            "sekunden": {l: runs[l][2] for l in LANGS}}
