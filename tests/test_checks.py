import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)
NBFILE=1
import re
"""Functional test: every solution must pass its own check_fn, and a deliberately
wrong variant must fail. Also exercises the gating/progress state machine."""
import json, sys, io, contextlib, re
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd
ipd.display = lambda *a, **k: None

nb = json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "Complex_Numbers_Step_by_Step.ipynb"))
src = __import__("megasrc").expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
src = "\n".join(l for l in src.splitlines() if not l.strip().startswith("%pip"))
G = {"__name__": "__main__", "display": lambda *a, **k: None}
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(src, "mega", "exec"), G)

np = G["np"]
fails = []

def run(code):
    g = dict(G); exec(code, g); return g

SOL = {
 "t1": ("_check_t1", "import numpy as np\ndef roots_of(q):\n r=np.sqrt(q)\n return (1j*r,-1j*r)\n",
        "import numpy as np\ndef roots_of(q):\n r=np.sqrt(q)\n return (r,-r)\n"),
 "t2": ("_check_t2", "def quadrant(a,b):\n if a==0 or b==0: return 0\n if a>0: return 1 if b>0 else 4\n return 2 if b>0 else 3\n",
        "def quadrant(a,b):\n if a>0: return 1 if b>0 else 4\n return 2 if b>0 else 3\n"),
 "t3": ("_check_t3", "def add_sub(a1,b1,a2,b2):\n return (complex(a1+a2,b1+b2), complex(a1-a2,b1-b2))\n",
        "def add_sub(a1,b1,a2,b2):\n return (complex(a1+a2,b1+b2), complex(a1-a2,b1+b2))\n"),
 "t4": ("_check_t4", "def mul(a1,b1,a2,b2):\n return complex(a1*a2-b1*b2, a1*b2+a2*b1)\n",
        "def mul(a1,b1,a2,b2):\n return complex(a1*a2+b1*b2, a1*b2+a2*b1)\n"),
 "t5": ("_check_t5", "def divide(a1,b1,a2,b2):\n d=a2**2+b2**2\n if d==0: raise ZeroDivisionError('x')\n return complex((a1*a2+b1*b2)/d,(a2*b1-a1*b2)/d)\n",
        "def divide(a1,b1,a2,b2):\n d=a2**2+b2**2\n if d==0: raise ZeroDivisionError('x')\n return complex((a1*a2+b1*b2)/d,(a1*b2-a2*b1)/d)\n"),
 "t6": ("_check_t6", "import numpy as np\ndef to_polar(a,b):\n return (np.hypot(a,b), np.arctan2(b,a)%(2*np.pi))\n",
        "import numpy as np\ndef to_polar(a,b):\n return (np.hypot(a,b), np.arctan(b/a) if a!=0 else 0.0)\n"),
 "t7": ("_check_t7", "import numpy as np\ndef rotate(a,b,phi):\n c,s=np.cos(phi),np.sin(phi)\n return complex(a*c-b*s, a*s+b*c)\n",
        "import numpy as np\ndef rotate(a,b,phi):\n c,s=np.cos(phi),np.sin(phi)\n return complex(a*c+b*s, -a*s+b*c)\n"),
}
_START_SOL = {
 "c01": ("_check_c01", "def cell_count():\n return 2\n",
         "def cell_count():\n return 9\n"),
 "c03": ("_check_c03",
         "def tally(total, solved, skipped, failed):\n return (total-solved-skipped-failed, 100.0*solved/total)\n",
         "def tally(total, solved, skipped, failed):\n return (total-solved, 100.0*solved/total)\n"),
}
# 2026-09-24 — the Sets notebook (script section 1.1) has its own seven.
_SETS_SOL = {
 "t1": ("_check_t1", "def about(A):\n n=len(set(A))\n return (n, 2**n)\n",
        "def about(A):\n n=len(A)\n return (n, 2**n - 1)\n"),
 "t2": ("_check_t2", "def counts(A,B):\n A,B=set(A),set(B)\n return (len(A&B), len(A|B), len(A-B))\n",
        "def counts(A,B):\n A,B=set(A),set(B)\n return (len(A&B), len(A)+len(B), len(A-B))\n"),
 "t3": ("_check_t3", "def product_size(m1,m2):\n return (m1*m2, m1*m1)\n",
        "def product_size(m1,m2):\n return (m1+m2, m1*m1)\n"),
 "t4": ("_check_t4", "def de_morgan(M,A,B):\n M,A,B=set(M),set(A),set(B)\n l=M-(A|B)\n o=M-(A&B)\n return (len(l), l==o)\n",
        "def de_morgan(M,A,B):\n M,A,B=set(M),set(A),set(B)\n l=M-(A&B)\n o=M-(A|B)\n return (len(l), l==o)\n"),
 "t5": ("_check_t5",
        "from fractions import Fraction\ndef smallest_home(x):\n"
        " if isinstance(x, Fraction):\n"
        "  return 'Q' if x.denominator!=1 else ('N' if x.numerator>=1 else 'Z')\n"
        " return 'R' if x!=int(x) else ('N' if x>=1 else 'Z')\n",
        "from fractions import Fraction\ndef smallest_home(x):\n return 'R'\n"),
 "t6": ("_check_t6",
        "import math\ndef sigma_pi(m,n,k):\n return (sum(j*j for j in range(m,n+1)), math.factorial(k))\n",
        "import math\ndef sigma_pi(m,n,k):\n return (sum(j*j for j in range(m,n)), math.factorial(k))\n"),
 "t7": ("_check_t7",
        "def choose(n,k):\n"
        " o=1\n"
        " for j in range(n,n-k,-1): o*=j\n"
        " f=1\n"
        " for j in range(1,k+1): f*=j\n"
        " return (o, o//f)\n",
        "def choose(n,k):\n"
        " o=1\n"
        " for j in range(n,n-k,-1): o*=j\n"
        " return (o, o)\n"),
}
# 2026-09-30 (E10 Teil 4) — Modeling on the standard: nine exercises, each with
# a number first and an optional code fold (the solutions are the folds' own).
_MOD_SOL = {
 "t1": ("_check_t1", "import numpy as np\ndef orders(t_fast_ms, t_slow_h):\n return float(np.log10(t_slow_h*3600*1000/t_fast_ms))\n",
        "import numpy as np\ndef orders(t_fast_ms, t_slow_h):\n return float(np.log10(t_slow_h*3600/t_fast_ms))\n"),
 "t2": ("_check_t2", "import numpy as np\ndef mean_sd(obs):\n y=np.asarray(obs,float)\n return float(y.mean()), float(y.std(ddof=1))\n",
        "import numpy as np\ndef mean_sd(obs):\n y=np.asarray(obs,float)\n return float(y.mean()), float(y.std())\n"),
 "t3": ("_check_t3", "import numpy as np\ndef predict_both(C0, C2, T):\n k=np.log(C0/C2)/2\n return float(C0*np.exp(-k*T)), float(C0+(C2-C0)/2*T)\n",
        "import numpy as np\ndef predict_both(C0, C2, T):\n k=np.log(C0/C2)/2\n return float(C0*np.exp(-k*T)), float(C0-(C2-C0)/2*T)\n"),
 "t4": ("_check_t4", "import numpy as np\ndef pk_numbers(C0, k, t):\n return float(np.log(2)/k), float(C0*np.exp(-k*t))\n",
        "import numpy as np\ndef pk_numbers(C0, k, t):\n return float(k/np.log(2)), float(C0*np.exp(-k*t))\n"),
 "t5": ("_check_t5", "import numpy as np\ndef my_sse(y_true, y_pred):\n y_true=np.asarray(y_true,float); y_pred=np.asarray(y_pred,float)\n return float(np.sum((y_true-y_pred)**2))\n",
        "import numpy as np\ndef my_sse(y_true, y_pred):\n y_true=np.asarray(y_true,float); y_pred=np.asarray(y_pred,float)\n return float(np.sum(np.abs(y_true-y_pred)))\n"),
 "t6": ("_check_t6", "def gd_step(p, g, lr):\n return p - lr*g\n",
        "def gd_step(p, g, lr):\n return p + lr*g\n"),
 "t7": ("_check_t7", "def test_mse(y, yhat):\n return sum((a-b)**2 for a, b in zip(y, yhat))/len(y)\n",
        "def test_mse(y, yhat):\n return sum((a-b)**2 for a, b in zip(y, yhat))\n"),
 "t8": ("_check_t8", "def sensitivity(F, mu0, delta):\n return (F(mu0+delta)-F(mu0-delta))/(2*delta)\n",
        "def sensitivity(F, mu0, delta):\n return (F(mu0+delta)-F(mu0-delta))/delta\n"),
 "t9": ("_check_t9", "import numpy as np\ndef estimate_pi(x, y):\n x=np.asarray(x,float); y=np.asarray(y,float)\n return 4.0*float(np.mean(x**2+y**2<=1.0))\n",
        "import numpy as np\ndef estimate_pi(x, y):\n x=np.asarray(x,float); y=np.asarray(y,float)\n return float(np.mean(x**2+y**2<=1.0))\n"),
}
# E28 (2026-10-12) — the template: five exercises, each with a code fold (k01–k05)
_VOR_SOL = {
 "t1": ("_check_t1", "def y_von(a, x):\n return a * x\n", "def y_von(a, x):\n return a + x\n"),
 "t2": ("_check_t2", "def y_von(a, x):\n return a * x\n", "def y_von(a, x):\n return a * x + 1\n"),
 "t3": ("_check_t3", "def zunahme(a):\n return a > 0\n", "def zunahme(a):\n return a >= 0\n"),
 "t4": ("_check_t4", "import numpy as np\ndef halb(phi):\n return (phi + np.pi) % (2 * np.pi)\n",
        "import numpy as np\ndef halb(phi):\n return phi + np.pi\n"),
 "t5": ("_check_t5", "import numpy as np\ndef abstand(x, y, tx, ty):\n return np.hypot(x - tx, y - ty)\n",
        "def abstand(x, y, tx, ty):\n return abs(x - tx) + abs(y - ty)\n"),
}
_which = sys.argv[1] if len(sys.argv) > 1 else ""
if "Vorlage" in _which:
    SOL = _VOR_SOL
