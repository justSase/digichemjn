_intro_txt = (
  "We now have a line with two parameters, but nothing yet tells us whether a particular choice of "
  "<b><i>w</i></b> and <b><i>b</i></b> is good or bad. The missing piece is a <b>loss</b>, a single "
  "number measuring how wrong the model's predictions are. The <b>mean squared error</b> is the "
  "classic choice for regression, because squaring punishes large mistakes and gives a smooth, "
  "bowl-shaped surface that is easy to minimise" + cite(5, 6) + ".")

info = concept_box(_intro_txt, r"$\mathrm{MSE} = \frac{1}{n}\sum_i (y_i-\hat{y}_i)^2$",
    variables=[("MSE", "mean squared error (the loss)"), ("n", "number of data points"),
               ("y&#7522;", "true value of point i"), ("&#375;&#7522;", "predicted value of point i")],
    function="An " + imath(r"\mathrm{MSE}=0", color="#243b53") + " is a perfect fit, and large errors are punished quadratically.")

def render(w=0.5, b=1.0):
    pred = w*xd + b
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(xd, yd, color="#2c6e91", label="data")
    ax.plot(xd, pred, color="#b5482e", lw=2.5, label="guess w=%.1f" % w)
    ax.set_title("MSE loss = %s   (smaller = better)" % fnum(mse(yd, pred)))
    ax.legend(); ax.grid(alpha=.3); ax.set_xlabel("x"); ax.set_ylabel("y")
    return fig

viz = [viz_intro_box("",
        "The blue points are a fixed data set and the red line is your current model " +
        imath(r"\hat{y}=w\,x+b", color="#6b4a5e") + ". The title reports the mean squared error, the "
        "average of the squared vertical gaps between each point and the line. Move the slope slider "
        "and watch that number shrink as the line settles onto the points and grow as it moves away; "
        "try " + imath("w=0.5", color="#6b4a5e") + ", " + imath("w=1.5", color="#6b4a5e") + " and " +
        imath("w=2.3", color="#6b4a5e") + " to bracket the lowest value, and nudge <b><i>b</i></b> to "
        "see how the intercept changes the fit as well.")]
viz += slider_plot(render, {"w": FloatSlider(value=0.5, min=-1, max=5, step=0.1, description="w"),
                            "b": FloatSlider(value=1.0, min=-5, max=5, step=0.5, description="b")})

def check(ns):
    f = ns.get("my_mse")
    if f is None: return False, "Define a function called <code>my_mse</code>."
    a = float(f([1, 2, 3], [1, 2, 3]))   # identical → 0
    b = float(f([0, 0], [1, 3]))         # squared diffs 1 and 9 → mean 5 (sum 10)
    if np.isclose(a, 0.0) and np.isclose(b, 5.0):
        return True, ""
    if a == 0.0 and b == 0.0:
        return False, "You're still returning the placeholder. Now actually combine y_true and y_pred."
    if not np.isclose(a, 0.0):
        return False, "Identical inputs should give 0: subtract y_pred from y_true before anything else."
    if np.isclose(b, 10.0):
        return False, "You summed the squared errors but didn't average them. Divide by the number of points."
    if np.isclose(b, 2.0):
        return False, "That looks like the mean of the raw differences. Square each difference before averaging."
    return False, "Expected 0 and 5 for the two test cases; got %s and %s. Square the errors, then take the mean." % (fnum(a), fnum(b))

practice = [
  exercise_box("",
               taskline("Complete the function my_mse(y_true, y_pred) so that it returns the mean squared error.") +
               formula_line(r"$\mathrm{MSE}=\frac{1}{n}\sum_i (y_i-\hat{y}_i)^2$", color="#7a4a4a") +
               "Work in three small steps: first subtract the predictions from the true values to get "
               "the error of every point, then square those errors so that over- and under-estimates "
               "both count and large gaps count more, and finally take the mean over all points. Both "
               "inputs are already numpy arrays, so writing y_true - y_pred subtracts them element by "
               "element and np.mean(...) averages the result in a single call."),
  editable_exercise(
    "def my_mse(y_true, y_pred):\n"
    "    y_true = np.asarray(y_true); y_pred = np.asarray(y_pred)\n"
    "    return 0.0\n", check),
  solution_box("",
    "def my_mse(y_true, y_pred):\n"
    "    y_true = np.asarray(y_true); y_pred = np.asarray(y_pred)\n"
    "    return float(np.mean((y_true - y_pred)**2))")]

interp = interpretation_box(
    "The loss is a <b>bowl</b> with one lowest point, the best <b><i>w</i></b>. Guessing by hand means "
    "walking along this bowl; in the next section the model finds the bottom automatically. "
    "That bottom is what 'a trained model' means.")

build_chapter(3, "Measuring error: The loss", info=info, viz=viz, practice=practice, interp=interp)
