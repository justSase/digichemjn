"""E28 (2026-10-12, Python) — WHICH NOTEBOOK A GATE SCRIPT TESTS WHEN NONE IS NAMED.
Dauerregel (Nutzer 12.10.): "nur die Vorlage" — the template is the default;
Complex and the others only on request ("--nb complex").

    resolve("vorlage" | "complex" | "modeling" | "<file.ipynb>") -> path

A short name picks the newest build in its folder (version sort, v1.74 > v1.9).
No build there → SystemExit with the build command: a gate that cannot find
its notebook must stop red, never test something else."""
import os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NBS = {"vorlage":  ("vorlage",  "Vorlage_v*.ipynb",                    "cd vorlage && python3 build_vorlage.py"),
       "complex":  ("complex",  "Complex_Numbers_Step_by_Step_v*.ipynb", "cd complex && python3 build_complex.py"),
       "modeling": ("modeling", "Introduction_to_Modeling_v*.ipynb",     "cd modeling && python3 build_modeling.py")}
DEFAULT = "vorlage"

def _ver(p):
    m = re.search(r"_v(\d+)\.(\d+)", os.path.basename(p))
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

def resolve(name=None):
    name = name or DEFAULT
    if name.endswith(".ipynb") or os.sep in name or "/" in name:
        return name
    if name not in NBS:
        raise SystemExit("--nb %s: unknown (vorlage | complex | modeling | <file.ipynb>)" % name)
    d, pat, how = NBS[name]
    hits = sorted(glob.glob(os.path.join(ROOT, d, pat)), key=_ver)
    if not hits:
        raise SystemExit("--nb %s: no build in %s/ — first: %s" % (name, d, how))
    return hits[-1]

def from_argv(argv, default=None):
    """The suites' old calling convention: argv[1] a file, or --nb <name>, or nothing."""
    if "--nb" in argv:
        i = argv.index("--nb")
        return resolve(argv[i + 1] if i + 1 < len(argv) else None)
    # a notebook is a file .ipynb or a short name — never the value of another option (--shots DIR)
    files = [a for a in argv[1:] if a.endswith(".ipynb") or a in NBS]
    return resolve(files[0] if files else default)

def argv_fix(argv, default=None):
    """In place: argv[1] becomes the notebook (resolved; --nb <name> or nothing →
    the template), the other arguments keep their order. For the suites that
    read sys.argv[1] (test_nb, test_checks, test_gating, …)."""
    rest, i, name = [], 1, None
    while i < len(argv):
        a = argv[i]
        if a == "--nb" and i + 1 < len(argv):
            name, i = argv[i + 1], i + 2; continue
        rest.append(a); i += 1
    if name is None:
        for j, a in enumerate(rest):
            if a.endswith(".ipynb") or a in NBS:
                name = rest.pop(j); break
    argv[1:] = [resolve(name or default)] + rest
    return argv[1]
