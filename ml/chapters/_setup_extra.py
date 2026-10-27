
# ----- notebook-specific setup (helpers, data, models) -----
import warnings
warnings.filterwarnings("ignore")   # hide library deprecation/runtime warnings (e.g. Pyodide/threadpoolctl)

rng = np.random.default_rng(0)                      # fixed seed → reproducible (K1/K5)

def mse(y_true, y_pred):
    return float(np.mean((np.asarray(y_true) - np.asarray(y_pred))**2))

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.asarray(z, dtype=float)))

def softmax(z):
    z = np.asarray(z, dtype=float); z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z); return e / e.sum(axis=-1, keepdims=True)

# fixed synthetic data for the loss / gradient-descent chapters:  y ≈ 2.3·x + 1  (+ noise)
xd = np.linspace(0, 10, 30); yd = 2.3*xd + 1.0 + rng.normal(0, 1.5, xd.size)

# --------------------------------------------------------------------------
# Simulated demonstration dataset for the "Bring your own data" chapter.
# A synthetic aqueous-solubility set (600 molecules) whose target logS follows
# the well-known Delaney "ESOL" linear relationship between simple descriptors.
# It is CLEARLY SIMULATED (fixed seed) and for teaching only; for real work use a
# measured, licensed dataset such as ESOL / AqSolDB and cite its DOI (FAIR, K1/K5).
_rngd = np.random.default_rng(20240815)
_Nd   = 600
_logP = np.clip(_rngd.normal(2.4, 1.5, _Nd), -1.5, 6.5)          # lipophilicity
_MW   = np.clip(_rngd.normal(310, 90, _Nd), 120, 600)            # molecular weight
_TPSA = np.clip(_rngd.normal(70, 35, _Nd), 5, 180)              # polar surface area
_HBD  = _rngd.integers(0, 6,  _Nd).astype(float)                # H-bond donors
_HBA  = _rngd.integers(1, 11, _Nd).astype(float)                # H-bond acceptors
_RotB = _rngd.integers(0, 11, _Nd).astype(float)                # rotatable bonds
_AP   = np.clip(_rngd.normal(0.4, 0.2, _Nd), 0.0, 0.9)          # aromatic proportion
# Delaney ESOL-style ground truth + measurement noise
_logS = (0.16 - 0.63*_logP - 0.0062*_MW + 0.066*_RotB - 0.74*_AP
         + _rngd.normal(0, 0.5, _Nd))
demo_cols = ["logP", "MW", "TPSA", "HBD", "HBA", "RotB", "AP", "logS"]
demo_data = np.column_stack([_logP, _MW, _TPSA, _HBD, _HBA, _RotB, _AP, _logS])

# tiny bigram language model for chapter 13
corpus = ("the cat sat on the mat . the cat ran to the dog . "
          "the dog sat on the mat . a dog ran to a cat .").split()
bg_vocab = sorted(set(corpus)); bg_idx = {w: i for i, w in enumerate(bg_vocab)}
BG = np.ones((len(bg_vocab), len(bg_vocab))) * 0.1
for _a, _b in zip(corpus[:-1], corpus[1:]): BG[bg_idx[_a], bg_idx[_b]] += 1

# ----- multiple-choice quiz (defined here so the quiz section is a one-liner) -----
def MC(q, options):
    """options: list of (text, is_correct, feedback) -> a jupyterquiz question."""
    return {"question": q, "type": "multiple_choice",
            "answers": [{"answer": t, "correct": c, "feedback": f} for (t, c, f) in options]}

