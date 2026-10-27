info = note_box(
  "This notebook is part of a planned series. The series turns lecture material of <b>Vertiefende Methoden der "
  "Bioinformatik</b> into interactive open educational resources (free teaching material). Basic prerequisites come "
  "before it, deeper applications after it. Each will appear as a separate notebook and will be "
  "<b>linked here</b> once it exists."
  "<div style='margin-top:12px'><b>Fundamentals, recommended beforehand (coming soon):</b>"
  "<ul style='margin:4px 0 0;padding-left:22px;line-height:1.6'>"
  "<li>Introduction to Python programming <i>(coming soon)</i></li>"
  "<li>Working with data: NumPy &amp; pandas basics <i>(coming soon)</i></li>"
  "<li>Scientific plotting with matplotlib <i>(coming soon)</i></li>"
  "</ul></div>"
  "<div style='margin-top:12px'><b>Advanced, building on this notebook (coming soon):</b>"
  "<ul style='margin:4px 0 0;padding-left:22px;line-height:1.6'>"
  "<li>Compartmental pharmacokinetic modelling in depth (multi-compartment, absorption) <i>(coming soon)</i></li>"
  "<li>Global sensitivity analysis (Sobol indices) &amp; uncertainty quantification <i>(coming soon)</i></li>"
  "<li>Machine learning &amp; large language models, step by step <i>(available as a separate notebook)</i></li>"
  "</ul></div>"
  "<div style='margin-top:14px;padding-top:12px;border-top:1px solid var(--nbskin-line,#cdd6dd)'>All notebooks of the series "
  "will be collected on the project's GitHub page: "
  "<a href='https://github.com/digichemjn/digichemjn'>github.com/digichemjn/digichemjn</a> "
  "<i>(placeholder link: the repository fills up as the notebooks are published)</i>.</div>"
  # E21.13 — the contact for errors and feedback, at the very bottom
  "<div class='nbcontact' style='margin-top:14px;padding-top:12px;border-top:1px solid var(--nbskin-line,#cdd6dd)'>"
  "Found a mistake, or want to tell us what helped and what did not? Write to "
  "<a href='mailto:samuel.wiese@gmx.de'>samuel.wiese@gmx.de</a>.</div>",
  grey=True)
build_chapter(None, "Topic roadmap", info=info, icon="🗺️", anchor="roadmap", chapter_open=False)
