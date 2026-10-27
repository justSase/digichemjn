# ---------------------------------------------------------------------------
# DigiChemJN · Sets — domain setup
# Source of the content: L. Heidinger, "Principles of Biophysics &
# Computational methods", Univ. Freiburg, script 2025 V6.1,
# section 1.1 "Sets" (pp. 17-25).
# ---------------------------------------------------------------------------

use_profile("biophysics")
use_style("quiet")
set_notebook("sets", "Sets")

set_metadata(
    title="Sets",
    subtitle="Principles of Biophysics & Computational methods, section 1.1",
    authors=["… Autor:innen bitte eintragen …"],
    institution="Fakultät für Chemie und Pharmazie, Albert-Ludwigs-Universität Freiburg",
    licence="CC BY-SA 4.0",
    licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    version=NB_VERSION,
    date="2026-09",
    doi="",
    repo="",
    audience="Master Chemie, Biochemie & Biophysik, Pharmazeutische Wissenschaften, "
             "Sustainable Materials — from the 7th semester",
    prerequisites="School algebra; no programming knowledge required",
    duration="75–100 minutes",
    keywords=["sets", "set operations", "De Morgan", "Cartesian product",
              "number sets", "binomial coefficient", "OER", "Jupyter", "DigiChemJN"],
    source="L. Heidinger, Principles of Biophysics & Computational methods, "
           "Univ. Freiburg, script 2025 V6.1, section 1.1 (pp. 17–25)",
)
inject_style()

# --- personal task values -------------------------------------------------
SET_SEED = notebook_seed(int(_NBID, 16) % 100000)
_rng = np.random.default_rng(SET_SEED)


def _pick(lo, hi, n):
    """n distinct integers from [lo, hi], sorted."""
    return sorted(int(v) for v in _rng.choice(range(lo, hi + 1), size=n, replace=False))


# Two overlapping sets the reader carries through the whole notebook. The
# overlap is forced to be non-empty and not everything, so ∩, ∪ and \ all say
# something different — an exercise whose answer is ∅ teaches nothing.
_pool = list(range(1, 13))
_A = sorted(int(v) for v in _rng.choice(_pool, size=6, replace=False))
_rest = [v for v in _pool if v not in _A]
_shared = sorted(int(v) for v in _rng.choice(_A, size=int(_rng.integers(2, 4)), replace=False))
_only_b = sorted(int(v) for v in _rng.choice(_rest, size=3, replace=False))
_B = sorted(_shared + _only_b)

TV = dict(
    A=_A, B=_B, M=_pool,
    dice=int(_rng.integers(4, 9)),          # faces on the die, for the product
    coin=int(_rng.integers(2, 4)),          # sides of the second set
    n_sum=int(_rng.integers(4, 9)),         # upper limit of the sum
    m_sum=int(_rng.integers(1, 4)),         # lower limit of the sum
    fact=int(_rng.integers(4, 8)),          # n!
    n_ch=int(_rng.integers(6, 11)),         # n choose k
    k_ch=int(_rng.integers(2, 5)),
)
# k must be smaller than n, whatever the seed handed us
if TV["k_ch"] >= TV["n_ch"]:
    TV["k_ch"] = max(2, TV["n_ch"] - 2)
if TV["m_sum"] >= TV["n_sum"]:
    TV["m_sum"] = 1


def setstr(s):
    """A set the way the script writes it: {1, 2, 3}."""
    return "{" + ", ".join(str(int(v)) for v in sorted(s)) + "}"


_seed_html = (
    "<div style='margin-top:10px;font-size:.94em'>Your personal numbers come from the "
    "seed <b>%d</b>. The same seed always gives the same numbers, so any result you "
    "write down stays reproducible — you can pin or change it in the ⚙ drawer of the "
    "panel.</div>" % SET_SEED)

# --- the tasks, declared up front so the progress strip is complete --------
register_tasks([
    ("t1", "1 · what a set is",   "ch1"),
    ("t2", "2 · ∩ ∪ and \\",      "ch2"),
    ("t3", "3 · how many",        "ch3"),
    ("t4", "4 · De Morgan",       "ch4"),
    ("t5", "5 · number sets",     "ch5"),
    ("t6", "6 · Σ and Π",         "ch6"),
    ("t7", "7 · choose",          "ch7"),
    ("q1", "8 · multiple choice", "quiz"),
    ("b1", "9 · own data",        "byod"),
])

# --- bibliography ---------------------------------------------------------
BIB = {
 1: 'L. Heidinger, <i>Principles of Biophysics &amp; Computational methods</i>, '
    'Albert-Ludwigs-Universität Freiburg, script 2025 V6.1, section 1.1 “Sets”, pp. 17–25.',
 2: 'P. R. Halmos, <i>Naive Set Theory</i>, Springer, 1974. ISBN 978-0-387-90092-6.',
 3: 'K. F. Riley, M. P. Hobson, S. J. Bence, <i>Mathematical Methods for Physics and '
    'Engineering</i>, 3rd ed., Cambridge University Press, 2006.',
 4: 'IUPAC-IUBMB Joint Commission on Biochemical Nomenclature, “Nomenclature and symbolism '
    'for amino acids and peptides”, <i>Pure Appl. Chem.</i> <b>56</b>, 595–624 (1984). '
    'DOI: <a href="https://doi.org/10.1351/pac198456050595" target="_blank">10.1351/pac198456050595</a>',
 5: 'M. D. Wilkinson et al., “The FAIR Guiding Principles for scientific data management and '
    'stewardship”, <i>Sci. Data</i> <b>3</b>, 160018 (2016). '
    'DOI: <a href="https://doi.org/10.1038/sdata.2016.18" target="_blank">10.1038/sdata.2016.18</a>',
}

# the title page is the first bar on the timeline
notebook_start()
