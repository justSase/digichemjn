"""E35 P2 · Python — THE SAVED PREVIEW IN digi (Werkstatt Python, 2026-10-19; AUFTRAG E35 P1, Nutzer 19.10.:
„Die Vorschau soll auch den digi-Stil haben, es soll alles bündig aussehen, als wäre es Teil der digi App").
    python3 tests/regress/py_e35.py [--nb vorlage|<file.ipynb>] [--no-lab] [--shots DIR] [--json out.json]

The BUILT file (not run) carries one saved output, the still preview `.nbstill` (E33 A2). It is what GitHub,
nbviewer, Lab/PyCharm/VS Code before the first run and the digi app's preview show — no CSS of ours reaches it.
  K1  the toolkit's NB_DEFAULTS: skin = digi, theme = dark (E34 stays)
  S1  the file (static): exactly one .nbstill output; card background #0b0e1c (digi dark surface), kicker gold
      #ffd36b, every colour in its style attributes from the digi-dark palette, the title's font-family starts with
      Unbounded and falls back to system-ui … sans-serif; nothing a sanitizer drops (<style>, <script>, <svg>,
      var(), data-*, <button>)
  B1  Chromium, the preview through a JupyterLab-like sanitizer on four pages — white (#fff: GitHub, nbviewer, Lab
      light), digi page (#04050b), Lab dark (#111), GitHub dark (#0d1117): painted card = rgb(11,14,28), kicker
      rgb(255,211,107), the run pill gold, title font Unbounded first; every visible text ≥ 4.5 on its painted ground
  B2  real JupyterLab, file NOT trusted, light + dark, and nbconvert HTML (the GitHub/nbviewer stand-in, no script):
      the same card, kicker gold, contrast ≥ 4.5, "Run this cell to start" visible
v1.80: red (S1 card #f6f8fa, grey kicker, no Unbounded; B1/B2 card rgb(246,248,250)); K1 green (guard).
Owner: Python. exit 0 = REGRESS-PY-E35 OK."""
import sys, os, re, json, shutil, subprocess, tempfile, ast
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import py_e33 as E33   # sanitize, MEASURE, start_lab, open_nb (its main() runs only as a script)

A = sys.argv[1:]
NOLAB = "--no-lab" in A
SHOTS = A[A.index("--shots") + 1] if "--shots" in A else None
JOUT = A[A.index("--json") + 1] if "--json" in A else None

# digi dark (toolkit/css/07-skins.css, body.nbdark.nbskin-digi): surface, ink, quiet, gold, pill ink, line
PALETTE = {"#0b0e1c", "#e9ecf6", "#c3c9de", "#ffd36b", "#141826", "#3a4166"}
CARD, GOLD = "rgb(11, 14, 28)", "rgb(255, 211, 107)"
PAGES = {"white": "#ffffff", "digi": "#04050b", "labdark": "#111111", "ghdark": "#0d1117"}

rows, fails = [], []
def row(name, ok, detail):
    rows.append((name, bool(ok), detail))
    if not ok: fails.append("%s: %s" % (name, detail))
    print("%-30s %s  %s" % (name, "ok " if ok else "RED", detail), flush=True)

def shot(pg, name):
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, name))

def nb_defaults():
    src = open(os.path.join(ROOT, "toolkit", "chapter_template.py"), encoding="utf-8").read()
    m = re.search(r"^NB_DEFAULTS = (\{.*?\})\s*$", src, re.S | re.M)
    return ast.literal_eval(m.group(1)) if m else {}

PROBE = r"""() => {
  var c = document.querySelector('.nbstill'); if (!c) return {none: true};
  var cs = function(e){ return e ? getComputedStyle(e) : {}; };
  var kick = c.firstElementChild, title = kick && kick.nextElementSibling, pill = c.querySelector('.nbstill-run');
  var r = c.getBoundingClientRect();
  return {card: cs(c).backgroundColor, kick: cs(kick).color, kickText: kick ? kick.textContent : '',
          titleFont: cs(title).fontFamily, pill: cs(pill).backgroundColor, pillInk: cs(pill).color,
          w: Math.round(r.width), h: Math.round(r.height)}; }"""

def judge_card(name, r, m):
    ok = (not r.get("none") and r["card"] == CARD and r["kick"] == GOLD and r["pill"] == GOLD
          and r["titleFont"].startswith("Unbounded") and m["low"] == 0 and m["n"] > 0 and not m["miss"])
    row(name, ok, "card %s · kicker %s · pill %s · title font %s · contrast min %.2f (%d below 4.5 %s) · %d texts · missing %s"
        % (r.get("card"), r.get("kick"), r.get("pill"), (r.get("titleFont") or "")[:24], m["minC"], m["low"], m["lowEx"][:3],
           m["n"], m["miss"]))

