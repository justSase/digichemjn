_intro_txt = (
  "The loss forms a bowl with one lowest point, the best parameters, and until now that point was "
  "found by hand. This step lets the model find it <b>automatically</b>. <b>Gradient descent</b> "
  "repeatedly nudges each parameter a small step against the slope of the loss, and this single "
  "idea trains everything from a line to a deep neural network and the largest language models" +
  cite(1, 4) + ".")

info = concept_box(_intro_txt, r"$w \leftarrow w - \eta\,\frac{\partial \mathrm{Loss}}{\partial w}$",
    variables=[("w", "the parameter being updated"),
               ("&#951; (eta)", "learning rate, the step size"),
               ("&#8706;Loss/&#8706;w", "gradient: slope of the loss")],
    function="Repeatedly step downhill against the gradient until the loss stops falling.")

def render(learning_rate=0.02, epochs=60):
    w, b, hist = 0.0, 0.0, []
    for _ in range(int(epochs)):
        err = (w*xd + b) - yd
        w -= learning_rate*(2/xd.size)*np.sum(err*xd)
        b -= learning_rate*(2/xd.size)*np.sum(err)
        hist.append(mse(yd, w*xd + b))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].scatter(xd, yd, color="#2c6e91", s=25); ax[0].plot(xd, w*xd + b, color="#b5482e", lw=2.5)
    ax[0].set_title("fit: w=%s, b=%s" % (fnum(w), fnum(b))); ax[0].grid(alpha=.3)
    ax[1].plot(hist, color="#2f8f6f", lw=2); ax[1].set_xlabel("step"); ax[1].set_ylabel("loss")
    ax[1].ticklabel_format(axis="y", style="sci", scilimits=(-4, 4))
    ax[1].set_title("loss vs step (lr=%s) · final %s" % (fnum(learning_rate), fnum(hist[-1])))
    ax[1].grid(alpha=.3); fig.tight_layout()
    return fig

viz = [viz_intro_box("",
        "Training starts from " + imath("w=b=0", color="#6b4a5e") + " and repeatedly steps each "
        "parameter a little way downhill on the loss. The left plot shows the line gradually settling "
        "onto the data, while the right plot shows the loss falling with every step. The learning rate "
        "sets the size of each step and is the single most important knob in machine learning: try a "
        "tiny rate such as " + imath("0.001", color="#6b4a5e") + " and watch the loss crawl down, a "
        "moderate " + imath("0.02", color="#6b4a5e") + " that converges smoothly, and a large " +
        imath("0.5", color="#6b4a5e") + " that can overshoot and make the loss jump around; the epochs "
        "slider controls how many steps are taken in total.")]
viz += slider_plot(render, {
    "learning_rate": FloatSlider(value=0.02, min=0.001, max=0.5, step=0.001, readout_format=".3f", description="lr"),
    "epochs": IntSlider(value=60, min=10, max=300, step=10, description="epochs")})

def check(ns):
    f = ns.get("gd_step")
    if f is None: return False, "Define a function called <code>gd_step</code>."
    r1 = float(f(5.0, 2.0, 0.1))   # expect 4.8
    r2 = float(f(0.0, -1.0, 0.5))  # expect 0.5
    if np.isclose(r1, 4.8) and np.isclose(r2, 0.5):
        return True, ""
    if np.isclose(r1, 5.0):
        return False, "You're returning p unchanged. Take one step away from p."
    if np.isclose(r1, 5.2):
        return False, "Wrong direction: you're going uphill. Move <i>against</i> the gradient, not with it."
    if np.isclose(r1, 3.0):
        return False, "You forgot the step size. Scale the gradient by <code>lr</code>."
    return False, "For p=5, g=2, lr=0.1 the answer is 4.8; you got %s. Step against the gradient, scaled by lr." % fnum(r1)

practice = [
  exercise_box("",
               taskline("Complete gd_step(p, g, lr) so that it performs one gradient-descent update of a "
                        "single parameter.") +
               formula_line(r"$p \leftarrow p - \mathrm{lr}\cdot g$", color="#7a4a4a") +
               "The gradient g points in the direction that <i>increases</i> the loss, so to go "
               "downhill you move the opposite way; scale the gradient by the step size lr and subtract "
               "it from the current value p. The whole update is a single arithmetic expression, and "
               "this very same line is applied to every weight when a neural network is trained."),
  editable_exercise("def gd_step(p, g, lr):\n    return p\n", check),
  solution_box("One line:", "def gd_step(p, g, lr):\n    return p - lr * g")]

interp = interpretation_box(
    "Left: The line settling onto the data. Right: The <b>loss curve</b>, which should fall smoothly to a "
    "plateau. A tiny learning rate makes it fall too slowly; a large one makes it <b>jump around or "
    "explode</b> upward. A concrete chemistry use of exactly this fit is predicting a molecule's aqueous "
    "solubility (logS) from its lipophilicity (logP), where the fitted line captures the trend that more "
    "lipophilic compounds tend to be less soluble" + cite(8) + ". You will try this on a real dataset in the final "
    "<b>Bring your own data</b> section. The same 'follow the downhill gradient' rule also trains every "
    "neural network, including LLMs.")

build_chapter(4, "Learning by rolling downhill (gradient descent)",
              info=info, viz=viz, practice=practice, interp=interp)
