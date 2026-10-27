# E21.13 (2026-10-02, Inhalt + Struktur) — ONE CHAPTER "CONCLUSION", as in
# Complex (Nutzer: "Summary + Glossary → ein Kapitel Conclusion; Setup
# entfällt"). The summary, the glossary, the red note that the locks are no
# assessment (Konzept §4, E19.8) and, from the old Setup, the one sentence a
# reader still needs: the pharmacokinetic data are simulated. The seed is in
# the ⚙ drawer; "runs entirely in your browser" went with Setup (not true in
# JupyterLab on a server).
info = note_box(
  "<p style='margin:0 0 12px'>This notebook built the modelling workflow from the ground up on a small "
  "pharmacokinetic example. A <b>model</b> is a purpose-built, simplified representation of a real system. "
  "You build it in stages. The <b>perceptual</b> model captures which processes matter, the "
  "<b>conceptual</b> model writes them as equations, and the <b>procedural</b> model implements them in "
  "code. We only ever see noisy, incomplete observations. A model is therefore a parameterised abstraction, "
  "and its disagreement with the data shapes its parameters.</p>"
  "<p style='margin:0 0 12px'>Models range from <b>event-driven</b> white boxes, built on mechanism, to "
  "<b>data-driven</b> black boxes, learned from data. Grey boxes lie in between. Mechanism gives trustworthy "
  "extrapolation beyond the data; flexibility gives a good fit within their range. Our running conceptual model was first-order "
  "elimination: the concentration falls exponentially with a single rate constant.</p>"
  "<p style='margin:0 0 12px'><b>Calibration</b> turned fitting into the minimisation of an "
  "<b>objective function</b>, here the sum of squared errors. <b>Optimization</b> by gradient descent "
  "carried out that minimisation automatically. <b>Evaluation</b> then judged the result on held-out data that the fit never saw. "
  "This showed the balance between model complexity and the amount of data, known as the "
  "<b>bias&ndash;variance</b> trade-off. Cross-validation and bootstrap gave more stable estimates "
  "of how well the model works on new data.</p>"
  "<p style='margin:0'>Finally, <b>sensitivity analysis</b> asked which parameters matter. A local "
  "one-factor-at-a-time difference gives a quick answer; <b>Monte-Carlo</b> sampling handles global questions "
  "and uncertainty. One warning holds throughout: all models are wrong, but some are useful. So "
  "calibrate, validate and quantify uncertainty. Document the data and code so that the whole analysis stays "
  "reproducible and <b>FAIR</b> (findable, accessible, interoperable, reusable)" + cite(9) + ".</p>", grey=True)
_terms = [
  ("Model", "A simplified, purpose-built representation of a real system, used to explain and predict."),
  ("Perceptual model", "What you understand about the system from observation: which processes matter."),
  ("Conceptual model", "The formal equations that link the system's state variables."),
  ("Procedural model", "The code and numerical solver that simulate the conceptual model."),
  ("Event-driven (white box)", "A mechanistic model built from known laws. It explains why something happens."),
  ("Data-driven (black box)", "A model learned from data with little mechanism. It captures what tends to happen."),
  ("Parameter", "A number inside the model that calibration adjusts, such as the rate k."),
  ("Objective function", "A single number that measures how much the model disagrees with the data. Calibration minimises it."),
  ("Calibration", "Choosing the parameters that best fit the observed data."),
  ("Validation", "Testing the calibrated model on independent, held-out data."),
  ("Overfitting / underfitting", "Overfitting chases the noise (high variance); underfitting is too simple to fit the data (high bias)."),
  ("Cross-validation", "Rotating which part of the data (the fold) is held out, to estimate more stably how well the model works on new data."),
  ("Sensitivity analysis", "Quantifying how much the output changes when an input changes."),
  ("Monte-Carlo", "Estimating a quantity by repeated random sampling of the inputs."),
  ("FAIR", "Findable, Accessible, Interoperable, Reusable: principles for reproducible data."),
]
_rows = "".join("<div style='font-weight:700'>%s:</div><div>%s</div>" % (t, d) for t, d in _terms)
_grid = ("<div style='display:grid;grid-template-columns:max-content 1fr;gap:9px 18px;"
         "text-align:left;line-height:1.55'>%s</div>" % _rows)
_rows = "".join("<div style='font-weight:700'>%s:</div><div>%s</div>" % (t, d) for t, d in _terms)
_grid = ("<div style='display:grid;grid-template-columns:max-content 1fr;gap:9px 18px;"
         "text-align:left;line-height:1.55;margin-top:10px'>%s</div>" % _rows)
build_chapter(None, "Conclusion", info=info, icon="📋", anchor="conclusion",
  body=[note_box("<b>Glossary</b>" + _grid, grey=True),
        warn_box(
    "<b>The locks in this notebook set your pace; they are not an assessment.</b> Everything runs in "
    "your browser, the check functions sit in the same cell as the exercises, and the "
    "<b>Skip for now</b> button is there on purpose. Treat the timeline as a note to yourself about "
    "what to revisit."),
        warn_box(
    "<b>The data are simulated.</b> The pharmacokinetic data in this notebook (drug concentrations "
    "over time) are generated from a fixed seed with realistic orders of magnitude and are meant "
    "for teaching only.")])
