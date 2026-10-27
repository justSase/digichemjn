# ======================================================================
# DigiChemJN — SUBJECT PROFILES
# ----------------------------------------------------------------------
# ONE toolkit (chapter_template.py), several subject standards. A profile
# carries the things that legitimately differ between subject areas —
# policy and palette — and nothing else. Anything that is a bug fix or a
# new capability lives in the toolkit and therefore reaches every subject
# at once. Never fork chapter_template.py to make a new standard.
#
#   use_profile("biophysics")      -> call it once, in the setup file
#
# What a profile may set:
#   requires_code   does solving an exercise require Python?
#   objectives      which K-tags this standard commits to
#   design          DESIGN overrides (pill gradients, box palettes, …)
# ======================================================================
PROFILES = {
  "biophysics": dict(
      label        = "Biophysics",
      requires_code= False,
      # K2 (implement it in Python) is deliberately NOT part of this standard.
      # Coding stays available as the optional second route on every exercise,
      # but nothing in the notebook depends on it.
      objectives   = ["K1", "K3", "K4", "K5", "K6"],
      practice     = "answer-first",     # numeric / choice / target, code optional
      design       = dict(),             # inherits the toolkit defaults
  ),
  "bioinformatics": dict(
      label        = "Bioinformatics",
      requires_code= True,
      objectives   = ["K1", "K2", "K3", "K5", "K6"],
      practice     = "code-first",       # editable_exercise is the main route
      design       = dict(),
  ),
}

# The active profile. Chapters read PROFILE["requires_code"] / ["objectives"]
# rather than hard-coding the policy.
PROFILE = dict(PROFILES["biophysics"])

def use_profile(name):
    """Activate a subject standard. Call once, in the setup file, before any
    chapter renders (DESIGN is read while the boxes are built)."""
    if name not in PROFILES:
        raise KeyError("unknown profile %r — have %s" % (name, sorted(PROFILES)))
    PROFILE.clear(); PROFILE.update(PROFILES[name])
    DESIGN.update(PROFILE.get("design") or {})
    return PROFILE
