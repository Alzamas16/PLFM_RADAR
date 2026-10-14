#!/usr/bin/env python3
"""M2 NCO waveform check with the correct 256-sample window.

Established by m2_nco_trace.py: the first dds_ready output corresponds to
lut address 1, and subsequent outputs advance the address by 1.  So the
first 256 ready outputs cover addresses 1..255,0 -- exactly one full cycle.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COSIM = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                     "9_Firmware", "9_2_FPGA", "tb", "cosim"))
sys.path.insert(0, COSIM)
import fpga_model as fm  # noqa: E402

A = 32767.0
OUT = []
def p(s=""):
    print(s)
    OUT.append(s)

nco = fm.NCO()
raw = []
for k in range(400):
    s, c, rdy = nco.step(1 << 24, phase_offset=0, phase_valid=True)
    if rdy:
        raw.append((c, s))

win = raw[0:256]                       # addr = 1,2,...,255,0
p("window: 256 consecutive ready outputs (addr 1..255,0)")
p("  mean(cos) = %8.3f    mean(sin) = %8.3f     (ideal 0, 0)"
  % (sum(v[0] for v in win) / 256.0, sum(v[1] for v in win) / 256.0))

# per-quadrant view: addr = i+1 mod 256
p("")
p(" q    r  |  cos_model  sin_model  |  ideal_cos ideal_sin |  |LO|   ang_model ang_ideal")
tab = {}
for i, (c, s) in enumerate(win):
    addr = (i + 1) & 0xFF
    tab[(addr >> 6, addr & 63)] = (c, s)

resid = []
for q in range(4):
    for r in range(0, 64, 8):
        c, s = tab[(q, r)]
        addr = q * 64 + r
        th = 2 * math.pi * addr / 256.0
        ic, isx = A * math.cos(th), A * math.sin(th)
        ang_m = math.degrees(math.atan2(s, c)) % 360
        ang_i = math.degrees(math.atan2(isx, ic)) % 360
        p("%2d  %3d  | %9d %9d  | %9.0f %9.0f  | %7.1f  %7.2f  %7.2f"
          % (q, r, c, s, ic, isx, math.hypot(c, s), ang_m, ang_i))
        resid.append(math.hypot(c - ic, s - isx))

# RMS of the complex error vs an ideal LO, after removing the mean
mc = sum(v[0] for v in win) / 256.0
ms = sum(v[1] for v in win) / 256.0
ac = [v[0] - mc for v in win]
asx = [v[1] - ms for v in win]
p("")
p("LO DC (mean)          = (%.2f, %.2f)  -> |DC| = %.2f LSB = %.4f%% FS"
  % (mc, ms, math.hypot(mc, ms), 100 * math.hypot(mc, ms) / A))
p("LO RMS after DC removal = %.1f LSB  (ideal %.1f)" %
  (math.sqrt(sum(v * v for v in ac + asx) / (2 * 256.0)), A / math.sqrt(2)))

# what DC does that predict at the mixer output for the DC scenario?
# mix = floor(adc_signed * cos / 65536) = floor(256*cos/65536) = floor(cos/256)
import statistics
adc_signed = 256
mix_mean = sum(math.floor(adc_signed * tab[(q, r)][0] / 65536.0)
               for q in range(4) for r in range(64)) / 256.0
p("predicted mixer-output DC for DC input = floor(256*cos/2^16) mean = %.3f"
  % mix_mean)

with open(os.path.join(HERE, "..", "data", "m2_nco_waveform.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
