# References & Literature. Keyed by stable source ids (the same ids the chapters pass
# to cite()). Printed in first-citation order via the registry, so the visible [n]
# markers run 1, 2, 3, … in reading order. All sources are real; the lecture's own
# references are reused, each checked against its DOI / URL.
BIB = {
  1: ("E. C. Butcher, E. L. Berg, E. J. Kunkel, &ldquo;Systems biology in drug discovery&rdquo;, "
      "<i>Nature Biotechnology</i> <b>2004</b>, <i>22</i>, 1253&ndash;1259. "
      "DOI: <a href='https://doi.org/10.1038/nbt1017'>10.1038/nbt1017</a>."),
  2: ("K. Yilmaz, J. A. Vrugt, H. Gupta, S. Sorooshian, &ldquo;Model calibration in watershed "
      "hydrology&rdquo;, <b>2010</b>. DOI: "
      "<a href='https://doi.org/10.1142/9789814307987_0003'>10.1142/9789814307987_0003</a>."),
  3: ("A. J. A. M. Temme, J. M. Schoorl, L. Claessens, A. Veldkamp, &ldquo;Quantitative Modeling of "
      "Landscape Evolution&rdquo;, <b>2021</b>. DOI: "
      "<a href='https://doi.org/10.1016/B978-0-12-818234-5.00140-1'>10.1016/B978-0-12-818234-5.00140-1</a>."),
  4: ("J. Barrowman, M. Wilson, &ldquo;Total intravenous anaesthesia&rdquo;, <i>Anaesthesia &amp; "
      "Intensive Care Medicine</i> <b>2022</b>, <i>23</i>(1), 54&ndash;59. DOI: "
      "<a href='https://doi.org/10.1016/j.mpaic.2021.09.003'>10.1016/j.mpaic.2021.09.003</a>."),
  5: ("D. Bindellini, P. Simon, D. Busse, et al., &ldquo;Evaluation of the need for dosing adaptations "
      "in obese patients for surgical antibiotic prophylaxis: a model-based analysis of cefazolin "
      "pharmacokinetics&rdquo;, <i>British Journal of Anaesthesia</i> <b>2025</b>, <i>134</i>(4), "
      "1041&ndash;1049. DOI: <a href='https://doi.org/10.1016/j.bja.2024.11.044'>10.1016/j.bja.2024.11.044</a>."),
  6: ("M. Ghasemizade, M. Schirmer, &ldquo;Subsurface flow contribution in the hydrological "
      "cycle&rdquo;, <b>2015</b>. DOI: "
      "<a href='https://doi.org/10.13140/RG.2.1.1878.9608'>10.13140/RG.2.1.1878.9608</a>."),
  7: ("S. J. D. Prince, &ldquo;Bayesian Machine Learning: Function Space&rdquo;, Borealis AI. "
      "<a href='https://rbcborealis.com/research-blogs/bayesian-machine-learning-function-space/'>"
      "rbcborealis.com</a>."),
  8: ("G. E. P. Box, &ldquo;Science and Statistics&rdquo;, <i>Journal of the American Statistical "
      "Association</i> <b>1976</b>, <i>71</i>(356), 791&ndash;799. DOI: "
      "<a href='https://doi.org/10.1080/01621459.1976.10480949'>10.1080/01621459.1976.10480949</a>."),
  9: ("M. D. Wilkinson, M. Dumontier, IJ. J. Aalbersberg, et al., &ldquo;The FAIR Guiding Principles "
      "for scientific data management and stewardship&rdquo;, <i>Scientific Data</i> <b>2016</b>, "
      "<i>3</i>, 160018. DOI: <a href='https://doi.org/10.1038/sdata.2016.18'>10.1038/sdata.2016.18</a>."),
  10: ("&ldquo;Goodhart&rsquo;s law&rdquo;, Sketchplanations. "
       "<a href='https://sketchplanations.com/goodharts-law'>sketchplanations.com/goodharts-law</a>."),
}

# The list is written LAST and shown HERE (as in Complex): its numbers follow
# the order the sources first appear, and the quiz and the own-data section now
# come after this one (they cite too). So the box is placed empty and filled by
# a finalizer once every section exists — together with the OER record, whose
# goals and working time come from register_goals() and time_budget_text().
_refs_box = HTML(layout=_w(), value="")
_meta_box = HTML(layout=_w(), value="")

def _fill_references():
    _items = "".join(
        "<li id='%s' style='margin:7px 0;scroll-margin-top:64px'>%s</li>"
        % (_aid("ref%d" % _CITEREG["num"][sid]), BIB[sid])
        for sid in _CITEREG["order"] if sid in BIB)
    _refs_box.value = note_box(
      "Content in this notebook is backed by the following sources; the [n] markers in the text link here "
      "and are numbered in the order they first appear. The lecture's own references are reused."
      "<ol style='margin:12px 0 0;padding-left:24px;line-height:1.7'>%s</ol>"
      "<div style='margin-top:14px;font-size:.92em;opacity:.85'>Based on the lecture "
      "<b>Vertiefende Methoden der Bioinformatik &mdash; Introduction to Modeling</b> "
      "(Prof. Dr. Stefan G&uuml;nther / Sinclair Rockwell-Kollmann, Universit&auml;t Freiburg, WS&nbsp;2025/26). "
      "All sources were checked against their DOIs / URLs.</div>" % _items, grey=True).value
    set_metadata(objectives=goal_strings(), duration=time_budget_text())
    _meta_box.value = metadata_box().value

on_notebook_built(_fill_references)
build_chapter(None, "References and licence", icon="📎", chapter_open=False, anchor="references",
              body=[_refs_box, _meta_box])
