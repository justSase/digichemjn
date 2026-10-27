_g = [
 ("set", "an amount of elements, finite or infinite"),
 ("element / member", "a thing that is in a set; x ∈ M"),
 ("subset ⊂", "every element of the first set is also in the second"),
 ("empty set ∅", "the set with no elements; a subset of every set"),
 ("cardinality # A", "the number of elements of A; also written |A|"),
 ("countable", "infinite, but the elements can be listed so each is reached: ℕ, ℤ, ℚ"),
 ("uncountable", "infinite and no such list exists: ℝ"),
 ("intersection ∩", "the elements in both sets"),
 ("union ∪", "the elements in at least one — the inclusive or"),
 ("disjoint", "A ∩ B = ∅; the two sets share nothing"),
 ("relative complement \\", "M \\ A — in M but not in A"),
 ("absolute complement ᶜ", "Aᶜ = {x | x ∉ A} — everything outside A"),
 ("Cartesian product ×", "the set of ordered pairs (a, b), one entry from each set"),
 ("ordered", "(a, b) ≠ (b, a); the opposite of how a set behaves"),
 ("De Morgan rules", "(A∪B)ᶜ = Aᶜ∩Bᶜ and (A∩B)ᶜ = Aᶜ∪Bᶜ"),
 ("∀ ∃ ∃!", "for all, there exists (at least one), there exists exactly one"),
 ("∧ ∨ ¬", "logical and, or, not"),
 ("⇒ ⇐ ⇔", "implies, is implied by, is equivalent to"),
 ("order relation", "for any two elements you can say which is smaller"),
 ("interval", "a set of reals; the bracket says whether the endpoint belongs"),
 ("Σ, Π", "sum and product over an index, both limits inclusive"),
 ("factorial n!", "the product 1·2·…·n; 0! = 1 by convention"),
 ("binomial coefficient", "C(n,k) — the number of unordered choices of k from n"),
]
_html = "".join(
  "<tr><td style='padding:4px 16px 4px 0;vertical-align:top;white-space:nowrap'><b>%s</b></td>"
  "<td style='padding:4px 0'>%s</td></tr>" % r for r in _g)
build_chapter(None, "Glossary", icon="📖", chapter_open=False, anchor="glossary",
  info=note_box("<table style='border-collapse:collapse;margin:4px auto 0'>%s</table>" % _html))
