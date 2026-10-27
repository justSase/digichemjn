"""E34 P3 · Python — THE STANDARD STYLE IS digi, DARK (Werkstatt Python, 2026-10-19; AUFTRAG E34, Nutzer 19.10.:
the notebooks look like the digi web site and the digi app, „Standardstil“).
    python3 tests/regress/py_e34.py [--nb vorlage|complex|<file.ipynb>] [--kernel-only] [--js] [--shots DIR] [--json out.json]

K  the kernel's side (a real kernel, own HOME, the built file):
   K1  NB_DEFAULTS skin = digi, theme = dark (lang en, mode both unchanged)
   K2  the run's feed (.nbfeed, an HTML widget's value) carries data-nbdefaults with skin digi + theme dark
   K3  five styles in _ORN_SKINS (minimal first, digi among them); the ornament sprite has a group nbo-digi per
       motif and the sprite's own rule `body.nbskin-digi .nbo-digi{display:inline}` (+ hides minimal for digi)
   K4  the style button's title names digi, English and German (the toolkit's table toolkit/de.txt)
B  the browser (real JupyterLab, own server and HOME, Lab theme left at its default LIGHT, fresh browser profile):
   B1  nothing stored → body.nbskin-digi and dark (body.nbdark), measured after Run All + Play
   B2  the style menu: clicking the 🎨 button visits four different styles (digi, minimal = no class, cyber, fairy) and
       comes back (Hauptwerkstatt E34: retro is not offered, E24.6; behauptete bisher fünf)
   B3  a stored choice wins: digichemjn.skin.v1.<id> = cyber, theme light → body.nbskin-cyber, not dark
   B4  (info) stored retro: what the page shows (E24.6 writes it back as minimal; the AUFTRAG names retro among the five)
B1–B3 are the JS workshop's behaviour (J1, 15-rail-theme.js) on Python's standard: with the Python patch alone
they stay red until PATCH-js-E34 is merged. They are REPORTED here and count only with --js (the Hauptwerkstatt
runs the gate with --js after the merge). K1–K4 always count.
v1.79: red (K1 minimal/auto, K2 the same, K3 four styles, K4 no digi; B1 minimal + light).
Owner: Python. exit 0 = REGRESS-PY-E34 OK."""
import sys, os, re, json, time, shutil, socket, subprocess, tempfile, html as _h
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)

A = sys.argv[1:]
KONLY, STRICT_JS = "--kernel-only" in A, "--js" in A
SHOTS = A[A.index("--shots") + 1] if "--shots" in A else None
JOUT = A[A.index("--json") + 1] if "--json" in A else None

PROBE = r'''
import json as _j34
print("@@E34@@" + _j34.dumps({"defaults": NB_DEFAULTS, "skins": list(_ORN_SKINS), "sprite": ornament_sprite()}))
'''

def kernel(src):
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(src))
    code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    home = tempfile.mkdtemp(prefix="e34_home_"); nbdir = tempfile.mkdtemp(prefix="e34_nb_")
    env = {k: v for k, v in os.environ.items() if not k.startswith("DIGICHEM_") and k != "PYCHARM_HOSTED"}
    env["HOME"] = home
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=nbdir)
    out, feeds, err = [], [], []
    try:
        mid = kc.execute(code + "\n" + PROBE)
        while True:
            m = kc.get_iopub_msg(timeout=900)
            if m["parent_header"].get("msg_id") != mid: continue
            t, c = m["msg_type"], m["content"]
            if t == "stream": out.append(c.get("text", ""))
            elif t == "error": err.append(c.get("ename", "") + ": " + c.get("evalue", ""))
            elif t == "comm_msg" or t == "comm_open":
                st = (c.get("data") or {}).get("state") or {}
                v = st.get("value")
                if isinstance(v, str) and "nbfeed" in v: feeds.append(v)
            elif t == "status" and c.get("execution_state") == "idle": break
    finally:
        km.shutdown_kernel(now=True)
        shutil.rmtree(home, ignore_errors=True); shutil.rmtree(nbdir, ignore_errors=True)
    txt = "".join(out); i = txt.rfind("@@E34@@")
    if i < 0: raise RuntimeError("no probe output%s" % (" — " + err[0][:200] if err else ""))
    return json.loads(txt[i + 7:].splitlines()[0]), feeds

