"""E38 P3 (2026-10-27, Python) — THE CELL OF THE .ipynb SHOWS THE PACKAGE (build side).

Auftrag E38 P3: „Zelle 2 der .ipynb zeigt das mitgelieferte Paket (Hülle + Inhalt eingebettet, gepackt), statt das
Dokument neu zu bauen.“ Measured 27.10. (Dirigent, Vorlage v1.83, JupyterLab 4.6.4): Run All → cover 6,1–6,4 s; the
kernel built the whole document (ipywidgets, matplotlib, every figure) on every run. Python now builds it ONCE, here:

  einbauen(nb_path, md)
      1. the built .ipynb (short cell, E26.3) runs once per language in a fresh kernel (paket.run_cell: seed of
         the build, all pictures, DIGICHEM_LAB=1 → the Lab document, DIGICHEM_READ_PAGE=ipynb → the reading line
         for a notebook) — the reading version is the kernel's own output;
      2. that output is cut into a skeleton per language (the hull blocks — <style>, code <script> — replaced by
         \\x00<n>\\x00) and ONE list of blocks (the same for both languages, else the build stops);
      3. package = {id, v, toolkit, seed, lang, title, doc {en, de}, blocks, fonts_css (the hull's fonts, data:
         URLs — toolkit/fonts, E38 P1, if present), daten (daten.json of these runs: paket.daten)};
         (daten.json in the output: .nbreading > script[type=application/json][data-nbrw-daten], VERTRAG-E38-js)
      4. the cell gets ONE more line, `_NBP = "<zlib + base64>"` (a Python program: _NBP_DATA = … + the runtime
         toolkit/paketzelle_lauf.py), and its last line runs that program instead of the cargo. The cargo (_NBZ)
         stays: DIGICHEM_LAB=1 builds the Lab document as before (the build itself, the suites, py_e36 R1).
  The proof on every build: the program unpacks to itself, compiles, and its document for each language is
  the kernel's output character for character (the runtime's _nbp_html without fonts/daten).
The trust model stays: the saved output is the still preview (card_facts), no script until the cell runs."""
import base64, json, os, re, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(HERE, "paketzelle_lauf.py")
NBP = re.compile(r'^_NBP = "([A-Za-z0-9+/=]+)"$', re.M)
CALL = "_nbz_run(_NBZ, globals())"
EXEC = ('exec(compile(__import__("zlib").decompress(__import__("base64").b64decode(_NBP)).decode(), '
        '"<digichemjn:paket>", "exec"), globals())')
LANGS = ("en", "de")


def skeleton(h):
    """kernel output → (skeleton with \\x00n\\x00 for each hull block, [block texts])."""
    import paket
    out, blocks, last = [], [], 0
    for a, b, kind, attrs, body in paket._blocks(h):
        if kind == "script" and paket.is_data_script(attrs):
            continue
        out.append(h[last:a])
        out.append("\x00%d\x00" % len(blocks))
        blocks.append(h[a:b])
        last = b
    out.append(h[last:])
    return "".join(out), blocks


def fonts_css():
    """@font-face of the hull's fonts as data: URLs (E38 P1, toolkit/fonts) — "" without them."""
    import paket
    if not hasattr(paket, "fonts"):
        return ""
    out = []
    for fam, w, st, fn, b, lic, lb, q in paket.fonts():
        out.append(paket.font_face(fam, w, st, "data:font/woff2;base64," + base64.b64encode(b).decode("ascii")))
    return "".join(out)


def program(data):
    rt = open(RUNTIME, encoding="utf-8").read()
    return ("# DigiChemJN %s - the package of this notebook (E38 P3, toolkit/paketzelle.py)\n"
            "_NBP_DATA = %r\n%s\n_nbp_main(globals())\n" % (data.get("v"), data, rt))


def unpack(cell):
    m = NBP.search(cell)
    return zlib.decompress(base64.b64decode(m.group(1))).decode("utf-8") if m else None


