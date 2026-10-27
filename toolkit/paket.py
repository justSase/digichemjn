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
      schriften.<sha8>.css         E38 P1: @font-face der Schriften von digi, ERSTE in manifest.css
      <schrift>.<sha8>.woff2, ofl-<familie>.<sha8>.txt   aus toolkit/fonts/ (manifest.fonts)
      manifest.json                {toolkit, css: [...], js: {lader, reader}, fonts, pyodide} + Bytes/gzip/sha256
                                   (pyodide: E38a P2, Standard "/pyodide/<PYV>/", DIGICHEM_PYODIDE_URL, "off" → null)
  dist/inhalt/<id>/<NB_VERSION>/   nur das Notebook-Eigene
      lesefassung.<lang>.html      die Lesefassung ohne Hülle (0 <style>, <script> nur
                                   type=application/json data-nbrw-put)
      daten.json                   Kapitel, Aufgaben + Antworten/Toleranzen, Code-Aufgaben +
                                   Prüf-Code, Regler (Steuerung; Bilder siehe unten), Gating,
                                   Marken der Zeitleiste, Seed und Modus des Baus; E38 P2: je Aufgabe Hinweise
                                   (Stufen en/de), Lösung, Überspringen, Toleranz je Schwierigkeit, Prüf-Code
                                   en/de; Schwierigkeitsstufen, Gating-Regeln, Sätze des Labs (aufgaben_regeln)
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
    "p4": _nbrw_live_all() if "_nbrw_live_all" in globals() else None,
    "toolkit": TOOLKIT_VERSION, "nb_version": NB_VERSION,
    "gate": _nbrw_gate(), "timeline": _e36_tl(),
    "titles": globals().get("_NBRW_TITLES") or {},
    "meta": {k: v for k, v in META.items()},
    "p2": _nbrw_daten() if "_nbrw_daten" in globals() else None,
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
               MPLBACKEND="module://matplotlib_inline.backend_inline",
               # E38 P3: die Zelle der Vorlage zeigt sonst das mitgelieferte Paket (toolkit/paketzelle.py) — der Bau
               # (und wer das Paket nachbaut: py_e36 R1) braucht das Dokument aus dem Kernel, den Weg des Labs
               DIGICHEM_LAB="1")
    return env


def run_cell(nb_path, lang, timeout=1200, extra_env=None):
    """Führt die Code-Zelle der gebauten .ipynb in einem frischen Kernel aus.
    → (Lesefassung als HTML, Daten des Kernels, Sekunden). extra_env (E38 P3): Variablen über _clean_env hinaus."""
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(nb_path, encoding="utf-8"))
    code = "".join(next(c for c in nb["cells"] if c["cell_type"] == "code")["source"])
    home = tempfile.mkdtemp(prefix="digichem-e36-")
    t0 = time.time()
    km, kc = start_new_kernel(kernel_name="python3", env=dict(_clean_env(home, lang), **(extra_env or {})), cwd=home)
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


def _fig0(doc, at):
    """Das Startbild eines Reglers ohne data-z: der Inhalt seines <div class='nbrw-fig'>."""
    i = doc.find("<div class='nbrw-fig'>", at)
    if i < 0:
        return ""
    i += len("<div class='nbrw-fig'>")
    j = doc.find("</div></div>", i)          # _nbrw_slider: fig + Ende des Reglers
    return doc[i:j] if j > 0 else ""


def live(f0, k):
    """E38 P4 (2026-10-27, Python) — das Render-Programm des Reglers (toolkit `_nbrw_live`), zugeordnet über sein
    Startbild (sha8 = erstes Bild in data-z). {code, fn, html, params, pkgs, dpi, spec, start} — code ist eigenständiges
    Python (numpy + matplotlib), `_nbrw_render(**werte)` (= html) → das Bild als HTML; `fn`/`params`/`_nbrw_svg` für den
    Leser (claude/VERTRAG-E38-js.md J3); spec = jede Steuerung mit vollem Bereich.
    Der Lauf des Baus gibt dieselben Bilder wie data-z (tests/regress/py_e38_p4.py). None = nicht gefunden,
    {"fehlt": [...]} = ein Name kann nicht reisen (dann bleibt das Fenster bei der Vorschaustufe)."""
    s8 = _sha(f0.encode("utf-8"))[:8] if f0 else None
    for p in k.get("p4") or []:
        if p.get("f0_sha8") == s8:
            return {x: y for x, y in p.items() if x != "f0_sha8"}
    fehlt = [p for p in k.get("p4") or [] if "fehlt" in p]
    return fehlt[0] if fehlt and len(fehlt) == len(k.get("p4") or []) else None


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
                        "in": "lesefassung (data-z)" if z else "lesefassung (nur Startbild)",
                        "live": live(d["f"][0] if d["f"] else _fig0(doc, m.end()), k)})
    titles = k.get("titles") or {}
    p2 = aufgaben_regeln(calc, code, k, k_other)
    return {"format": "digichemjn-daten/1", "id": k["id"], "version": k["nb_version"], "toolkit": k["toolkit"],
            "seed": k["seed"], "modus": k["mode"], "sprache_des_laufs": k["lang"],
            "kapitel": k["gate"]["chap"], "kapitel_titel": {l: titles.get(l) or [] for l in LANGS}, "gating": {x: y for x, y in k["gate"].items() if x != "chap"}, "aufgaben": calc, "code": code, "regler": sliders,
            "marken": k["timeline"], **p2}


