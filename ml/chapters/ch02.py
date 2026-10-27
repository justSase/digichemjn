info = note_box(
  "In classical programming you write the <b>rules</b> and the computer applies them. "
  "<b>Machine learning</b> turns this around. You provide <b>examples</b> (the data), and the computer "
  "<i>learns the rule</i> by itself, adjusting its internal <b>parameters</b> until its predictions match "
  "those examples."
  "<div style='margin:14px 0'>" + make_table(["paradigm","you provide","the computer finds"],
      [["programming","rules + data","answers"],
       ["<b>machine learning</b>","data + answers","<b>the rule (parameters)</b>"]], scheme="info") + "</div>"
  "In <b>supervised</b> learning the examples are labelled, so the model either predicts a number "
  "(regression) or assigns a category (classification). "
  "In <b>unsupervised</b> learning the data carries no labels and the model instead discovers structure in "
  "it, such as clusters or a lower-dimensional representation. "
  "In <b>reinforcement</b> learning the model learns from reward, which this notebook does not cover.<br><br>"
  "<b>Where do LLMs fit?</b> An LLM is a very large <b>neural network</b> trained by "
  "<b>supervised</b> next-word prediction. Everything covered here, from parameters, loss and gradient "
  "descent to softmax and attention, is a building block of exactly that.<br><br>"
  "<b>Key idea:</b> Learning means <b>adjusting the parameters to reduce a loss</b>, a single number that "
  "measures how wrong the model currently is.")
build_chapter(1, "What is machine learning?", info=info)
