"""Build-time helper (Paket 21a, 2026-09-29): typeset the notebook's formulas
at BUILD time, so the kernel does not have to.

The build runs the assembled mega-cell headless for three fixed seeds (as
tests/test_nb.py runs it), each in its own process, and records every formula
imath/dmath typeset (_MATH_REC). A formula all three runs drew does not depend
on the seed: it is written into the cell as a compact SVG (_MATH_PRE, glyph
paths once in _MATH_GLYPHS). Everything else — the seed-dependent ones — is
typeset at run time by the same _math_svg, so a miss costs time, never
correctness. Fixed seeds keep the build byte-for-byte reproducible.

    from math_pre import math_pre_code
    code = math_pre_code(mega_source)
"""
import json, os, re, subprocess, sys, tempfile

SEEDS = (1, 2, 3)

_RUN = r'''
import json, sys, io, contextlib, random
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display = lambda *a, **k: None
src = open(sys.argv[1], encoding="utf-8").read()
random.seed(int(sys.argv[2]))
g = {"__name__": "__main__", "display": lambda *a, **k: None}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "<mega-cell>", "exec"), g)
json.dump({"rec": g["_MATH_REC"], "pre": g["_MATH_PRE"], "gl": g["_MATH_GLYPHS"]},
          open(sys.argv[3], "w"))
'''


def math_pre_code(mega_src):
    src = "\n".join(l for l in mega_src.splitlines() if not l.strip().startswith("%pip"))
    assert src.count("\n_MATH_REC = None") == 1
    src = src.replace("\n_MATH_REC = None", "\n_MATH_REC = []")
    with tempfile.TemporaryDirectory() as td:
        sp = os.path.join(td, "mega.py")
        open(sp, "w", encoding="utf-8").write(src)
        rp = os.path.join(td, "run.py")
        open(rp, "w").write(_RUN)
        env = dict(os.environ, HOME=td, MPLBACKEND="Agg")   # no stored seed or settings
        procs = [(s, os.path.join(td, "o%d.json" % s)) for s in SEEDS]
        ps = [subprocess.Popen([sys.executable, rp, sp, str(s), o], env=env, cwd=td) for s, o in procs]
        for p in ps:
            assert p.wait() == 0, "math_pre: the headless run failed"
        runs = [json.load(open(o)) for s, o in procs]
    keep = set(runs[0]["rec"])
    for r in runs[1:]:
        keep &= set(r["rec"])
    pre = {k: runs[0]["pre"][k] for k in sorted(keep)}
    used = sorted({g for k in pre for g in pre[k][3].split()})
    # E10.8 (2026-09-30, Applikation) — SHORT GLYPH IDS. matplotlib names a
    # glyph "Cmmi10-61"; the cell only needs a name that is unique in it. The
    # build's glyphs are "0".."9", "a".."z", "10"… (base 36, in the old order);
    # a formula typeset at run time keeps matplotlib's names, which start with
    # a font name and so can never be one of these.
    def b36(i):
        d = "0123456789abcdefghijklmnopqrstuvwxyz"
        return d[i] if i < 36 else b36(i // 36) + d[i % 36]
    short = {g: b36(i) for i, g in enumerate(used)}
    href = re.compile(r'href="#@([^"]+)"')
    lines = ["# ---- formulas typeset by the build (Paket 21a, toolkit/math_pre.py) ----",
             "_MATH_GLYPHS.update({"]
    lines += ["%r: %r," % (short[g], runs[0]["gl"][g]) for g in used]
    lines += ["})", "_MATH_PRE.update({"]
    for k in pre:
        h, W, H, ids, body = pre[k]
        ids = " ".join(sorted(short[g] for g in ids.split()))
        body = href.sub(lambda m: 'href="#@%s"' % short[m.group(1)], body)
        # h, W, H stay as they are: the em size is rounded to 0.01 from h, and
        # a rounded h tipped 1.725 to 1.72; W/H is the width (measured: a
        # rounded viewBox made formulas up to 0.67 px narrower in the Lab)
        # E12 (2026-10-01, Applikation) — SIZE: "~" stands for '<use href="#@'
        # (≈ 520 times, −6 KB); the line after the dict puts it back, so every
        # body in _MATH_PRE is byte-for-byte what it was.
        assert "~" not in body, k
        body = body.replace('<use href="#@', "~")
        lines.append("%r: %r," % (k, (h, W, H, ids, body)))
    lines += ["})", "for _k, _v in _MATH_PRE.items(): _MATH_PRE[_k] = _v[:4] + (_v[4].replace(\"~\", '<use href=\"#@'),)"]
    return "\n".join(lines), len(pre), len(set().union(*[set(r["rec"]) for r in runs])) - len(pre)
