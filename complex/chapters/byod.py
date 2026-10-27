_txt = (
  "Here is why a biophysicist cares. To a first approximation, a patch of cell membrane behaves like "
  "a resistor and a capacitor in parallel. Ions leak through channels (the resistance "
  + imath("R_m") + "), and the lipid bilayer stores charge (the capacitance " + imath("C_m") + "). "
  "Hodgkin and Huxley built their description of the axon on exactly this circuit" + cite(5) + ". "
  "The specific membrane capacitance (capacitance per area) has since been measured directly; it is close to "
  + imath(r"1\;\mu F/cm^2") + cite(6) + ".<br><br>"
  "Drive such a membrane with a sinusoidal current of angular frequency " + imath("\\omega") + ", and "
  "the voltage response lags behind the current. Describing this with two real numbers, an amplitude "
  "and a phase shift, is awkward. With <b>one complex number</b>, the impedance Z, it is easy:"
  "<div style='text-align:center;margin:10px 0'>" + dmath(r"$Z(\omega) = \frac{R_m}{1 + i\,\omega R_m C_m}$")
  + "</div>"
  "The modulus " + imath("|Z|") + " is the amplitude ratio, and the argument " + imath("\\arg Z") + " is "
  "the phase shift. One object carries both. Every rule from this notebook now does real "
  "work: the conjugate trick splits Z into real and imaginary parts, the modulus gives the amplitude, "
  "and the quadrant-aware angle gives the phase.<br><br>"
  "<b>The values below are simulated.</b> They lie in a physiologically plausible range for a small "
  "cell, but they are not measurements. Replace <b>R_m</b> and <b>C_m</b> with your own values and run again.")

_code = '''# --- membrane impedance of an RC patch --------------------------------
# SIMULATED values in a plausible range for a small cell — replace with yours.
R_m = 500e6      # membrane resistance  [ohm]      (500 MOhm)
C_m = 30e-12     # membrane capacitance [farad]    (30 pF)

f = np.logspace(-1, 4, 300)          # 0.1 Hz ... 10 kHz
w = 2*np.pi*f
Z = R_m / (1 + 1j*w*R_m*C_m)         # ONE complex number per frequency

f_c = 1.0/(2*np.pi*R_m*C_m)          # corner frequency
print("corner frequency f_c = %.2f Hz" % f_c)
print("at f_c:  |Z| = %.3e ohm,  phase = %.1f deg"
      % (np.interp(f_c, f, np.abs(Z)),
         np.degrees(np.interp(f_c, f, np.angle(Z)))))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.2))
theme_axes(ax1); theme_axes(ax2)

ax1.loglog(f, np.abs(Z), color=PAL["z"], lw=2.2)
ax1.axvline(f_c, color=PAL["warn"], ls="--", lw=1.4)
ax1.set_xlabel("frequency [Hz]"); ax1.set_ylabel("|Z|  [ohm]")
ax1.set_title("amplitude = modulus", fontsize=10)

ax2.semilogx(f, np.degrees(np.angle(Z)), color=PAL["z2"], lw=2.2)
ax2.axvline(f_c, color=PAL["warn"], ls="--", lw=1.4)
ax2.axhline(-45, color=PLOT_INK, ls=":", lw=1.2)
ax2.set_xlabel("frequency [Hz]"); ax2.set_ylabel("arg Z  [deg]")
ax2.set_title("phase shift = argument", fontsize=10)
fig.tight_layout()
'''

build_chapter(None, "Bring your own data: membrane impedance", icon="🧪", chapter_open=False,
  anchor="byod", info=note_box(_txt),
  body=[editable_runner(_code, run_label="Run ▶", height="430px"),
        note_box("<b>Things to try.</b> At low frequency the capacitor is effectively an open circuit, "
                 "so " + imath("|Z|\\to R_m") + " with almost no phase shift: the membrane looks "
                 "purely resistive. At high frequency the capacitor shorts out the resistance. "
                 + imath("|Z|") + " falls off and the phase approaches −90°; the response is now "
                 "almost purely capacitive. At the corner frequency "
                 + imath("f_c=1/(2\\pi R_mC_m)") + " the phase passes exactly −45°. This is the "
                 "dotted line in the right-hand plot. Change " + imath("C_m") + " by a factor of ten "
                 "and watch the whole picture shift by a decade. This is why membrane capacitance "
                 "is worth measuring carefully" + cite(6) + "."),
        completion_button("b1", "I have run this with my own values")], task="b1")
