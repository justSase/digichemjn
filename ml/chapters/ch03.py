_intro_txt = (
  "Machine learning starts from the simplest possible model, a straight line. <b>Learning means "
  "adjusting parameters to reduce a loss</b>, and here we meet the very first parameters, the slope "
  "<b><i>w</i></b> and the intercept <b><i>b</i></b>. Every richer model in this notebook, up to a "
  "full neural network, is built by combining and stacking exactly this building block" + cite(5, 6) + ".")

info = concept_box(_intro_txt, r"$\hat{y} = w\,x + b$",
    variables=[("w", "weight / slope"), ("b", "bias / intercept"),
               ("x", "input"), ("&#375;", "prediction")],
    function="The simplest model; <b><i>w</i></b> tilts the line, <b><i>b</i></b> shifts it up or down.")

def render(w=2.0, b=0.0):
    x = np.linspace(-5, 5, 100); y = w*x + b
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.axhline(0, color="gray", lw=.6); ax.axvline(0, color="gray", lw=.6)
    ax.plot(x, y, color="#2c6e91", lw=2.5)
    ax.set_title("y = %.1f·x + %.1f" % (w, b))
    ax.set_xlabel("input x"); ax.set_ylabel("prediction ŷ")
    ax.grid(alpha=.3); ax.set_ylim(-12, 12)
    return fig

viz = [viz_intro_box("",
        "The plot shows the straight line " + imath(r"\hat{y}=w\,x+b", color="#6b4a5e") + " on a fixed "
        "pair of axes. Drag the two sliders to reshape it: the slope <b><i>w</i></b> sets how steeply "
        "the line rises or falls, while the intercept <b><i>b</i></b> moves the whole line up or down "
        "without changing its tilt. Try a steep positive slope such as " + imath("w=3", color="#6b4a5e") +
        ", then a flat line " + imath("w=0", color="#6b4a5e") + ", then a negative slope, watching how "
        "the line pivots each time; afterwards change <b><i>b</i></b> and see the same line slide "
        "vertically while its steepness stays fixed.")]
viz += slider_plot(render, {"w": FloatSlider(value=2.0, min=-3, max=3, step=0.1, description="w"),
                            "b": FloatSlider(value=0.0, min=-5, max=5, step=0.5, description="b")})

interp = interpretation_box(
    "The slope <b><i>w</i></b> tilts the line, and the larger " + imath("|w|") + " is the steeper it "
    "runs, while the bias <b><i>b</i></b> slides it vertically. A model 'learns' by choosing exactly "
    "these two numbers so that the line runs through the data, which is the whole game, simply scaled up.")

build_chapter(2, "The building block: A line", info=info, viz=viz, interp=interp)
