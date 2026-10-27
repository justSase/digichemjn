/* The HTML edition's runtime: figures, answers, the gate and the progress panel.

   State lives in localStorage. The series record uses the SAME key and the same
   shape as the notebook, so working here and working in the notebook add up to
   one progress for this notebook. */
(function(){
  var D = window.NBDATA, FIGS = window.NBFIGS || {}, CHECKS = window.NBCHECKS || {};
  var ORDER = D.tasks.order, LABEL = D.tasks.label || {};
  var KEY_STATE = "digichemjn.html." + D.id;
  var KEY_SERIES = "digichemjn.progress.v1";
  var S = {tasks: {}};
  ORDER.forEach(function(t){ S.tasks[t] = "open"; });
  try {
    var kept = JSON.parse(localStorage.getItem(KEY_STATE) || "null");
    if (kept && kept.tasks) ORDER.forEach(function(t){
      if (kept.tasks[t]) S.tasks[t] = kept.tasks[t]; });
  } catch (e) {}

  function settled(t){ return S.tasks[t] !== "open"; }
  function locked(t){
    var i = ORDER.indexOf(t);
    return i > 0 && !settled(ORDER[i-1]);
  }
  function save(){
    try { localStorage.setItem(KEY_STATE, JSON.stringify(S)); } catch (e) {}
    var done = ORDER.filter(function(t){ return S.tasks[t] === "done"; }).length;
    try {
      var all = JSON.parse(localStorage.getItem(KEY_SERIES) || "{}");
      all[D.notebook.id] = {title: D.notebook.title, a: [done, ORDER.length],
                            c: [0, 0], t: Date.now()};
      localStorage.setItem(KEY_SERIES, JSON.stringify(all));
    } catch (e) {}
  }

  // ---------------------------------------------------------------- figures
  function figValues(box){
    var v = [];
    box.querySelectorAll("input[type=range]").forEach(function(r){ v.push(parseFloat(r.value)); });
    var sel = box.querySelector("select");
    if (sel) v.push(sel.value);
    return v;
  }
  function drawFig(box){
    var id = box.getAttribute("data-fig"), spec = FIGS[id];
    var cv = box.querySelector("canvas"), wrap = box.querySelector(".nbcanvas-wrap");
    var vals = figValues(box);
    box.querySelectorAll(".nbsl").forEach(function(l){
      var r = l.querySelector("input[type=range]"), o = l.querySelector("output");
      if (r && o) o.textContent = (+r.value).toFixed(Math.abs(+r.step) < 0.1 ? 2 : 1);
    });
    if (!spec){ return; }                          // keeps the rendered PNG
    if (spec.frames){                              // a step-through figure
      var frames = D.frames[spec.frames] || [];
      var i = Math.max(0, Math.min(frames.length - 1, Math.round(vals[0])));
      var img = box.querySelector(".nbfallback");
      var m = /src="([^"]+)"/.exec(frames[i] || "");
      if (img && m) img.src = m[1];
      var labs = D.labels[spec.labels] || [];
      var slot = box.querySelector(".nbread-slot");
      if (slot && labs[i])
        slot.innerHTML = "<div class='nbread' style='text-align:center;font-size:.95em;"
                       + "margin:4px auto 2px'>" + labs[i] + "</div>";
      return;
    }
    wrap.classList.add("js");
    spec.draw(cv, vals);
    if (spec.read){
      var s = box.querySelector(".nbread-slot");
      if (s) s.innerHTML = spec.read(vals);
    }
  }
  function wireFigures(){
    document.querySelectorAll(".nbfig").forEach(function(box){
      box.addEventListener("input", function(){ drawFig(box); });
      box.addEventListener("change", function(){ drawFig(box); });
      drawFig(box);
    });
  }

  // ---------------------------------------------------------------- answers
  function feedback(box, ok, tip){
    var el = box.querySelector(".nbfeedback");
    if (!el) return;
    el.innerHTML = "<div class='nbmsg " + (ok ? "ok" : "no") + "'>"
                 + (ok ? "✓ " : "✗ ") + tip + "</div>";
  }
  function answerValues(box){
    var kind = box.getAttribute("data-kind");
    if (kind === "choice"){
      var picked = box.querySelector("input[type=radio]:checked");
      return picked ? {choice: parseInt(picked.value, 10)} : null;
    }
    var v = [];
    box.querySelectorAll("input[type=number]").forEach(function(inp){
      v.push(inp.value === "" ? NaN : parseFloat(inp.value)); });
    return v;
  }
  function runCheck(box){
    var task = box.getAttribute("data-task") || "";
    var fn = CHECKS[task] || (box.getAttribute("data-kind") === "choice" && !task
                              ? CHECKS.axis : null);
    if (!fn){ feedback(box, false, "This question has no checker on the HTML page."); return; }
    var vals = answerValues(box);
    if (vals === null){ feedback(box, false, "Pick one of the options first."); return; }
    if (Array.isArray(vals) && vals.some(isNaN)){
      feedback(box, false, "Fill in every box first."); return;
    }
    var r = fn(vals);
    feedback(box, r[0], r[1]);
    if (r[0] && task && S.tasks[task] !== "done"){
      S.tasks[task] = "done"; save(); render();
    }
  }
  // the slider exercise checks the figure, not a box
  function wireTarget(){
    document.querySelectorAll(".nbfig[data-task='t7']").forEach(function(fig){
      var host = fig.closest(".nbvbox") || fig.parentElement;
      var btn = document.createElement("div");
      btn.className = "nbans";
      btn.setAttribute("data-task", "t7");
      btn.setAttribute("data-kind", "target");
      btn.innerHTML = "<div class='nbcheck'><button class='sc-btn' data-check='t7'>"
                    + "🎯  Check position</button></div><div class='nbfeedback'></div>";
      fig.parentElement.insertBefore(btn, fig.nextSibling);
    });
  }
  function targetValues(){
    var fig = document.querySelector(".nbfig[data-task='t7']");
    var v = figValues(fig);
    return {r2: v[0], p2: v[1]};
  }

  // ---------------------------------------------------------------- the gate
  function lockBox(task){
    var lab = LABEL[ORDER[ORDER.indexOf(task)-1]] || "the previous exercise";
    return "<div class='nblock' data-lock='" + task + "'>"
         + "<div style='font-size:1.5em;line-height:1'>🔒</div>"
         + "<div style='font-weight:800;margin:8px 0 4px'>This exercise is still locked</div>"
         + "<div style='max-width:580px;margin:0 auto;line-height:1.55'>It opens as soon as <b>"
         + lab + "</b> is answered — that is the step it builds on. The chapter itself is fully "
         + "readable in the meantime. If you want to move on now, say which it is: coming back "
         + "later keeps a ⤼ in the panel, giving up marks it ✗. Neither fills the progress.</div>"
         + "<div style='margin-top:10px'>"
         + "<button class='sc-btn' data-skip='" + task + "'>⤼  Skip for now</button> "
         + "<button class='sc-btn' data-give='" + task + "'>✗  Give up, open it</button>"
         + "</div></div>";
  }
  function applyLocks(){
    document.querySelectorAll("details[data-lockfor]").forEach(function(acc){
      var task = acc.getAttribute("data-lockfor");
      if (!task) return;
      var body = acc.querySelector(".nbacc-body");
      var bar = acc.querySelector(".nblock");
      if (locked(task)){
        if (!bar){
          var d = document.createElement("div");
          d.innerHTML = lockBox(task);
          acc.insertBefore(d.firstChild, body);
        }
        body.style.display = "none";
      } else {
        if (bar) bar.remove();
        body.style.display = "";
      }
    });
  }

  // ---------------------------------------------------------------- panel
  function dotClass(t){
    var st = S.tasks[t];
    return st === "done" ? "st-ans" : st === "skip" ? "st-skip"
         : st === "fail" ? "st-fail" : "st-open";
  }
  var MARK = {skip: "⤼", fail: "✗"};
  function render(){
    var host = document.getElementById("nbpanel-root");
    if (!host) return;
    var cur = null;
    for (var i = 0; i < ORDER.length; i++)
      if (S.tasks[ORDER[i]] === "open"){ cur = ORDER[i]; break; }
    host.querySelectorAll(".nbmap-node.task").forEach(function(n){
      var t = n.getAttribute("data-task");
      var dot = n.querySelector(".nbrail-dot");
      if (!dot) return;
      dot.className = "nbrail-dot " + dotClass(t);
      dot.textContent = MARK[S.tasks[t]] || String(ORDER.indexOf(t) + 1);
      n.classList.toggle("is-current", t === cur);
    });
    measure(host);
    gauge(host);
    var done = ORDER.filter(function(t){ return S.tasks[t] === "done"; }).length;
    var badge = host.querySelector(".nbseries");
    if (badge) badge.textContent = "📚 " + done + "/" + ORDER.length;
    applyLocks();
  }
  function gauge(host){
    var inner = host.querySelector(".nbmap-inner"), fill = host.querySelector(".nbmap-fill");
    if (!inner || !fill) return;
    var nodes = inner.querySelectorAll(".nbmap-node");
    var span = Math.round(inner.scrollWidth || inner.getBoundingClientRect().width);
    var reached = null, lastChap = null, done = true;
    for (var i = 0; i < nodes.length; i++){
      var n = nodes[i];
      if (n.classList.contains("chap") || n.classList.contains("sect")) lastChap = n;
      if (!n.classList.contains("task")) continue;
      var d = n.querySelector(".nbrail-dot");
      if (!(d && (d.classList.contains("st-ans") || d.classList.contains("st-both")))){
        reached = lastChap || n; done = false; break;
      }
    }
    var w = done ? span : Math.round(reached.offsetLeft + reached.offsetWidth / 2);
    fill.style.width = w + "px";
    nodes.forEach(function(n){
      n.classList.toggle("passed", n.offsetLeft + n.offsetWidth / 2 <= w + 1);
    });
    if (reached) reached.classList.add("passed");
    var map = host.querySelector(".nbmap"), c = inner.querySelector(".is-current");
    if (map && c && host.getAttribute("data-follow") !== "manual")
      map.scrollLeft = Math.max(0, Math.min(
        c.offsetLeft - map.clientWidth / 2 + c.offsetWidth / 2, map.scrollWidth - map.clientWidth));
  }

  // the timeline mirrors the page: the gap between two markers is the gap between
  // the two pills they stand for
  function measure(host){
    var inner = host.querySelector(".nbmap-inner"), map = host.querySelector(".nbmap");
    if (!inner || !map) return;
    var nodes = [].slice.call(inner.querySelectorAll(".nbmap-node"));
    if (nodes.length < 2) return;
    var pos = nodes.map(function(n){
      var t = (n.getAttribute("data-target") || "").split("__")[0];
      var el = t ? document.getElementById(t) : null;
      if (!el) return null;
      return el.getBoundingClientRect().top + (window.scrollY || 0);
    });
    var first = null, last = null, k;
    for (k = 0; k < pos.length; k++)
      if (pos[k] !== null){ if (first === null) first = k; last = k; }
    if (first === null || last === first) return;
    for (k = 0; k < first; k++) pos[k] = pos[first];
    for (k = last + 1; k < pos.length; k++) pos[k] = pos[last];
    for (k = first + 1; k < last; k++){
      if (pos[k] !== null) continue;
      var a = k - 1, b = k;
      while (pos[b] === null) b++;
      var stp = (pos[b] - pos[a]) / (b - a);
      for (var m = a + 1; m < b; m++) pos[m] = pos[a] + stp * (m - a);
    }
    var gaps = [], total = 0;
    for (k = 0; k < pos.length - 1; k++){
      var g = Math.max(0, pos[k+1] - pos[k]); gaps.push(g); total += g;
    }
    if (total <= 0) return;
    var target = Math.max(760, Math.min(2600, (map.clientWidth || 480) * 2.4));
    var scale = target / total;
    nodes.forEach(function(n, i){
      var wpx = i < gaps.length ? Math.round(gaps[i] * scale) : 34;
      var mn = n.classList.contains("task") ? 34 : n.classList.contains("sect") ? 80 : 18;
      wpx = Math.max(mn, Math.min(220, wpx));
      if (n.style.width !== wpx + "px") n.style.width = wpx + "px";
    });
  }

  // ---------------------------------------------------------- settings drawer
  var SCHAR = {open: "o", done: "d", skip: "s", fail: "f"};
  var SBACK = {o: "open", d: "done", s: "skip", f: "fail"};
  function progressCode(){
    var body = D.notebook.id + "|"
             + ORDER.map(function(t){ return SCHAR[S.tasks[t]] || "o"; }).join("") + "|"
             + ORDER.map(function(){ return "o"; }).join("");
    return btoa(body).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function applyCode(code){
    var raw = (code || "").trim().replace(/-/g, "+").replace(/_/g, "/");
    var body;
    try { body = atob(raw + "===".slice((raw.length + 3) % 4)); }
    catch (e) { return [false, "That does not look like a progress code."]; }
    var parts = body.split("|");
    if (parts.length !== 3) return [false, "That does not look like a progress code."];
    if (parts[0] !== D.notebook.id)
      return [false, "This code belongs to \u201c" + parts[0] + "\u201d, not to this notebook."];
    if (parts[1].length !== ORDER.length)
      return [false, "The code covers " + parts[1].length + " exercises, this notebook has "
                   + ORDER.length + "."];
    for (var i = 0; i < ORDER.length; i++){
      var st = SBACK[parts[1][i]];
      if (!st) return [false, "The code contains a state this notebook does not know."];
      S.tasks[ORDER[i]] = st;
    }
    save(); render();
    var done = ORDER.filter(function(t){ return S.tasks[t] === "done"; }).length;
    return [true, "Restored: " + done + " of " + ORDER.length + " answered."];
  }
  function drawerHTML(){
    var lv = ["gentle", "standard", "strict"].map(function(l){
      return "<option value='" + l + "'" + (l === (S.level || "standard") ? " selected" : "")
           + ">" + l + "</option>"; }).join("");
    return "<div class='nbdrawer-grid'>"
      + "<div class='nbcell'><div class='nbcell-h'>Difficulty</div>"
      + "<select class='nbdiffsel'>" + lv + "</select>"
      + "<div class='nbink' style='font-size:.8em;margin-top:4px'>changes how close a typed "
      + "answer has to be</div></div>"
      + "<div class='nbcell'><div class='nbcell-h'>Carry your progress</div>"
      + "<button class='sc-btn nbcodeshow'>Show my code</button>"
      + "<input class='nbcodein' type='text' placeholder='paste a progress code here'>"
      + "<button class='sc-btn nbcodeload'>Restore</button>"
      + "<div class='nbcodeout' style='font-size:.82em;margin-top:4px;word-break:break-all'></div>"
      + "</div>"
      + "<div class='nbcell'><div class='nbcell-h'>This series, in this browser</div>"
      + "<div class='nbserieslist'>—</div></div>"
      + "<div class='nbcell'><div class='nbcell-h'>Start over</div>"
      + "<button class='sc-btn nbresetbtn'>\u21ba  Reset this notebook</button>"
      + "<div class='nbresetout' style='font-size:.82em;margin-top:4px'></div></div></div>";
  }
  function seriesList(){
    var el = document.querySelector("#nbpanel-root .nbserieslist");
    if (!el) return;
    var all = {};
    try { all = JSON.parse(localStorage.getItem(KEY_SERIES) || "{}"); } catch (e) {}
    var ids = Object.keys(all).sort();
    el.innerHTML = ids.length
      ? ids.map(function(k){
          var r = all[k];
          return "<div>" + (k === D.notebook.id ? "\u25b8 " : "&nbsp;&nbsp;")
               + "<b>" + r.title + "</b> \u2014 " + r.a[0] + "/" + r.a[1] + "</div>"; }).join("")
      : "Only this notebook so far.";
  }

  // ---------------------------------------------------------------- events
  var FONTS = ["", "nbfont-l", "nbfont-xl"];
  document.addEventListener("click", function(ev){
    var t = ev.target;
    var chk = t.closest && t.closest("[data-check]");
    if (chk){
      var task = chk.getAttribute("data-check");
      var box = chk.closest(".nbans");
      if (task === "t7"){
        var r = CHECKS.t7(targetValues());
        feedback(box, r[0], r[1]);
        if (r[0] && S.tasks.t7 !== "done"){ S.tasks.t7 = "done"; save(); render(); }
      } else runCheck(box);
      return;
    }
    var sk = t.closest && t.closest("[data-skip]");
    if (sk){ var k = sk.getAttribute("data-skip");
             if (S.tasks[k] === "open"){ S.tasks[k] = "skip"; save(); render(); } return; }
    var gv = t.closest && t.closest("[data-give]");
    if (gv){ var g = gv.getAttribute("data-give");
             if (S.tasks[g] === "open"){ S.tasks[g] = "fail"; save(); render(); } return; }
    var btn = t.closest && t.closest(".nbbtn");
    if (btn){
      ev.preventDefault();
      if (btn.classList.contains("nbfull")){
        if (document.fullscreenElement) document.exitFullscreen();
        else document.documentElement.requestFullscreen();
      } else if (btn.classList.contains("nbtheme")){
        document.body.classList.toggle("nbdark");
        document.querySelectorAll(".nbfig").forEach(drawFig);
      } else if (btn.classList.contains("nbgear")){
        var host = document.getElementById("nbpanel-root");
        var dr = host.querySelector(".nbdrawer");
        // the Python markup ships slots for the notebook's widgets; this edition
        // brings its own controls instead
        if (dr && dr.getAttribute("data-htmlfilled") !== "1"){
          dr.innerHTML = drawerHTML(); dr.setAttribute("data-htmlfilled", "1");
        }
        host.classList.toggle("open");
        seriesList();
        setTimeout(function(){ measure(host); gauge(host); }, 380);
      } else if (btn.classList.contains("nbfont")){
        var cur = FONTS.findIndex(function(c){ return c && document.body.classList.contains(c); });
        FONTS.forEach(function(c){ if (c) document.body.classList.remove(c); });
        var nxt = FONTS[(cur + 1 + FONTS.length) % FONTS.length];
        if (nxt) document.body.classList.add(nxt);
      }
      return;
    }
    if (t.classList && t.classList.contains("nbcodeshow")){
      t.parentElement.querySelector(".nbcodeout").textContent = progressCode();
      return;
    }
    if (t.classList && t.classList.contains("nbcodeload")){
      var inp = t.parentElement.querySelector(".nbcodein");
      var r = applyCode(inp.value);
      var out = t.parentElement.querySelector(".nbcodeout");
      out.textContent = r[1];
      out.style.color = r[0] ? "#2f8f63" : "#a3352b";
      return;
    }
    if (t.classList && t.classList.contains("nbresetbtn")){
      var o = t.parentElement.querySelector(".nbresetout");
      if (t.getAttribute("data-armed") !== "1"){
        t.setAttribute("data-armed", "1");
        o.textContent = "Click again to confirm — this clears every answer.";
        return;
      }
      ORDER.forEach(function(k){ S.tasks[k] = "open"; });
      save(); render(); seriesList();
      t.removeAttribute("data-armed");
      o.textContent = "Reset — " + ORDER.length + " exercises are open again.";
      return;
    }
    var jump = t.closest && t.closest(".nbjump");
    if (jump){
      var target = jump.getAttribute("data-target") || "";
      var id = target.split("__")[0];
      var el = document.getElementById(id);
      if (el){
        ev.preventDefault();
        var p = el.nextElementSibling || el.parentElement;
        var d = el.parentElement;
        while (d){ if (d.tagName === "DETAILS") d.open = true; d = d.parentElement; }
        var after = el.nextElementSibling;
        while (after && after.tagName !== "DETAILS") after = after.nextElementSibling;
        if (after) after.open = true;
        el.scrollIntoView({behavior: "smooth", block: "start"});
      }
    }
  }, true);

  // revealing a solution marks the exercise, exactly as in the notebook
  document.addEventListener("toggle", function(ev){
    var d = ev.target;
    if (d.classList && d.classList.contains("nbsol") && d.open){
      var task = d.getAttribute("data-task");
      if (task && S.tasks[task] === "open"){ S.tasks[task] = "fail"; save(); render(); }
    }
  }, true);

  window.addEventListener("resize", function(){
    var host = document.getElementById("nbpanel-root");
    if (host){ measure(host); gauge(host); }
  });
  // opening or closing a section moves the pills, so the timeline is re-measured
  document.addEventListener("toggle", function(){
    var host = document.getElementById("nbpanel-root");
    if (host) setTimeout(function(){ measure(host); gauge(host); }, 60);
  }, true);
  // the wheel scrolls the timeline while the pointer is over the panel
  document.addEventListener("change", function(ev){
    var sel = ev.target;
    if (sel.classList && sel.classList.contains("nbdiffsel")){
      S.level = sel.value;
      // gentle 2e-2 · standard 5e-3 · strict 1e-3, the same ladder as the notebook
      window.NBTOL = {gentle: 2e-2, standard: 5e-3, strict: 1e-3}[sel.value] || 5e-3;
      save();
    }
  }, true);
  document.addEventListener("wheel", function(ev){
    var host = document.getElementById("nbpanel-root");
    if (!host || !host.contains(ev.target)) return;
    var map = host.querySelector(".nbmap");
    if (!map) return;
    var d = Math.abs(ev.deltaY) > Math.abs(ev.deltaX) ? ev.deltaY : ev.deltaX;
    if (!d) return;
    ev.preventDefault();
    map.scrollLeft += d;
    host.setAttribute("data-follow", "manual");
  }, {capture: true, passive: false});

  // ---------------------------------------------------------------- start
  function start(){
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)
      document.body.classList.add("nbdark");
    wireTarget();
    wireFigures();
    render();
    if (window.console) console.log("[DigiChemJN] HTML edition ready — "
      + document.querySelectorAll(".nbfig").length + " figures, " + ORDER.length + " exercises");
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