elif "Start_Here" in _which:
    SOL = _START_SOL
elif "Sets" in _which:
    SOL = _SETS_SOL
elif "Modeling" in _which:
    SOL = _MOD_SOL

# A task is gradeable when it has a code-fold checker, a completion button, OR a
# no-code answer widget bound to it. The biophysics standard makes the last one
# the MAIN route, so a notebook may legitimately have no _check_* at all.
_ANS = set()
for _m in re.finditer(r"(numeric_answer|choice_answer|target_answer)\(", src):
    _seg = src[_m.end():_m.end() + 900]
    _t = re.search(r'task\s*=\s*"([a-z0-9]+)"', _seg)
    if _t: _ANS.add(_t.group(1))

for key,(chk,good,bad) in SOL.items():
    fn = G.get(chk)
    if fn is None:
        fails.append("%s: check function %s missing" % (key, chk)); continue
    ok,tip = fn(run(good))
    print("%-4s solution -> %-5s  %s" % (key, ok, "" if ok else "TIP: "+str(tip)[:90]))
    if not ok: fails.append("%s: the published solution does NOT pass its own check (%s)" % (key,tip))
    ok2,tip2 = fn(run(bad))
    print("%-4s wrong    -> %-5s  hint: %s" % (key, ok2, re.sub("<[^>]+>","",str(tip2))[:95]))
    if ok2: fails.append("%s: a deliberately wrong answer PASSED" % key)

# ---- gating: detailed behaviour lives in test_gating.py; here only the wiring ----
T = G["_TASKS"]; L = G["_LOCKS"]

# Every registered exercise must be gradeable one way or the other: either it has
# a check function, or it is a self-reported section (quiz / own data) whose
# circle is filled by a completion_button. Nothing may be silently ungradeable.
SELF = set(re.findall(r'completion_button\("([a-z0-9]+)"', src))
print("self-reported sections:", sorted(SELF))
print("answer-widget tasks:", sorted(_ANS))
for key in T["order"]:
    if key in SOL or key in SELF or key in _ANS:
        continue
    fails.append("%s: neither a check function nor a completion_button" % key)
for key in SELF:
    if key in SOL:
        fails.append("%s: has a checker AND a completion button" % key)

