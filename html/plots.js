/* The figures, re-drawn in the browser.

   The notebook renders them with matplotlib inside the kernel; here the same
   pictures are drawn on a <canvas>, with the same palette, the same fixed frames
   and the same readout line. A figure with no port here keeps the matplotlib PNG
   that the build embedded, so nothing is ever missing — it just stops moving. */
(function(){
  var PAL = {z:"#e0563f", z2:"#3f93d1", sum:"#37a06a", aux:"#b06fd0",
             warn:"#d99b2b", ghost:"#9aa4ae"};
  function ink(){ return document.body.classList.contains("nbdark") ? "#8a94a0" : "#8a94a0"; }

  function Plot(cv, o){
    o = o || {};
    var dpr = window.devicePixelRatio || 1;
    var W = o.w || 560, Hh = o.h || 560;
    cv.style.width = W + "px"; cv.style.height = Hh + "px";
    cv.width = Math.round(W*dpr); cv.height = Math.round(Hh*dpr);
    var g = cv.getContext("2d");
    g.setTransform(dpr,0,0,dpr,0,0);
    g.clearRect(0,0,W,Hh);
    var pad = o.pad || {l:46, r:14, t:14, b:40};
    var x0 = o.xlim[0], x1 = o.xlim[1], y0 = o.ylim[0], y1 = o.ylim[1];
    var iw = W - pad.l - pad.r, ih = Hh - pad.t - pad.b;
    var P = {
      g:g, W:W, H:Hh,
      X: function(x){ return pad.l + (x - x0) / (x1 - x0) * iw; },
      Y: function(y){ return pad.t + (1 - (y - y0) / (y1 - y0)) * ih; },
      box: function(){ g.save(); g.beginPath();
             g.rect(pad.l, pad.t, iw, ih); g.clip(); },
      unbox: function(){ g.restore(); },
      frame: function(){
        g.strokeStyle = ink(); g.lineWidth = 1; g.globalAlpha = .9;
        g.strokeRect(pad.l, pad.t, iw, ih); g.globalAlpha = 1;
      },
      grid: function(step, alpha){
        g.strokeStyle = ink(); g.globalAlpha = alpha === undefined ? .22 : alpha;
        g.lineWidth = .7; g.beginPath();
        for (var x = Math.ceil(x0/step)*step; x <= x1; x += step){
          g.moveTo(P.X(x), P.Y(y0)); g.lineTo(P.X(x), P.Y(y1)); }
        for (var y = Math.ceil(y0/step)*step; y <= y1; y += step){
          g.moveTo(P.X(x0), P.Y(y)); g.lineTo(P.X(x1), P.Y(y)); }
        g.stroke(); g.globalAlpha = 1;
      },
      ticks: function(step, fmt){
        g.fillStyle = ink(); g.font = "11px system-ui,sans-serif";
        g.textAlign = "center"; g.textBaseline = "top";
        for (var x = Math.ceil(x0/step)*step; x <= x1 + 1e-9; x += step){
          if (Math.abs(x) < 1e-9) continue;
          g.fillText(fmt ? fmt(x) : String(+x.toFixed(2)), P.X(x), P.Y(y0) + 6); }
        g.textAlign = "right"; g.textBaseline = "middle";
        for (var y = Math.ceil(y0/step)*step; y <= y1 + 1e-9; y += step){
          if (Math.abs(y) < 1e-9) continue;
          g.fillText(fmt ? fmt(y) : String(+y.toFixed(2)), P.X(x0) - 7, P.Y(y)); }
      },
      axes: function(){
        g.strokeStyle = ink(); g.lineWidth = 1.1; g.beginPath();
        if (y0 < 0 && y1 > 0){ g.moveTo(P.X(x0), P.Y(0)); g.lineTo(P.X(x1), P.Y(0)); }
        if (x0 < 0 && x1 > 0){ g.moveTo(P.X(0), P.Y(y0)); g.lineTo(P.X(0), P.Y(y1)); }
        g.stroke();
      },
      seg: function(ax, ay, bx, by, col, lw, dash, alpha){
        g.save(); g.strokeStyle = col; g.lineWidth = lw || 2;
        if (dash) g.setLineDash(dash);
        if (alpha !== undefined) g.globalAlpha = alpha;
        g.beginPath(); g.moveTo(P.X(ax), P.Y(ay)); g.lineTo(P.X(bx), P.Y(by));
        g.stroke(); g.restore();
      },
      dot: function(x, y, col, r){
        g.fillStyle = col; g.beginPath();
        g.arc(P.X(x), P.Y(y), r || 5, 0, 6.2832); g.fill();
      },
      cross: function(x, y, col, s){
        s = s || 7; g.strokeStyle = col; g.lineWidth = 2.4; g.beginPath();
        g.moveTo(P.X(x)-s, P.Y(y)-s); g.lineTo(P.X(x)+s, P.Y(y)+s);
        g.moveTo(P.X(x)+s, P.Y(y)-s); g.lineTo(P.X(x)-s, P.Y(y)+s); g.stroke();
      },
      ring: function(cx, cy, r, col, lw, alpha){
        g.save(); g.strokeStyle = col; g.lineWidth = lw || 1.2;
        if (alpha !== undefined) g.globalAlpha = alpha;
        g.beginPath();
        for (var i = 0; i <= 120; i++){
          var t = i/120*6.2832, X = P.X(cx + r*Math.cos(t)), Y = P.Y(cy + r*Math.sin(t));
          i ? g.lineTo(X, Y) : g.moveTo(X, Y);
        }
        g.stroke(); g.restore();
      },
      arc: function(cx, cy, r, a0, a1, col, lw){
        g.strokeStyle = col; g.lineWidth = lw || 1.6; g.beginPath();
        var n = 80;
        for (var i = 0; i <= n; i++){
          var t = a0 + (a1 - a0) * i / n;
          var X = P.X(cx + r*Math.cos(t)), Y = P.Y(cy + r*Math.sin(t));
          i ? g.lineTo(X, Y) : g.moveTo(X, Y);
        }
        g.stroke();
      },
      curve: function(fn, from, to, col, lw){
        g.save(); g.strokeStyle = col; g.lineWidth = lw || 2.4; g.beginPath();
        var n = 300;
        for (var i = 0; i <= n; i++){
          var x = from + (to - from) * i / n;
          var X = P.X(x), Y = P.Y(fn(x));
          i ? g.lineTo(X, Y) : g.moveTo(X, Y);
        }
        g.stroke(); g.restore();
      },
      text: function(x, y, s, col, size, align, alpha){
        g.save(); g.fillStyle = col || ink();
        g.font = (size || 12) + "px system-ui,sans-serif";
        g.textAlign = align || "center"; g.textBaseline = "middle";
        if (alpha !== undefined) g.globalAlpha = alpha;
        g.fillText(s, P.X(x), P.Y(y)); g.restore();
      },
      label: function(sx, sy, s, size){
        g.save(); g.fillStyle = ink(); g.font = (size || 12) + "px system-ui,sans-serif";
        g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(s, sx, sy); g.restore();
      },
      pad: pad, iw: iw, ih: ih
    };
    return P;
  }

  function argand(cv, lim, size){
    var P = Plot(cv, {w: size || 560, h: size || 560, xlim: [-lim, lim], ylim: [-lim, lim],
                      pad: {l: 40, r: 14, t: 14, b: 34}});
    P.grid(lim > 8 ? 4 : (lim > 5 ? 2 : 1));
    P.axes(); P.frame(); P.ticks(lim > 8 ? 4 : (lim > 5 ? 2 : 1));
    P.label(P.W - 40, P.Y(0) - 12, "Re", 12);
    P.label(P.X(0) + 18, 18, "Im", 12);
    return P;
  }

  // ---- readout chips, same markup as the notebook -------------------------
  function ro(pairs){
    var cells = pairs.map(function(p){
      return "<span style='display:inline-block;min-width:118px;margin:2px 6px;text-align:center'>"
           + "<span style='opacity:.75'>" + p[0] + "</span>&nbsp;<b>" + p[1] + "</b></span>";
    }).join("");
    return "<div class='nbread' style='text-align:center;font-variant-numeric:tabular-nums;"
         + "font-size:.95em;margin:4px auto 2px'>" + cells + "</div>";
  }
  function f(x, n){ return Number(x).toFixed(n === undefined ? 2 : n); }
  function zs(re, im, n){
    n = n === undefined ? 1 : n;
    var s = f(re, n) + (im < 0 ? " − " : " + ") + f(Math.abs(im), n) + "i";
    return s;
  }
  function ang(re, im){ var a = Math.atan2(im, re); return a < 0 ? a + 2*Math.PI : a; }

  var FIGS = {};

  // ---- chapter 1: the parabola that misses the axis -----------------------
  FIGS["ch1-viz"] = {
    draw: function(cv, v){
      var q = +v[0];
      var P = Plot(cv, {w: 660, h: 390, xlim: [-4, 4], ylim: [-8, 26],
                        pad: {l: 52, r: 16, t: 14, b: 40}});
      P.grid(2); P.axes(); P.frame(); P.ticks(2);
      P.box();
      P.curve(function(x){ return x*x + q; }, -4, 4, PAL.z2, 2.4);
      P.unbox();
      if (q < 0){ var r = Math.sqrt(-q); P.dot(-r, 0, PAL.sum, 6); P.dot(r, 0, PAL.sum, 6); }
      else if (q <= 26) { P.dot(0, q, PAL.warn, 6); }
      P.label(P.W/2, P.H - 12, "x", 12);
    },
    read: function(v){
      var q = +v[0];
      if (q < 0){ var r = Math.sqrt(-q);
        return ro([["q", f(q,1)], ["real roots", "2"], ["x", "±" + f(r,3)],
                   ["lowest point", f(q,1)]]); }
      return ro([["q", f(q,1)], ["real roots", "0"], ["x", "none on this line"],
                 ["lowest point", f(q,1)]]);
    }
  };

  // ---- chapter 2: the plane ----------------------------------------------
  FIGS["ch2-viz"] = {
    draw: function(cv, v){
      var a = +v[0], b = +v[1];
      var P = argand(cv, 6);
      var r = Math.hypot(a, b), phi = Math.atan2(b, a);
      if (r > 1e-9){
        P.arc(0, 0, 0.9, 0, phi, PAL.aux, 1.6);
        P.text(1.3*Math.cos(phi/2), 1.3*Math.sin(phi/2), "φ", PAL.aux, 13);
      }
      P.seg(a, 0, a, b, PAL.ghost, 1.4, [2,3]);
      P.seg(0, b, a, b, PAL.ghost, 1.4, [2,3]);
      P.seg(0, 0, a, b, PAL.z, 2.6);
      P.dot(a, b, PAL.z, 6);
      var q = [["I",4.8,4.8],["II",-4.8,4.8],["III",-4.8,-4.8],["IV",4.8,-4.8]];
      q.forEach(function(t){ P.text(t[1], t[2], "(" + t[0] + ")", null, 11, "center", .6); });
    },
    read: function(v){
      var a = +v[0], b = +v[1], r = Math.hypot(a, b), phi = ang(a, b);
      var quad = (Math.abs(a) < 1e-9 || Math.abs(b) < 1e-9) ? 0 :
                 (a > 0 && b > 0) ? 1 : (a < 0 && b > 0) ? 2 : (a < 0 && b < 0) ? 3 : 4;
      return ro([["z", zs(a, b, 1)], ["|z|", f(r,3)], ["φ", f(phi,3) + " rad"],
                 ["", f(phi*180/Math.PI,1) + "°"],
                 ["quadrant", quad ? String(quad) : "on an axis"]]);
    }
  };

  // ---- chapter 3: adding is closing a parallelogram ------------------------
  FIGS["ch3-viz"] = {
    draw: function(cv, v){
      var a1 = +v[0], b1 = +v[1], a2 = +v[2], b2 = +v[3];
      var plus = (v[4] || "").indexOf("+") >= 0 || v[4] === undefined;
      var zr = plus ? a1 + a2 : a1 - a2, zi = plus ? b1 + b2 : b1 - b2;
      var P = argand(cv, 13, 580);
      P.seg(0, 0, a1, b1, PAL.z, 2.4); P.dot(a1, b1, PAL.z, 5);
      if (plus){
        P.seg(0, 0, a2, b2, PAL.z2, 2.4); P.dot(a2, b2, PAL.z2, 5);
        P.seg(a1, b1, zr, zi, PAL.z2, 1.6, [6,4], .85);
        P.seg(a2, b2, zr, zi, PAL.z, 1.6, [6,4], .85);
      } else {
        P.seg(0, 0, -a2, -b2, PAL.z2, 2.4, [6,4]); P.dot(-a2, -b2, PAL.z2, 5);
        P.seg(a1, b1, zr, zi, PAL.z2, 1.6, [6,4], .85);
      }
      P.seg(0, 0, zr, zi, PAL.sum, 3.0); P.dot(zr, zi, PAL.sum, 6);
    },
    read: function(v){
      var a1 = +v[0], b1 = +v[1], a2 = +v[2], b2 = +v[3];
      var plus = (v[4] || "").indexOf("+") >= 0 || v[4] === undefined;
      var zr = plus ? a1 + a2 : a1 - a2, zi = plus ? b1 + b2 : b1 - b2;
      var sg = plus ? "+" : "−";
      return ro([["z₁", zs(a1,b1,1)], ["z₂", zs(a2,b2,1)],
                 [plus ? "z₁ + z₂" : "z₁ − z₂", zs(zr,zi,1)]])
           + ro([["real", f(a1,1) + " " + sg + " " + f(a2,1) + " = " + f(zr,1)],
                 ["imag", f(b1,1) + " " + sg + " " + f(b2,1) + " = " + f(zi,1)]]);
    }
  };

  // ---- chapter 4: the conjugate mirrors across the real axis ---------------
  FIGS["ch4-viz2"] = {
    draw: function(cv, v){
      var a = +v[0], b = +v[1];
      var P = argand(cv, 6, 540);
      P.seg(0, 0, a, b, PAL.z, 2.6); P.dot(a, b, PAL.z, 6);
      P.seg(0, 0, a, -b, PAL.z2, 2.6, [6,4]); P.dot(a, -b, PAL.z2, 6);
      P.seg(a, b, a, -b, PAL.ghost, 1.2, [2,3]);
    },
    read: function(v){
      var a = +v[0], b = +v[1], r = Math.hypot(a, b);
      return ro([["z", zs(a,b,1)], ["z̄", zs(a,-b,1)], ["z·z̄", f(r*r,2)], ["|z|", f(r,3)]]);
    }
  };

  // ---- chapter 5: moduli multiply, the quotient lives on its own frame -----
  FIGS["ch5-viz"] = {
    draw: function(cv, v){
      var a1 = +v[0], b1 = +v[1], a2 = +v[2], b2 = +v[3];
      var dpr = window.devicePixelRatio || 1;
      cv.style.width = "940px"; cv.style.height = "490px";
      cv.width = 940*dpr; cv.height = 490*dpr;
      var g = cv.getContext("2d"); g.setTransform(dpr,0,0,dpr,0,0); g.clearRect(0,0,940,490);
      var left  = document.createElement("canvas"), right = document.createElement("canvas");
      var PL = Plot(left,  {w: 460, h: 470, xlim: [-10,10], ylim: [-10,10],
                            pad:{l:38,r:12,t:12,b:30}});
      PL.grid(4); PL.axes(); PL.frame(); PL.ticks(4);
      [[a1,b1,PAL.z],[a2,b2,PAL.z2]].forEach(function(t){
        var r = Math.hypot(t[0], t[1]);
        PL.ring(0, 0, r, t[2], 1.1, .45);
        PL.seg(0, 0, t[0], t[1], t[2], 2.5); PL.dot(t[0], t[1], t[2], 5);
      });
      var PR = Plot(right, {w: 460, h: 470, xlim: [-4,4], ylim: [-4,4],
                            pad:{l:38,r:12,t:12,b:30}});
      PR.grid(2); PR.axes(); PR.frame(); PR.ticks(2);
      var d = a2*a2 + b2*b2;
      if (d > 1e-12){
        var qr = (a1*a2 + b1*b2)/d, qi = (b1*a2 - a1*b2)/d;
        if (Math.abs(qr) <= 4 && Math.abs(qi) <= 4){
          PR.seg(0,0,qr,qi,PAL.sum,2.8); PR.dot(qr,qi,PAL.sum,6);
        } else {
          var m = Math.hypot(qr,qi), ur = qr/m*3.8, ui = qi/m*3.8;
          PR.seg(0,0,ur,ui,PAL.warn,2.4,[6,4]);
          PR.text(ur*.55, ui*.55, "off frame", PAL.warn, 10);
        }
      }
      g.drawImage(left, 0, 10, 460, 470);
      g.drawImage(right, 475, 10, 460, 470);
      g.fillStyle = ink(); g.font = "12px system-ui,sans-serif"; g.textAlign = "center";
      g.fillText("z₁ and z₂ on their moduli circles", 230, 488);
      g.fillText("the quotient z₁/z₂", 705, 488);
    },
    read: function(v){
      var a1=+v[0], b1=+v[1], a2=+v[2], b2=+v[3];
      var r1 = Math.hypot(a1,b1), r2 = Math.hypot(a2,b2);
      if (r2 < 1e-12)
        return ro([["|z₁|", f(r1,3)], ["|z₂|", "0"], ["z₁/z₂", "undefined — z₂ is zero"]]);
      var d = a2*a2 + b2*b2, qr = (a1*a2 + b1*b2)/d, qi = (b1*a2 - a1*b2)/d;
      return ro([["|z₁|", f(r1,3)], ["|z₂|", f(r2,3)], ["z₁/z₂", zs(qr,qi,3)]])
           + ro([["|z₁|/|z₂|", f(r1/r2,4)], ["|z₁/z₂|", f(Math.hypot(qr,qi),4)],
                 ["", "identical, always"]]);
    }
  };

  // ---- chapter 6: the arctan trap -----------------------------------------
  FIGS["ch6-viz2"] = {
    draw: function(cv, v){
      var a = +v[0], b = +v[1];
      var P = argand(cv, 6, 560);
      var naive = Math.abs(a) > 1e-12 ? Math.atan(b/a) : Math.sign(b)*Math.PI/2;
      var r = Math.max(Math.hypot(a,b), 1e-9);
      P.seg(0, 0, r*Math.cos(naive), r*Math.sin(naive), PAL.warn, 2.4, [6,4]);
      P.seg(0, 0, a, b, PAL.z, 2.8); P.dot(a, b, PAL.z, 6);
    },
    read: function(v){
      var a = +v[0], b = +v[1];
      var naive = Math.abs(a) > 1e-12 ? Math.atan(b/a) : Math.sign(b)*Math.PI/2;
      var truth = ang(a, b);
      var same = Math.abs(((naive - truth + Math.PI) % (2*Math.PI)) - Math.PI) < 1e-9;
      var verdict = same ? "<span class='nbok'>arctan is correct here (a &gt; 0)</span>"
                         : "<span class='nbwarn'>arctan lands in the wrong half — add π</span>";
      return ro([["z", zs(a,b,1)], ["arctan(b/a)", f(naive,3) + " rad"],
                 ["true φ", f(truth,3) + " rad"], ["", f(truth*180/Math.PI,1) + "°"]])
           + "<div style='text-align:center;font-weight:700;margin-top:2px'>" + verdict + "</div>";
    }
  };

  // ---- chapter 7: lengths multiply, angles add ----------------------------
  FIGS["ch7-viz"] = {
    draw: function(cv, v){
      var r1 = +v[0], p1 = +v[1], r2 = +v[2], p2 = +v[3];
      var prod = (v[4] || "·").indexOf("·") >= 0;
      var z1r = r1*Math.cos(p1), z1i = r1*Math.sin(p1);
      var z2r = r2*Math.cos(p2), z2i = r2*Math.sin(p2);
      var R = prod ? r1*r2 : r1/r2, A = prod ? p1 + p2 : p1 - p2;
      var zr = R*Math.cos(A), zi = R*Math.sin(A);
      var P = argand(cv, 6.5, 590);
      [[z1r,z1i,PAL.z,2.5],[z2r,z2i,PAL.z2,2.5],[zr,zi,PAL.sum,3.2]].forEach(function(t){
        P.seg(0,0,t[0],t[1],t[2],t[3]); P.dot(t[0],t[1],t[2],5);
      });
      P.arc(0, 0, 0.55*Math.min(r1, R), Math.atan2(z1i,z1r), Math.atan2(zi,zr), PAL.aux, 2.0);
    },
    read: function(v){
      var r1=+v[0], p1=+v[1], r2=+v[2], p2=+v[3];
      var prod = (v[4] || "·").indexOf("·") >= 0;
      var R = prod ? r1*r2 : r1/r2, A = prod ? p1 + p2 : p1 - p2;
      var a1 = ((p1 % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
      var a2 = ((p2 % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
      var ar = ((A % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
      return ro([["|z₁|", f(r1)], ["φ₁", f(a1)], ["|z₂|", f(r2)], ["φ₂", f(a2)]])
           + ro([["moduli", f(r1) + (prod ? " × " : " ÷ ") + f(r2) + " = " + f(R)],
                 ["angles", f(a1) + (prod ? " + " : " − ") + f(a2) + " = " + f(ar)]])
           + ro([["result", zs(R*Math.cos(A), R*Math.sin(A), 3)]]);
    }
  };

  // ---- chapter 7 exercise: steer the product onto the target --------------
  var TZ1 = {r: 2.0, p: 0.6};
  var TGT = {r: 3.0, p: 0.6 + Math.PI/2}, TTOL = 0.25;
  FIGS["ch7-target"] = {
    draw: function(cv, v){
      var r2 = +v[0], p2 = +v[1];
      var P = argand(cv, 6.5, 560);
      var tx = TGT.r*Math.cos(TGT.p), ty = TGT.r*Math.sin(TGT.p);
      P.ring(tx, ty, TTOL, PAL.warn, 2.0);
      P.cross(tx, ty, PAL.warn, 7);
      var z1r = TZ1.r*Math.cos(TZ1.p), z1i = TZ1.r*Math.sin(TZ1.p);
      var z2r = r2*Math.cos(p2), z2i = r2*Math.sin(p2);
      var R = TZ1.r*r2, A = TZ1.p + p2;
      [[z1r,z1i,PAL.z,2.4],[z2r,z2i,PAL.z2,2.4],
       [R*Math.cos(A), R*Math.sin(A), PAL.sum,3.2]].forEach(function(t){
        P.seg(0,0,t[0],t[1],t[2],t[3]); P.dot(t[0],t[1],t[2],5);
      });
    },
    read: function(v){
      var r2 = +v[0], p2 = +v[1];
      var R = TZ1.r*r2, A = TZ1.p + p2;
      var zr = R*Math.cos(A), zi = R*Math.sin(A);
      var tx = TGT.r*Math.cos(TGT.p), ty = TGT.r*Math.sin(TGT.p);
      var d = Math.hypot(zr - tx, zi - ty);
      var state = d < TTOL ? "<span class='nbok'>on target</span>"
                           : "<span class='nbwarn'>distance to target: " + f(d) + "</span>";
      var a2 = ((p2 % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
      return ro([["|z₁|·|z₂|", "2.00 × " + f(r2) + " = " + f(R)],
                 ["φ₁+φ₂", "0.60 + " + f(a2) + " = " + f(((A%(2*Math.PI))+2*Math.PI)%(2*Math.PI))],
                 ["product", zs(zr, zi, 2)]])
           + "<div style='text-align:center;font-weight:700;margin-top:2px'>" + state + "</div>";
    }
  };

  // ---- the two step-through figures keep their rendered frames ------------
  FIGS["ch4-viz"]  = {frames: "_ipow_frames",  labels: "_ipow_labels"};
  FIGS["ch6-viz"]  = {frames: "_euler_frames", labels: "_euler_labels"};

  window.NBFIGS = FIGS;
  window.NBPLOT = {Plot: Plot, argand: argand, ro: ro, PAL: PAL};
})();
