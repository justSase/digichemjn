"""Paket 12/12b — SEED SWEEP: every seed on every level gives exercises that
can be solved, checked and hinted (2026-09-30, E10 Teil 2, Inhalt).

    python3 tests/test_seed_sweep.py <notebook> [seeds]      (default 200)

The notebook is run once in plain Python (as the other suites do); then each
seed is drawn IN PLACE with `reseed()` — the path the ⚙ seed buttons take
(Paket 13) — on each of the three levels. Per seed and level:

  A  answers: the right answer, typed as the exercise text asks (4 decimals,
     π ≈ 3.1416, √2 ≈ 1.4142), is accepted; on gentle also with 2 decimals;
     the targeted wrong one of test_answers is rejected; t2 right/wrong choice
  B  hints: every hint text is rebuilt without giving its answer away
     (`_HINT_SRC` raises on a leak — a reseed would swallow that silently
     and keep the OLD hints)
  C  code: every coding solution of test_checks passes its check, every
     wrong variant fails
  D  settable: every personal number the chapter's sliders show lies on them
     (range and step): z1 ch2/ch4 ±5, z1/z2 ch3 ±6, n5/d5 ch5 ±7, zq ch6 ±5
     (ch6 only on gentle — standard/strict draw a Pythagorean point, see E);
     the t7 target is reachable on its slider grid
  E  gentle, no calculator: every input and result whole or .5, every
     modulus whole or k√2, every angle a multiple of π/4 or π/6
  F  a level change keeps every number except zq (same number of draws)

exit 0 = SEED SWEEP OK. Informational (not a failure): how often zq of
standard/strict lies outside the ch6 sliders — the exercise does not ask for
it to be set there."""
import json, io, contextlib, re, sys, os, ast, time
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display = lambda *a, **k: None

NB = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
nb = json.load(open(NB, encoding="utf-8"))
src = "\n".join(l for l in __import__("megasrc").expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines()
                if not l.strip().startswith("%pip"))
G = {"__name__": "__main__", "display": lambda *a, **k: None}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "m", "exec"), G)
np = G["np"]; TV = G["TV"]