print("\ntasks registered:", len(T["order"]), T["order"])
print("locks: %d chapter, %d practice, %d code"
      % (sum(1 for k in L if k[0] == "chapter"),
         sum(1 for k in L if k[0] == "practice"),
         sum(1 for k in L if k[0] == "code")))
if any(k[1] not in T["order"] for k in L):
    fails.append("a lock refers to an unknown task")
if any(k[0] not in ("content", "practice", "chapter", "code") for k in L):
    fails.append("a lock has an unknown kind")
if not [k for k in L if k[0] == "chapter"]:
    fails.append("no chapter-level locks were created")

# ---- the stylesheet must actually be built AND injected --------------------
_grab = {}
class _R:
    def __init__(self, v): _grab["css"] = v
_saveI, _saveJ = G["IHTML"], G["inject_jump"]
G["IHTML"] = _R; G["inject_jump"] = lambda: None
try:
    G["inject_style"]()          # would raise on an unescaped % in the CSS
except Exception as e:
    fails.append("inject_style() raised %r" % (e,))
G["IHTML"], G["inject_jump"] = _saveI, _saveJ
_css = _grab.get("css", "")
# 2026-09-25: the guard is gone because what it guarded is gone. Every dark
# rule is keyed on OUR class now, and the front end's theme attribute does not
# appear in the finished stylesheet at all — that is the whole of "the Jupyter
# theme must not interfere with the design settings", and it is checkable in
# one line rather than argued about per rule.
for _probe in ('.nbpanel-host{position:fixed',
               'body.nbdark .nbbox',
               "img.dmath", "filter:invert(1)", "@media (max-width:820px)",
               ".nbmap-fill", ".nbmap-inner", ".st-fail",
               ".nbrail-dot.st-ans", ".nbrail-dot.st-code", ".nbrail-dot.st-both",
               "transition:width", "@keyframes nbopen", "prefers-reduced-motion",
               # the skin palette: six named values, twice per skin
               "--nbskin-surf", "--nbskin-acc2", "body.nbdark.nbskin-retro{",
               "body:not(.nbdark).nbskin-cyber{",
               # the controls inside the exercises follow it — the REAL
               # ipywidgets 8 class names, taken from a census of the running
               # notebook rather than from memory (`.ui-slider` does not exist)
               ".jp-OutputArea .slider.noUi-target",
               ".jp-OutputArea .widget-readout"):
    if _probe not in _css:
        fails.append("CSS is missing %r" % _probe)
# NOT ONE mention of the front end's theme may survive in the stylesheet. A
# single one is a rule that JupyterLab's Settings menu can still reach into.
import re as _re2
_leak = [m.start() for m in _re2.finditer(r"data-jp-theme", _css)]
if _leak:
    _ctx = _css[max(0, _leak[0] - 60):_leak[0] + 60].replace("\n", " ")
    fails.append("%d selectors still read JupyterLab's own theme attribute "
                 "(first at %d: ...%s...)" % (len(_leak), _leak[0], _ctx))
# ...and the light halves of the skins must be keyed on our class too, or a
# skin's light rules simply never apply under a dark front end (measured: that
# was the leak the :not(.nbforce-light) guard never covered, because it looks
# for `body[` and these are spelled `body:not([`)
if 'body:not(.nbdark).nbskin-' not in _css:
    fails.append("the skins' light halves are not keyed on :not(.nbdark)")
# 2026-09-26b — B · THE PAGE FOLLOWS THE SKIN. Six token sets (three skins
# x light/dark; minimal is the absence of a class and must have none), and the
# texture may be painted on ONE element only: the notebook's own scroller.
# A rule that put var(--nbskin-tex) on <body> or a JupyterLab frame would pass
# every contrast check and still texture the whole application.
import re as _re3
for _sk in ("cyber", "retro", "fairy"):
    for _half in ("body:not(.nbdark).nbskin-%s{--nbskin-page:" % _sk,
                  "body.nbdark.nbskin-%s{--nbskin-page:" % _sk):
        if _half not in _css:
            fails.append("texture tokens missing: %r" % _half)
if "nbskin-minimal" in _css and "--nbskin-page" in _css.split("nbskin-minimal", 1)[1][:200]:
    fails.append("minimal carries a page texture — minimal is the absence of a skin")
for _m in _re3.finditer(r"([^{}]*)\{[^{}]*var\(--nbskin-tex\)", _css):
    for _sel in _m.group(1).split(","):
        _sel = _sel.strip()
        # 2026-09-30 (E10, CSS) — behauptete bisher: NUR der Dokument-Scroller.
        # E9.12 legt die Textur auch aufs eigene Panel (#nbpanel-root: Rail,
        # Dock, Schublade — gibt es nur in unserem Notebook). Verboten bleibt,
        # was die Regel meinte: <body> oder ein JupyterLab-Rahmen.
        if not (_sel.endswith(".nbrail-own .jp-WindowedPanel-outer")
                or _re3.search(r"#nbpanel-root\s+\.nb[\w-]+$", _sel)):
            fails.append("the texture is painted outside the document scroller: %r" % _sel)
if not _re3.search(r"@media print\{[^}]*nbskin-retro \.nbrail-own \.jp-WindowedPanel-outer[^}]*background-image:none", _css):
    fails.append("print does not take the texture off")
# 2026-09-26c — C2. (1) Retro never turns a mark: the general "turn under the
# pointer" rules outrank retro's upright rule, so retro must name :hover and
# :focus for every mark kind itself, with a transform that has no rotate().
# (2) The keyboard mode is visible on the panel: .nbkbd draws an outline.
for _k in ("hover .nbchapdot", "hover .nbsubdot", "focus .nbchapdot",
           "focus .nbsubdot", "focus .nbrail-dot", "focus .nbcodemark",
           "focus .nbvizmark"):
    _m = _re3.search(r"body\.nbskin-retro #nbpanel-root\.vert \.nbmap-node:" + _re3.escape(_k)
                     + r"[^{]*\{([^}]*)\}", _css)
    if not _m:
        fails.append("retro does not name :%s — the general rule turns it" % _k)
    elif "rotate" in _m.group(1):
        fails.append("retro turns the mark on :%s" % _k)
