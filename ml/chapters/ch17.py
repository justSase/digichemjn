# References & Literature.
# The bibliography is keyed by STABLE source ids (the same 1..14 that the chapters
# pass to cite()). The list is printed in the order the sources are FIRST cited in
# the notebook (from the citation registry _CITEREG), so the visible [n] markers run
# 1, 2, 3, … in reading order and each entry gets a matching id="ref{n}" anchor.
# All sources are real and verified against their DOI / arXiv identifiers.
BIB = {
  1: ("D. E. Rumelhart, G. E. Hinton, R. J. Williams, &ldquo;Learning representations by "
      "back-propagating errors&rdquo;, <i>Nature</i> <b>1986</b>, <i>323</i>, 533&ndash;536. "
      "DOI: <a href='https://doi.org/10.1038/323533a0'>10.1038/323533a0</a>."),
  2: ("Y. LeCun, Y. Bengio, G. Hinton, &ldquo;Deep learning&rdquo;, <i>Nature</i> <b>2015</b>, "
      "<i>521</i>, 436&ndash;444. DOI: <a href='https://doi.org/10.1038/nature14539'>10.1038/nature14539</a>."),
  3: ("A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, "
      "I. Polosukhin, &ldquo;Attention Is All You Need&rdquo;, <i>Advances in Neural Information "
      "Processing Systems (NeurIPS)</i> <b>2017</b>. arXiv: "
      "<a href='https://arxiv.org/abs/1706.03762'>1706.03762</a>."),
  4: ("I. Goodfellow, Y. Bengio, A. Courville, <i>Deep Learning</i>, MIT Press, <b>2016</b>. "
      "Freely available at <a href='https://www.deeplearningbook.org'>deeplearningbook.org</a>."),
  5: ("C. M. Bishop, <i>Pattern Recognition and Machine Learning</i>, Springer, <b>2006</b>. "
      "Freely available at "
      "<a href='https://www.microsoft.com/en-us/research/publication/pattern-recognition-machine-learning/'>"
      "microsoft.com/research</a>."),
  6: ("T. Hastie, R. Tibshirani, J. Friedman, <i>The Elements of Statistical Learning</i>, "
      "2nd ed., Springer, <b>2009</b>. Freely available at "
      "<a href='https://hastie.su.domains/ElemStatLearn/'>hastie.su.domains/ElemStatLearn</a>."),
  7: ("T. Mikolov, K. Chen, G. Corrado, J. Dean, &ldquo;Efficient Estimation of Word "
      "Representations in Vector Space&rdquo;, <b>2013</b>. arXiv: "
      "<a href='https://arxiv.org/abs/1301.3781'>1301.3781</a>."),
  8: ("J. S. Delaney, &ldquo;ESOL: Estimating Aqueous Solubility Directly from Molecular "
      "Structure&rdquo;, <i>J. Chem. Inf. Comput. Sci.</i> <b>2004</b>, <i>44</i>, 1000&ndash;1005. "
      "DOI: <a href='https://doi.org/10.1021/ci034243x'>10.1021/ci034243x</a>."),
  9: ("T. B. Brown, B. Mann, N. Ryder, et al., &ldquo;Language Models are Few-Shot "
      "Learners&rdquo; (GPT-3), <i>NeurIPS</i> <b>2020</b>. arXiv: "
      "<a href='https://arxiv.org/abs/2005.14165'>2005.14165</a>."),
  10: ("A. Holtzman, J. Buys, L. Du, M. Forbes, Y. Choi, &ldquo;The Curious Case of Neural "
       "Text Degeneration&rdquo;, <i>ICLR</i> <b>2020</b>. arXiv: "
       "<a href='https://arxiv.org/abs/1904.09751'>1904.09751</a>."),
  11: ("Z. Ji, N. Lee, R. Frieske, et al., &ldquo;Survey of Hallucination in Natural Language "
       "Generation&rdquo;, <i>ACM Computing Surveys</i> <b>2023</b>, <i>55</i>(12), Article 248. "
       "DOI: <a href='https://doi.org/10.1145/3571730'>10.1145/3571730</a>."),
  12: ("E. M. Bender, T. Gebru, A. McMillan-Major, S. Shmitchell, &ldquo;On the Dangers of "
       "Stochastic Parrots: Can Language Models Be Too Big?&rdquo;, <i>ACM FAccT</i> <b>2021</b>. "
       "DOI: <a href='https://doi.org/10.1145/3442188.3445922'>10.1145/3442188.3445922</a>."),
  13: ("M. D. Wilkinson, M. Dumontier, IJ. J. Aalbersberg, et al., &ldquo;The FAIR Guiding "
       "Principles for scientific data management and stewardship&rdquo;, <i>Scientific Data</i> "
       "<b>2016</b>, <i>3</i>, 160018. DOI: "
       "<a href='https://doi.org/10.1038/sdata.2016.18'>10.1038/sdata.2016.18</a>."),
  14: ("F. Pedregosa, G. Varoquaux, A. Gramfort, et al., &ldquo;Scikit-learn: Machine Learning "
       "in Python&rdquo;, <i>Journal of Machine Learning Research</i> <b>2011</b>, <i>12</i>, "
       "2825&ndash;2830. <a href='https://www.jmlr.org/papers/v12/pedregosa11a.html'>jmlr.org</a>."),
  15: ("N. J. A. Sloane (ed.), &ldquo;Decimal expansion of <i>e</i>&rdquo;, Sequence A001113 in the "
       "<i>On-Line Encyclopedia of Integer Sequences</i> (OEIS). "
       "<a href='https://oeis.org/A001113'>oeis.org/A001113</a>."),
}

# print the entries in first-citation order; the <ol> marker equals the id number
# because _CITEREG assigns 1, 2, 3, … in exactly this order
_items = "".join(
    "<li id='%s' style='margin:7px 0;scroll-margin-top:64px'>%s</li>"
    % (_aid("ref%d" % _CITEREG["num"][sid]), BIB[sid])
    for sid in _CITEREG["order"] if sid in BIB)

info = note_box(
  "Content in this notebook is backed by the following sources; the [n] markers in the "
  "text link here and are numbered in the order they first appear. Foundational textbooks "
  "cover the general methods, while individual papers back the specific claims about deep "
  "learning, transformers, embeddings, language models and reproducibility."
  "<ol style='margin:12px 0 0;padding-left:24px;line-height:1.7'>%s</ol>"
  "<div style='margin-top:14px;color:#5b6b7b;font-size:.92em'>This project also builds on the "
  "open teaching material <b>intro_pharma_ai</b> (kochgroup) and <b>TeachOpenCADD</b> "
  "(volkamerlab). All sources were checked against their DOIs / arXiv identifiers.</div>"
  % _items, grey=True)
build_chapter(None, "References & Literature", info=info, icon="📎", anchor="references")
