# Glossary as an aligned two-column list: terms in a left column, definitions in a
# second column that all start at the same x (flush, like the chapter overview).
_terms = [
  ("Parameter (weight or bias)", "A number the model learns."),
  ("Loss", "How wrong the model is; training minimises it."),
  ("Gradient descent", "Repeatedly stepping downhill on the loss."),
  ("Learning rate", "The step size of gradient descent."),
  ("Activation", "The non-linearity inside a neuron, such as ReLU, sigmoid or tanh."),
  ("Sigmoid and softmax", "Functions that turn scores into a probability or a probability distribution."),
  ("Overfitting and underfitting", "Fitting the training noise versus being too simple to capture the pattern."),
  ("Embedding", "A vector that represents a token, where nearby vectors mean similar meaning."),
  ("Attention", "Weighting other tokens by their relevance; it is the core of transformers."),
  ("Temperature", "A sampling knob where low values stay safe and repetitive while high values become creative and erratic."),
  ("Supervised and unsupervised", "Learning from labelled examples versus finding structure in unlabelled data."),
]
_rows = "".join(
    "<div style='font-weight:700'>%s:</div><div>%s</div>" % (t, d) for t, d in _terms)
_grid = ("<div style='display:grid;grid-template-columns:max-content 1fr;gap:9px 18px;"
         "text-align:left;line-height:1.55'>%s</div>" % _rows)
build_chapter(None, "Glossary", info=note_box(_grid, grey=True), icon="🔤", anchor="glossary")