# 2026-09-27c — G1. The loop above passed while retro still spun on .nbpop
# (the marker passing a mark): it asked only for :hover and :focus. Measured in
# the real Lab: 174.8° off level mid-way. Retro names .nbpop now, without rotate;
# and in every other skin a mark that carries a sign grows but does not turn.
_m = _re3.search(r"body\.nbskin-retro #nbpanel-root\.vert \.nbmap-node:is\(:hover,:focus,\.nbpop\)[^{]*\{([^}]*)\}", _css)
if not _m or "rotate" in _m.group(1):
    fails.append("retro does not hold its marks upright on .nbpop")
_m = _re3.search(r"body:not\(\.nbskin-retro\) #nbpanel-root\.vert \.nbmap-node:is\(:hover,:focus,\.nbpop\) :is\(\.nbrail-dot,\.nbcodemark\)[^{]*\{([^}]*)\}", _css)
if not _m or "rotate(45deg)" not in _m.group(1) or "360" in _m.group(1):
    fails.append("a mark with a sign still turns when hovered, focused or passed")
# scs3 and the panel's face
if not _re3.search(r"\.nbrail-own \.jp-Cell \.jp-Collapser\{display:none", _css):
    fails.append("JupyterLab's active-cell strip is still shown in a notebook with the panel")
# 2026-09-30 (E10, CSS) — behauptete bisher blur(6px) als Zahl; Paket 7
# (28.09.) machte daraus das Token --nbpanel-blur (8 px). Geprüft wird die
# Unschärfe an der Fläche UND dass das Token gesetzt ist.
if not (_re3.search(r"\.nbrail::before\{[^}]*backdrop-filter:blur\(var\(--nbpanel-blur,\d+px\)\)", _css)
        and _re3.search(r"body\{[^}]*--nbpanel-blur:\d+px", _css)):
    fails.append("the panel has no translucent face (E, backdrop blur)")
# 2026-09-30 — E10.1–E10.4 (CSS). Retro: hell Leinen (Schrägfäden 63°),
# dunkel Bütten (Wolken), kein Schalter mehr; der Kopf des Titel-Akkordeons
# ist weg; die Sonde des Markenbodens misst ohne Lupe; der YOC-Streifen ist
# ein Block (sonst zentriert margin:auto nicht).
if "data-nbretro" in _css:
    fails.append("retro still has the A/B switch html[data-nbretro]")
# (the last rule wins: older token sets stand above it in the sheet)
_m = _re3.findall(r"body:not\(\.nbdark\)\.nbskin-retro\{--nbskin-page:[^}]*\}", _css)
if not _m or "63deg" not in _m[-1]:
    fails.append("retro light is not linen (B)")
_m = _re3.findall(r"body\.nbdark\.nbskin-retro\{--nbskin-page:[^}]*\}", _css)
if not _m or "ellipse at 70%" not in _m[-1] or "63deg" in _m[-1]:
    fails.append("retro dark is not laid paper (A)")
if not _re3.search(r"\.acc-title\.acc-root>\.jupyter-widget-Collapse>\.jupyter-widget-Collapse-header\{display:none", _css):
    fails.append("the title accordion still shows its header (double title)")
if not _re3.search(r"\.nbmap \.nbprobe\{--nbsym:2\.9", _css):
    fails.append("the mark floor is probed under the lens (marks do not scale with it)")
if not _re3.search(r"\.jp-Notebook-footer\{display:block", _css):
    fails.append("the add-a-cell strip is inline-block (margin:auto cannot centre it)")
if not _re3.search(r"\.nbpanel-host\.nbkbd \.nbrail\{[^}]*outline:2px solid", _css):
    fails.append("the keyboard mode draws no outline on the panel")
# 2026-09-30 (E11.1, Python) — "Your own cell" is no accordion any more: no
# pill, no sentence, no "＋ Your own cell" button in the document; only the
# anchor #nbyoc and the restore list `.nbyoc-list` stay, outside the title.
if "_yoc_mark" in G:
    _yo = []
    _d0 = G.get("display")
    G["display"] = lambda *a, **k: _yo.extend(a)
    try:
        G["_yoc_mark"]()
    finally:
        G["display"] = _d0
    _yh = " ".join(getattr(w, "value", "") or "" for w in _yo)
    if any(type(w).__name__ == "Accordion" for w in _yo) or "nbyoc-add" in _yh \
            or "nbyoc-note" in _yh or "nbyoc-list" not in _yh or "nbyoc" not in _yh:
        fails.append("E11.1: YOC is not just anchor + restore list: %r" % _yh[:160])
if "_yoc_accordion" in G or "_yoc_mark" not in G or "Cells of your own sit" in src:
    fails.append("E11.1: 'Your own cell' is still an accordion with pill/sentence/＋ button")
# 2026-09-25 — COMMENTS THAT DO NOT CLOSE PROPERLY EAT THE RULE BELOW THEM.
# This cost a measurement round: a block of prose ended with `*/` while the
# comment above it had ALREADY closed, so four lines of English stood in the
# stylesheet as if they were CSS. The browser discards from there until it can
# resynchronise — which took the very rule the comment was introducing with it.
# Nothing in the page looked broken; the rule was simply not applied, and the
# only way to see it was to read a computed style back and find the old value.
# One scan, and that whole class of loss is caught at build time.
_i, _inc, _stray, _open = 0, False, [], None
while _i < len(_css) - 1:
    _two = _css[_i:_i + 2]
    if not _inc and _two == "/*":
        _inc, _open, _i = True, _i, _i + 2
        continue
    if _inc and _two == "*/":
        _inc, _i = False, _i + 2
        continue
    if not _inc and _two == "*/":
        _stray.append(_i)
    _i += 1
if _stray:
    _c = _css[max(0, _stray[0] - 90):_stray[0] + 10].replace("\n", " ")
    fails.append("%d comment terminators stand outside any comment — the CSS "
                 "after them is discarded (first at %d: ...%s)"
                 % (len(_stray), _stray[0], _c))
if _inc:
    _c = _css[_open:_open + 90].replace("\n", " ")
    fails.append("a comment is never closed (opens at %d: %s...)" % (_open, _c))
