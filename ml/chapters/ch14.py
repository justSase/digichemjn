info = note_box(
  "A modern LLM is nothing exotic. It scales up exactly the pieces you have just built: <b>tokens "
  "&rarr; embeddings &rarr; many attention layers &rarr; softmax over the vocabulary</b>, trained by "
  "next-token prediction (<b>pre-training</b>), then adapted (<b>fine-tuning</b>, instruction-tuning, "
  "RLHF) and steered by <b>prompting</b>" + cite(2, 9) + ". What such a model can and cannot be trusted "
  "to do is the subject of the next section.")
build_chapter(12, "What LLMs are and are not", info=info)
