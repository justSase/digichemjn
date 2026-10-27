_txt = (
  "Here is where counting stops being an exercise. A protein sequence is an element of "
  + imath(r"\text{AminoA}^n") + " — the Cartesian product of the twenty natural amino acids"
  + cite(4) + " with itself, n times — so the number of possible sequences of length n is "
  + imath("20^n") + ". A peptide of 10 residues already has " + imath("20^{10}") + " ≈ 10¹³ "
  "possibilities, which is more than any experiment can enumerate and roughly why directed "
  "evolution, docking and machine learning exist at all.<br><br>"
  "The second question is the one chapter 7 answers. If you want to mutate exactly <b>k</b> "
  "positions out of <b>n</b>, and you do not care in which order you pick them, the number of "
  "position sets is " + imath(r"\binom{n}{k}") + ". Each of those positions can then become any "
  "of the 19 other residues, so the size of that mutant library is "
  + imath(r"\binom{n}{k}\cdot 19^k") + ". Both factors are from this notebook: an unordered "
  "choice, times an ordered product.<br><br>"
  "<b>Change the numbers below to your own protein</b> and re-run. The values here are a "
  "plausible small domain, not a measurement.")

_code = r'''
import numpy as np, matplotlib.pyplot as plt
from math import comb

# ---- your own values -----------------------------------------------------
n_res    = 60      # length of your sequence (number of residues)
alphabet = 20      # 20 natural amino acids
k_max    = 6       # largest number of simultaneous mutations to plot
# --------------------------------------------------------------------------

ks   = np.arange(0, k_max + 1)
lib  = np.array([comb(n_res, int(k)) * (alphabet - 1) ** int(k) for k in ks], dtype=float)
whole = float(alphabet) ** n_res

print("sequence length          : %d" % n_res)
print("whole sequence space     : %d^%d = 10^%.1f" % (alphabet, n_res, np.log10(whole)))
for k, v in zip(ks, lib):
    print("  exactly %d mutation(s)  : C(%d,%d) x %d^%d = %.3g"
          % (k, n_res, k, alphabet - 1, k, v))
print("all libraries up to k=%d  : %.3g  (a fraction %.1e of the whole space)"
      % (k_max, lib.sum(), lib.sum() / whole))

fig, ax = plt.subplots(figsize=(7.0, 3.8))
ax.semilogy(ks, np.maximum(lib, 1), "o-", color="#3f93d1", lw=2.2, ms=7)
ax.axhline(whole, color="#e0563f", ls="--", lw=1.6)
ax.text(0.1, whole, " whole sequence space", color="#e0563f", va="bottom", fontsize=9)
ax.set_xlabel("k  (positions mutated at once)")
ax.set_ylabel("number of variants")
ax.set_title("C(n,k) x 19^k  against the whole space", fontsize=10)
ax.grid(True, alpha=.25)
fig.tight_layout()
'''

build_chapter(None, "Bring your own data: how big is a mutant library?", icon="🧪",
  chapter_open=False, anchor="byod", info=note_box(_txt),
  body=[editable_runner(_code, run_label="Run ▶", height="430px"),
        note_box("<b>Things to try.</b> Raise <b>k</b> by one and watch the library grow by "
                 "roughly a factor of 19·(n−k)/(k+1) — the two effects of chapter 7 pulling "
                 "against each other. Then notice the gap to the dashed line: even every "
                 "single, double and triple mutant of a 60-residue domain together is a "
                 "vanishing fraction of 20⁶⁰. Exhaustive search is not merely expensive here, "
                 "it is arithmetically hopeless, and that is a statement from this notebook "
                 "rather than from biology. Finally set <b>alphabet</b> to 4 and <b>n_res</b> "
                 "to the length of a primer: the same two formulas count oligonucleotides."),
        completion_button("b1", "I have run this with my own values")], task="b1")