# and the nine changes of 2026-09-25 each leave a fingerprint.
# 2026-10-02 (E16.3) — BEHAUPTETE BISHER: the marker's light is a column
# three marker-heights tall, stated twice (`[data-dir="up"]::after`,
# `height:300%`). The user replaced it: one round light under the marker,
# no trail. Those two fingerprints became these two.
for _probe in ("--nbskin-quiet", ".nbmap-trail{display:none!important",
               "border-radius:50%!important;-webkit-mask-image:none", ".noUi-handle", "button.widget-button",
               "nbskin-fairy #nbpanel-root.vert .nbrail-dot",
               "nbskin-cyber #nbpanel-root.vert .nbrail-dot",
               "width:fit-content", ".nblocked-head{color:"):
    if _probe not in _css:
        fails.append("CSS is missing %r" % _probe)
# 2026-09-28d (K3, rebased onto 28c): each part leaves a fingerprint. What they
# DO is measured in the real JupyterLab by tests/lab_k3.py; this only says the
# rules shipped. K3.8 ("no tail") is not among them — replaced by the trail
# behind the movement (28c), whose fingerprints above stay.
for _probe in ("calc(12px * var(--nbk,1))",                 # K3.1 pips 12 px
               "color-mix(in srgb,#3aa06f 46.7%",            # K3.2 fills into the panel
               "--nbrail-edge",                              # K3.3 tab = panel
               "content:'Locked'", "cursor:not-allowed",     # K3.4 locked / waiting
               "button.widget-button.nbskipnow",             # K3.4 skip is a button
               "--nbtexz",                                   # K3.5 texture zooms
               ".nbhint-btn"):                               # K3.6 hint button
    if _probe not in _css:
        fails.append("CSS is missing %r (K3)" % _probe)
# and the setup must CALL it, otherwise the notebook renders unstyled
import re as _re
_calls = _re.findall(r"^inject_style\(\)\s*$", src, _re.M)   # a real call, not the docstring
if len(_calls) != 1:
    fails.append("inject_style() is called %d times at top level (expected exactly 1)" % len(_calls))
_rail = _re.findall(r"^\s*nbrail_js\(\)\s*$", src, _re.M)
if not _rail:
    fails.append("nbrail_js() is never called — the bar will not stay pinned")
_prof = _re.findall(r"^use_profile\(", src, _re.M)
if len(_prof) != 1:
    fails.append("use_profile() is called %d times at top level (expected exactly 1)" % len(_prof))
print("\nstylesheet: %d chars, all probes present; top-level calls: "
      "inject_style x%d, use_profile x%d" % (len(_css), len(_calls), len(_prof)))


# --- the OER record the FCI proposal requires --------------------------------
_meta = G["META"]
for _f in ("title", "institution", "licence", "version", "audience", "prerequisites",
           "duration", "source"):
    if not _meta.get(_f):
        fails.append("OER metadata field %r is empty" % _f)
if not _meta.get("keywords"): fails.append("OER metadata has no keywords")
if not _meta.get("objectives"): fails.append("OER metadata carries no learning objectives")
if "CC BY" not in _meta.get("licence", ""):
    fails.append("the licence is not a CC BY licence: %r" % _meta.get("licence"))
_mbox = G["metadata_box"]().value
_L = G.get("_nbL", lambda en, de: en)       # E17.1: the probes in the run's language
for _probe in (_L("Licence", "Lizenz"), _L("Cite as", "Zitieren als"), "DOI", "Version",
               _L("Open Educational Resource", "offene Bildungsressource")):
    if _probe not in _mbox:
        fails.append("the metadata box is missing %r" % _probe)
print("OER record: %s, %s, version %s, %d objectives, %d keywords"
      % (_meta["licence"], _meta["institution"][:38], _meta["version"],
         len(_meta["objectives"]), len(_meta["keywords"])))

# --- 2026-09-26 (Inhalt A), eingebaut R2 · 15: the title card's facts ---------
# One source: register_goals(), TIME_RULE and the panel's chapters. Asserts:
#  (1) the cold card (markdown cell) lists exactly the registered goals, in order,
#      and exactly the numbered chapters of the timeline;
#  (2) the warm card (title_card(...) in the mega-cell) carries NO facts (E8.17);
#  (3) the time line on the card is what the running notebook computes now;
#  (4) the registry counts agree with an independent tally of the chapter SOURCE;
#  (5) the OER record carries the same goals and the same working time.
import html as _html
_goals = G["goals"]() if "goals" in G else []
if not _goals:
    print("\ntitle-card facts: NO GOALS REGISTERED — check skipped (not a pass)")
