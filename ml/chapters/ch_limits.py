# A dedicated chapter listing the errors, weaknesses and important caveats of
# everything covered in this notebook (was the red "limits" box). K3/K5.
_box = (
  "Every model in this notebook can be wrong, so its output always has to be checked against measured data "
  "and domain knowledge. The habit of “verify the AI” applies to all of the methods below."
  "<div style='font-weight:700;color:#1a1a1a;margin:14px 0 4px'>Machine-learning models in general</div>"
  "<ul style='margin:4px 0 0;padding-left:20px'>"
  "<li><b>Overfitting:</b> A low training error does not guarantee good predictions on new data, so a model "
  "must always be judged on held-out data.</li>"
  "<li><b>Correlation is not causation:</b> A fitted trend describes an association in the data, not a "
  "mechanism, and a single feature can only ever explain part of the picture.</li>"
  "<li><b>Metrics can mislead:</b> On imbalanced data a high accuracy can hide a useless model, so the "
  "metric has to match the question (for example precision and recall).</li>"
  "<li><b>Data quality decides everything:</b> Small, biased, simulated or poorly documented data leads to "
  "unreliable models, so record the source, licence and a DOI and keep the work reproducible and FAIR"
  + cite(13) + ".</li>"
  "</ul>"
  "<div style='font-weight:700;color:#1a1a1a;margin:14px 0 4px'>Large language models in particular</div>"
  "<ul style='margin:4px 0 0;padding-left:20px'>"
  "<li><b>Hallucination:</b> A fluent answer can be confidently wrong, because the model optimises for "
  "plausibility rather than truth" + cite(11) + ".</li>"
  "<li><b>No built-in facts:</b> There is no database inside, so facts, numbers and citations must be "
  "checked against primary sources.</li>"
  "<li><b>Bias:</b> A model mirrors the biases present in its training data" + cite(12) + ".</li>"
  "<li><b>Non-determinism:</b> The prompt wording and the temperature both change the output.</li>"
  "<li><b>Stale knowledge:</b> A model only knows its training data up to its cut-off date.</li>"
  "</ul>"
  "<div style='margin-top:12px'>In science, treat any model as a fast but fallible assistant, and verify "
  "every claim, unit and reference against primary, measured sources.</div>")
info = note_box(_box, grey=True)
build_chapter(None, "Remarks", info=info, icon="⚠️", anchor="remarks")