def cell_with(cell, prog):
    """The short cell with the package line after the cargo and the last call running the package."""
    z = base64.b64encode(zlib.compress(prog.encode("utf-8"), 9)).decode("ascii")
    lines = cell.split("\n")
    i = next(n for n, l in enumerate(lines) if l.startswith("_NBZ = "))
    if lines[i] != lines[i].rstrip() or lines[i].endswith("("):
        raise SystemExit("paketzelle: the cargo is not one line (NB_CELL_CHUNK > 0 is not supported here)")
    if lines.count(CALL) != 1:
        raise SystemExit("paketzelle: the cell's last call %r not found once" % CALL)
    lines.insert(i + 1, '_NBP = "%s"' % z)
    lines[lines.index(CALL)] = EXEC
    new = "\n".join(lines)
    if unpack(new) != prog:
        raise SystemExit("paketzelle: the package does not unpack to the program")
    return new


def einbauen(nb_path, md, log=print):
    import paket
    nb = json.load(open(nb_path, encoding="utf-8"))
    ci = next(n for n, c in enumerate(nb["cells"]) if c["cell_type"] == "code")
    cell = "".join(nb["cells"][ci]["source"])
    if NBP.search(cell):
        raise SystemExit("paketzelle: the cell carries a package already")
    runs, blocks, sec = {}, None, {}
    for lang in LANGS:
        h, k, s = paket.run_cell(nb_path, lang, extra_env={"DIGICHEM_READ_PAGE": "ipynb"})
        sk, bl = skeleton(h)
        if blocks is None:
            blocks = bl
        elif bl != blocks:
            raise SystemExit("paketzelle: the hull blocks differ between the languages (%s)" % lang)
        runs[lang] = (sk, k, h)
        sec[lang] = s
    k_en = runs["en"][1]
    doc_en = paket.split_huelle(runs["en"][2], md["id"], md["toolkit"])[0]
    try:
        daten = paket.daten(doc_en, k_en, runs["de"][1])
    except TypeError:                                   # paket.daten without the second run (before E38 P2)
        daten = paket.daten(doc_en, k_en)
    data = {"format": "digichemjn-paketzelle/1", "id": md["id"], "v": md["version"], "toolkit": md["toolkit"],
            "seed": k_en.get("seed"), "lang": "en", "title": {"en": md.get("title"), "de": md.get("title_de")},
            "doc": {l: runs[l][0] for l in LANGS}, "blocks": blocks, "fonts_css": fonts_css(), "daten": daten}
    prog = program(data)
    compile(prog, "<digichemjn:paket>", "exec")
    # the proof: the runtime puts the kernel's output back together, character for character
    g = {"__name__": "_nbp_proof"}
    exec(compile(prog.replace("\n_nbp_main(globals())\n", "\n"), "<digichemjn:paket>", "exec"), g)
    for lang in LANGS:
        d0 = dict(data, fonts_css="", daten=None)
        if g["_nbp_html"](d0, lang) != runs[lang][2] + g["_NBP_RAHMEN"]:
            raise SystemExit("paketzelle: the package's %s document is not the kernel's output" % lang)
    new = cell_with(cell, prog)
    if not all(l.isascii() for l in new.split("\n") if not l.startswith("_NBZ = ")):
        raise SystemExit("paketzelle: the visible cell is not ASCII")
    nb["cells"][ci]["source"] = new.splitlines(keepends=True)
    nb["metadata"].setdefault("digichemjn", {})["cell"] = (
        "package cell (E38 P3): _NBP = zlib + base64 of the program that shows the built document "
        "(toolkit/paketzelle.py); _NBZ = the cargo, run with DIGICHEM_LAB=1 (toolkit/shortcell.py expand())")
    json.dump(nb, open(nb_path, "w"), ensure_ascii=False, indent=1)
    zb = len(NBP.search(new).group(1))
    log("package cell: %d chars package (program %d chars: documents %s, blocks %d, fonts %d, daten %d) · "
        "kernel %s · .ipynb %d bytes"
        % (zb, len(prog), "/".join("%d" % len(runs[l][0]) for l in LANGS), sum(len(b) for b in blocks),
           len(data["fonts_css"]), len(json.dumps(daten, ensure_ascii=False)),
           " + ".join("%s %.1f s" % (l, sec[l]) for l in LANGS), os.path.getsize(nb_path)))
    return {"zeichen": zb, "programm": len(prog), "datei": os.path.getsize(nb_path)}