else:
    _cold = "".join(nb["cells"][0]["source"])
    # E24.3 (06.10.): the cover with its facts is an output of the mega-cell,
    # display(IHTML('<div class="nbtitle nbcover-out" …')); the markdown cell is one line
    if "nbtitle-facts" not in _cold:
        import ast as _astc
        # E24 Stufe 2: the cover rides in `_nbcv = '…'` (German words put in at run time)
        _mc = (re.search(r"^_nbcv = (.*nbcover-out.*)$", src, re.M)
               or re.search(r"^display\(IHTML\((.*nbcover-out.*)\)\)$", src, re.M))
        _cold = _astc.literal_eval(_mc.group(1)) if _mc else ""
    # E17.1 (02.10.): the cold card stays English; a German run is held against
    # the German facts the cell carries for the page (.nbcover-de data-map)
    # E29 P1 (12.10.): a cover with both languages (data-nbl spans, card_facts.cover_two,
    # the Vorlage) is read in the run's language — there is no .nbcover-de map then
    if 'data-nbl="de"' in _cold:
        _lg = "de" if _L(0, 1) else "en"
        _ot = "en" if _lg == "de" else "de"
        _cold = re.sub(r'<span data-nbl="%s"(?: style="display:none")?>.*?</span>' % _ot, "", _cold, flags=re.S)
        _cold = re.sub(r'<span data-nbl="%s"(?: style="display:none")?>(.*?)</span>' % _lg, r"\1", _cold, flags=re.S)
    elif _L(0, 1):
        import ast as _ast0, json as _json0
        _mv = re.search(r'^\s*_show\(HTML\(value=(\'<div class="nbcover-de".*), layout=Layout\(height="0px", margin="0px"\)\)\)$', src, re.M)
        _md = re.search(r"data-map='([^']*)'", _ast0.literal_eval(_mv.group(1))) if _mv else None
        _cold = _json0.loads(_html.unescape(_md.group(1)))["facts"] if _md else ""
    _fm = re.search(r"<div class='nbtitle-facts'.*?<div class='nbtitle-time'[^>]*>.*?</div></div>", _cold, re.S)
    if not _fm:
        fails.append("the cold title card has no facts block")
    else:
        _fx = _fm.group(0)
        _li = [(k, _html.unescape(t).strip()) for t, k in
               re.findall(r"<li class='nbtitle-goal'[^>]*>(.*?) <span class='nbtitle-k'[^>]*>(K\d)</span>", _fx, re.S)]
        if _li != [(g, t) for g, l, t in _goals]:
            fails.append("card goals differ from register_goals(): %r" % (_li[:2],))
        _ch = [(int(n), _html.unescape(t)) for n, t in
               re.findall(r"<li class='nbtitle-chap'[^>]*><b>(\d+)</b>&ensp;(.*?)</li>", _fx)]
        _want = [(e["num"], e["title"]) for e in G["_STRUCT"] if e.get("kind") == "chapter"]
        if _ch != _want:
            fails.append("card chapters %r != timeline chapters %r" % (_ch[:2], _want[:2]))
        import ast as _ast
        _wc = re.search(r"^title_card\((.*)\)$", src, re.M)
        # E17.1 (02.10.): the warm card comes in two languages,
        # title_card(_nbL(english, german)); the rule holds for both
        _wn = _ast.parse(_wc.group(1), mode="eval").body if _wc else None
        _warms = ([_ast.literal_eval(a) for a in _wn.args] if isinstance(_wn, _ast.Call)
                  else [_ast.literal_eval(_wn)] if _wn is not None else [""])
        for _warm in _warms:
            # E8.17 (29.09.): after Play only the subtitle stands between the title
            # pill and the Introduction — the warm card carries NO facts block
            if "nbtitle-facts" in _warm:
                fails.append("E8.17: the warm card (title_card in the mega-cell) still carries the facts block")
            if "nbtitle-lead" not in _warm:
                fails.append("E8.17: the warm card lost its subtitle (nbtitle-lead)")
        _line = _html.unescape(re.search(r"<div class='nbtitle-time'[^>]*>(.*?)</div>", _fx).group(1))
        if _line != G["time_budget_text"]():
            fails.append("card time line %r != computed %r" % (_line, G["time_budget_text"]()))
        _sec = src[src.index("# ===== sections"):]
        _tally = {"chapter": len(re.findall(r"^build_chapter\(\s*\d", _sec, re.M)),
                  "coding": len(re.findall(r"\bcode_fold\(", _sec)),
                  "figure": len(re.findall(r"\b(?:slider_plot|target_exercise)\(", _sec))}
        _cnt = G["element_counts"]()
        for _k in ("chapter", "coding", "figure"):
            if _tally[_k] != _cnt[_k]:
                fails.append("%s: registry counts %d, the source has %d" % (_k, _cnt[_k], _tally[_k]))
        if _meta.get("objectives") != G["goal_strings"]():
            fails.append("OER objectives are not the registered goals")
        if _meta.get("duration") != _line:
            fails.append("OER working time %r != card %r" % (_meta.get("duration"), _line))
        print("\ntitle-card facts: %d goals, %d chapters, %s | counts %s | source tally %s"
              % (len(_li), len(_ch), _line, _cnt, _tally))
# 2026-09-25h — THE PROGRESS CODE IS TAMPER-EVIDENT. A code that was changed by
# hand — one state flipped, or the checksum cut off — must be REFUSED, and the
# untouched code must still restore.
import base64 as _b64
_HAS_TASKS = bool(G["_TASKS"]["order"])     # ML and Modeling have none yet
_pc = G["progress_code"]()
_ok0, _m0 = G["apply_progress_code"](_pc)
if not _ok0: fails.append("the notebook's own progress code does not restore: %s" % _m0)
_raw = _b64.urlsafe_b64decode(_pc + "=" * (-len(_pc) % 4)).decode()
_f = _raw.split("|")
_flip = list(_f[1]) or ["o"]; _flip[0] = {"o": "d"}.get(_flip[0], "o"); _f1 = list(_f); _f1[1] = "".join(_flip)
_enc = lambda s: _b64.urlsafe_b64encode(s.encode()).decode().rstrip("=")
for _name, _bad in (("one state flipped", _enc("|".join(_f1))),
                    ("checksum cut off", _enc("|".join(_f[:-1]))),
                    ("checksum of another body", _enc("|".join(_f1[:-1] + [_f[-1]])))):
    _okb, _mb = G["apply_progress_code"](_bad)
    if _okb: fails.append("a progress code with %s was accepted" % _name)
print("progress code: own restores=%s; flipped/cut/foreign refused" % _ok0)
# 2026-09-26a — a restore opens what the live answer opened. Measured by D: a
# coding exercise solved, the notebook run again → its chapter locked again.
def _fresh_ns():
    _g = {"__name__": "__main__", "display": lambda *a, **k: None}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "mega", "exec"), _g)
    return _g
if _HAS_TASKS:
    # two FRESH runs — the G above has been through the whole state machine
    _GA, _GB = _fresh_ns(), _fresh_ns()
    _k1 = _GA["_TASKS"]["order"][0]
    _GA["task_code_solved"](_k1)
    _live = {k: v["open"] for k, v in _GA["_LOCKS"].items()}
    _GB["apply_progress_code"](_GA["progress_code"]())
    _rest = {k: v["open"] for k, v in _GB["_LOCKS"].items()}
    _diff = sorted(k for k in _live if _live[k] != _rest.get(k))
    if _diff: fails.append("a restore does not open what the live answer opened: %s" % _diff[:4])
    print("restore = live locks after a coding solve: %s" % (not _diff))
# 2026-09-25h — PROGRESS SURVIVES A RUN. Kept on every change, brought back at
# the end of the next run (in a real kernel; here the switch is thrown by hand,
# and the home directory is a temporary one, so no suite sees another's state).
import os as _os, tempfile as _tf
_home0 = _os.environ.get("HOME")
_os.environ["HOME"] = _tf.mkdtemp()
try:
    if not _HAS_TASKS: raise StopIteration
    G["_persist_ok"] = lambda: True
    _st0 = (dict(G["_TASKS"]["state"]), dict(G["_TASKS"]["code"]))
    _k = G["_TASKS"]["order"][0]
    G["task_solved"](_k)
    _kept = G["progress_stored"]()
    if not _kept: fails.append("a change was not kept for the next run")
    for _k2 in G["_TASKS"]["order"]:                    # a fresh run: all open
        G["_TASKS"]["state"][_k2] = "open"; G["_TASKS"]["code"][_k2] = "open"
    G["_PROG"]["persist"] = False
    G["_progress_resume"]()
    if G["_TASKS"]["state"].get(_k) != "done":
        fails.append("the next run did not bring the kept progress back (%s)" % G["_PROG"].get("resumed"))
    G["progress_forget"]()
    if G["progress_stored"]() is not None: fails.append("progress_forget() left the kept progress")
    print("kept across a run: %s" % G["_PROG"].get("resumed"))
