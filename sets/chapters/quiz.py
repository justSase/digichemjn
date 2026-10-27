QUIZ = [
 {"question": "A set A has 5 elements. How many subsets does it have?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "32", "correct": True,
     "feedback": "Correct — each element is independently in or out, so 2⁵ = 32."},
    {"answer": "25", "correct": False, "feedback": "That is 5², not 2⁵."},
    {"answer": "31", "correct": False,
     "feedback": "Close — but the empty set counts as a subset too, so nothing is subtracted."},
    {"answer": "5", "correct": False, "feedback": "That is the number of elements."}]},
 {"question": "A ∪ B contains the elements that are …",
  "type": "multiple_choice",
  "answers": [
    {"answer": "in at least one of the two", "correct": True,
     "feedback": "Yes — ∨ is the inclusive or, so the shared elements stay in."},
    {"answer": "in exactly one of the two", "correct": False,
     "feedback": "That is the symmetric difference. The mathematical or is inclusive."},
    {"answer": "in both", "correct": False, "feedback": "That is the intersection."},
    {"answer": "in neither", "correct": False, "feedback": "That is (A ∪ B)ᶜ."}]},
 {"question": "(A ∪ B)ᶜ equals …",
  "type": "multiple_choice",
  "answers": [
    {"answer": "Aᶜ ∩ Bᶜ", "correct": True,
     "feedback": "Correct — De Morgan. Not in (A or B) means not in A and not in B."},
    {"answer": "Aᶜ ∪ Bᶜ", "correct": False,
     "feedback": "That is (A ∩ B)ᶜ. The complement swaps the operator."},
    {"answer": "A ∩ B", "correct": False, "feedback": "No complement has been taken there."},
    {"answer": "M \\ (A ∩ B)", "correct": False,
     "feedback": "That is (A ∩ B)ᶜ again — a larger region whenever A ∩ B is not empty."}]},
 {"question": "M₁ has 4 elements, M₂ has 3. How many elements has M₁ × M₂?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "12", "correct": True,
     "feedback": "Correct — every first entry pairs with every second, so the counts multiply."},
    {"answer": "7", "correct": False, "feedback": "You added. A product is not a union."},
    {"answer": "64", "correct": False, "feedback": "That is 4³."},
    {"answer": "6", "correct": False,
     "feedback": "That would ignore the order, but a Cartesian product is ordered."}]},
 {"question": "Which number is in ℝ but not in ℚ?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "√2", "correct": True,
     "feedback": "Correct — it cannot be written as a ratio of two integers."},
    {"answer": "−7", "correct": False, "feedback": "That is in ℤ, and ℤ ⊂ ℚ."},
    {"answer": "3/4", "correct": False, "feedback": "A ratio of integers is exactly what ℚ is."},
    {"answer": "0", "correct": False, "feedback": "0 is rational: 0/1."}]},
 {"question": "Σ from j = 3 to 7 of j² has how many terms?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "5", "correct": True,
     "feedback": "Correct — both limits are inclusive: 3, 4, 5, 6, 7."},
    {"answer": "4", "correct": False,
     "feedback": "That is 7 − 3. The upper limit belongs to the sum, so add one."},
    {"answer": "7", "correct": False, "feedback": "The sum starts at 3, not at 1."},
    {"answer": "135", "correct": False, "feedback": "That is the value of the sum, not the term count."}]},
 {"question": "Why does 'choose 6 from 49' divide by 6!?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "Because the order of the six numbers does not matter",
     "correct": True,
     "feedback": "Correct — those same six could have been drawn in 6! = 720 orders, "
                 "and a ticket does not distinguish them."},
    {"answer": "Because a number cannot be drawn twice", "correct": False,
     "feedback": "That is already handled by the factors falling 49·48·47…, not by the division."},
    {"answer": "To make the result a whole number", "correct": False,
     "feedback": "It does come out whole, but that is a consequence, not the reason."},
    {"answer": "Because there are 6 numbers on the ticket", "correct": False,
     "feedback": "True but not the reason — it is the number of ORDERS of those 6 that is divided out."}]},
]
_qout = Output()
with _qout:
    try:
        from jupyterquiz import display_quiz
        display_quiz(QUIZ)
    except Exception as _e:
        display(IHTML("<div style='text-align:center'>Quiz unavailable: %r</div>" % (_e,)))
build_chapter(None, "Multiple choice quiz", icon="❓", chapter_open=False, anchor="quiz",
  body=[_qout, completion_button("q1", "I have worked through the quiz")], task="q1")
