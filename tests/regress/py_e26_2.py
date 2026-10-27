"""E26 Teil 2 · Python — EXERCISES IN THE READING WINDOW (Werkstatt Python, 2026-10-11).
    python3 tests/regress/py_e26_2.py <notebook.ipynb> [--shots DIR] [--json out.json]

The viewer of env_iframe/env_reader (real kernel, every output in an iframe of
its own, no widget manager — PyCharm), served over http, fresh HOME (no kept
progress). Rows:
  K1 answers right      in the KERNEL: every exercise the reading window
                        offers, fed with its own answer data (data-a), passes
                        the Lab check; off by 3 × its tolerance it fails
  P1 exercises there    in the window: calc tasks = the run's written
                        exercises (Complex 7), code copy lines = its coding
                        exercises, sliders with pictures ≥ 1 per figure task;
                        none visible in the nbconvert page (W9 of env_reader)
  P2 calc right/wrong   per task in order: a wrong value → red verdict, the
                        next task still locked (t1 before), right value →
                        green, data-st solved, the next task opens; a choice
                        likewise; the panel mark of t1 turns solved; kept
                        after reload
  P3 slider             every slider with pictures: moving a range changes
                        the picture (frame index and the SVG), the value line
                        follows, the others go back to their start
  P4 pruefe()           in the same kernel: pruefe("t2") while coding t1 is
                        open → locked, nothing recorded; pruefe("t1") with a
                        wrong roots_of → ✗, code state fail; right → ✓, done,
                        progress file ~/.digichemjn/<id>.progress written and a
                        new kernel with the same HOME starts with t1 done
                        (reading markup data-st solved)
v1.72: red (no exercise in the window, no pruefe). Owner: Python.
exit 0 = REGRESS-PY-E26-2 OK."""
import sys, os, re, json, base64, tempfile, shutil, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from env_iframe import host_page
from env_reader import serve

WRONG_ROOTS = "def roots_of(q):\n    return (1j*q, -1j*q)\n"
RIGHT_ROOTS = "import numpy as np\ndef roots_of(q):\n    r = np.sqrt(q)\n    return (1j*r, -1j*r)\n"
# the template notebook (vorlage/): its first coding exercise
CODES = {"roots_of": (WRONG_ROOTS, RIGHT_ROOTS),
         "y_von": ("def y_von(a, x):\n    return a + x\n", "def y_von(a, x):\n    return a * x\n")}

class K:
    """One kernel, kept open: the mega-cell, then cells of our own."""
    def __init__(self, src, home, extra=None):
        from jupyter_client.manager import start_new_kernel
        env = {k: v for k, v in os.environ.items()
               if k not in ("PYCHARM_HOSTED", "DIGICHEM_STATIC_HTML", "DIGICHEM_LANG", "VSCODE_PID", "DIGICHEM_MODE")}
        env.update(extra or {}); env["HOME"] = home
        self.km, self.kc = start_new_kernel(kernel_name="python3", env=env, cwd=os.path.dirname(os.path.abspath(src)))
        nb = json.load(open(src))
        self.code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    def run(self, code):
        mid = self.kc.execute(code); outs, errs, text = [], [], []
        while True:
            m = self.kc.get_iopub_msg(timeout=600)
            if m["parent_header"].get("msg_id") != mid: continue
            t, c = m["msg_type"], m["content"]
            did = (c.get("transient") or {}).get("display_id")
            if t in ("display_data", "execute_result"): outs.append({"data": c["data"], "raw": c["data"], "id": did})
            elif t == "update_display_data":
                for o in outs:
                    if did and o["id"] == did: o["data"] = c["data"]
            elif t == "stream": text.append(c["text"])
            elif t == "error": errs.append(c["ename"] + ": " + c["evalue"])
            elif t == "status" and c["execution_state"] == "idle": break
        return outs, errs, "".join(text)
    def val(self, expr):
        _, e, t = self.run("import json as _j; print(_j.dumps(%s))" % expr)
        if e: raise RuntimeError(e[0])
        return json.loads(t.strip().splitlines()[-1])
    def close(self):
        self.km.shutdown_kernel(now=True)