# the coding solutions, read from test_checks (one source for both suites)
_tc = ast.parse(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_checks.py"), encoding="utf-8").read())
SOL = next(ast.literal_eval(n.value) for n in _tc.body
           if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SOL")

def run(code):
    g = dict(G); exec(code, g); return g

def on_grid(x, lo, hi, step=0.5):
    return lo - 1e-9 <= x <= hi + 1e-9 and abs(x / step - round(x / step)) < 1e-9

def nice(x):                       # whole or .5
    return abs(2 * x - round(2 * x)) < 1e-9

def nice_mod(r):                   # whole, .5 or k·√2
    return nice(r) or nice(r / np.sqrt(2))

def nice_angle(p):                 # multiple of π/4 or π/6
    return any(abs(p / (np.pi / d) - round(p / (np.pi / d))) < 1e-9 for d in (4, 6))

rng = np.random.default_rng(20260930)
# the per-run seed is id % 100000; a pinned one may be up to 99999999 (⚙ box)
SEEDS = sorted(set([0, 1, 99999, 12345678, 99999999] + [int(x) for x in rng.integers(0, 100000, N)]))
LEVELS = ["gentle", "standard", "strict"]
fails, info = [], {"zq_off_slider": {"standard": 0, "strict": 0}}
t0 = time.time()

def f(msg):
    if len(fails) < 400: fails.append(msg)

draws = {}
for level in LEVELS:
    G["DIFFICULTY"]["level"] = level
    for seed in SEEDS:
        with contextlib.redirect_stdout(io.StringIO()):
            G["reseed"](seed)
        tag = "%s/%d" % (level, seed)
        z1, z2, zq, n5, d5, q = TV["z1"], TV["z2"], TV["zq"], TV["n5"], TV["d5"], TV["q"]
        draws.setdefault(seed, {})[level] = dict(TV)
        prod = z1 * z2; s_, d_ = z1 + z2, z1 - z2; qd = n5 / d5
        phiq = np.angle(zq) % (2 * np.pi); rq = abs(zq)
        # A — answers, typed as the text asks
        P4 = lambda x: round(float(x), 4)
        rows = [("t1", "_ans_t1", dict(re=0.0, im=np.sqrt(q)), dict(re=np.sqrt(q), im=0.0)),
                ("t3", "_ans_t3", dict(sre=s_.real, sim=s_.imag, dre=d_.real, dim=d_.imag),
                                  dict(sre=s_.real, sim=s_.imag, dre=d_.real, dim=d_.imag + 1.0)),
                ("t4", "_ans_t4", dict(re=prod.real, im=prod.imag),
                                  dict(re=prod.real + 2 * z1.imag * z2.imag, im=prod.imag)),
                ("t5", "_ans_t5", dict(re=qd.real, im=qd.imag), dict(re=qd.real, im=qd.imag + 0.5)),
                ("t6", "_ans_t6", dict(r=rq, phi=phiq), dict(r=rq, phi=(phiq + np.pi) % (2 * np.pi)))]
        # t6 with the constants the text offers (π ≈ 3.1416, √2 ≈ 1.4142)
        if abs(zq.real) == abs(zq.imag):
            typed6 = dict(r=round(abs(zq.real) * 1.4142, 4), phi=round(1.25 * 3.1416, 4))
        else:
            typed6 = dict(r=P4(rq), phi=P4(phiq))
        for key, fn, good, bad in rows:
            g4 = {k: P4(v) for k, v in good.items()} if key != "t6" else typed6
            ok, tip = G[fn](g4)
            if not ok: f("%s %s: right answer (4 decimals) rejected: %s" % (tag, key, re.sub("<[^>]+>", "", str(tip))[:80]))
            if level == "gentle":
                g2 = {k: round(float(v), 2) for k, v in good.items()}
                ok, tip = G[fn](g2)
                if not ok: f("%s %s: right answer (2 decimals) rejected on gentle" % (tag, key))
            ok, _ = G[fn](bad)
            if ok: f("%s %s: wrong answer accepted" % (tag, key))
        ti = G["_QTRUE"]
        if not G["_ans_t2"](ti, "")[0]: f("%s t2: right choice rejected" % tag)
        if G["_ans_t2"]((ti + 1) % 4, "")[0]: f("%s t2: wrong choice accepted" % tag)
        # B — hints rebuilt, no leak
        for key, get in G["_HINT_SRC"].items():
            try:
                get()
            except Exception as e:
                f("%s hint %s: %s" % (tag, key, str(e)[:90]))
        # C — code checks
        for key, (chk, good, bad) in SOL.items():
            fn = G.get(chk)
            if fn is None: f("%s %s: no %s" % (tag, key, chk)); continue
            if not fn(run(good))[0]: f("%s code %s: solution rejected" % (tag, key))
            if fn(run(bad))[0]: f("%s code %s: wrong variant accepted" % (tag, key))
        # D — settable on the chapter's sliders
        for name, z, lo in (("z1 ch2/ch4", z1, 5), ("z2 ch3", z2, 6), ("z1 ch3", z1, 6),
                            ("n5 ch5", n5, 7), ("d5 ch5", d5, 7)):
            if not (on_grid(z.real, -lo, lo) and on_grid(z.imag, -lo, lo)):
                f("%s %s = %s not on the ±%d/0.5 sliders" % (tag, name, z, lo))
        if not (on_grid(zq.real, -5, 5) and on_grid(zq.imag, -5, 5)):
            if level == "gentle": f("%s zq = %s not on the ch6 sliders" % (tag, zq))
            else: info["zq_off_slider"][level] += 1
        # E — gentle: no calculator
        if level == "gentle":
            ins = [q, z1.real, z1.imag, z2.real, z2.imag, n5.real, n5.imag, d5.real, d5.imag, zq.real, zq.imag]
            outs = [np.sqrt(q), s_.real, s_.imag, d_.real, d_.imag, prod.real, prod.imag, qd.real, qd.imag]
            for v in ins + outs:
                if not nice(v): f("%s: %g is not whole or .5" % (tag, v)); break
            if not nice_mod(rq): f("%s: |zq| = %g not whole/k√2" % (tag, rq))
            if not nice_angle(phiq): f("%s: φ(zq) = %g not a multiple of π/4, π/6" % (tag, phiq))

# t7 — fixed target; reachable on the slider grid (|z2| 0.5…3 step .05, φ2 0…6.28 step .02)
tz1, tgt = G["_TZ1"], G["_TGT"]
best = min(abs(tz1 * r * np.exp(1j * p) - tgt)
           for r in np.round(np.arange(0.5, 3.0001, 0.05), 2) for p in np.round(np.arange(0, 6.2801, 0.02), 2))
if best >= G["_TTOL"]: f("t7: target not reachable on the slider grid (best %.3f)" % best)
for level in LEVELS:
    G["DIFFICULTY"]["level"] = level
    if not G["_ans_t7"](dict(r2=1.5, p2=1.58))[0]: f("%s t7: slider setting 1.50 / 1.58 rejected" % level)

# F — only zq depends on the level
for seed, byl in draws.items():
    for k in byl["gentle"]:
        if k == "zq": continue
        if not (byl["gentle"][k] == byl["standard"][k] == byl["strict"][k]):
            f("seed %d: %s changes with the level" % (seed, k)); break

cases = len(SEEDS) * len(LEVELS)
print("seeds %d × levels %d = %d draws in %.1f s; t7 best distance on the grid %.3f (tol %.2f)"
      % (len(SEEDS), len(LEVELS), cases, time.time() - t0, best, G["_TTOL"]))
print("info: zq outside the ch6 sliders (not asked there): standard %d/%d, strict %d/%d"
      % (info["zq_off_slider"]["standard"], len(SEEDS), info["zq_off_slider"]["strict"], len(SEEDS)))
print("\n" + ("SEED SWEEP OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails[:60])))
sys.exit(1 if fails else 0)
