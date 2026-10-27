from ipywidgets import FileUpload

# ----------------------------------------------------------------------
# "Bring your own data" — a guided, step-by-step mini-analysis that applies
# the whole notebook (a model, a loss, gradient descent, held-out evaluation)
# to a real or simulated dataset, laid out in the SAME steps used throughout
# the chapters. Single-feature linear regression by gradient descent, exactly
# the method from the loss / gradient-descent sections. Pyodide-safe (numpy only).
# ----------------------------------------------------------------------
_intro = note_box(
  "This closing section applies everything to a <b>dataset</b> and works through it in the same steps "
  "used throughout the notebook: load the data, choose what to predict, explore it, fit a line by "
  "gradient descent, evaluate on held-out data, and interpret the result critically. You can upload "
  "your own CSV with at least two numeric columns, or keep the built-in <b>simulated</b> solubility "
  "dataset (600 molecules, patterned on the published ESOL aqueous-solubility data" + cite(8) + " and "
  "clearly marked as simulated). Whatever data you use, record its source, licence and a DOI so the "
  "analysis stays reproducible and <b>FAIR</b>" + cite(13) + ".", grey=True)

def _step(n, title, text):
    """A small left-aligned step heading (plus optional explanation) used to lay the
    analysis out as a numbered walkthrough, mirroring the chapters."""
    body = ("<div style='color:#33475b;line-height:1.6;margin-top:3px'>%s</div>" % text) if text else ""
    return HTML(layout=_w(), value=(
      "<div style='max-width:760px;margin:8px auto 0;text-align:left'>"
      "<div style='color:#2c6e91;font-weight:800;font-size:1.06em'>Step %s &middot; %s</div>%s</div>"
      % (n, title, body)))

# Steps 1 and 2 are the controls below (load + choose); steps 3 to 6 are produced
# by _analyse each time the button is pressed or the data changes.
_s1 = _step("1", "Load the data",
      "Upload a CSV using the button below, or simply keep the built-in simulated solubility dataset "
      "to follow a worked example.")
_s2 = _step("2", "Choose what to predict",
      "Pick one column as the input feature <i>x</i> and another as the target <i>y</i>, then press "
      "Analyse. The example predicts solubility (logS) from lipophilicity (logP).")

def _demo():
    return list(demo_cols), np.asarray(demo_data, dtype=float)

def _parse_csv(content):
    """Parse uploaded CSV bytes into (columns, numeric array). Non-numeric rows are skipped."""
    import io as _io, csv as _csv
    text = bytes(content).decode("utf-8", "replace")
    rows = [r for r in _csv.reader(_io.StringIO(text)) if r]
    if not rows:
        return _demo()
    header = [h.strip() for h in rows[0]]
    data = []
    for r in rows[1:]:
        try:
            data.append([float(v) for v in r])
        except (ValueError, TypeError):
            continue
    if len(data) < 5:
        return _demo()
    arr = np.array(data, dtype=float)
    header = header[:arr.shape[1]]
    return header, arr

def _current():
    """Columns + data from the upload if one is present, else the built-in demo."""
    up = _uploader.value
    if up:
        item = up[0] if isinstance(up, (list, tuple)) else list(up.values())[0]
        return _parse_csv(item["content"])
    return _demo()

def _fit_gd(x, y, epochs=4000, lr=0.05):
    """Single-feature linear regression by gradient descent on standardised x."""
    xm, xs = float(x.mean()), float(x.std() + 1e-9)
    xz = (x - xm) / xs
    w = b = 0.0
    for _ in range(epochs):
        err = (w*xz + b) - y
        w -= lr*(2/len(x))*np.sum(err*xz)
        b -= lr*(2/len(x))*np.sum(err)
    return w, b, xm, xs

def _metrics_box(r2, mse_te):
    return HTML(layout=_w(), value=(
        "<div style='background:linear-gradient(90deg,#eef4fb,#f6faff);border:4px solid #7fb0cd;"
        "border-radius:14px;padding:14px 22px;margin:8px auto;max-width:460px;text-align:center;"
        "font-family:monospace;font-size:1.05em;line-height:1.9;color:#243b53'>"
        "R&sup2; = %s<br>MSE = %s</div>" % (fnum(r2), fnum(mse_te))))