KCHECK = r"""
# own names only (_k1*): the notebook's globals are the checks' globals (vorlage: _a)
_k1res = []
for _k1r in _NBRW.values():
    if _k1r["kind"] not in ("calc", "choice") or _k1r.get("check") is None: continue
    _k1a = _k1r["answer"]() if callable(_k1r["answer"]) else _k1r["answer"]
    if _k1r["kind"] == "choice":
        _k1ok = _k1r["check"](int(_k1a), _k1r["options"][int(_k1a)])[0]
        _k1bad = _k1r["check"]((int(_k1a) + 1) % len(_k1r["options"]), "")[0]
    else:
        _k1v, _k1w = {}, {}
        for _k1k, _k1lab in _k1r["fields"]:
            _k1x = _k1a[_k1k]; _k1x = tuple(_k1x) if isinstance(_k1x, (tuple, list)) else (_k1x,)
            _k1t = _k1x[1] if len(_k1x) > 1 and _k1x[1] is not None else tol()
            _k1v[_k1k] = float(_k1x[0]); _k1w[_k1k] = float(_k1x[0]) + 3 * _k1t + 0.5
        _k1ok = _k1r["check"](_k1v)[0]; _k1bad = _k1r["check"](_k1w)[0]
    _k1res.append([_k1r.get("task"), bool(_k1ok), bool(_k1bad)])
"""

P_STATE = r"""() => { var f = [].slice.call(document.querySelectorAll('iframe.out')).map(function(x){ return x.contentDocument; })
  .filter(function(d){ return d && d.querySelector('.nbrw'); })[0];
  if (!f) return null;
  var vis = function(e){ var b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0 && f.defaultView.getComputedStyle(e).display !== 'none'; };
  return { calc: [].map.call(f.querySelectorAll('.nbrw-task[data-kind=calc]'), function(e){ return [e.getAttribute('data-task'), e.getAttribute('data-st'), vis(e), !!e.closest('[data-nbrw-gate][data-st=locked]')]; }),
           code: [].map.call(f.querySelectorAll('.nbrw-copy[data-kind=code]'), function(e){ return [e.getAttribute('data-task'), e.getAttribute('data-st'), vis(e), !!e.closest('[data-nbrw-gate][data-st=locked]')]; }),
           sliders: [].map.call(f.querySelectorAll('.nbrw-slider'), function(e){ return [!!e.getAttribute('data-z'), e.getAttribute('data-ready') === '1', e.querySelectorAll('.nbrw-range').length]; }),
           marks: [].map.call(f.querySelectorAll('.nbrw-mark[data-kind=calc],.nbrw-mark[data-kind=code]'), function(e){ return [e.getAttribute('data-kind'), e.getAttribute('data-task'), e.getAttribute('data-st')]; }) }; }"""

def frame(pg):
    for fr in pg.frames:
        try:
            if fr.evaluate("() => !!document.querySelector('.nbrw')"):
                # E26.3 (JS): the window opens on the preview → Play (behauptete bisher: it opens on the document)
                fr.evaluate("() => { var w = document.querySelector('.nbrw'), p = w.querySelector('[data-nbrw-act=play]'); if (p && w.getAttribute('data-nbrw-view') === 'cover') p.click(); }")
                return fr
        except Exception: pass
    return None

def answers_of(fr, key):
    a = fr.evaluate("(k) => { var e = document.querySelector('.nbrw-task[data-task=\"' + k + '\"]'); return e ? e.getAttribute('data-a') : null; }", key)
    return json.loads(base64.b64decode(a)) if a else None

def enter(fr, key, a, right):
    """Fill the task like a reader, press Check; return [verdict, data-st]."""
    sel = '.nbrw-task[data-task="%s"]' % key
    fr.evaluate("(s) => document.querySelector(s).scrollIntoView({block:'center'})", sel)
    if "c" in a:
        n = fr.evaluate("(s) => document.querySelectorAll(s + ' input[type=radio]').length", sel)
        i = a["c"] if right else (a["c"] + 1) % n
        fr.click('%s input[type=radio][value="%d"]' % (sel, i))
    else:
        for k, v, t, p in a["f"]:
            x = v if right else v + 3 * t + 0.5
            s = ("%.6f" % x).rstrip("0").rstrip(".")
            if right and len(a["f"]) and k == a["f"][0][0]: s = s.replace(".", ",")     # a German reader types a comma
            fr.fill('%s .nbrw-input[data-f="%s"]' % (sel, k), s)
    fr.click(sel + " .nbrw-check")
    fr.wait_for_timeout(80)
    return fr.evaluate("(s) => { var e = document.querySelector(s); var f = e.querySelector('.nbrw-fb'); return [f.getAttribute('data-ok'), e.getAttribute('data-st'), f.textContent]; }", sel)