def loesung(per_lang):
    """{en: {intro, code, warn}, de: …} → {intro: {en, de}, code: {en, de}, warn: {en, de}} (claude/VERTRAG-E38-js.md J1:
    loesung = {intro: Text, code: Text}, Text = {en, de}); None ohne Lösung."""
    if not any(per_lang.values()):
        return None
    return {f: {l: (s or {}).get(f, "") for l, s in per_lang.items()} for f in ("intro", "code", "warn")}


def aufgaben_regeln(calc, code, k, k_other=None):
    """E38 P2 (2026-10-27, Python) — was das Lab um eine Aufgabe herum tut, als Daten fürs Lesefenster (JS J1):
    je Aufgabe Hinweise (Stufen), Lösung, „Überspringen“, Toleranz je Schwierigkeit; je Code-Aufgabe Lösung,
    Überspringen, Prüf-Code in beiden Sprachen; dazu Schwierigkeitsstufen, Gating-Regeln und die Sätze des Labs.
    Quelle: toolkit/chapter_template.py `_nbrw_daten()` im Kernel des Baus, je Sprache ein Lauf (en = k, de = k_other)
    — dieselben Aufrufe (hint_steps, solution_box, skip_button, _DIFF), die die Lab-Knöpfe bauen. Die Werte gelten für
    den Seed des Baus wie die Antworten (daten.json "seed")."""
    runs = {"en": (k.get("p2") or {})}
    if k_other is not None:
        runs["de"] = k_other.get("p2") or {}
    if not runs["en"]:
        raise RuntimeError("E38 P2: der Kernel hat keine Aufgaben-Regeln gemeldet (_nbrw_daten fehlt)")
    en = runs["en"]
    by = lambda f: {l: f(r) for l, r in runs.items()}
    for t in calc:
        key = t["task"]
        t["hinweise"] = by(lambda r: (r.get("hinweise") or {}).get(key) or [])
        t["loesung"] = loesung(by(lambda r: ((r.get("loesungen") or {}).get("answer") or {}).get(key)))
        t["ueberspringen"] = key in ((en.get("ueberspringen") or {}).get("answer") or [])
        # claude/VERTRAG-E38-js.md J2: je Stufe die Toleranz je Feld (Zahlen, in der Reihenfolge der Felder von data-a);
        # welches Feld der Stufe folgt („stufe“) und welches seine eigene hat („eigen“): toleranz_felder
        tz = (en.get("toleranz") or {}).get(key) or {}
        t["toleranz"] = {lv: [f[1] for f in fl] for lv, fl in tz.items()}
        t["toleranz_felder"] = [[f[0], f[2]] for f in (tz.get("standard") or next(iter(tz.values()), []))]
    for c in code:
        key = c["task"]
        c["loesung"] = loesung(by(lambda r: ((r.get("loesungen") or {}).get("code") or {}).get(key)))
        c["ueberspringen"] = key in ((en.get("ueberspringen") or {}).get("code") or [])
        c["pruef"] = by(lambda r: (r.get("pruef_code") or {}).get(key))
    # Hinweise zu einer Aufgabe, die dieser Modus nicht als Rechenaufgabe baut (Modus code): bei der Code-Aufgabe
    have = {t["task"] for t in calc}
    for c in code:
        if c["task"] not in have:
            h = by(lambda r: (r.get("hinweise") or {}).get(c["task"]) or [])
            if any(h.values()):
                c["hinweise"] = h
    return {"schwierigkeit": en.get("schwierigkeit"), "regeln": en.get("regeln"),
            "texte": by(lambda r: r.get("texte") or {})}


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


