_intro_txt = (
  "So far the line has produced an unbounded number, which is fine for regression but not for a "
  "<b>yes/no</b> decision. Feeding the same line " + imath("z=w\\,x+b") + " through the "
  "<b>sigmoid</b> squashes any value into a probability between 0 and 1. A line plus a sigmoid is "
  "exactly <b>logistic regression</b>, the simplest classifier" + cite(5, 6) + ".")

info = concept_box(_intro_txt, r"$\sigma(z)=\dfrac{1}{1+e^{-z}},\quad z=w\,x+b$",
    variables=[("&#963;(z)", "probability in (0, 1)"), ("z", "the line <b><i>w·x + b</i></b>"),
               ("w", "steepness"), ("b", "shift")],
    constants=[("<b><i>e</i></b> <b>&#8776; 2.71828</b>", "Euler's number" + cite(15))])

def render_sig(w=1.0, b=0.0):
    z = np.linspace(-10, 10, 200)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(z, sigmoid(w*z + b), color="#2c6e91", lw=2.5)
    ax.axhline(0.5, color="gray", ls=":"); ax.axvline(-b/w if w else 0, color="#b5482e", ls="--")
    ax.set_title("σ(%.1f·z + %.1f)" % (w, b)); ax.set_ylim(-.05, 1.05)
    ax.set_xlabel("z"); ax.set_ylabel("probability"); ax.grid(alpha=.3)
    return fig

def boundary_fig():
    A = rng.normal([-1, -1], 0.7, (60, 2)); B = rng.normal([1.2, 1.2], 0.7, (60, 2))
    Xc = np.vstack([A, B]); yc = np.r_[np.zeros(60), np.ones(60)]; wv = np.zeros(2); bb = 0.0
    for _ in range(2000):
        g = sigmoid(Xc@wv + bb) - yc; wv -= 0.1*(Xc.T@g)/len(yc); bb -= 0.1*g.mean()
    xx, yy = np.meshgrid(np.linspace(-3, 3, 200), np.linspace(-3, 3, 200))
    zz = sigmoid(np.c_[xx.ravel(), yy.ravel()]@wv + bb).reshape(xx.shape)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.contourf(xx, yy, zz, levels=20, cmap="RdBu_r", alpha=.6)
    ax.scatter(A[:, 0], A[:, 1], color="#b5482e", label="class 0")
    ax.scatter(B[:, 0], B[:, 1], color="#2c6e91", label="class 1")
    ax.contour(xx, yy, zz, levels=[0.5], colors="k"); ax.legend()
    acc = ((sigmoid(Xc@wv + bb) > .5) == yc).mean()
    ax.set_title("logistic regression, accuracy %.0f%%" % (acc*100))
    return fig

viz = [viz_intro_box("",
        "The sigmoid " + imath(r"\sigma(z)=1/(1+e^{-z})", color="#6b4a5e") + " turns any real number into "
        "a probability between 0 and 1. The slider <b><i>w</i></b> stretches or compresses the input and "
        "so sets how sharp the switch is, while <b><i>b</i></b> shifts the whole curve left or right along "
        "the axis. Start near " + imath("w=0.3", color="#6b4a5e") + " for a very gentle S-shape, then "
        "raise it toward " + imath("w=5", color="#6b4a5e") + " to see the curve approach a hard step; the "
        "dashed line marks the decision boundary at " + imath(r"\sigma=0.5", color="#6b4a5e") + ".")]
viz += slider_plot(render_sig, {"w": FloatSlider(value=1.0, min=0.1, max=5, step=0.1, description="w"),
                                "b": FloatSlider(value=0.0, min=-5, max=5, step=0.5, description="b")})
viz += [viz_intro_box("",
         "This second plot fits a logistic-regression classifier to two clouds of points and colours the "
         "plane by the predicted probability of belonging to class 1. The black curve is the decision "
         "boundary, the set of points where that probability equals " + imath("0.5", color="#6b4a5e") +
         ", so it separates the two groups; the accuracy in the title says how many points end up on the "
         "correct side of it."),
        plot_html(boundary_fig())]

def check(ns):
    f = ns.get("my_sigmoid")
    if f is None: return False, "Define a function called <code>my_sigmoid</code>."
    z0 = float(f(0)); zp = float(f(100)); zn = float(f(-100))
    if np.isclose(z0, 0.5) and np.isclose(zp, 1.0, atol=1e-3) and np.isclose(zn, 0.0, atol=1e-3):
        return True, ""
    if np.isclose(z0, 0.0):
        return False, "You're returning z unchanged. Pass it through the sigmoid instead of returning it directly."
    if np.isclose(zp, 0.0) and np.isclose(zn, 1.0, atol=1e-3):
        return False, "It's flipped: large z should give ~1. Check the sign of the exponent (it is −z)."
    if np.isclose(z0, 1.0):
        return False, "σ(0) should be 0.5, not 1. Don't forget the +1 in the denominator."
    return False, "σ(0) must be 0.5, σ(large)≈1, σ(−large)≈0; you got %s at z=0. Use 1/(1+np.exp(−z))." % fnum(z0)

practice = [
  exercise_box("",
               taskline("Complete my_sigmoid(z) so that it evaluates the sigmoid function.") +
               formula_line(r"$\sigma(z)=\dfrac{1}{1+e^{-z}}$", color="#7a4a4a") +
               "Read it straight off the formula: negate z, raise <i>e</i> to that power with np.exp(-z), "
               "add one, then take the reciprocal. Because z is already a numpy array the same expression "
               "runs on every element at once, so no loop is needed. As quick sanity checks, the sigmoid "
               "of 0 is 0.5, a large positive z gives almost 1, and a large negative z gives almost 0."),
  editable_exercise(
    "def my_sigmoid(z):\n    z = np.asarray(z, dtype=float)\n    return z\n", check),
  solution_box("Worked version:",
    "def my_sigmoid(z):\n    z = np.asarray(z, dtype=float)\n    return 1.0 / (1.0 + np.exp(-z))")]

interp = interpretation_box(
    "The curve is a soft <b>yes/no switch</b>. A larger weight makes the switch sharper, so the model "
    "becomes more 'confident' near the boundary. Classification is simply a sigmoid placed on top of a "
    "straight line. In the analysis plot the black line is the <b>decision boundary</b> at " +
    imath(r"\sigma=0.5") + ", where the model has learned a straight boundary separating the two groups "
    "of molecules, which shows that classification is just a sigmoid placed on a line.")

build_chapter(5, "From a line to a probability: The sigmoid",
              info=info, viz=viz, practice=practice, interp=interp)
