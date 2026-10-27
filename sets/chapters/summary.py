_rows = [
 ("a set", "an amount of elements; the only question it answers is in / not in"),
 ("∈ ∉ ⊂ ∅", "member, not a member, subset, the empty set"),
 ("# A", "cardinality — how many elements (also written |A|)"),
 ("2ⁿ", "the number of subsets of an n-element set: in or out, independently"),
 ("A ∩ B", "in both;  A ∩ B = ∅ means A and B are disjoint"),
 ("A ∪ B", "in at least one — the inclusive or, so the overlap is kept"),
 ("M \\ A", "in M but not in A;  Aᶜ = {x | x ∉ A}"),
 ("#(A∪B)", "= #A + #B − #(A∩B): count, then remove what was counted twice"),
 ("M₁ × M₂", "all ordered pairs (a, b);  #M = #M₁ · #M₂"),
 ("De Morgan", "(A∪B)ᶜ = Aᶜ ∩ Bᶜ  and  (A∩B)ᶜ = Aᶜ ∪ Bᶜ — a complement swaps ∪ and ∩"),
 ("ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ", "counting → subtraction → division → no gaps"),
 ("(a,b) vs [a,b]", "the bracket says whether the endpoint belongs to the set"),
 ("Σ, Π", "abbreviations; both limits are inclusive — count the terms first"),
 ("n!", "∏ⱼ₌₁ⁿ j, and 0! = 1"),
 ("C(n,k)", "n!/((n−k)!k!) — the ordered count, divided by the k! orders you ignore"),
 ("(a+b)ⁿ", "= Σⱼ C(n,j) aʲ bⁿ⁻ʲ — the same coefficient, counting which brackets gave a"),
]
_html = "".join(
  "<tr><td style='padding:5px 16px 5px 0;vertical-align:top;white-space:nowrap'><b>%s</b></td>"
  "<td style='padding:5px 0'>%s</td></tr>" % r for r in _rows)
build_chapter(None, "Summary", icon="📋", chapter_open=False, anchor="summary",
  info=note_box("Everything in one screen:"
                "<table style='border-collapse:collapse;margin:12px auto 0'>%s</table>" % _html))