def main():
    import nbpick
    built = os.path.abspath(nbpick.from_argv(sys.argv))
    print("notebook:", built)
    d = nb_defaults()
    row("K1 NB_DEFAULTS digi + dark", d.get("skin") == "digi" and d.get("theme") == "dark", "NB_DEFAULTS %s" % d)

    nb = json.load(open(built, encoding="utf-8"))
    outs = [o for c in nb["cells"] if c.get("cell_type") == "code" for o in c.get("outputs", [])]
    st = ["".join(o.get("data", {}).get("text/html", "")) for o in outs]
    st = [h for h in st if 'class="nbstill"' in h]
    h = st[0] if st else ""
    cols = set(x.lower() for x in re.findall(r"#[0-9a-fA-F]{6}\b", " ".join(re.findall(r'style="([^"]*)"', h))))
    m0 = re.match(r'<div class="nbstill" style="([^"]*)"', h)
    s0 = m0.group(1) if m0 else ""
    m1 = re.search(r'<div style="([^"]*)">Preview', h)
    ft = re.search(r"font-family:(Unbounded[^;\"]*)", h)
    bad = [k for k, rx in (("style", r"<style"), ("script", r"<script"), ("svg", r"<svg"), ("var()", r"var\("),
                           ("data-*", r"\sdata-[a-z]"), ("button", r"<button")) if re.search(rx, h, re.I)]
    row("S1 file: still in digi", len(st) == 1 and "background:#0b0e1c" in s0 and m1 and "color:#ffd36b" in m1.group(1)
        and not (cols - PALETTE) and ft and "system-ui" in ft.group(1) and ft.group(1).rstrip().endswith("sans-serif") and not bad,
        "outputs %d · card %s · kicker %s · colours outside the palette %s · title font %s · forbidden %s"
        % (len(st), (re.search(r"background:(#\w+)", s0) or [None, "-"])[1],
           (re.search(r"color:(#\w+)", m1.group(1)) or [None, "-"])[1] if m1 else "-", sorted(cols - PALETTE),
           ft.group(1)[:40] if ft else "-", bad))
    if not h:
        return finish()
    title = re.sub(r"<[^>]+>", "", (re.search(r"font-size:28px[^>]*>(.*?)</div>|font-size:30px[^>]*>(.*?)</div>", h) or [""])[0]).strip()

    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        clean = E33.sanitize(h)
        for name, bg in PAGES.items():
            ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
            pg.set_content("<!doctype html><meta charset=utf-8><body style='margin:0;padding:24px;background:%s;"
                           "color:%s;font:14px sans-serif'>%s</body>" % (bg, "#1f2328" if bg == "#ffffff" else "#dfe1e5", clean))
            pg.wait_for_timeout(300)
            r = pg.evaluate(PROBE)
            m = pg.evaluate(E33.MEASURE, [[], "rgb(%d,%d,%d)" % tuple(int(bg[i:i + 2], 16) for i in (1, 3, 5)), ".nbstill",
                                          ["Run this cell to start"]])
            shot(pg, "py-E35-B1-%s.png" % name)
            judge_card("B1 page %s" % name, r, m)
            ctx.close()

        tmp = tempfile.mkdtemp(prefix="e35_")
        if not NOLAB:
            root = os.path.join(tmp, "root"); os.makedirs(root)
            shutil.copy(built, os.path.join(root, "built.ipynb"))
            for theme in ("light", "dark"):
                proc, base = E33.start_lab(root, theme)
                try:
                    ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme=theme); pg = ctx.new_page()
                    tr = E33.open_nb(pg, base + "/lab/tree/built.ipynb")
                    sel = ".jp-NotebookPanel:not(.lm-mod-hidden) .jp-OutputArea-output"
                    r = pg.evaluate(PROBE)
                    m = pg.evaluate(E33.MEASURE, [[], E33.LAB_BG[theme], sel, ["Run this cell to start"]])
                    shot(pg, "py-E35-B2-lab-%s.png" % theme)
                    judge_card("B2 Lab %s not trusted%s" % (theme, "" if not tr else " (TRUSTED %d)" % tr), r, m)
                    ctx.close()
                finally:
                    proc.terminate()
        out = os.path.join(tmp, "built.html")
        subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", built, "--output", out], capture_output=True)
        ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
        pg.route("**/*", lambda rt: rt.abort() if rt.request.resource_type == "script" else rt.continue_())
        pg.goto("file://" + out); pg.wait_for_timeout(800)
        r = pg.evaluate(PROBE)
        m = pg.evaluate(E33.MEASURE, [[], "rgb(255,255,255)", ".jp-OutputArea-output, .output_area", ["Run this cell to start"]])
        shot(pg, "py-E35-B2-nbconvert.png")
        judge_card("B2 nbconvert", r, m)
        ctx.close(); b.close()
    finish()

def finish():
    if JOUT: json.dump([{"row": n, "ok": ok, "detail": d} for n, ok, d in rows], open(JOUT, "w"), ensure_ascii=False, indent=1)
    print("REGRESS-PY-E35 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
