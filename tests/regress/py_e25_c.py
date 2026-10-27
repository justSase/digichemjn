"""E25.c · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_c.py <notebook.ipynb>
  THE START LINE OVER THE CELL, EVERYWHERE (E25.c, PyCharm Video 08.10.: the
  line "▶ Run the cell below" stood top right beside the tool bar). PyCharm
  cannot be driven here; Lesart: its Markdown view lays out an HTML block of
  its own (a <div> with inline style). Measured:
    S  the markdown cell, read by a CommonMark parser (markdown-it, as the
       front ends do): ONE paragraph, no HTML block, no inline style, both
       languages, the .nbstart / .nbtitle classes kept
    L  in a real JupyterLab, the file opened (nothing run): .nbstart is drawn,
       its box lies above the code cell, inside the markdown cell, no literal
       "**" (the Markdown inside was rendered), ≤ 60 px high
  v1.67: an HTML block (<div class="nbtitle nbstart" style=…>). Owner: Python.
exit 0 = REGRESS-PY-E25-C OK."""
import sys, os, json, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

LAB_JS = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); if (!P) return null;
  var s = P.querySelector('.jp-MarkdownCell .nbstart'), md = s && s.closest('.jp-MarkdownCell'), code = P.querySelector('.jp-CodeCell');
  if (!s) return {start: false};
  var b = s.getBoundingClientRect(), m = md.getBoundingClientRect(), c = code ? code.getBoundingClientRect() : null;
  return {start: true, w: Math.round(b.width), h: Math.round(b.height), top: Math.round(b.top), bottom: Math.round(b.bottom),
          mdTop: Math.round(m.top), mdBottom: Math.round(m.bottom), codeTop: c ? Math.round(c.top) : null,
          text: s.innerText.replace(/\s+/g, ' ').trim()}; }"""

def main():
    src = os.path.abspath([a for a in sys.argv[1:] if not a.startswith("--")][0])
    sys.argv = sys.argv[:1] + ["x"]
    rows, fails = [], []
    nb = json.load(open(src))
    mdc = [c for c in nb["cells"] if c["cell_type"] == "markdown"]
    if not mdc:
        fails.append("E25.c BAD no markdown cell")
    else:
        from markdown_it import MarkdownIt
        text = "".join(mdc[0]["source"])
        toks = MarkdownIt("commonmark").parse(text)
        top = [t.type for t in toks if t.level == 0]
        html = MarkdownIt("commonmark").render(text)
        rows.append("E25.c S top-level tokens %s · %d chars" % (top, len(text)))
        if "html_block" in top: fails.append("E25.c S the start line is an HTML block (%s)" % top)
        if top[:1] != ["paragraph_open"] or top.count("paragraph_open") != 1: fails.append("E25.c S not one paragraph: %s" % top)
        if "style=" in text: fails.append("E25.c S inline style in the start line")
        for w in ("Run the cell below", "Zelle darunter", "nbstart", "nbtitle"):
            if w not in html: fails.append("E25.c S missing %r" % w)
    from lab_keys import ensure_lab, CHROME, kill_sessions
    from playwright.sync_api import sync_playwright
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    name = "e25c_%d_%s" % (int(time.time() * 1000) % 10 ** 7, os.path.basename(src))
    shutil.copy(src, os.path.join(root, name))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
            pg.goto(base + "/lab/tree/" + name + "?reset")
            pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-MarkdownCell", state="attached", timeout=120000)
            pg.wait_for_timeout(3000)
            r = pg.evaluate(LAB_JS)
            if os.environ.get("E25C_SHOT"): pg.screenshot(path=os.environ["E25C_SHOT"])
            rows.append("E25.c L %s" % r)
            if not r or not r.get("start"): fails.append("E25.c L BAD no .nbstart in the markdown cell")
            else:
                if r["w"] < 50 or r["h"] < 8 or r["h"] > 60: fails.append("E25.c L the line is %dx%d px" % (r["w"], r["h"]))
                if r["codeTop"] is not None and r["bottom"] > r["codeTop"]: fails.append("E25.c L the line is not above the code cell")
                if r["top"] < r["mdTop"] - 1 or r["bottom"] > r["mdBottom"] + 1: fails.append("E25.c L the line is outside its cell")
                if "**" in r["text"] or "Run the cell below" not in r["text"]: fails.append("E25.c L text %r" % r["text"][:90])
            ctx.close()
        except Exception as e:
            fails.append("E25.c BAD %s" % str(e)[:200])
        finally:
            kill_sessions(base)
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E25-C OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
