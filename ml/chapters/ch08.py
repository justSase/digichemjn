info = note_box(
  "Now that a model can be fitted by gradient descent, a new danger appears. More flexibility fits "
  "the training data better, but it may <b>memorise noise</b> and then fail on new data. The art of "
  "machine learning is choosing a model just flexible enough: complex enough to capture the real "
  "pattern, simple enough to generalise" + cite(4, 6) + ".")

def render(degree=1):
    xt = np.linspace(0, 1, 30); yt = np.sin(2*np.pi*xt) + rng.normal(0, 0.25, xt.size)
    tr = (xt[::2], yt[::2]); te = (xt[1::2], yt[1::2])
    fit = np.poly1d(np.polyfit(tr[0], tr[1], int(degree))); xx = np.linspace(0, 1, 200)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(*tr, color="#2c6e91", label="train"); ax.scatter(*te, color="#b5482e", label="test")
    ax.plot(xx, fit(xx), color="#2f8f6f", lw=2, label="degree %d" % int(degree))
    ax.plot(xx, np.sin(2*np.pi*xx), color="gray", ls=":", label="truth")
    ax.set_ylim(-2, 2); ax.legend(); ax.grid(alpha=.3)
    ax.set_title("train MSE=%s   test MSE=%s" % (fnum(mse(tr[1], fit(tr[0]))), fnum(mse(te[1], fit(te[0])))))
    return fig

viz = [viz_intro_box("",
        "The slider fits a polynomial of the chosen <b>degree</b> to a small, noisy data set. Blue points "
        "are the training data the curve is fitted to, red points are held-out test data it never sees "
        "during fitting, and the grey dotted line is the true underlying function. The title reports the "
        "error on both sets. Try " + imath("degree=1", color="#6b4a5e") + " for a straight line that is "
        "too simple, a middling " + imath("degree=3", color="#6b4a5e") + ", and a high " +
        imath("degree=15", color="#6b4a5e") + " that bends through every training point; watch how the "
        "training error keeps falling while the test error stops improving and starts to rise again.")]
viz += slider_plot(render, {"degree": IntSlider(value=1, min=1, max=15, step=1, description="degree")})

interp = interpretation_box(
    "Watch the two MSE numbers in the title. Low degree: <b>both high</b> (underfitting). High degree: the "
    "green curve wiggles through every training point (train MSE ↓) but misses the grey true curve, so "
    "<b>test MSE ↑</b> (overfitting). The best model is the simplest one that still fits, which is why we "
    "always keep a test set.")

build_chapter(6, "Over- and underfitting", info=info, viz=viz, interp=interp)
