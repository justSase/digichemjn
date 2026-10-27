
# ---------------------------------------------------------------------------
# DigiChemJN · Introduction to Modeling — domain setup
# Source of the content: lecture "Vertiefende Methoden der Bioinformatik —
# Introduction to Modeling" (S. Günther, S. Rockwell-Kollmann), Univ. Freiburg,
# WS 2025/26.
# 2026-09-30 (E10 Teil 4, Python) — brought to the standard of Complex:
# profile + style + OER record first, goals, personal numbers drawn by a
# function (reseed in place), mode, tasks with names, then the data.
# ---------------------------------------------------------------------------
import warnings
warnings.filterwarnings("ignore")

# Subject standard first (it may override DESIGN), then the stylesheet.
use_profile("biophysics")
# the document speaks the panel's language: one quiet surface, colour only for state
use_style("quiet")
set_notebook("intro-modeling", "Introduction to Modeling")
# --- OER record (FCI proposal: open licence, metadata, DOI, versioning) -----
# duration and objectives are NOT typed: refs_m.py writes them in at the end,
# from time_budget_text() and register_goals() — one source each.
set_metadata(
    title="Introduction to Modeling",
    subtitle="Perception, calibration, validation and sensitivity",
    authors=["… Autor:innen bitte eintragen …"],
    institution="Fakultät für Chemie und Pharmazie, Albert-Ludwigs-Universität Freiburg",
    licence="CC BY-SA 4.0",
    licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    version=NB_VERSION,
    date="2026-09",
    doi="",                     # reserved on the Zenodo deposit
    repo="",                    # GitHub URL once the module is published
    audience="Master Chemie, Biochemie & Biophysik, Pharmazeutische Wissenschaften, "
             "Sustainable Materials — from the 7th semester",
    prerequisites="School algebra and the exponential function; no programming knowledge required",
    keywords=["modeling", "pharmacokinetics", "calibration", "objective function",
              "gradient descent", "sensitivity analysis", "Monte-Carlo", "OER", "DigiChemJN"],
    source="Lecture 'Vertiefende Methoden der Bioinformatik — Introduction to Modeling' "
           "(S. Günther, S. Rockwell-Kollmann), Univ. Freiburg, WS 2025/26",
)
inject_style()

# --- learning goals: declared ONCE, read by the Introduction, the OER record
# and the title card. K-tag · level · what the reader can do. One tag per goal
# (the old list carried pairs such as "K3/K4"; the primary one is kept). In the
# biophysics standard K2 ("implement it") is absent: every exercise is solved
# by entering numbers, code is the optional second route.
register_goals([
 # one line each on the cold card (E10 Teil 4: with nine chapters the card
 # pushed Play below a 900 px window)
 ("K4", "basic", "explain the reality–observation–model relationship and the three modeling stages"),
 ("K4", "basic", "tell white-box from black-box models and judge which one suits a question"),
 ("K3", "intermediate", "compute a calibration objective and take one step of the search that minimises it"),
 ("K5", "intermediate", "check a calibrated model for under- and overfitting with a train–test split"),
 ("K4", "advanced", "measure a parameter's influence by a central difference and sample by Monte-Carlo"),
 ("K6", "advanced", "apply the workflow to your own PK data and document it reproducibly (FAIR)"),
])

# --- personal task values -------------------------------------------------
# Seeded from the per-run notebook id (or the seed pinned in the ⚙ drawer), so
# two students almost never get the same numbers; same seed -> same numbers.
MOD_SEED = notebook_seed(int(_NBID, 16) % 100000)
# R3 · 18 — which content this run builds (calc / code / both), read once,
# before the first chapter: DIGICHEM_MODE, else the stored choice, else both
MOD_MODE = notebook_mode()