except StopIteration:
    print("kept across a run: no exercises in this notebook")
finally:
    if _home0 is None: _os.environ.pop("HOME", None)
    else: _os.environ["HOME"] = _home0
# 2026-09-28b — K2: WHAT THE TIMELINE CALLS THINGS (STRUKTUR K2.3, K2.8, K2.11).
# Read from the panel's own markup (_prog_html), the one both the rail and
# its mirrors are made of.
_nb_is = lambda n: n.lower() in _which.lower()    # which notebook this run checks
try:
    if "_prog_html" not in G or not _HAS_TASKS: raise StopIteration
    import html as _html
    _ph = G["_prog_html"]()
    # the panel's markup carries the timeline twice (two layouts of one map):
    # the first one is the timeline
    _i1 = _ph.find('<div class="nbmap"'); _i2 = _ph.find('<div class="nbmap"', _i1 + 1)
    _ph = _ph[_i1:_i2] if _i1 >= 0 and _i2 > _i1 else _ph
    _nodes = re.findall(r'<a class="nbjump nbmap-node([^"]*)"([^>]*)>(.*?)</a>', _ph, re.S)
    def _lab(body):
        m = re.search(r'<span class="(?:nbmap-lab|nbtasklab)">([^<]*)</span>', body.replace('<span class="nbmap-lab"></span>', ''))
        return _html.unescape(m.group(1)) if m else None
    # K2.11 — the top mark is the notebook's title, read from the card
    _card = G.get("_NB_TITLE", {}).get("text")
    _top = _nodes[0] if _nodes else None
    if not _top or " title" not in _top[0]:
        fails.append("K2.11: the first mark is not the title mark")
    elif (_nb_is("complex") and (_card != _L("Complex Numbers", "Komplexe Zahlen") or _lab(_top[2]) != _card)) or \
         (_nb_is("modeling") and (_card != _L("Introduction to Modeling", "Einführung in die Modellierung")
                                  or _lab(_top[2]) != _card)):
        fails.append("K2.11: the title mark reads %r, the card %r" % (_lab(_top[2]), _card))
    # K2.3 — one mark per exercise: no other mark points where an exercise's does
    _tgt = {}
    for cls, attrs, body in _nodes:
        m = re.search(r'data-target="([^"]+)"', attrs)
        if m: _tgt.setdefault(m.group(1), []).append(cls)
    for _k in G["_TASKS"]["order"]:
        _own = [a for c, a, b in _nodes if ' data-task="%s"' % _k in a and re.search(r"(^| )task( |$)", c)]
        if len(_own) != 1:
            fails.append("K2.3: %s has %d exercise marks" % (_k, len(_own))); continue
        _t = re.search(r'data-target="([^"]+)"', _own[0]).group(1)
        if len(_tgt.get(_t, [])) != 1:
            fails.append("K2.3: %d marks point at %s's place (%s)" % (len(_tgt[_t]), _k, _tgt[_t]))
    # K2.8 — every numbered mark: "Chapter|Figure|Exercise|Coding n: name"
    _bad = []
    for cls, attrs, body in _nodes:
        if not re.search(r"\b(chap|viztask|task|codetask)\b", cls): continue
        l = _lab(body) or ""
        if not re.match(r"^(Chapter|Figure|Exercise|Coding|Kapitel|Abbildung|Aufgabe|Code) \d+: .+", l): _bad.append(l)
    if (_nb_is("complex") or _nb_is("modeling")) and _bad:
        fails.append("K2.8: names without their title: %s" % _bad[:6])
    print("K2 names: %d marks, title %r, e.g. %s" % (len(_nodes), _card,
          [(_lab(b)) for c, a, b in _nodes if re.search(r"\b(chap|task|codetask|viztask)\b", c)][:4]))
except StopIteration:
    print("K2 names: no panel in this notebook")
# --- 2026-09-27 (Inhalt, hinweise + hinweise2), eingebaut R2 · 15 -------------
# HINTS BEFORE THE SOLUTION. Per hint widget: (1) nothing shown before the first
# click; (2) each click opens exactly ONE more step; (3) the last click hides
# them, the next shows all seen; (4) asking changes no progress state; (5) no
# step states a correct result — recomputed HERE from TV, not from `forbid`.
# Complex carries hints on all seven exercises, two steps each.
import numpy as np
_HW = G.get("_HINT_WIDGETS", {})
if "Complex" in _which:
    _tv = G["TV"]; _za, _zb = _tv["z1"], _tv["z2"]
    _tgt = 3.0 * np.exp(1j * (0.6 + np.pi / 2))          # c07: |z1| = 2, φ1 = 0.60
    _qd = _tv["n5"] / _tv["d5"]; _zq = _tv["zq"]; _phq = float(np.angle(_zq) % (2 * np.pi))
    _TRUE = {"t1": (float(np.sqrt(_tv["q"])),),
             "t2": ("Quadrant " + ("I" if _za.real > 0 and _za.imag > 0 else
                                   "II" if _za.real < 0 and _za.imag > 0 else
                                   "III" if _za.real < 0 else "IV"),),
             "t3": ((_za + _zb).real, (_za + _zb).imag, (_za - _zb).real, (_za - _zb).imag),
             "t4": ((_za * _zb).real, (_za * _zb).imag),
             "t5": (_qd.real, _qd.imag),
             "t6": (abs(_zq), _phq, float(np.degrees(_phq))),
             "t7": (abs(_tgt) / 2, float((np.angle(_tgt) - 0.6) % (2 * np.pi)))}
    if sorted(_HW) != ["t%d" % _i for _i in range(1, 8)]:
        fails.append("Complex should carry hints on t1–t7, found %r" % sorted(_HW))
    for _hk in sorted(_HW):
        if len(_HW[_hk][2]) != 2:
            fails.append("hint %s: %d steps, the standard is two" % (_hk, len(_HW[_hk][2])))
