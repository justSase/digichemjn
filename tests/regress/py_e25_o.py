"""E25.o · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_o.py <notebook.ipynb>
  STANDARD FIRST, AND EACH NOTEBOOK ITS OWN (E25.o, Nutzer 08.10.: "jedes
  Notebook merkt sich seine eigenen Einstellungen … übernimmt nichts aus
  anderen Notebooks"). The kernel's side of it — the language a run is built
  in. A real kernel (jupyter_client, its own HOME, a copy of the notebook in
  a folder of its own); the run's feed (.nbfeed, an HTML widget's value)
  says what was built (data-nblang) and the standard values (data-nbdefaults):
    nothing stored                                      → en
    the OLD shared file ~/.digichemjn/lang = de         → en  (taken from no one)
    ANOTHER notebook's ~/.digichemjn/<other>.lang = de  → en
    THIS notebook's ~/.digichemjn/<id>.lang = de        → de
    THIS notebook's file beside the notebook = de       → de
  and data-nbdefaults = {skin digi, theme dark, lang en, mode both, …}
  (E34 P1/P2, 19.10.: the standard is digi, dark; before: minimal, auto).
  v1.67: the shared file turns every notebook German, its own file is not
  read. Owner: Python.
exit 0 = REGRESS-PY-E25-O OK."""
import sys, os, re, json, shutil, tempfile, html as _h
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

def feed(src, home, nbdir):
    """Run the mega-cell; the feed attributes from the widget states."""
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(src))
    code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    env = {k: v for k, v in os.environ.items() if not k.startswith("DIGICHEM_") and k != "PYCHARM_HOSTED"}
    env["HOME"] = home
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=nbdir)
    found = {}
    try:
        kc.execute(code)
        while True:
            m = kc.get_iopub_msg(timeout=600)
            t, c = m["msg_type"], m["content"]
            if t in ("comm_open", "comm_msg"):
                st = (c.get("data") or {}).get("state") or {}
                v = st.get("value")
                if isinstance(v, str) and 'class="nbfeed"' in v:
                    for a in ("data-nblang", "data-nbdefaults", "data-nbid"):
                        mm = re.search(a + r"""=(["'])(.*?)\1""", v)
                        if mm: found[a] = _h.unescape(mm.group(2))
            elif t == "error":
                found["error"] = c["ename"] + ": " + c["evalue"]
            elif t == "status" and c["execution_state"] == "idle" and m["parent_header"].get("msg_type") == "execute_request":
                break
    finally:
        km.shutdown_kernel(now=True)
    return found

def main():
    src = os.path.abspath([a for a in sys.argv[1:] if not a.startswith("--")][0])
    nid = re.search(r"nbid-([a-z0-9-]+)", open(src).read()).group(1)
    other = "intro-modeling" if nid != "intro-modeling" else "complex-numbers"
    rows, fails = [], []
    cases = [("nothing stored", {}, "en"),
             ("old shared ~/.digichemjn/lang = de", {"home/lang": "de"}, "en"),
             ("other notebook ~/.digichemjn/%s.lang = de" % other, {"home/%s.lang" % other: "de"}, "en"),
             ("this notebook ~/.digichemjn/%s.lang = de" % nid, {"home/%s.lang" % nid: "de"}, "de"),
             ("this notebook beside the file .digichemjn/%s.lang = de" % nid, {"here/%s.lang" % nid: "de"}, "de")]
    for name, files, want in cases:
        tmp = tempfile.mkdtemp(prefix="e25o_")
        home, nbdir = os.path.join(tmp, "home"), os.path.join(tmp, "nb")
        for d in (home, nbdir): os.makedirs(os.path.join(d, ".digichemjn"))
        shutil.copy(src, nbdir)
        for k, v in files.items():
            where, fn = k.split("/", 1)
            open(os.path.join(home if where == "home" else nbdir, ".digichemjn", fn), "w").write(v)
        try:
            f = feed(src, home, nbdir)
        except Exception as e:
            f = {"error": "BAD %s" % str(e)[:160]}
        rows.append("E25.o %-55s built %s (want %s)%s" % (name, f.get("data-nblang"), want, "  " + f["error"] if "error" in f else ""))
        if "error" in f: fails.append("E25.o %s: the run raised %s" % (name, f["error"]))
        elif not f.get("data-nbid"): fails.append("E25.o BAD %s: no feed in the widget states" % name)
        elif (f.get("data-nblang") or "en") != want: fails.append("E25.o %s: built %s, want %s" % (name, f.get("data-nblang"), want))
        if name == "nothing stored":
            try:
                d = json.loads(f.get("data-nbdefaults") or "")
                rows.append("E25.o standard values: %s" % d)
                w = {"skin": "digi", "theme": "dark", "lang": "en", "mode": "both"}   # E34
                bad = {k: d.get(k) for k in w if d.get(k) != w[k]}
                if bad: fails.append("E25.o standard values differ: %s" % bad)
            except Exception:
                fails.append("E25.o no standard values on the feed (data-nbdefaults %r)" % (f.get("data-nbdefaults") or "")[:60])
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n".join(rows))
    print("REGRESS-PY-E25-O OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
