"""E25.v · test_regress, stage 2 (scripts.txt) — Python workshop.
    python3 tests/regress/py_e25_v.py <notebook.ipynb> [--py38=PY --py39=PY --py310=PY --w7=PY]
  VERSIONS, CHECKED AND SAID (E25 Versionsprüfung + Mindest-Python; Nutzer
  08.10.: an old venv, Python 3.9, did not start; "kann eine zu alte Version
  auch woanders vorkommen?"). Each PY is the python of an environment with
  ipykernel; not given, the script builds it with uv (cached in
  ~/.cache/digichem-e25v): 3.8 with ipykernel only; 3.9 and 3.10 with numpy,
  matplotlib, ipywidgets 8, jupyterquiz; w7 = 3.10 with ipywidgets 7. The mega-cell runs in a kernel of that python (a kernelspec
  of its own), every output collected:
    3.8   one box .nbboot-old.nbboot-fail naming Python 3.8 and the way (en+de),
          the run stops there: no traceback, no document (no feed)
    3.9   no box (E33 A3, Nutzer 13.10.: the note stood above the document — behauptete
          bisher "a note .nbboot-old naming 3.9"; now one line on the kernel's console,
          py_e33.py A3), the document is built (feed)
    w7    a note .nbboot-old naming ipywidgets 7, the document is built
    3.10  no note, the document is built
  An environment that is not given is NOT RUN (= red). v1.67: no box, no note
  anywhere. Owner: Python (kernel side; the front end and the browser: JS).
exit 0 = REGRESS-PY-E25-V OK."""
import sys, os, re, json, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))

def run(src, py):
    from jupyter_client.manager import KernelManager
    from jupyter_client.kernelspec import KernelSpecManager
    nb = json.load(open(src))
    code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    tmp = tempfile.mkdtemp(prefix="e25v_")
    kd = os.path.join(tmp, "kernels", "k")
    os.makedirs(kd)
    json.dump({"argv": [py, "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "k", "language": "python"},
              open(os.path.join(kd, "kernel.json"), "w"))
    ksm = KernelSpecManager(kernel_dirs=[os.path.join(tmp, "kernels")])
    env = {k: v for k, v in os.environ.items() if not k.startswith(("DIGICHEM_", "PYTHON", "VIRTUAL_ENV")) and k != "PYCHARM_HOSTED"}
    env["HOME"] = tmp
    km = KernelManager(kernel_name="k", kernel_spec_manager=ksm)
    km.start_kernel(env=env, cwd=tmp)
    kc = km.client(); kc.start_channels(); kc.wait_for_ready(timeout=120)
    html, errs, feed = [], [], False
    try:
        kc.execute(code)
        while True:
            m = kc.get_iopub_msg(timeout=900)
            t, c = m["msg_type"], m["content"]
            if t in ("display_data", "execute_result", "update_display_data"):
                h = (c.get("data") or {}).get("text/html")
                if h: html.append(h)
            elif t in ("comm_open", "comm_msg"):
                v = ((c.get("data") or {}).get("state") or {}).get("value")
                if isinstance(v, str) and 'class="nbfeed"' in v: feed = True
            elif t == "error":
                errs.append(c["ename"] + ": " + c["evalue"][:80])
            elif t == "status" and c["execution_state"] == "idle" and m["parent_header"].get("msg_type") == "execute_request":
                break
    finally:
        kc.stop_channels(); km.shutdown_kernel(now=True); shutil.rmtree(tmp, ignore_errors=True)
    old = [h for h in html if 'class="nbboot-old' in h]
    return {"old": old, "fail": [h for h in old if "nbboot-fail" in h], "errs": errs, "feed": feed}

ENVS = {"py38": ("3.8", ["ipykernel"]),
        "py39": ("3.9", ["ipykernel", "numpy", "matplotlib", "ipywidgets>=8", "jupyterquiz"]),
        "py310": ("3.10", ["ipykernel", "numpy", "matplotlib", "ipywidgets>=8", "jupyterquiz"]),
        "w7": ("3.10", ["ipykernel", "numpy", "matplotlib", "ipywidgets<8", "jupyterquiz"])}

def make_env(key):
    """Without --<key>=PY: build the environment with uv (cached)."""
    import subprocess
    ver, pkgs = ENVS[key]
    d = os.path.join(os.path.expanduser("~"), ".cache", "digichem-e25v", key)
    py = os.path.join(d, "bin", "python")
    if os.path.exists(py):
        return py
    uv = shutil.which("uv")
    if not uv:
        return None
    subprocess.run([uv, "python", "install", ver], capture_output=True, timeout=600)
    subprocess.run([uv, "venv", "-q", "-p", ver, d], capture_output=True, timeout=300)
    subprocess.run([uv, "pip", "install", "-q"] + pkgs, capture_output=True, timeout=900, env=dict(os.environ, VIRTUAL_ENV=d))
    return py if os.path.exists(py) else None

def main():
    src = os.path.abspath([a for a in sys.argv[1:] if not a.startswith("--")][0])
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    rows, fails = [], []
    def txt(hs): return re.sub(r"<[^>]+>", " ", " ".join(hs))
    for key, want in (("py38", "fail"), ("py39", "none"), ("w7", "note-w"), ("py310", "none")):
        py = opt.get(key) or make_env(key)
        if not py or not os.path.exists(py):
            fails.append("E25.v %s NOT RUN (no --%s=<python>)" % (key, key)); continue
        try:
            r = run(src, py)
        except Exception as e:
            fails.append("E25.v %s BAD %s" % (key, str(e)[:160])); continue
        t = txt(r["old"])
        rows.append("E25.v %-5s boxes %d (fail %d) · errors %s · document %s · %r" % (key, len(r["old"]), len(r["fail"]), r["errs"][:1], r["feed"], t[:100]))
        if r["errs"]: fails.append("E25.v %s: traceback %s" % (key, r["errs"][:1]))
        if want == "fail":
            if len(r["fail"]) != 1 or "Python 3.8" not in t or "Python 3.10" not in t or "lang=\"de\"" not in "".join(r["fail"]):
                fails.append("E25.v %s: want one stop box naming Python 3.8 and 3.10, en+de (%d boxes)" % (key, len(r["fail"])))
            if r["feed"]: fails.append("E25.v %s: the document was built on an unsupported Python" % key)
        else:
            if not r["feed"]: fails.append("E25.v %s: no document" % key)
            if r["fail"]: fails.append("E25.v %s: a stop box" % key)
            if want == "note" and not ("Python 3.9" in t and len(r["old"]) == 1): fails.append("E25.v %s: want one note on Python 3.9 (%r)" % (key, t[:80]))
            if want == "note-w" and not ("ipywidgets 7" in t and len(r["old"]) == 1): fails.append("E25.v %s: want one note on ipywidgets 7 (%r)" % (key, t[:80]))
            if want == "none" and r["old"]: fails.append("E25.v %s: a note on a supported environment (%r)" % (key, t[:80]))
    print("\n".join(rows))
    print("REGRESS-PY-E25-V OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