# ---------------------------------------------------------------------------
# E38 P1 (2026-10-27, Python) — DIE SCHRIFTEN GEHÖREN ZUR HÜLLE.
# lesen.html zeigte Systemschriften: das Lab bringt Unbounded als data:-URL in 07-skins.css mit, die Hülle
# nichts (manifest.fonts = []). Jetzt liegen die drei Schriften von digi als woff2 (Lateinisch-Teilmenge von
# @fontsource 5.3.0 = Google Fonts; Unbounded 400 ist Byte für Byte die Schrift des Labs) in toolkit/fonts/
# und gehen beim Bau in die Hülle: je Datei `<stamm>.<sha8>.woff2`, die OFL je Familie als
# `ofl-<familie>.<sha8>.txt`, dazu `schriften.<sha8>.css` (@font-face, url relativ zur CSS-Datei) als ERSTE
# in manifest.css — der Lader lädt sie wie jede CSS (claude/VERTRAG-E36.md, Feld fonts ergänzt):
#   fonts: [{family, weight, style, file, unicode_range, bytes, sha8, lizenz, quelle}]
# Gewichte: 15-reader.css nutzt 400 und 600–800, kursiv einmal → Instrument Sans 400 + 700 (600/800 nimmt der
# Browser von 700, kursiv schräg gestellt), Unbounded 400 (Überschriften), JetBrains Mono 400. ≈ 75 KB.
# Lizenz: SIL Open Font License 1.1 — Einbetten und Weitergeben mit Software erlaubt, Namen unverändert,
# die Lizenz liegt bei (https://openfontlicense.org).
# ---------------------------------------------------------------------------
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,"
         "U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")       # @fontsource unicode.json "latin"
FONTS = (  # (Familie, Gewicht, Stil, Datei in toolkit/fonts/, Lizenz in toolkit/fonts/, Quelle)
    ("Unbounded", 400, "normal", "unbounded-latin-400-normal.woff2", "OFL-unbounded.txt", "@fontsource/unbounded 5.3.0"),
    ("Instrument Sans", 400, "normal", "instrument-sans-latin-400-normal.woff2", "OFL-instrument-sans.txt",
     "@fontsource/instrument-sans 5.3.0"),
    ("Instrument Sans", 700, "normal", "instrument-sans-latin-700-normal.woff2", "OFL-instrument-sans.txt",
     "@fontsource/instrument-sans 5.3.0"),
    ("JetBrains Mono", 400, "normal", "jetbrains-mono-latin-400-normal.woff2", "OFL-jetbrains-mono.txt",
     "@fontsource/jetbrains-mono 5.3.0"),
)


def font_face(family, weight, style, url):
    return ("@font-face{font-family:\"%s\";font-style:%s;font-weight:%d;font-display:swap;"
            "src:url(%s) format(\"woff2\");unicode-range:%s;}" % (family, style, weight, url, LATIN))


def fonts(src=None):
    """Die Schriften der Hülle aus toolkit/fonts/: [(Familie, Gewicht, Stil, Datei, woff2-Bytes, Lizenz, Lizenz-Bytes,
    Quelle)]. Fehlt eine Datei oder ist sie kein woff2: Abbruch (eine Hülle ohne Schrift fiele still auf Systemschriften)."""
    d = src or FONTS_DIR
    out = []
    for fam, w, st, fn, lic, q in FONTS:
        p, lp = os.path.join(d, fn), os.path.join(d, lic)
        if not os.path.isfile(p) or not os.path.isfile(lp):
            raise RuntimeError("E38 P1: Schrift oder Lizenz fehlt: %s / %s" % (p, lp))
        b = open(p, "rb").read()
        if b[:4] != b"wOF2":
            raise RuntimeError("E38 P1: %s ist kein woff2" % p)
        lb = open(lp, "rb").read()
        if b"SIL Open Font License" not in lb:
            raise RuntimeError("E38 P1: %s ist nicht die OFL" % lp)
        out.append((fam, w, st, fn, b, lic, lb, q))
    return out


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
    # E38 P1: die Schriften zuerst (woff2 + OFL mit sha8 im Namen, @font-face in schriften.<sha8>.css)
    faces, lics = [], {}
    for fam, w, st, fn, b, lic, lb, q in fonts():
        ff = put(fn[:-len(".woff2")], "woff2", b)
        if lic not in lics:
            lics[lic] = put(lic[:-len(".txt")].lower(), "txt", lb)
        faces.append(font_face(fam, w, st, ff))
        man["fonts"].append({"family": fam, "weight": w, "style": st, "file": ff, "unicode_range": LATIN,
                             "bytes": len(b), "sha8": _sha(b)[:8], "lizenz": lics[lic], "quelle": q})
    man["css"].append(put("schriften", "css", ("/* DigiChemJN — Schriften von digi (SIL Open Font License 1.1, "
                                               "Lizenzen: ofl-*.txt) */\n" + "\n".join(faces) + "\n").encode("utf-8")))
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
    b = json.dumps(daten(runs["en"][0], k_en, runs["de"][1]), ensure_ascii=False, indent=1).encode("utf-8")
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