questions = [
 MC("In ŷ = w·x + b, b is the…",
    [("intercept", True, "Yes, b shifts the line vertically."),
     ("slope", False, "That's w."),
     ("learning rate", False, "A training knob, not part of the model."),
     ("loss", False, "The loss measures error, not the line.")]),
 MC("Training loss = 0 tells you the model…",
    [("fits the training data exactly", True, "Right, and it may still fail on new data (overfitting)."),
     ("will generalise perfectly", False, "Zero train loss can mean memorised noise."),
     ("has too few parameters", False, "That would give high loss, not zero."),
     ("was trained too briefly", False, "Zero loss means it fit the data, not that it stopped early.")]),
 MC("Too large a learning rate makes training…",
    [("diverge / oscillate", True, "Steps overshoot the minimum."),
     ("converge slowly", False, "That's a rate too small."),
     ("use fewer parameters", False, "Capacity is unrelated to the rate."),
     ("overfit faster", False, "Overfitting is about capacity, not step size.")]),
 MC("Without a non-linear activation, stacked layers…",
    [("collapse to one linear map", True, "So depth adds no power."),
     ("still fit any curve", False, "Only the non-linearity lets them bend."),
     ("stop being differentiable", False, "Linear maps are differentiable."),
     ("output probabilities", False, "That needs a sigmoid/softmax, not linearity.")]),
 MC("The sigmoid turns a score into…",
    [("a probability in (0,1)", True, "One squashed value."),
     ("a class label 0 or 1", False, "Only after you threshold it."),
     ("values that sum to 1", False, "That's softmax over a vector."),
     ("a gradient", False, "It's an activation, not a derivative.")]),
 MC("Softmax returns…",
    [("values ≥ 0 that sum to 1", True, "A probability distribution."),
     ("a single value in (0,1)", False, "That's the sigmoid."),
     ("the largest input only", False, "That's argmax, not softmax."),
     ("the model's weights", False, "It transforms scores, not parameters.")]),
 MC("Logistic regression is a line…",
    [("passed through a sigmoid", True, "w·x+b, then squashed to a probability."),
     ("passed through a softmax", False, "Softmax is for several classes at once."),
     ("fitted by k-means", False, "k-means is unsupervised clustering."),
     ("scored by MSE", False, "Classification uses a probability loss, not MSE.")]),
 MC("Train error falls, test error rises. This is…",
    [("overfitting", True, "Memorising noise; keep a test set."),
     ("underfitting", False, "That keeps both errors high."),
     ("class imbalance", False, "A metric issue, not this curve."),
     ("a rate too small", False, "Complexity, not step size, drives this.")]),
 MC("Attention weights are the…",
    [("softmax of query·key scores", True, "They sum to 1 across tokens."),
     ("cosine of the embeddings", False, "Close idea (a dot product), but not the definition."),
     ("sigmoid of the values", False, "Values are mixed after, not squashed."),
     ("gradient of the loss", False, "No loss is computed here.")]),
 MC("GD, logistic regression and LLM training all…",
    [("lower a loss via gradients", True, "The same engine at every scale."),
     ("end in a softmax layer", False, "Often true, but not the shared core."),
     ("need labelled images", False, "None needs images specifically."),
     ("start with k-means", False, "Clustering isn't part of them.")]),
 MC("Embedding closeness is measured by…",
    [("cosine similarity", True, "Angle between the vectors."),
     ("mean squared error", False, "A regression loss, not a similarity."),
     ("softmax probability", False, "That normalises scores, not distance."),
     ("the learning rate", False, "A training knob, not a measure.")]),
 MC("More capacity raised test error. Best fix?",
    [("reduce capacity or add data", True, "Attack the overfitting directly."),
     ("train for more epochs", False, "Real knob, but it worsens overfitting."),
     ("raise the learning rate", False, "Real knob, but unrelated to this."),
     ("lower the temperature", False, "Temperature is for generation, not this.")]),
 MC("With 95% accuracy on data that is 95% one class, what do you check…",
    [("precision and recall", True, "Accuracy hides an 'always-majority' model."),
     ("the R² score", False, "R² is for regression, not this."),
     ("the training loss", False, "Useful, but it won't reveal the imbalance."),
     ("the learning rate", False, "Irrelevant to the metric problem.")]),
 MC("Lowering temperature toward 0 makes output…",
    [("more deterministic", True, "Safer but less creative."),
     ("more diverse", False, "That's higher temperature."),
     ("more factually correct", False, "It doesn't fix wrong facts."),
     ("shorter", False, "Length isn't set by temperature.")]),
 MC("An LLM invents a citation because it…",
    [("optimises plausibility, not truth", True, "Verify every fact against sources."),
     ("overfit its training data", False, "Real concept, but not the cause here."),
     ("used too low a temperature", False, "Low T doesn't cause hallucination."),
     ("had a non-normalised softmax", False, "Technical-sounding, but not the reason.")]),
]

def show_quiz():
    """Render the quiz (defined above in setup). Falls back to plain text."""
    try:
        from jupyterquiz import display_quiz
        display_quiz(questions)
    except Exception as e:
        print("jupyterquiz not available (%s). Questions as text:" % e)
        for i, q in enumerate(questions, 1):
            print("\n%d. %s" % (i, q["question"]))
            for a in q["answers"]:
                print("   [%s] %s" % ("x" if a["correct"] else " ", a["answer"]))

use_profile("bioinformatics")
set_notebook("ml-llm-ai", "Machine Learning, LLMs & AI")
inject_style()
# (no "Ready." print — the input bar is hidden, so any stray output would show)