def kernel_rows(src, rows, fails):
    p, feeds = kernel(src)
    d = p["defaults"]
    rows.append("K1 NB_DEFAULTS %s" % d)
    want = {"skin": "digi", "theme": "dark", "lang": "en", "mode": "both"}
    bad = {k: d.get(k) for k in want if d.get(k) != want[k]}
    if bad: fails.append("K1 standard values differ: %s (want %s)" % (bad, {k: want[k] for k in bad}))
    fd = None
    for v in feeds:
        m = re.search(r"""data-nbdefaults='([^']*)'""", v)
        if m: fd = json.loads(_h.unescape(m.group(1)))
    rows.append("K2 feed data-nbdefaults %s (%d feeds)" % (fd, len(feeds)))
    if not fd: fails.append("K2 BAD no feed with data-nbdefaults in the widget states")
    elif fd.get("skin") != "digi" or fd.get("theme") != "dark":
        fails.append("K2 feed standard: skin %s theme %s (want digi dark)" % (fd.get("skin"), fd.get("theme")))
    sk, sp = p["skins"], p["sprite"]
    n_sym = sp.count("<symbol "); n_digi = sp.count('class="nbo-digi"')
    rows.append("K3 styles %s · sprite: %d motifs, %d digi groups" % (sk, n_sym, n_digi))
    if len(sk) != 5 or sk[0] != "minimal" or "digi" not in sk or len(set(sk)) != 5:
        fails.append("K3 styles %s (want five, minimal first, digi among them)" % sk)
    if n_sym == 0 or n_digi != n_sym: fails.append("K3 sprite: %d of %d motifs have a digi group" % (n_digi, n_sym))
    if "body.nbskin-digi .nbo-digi" not in sp or "body.nbskin-digi .nbo-minimal" not in sp:
        fails.append("K3 the sprite's own rules do not pick the digi group for body.nbskin-digi")
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "toolkit"))
    import megasrc
    nb = json.load(open(src))
    code = megasrc.expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
    en_ok = "the notebook\\'s style — digi, minimal" in code or "the notebook's style — digi, minimal" in code
    de_ok = "der Stil des Notebooks: digi, minimal" in code
    rows.append("K4 style button title names digi: en %s · de %s" % (en_ok, de_ok))
    if not (en_ok and de_ok): fails.append("K4 the style button's title does not name digi (en %s, de %s)" % (en_ok, de_ok))

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

STATE = r"""() => { var c = [].filter.call(document.body.classList, function(x){ return /^nbskin-/.test(x); });
  return {skin: c.length ? c.join(' ').replace(/nbskin-/g, '') : 'minimal', dark: document.body.classList.contains('nbdark'),
          title: ((document.querySelector('#nbpanel-root .nbbtn.nbskin') || {}).title || '')}; }"""