# `_draw_tv` is a function so a reseed (⚙ drawer, in place) and a seed sweep can
# call it without the notebook. Every number is SIMULATED. The level is taken
# for the interface of reseed(); in this notebook the levels change only the
# tolerance, not the numbers.
def _draw_tv(rng, level=None):
    def nzi(lo, hi):
        v = 0
        while v == 0:
            v = int(rng.integers(lo, hi + 1))
        return v
    # chapter 5: the objective of one guess
    obs = [int(v) for v in rng.integers(20, 90, 3)]
    res = [nzi(-4, 4) for _ in range(3)]
    while len({abs(r) for r in res}) == 1:
        res[2] = nzi(-4, 4)
    mcn = int(rng.choice([200, 400, 500, 1000]))
    tv = dict(
        sse_obs  = obs,                                    # t5: observed concentrations
        sse_pred = [o - r for o, r in zip(obs, res)],      #     model predictions
        gd_k  = float(rng.choice([0.2, 0.3, 0.4, 0.5])),   # t6: rate constant 1/h
        gd_g  = float(nzi(-8, 8)),
        gd_lr = float(rng.choice([0.01, 0.02, 0.05])),
        sn_a  = float(rng.choice([0.5, 1.5, 2.0, 3.0])),   # t8: F(μ) = a·μ²
        sn_mu = float(rng.integers(2, 7)),
        sn_d  = float(rng.choice([0.5, 1.0])),             # large enough that a one-sided
                                                           # difference cannot pass as right
        mc_n  = mcn,                                       # t9: points thrown
        mc_r  = int(round(mcn * np.pi / 4 + rng.integers(-mcn // 50, mcn // 50 + 1))),
    )
    # a rate constant stays positive, and the step is big enough that the uphill
    # answer cannot pass within the gentle tolerance (measured 27.09.: lr 0.01
    # with g = ±1 made k ± 0.01 indistinguishable)
    # (E10 Teil 4) …and the new k is never the learning rate itself: the hint
    # prints lr, and a hint that shows the answer is refused (hint_steps)
    while (tv["gd_k"] - tv["gd_lr"] * tv["gd_g"] < 0.05
           or abs(tv["gd_lr"] * tv["gd_g"]) < 0.05
           or abs(tv["gd_k"] - tv["gd_lr"] * tv["gd_g"] - tv["gd_lr"]) < 0.006):
        tv["gd_g"] = float(nzi(-8, 8))
    # the chapters that had no exercise until 27d — drawn AFTER the values above
    m2o = [int(v) for v in rng.integers(35, 56, 4)]
    while len(set(m2o)) < 3:
        m2o = [int(v) for v in rng.integers(35, 56, 4)]
    m3C0 = float(rng.choice([80.0, 100.0, 120.0]))
    m3k = float(rng.choice([0.2, 0.25, 0.3, 0.4]))
    m7y = [round(float(v), 1) for v in rng.uniform(-1.0, 1.0, 3)]
    m7tr = round(float(rng.uniform(0.02, 0.06)), 3)
    m7e = [0.0, 0.0, 0.0]
    # distinct errors, none small, and a gap of at least 0.05 so its sign is never moot
    while (len({abs(e) for e in m7e}) < 3 or min(abs(e) for e in m7e) < 0.1
           or sum(e * e for e in m7e) / 3 - m7tr < 0.05):
        m7e = [round(float(v), 1) for v in rng.uniform(-0.8, 0.8, 3)]
    tv.update(
        sc_fast = int(rng.choice([1, 2, 5, 10, 20, 50])),                 # t1: ms
        sc_slow = int(rng.choice([6, 12, 24, 48, 72])),                   #     h
        ob_y  = m2o,                                                      # t2: four repeats
        wb_C0 = m3C0, wb_C2 = round(m3C0 * float(np.exp(-2 * m3k)), 1),   # t3
        wb_T  = int(rng.choice([6, 8, 10])),
        pk_C0 = float(rng.choice([60.0, 80.0, 100.0, 120.0, 150.0])),     # t4
        pk_k  = float(rng.choice([0.15, 0.2, 0.25, 0.35, 0.5])),          # not near ln 2
        pk_t  = int(rng.choice([2, 3, 4, 6, 8])),
        ov_y  = m7y, ov_p = [round(y - e, 1) for y, e in zip(m7y, m7e)],  # t7
        ov_tr = m7tr,
    )
    return tv

TV = _draw_tv(np.random.default_rng(MOD_SEED))
# the ⚙ seed buttons draw again IN PLACE: TV is refilled (same dict), and the
# chapters' on_reseed hooks recompute what they derived from it
personal_draw(lambda seed: TV.update(_draw_tv(np.random.default_rng(seed))))

def _near(v, want):
    """The answer check's tolerance: the difficulty setting (tol()), plus half a
    unit in the third decimal so that a correctly ROUNDED answer always passes."""
    return abs(float(v) - want) <= tol() * max(1.0, abs(want)) + 5e-4

def _g3(x):
    """A number for a worked line: at most three decimals, no trailing zeros."""
    s = ("%.3f" % float(x)).rstrip("0").rstrip(".")
    return s.replace("-", "−")

# --- the tasks, declared up front so the progress strip is complete --------
# (key, label, anchor of the chapter, name on the timeline)
register_tasks([
    ("t1", "1 · scales",             "ch1",  "Scales of a drug model"),
    ("t2", "2 · noisy observations", "ch2",  "Noisy observations"),
    ("t3", "3 · white vs black box", "ch3",  "White box against black box"),
    ("t4", "4 · half-life",          "ch4",  "Half-life and what is left"),
    ("t5", "5 · the objective",      "ch5",  "The objective of one guess"),
    ("t6", "6 · one search step",    "ch6",  "One step downhill"),
    ("t7", "7 · test error",         "ch7",  "Test error and gap"),
    ("t8", "8 · sensitivity",        "ch8",  "Central difference"),
    ("t9", "9 · Monte-Carlo π",      "ch9",  "π from a sample"),
    # E25.l (08.10.): q1 (quiz) and b1 (own data) out for now; sources stay
])


rng = np.random.default_rng(0)                      # fixed seed → reproducible (K1/K5)

def sse(y_true, y_pred):
    """Sum of squared errors — the objective used for calibration in this notebook."""
    y_true = np.asarray(y_true, float); y_pred = np.asarray(y_pred, float)
    return float(np.sum((y_true - y_pred)**2))

def pk(t, C0, k):
    """First-order (one-compartment) elimination: concentration over time."""
    return C0 * np.exp(-k * np.asarray(t, float))

# --------------------------------------------------------------------------
# Simulated single-dose pharmacokinetic data (one-compartment, first-order
# elimination). Realistic order of magnitude for an intravenous antibiotic
# such as cefazolin, but CLEARLY SIMULATED (fixed seed) and for teaching only.
# For real analyses use measured, licensed data and cite its DOI (FAIR, K1/K5).
# Shape follows the classic C(t) = C0 * exp(-k t) model taught in the notebook.
# --------------------------------------------------------------------------
C0_TRUE, K_TRUE = 100.0, 0.35                       # mg/L, 1/h  (half-life ~2 h)
t_obs = np.array([0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12], dtype=float)
# proportional (log-normal) assay noise, ~12% CV — the realistic error model for a
# concentration assay, and the one under which log-linear calibration is unbiased.
c_obs = pk(t_obs, C0_TRUE, K_TRUE) * np.exp(rng.normal(0, 0.12, t_obs.size))

# --------------------------------------------------------------------------
# A second synthetic set for the over-/underfitting chapter: a smooth curve
# with noise, sampled so that a train and a test split can be formed.
# --------------------------------------------------------------------------
def _truth(x):
    return np.sin(2*np.pi*x)
_xp = np.linspace(0, 1, 30)
_yp = _truth(_xp) + rng.normal(0, 0.25, _xp.size)

# ----- multiple-choice quiz -----
def MC(q, options):
    return {"question": q, "type": "multiple_choice",
            "answers": [{"answer": t, "correct": c, "feedback": f} for (t, c, f) in options]}

questions = [
 MC("The three modeling stages, in order, are…",
    [("perceptual → conceptual → procedural", True, "Yes: understand the system, formalise it, then implement it."),
     ("procedural → conceptual → perceptual", False, "That reverses the workflow."),
     ("conceptual → perceptual → procedural", False, "Perception (system understanding) comes first."),
     ("calibration → validation → perception", False, "Those come after a model exists.")]),
 MC("A white-box (physics-based) model is one that…",
    [("is built from known mechanisms and laws", True, "White means the mechanism is transparent and explicit."),
     ("learns only from data with no mechanism", False, "That describes a black-box, data-driven model."),
     ("cannot be written down as equations", False, "White-box models are exactly the equation-based ones."),
     ("is always more accurate than any other", False, "Accuracy depends on the problem and the data, not on the colour.")]),
 MC("Calibration of a model means…",
    [("adjusting its parameters so it fits observed data", True, "Right. This is usually done by minimising an objective function."),
     ("collecting more observations", False, "That is data gathering, not calibration."),
     ("writing the simulation code", False, "That is the procedural stage."),
     ("choosing the plot colours", False, "That is cosmetics, not calibration.")]),
 MC("An objective (loss) function in calibration measures…",
    [("the difference between predicted and observed data", True, "Calibration minimises exactly this."),
     ("the runtime of the code", False, "Speed is not the objective here."),
     ("the number of parameters", False, "That relates to complexity, not the objective."),
     ("the size of the dataset", False, "That is unrelated to the objective value.")]),
 MC("Low training error but high test error is a sign of…",
    [("overfitting", True, "The model has memorised the noise and fails on new data."),
     ("underfitting", False, "Underfitting keeps BOTH errors high."),
     ("perfect calibration", False, "A good calibration must also work on new data."),
     ("too little model capacity", False, "Too little capacity gives underfitting.")]),
 MC("In the bias–variance picture, high bias corresponds to…",
    [("underfitting (too simple a model)", True, "High bias is the systematic error of an over-simple model."),
     ("overfitting (too flexible a model)", False, "That is high variance."),
     ("random measurement noise", False, "Noise is irreducible error, not bias."),
     ("a large learning rate", False, "The learning rate is unrelated to bias.")]),
 MC("Cross-validation is used to…",
    [("estimate how well a model generalises to unseen data", True, "It holds out different parts (folds) of the data in turn."),
     ("increase the size of the dataset", False, "It reuses the same data and adds none."),
     ("speed up the optimisation", False, "It usually costs more computing time, not less."),
     ("remove all noise from the data", False, "Noise cannot be removed this way.")]),
 MC("One-factor-at-a-time (OFAT) sensitivity analysis…",
    [("varies a single parameter while holding the others fixed", True, "Simple and local, but it misses interactions."),
     ("varies all parameters simultaneously at random", False, "That is closer to a global (Monte-Carlo) approach."),
     ("removes the least important parameter", False, "It measures influence; it does not delete parameters."),
     ("is a way to train neural networks", False, "It is a sensitivity method, not a training method.")]),
 MC("Monte-Carlo methods estimate a quantity by…",
    [("repeated random sampling of the inputs", True, "Many random draws, taken together, approximate the answer."),
     ("solving the problem exactly with algebra", False, "Monte-Carlo is used when exact solutions are impractical."),
     ("using a single best-guess input", False, "A single input value is not Monte-Carlo."),
     ("sorting the data", False, "Sorting is unrelated.")]),
 MC("“All models are wrong, but some are useful” is attributed to…",
    [("George Box", True, "Box, 1976: the classic reminder to judge models by their usefulness."),
     ("Thomas Bayes", False, "Bayes gave us the theorem, not this quote."),
     ("Claude Shannon", False, "Shannon founded information theory."),
     ("Isaac Newton", False, "Not Newton.")]),
]

def show_quiz():
    try:
        from jupyterquiz import display_quiz
        display_quiz(questions)
    except Exception as e:
        print("jupyterquiz not available (%s). Questions as text:" % e)
        for i, q in enumerate(questions, 1):
            print("\n%d. %s" % (i, q["question"]))
            for a in q["answers"]:
                print("   [%s] %s" % ("x" if a["correct"] else " ", a["answer"]))


# the title page is the first bar on the timeline: the marker and the
# scrollbar start there, not a screen further down at the Introduction
notebook_start()