def _analyse(_=None):
    _out.clear_output(wait=True)
    with _out:
        cols, data = _current()
        xi = cols.index(_xdd.value) if _xdd.value in cols else 0
        yi = cols.index(_ydd.value) if _ydd.value in cols else (len(cols) - 1)
        if xi == yi:
            display(IHTML("<div style='text-align:center;color:#a3352b;font-weight:600'>"
                          "Please pick two different columns for the feature and the target.</div>"))
            return
        x, y = data[:, xi], data[:, yi]
        n = len(x)

        # ---- Step 3 · Explore -------------------------------------------------
        display(center(_step("3", "Explore the data",
            "Before modelling, look at the raw data as a scatter plot of all %d rows, so its size, "
            "spread and any obvious trend are visible." % n)))
        fig1, ax = plt.subplots(figsize=(6.6, 4))
        ax.scatter(x, y, s=14, color="#2c6e91", alpha=.6)
        ax.set_xlabel(cols[xi]); ax.set_ylabel(cols[yi]); ax.grid(alpha=.3)
        ax.set_title("%s vs %s  (%d rows)" % (cols[xi], cols[yi], n))
        display(center(HTML(layout=_w(), value=fig_to_html(fig1))))

        # reproducible held-out split (25% test)
        r = np.random.default_rng(0); idx = r.permutation(n); cut = int(0.75*n)
        tr, te = idx[:cut], idx[cut:]
        w, b, xm, xs = _fit_gd(x[tr], y[tr])
        def predict(xv): return w*((xv - xm)/xs) + b

        # ---- Step 4 · Fit -----------------------------------------------------
        display(center(_step("4", "Fit a line with gradient descent",
            "Now fit a straight line with the same gradient-descent method used earlier: start from a "
            "flat line and step downhill on the mean squared error until it settles. The red line is the "
            "fitted model, shown here on the held-out test points.")))
        fig2, ax = plt.subplots(figsize=(6.6, 4))
        ax.scatter(x[te], y[te], s=16, color="#2c6e91", alpha=.6, label="test data")
        xs_line = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs_line, predict(xs_line), color="#b5482e", lw=2.5, label="fitted line")
        ax.set_xlabel(cols[xi]); ax.set_ylabel(cols[yi]); ax.legend(); ax.grid(alpha=.3)
        ax.set_title("gradient-descent fit")
        display(center(HTML(layout=_w(), value=fig_to_html(fig2))))

        # metrics on the held-out test set
        yp = predict(x[te]); resid = y[te] - yp
        mse_te = float(np.mean(resid**2))
        ss_res = float(np.sum(resid**2)); ss_tot = float(np.sum((y[te] - y[te].mean())**2)) + 1e-12
        r2 = 1 - ss_res/ss_tot

        # ---- Step 5 · Evaluate ------------------------------------------------
        display(center(_step("5", "Evaluate on held-out data",
            "Judge the model on the %d test rows it never saw during fitting. " % len(te) +
            "R&sup2; is the fraction of the variation the line explains (1 is perfect, 0 is no better "
            "than the mean), and the mean squared error is the average squared miss.")))
        display(center(_metrics_box(r2, mse_te)))

        # ---- Step 6 · Interpret ----------------------------------------------
        slope = w/xs; trend = "increases" if slope >= 0 else "decreases"
        display(center(_step("6", "Interpret the result critically", "")))
        display(center(interpretation_box(
            "The model was trained on %d rows and evaluated on %d held-out ones, reaching an R&sup2; of "
            "%s and a mean squared error of %s on that test set. The fitted line says that, on average, "
            "<b>%s</b> <b>%s</b> by about %s per unit of <b>%s</b>. A single feature can only capture "
            "part of the story, and a trend in simulated or observational data is not proof of "
            "causation, so treat the model as a first hypothesis and check it against measured data and "
            "domain knowledge (verify the AI)."
            % (len(tr), len(te), fnum(r2), fnum(mse_te), cols[yi], trend, fnum(abs(slope)), cols[xi]))))

def _refresh(_=None):
    cols, _data = _current()
    _xdd.options = cols; _ydd.options = cols
    _xdd.value = "logP" if "logP" in cols else cols[0]
    _ydd.value = "logS" if "logS" in cols else cols[-1]

_uploader = FileUpload(accept=".csv", multiple=False, description="Upload CSV")
_xdd = Dropdown(description="feature x", layout=Layout(width="260px"))
_ydd = Dropdown(description="target y",  layout=Layout(width="260px"))
_go  = Button(description="Analyse ▶", layout=Layout(width="200px", height="44px")); _go.add_class("sc-btn")
_out = Output(layout=Layout(width="900px"))

_uploader.observe(_refresh, "value")
_go.on_click(_analyse)
_refresh()          # populate the dropdowns from the built-in demo
_analyse()          # show a worked example immediately (on the demo data)

build_chapter(None, "Bring your own data", info=_intro,
              body=[_s1, _uploader, _s2, HBox([_xdd, _ydd]), _go, _out],
              icon="📥", anchor="byod")