elif "Modeling" in _which:
    # 2026-09-30 (E10 Teil 4) — the results recomputed HERE from TV, not taken
    # from the chapters' own variables (which the forbid lists use)
    _tv = G["TV"]
    _y2 = np.array(_tv["ob_y"], float)
    _k3 = np.log(_tv["wb_C0"] / _tv["wb_C2"]) / 2
    _e7 = np.array(_tv["ov_y"]) - np.array(_tv["ov_p"]); _m7 = float(np.mean(_e7 ** 2))
    _TRUE = {"t1": (float(np.log10(_tv["sc_slow"] * 3.6e6 / _tv["sc_fast"])),),
             "t2": (float(_y2.mean()), float(_y2.std(ddof=1))),
             "t3": (float(_tv["wb_C0"] * np.exp(-_k3 * _tv["wb_T"])),
                    float(_tv["wb_C0"] + (_tv["wb_C2"] - _tv["wb_C0"]) / 2 * _tv["wb_T"])),
             "t4": (float(np.log(2) / _tv["pk_k"]), float(_tv["pk_C0"] * np.exp(-_tv["pk_k"] * _tv["pk_t"]))),
             "t5": (float(sum((o - p) ** 2 for o, p in zip(_tv["sse_obs"], _tv["sse_pred"]))),),
             "t6": (_tv["gd_k"] - _tv["gd_lr"] * _tv["gd_g"],),
             "t7": (_m7, _m7 - _tv["ov_tr"]),
             "t8": (2 * _tv["sn_a"] * _tv["sn_mu"],),
             "t9": (4.0 * _tv["mc_r"] / _tv["mc_n"],)}
    if sorted(_HW) != ["t%d" % _i for _i in range(1, 10)]:
        fails.append("Modeling should carry hints on t1–t9, found %r" % sorted(_HW))
    for _hk in sorted(_HW):
        if len(_HW[_hk][2]) != 2:
            fails.append("hint %s: %d steps, the standard is two" % (_hk, len(_HW[_hk][2])))
else:
    _TRUE = {}
# E17.1 (02.10.): the step label is the reader's language ("Hint" / "Hinweis")
_HWD = G["_nbL"]("Hint", "Hinweis") if "_nbL" in G else "Hint"
for _hk, (_hb, _hbody, _hs) in sorted(_HW.items()):
    _st = (G["_TASKS"]["state"].get(_hk), G["_TASKS"]["code"].get(_hk))
    if _hbody.value:
        fails.append("hint %s: shown before it was asked for" % _hk)
    for _i in range(1, len(_hs) + 1):
        _hb.click()
        _n = _hbody.value.count("<b>%s " % _HWD)
        if _n != _i or ("<b>%s %d.</b>" % (_HWD, _i)) not in _hbody.value:
            fails.append("hint %s: after %d clicks %d steps shown" % (_hk, _i, _n))
    _hb.click()
    if _hbody.value:
        fails.append("hint %s: the last click did not hide the hints" % _hk)
    _hb.click()
    if _hbody.value.count("<b>%s " % _HWD) != len(_hs):
        fails.append("hint %s: reopening did not show every step seen" % _hk)
    if G["hints_seen"]().get(_hk) != len(_hs):
        fails.append("hint %s: hints_seen() says %r" % (_hk, G["hints_seen"]().get(_hk)))
    if (G["_TASKS"]["state"].get(_hk), G["_TASKS"]["code"].get(_hk)) != _st:
        fails.append("hint %s: asking for a hint changed the progress state" % _hk)
    _plain = re.sub(r"<[^>]+>", "", " ".join(_hs)).replace("−", "-")
    _plain = re.sub(r"(?<=\d),(?=\d)", ".", _plain)    # E22.2: a German 0,2 is a 0.2
    for _num in re.findall(r"\d+\.\d+", _plain):
        _dp = len(_num.split(".")[1])
        for _t in _TRUE.get(_hk, ()):
            if not isinstance(_t, str) and abs(float(_num) - abs(_t)) <= 0.5 * 10 ** -_dp + 1e-12:
                fails.append("hint %s states a result: %s" % (_hk, _num))
    for _t in _TRUE.get(_hk, ()):
        if isinstance(_t, str):
            if re.search(r"(?<!\w)" + re.escape(_t) + r"(?!\w)", _plain, re.I):
                fails.append("hint %s names the right option: %s" % (_hk, _t))
        elif float(_t).is_integer():
            _m = re.search(r"=\s*\(?\s*-?\s*%d\s*\)?(?!\d|[.,]\d)" % abs(int(_t)), _plain)
            if _m:
                fails.append("hint %s states a result: %s" % (_hk, _m.group(0).strip()))
    if ("Complex" in _which or "Modeling" in _which) and _hk not in _TRUE:
        fails.append("hint %s: no independent result list in this test" % _hk)
print("hints %s: %d steps, click order, no result stated" % (sorted(_HW), len(_HW)))
# the guard itself must bite: a step that states a result is refused
if "hint_steps" not in G:
    fails.append("the toolkit has no hint_steps()")
else:
    for _txt, _fb in (("the answer is 0.639", (-0.6393,)), ("so Re(z1 z2) = (−7)", (-7,)),
                      ("the real part = −7.", (-7,)), ("z is in Quadrant III", ("Quadrant III",))):
        try:
            G["hint_steps"]("_probe", [_txt], forbid=_fb)
            fails.append("hint_steps accepted %r with forbid %r" % (_txt, _fb))
        except ValueError:
            pass
    try:
        G["hint_steps"]("_probe", ["A quadrant is decided by signs; Quadrant II is (−, +); 7 m = 70 dm = 7.5 m − 0.5 m"],
                        forbid=("Quadrant I", 7))
    except ValueError as _e:
        fails.append("hint_steps refused a harmless step: %s" % _e)
for _d in ("_HINT_WIDGETS", "_HINT_SRC"):
    G.get(_d, {}).pop("_probe", None)
print("\n" + ("ALL CHECKS PASSED" if not fails else "FAILURES:\n- " + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
