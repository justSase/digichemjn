/* The answer checks, ported from the notebook one to one: same tolerance, same
   wrong-answer diagnostics. The personal values come from NBDATA.tv, which the
   build took from the notebook's own seeded draw, so page and notebook pose the
   same question. */
(function(){
  var D = window.NBDATA, TV = D.tv;
  function TOLV(){ return window.NBTOL || D.tol || 5e-3; }
  function C(o){ return {re: o.re, im: o.im}; }
  function add(a,b){ return {re:a.re+b.re, im:a.im+b.im}; }
  function sub(a,b){ return {re:a.re-b.re, im:a.im-b.im}; }
  function mul(a,b){ return {re:a.re*b.re-a.im*b.im, im:a.re*b.im+a.im*b.re}; }
  function div(a,b){ var d=b.re*b.re+b.im*b.im;
                     return {re:(a.re*b.re+a.im*b.im)/d, im:(a.im*b.re-a.re*b.im)/d}; }
  function abs(a){ return Math.hypot(a.re, a.im); }
  function dist(a,b){ return Math.hypot(a.re-b.re, a.im-b.im); }
  function ang(a){ var t = Math.atan2(a.im, a.re); return t < 0 ? t + 2*Math.PI : t; }
  function f(x,n){ return Number(x).toFixed(n===undefined?2:n); }
  function zs(z,n){ n = n===undefined?1:n;
    return f(z.re,n) + (z.im<0?" − ":" + ") + f(Math.abs(z.im),n) + "i"; }
  function deg(r){ return r*180/Math.PI; }

  var z1 = C(TV.z1), z2 = C(TV.z2), zq = C(TV.zq), q = TV.q;
  var SUM = add(z1,z2), DIF = sub(z1,z2), PROD = mul(z1,z2);
  var QD = div({re:4,im:3}, {re:-5,im:6});
  var RQ = abs(zq), PHQ = ang(zq);
  var PHI_TRUE = ang({re:-2, im:-4});
  var QTRUE = (zq && 0) || ((z1.re>0 && z1.im>0) ? 0 : (z1.re<0 && z1.im>0) ? 1 :
                            (z1.re<0 && z1.im<0) ? 2 : 3);
  var QNAME = ["Quadrant I","Quadrant II","Quadrant III","Quadrant IV"];

  var CHECKS = {
    t1: function(v){
      var re = v[0], im = v[1], r = Math.sqrt(q);
      if (Math.abs(re) > 1e-6)
        return [false, "Both roots are purely imaginary, so the real part is 0 — you entered "
                + re + "."];
      if (Math.abs(Math.abs(im) - r) > TOLV()){
        if (Math.abs(im - Math.round(im)) < 1e-9 && Math.abs(Math.abs(im) - r) < 1.0)
          return [false, "Close — but √" + q + " is not a whole number. It is " + f(r,3)
                  + "… , so enter the decimal, not the nearest integer."];
        if (Math.abs(Math.abs(im) - q) < 1e-9)
          return [false, "You entered q itself. The imaginary part is the square <i>root</i> of q."];
        return [false, "Not yet. Take the square root of q = " + q + " and attach the i: the two "
                + "roots are ±i·√" + q + "."];
      }
      if (im <= 0) return [false, "That is the root with the negative imaginary part — "
                                + "enter the positive one."];
      return [true, "Correct: √" + q + " = " + f(r,4) + ", so the roots are ±" + f(r,4) + " i."];
    },
    t2: function(v){
      var idx = v.choice;
      if (idx === QTRUE)
        return [true, "Correct — Re(z) = " + z1.re + " and Im(z) = " + z1.im + ", so z sits in "
                + QNAME[QTRUE] + "."];
      if (idx === 4) return [false, "Neither part is zero, so z is not on an axis."];
      if ((idx === 1 || idx === 3) && (QTRUE === 1 || QTRUE === 3))
        return [false, "Right half of the plane or left? Re(z) = " + z1.re
                + " decides that, and you picked the other side."];
      return [false, "Not that one. Read off the two signs: Re(z) = " + z1.re + " and Im(z) = "
              + z1.im + ". Quadrants are counted anticlockwise from the one where both are positive."];
    },
    t3: function(v){
      var gs = {re:v[0], im:v[1]}, gd = {re:v[2], im:v[3]};
      if (dist(gs, SUM) > TOLV()){
        if (dist(gs, DIF) < TOLV())
          return [false, "You have swapped them — the first pair of boxes is the sum."];
        return [false, "The sum is not right yet: add the real parts (" + z1.re + " + " + z2.re
                + ") and the imaginary parts (" + z1.im + " + " + z2.im + ") separately."];
      }
      if (dist(gd, DIF) > TOLV())
        return [false, "The sum is right, the difference is not. Watch the sign on the imaginary "
                + "part: " + z1.im + " − (" + z2.im + ") = " + DIF.im + "."];
      return [true, "Both correct — and note that the two components never influenced one another."];
    },
    t4: function(v){
      var got = {re:v[0], im:v[1]};
      if (dist(got, PROD) < TOLV())
        return [true, "Correct: " + zs(z1) + " · " + zs(z2) + " = " + zs(PROD)
                + ". The minus in the real part is i² doing its work."];
      if (dist(got, {re: PROD.re + 2*z1.im*z2.im, im: PROD.im}) < TOLV())
        return [false, "Sign slip: you used a₁a₂ <b>+</b> b₁b₂ for the real part. It must be "
                + "a₁a₂ <b>−</b> b₁b₂, because i·i = −1."];
      if (dist(got, {re: PROD.im, im: PROD.re}) < TOLV())
        return [false, "Real and imaginary part are swapped."];
      return [false, "Not yet. Real part: a₁a₂ − b₁b₂ = " + z1.re + "·" + z2.re + " − " + z1.im
              + "·" + z2.im + ". Imaginary part: a₁b₂ + a₂b₁."];
    },
    t5: function(v){
      var got = {re:v[0], im:v[1]};
      if (dist(got, QD) < TOLV())
        return [true, "Correct: (4+3i)/(−5+6i) = −2/61 − 39/61 i = " + zs(QD,4)
                + ". The conjugate turned the denominator into the real number 61."];
      if (dist(got, div({re:-5,im:6},{re:4,im:3})) < TOLV())
        return [false, "You divided the other way round — it is z₁/z₂, not z₂/z₁."];
      if (dist(got, {re:QD.re, im:-QD.im}) < TOLV())
        return [false, "Your answer is the conjugate of the right one — check the sign in the "
                + "imaginary part of the numerator: it is a₂b₁ − a₁b₂."];
      return [false, "Not yet. Multiply top and bottom by z̄₂ = −5 − 6i. The denominator becomes "
              + "(−5)² + 6² = 61, then divide both components by 61."];
    },
    t6: function(v){
      var r = v[0], phi = ((v[1] % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
      if (Math.abs(r - RQ) > TOLV())
        return [false, "The modulus is not right: |z| = √(a² + b²) = √(" + zq.re + "² + "
                + zq.im + "²) = " + f(RQ,4) + "."];
      if (Math.abs(((phi - PHQ + Math.PI) % (2*Math.PI)) - Math.PI) < TOLV())
        return [true, "Correct: |z| = " + f(RQ,4) + " and φ = " + f(PHQ,4) + " rad = "
                + f(deg(PHQ),1) + "°."];
      if (Math.abs((((phi - PHQ) % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI) - Math.PI) < TOLV())
        return [false, "Off by exactly π — that is the trap. Re(z) = " + zq.re + " is negative, so "
                + "plain arctan(b/a) lands in the wrong half of the plane and needs + π."];
      if (Math.abs(v[1] - deg(PHQ)) < 0.5)
        return [false, "That looks like degrees. The box wants radians."];
      return [false, "The modulus is right, the angle is not. Start from arctan(b/a) = arctan("
              + zq.im + "/" + zq.re + "), then look at the sign of Re(z) to decide whether π has "
              + "to be added."];
    },
    t7: function(v){
      // the slider exercise: v comes from the figure, not from boxes
      var r2 = v.r2, p2 = v.p2;
      var R = 2.0*r2, A = 0.6 + p2;
      var z = {re: R*Math.cos(A), im: R*Math.sin(A)};
      var tgt = {re: 3.0*Math.cos(0.6 + Math.PI/2), im: 3.0*Math.sin(0.6 + Math.PI/2)};
      var d = dist(z, tgt);
      if (d < 0.25)
        return [true, "On target. You needed |z₂| = 1.50 so that 2·|z₂| = 3.0, and φ₂ = 1.57 so "
                + "that 0.60 + φ₂ reaches " + f(ang(tgt)) + " — length and angle, set independently."];
      if (Math.abs(abs(z) - abs(tgt)) > 0.25)
        return [false, "The length is off: the product has |z| = " + f(abs(z)) + ", the target sits "
                + "at " + f(abs(tgt)) + ". Remember that the moduli <i>multiply</i> — |z₁| is fixed at 2."];
      return [false, "The length is right, the direction is not: your product points at "
              + f(ang(z)) + " rad, the target at " + f(ang(tgt)) + " rad. The angles <i>add</i>, "
              + "and φ₁ is fixed at 0.60."];
    },
    t8: function(v){
      var phi = ((v[0] % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
      if (Math.abs(phi - PHI_TRUE) < TOLV())
        return [true, "Correct: φ = " + f(PHI_TRUE,4) + " rad, and that is " + f(deg(PHI_TRUE),1)
                + "°. So the script's 243.4° is right while the 2.678 rad printed next to it is "
                + "not — 2.678 rad would be " + f(deg(2.678),1) + "°."];
      if (Math.abs(phi - 2.678) < TOLV())
        return [false, "That is the value printed in the script — the one you are checking. "
                + "Convert it to degrees and compare it with the 243.4° beside it."];
      if (Math.abs((((phi - PHI_TRUE) % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI) - Math.PI) < TOLV())
        return [false, "Off by π: Re(z) = −2 is negative, so arctan(b/a) still needs the + π."];
      if (Math.abs(v[0] - 243.4) < 1.0)
        return [false, "That is the degree value — the box asks for radians."];
      return [false, "Not yet. Compute arctan(−4 / −2) = arctan(2), then add π because Re(z) < 0."];
    },
    // the second question in "Verify the script" — no task, so it only gives feedback
    axis: function(v){
      if (v.choice === 0)
        return [true, "Right. The text says “we define the x-axis as the real axis”, and figure 1.3 "
                + "on p. 33 draws it that way — figure 1.2 has its two axis names swapped."];
      if (v.choice === 1)
        return [false, "That is what figure 1.2 claims, but read the sentence just above it, and "
                + "compare with figure 1.3 on p. 33."];
      return [false, "Compare the axis labels of figure 1.2 with those of figure 1.3 — they disagree."];
    }
  };
  window.NBCHECKS = CHECKS;
})();
