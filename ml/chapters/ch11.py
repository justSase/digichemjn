info = note_box(
  "The models so far worked on numbers, yet language models must read text. The bridge is to turn "
  "text into <b>tokens</b> (integer ids) and then into <b>embeddings</b> (vectors), so that similar "
  "meanings become <b>nearby vectors</b>, with closeness measured by <b>cosine similarity</b>. These "
  "learned word vectors are what let a network handle meaning" + cite(7) + "; real LLMs use the same "
  "idea but with hundreds of dimensions instead of the two used here.")

def render(sentence="the cat sat on the mat"):
    vocab = {"the": [0.9, 0.1], "a": [0.85, 0.15], "cat": [0.2, 0.9], "dog": [0.25, 0.85],
             "sat": [0.6, 0.5], "ran": [0.62, 0.55], "on": [0.1, 0.2], "mat": [0.3, 0.8]}
    tokens = sentence.lower().split()
    fig, ax = plt.subplots(figsize=(6, 6))
    for wd, (x, y) in vocab.items():
        ax.scatter(x, y, color="#2c6e91"); ax.text(x + .01, y + .01, wd)
    for t in tokens:
        if t in vocab:
            x, y = vocab[t]; ax.scatter(x, y, color="#b5482e", s=90)
    ids = [list(vocab).index(t) if t in vocab else -1 for t in tokens]
    ax.set_title("tokens: %s   ids: %s" % (tokens, ids), fontsize=9)
    ax.set_xlabel("dim 1"); ax.set_ylabel("dim 2"); ax.grid(alpha=.3)
    return fig

viz = [viz_intro_box("",
        "Pick a sentence from the dropdown. It is split into <b>tokens</b> (individual words), and each "
        "token is looked up in a tiny two-dimensional vocabulary of toy word vectors, which is drawn as "
        "a scatter of points. The words of your chosen sentence are highlighted in red, and the title "
        "lists their integer token ids. Notice how words with a similar role, such as <i>cat</i> and "
        "<i>dog</i> or <i>the</i> and <i>a</i>, sit close together, which previews how real embeddings "
        "place related words near one another.")]
viz += slider_plot(render, {"sentence": Dropdown(
    options=["the cat sat on the mat", "a dog ran", "the dog on the mat", "a cat sat"],
    value="the cat sat on the mat", description="sentence")})

def check(ns):
    f = ns.get("cosine")
    if f is None: return False, "Define a function called <code>cosine</code>."
    par  = float(f([1, 0], [1, 0]))   # 1
    perp = float(f([1, 0], [0, 1]))   # 0
    scal = float(f([1, 1], [2, 2]))   # 1 (same direction, different length)
    if np.isclose(par, 1.0) and np.isclose(perp, 0.0) and np.isclose(scal, 1.0):
        return True, ""
    if par == 0.0 and perp == 0.0:
        return False, "You're still returning the placeholder. Compute the dot product of a and b first."
    if np.isclose(scal, 4.0) or scal > 1.0:
        return False, "You have the dot product but not the normalisation. Divide by (‖a‖·‖b‖)."
    if not np.isclose(perp, 0.0):
        return False, "Perpendicular vectors must give 0. Use the dot product a·b in the numerator."
    return False, "Parallel → 1, perpendicular → 0; you got %s and %s. Divide a·b by the product of the norms." % (fnum(par), fnum(perp))

practice = [
  exercise_box("",
               taskline("Complete cosine(a, b) so that it returns the cosine of the angle between two vectors.") +
               formula_line(r"$\cos\theta=\dfrac{a\cdot b}{\|a\|\,\|b\|}$", color="#7a4a4a") +
               "Build it from three pieces: the dot product of the two vectors, written a @ b, in the "
               "numerator, and each vector's length (its norm) via np.linalg.norm(...) multiplied "
               "together in the denominator. The result is 1 when the vectors point the same way and 0 "
               "when they are perpendicular, and it ignores their lengths, which is exactly why it "
               "measures similarity of meaning rather than magnitude."),
  editable_exercise(
    "def cosine(a, b):\n    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)\n    return 0.0\n", check),
  solution_box("Worked version:",
    "def cosine(a, b):\n    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)\n"
    "    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))")]

interp = interpretation_box(
    "Each word is a point (vector); words with a similar role sit close together (<b>cat/dog</b>, "
    "<b>the/a</b>). Red points are the tokens of your sentence. <b>Cosine similarity</b> (the exercise) is "
    "exactly how we measure that closeness. LLMs use the same idea with hundreds of learned dimensions.")

build_chapter(9, "From words to vectors: Tokenisation & embeddings",
              info=info, viz=viz, practice=practice, interp=interp)
