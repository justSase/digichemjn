"""E25.n · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_n.py <notebook.ipynb>
  FEEDBACK — THE TEXT. E29 P5 (Nutzer 12.10. zu v1.75) replaces E25.n: no
  form, no mailto:, no error list sent — one line of text, en and de, with the
  contact address of E21.13. A real kernel (its own HOME), en and de; in the
  ⚙ drawer (.nbfb, an HTML widget's value):
    .nbfb-text       "Feedback, errors and contact: by e-mail to <address>" /
                     "Feedback, Fehler und Kontakt: per E-Mail an <address>",
                     the address in .nbfb-to
    gone             data-nbfeedback, a.nbfb-link, any mailto:
  (behauptete bisher, E25.n: JSON data-nbfeedback + a mailto: link with
  subject/body templates — exactly what E29 P5 takes out.) The cover's line:
  py_e29 P5. v1.75: red (link + JSON). Owner: Python.
exit 0 = REGRESS-PY-E25-N OK."""
import sys, os, re, json, shutil, tempfile, html as _h
from urllib.parse import urlsplit, parse_qs
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
TO = "samuel.wiese@gmx.de"

def drawer(src, lang):
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(src))
    code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    tmp = tempfile.mkdtemp(prefix="e25n_")
    env = {k: v for k, v in os.environ.items() if not k.startswith("DIGICHEM_") and k != "PYCHARM_HOSTED"}
    env.update(HOME=tmp, DIGICHEM_LANG=lang)
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=tmp)
    got = None
    try:
        kc.execute(code)
        while True:
            m = kc.get_iopub_msg(timeout=600)
            t, c = m["msg_type"], m["content"]
            if t in ("comm_open", "comm_msg"):
                v = ((c.get("data") or {}).get("state") or {}).get("value")
                if isinstance(v, str) and 'class="nbcell pg-fb nbfb' in v:
                    got = v
            elif t == "status" and c["execution_state"] == "idle" and m["parent_header"].get("msg_type") == "execute_request":
                break
    finally:
        km.shutdown_kernel(now=True); shutil.rmtree(tmp, ignore_errors=True)
    return got

def main():
    src = os.path.abspath([a for a in sys.argv[1:] if not a.startswith("--")][0])
    rows, fails = [], []
    for lang, want in (("en", "Feedback, errors and contact: by e-mail to"),
                       ("de", "Feedback, Fehler und Kontakt: per E-Mail an")):
        v = drawer(src, lang)
        if not v:
            fails.append("E25.n %s: no feedback cell (.nbfb) in the ⚙ drawer" % lang); continue
        m = re.search(r'<div class="nbcell pg-fb nbfb[^"]*"[^>]*>.*?</div></div>', v, re.S)
        cell = m.group(0) if m else ""
        txt = re.sub(r"<[^>]+>", "", _h.unescape(cell))
        rows.append("E25.n %s: %r · mailto %d · data-nbfeedback %s" % (lang, txt[:120], cell.count("mailto:"), "data-nbfeedback" in cell))
        if want not in txt or TO not in txt or 'class="nbfb-to"' not in cell:
            fails.append("E25.n %s: the line %r" % (lang, txt[:120]))
        if "mailto:" in cell or "data-nbfeedback" in cell or "nbfb-link" in cell:
            fails.append("E25.n %s: still a mailto/JSON/link in the cell" % lang)
    print("\n".join(rows))
    print("REGRESS-PY-E25-N OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