def browser_rows(src, rows, jrows, jfails, shots):
    from lab_keys import open_nb, CHROME
    from playwright.sync_api import sync_playwright
    import run as _run
    nid = _run.nb_id(src)
    root = tempfile.mkdtemp(prefix="e34_lab_")
    port = free_port(); base = "http://127.0.0.1:%d" % port
    env = dict(os.environ, HOME=root, JUPYTER_DATA_DIR=os.path.join(root, ".jd"), JUPYTER_RUNTIME_DIR=os.path.join(root, ".jr"),
               JUPYTER_CONFIG_DIR=os.path.join(root, ".jc"))
    lab = subprocess.Popen([sys.executable, "-m", "jupyter", "lab", "--no-browser", "--port=%d" % port,
                            "--ServerApp.token=", "--ServerApp.password=", "--ServerApp.disable_check_xsrf=True",
                            "--ServerApp.root_dir=" + root, "--allow-root", "--LabApp.news_url=",
                            "--LabApp.check_for_updates_class=jupyterlab.NeverCheckForUpdate"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    try:
        import urllib.request
        for _ in range(120):
            try: urllib.request.urlopen(base + "/api", timeout=1); break
            except Exception: time.sleep(0.5)
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            def opened(name, items):
                shutil.copy(src, os.path.join(root, name))
                orig = b.new_context
                def nc(**kw):
                    c = orig(**kw)
                    if items: c.add_init_script(_run.INIT_JS % json.dumps(items))
                    return c
                b.new_context = nc
                try: return open_nb(b, base, name)
                finally: b.new_context = orig
            # B1 + B2: fresh
            ctx, pg, errs = opened("e34_fresh.ipynb", {})
            pg.wait_for_timeout(1500)
            s = pg.evaluate(STATE)
            jrows.append("B1 fresh profile: style %s, dark %s" % (s["skin"], s["dark"]))
            if s["skin"] != "digi" or not s["dark"]:
                jfails.append("B1 fresh profile shows %s %s (want digi dark)" % (s["skin"], "dark" if s["dark"] else "light"))
            if shots:
                pg.screenshot(path=os.path.join(shots, "py-E34-frisch.png"))
            seen = [s["skin"]]
            for _ in range(6):
                try: pg.click("#nbpanel-root .nbbtn.nbskin", timeout=5000)
                except Exception: break
                pg.wait_for_timeout(500); seen.append(pg.evaluate(STATE)["skin"])
            jrows.append("B2 style menu (🎨 clicked 6×): %s" % " → ".join(seen))
            # Hauptwerkstatt E34: four in the menu, not five — retro stays out (E24.6, Nutzer 06.10.; js-E34 S3)
            if len(set(seen)) != 4 or seen[4] != seen[0]:
                jfails.append("B2 the style menu visits %d styles %s (want four, then back)" % (len(set(seen)), sorted(set(seen))))
            ctx.close()
            # B3: stored cyber + light
            items = {"digichemjn.skin.v1." + nid: "cyber", "digichemjn.theme.v1." + nid: "light"}
            ctx, pg, errs = opened("e34_stored.ipynb", items)
            pg.wait_for_timeout(1500)
            s = pg.evaluate(STATE)
            rows.append("B3 stored cyber + light: style %s, dark %s" % (s["skin"], s["dark"]))
            if s["skin"] != "cyber" or s["dark"]:
                jfails.append("B3 a stored choice (cyber, light) shows %s %s" % (s["skin"], "dark" if s["dark"] else "light"))
            ctx.close()
            # B4: stored retro (info)
            ctx, pg, errs = opened("e34_retro.ipynb", {"digichemjn.skin.v1." + nid: "retro"})
            pg.wait_for_timeout(1500)
            s = pg.evaluate(STATE)
            rows.append("B4 (info) stored retro: style %s, dark %s" % (s["skin"], s["dark"]))
            ctx.close(); b.close()
    finally:
        lab.terminate()
        try: lab.wait(10)
        except Exception: lab.kill()
        shutil.rmtree(root, ignore_errors=True)

def main():
    import nbpick
    src = nbpick.from_argv([a for a in sys.argv if a not in ("--kernel-only", "--js")])
    rows, fails, jrows, jfails = ["notebook: %s" % os.path.basename(src)], [], [], []
    try: kernel_rows(src, rows, fails)
    except Exception as e: fails.append("BAD kernel: %s" % str(e)[:300])
    if not KONLY:
        if SHOTS: os.makedirs(SHOTS, exist_ok=True)
        try: browser_rows(src, rows, jrows, jfails, SHOTS)
        except Exception as e: jfails.append("BAD browser: %s" % str(e)[:300])
        rows += jrows
        if STRICT_JS: fails += jfails
        elif jfails: rows.append("(JS, J1 — counts with --js) " + " · ".join(jfails))
    print("\n".join(rows))
    if JOUT: json.dump({"rows": rows, "fails": fails, "js": jfails}, open(JOUT, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-PY-E34 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
