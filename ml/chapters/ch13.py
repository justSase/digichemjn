info = note_box(
  "Attention and embeddings gave a model a way to relate tokens; a language model puts these to work "
  "by predicting the <b>next token</b>" + cite(9) + ". Our tiny <b>bigram</b> model learns, for each "
  "word, the distribution over the next word. <b>Temperature</b> then reshapes that distribution "
  "before sampling: low values are safe and repetitive, high values are creative and erratic" +
  cite(10) + ".")

def render(temperature=1.0, start="the"):
    r = np.random.default_rng(0); out = [start]; cur = start
    for _ in range(12):
        probs = softmax(np.log(BG[bg_idx[cur]].astype(float))/max(temperature, 1e-6))
        cur = bg_vocab[r.choice(len(bg_vocab), p=probs)]; out.append(cur)
    probs = softmax(np.log(BG[bg_idx[start]].astype(float))/max(temperature, 1e-6))
    order = np.argsort(probs)[::-1][:6]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([bg_vocab[i] for i in order], probs[order], color="#2c6e91")
    ax.set_title("P(next | '%s') at T=%s\n%s" % (start, fnum(temperature), " ".join(out)), fontsize=9)
    ax.set_ylabel("probability")
    return fig

viz = [viz_intro_box("",
        "Choose a starting word and a <b>temperature</b>, and the bigram model samples a short "
        "continuation one word at a time; the bar chart shows the probability it assigns to each "
        "possible next word and the title prints the sentence it generated. Temperature rescales those "
        "probabilities before sampling: a low value such as " + imath("T=0.2", color="#6b4a5e") + " makes "
        "the single most likely word dominate, so the text is safe but repetitive, while a high value "
        "such as " + imath("T=2.0", color="#6b4a5e") + " flattens the distribution, so rarer words get "
        "chosen and the text becomes more varied but more erratic.")]
viz += slider_plot(render, {
    "temperature": FloatSlider(value=1.0, min=0.1, max=2.5, step=0.1, description="T"),
    "start": Dropdown(options=sorted(set("the a cat dog sat ran on mat to .".split())), value="the", description="start")})

def check(ns):
    f = ns.get("apply_temperature")
    if f is None: return False, "Define a function called <code>apply_temperature</code>."
    lo = np.asarray(f([1.0, 5.0], 0.2), dtype=float)   # low T → peaked on the larger logit
    hi = np.asarray(f([1.0, 5.0], 5.0), dtype=float)   # high T → flatter
    if np.isclose(lo.sum(), 1.0) and lo[1] > hi[1] and lo[1] > 0.98:
        return True, ""
    if np.allclose(lo, hi):
        return False, "T has no effect yet because you're ignoring it. Scale the logits by T before the softmax."
    if lo[1] < hi[1]:
        return False, "It's the wrong way round: <i>lower</i> T should sharpen the peak. Divide by T, don't multiply."
    if not np.isclose(lo.sum(), 1.0):
        return False, "The output should still sum to 1, so apply softmax after scaling by T."
    return False, "Low T should make the top choice dominate (>0.98); yours is %s. Divide the logits by T, then softmax." % fnum(float(lo[1]))

practice = [
  exercise_box("",
               taskline("Complete apply_temperature(logits, T) so that it rescales the scores by the "
                        "temperature and then normalises them into probabilities.") +
               formula_line(r"$\mathrm{softmax}(\mathrm{logits}/T)$", color="#7a4a4a") +
               "It is just two steps: divide the whole logits array by T, then pass the result to the "
               "ready-made softmax helper. It helps to see why dividing works: a small T makes the "
               "scaled scores larger and more spread out, so softmax sharpens onto the top choice, "
               "whereas a large T shrinks the differences, so the distribution flattens toward uniform."),
  editable_exercise(
    "def apply_temperature(logits, T):\n    logits = np.asarray(logits, dtype=float)\n"
    "    return softmax(logits)\n", check),
  solution_box("Worked version:",
    "def apply_temperature(logits, T):\n    logits = np.asarray(logits, dtype=float)\n    return softmax(logits / max(T, 1e-6))")]

interp = interpretation_box(
    "The bars show the next-word distribution. <b>Low temperature</b> spikes on the single most likely word "
    "(predictable text); <b>high temperature</b> flattens the bars, so rarer words get sampled (creative but "
    "more error-prone), which is exactly what your <code>apply_temperature</code> does by dividing the logits by <b><i>T</i></b>. "
    "This one knob trades safety for creativity in real LLMs too.")

build_chapter(11, "A tiny language model: Next-token prediction & temperature",
              info=info, viz=viz, practice=practice, interp=interp)
