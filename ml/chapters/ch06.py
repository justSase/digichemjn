info = note_box(
  "Aqueous solubility (<i>logS</i>) usually falls as lipophilicity (<i>logP</i>) rises. We fit the line with "
  "gradient descent, and the method is identical on real measured data."
  "<div style='margin-top:12px;padding:10px 14px;background:#fff8e6;border:1px solid #f0dca0;border-radius:8px'>"
  "<b>Note:</b> The data here is <b>simulated</b> for teaching (seeded). For real work use measured datasets "
  "(e.g. AqSolDB) and cite the source.</div>")

def make_fig():
    logP = rng.uniform(-1, 5, 40); logS = -0.9*logP + 0.3 + rng.normal(0, 0.5, logP.size)
    w = b = 0.0
    for _ in range(400):
        err = (w*logP + b) - logS
        w -= 0.02*(2/logP.size)*np.sum(err*logP); b -= 0.02*(2/logP.size)*np.sum(err)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(logP, logS, color="#2c6e91", label="data"); xs = np.linspace(-1, 5, 50)
    ax.plot(xs, w*xs + b, color="#b5482e", lw=2.5, label="fit: logS=%s·logP+%s" % (fnum(w), fnum(b)))
    ax.set_xlabel("logP"); ax.set_ylabel("logS"); ax.legend(); ax.grid(alpha=.3)
    ax.set_title("solubility regression  (slope %s)" % fnum(w))
    return fig

viz = [viz_intro_box("📊 Analysis · linear regression on solubility",
        "A line fitted by gradient descent on simulated logP → logS data.", ""),
       plot_html(make_fig())]

interp = interpretation_box(
    "The fitted line's <b>negative slope</b> captures the chemical trend (lipophilic ⇒ poorly soluble). "
    "The scatter around the line is what a single descriptor cannot explain, so real models add more features "
    "to reduce it.")

build_chapter(5, "A chemistry example: predict solubility from logP", info=info, viz=viz, interp=interp)
