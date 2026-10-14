#!/usr/bin/env python3
"""M2 NCO sweep: verify the LO waveform actually produced by the NCO model.
Drives the NCO with ftw = 2^32/256 so the phase walks 1 LSB of the 8-bit
LUT address per clock, then compares against an ideal cosine/sine."""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COSIM = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                     "9_Firmware", "9_2_FPGA", "tb", "cosim"))
sys.path.insert(0, COSIM)
import fpga_model as fm  # noqa: E402

FTW = 1 << 24                      # advance exactly 1/256 cycle per clock
nco = fm.NCO()
cos_out, sin_out = [], []
for k in range(400):
    s, c, rdy = nco.step(FTW, phase_offset=0, phase_valid=True)
    if rdy:
        sin_out.append(s)
        cos_out.append(c)

# align: ready lags 6 clocks, and the first valid address is 0 -> find phase 0
# by locating the cos peak (should be at address 0)
n = 256
seg = cos_out[:n + 10]
pk = max(range(len(seg)), key=lambda i: seg[i])
print("first %d cos values around peak idx=%d" % (n, pk))
cos_w = cos_out[pk:pk + n]
sin_w = sin_out[pk:pk + n]

A = 32767.0
err_c, err_s = [], []
for k in range(n):
    th = 2 * math.pi * k / 256.0
    err_c.append(cos_w[k] - A * math.cos(th))
    err_s.append(sin_w[k] - A * math.sin(th))

print("ideal-cos max|err| = %.1f LSB  (%.2f%% of FS)"
      % (max(abs(e) for e in err_c), 100 * max(abs(e) for e in err_c) / A))
print("ideal-sin max|err| = %.1f LSB  (%.2f%% of FS)"
      % (max(abs(e) for e in err_s), 100 * max(abs(e) for e in err_s) / A))
print()
print("mean(cos_w) = %.2f   mean(sin_w) = %.2f   (ideal: 0, 0)"
      % (sum(cos_w) / n, sum(sin_w) / n))
print()
print(" k  addr  cos_model  A*cos    err      sin_model  A*sin    err")
for k in list(range(0, 40)) + [48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 255]:
    th = 2 * math.pi * k / 256.0
    print("%3d  %3d  %8d  %8.0f  %8.1f   %8d  %8.0f  %8.1f" % (
        k, k, cos_w[k], A * math.cos(th), err_c[k],
        sin_w[k], A * math.sin(th), err_s[k]))

# I/Q orthogonality: cos^2+sin^2 should be constant = A^2
mag = [cos_w[k] ** 2 + sin_w[k] ** 2 for k in range(n)]
print()
print("cos^2+sin^2 : min=%.3e max=%.3e  (ideal A^2=%.3e)" %
      (min(mag), max(mag), A * A))
