from ipywidgets import FileUpload

# ----------------------------------------------------------------------
# "Bring your own data" — apply the whole workflow (load → choose → explore
# → calibrate → evaluate → interpret) to a REAL or simulated concentration–
# time dataset, calibrating the first-order model C(t) = C0·exp(-k t) by
# (log-linear) least squares. Pyodide-safe (numpy only).
# ----------------------------------------------------------------------
_intro = note_box(
  "This closing section applies everything to a <b>dataset</b>. It uses the same steps as the rest of "
  "the notebook: load the data, choose what to fit, explore it, calibrate the first-order model "
  "C(t) = C0&#183;exp(&minus;k t), evaluate the fit, and interpret it. Upload your own CSV file with a time "
  "column and a concentration column. Or keep the built-in <b>simulated</b> pharmacokinetic data (a "
  "one-compartment IV profile, i.e. a drug injected into a single well-mixed volume, modelled on the cefazolin analysis" + cite(5) + " and clearly marked as "
  "simulated). Whatever data you use, record its source, licence and DOI, so that the analysis stays "
  "reproducible and <b>FAIR</b>" + cite(9) + ".", grey=True)

def _step(n, title, text):
    body = ("<div style='color:var(--nbskin-ink,#1a1a1a);line-height:1.6;margin-top:3px'>%s</div>" % text) if text else ""
    return HTML(layout=_w(), value=(
      # lab_center (02.10.): centred like every other exercise text (K2.4)
      "<div style='max-width:760px;margin:8px auto 0;text-align:center'>"
      "<div style='color:var(--nbskin-acc,#2c6e91);font-weight:800;font-size:1.06em'>Step %s &middot; %s</div>%s</div>"
      % (n, title, body)))

_s1 = _step("1", "Load the data",
      "Upload a CSV with at least two numeric columns (time and concentration) with the button below. Or "
      "keep the built-in simulated profile and follow a worked example.")
_s2 = _step("2", "Choose what to fit",
      "Pick the time column and the concentration column, then press Analyse.")

def _demo():
    # E23.1: the worked example's columns in the run's language
    return [_nbL("time", "Zeit"), _nbL("concentration", "Konzentration")], np.column_stack([t_obs, c_obs]).astype(float)

def _parse_csv(content):
    import io as _io, csv as _csv
    text = bytes(content).decode("utf-8", "replace")
    rows = [r for r in _csv.reader(_io.StringIO(text)) if r]
    if not rows: return _demo()
    header = [h.strip() for h in rows[0]]; data = []
    for r in rows[1:]:
        try: data.append([float(v) for v in r])
        except (ValueError, TypeError): continue
    if len(data) < 4: return _demo()
    arr = np.array(data, float); return header[:arr.shape[1]], arr

def _current():
    up = _uploader.value
    if up:
        item = up[0] if isinstance(up, (list, tuple)) else list(up.values())[0]
        return _parse_csv(item["content"])
    return _demo()

def _fit_loglin(t, c):
    """Calibrate C(t)=C0 exp(-k t) by least squares on ln C (needs c>0)."""
    m = c > 0
    b1, b0 = np.polyfit(t[m], np.log(c[m]), 1)
    return float(np.exp(b0)), float(-b1)          # C0, k

def _metrics_box(k, C0, r2):
    thalf = np.log(2)/k if k > 0 else float("inf")
    return HTML(layout=_w(), value=(
        "<div style='background:var(--nbskin-surf,#eef4fb);border:2px solid var(--nbskin-line,#7fb0cd);"
        "border-radius:14px;padding:14px 22px;margin:8px auto;max-width:520px;text-align:center;"
        "font-family:monospace;font-size:1.02em;line-height:1.9;color:var(--nbskin-ink,#1a1a1a)'>"
        "k = %s /h &nbsp;·&nbsp; C0 = %s mg/L<br>half-life = %s h &nbsp;·&nbsp; R&sup2; = %s</div>"
        % (fnum(k), fnum(C0), fnum(thalf), fnum(r2))))

