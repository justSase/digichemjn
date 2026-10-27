_intro_txt = (
  "Tokens are now <b>vectors</b> whose closeness reflects meaning. Attention is the mechanism that "
  "lets those vectors <b>interact</b>: every token forms a query and compares it to the keys of all "
  "other tokens, then mixes their values by how relevant they are. This operation is the defining "
  "component of the <b>transformer</b> and therefore of every modern large language model" + cite(3) + ".")

info = concept_box(_intro_txt, r"$\mathrm{weights}=\mathrm{softmax}\!\left(\dfrac{q\cdot K^{\top}}{\sqrt{d}}\right),\ \ \mathrm{output}=\mathrm{weights}\cdot V$",
    variables=[("q", "the query vector (what a token looks for)"),
               ("K", "keys of all tokens"), ("V", "values of all tokens"),
               ("d", "key dimension (scales the scores)")],
    function="A token's query is compared to every key; softmax turns the scores into weights that sum to 1; "
             "the output mixes the values accordingly.")

def render(qx=0.25, qy=0.85):
    words = ["cat", "sat", "on", "mat"]
    K = np.array([[0.2, 0.9], [0.6, 0.5], [0.1, 0.2], [0.3, 0.8]]); V = np.array([1., 2., 3., 4.])
    weights = softmax(K@np.array([qx, qy])/np.sqrt(2))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(words, weights, color="#2c6e91"); ax.set_ylim(0, 1); ax.set_ylabel("attention weight")
    ax.set_title("query (%.2f, %.2f) → context %s" % (qx, qy, fnum(float(weights@V))))
    return fig

viz = [viz_intro_box("",
        "Four tokens each carry a fixed two-dimensional <b>key</b>. The two sliders set the <b>query</b> "
        "vector, and the bar chart shows the resulting attention weight on each token together with the "
        "mixed output value in the title. Move the query around and watch the weight shift toward "
        "whichever token's key it most resembles; because the weights come from a softmax they always "
        "stay positive and add up to 1, so paying more attention to one token necessarily means paying "
        "less to the others.")]
viz += slider_plot(render, {"qx": FloatSlider(value=0.25, min=0, max=1, step=0.05, description="qx"),
                            "qy": FloatSlider(value=0.85, min=0, max=1, step=0.05, description="qy")})

def check(ns):
    f = ns.get("my_softmax")
    if f is None: return False, "Define a function called <code>my_softmax</code>."
    out = np.asarray(f([1.0, 2.0, 3.0]), dtype=float)
    s = float(np.sum(out))
    if np.isclose(s, 1.0) and np.argmax(out) == 2 and np.all(out >= 0):
        return True, ""
    if np.allclose(out, [1.0, 2.0, 3.0]):
        return False, "You're still returning the scores unchanged. Exponentiate them first with np.exp."
    if np.all(out >= 0) and not np.isclose(s, 1.0):
        return False, "Good, the values are ≥ 0, but they must also sum to 1. Divide each by their total."
    if np.any(out < 0):
        return False, "Probabilities can't be negative. Exponentiate before normalising."
    return False, "The result must be ≥ 0 and sum to 1 (yours sums to %s). exp, then divide by the sum." % fnum(s)

practice = [
  exercise_box("",
               taskline("Complete my_softmax(z) so that it turns a vector of scores into a probability "
                        "distribution.") +
               formula_line(r"$\mathrm{softmax}(z)_i=\dfrac{e^{z_i}}{\sum_j e^{z_j}}$", color="#7a4a4a") +
               "In words: exponentiate every score with np.exp so all values become positive, then "
               "divide each one by the sum of them all so the whole vector adds up to 1. One practical "
               "tip for numerical stability is to subtract the largest score from every element first, "
               "writing z - z.max(); this leaves the result unchanged but stops np.exp from overflowing "
               "on large inputs."),
  editable_exercise(
    "def my_softmax(z):\n    z = np.asarray(z, dtype=float)\n    return z\n", check),
  solution_box("Worked version:",
    "def my_softmax(z):\n    z = np.asarray(z, dtype=float)\n    z = z - z.max()\n    e = np.exp(z)\n    return e / e.sum()")]

interp = interpretation_box(
    "The bars are the <b>attention weights</b>, showing how much the query 'looks at' each token. They always sum to "
    "1, because they come from the <b>softmax</b> you just implemented. A query near a token's key puts most "
    "weight there. Stacking many such attention operations is the core mechanism of every transformer/LLM.")

build_chapter(10, "Attention: The heart of the transformer",
              info=info, viz=viz, practice=practice, interp=interp)
