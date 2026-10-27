info = note_box(
  "Having built and trained models, the final question is how to judge them honestly. Always evaluate "
  "on <b>held-out data</b>, pick metrics that fit the problem" + cite(6, 14) + ", and fix seeds and "
  "record versions so the work stays reproducible and <b>FAIR</b>" + cite(13) + "."
  "<div style='margin:12px 0'>" + make_table(["metric", "answers", "use when"],
      [["accuracy", "fraction correct", "balanced classes"],
       ["precision", "of predicted-positives, how many right?", "false positives costly"],
       ["recall", "of true-positives, how many caught?", "false negatives costly"],
       ["MSE / R²", "how close are the numbers?", "regression"]], scheme="info") + "</div>"
  "A single number can mislead. A deliberately lazy classifier that ignores its input and always "
  "predicts the majority class scores 90 percent accuracy on data where 90 percent of the cases belong "
  "to that class, yet its recall for the minority class is zero, so it never finds a single one. That is "
  "exactly the failure accuracy alone would hide, which is why precision and recall must be reported on "
  "imbalanced data.")

interp = interpretation_box(
    "Judge a model on data it has not seen, and choose the metric that matches the cost of each kind of "
    "mistake. On imbalanced problems a high accuracy can be worthless, so report <b>precision and "
    "recall</b> alongside it and treat any single headline number with suspicion.")

build_chapter(13, "Evaluation & good practice", info=info, interp=interp)
