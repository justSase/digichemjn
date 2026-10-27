import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)
NBFILE=1
"""The lock/progress state machine, exactly as specified:
   solve   -> green +1, content AND exercise of the next chapter open
   skip    -> ⤼, next chapter CONTENT opens, its EXERCISE stays locked
   bypass  -> ✗, exercise opens too, but NO bar moves
   code    -> purple +1 (and counts as solved)"""
import json, io, contextlib, re, sys
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display=lambda *a,**k: None
src="\n".join(l for l in __import__("megasrc").expand("".join(max(json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "Complex_Numbers_Step_by_Step.ipynb"))
              ["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines() if not l.strip().startswith("%pip"))
G={"__name__":"__main__","display":lambda *a,**k:None}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src,"m","exec"),G)
T,L = G["_TASKS"], G["_LOCKS"]
# E28 (2026-10-12) — the late block below used Complex's t5/t6/t7 by name; the
# template has five exercises: there it is the last two (no third one to stay locked)
L5, L6, L7 = ("t5", "t6", "t7") if len(T["order"]) >= 7 else (T["order"][-2], T["order"][-1], None)
counts=G["_prog_counts"]; fails=[]

def show(tag):
    d,t,cd,ct = counts()
    st = "".join({"open":"·","done":"✓","skip":"⤼","fail":"✗"}[T["state"][k]] for k in T["order"])
    print("%-26s green %d/%-2d  purple %d/%-2d  states %s" % (tag,d,t,cd,ct,st))
    return d,cd

def lock(kind,key): 
    e=L.get((kind,key)); return None if e is None else e["open"]

print("locks registered: chapter=%d  practice=%d"
      % (sum(1 for k in L if k[0]=="chapter"), sum(1 for k in L if k[0]=="practice")))
if sum(1 for k in L if k[0]=="chapter")==0: fails.append("no chapter locks were created")
if any(k[0]=="content" for k in L):
    fails.append("chapter CONTENT is locked somewhere — all text must stay readable")

d0,c0 = show("start")
if d0 or c0: fails.append("progress does not start at zero")

# --- SKIP t1: content of ch2 opens, exercise of ch2 must stay locked ---
G["task_skipped"]("t1"); d,c = show("skip t1")
if T["state"]["t1"]!="skip": fails.append("skip did not set the ⤼ state")
if lock("chapter","t1") is not True: fails.append("skip did not open the next exercise")
if d!=0: fails.append("a skipped task moved the green bar")

# --- SOLVE t2 properly: both locks of ch3 open, green +1 ---
G["task_solved"]("t2"); d,c = show("solve t2")
if T["state"]["t2"]!="done": fails.append("solve did not set done")
if not lock("chapter","t2"): fails.append("solve did not open the next exercise")
if d!=1: fails.append("green bar did not count the solved task")

# --- BYPASS t1: the exercise is opened anyway -> red ✗, no bar movement ---
G["task_bypassed"]("t1"); d,c = show("bypass t1")
if T["state"]["t1"]!="fail": fails.append("bypass did not set the ✗ state")
if lock("chapter","t1") is not True: fails.append("bypass did not open the exercise")
if d!=1: fails.append("a bypassed task moved the green bar")

# --- CODE route on t3: purple +1, green unchanged, circle upper half ---
G["task_code_solved"]("t3"); d,c = show("code-solve t3")
if T["code"]["t3"]!="done": fails.append("code route did not register")
if c!=1: fails.append("purple bar did not count the code solution")
if d!=1: fails.append("the code route must NOT fill the green bar")
if G["_dot_class"]("t3")!="st-open": fails.append("the code route must not fill the answer circle")
# 2026-09-24n: the two chains are separate. The code route opens the next
# CODING exercise and deliberately does NOT open a chapter.
_codelocks = [k[1] for k in L if k[0] == "code"]
print("code chain guards:", _codelocks)
if not _codelocks:
    fails.append("no coding lock registered — the purple chain is not wired up")
else:
    _g = _codelocks[0]
    G["task_code_solved"](_g)
    if lock("code", _g) is not True:
        fails.append("a correct code solution must open the next coding exercise")
    # 2026-09-27e — THIS LINE USED TO SAY THE OPPOSITE: "the code route must
    # not touch a chapter lock" — the rule of 24n, overturned by 24ak (a right
    # answer opens the next chapter, whichever route it came from) and by the
    # user's decision of 27.09. (F). It stayed green for a month because the
    # chapter it looked at had already been opened by the skip on t1 above:
    # before == after == True. Green because of the state, not because of the
    # rule. The rule now, on a state where it can fail: see block F below.
    if T["code"][_g] != "done":
        fails.append("the code route did not register on its own key")
    # …and skipping the code opens the next coding exercise just the same
    G["reset_progress"]()
    if lock("code", _g) is not False:
        fails.append("reset did not close the coding lock again")
    G["task_code_skipped"](_g)
    if lock("code", _g) is not True:
        fails.append("skipping the code must open the next coding exercise")
    if T["code"][_g] != "skip":
        fails.append("skipping the code did not record the state")
    G["reset_progress"]()
    G["task_code_bypassed"](_g)
    if lock("code", _g) is not True:
        fails.append("giving up on the code must open the next coding exercise")
    G["reset_progress"]()
    G["task_skipped"]("t1"); G["task_solved"]("t2"); G["task_bypassed"]("t1")
    G["task_code_solved"]("t3")

# --- answer t3 as well -> full circle ---
G["task_solved"]("t3"); d,c = show("also answer t3")
# 2026-09-24u: the circle is the ANSWER route only — the coding exercise has a
# mark of its own on the rail, so a second tick inside this one is gone.
if G["_dot_class"]("t3")!="st-ans": fails.append("an answered exercise should be green")
if d!=2: fails.append("green bar did not count the answer")

# --- circle halves for the other states ---
if G["_dot_class"]("t2")!="st-ans":  fails.append("answer-only circle should be the lower half")
if G["_dot_class"]("t1")!="st-fail": fails.append("bypassed circle should be red")
# an untouched exercise whose chapter is still shut shows the lock; once the
# guard is answered it becomes an ordinary open circle
if G["_dot_class"](L6)!="st-lock": fails.append("a locked circle should show the lock")
G["_open_lock"]("chapter", L5)          # open the shell without counting a solve
if G["_dot_class"](L6)!="st-open": fails.append("an unlocked circle should be empty")
if L7 and not G["_is_locked"](L7): fails.append("%s should still be locked" % L7)

# --- revealing the solution is a SKIP, not a wrong answer (2026-09-24q) ---
G["task_solution_opened"](L6); d2,c2 = show("solution revealed on %s" % L6)
if T["state"][L6]!="skip":
    fails.append("revealing the solution should mark ⤼, not ✗ (%s)" % T["state"][L6])

# --- a WRONGLY ENTERED answer is the only thing that marks ✗ now ---
G["task_wrong"](L5); d3,c3 = show("wrong answer on %s" % L5)
if T["state"][L5]!="fail": fails.append("a wrong answer did not mark ✗")
if G["_dot_class"](L5)!="st-fail": fails.append("a wrong answer should be red")
# 2026-09-28a (K1) — THIS BLOCK USED TO SAY: "a wrong answer must not unlock
# anything" — and it was green WITHOUT testing that. It compared the lock of
# t6 before and after a wrong answer on t6, but the solution revealed on t6 a
# few lines up had already opened it (27h: no; 28a: yes) — before == after
# either way whenever anything earlier touched it. The rule has also turned
# (K1: a task waits until the one before is answered — right, wrong or
# skipped). Checked now on a FRESH state, in block K1 below.
# ...and getting it right afterwards turns it green again
G["task_solved"](L5); d4,c4 = show("%s answered correctly after the ✗" % L5)
if T["state"][L5]!="done": fails.append("a correct answer after ✗ did not turn green")
if G["_dot_class"](L5) not in ("st-ans","st-both"):
    fails.append("the circle stayed red after a correct answer")
if d2!=d: fails.append("revealing the solution moved a bar")
G["task_solution_opened"]("t3")          # already solved -> must stay solved
if T["state"]["t3"]!="done": fails.append("revealing a solution downgraded a solved exercise")

# --- a solved task must never be downgraded by a later skip/bypass ---
G["task_skipped"]("t2"); G["task_bypassed"]("t2")
if T["state"]["t2"]!="done": fails.append("a solved task was downgraded")
d,c = show("skip+bypass on solved t2")
# t2, t3 and t5 (answered correctly after its ✗)
if d!=3: fails.append("green count changed unexpectedly (expected 3: t2, t3, t5)")

html=G["_prog_html"]()
# (the st-* classes are asserted per task above; here only the panel chrome)
for probe in ("nbmap-fill","nbmap-inner","st-fail","nbcodemark",
              "nbfeed","nbjump","nbchapdot","nbfull"):
    if probe not in html: fails.append("progress html is missing %r" % probe)
for _bad in ("✏️","💻","nbbar-emo","nbbar-num","fill-purple","nbbars"):
    if _bad in html: fails.append("the timeline carries the progress now, found %r" % _bad)
print("\ntimeline html: green fill in the rail, ✗ state, jump links, re-host source — all present"
      if not fails else "")
# --- K1 (2026-09-28a): SKIP ONLY AT THE EXERCISE; A WAITING TASK DOES NOT OPEN ---
# Every case on a FRESH state, so no assertion can pass on a lock something
# before it already opened (the lesson of the block above).
def _fresh():
    G["reset_progress"]()
    return dict(G.get("_GOTO") or {"seq": 0})["seq"]
def _both(k): return (lock("chapter", k), lock("practice", k))
def _widgets(w):
    yield w
    for c in getattr(w, "children", ()) or ():
        yield from _widgets(c)
def _cls(w): return tuple(getattr(w, "_dom_classes", ()))
if "unlock_chapter_only" in G:
    fails.append("K1: unlock_chapter_only is still there — the timeline's way past a lock")
if "skip_button" not in G:
    fails.append("K1: the toolkit has no skip_button — no 'Skip for now' at the exercise")
_k1 = T["order"][0]
_k1n = T["order"][1] if len(T["order"]) > 1 else None
# (a) the chapter lock carries no way past it any more
for (_kind, _key), _ent in L.items():
    if _kind not in ("chapter", "code"): continue
    for _w in (x for c in _ent["closed"] for x in _widgets(c)):   # what the lock SHOWS
        _d = str(getattr(_w, "description", "") or "")
        if "Skip" in _d or "open chapter only" in _d or "nbctl-unl" in _cls(_w):
            fails.append("K1: the %s lock of %s still offers %r" % (_kind, _key, _d or _cls(_w)))
            break
# (b) one "Skip for now" in every exercise with a lock chain, and in every coding fold
_pk = [k for k in T["order"] if T["pacc"].get(k) is not None]
_ck = [k for k in T["order"] if T["cacc"].get(k) is not None]
for _k in _pk:
    _n = sum(1 for _w in _widgets(T["pacc"][_k]) if "nbskipnow" in _cls(_w))
    if _n != 1: fails.append("K1: exercise %s carries %d 'Skip for now' buttons, want 1" % (_k, _n))
for _k in _ck:
    _ent = L.get(("code", T["cguard"].get(_k)))
    _root = _ent["real"] if (_ent and not _ent["open"]) else T["cacc"][_k]
    _n = sum(1 for _w in _widgets(_root) if "nbskipnow" in _cls(_w))
    if _n != 1: fails.append("K1: coding %s carries %d 'Skip for now' buttons, want 1" % (_k, _n))
print("K1: 'Skip for now' in %d exercises and %d coding folds" % (len(_pk), len(_ck)))
# (c) the button IS the skip: amber, and the next task opens (both locks)
_s0 = _fresh()
if _both(_k1) != (False, False): fails.append("K1: fresh state, %s's locks are %s" % (_k1, _both(_k1)))
_b = [w for w in _widgets(T["pacc"][_k1]) if "nbskipnow" in _cls(w)]
if _b:
    [w for w in _widgets(_b[0]) if hasattr(w, "click")][0].click()
    if T["state"][_k1] != "skip": fails.append("K1: 'Skip for now' did not mark %s ⤼ (%s)" % (_k1, T["state"][_k1]))
    if _both(_k1) != (True, True):
        fails.append("K1: after 'Skip for now' on %s the next chapter/exercise are %s, want open/open" % (_k1, _both(_k1)))
    # E8.3 (29.09.): a skip moves on (Paket 4), a wrong answer does not
    if G["_GOTO"]["seq"] == _s0: fails.append("E8.3: a skip did not ask the panel to move on")
# (d) a WRONG answer opens the next task too — and unfolds nothing, moves nothing
_s0 = _fresh()
_nacc = T["acc"].get(_k1n) if _k1n else None
_was = getattr(_nacc, "selected_index", None) if _nacc is not None else None
G["task_wrong"](_k1)
if T["state"][_k1] != "fail": fails.append("K1: a wrong answer did not mark ✗")
if _both(_k1) != (True, True):
    fails.append("K1: a wrong answer on %s left the next task %s, want open/open" % (_k1, _both(_k1)))
if _nacc is not None and getattr(_nacc, "selected_index", None) != _was:
    fails.append("K1: a wrong answer unfolded the next chapter")
if G["_GOTO"]["seq"] != _s0: fails.append("K1: a wrong answer asked the panel to move")
# (e) a revealed solution is ⤼, so it opens the next task as well
_fresh(); G["task_solution_opened"](_k1)
if _both(_k1) != (True, True):
    fails.append("K1: a revealed solution (⤼) left the next task %s" % (_both(_k1),))
# (f) an untouched task stays shut
_fresh()
if _both(_k1) != (False, False): fails.append("K1: reset did not shut %s again" % _k1)
# (g) a waiting CODING fold does not unfold, and opens after a wrong code answer
_cw = [k for k in _ck if T["cguard"].get(k)]
if _cw:
    _k = _cw[0]; _g = T["cguard"][_k]; _acc = T["cacc"][_k]
    _fresh()
    if "acc-tasklock" not in _cls(_acc):
        fails.append("K1: coding %s waits for %s but its fold is not marked acc-tasklock" % (_k, _g))
    _acc.selected_index = 0
    if _acc.selected_index is not None:
        fails.append("K1: coding %s unfolded while it waits for %s" % (_k, _g))
    G["task_wrong"](_g, "code")
    if lock("code", _g) is not True: fails.append("K1: a wrong code answer on %s did not open coding %s" % (_g, _k))
    if "acc-tasklock" in _cls(_acc): fails.append("K1: coding %s kept acc-tasklock after %s was answered" % (_k, _g))
    _acc.selected_index = 0
    if _acc.selected_index != 0: fails.append("K1: coding %s does not unfold once open" % _k)
    _acc.selected_index = None
    _fresh()
    if "acc-tasklock" not in _cls(_acc): fails.append("K1: reset did not lock coding %s's fold again" % _k)
    print("K1: coding %s waits for %s — shut, opens after a wrong answer, shut again after reset" % (_k, _g))
_fresh()

# --- F (2026-09-27e): CODING EXERCISES ARE EXERCISES ---------------------
# Measured on a FRESH state, so an assertion cannot pass on a lock that
# something before it already opened.
G["reset_progress"]()
# the coding exercises of THIS notebook (Complex t1…t7, Start only t1 and t3)
_cs = [k for k in T["order"] if T["has_code"].get(k)]
_ca = _cs[0] if _cs else "t1"
_cb = _cs[1] if len(_cs) > 1 else None
_cc = _cs[2] if len(_cs) > 2 else None
_goto = G.get("_GOTO")
if _goto is None:
    fails.append("F: the toolkit has no _GOTO — a right answer cannot move the reader on")
    _goto = {"run": "", "seq": 0, "route": "", "key": ""}
_seq0 = _goto["seq"]
if lock("chapter", _ca) is not False: fails.append("F: reset did not lock the chapter after %s again" % _ca)
G["task_code_solved"](_ca)
if lock("chapter", _ca) is not True:
    fails.append("F: coding %s solved did not open the next chapter" % _ca)
if _cb and lock("code", _ca) is not True:
    fails.append("F: coding %s solved did not open the next coding exercise" % _ca)
if T["state"][_ca] != "open":
    fails.append("F: the code route must not mark the WRITTEN exercise (%s)" % T["state"][_ca])
_h = G["_prog_html"]()
def _node(html, cls, key):
    m = re.search(r'<a class="nbjump nbmap-node %s[^"]*"[^>]*data-task="%s"[^>]*>(.*?)</a>' % (cls, key), html, re.S)
    return m.group(0) if m else ""
_c1, _c2 = _node(_h, "codetask", _ca), (_node(_h, "codetask", _cb) if _cb else "cd-current")
if "cd-done" not in _c1: fails.append("F: coding 1 is not drawn solved on the rail")
if 'data-cstate="done"' not in _c1: fails.append("F: coding 1 carries no data-cstate=done")
if "cd-current" not in _c2: fails.append("F: the purple door did not move to coding 2")
if _goto["seq"] != _seq0 + 1 or _goto["route"] != "c" or _goto["key"] != _ca:
    fails.append("F: coding 1 solved did not ask the panel to move on (%s)" % _goto)
if ('data-goto="%s:%d:c:%s"' % (_goto["run"], _goto["seq"], _ca)) not in _h:
    fails.append("F: the feed does not carry the move (data-goto)")
# skipped and wrong on the purple lane: their own states, and they open NO chapter
# (a notebook with one coding exercise has nothing left to skip here)
_sk = _cb or _ca; _wr = _cc or _ca
_ch2 = lock("chapter", _sk); _sq = _goto["seq"]
if _cb:
    G["task_code_skipped"](_cb)
    _h = G["_prog_html"]()
    if "cd-skip" not in _node(_h, "codetask", _cb) or 'data-cstate="skip"' not in _node(_h, "codetask", _cb):
        fails.append("F: coding %s skipped is not drawn amber (cd-skip / data-cstate)" % _cb)
if _cc:
    G["task_wrong"](_cc, "code"); _h = G["_prog_html"]()
    if "cd-fail" not in _node(_h, "codetask", _cc) or 'data-cstate="fail"' not in _node(_h, "codetask", _cc):
        fails.append("F: coding %s wrong is not drawn red (cd-fail / data-cstate)" % _cc)
if lock("chapter", _sk) != _ch2: fails.append("F: skipping a coding exercise opened a chapter")
# E8.3 (29.09.): the skip moves on, the wrong answer does not
if _goto["seq"] != _sq + (1 if _cb else 0):
    fails.append("E8.3: skip/wrong on the code route moved %d times, want %d"
                 % (_goto["seq"] - _sq, 1 if _cb else 0))
# the written route asks too — and a restore does not
_sq = _goto["seq"]
G["task_solved"]("t1")
if _goto["seq"] != _sq + 1 or _goto["route"] != "a":
    fails.append("F: a right written answer did not ask the panel to move on (%s)" % _goto)
if 'data-state="done"' not in _node(G["_prog_html"](), "task", "t1"):
    fails.append("F: exercise 1 carries no data-state=done")
_code = G["progress_code"](); G["reset_progress"](); _s1 = _goto["seq"]
G["apply_progress_code"](_code)
if _goto["seq"] != _s1: fails.append("F: restoring a progress code asked the panel to move")
print("F: coding counts, opens, is drawn; moves asked for: %d" % (_goto["seq"] - _seq0))

print(("GATING OK" if not fails else "FAILURES:\n- "+"\n- ".join(fails)))
sys.exit(1 if fails else 0)