def _analyse(_=None):
    _out.clear_output(wait=True)
    with _out:
        cols, data = _current()
        ti = cols.index(_xdd.value) if _xdd.value in cols else 0
        ci = cols.index(_ydd.value) if _ydd.value in cols else (len(cols) - 1)
        if ti == ci:
            display(IHTML("<div class='nberr' style='text-align:center;color:var(--nbskin-bad,#a3352b);font-weight:600'>"
                          "Please pick two different columns for time and concentration.</div>")); return
        t = data[:, ti]; c = data[:, ci]; n = len(t)
        order = np.argsort(t); t, c = t[order], c[order]

        display(center(_step("3", "Explore the data",
            "First look at the %d measurements as a concentration&ndash;time scatter plot. It shows the overall decay "
            "and the noise before you fit anything." % n)))
        fig1, ax = plt.subplots(figsize=(6.6, 4))
        theme_axes(ax); ax.scatter(t, c, color=PAL["z2"], s=26); ax.set_xlabel(cols[ti]); ax.set_ylabel(cols[ci])
        ax.set_title("%s vs %s  (%d points)" % (cols[ci], cols[ti], n))
        display(center(HTML(layout=_w(), value=fig_to_html(fig1))))

        C0, k = _fit_loglin(t, c)
        display(center(_step("4", "Calibrate the model",
            "Now calibrate C(t) = C0&#183;exp(&minus;k t) by least squares. The fit works on the logarithm, which makes "
            "the model linear. The red curve is the fitted model. Its two parameters are the initial "
            "concentration and the elimination rate.")))
        fig2, ax = plt.subplots(figsize=(6.6, 4))
        theme_axes(ax); ax.scatter(t, c, color=PAL["z2"], s=26, label="data")
        tt = np.linspace(float(t.min()), float(t.max()), 200)
        ax.plot(tt, pk(tt, C0, k), color=PAL["z"], lw=2.5, label="fitted model")
        ax.set_xlabel(cols[ti]); ax.set_ylabel(cols[ci]); theme_legend(ax)
        ax.set_title("calibrated fit"); display(center(HTML(layout=_w(), value=fig_to_html(fig2))))

        pred = pk(t, C0, k)
        ss_res = float(np.sum((c - pred)**2)); ss_tot = float(np.sum((c - c.mean())**2)) + 1e-12
        r2 = 1 - ss_res/ss_tot
        display(center(_step("5", "Evaluate the fit",
            "R&sup2; tells you how well the model reproduces the data (1 is perfect, 0 is no better than "
            "the mean). Also read off the derived half-life.")))
        display(center(_metrics_box(k, C0, r2)))

        display(center(_step("6", "Interpret the result", "")))
        display(center(interpretation_box(
            # E17.1 — whole sentences, so each language can order its own words
            ("The fitted model has an elimination rate of %s per hour, which gives a half-life of about "
             "%s hours. It explains an R&sup2; of %s of the variation in these %d points. This clearance "
             "is slower than the notebook's baseline of 0.35 per hour." if k < 0.35 else
             "The fitted model has an elimination rate of %s per hour, which gives a half-life of about "
             "%s hours. It explains an R&sup2; of %s of the variation in these %d points. This clearance "
             "is faster than the notebook's baseline of 0.35 per hour.")
            % (fnum(k), fnum(np.log(2)/k if k > 0 else float('inf')), fnum(r2), n)
            + " Remember that this one-compartment model assumes a "
            "single well-mixed volume and purely first-order elimination. If the data curve downward on a "
            "log scale or show an early distribution phase, you need a richer multi-compartment model. "
            "Treat this fit as a first hypothesis and check it against measured data and domain knowledge.")))

def _refresh(_=None):
    cols, _d = _current()
    _xdd.options = cols; _ydd.options = cols
    _xdd.value = next((c for c in ("time", "Zeit") if c in cols), cols[0])
    _ydd.value = next((c for c in ("concentration", "Konzentration") if c in cols), cols[-1])

_uploader = FileUpload(accept=".csv", multiple=False, description="Upload CSV")
# E23.1: the labels in the run's language (not through the table: "time" and
# "concentration" are also the column names this section looks for)
_xdd = Dropdown(description=_nbL("time", "Zeit"), layout=Layout(width="260px"))
_ydd = Dropdown(description=_nbL("concentration", "Konzentration"), layout=Layout(width="300px"))
_go  = Button(description="Analyse ▶", layout=Layout(width="200px", height="44px")); _go.add_class("sc-btn")
_out = Output(layout=Layout(width="900px"))

_uploader.observe(_refresh, "value"); _go.on_click(_analyse)
# 2026-09-30 (E10 Teil 4) — the worked example runs when the reader presses
# Analyse, as the own-data section of Complex runs on "Run ▶": drawing both
# figures at build time cost 0.4 s of every run of the notebook.
_refresh()
with _out:
    display(IHTML("<div style='text-align:center;opacity:.85'>Press <b>Analyse ▶</b> to work "
                  "through the steps with the data chosen above.</div>"))

build_chapter(None, "Bring your own data", info=_intro, chapter_open=False,
              body=[_s1, _uploader, _s2, HBox([_xdd, _ydd]), _go, _out,
                    completion_button("b1", "I have analysed a data set")],
              icon="📥", anchor="byod", task="b1")
