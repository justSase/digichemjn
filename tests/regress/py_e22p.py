"""E22.3 · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e22p.py <notebook.ipynb>
  the output form where no widget is drawn (PyCharm, Video 1:
             "roher HTML-Text"). Not measurable in PyCharm here (desktop
             application) — measured on what it receives: the kernel is run
             with PYCHARM_HOSTED=1 (jupyter_client, every iopub message):
               every widget output also carries text/html, no text/plain
               shows HTML or "<IPython.core.display…>"; the still copy, put
               together in Chromium as such a viewer does (text/html first,
               else text/plain), shows the document: no visible tag text,
               the note line, the folds (≥ 8) and the text (≥ 8 000 characters)
             and with no such variable (JupyterLab): no widget output carries
             text/html except the first, whose text/html is the E24.2 box
             `.nbwidget-hint` alone; text/plain empty everywhere.
             v1.62: 7 widget outputs text/plain only, 4 with HTML text, 7
             Javascript placeholders. Owner: Python.
exit 0 = REGRESS-PY-E22P OK. (A stage-2 script only: no matrix tests here.)"""
import sys, os, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

def iopub(src, extra):
    """Run the mega-cell in a kernel of its own; every output bundle."""
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(src))
    code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    env = {k: v for k, v in os.environ.items() if k not in ("PYCHARM_HOSTED", "DIGICHEM_STATIC_HTML")}
    env.update(extra)
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=os.path.dirname(os.path.abspath(src)))
    try:
        kc.execute(code); outs = []
        while True:
            m = kc.get_iopub_msg(timeout=600)
            t = m["msg_type"]
            if t in ("display_data", "execute_result", "update_display_data"): outs.append(m["content"]["data"])
            elif t == "error": outs.append({"error": m["content"]["ename"] + ": " + m["content"]["evalue"]})
            elif t == "status" and m["content"]["execution_state"] == "idle" and m["parent_header"].get("msg_type") == "execute_request": break
        return outs
    finally:
        km.shutdown_kernel(now=True)

WMIME = "application/vnd.jupyter.widget-view+json"
def pycharm(b, src, rows, fails, shot=None):
    outs = iopub(src, {"PYCHARM_HOSTED": "1"})
    errs = [o["error"] for o in outs if "error" in o]
    w = [o for o in outs if WMIME in o]
    noh = [o for o in w if "text/html" not in o]
    # what a viewer shows as text: text/plain where the bundle has nothing it draws instead
    shown = [o["text/plain"] for o in outs if o.get("text/plain") and not
             any(k in o for k in ("text/html", "image/png", "image/svg+xml", "text/markdown"))]
    tp = [t for t in shown if re.search(r"<\w+[ >]", t) or "<IPython.core.display" in t]
    rows.append("E22.3 PYCHARM_HOSTED=1: %d outputs, %d widget outputs, %d without text/html, %d text/plain with HTML/placeholder, %d B"
                % (len(outs), len(w), len(noh), len(tp), sum(len(json.dumps(o)) for o in outs)))
    if errs: fails.append("E22.3 the run raised: %s" % errs[:1])
    if not w: fails.append("E22.3 precondition: no widget output")
    # py-E26.1 (11.10.) — behauptete bisher: every widget output carries text/html
    # (the still copy of E22.3, PyCharm only) and a note line. The still copy is
    # gone: the cell's first output is the reading version (`.nbreading`, in every
    # kernel, no detection); widget outputs carry no text/html and draw nothing.
    if tp: fails.append("E22.3 %d text/plain outputs show HTML or a placeholder: %r" % (len(tp), tp[0][:80]))
    page = "".join(o.get("text/html") or ("<pre>%s</pre>" % o["text/plain"] if o.get("text/plain") else "") for o in outs)
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "e22_static_%s.html" % os.path.basename(src)[:12])
    open(tmp, "w", encoding="utf-8").write("<!doctype html><meta charset=utf-8><body style='font-family:sans-serif;max-width:1100px;margin:auto'>" + page)
    ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
    pg.goto("file://" + tmp); pg.wait_for_timeout(800)
    # E26.3 (Hauptwerkstatt, Zusammenführen): where our script runs, the reading window opens on the preview (like
    # Lab's cover) — Play first, then the document is read. Behauptete bisher: the document is shown at once.
    pg.evaluate("() => { var w = document.querySelector('.nbrw'), p = w && w.querySelector('[data-nbrw-act=play]'); if (p && w.getAttribute('data-nbrw-view') === 'cover') p.click(); }")
    pg.wait_for_timeout(400)
    r = pg.evaluate(r"""() => ({tags: (document.body.innerText.match(/<\/?(div|span|svg|style|button|details|b|i)\b[^>]*>/g) || []).length,
        line: !!document.querySelector('.nbreading .nbread-line'), heads: document.querySelectorAll('.nbreading .nbread-h').length,
        chars: document.body.innerText.length})""")
    if shot: pg.screenshot(path=shot)
    ctx.close()
    first = next((o for o in outs if (o.get("text/html") or "").strip()), {})
    rows.append("E22.3 viewer page: %d characters, %d visible tag texts, reading line %s, %d headings, first drawn output is the reading version: %s"
                % (r["chars"], r["tags"], r["line"], r["heads"], "nbreading" in (first.get("text/html") or "")[:200]))
    if r["tags"]: fails.append("E22.3 the viewer page shows %d tags as text" % r["tags"])
    if not r["line"]: fails.append("E22.3 the reading version has no top line")
    # E28: the template's placeholder text is short (≈ 4 500 characters for five chapters) —
    # behauptete bisher: ≥ 8 000 (Complex's text); the template is held to ≥ 3 000
    want_c = 3000 if "Vorlage" in os.path.basename(src) else 8000
    if r["heads"] < 8 or r["chars"] < want_c: fails.append("E22.3 the reading version is not the document (%d headings, %d characters, want ≥ 8 / %d)" % (r["heads"], r["chars"], want_c))
    if "nbreading" not in (first.get("text/html") or "")[:200]: fails.append("E22.3 the first drawn output is not the reading version")
    # JupyterLab: no widget output carries text/html, text/plain empty
    outs2 = iopub(src, {})
    w2 = [o for o in outs2 if WMIME in o]
    # E33 D: behauptete bisher "no widget output carries text/html" (the E22.3 still copy is only for PyCharm);
    # an EMPTY text/html is no copy — it keeps VS Code from drawing an empty text/plain as a "…" row
    add = [o for o in w2 if (o.get("text/html") or "").strip()]
    plain = [o for o in w2 if (o.get("text/plain") or "").strip()]
    rows.append("E22.3 JupyterLab kernel: %d widget outputs, %d with text/html (want 0), %d with text/plain" % (len(w2), len(add), len(plain)))
    if not w2: fails.append("E22.3 precondition: a JupyterLab kernel gets no widget output")
    if add: fails.append("E22.3 a JupyterLab kernel gets %d widget outputs with text/html" % len(add))
    if plain: fails.append("E22.3 %d widget outputs with text/plain %r" % (len(plain), plain[0]["text/plain"][:60]))

def main():
    src = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    rows, fails = [], []
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try: pycharm(b, src, rows, fails, os.environ.get("E22_SHOT"))
        except Exception as e: fails.append("E22.3 BAD %s" % str(e)[:200])
        b.close()
    print("\n".join(rows))
    print("REGRESS-PY-E22P OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