def main():
    args = sys.argv[1:]
    import nbpick
    src = nbpick.from_argv(sys.argv)              # E28: no notebook → the template
    shots = args[args.index("--shots") + 1] if "--shots" in args else None
    jout = args[args.index("--json") + 1] if "--json" in args else None
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    rows, fails = [], []
    def bad(m): fails.append(m)
    tmpd = tempfile.mkdtemp(prefix="pye262_"); home = os.path.join(tmpd, "home"); os.makedirs(home)
    srv = serve(tmpd); base = "http://127.0.0.1:%d/" % srv.server_address[1]
    k = K(src, home); fn = None
    try:
        outs, errs, _ = k.run(k.code)
        if errs: bad("the run raised: %s" % errs[:1])
        nid = k.val("NOTEBOOK.get('id')")
        order = k.val("[t for t in _TASKS['order']]")
        ncode = k.val("[t for t in _TASKS['order'] if _TASKS['has_code'].get(t)]")
        # ---- K1 in the kernel: the answer data pass the Lab check
        try:
            _, e1, _ = k.run(KCHECK)
            res = k.val("_k1res")
            rows.append("K1 answer data vs Lab check: %s" % " ".join("%s:%s/%s" % (t, "ok" if a else "NO", "no" if not b else "PASSES") for t, a, b in res))
            if not res: bad("K1 no exercise with answer data in the run")
            for t, a, b in res:
                if not a: bad("K1 %s: its own answer data fail the Lab check" % t)
                if b: bad("K1 %s: off by 3 × tolerance still passes" % t)
        except Exception as e:
            bad("K1 BAD %s" % str(e)[:200])
        # ---- the reading window in a page of its own
        h = host_page(outs, False)
        open(os.path.join(tmpd, "p.html"), "w", encoding="utf-8").write(h)
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            ctx = b.new_context(viewport={"width": 1400, "height": 900})
            pg = ctx.new_page(); pg.goto(base + "p.html"); pg.wait_for_timeout(3500)
            fr = frame(pg); pg.wait_for_timeout(400)          # E26.3: Play first (frame() presses it)
            st = pg.evaluate(P_STATE)
            if not st:
                bad("P1 no reading window"); st = {"calc": [], "code": [], "sliders": [], "marks": []}
            rows.append("P1 calc %s · code %s · sliders %s (with pictures %d, ready %d) · marks %d"
                        % ([x[0] for x in st["calc"]], [x[0] for x in st["code"]], len(st["sliders"]),
                           sum(1 for x in st["sliders"] if x[0]), sum(1 for x in st["sliders"] if x[1]), len(st["marks"])))
            want = [t for t in order]
            if [x[0] for x in st["calc"]] != want: bad("P1 calc tasks %s, want %s" % ([x[0] for x in st["calc"]], want))
            if [x[0] for x in st["code"]] != ncode: bad("P1 code lines %s, want %s" % ([x[0] for x in st["code"]], ncode))
            # E26.3 (Hauptwerkstatt, Zusammenführen): the window gates chapters like Lab ([data-nbrw-gate], py+js E26.3) —
            # an exercise in a locked chapter is hidden, its mark left out. Behauptete bisher: all 7 + 7 visible at once.
            if any(x[2] == x[3] for x in st["calc"] + st["code"]): bad("P1 exercise visible ≠ not in a locked chapter: %s" % [x[0] for x in st["calc"] + st["code"] if x[2] == x[3]])
            if not (st["calc"] and st["calc"][0][2]): bad("P1 the first exercise is not visible")
            if sum(1 for x in st["sliders"] if x[1]) < 1: bad("P1 no slider with pictures ready")
            nvis = sum(1 for x in st["calc"] + st["code"] if x[2])
            if len(st["marks"]) != nvis: bad("P1 marks %d, want %d (the visible exercises)" % (len(st["marks"]), nvis))
            if st["calc"] and st["calc"][0][1] != "open": bad("P1 first task %s, want open" % st["calc"][0][1])
            if len(st["calc"]) > 1 and st["calc"][1][1] != "locked": bad("P1 second task %s before the first is answered, want locked" % st["calc"][1][1])
            # ---- P2 every calc task: wrong, then right; the next one opens
            if fr:
                for i, (key, _s, _v, *_g) in enumerate(st["calc"]):
                    a = answers_of(fr, key)
                    if not a: bad("P2 %s no answer data" % key); continue
                    w = enter(fr, key, a, False)
                    nxt = st["calc"][i + 1][0] if i + 1 < len(st["calc"]) else None
                    nst = fr.evaluate("(k) => { var e = document.querySelector('.nbrw-task[data-task=\"' + k + '\"]'); return e && e.getAttribute('data-st'); }", nxt) if nxt else None
                    r = enter(fr, key, a, True)
                    nst2 = fr.evaluate("(k) => { var e = document.querySelector('.nbrw-task[data-task=\"' + k + '\"]'); return e && e.getAttribute('data-st'); }", nxt) if nxt else None
                    rows.append("P2 %s wrong → %s/%s · next %s · right → %s/%s · next %s" % (key, w[0], w[1], nst, r[0], r[1], nst2))
                    if w[0] != "0" or w[1] != "wrong": bad("P2 %s wrong value: verdict %s, state %s (want 0, wrong): %s" % (key, w[0], w[1], w[2]))
                    if r[0] != "1" or r[1] != "solved": bad("P2 %s right value: verdict %s, state %s (want 1, solved): %s" % (key, r[0], r[1], r[2]))
                    if nxt and nst2 != "open": bad("P2 after %s the next task %s is %s, want open" % (key, nxt, nst2))
                    if i == 0 and nxt and nst != "open": bad("P2 a wrong answer counts as answered (Lab): next %s, want open" % nst)
                    if i == 0 and shots: pg.screenshot(path=os.path.join(shots, "E26.2-py-aufgabe-hell.png"))
                mk = fr.evaluate("() => { var m = document.querySelector('.nbrw-mark[data-kind=calc][data-task=t1]'); return m && m.getAttribute('data-st'); }")
                if mk != "solved": bad("P2 panel mark t1 %s, want solved" % mk)
            # ---- P3 sliders
            if fr:
                sl = fr.evaluate("""() => [].map.call(document.querySelectorAll('.nbrw-slider[data-ready="1"]'), function(e, i){ e.setAttribute('data-ti', i);
                    return [].map.call(e.querySelectorAll('.nbrw-range'), function(r){ return +r.max; }); })""")
                nmoved, nbad = 0, []
                for si, mx in enumerate(sl):
                    for ri, m in enumerate(mx):
                        r = fr.evaluate("""([si, ri, m]) => { var e = document.querySelector('.nbrw-slider[data-ti="' + si + '"]'), rs = e.querySelectorAll('.nbrw-range'),
                              r = rs[ri], o = e.querySelectorAll('.nbrw-val')[ri], f = e.querySelector('.nbrw-fig');
                              var s0 = f.innerHTML, o0 = o.textContent, fr0 = e.getAttribute('data-frame');
                              var j = +r.value === m ? 0 : m; r.value = String(j); r.dispatchEvent(new Event('input', {bubbles: true}));
                              var others = [].every.call(rs, function(x, q){ return q === ri || +x.value === +x.defaultValue; });
                              return [s0 !== f.innerHTML, o0 !== o.textContent, e.getAttribute('data-frame'), others]; }""", [si, ri, m])
                        nmoved += 1
                        if not (r[0] and r[1] and r[3]): nbad.append((si, ri, r))
                rows.append("P3 sliders moved %d, picture + value changed in %d" % (nmoved, nmoved - len(nbad)))
                if nmoved == 0: bad("P3 no slider to move")
                if nbad: bad("P3 %d moves without a new picture/value (or others not back): %s" % (len(nbad), nbad[:3]))
                if shots:
                    fr.evaluate("() => document.querySelector('.nbrw-slider[data-ready=\"1\"]').scrollIntoView({block:'center'})")
                    pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(shots, "E26.2-py-regler-hell.png"))
            # reload: states kept (localStorage)
            pg.reload(); pg.wait_for_timeout(3500)
            st2 = pg.evaluate(P_STATE) or {"calc": []}
            kept = [x[1] for x in st2["calc"]]
            rows.append("P2 after reload: %s" % kept)
            if st["calc"] and any(x != "solved" for x in kept): bad("P2 after reload %s, want all solved" % kept)
            # E26.3: every exercise answered → every chapter open: all exercises visible, one mark each
            frame(pg); pg.wait_for_timeout(500); st3 = pg.evaluate(P_STATE) or {"calc": [], "code": [], "marks": []}
            nv = sum(1 for x in st3["calc"] + st3["code"] if x[2])
            rows.append("P1b all answered, after reload + Play: visible %d of %d, marks %d" % (nv, len(st3["calc"]) + len(st3["code"]), len(st3["marks"])))
            if st["calc"] and (nv != len(st3["calc"]) + len(st3["code"]) or len(st3["marks"]) != nv): bad("P1b after all answered: visible %d of %d, marks %d" % (nv, len(st3["calc"]) + len(st3["code"]), len(st3["marks"])))
            ctx.close()
            # ---- P4 pruefe() in the kernel
            pf = glob.glob(os.path.join(home, ".digichemjn", "*.progress"))
            t1c = ncode[0] if ncode else "t1"
            nxt = [t for t in ncode if k.val("_TASKS['cguard'].get(%r)" % t) == t1c]
            if nxt:
                o2, e2, _ = k.run('pruefe(%r)' % nxt[0])
                txt = " ".join((o["data"].get("text/plain") or "") for o in o2)
                s2 = k.val("_TASKS['code'][%r]" % nxt[0])
                rows.append("P4 pruefe(%r) while %s open: %s · state %s" % (nxt[0], t1c, txt[:60], s2))
                if s2 != "open" or "✗" in txt or "✓" in txt: bad("P4 pruefe(%r) before %s: %r, state %s — want locked, nothing recorded" % (nxt[0], t1c, txt[:80], s2))
            fn = next((n for n in CODES if ("def %s(" % n) in (__import__("megasrc").expand(k.code) if os.path.exists(os.path.join(os.path.dirname(HERE), "megasrc.py")) else k.code)), None)   # py-E26.3: the short cell
            if fn:
                k.run(CODES[fn][0])
                o3, e3, _ = k.run('pruefe("t1")')
                t3 = " ".join((o["data"].get("text/plain") or "") for o in o3); s3 = k.val("_TASKS['code']['t1']")
                k.run(CODES[fn][1])
                o4, e4, _ = k.run('pruefe("t1", %s)' % fn)
                t4 = " ".join((o["data"].get("text/plain") or "") for o in o4); s4 = k.val("_TASKS['code']['t1']")
                pf2 = glob.glob(os.path.join(home, ".digichemjn", "*.progress"))
                rows.append("P4 wrong: %s · %s | right: %s · %s | progress files %d → %d"
                            % (t3[:40], s3, t4[:40], s4, len(pf), len(pf2)))
                if e3 or not t3.startswith("✗") or s3 != "fail": bad("P4 wrong function: %r, state %s, errors %s" % (t3[:80], s3, e3))
                if e4 or not t4.startswith("✓") or s4 != "done": bad("P4 right function: %r, state %s, errors %s" % (t4[:80], s4, e4))
                if not pf2: bad("P4 no progress file in ~/.digichemjn")
                hs = " ".join((o["data"].get("text/html") or "") for o in o4)
                if "digichemjn.%s.reader.code.t1" % nid not in hs: bad("P4 the verdict does not tell the reading window (localStorage key)")
            else:
                bad("P4 BAD no known coding exercise to answer in this notebook")
        k.close(); k = None
        # a new kernel, same HOME: progress comes back, the reading markup says so
        if fn:
            k2 = K(src, home)
            try:
                o5, e5, _ = k2.run(k2.code)
                s5 = k2.val("_TASKS['code']['t1']")
                rh = [o["data"].get("text/html") or "" for o in o5 if "nbreading" in (o["data"].get("text/html") or "")[:300]]
                m = re.search(r"class='nbrw-copy'[^>]*data-task='t1' data-st='(\w+)'", rh[0] if rh else "")
                rows.append("P4 new kernel, same HOME: code t1 %s · reading markup %s" % (s5, m.group(1) if m else None))
                if s5 != "done": bad("P4 new kernel: code t1 %s, want done (progress file)" % s5)
                if not m or m.group(1) != "solved": bad("P4 new kernel: reading markup t1 %s, want solved" % (m.group(1) if m else None))
            finally:
                k2.close()
    except Exception as e:
        bad("BAD %s" % str(e)[:300])
    finally:
        if k: k.close()
        srv.shutdown(); shutil.rmtree(tmpd, ignore_errors=True)
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-PY-E26-2 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
