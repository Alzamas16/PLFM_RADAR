#!/usr/bin/env python3
"""M2 NCO internal trace: replicate fpga_model.NCO.step() with per-clock
printing so the lut_index / quadrant decode can be read off directly."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COSIM = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                     "9_Firmware", "9_2_FPGA", "tb", "cosim"))
sys.path.insert(0, COSIM)
from fpga_model import NCO_SINE_LUT, sign_extend  # noqa: E402

FTW = 1 << 24
M32 = (1 << 32) - 1

acc, accum_reg, with_off = 0, 0, 0
idx_p, q_p = 0, 0
sin_abs, cos_abs, q_reg = 0, 0x7FFF, 0
sin_neg, cos_neg = 0, sign_extend((-0x7FFF) & 0xFFFF, 16)
sin_abs2, cos_abs2, q_reg2 = 0, 0x7FFF, 0
sin_out, cos_out = 0, 0x7FFF
vp = 0

OUT = []
def p(s=""):
    print(s)
    OUT.append(s)

p(" clk  addr  q   raw    idx  idx_used  q_reg2 |  cos_out  sin_out | ideal_cos ideal_sin  addr_eff")
for clk in range(0, 100):
    old = dict(accum_reg=accum_reg, with_off=with_off, idx=idx_p, quad=q_p,
               sin_abs=sin_abs, cos_abs=cos_abs, q_reg=q_reg,
               sin_neg=sin_neg, cos_neg=cos_neg,
               sin_abs2=sin_abs2, cos_abs2=cos_abs2, q_reg2=q_reg2,
               vp=vp)
    # stage 1
    old_accum = acc
    acc = (acc + FTW) & M32
    accum_reg = old_accum
    # stage 2
    with_off = (old["accum_reg"] + 0) & M32
    # stage 3a
    if (old["vp"] >> 1) & 1:
        la = (old["with_off"] >> 24) & 0xFF
        q = (la >> 6) & 3
        raw = la & 0x3F
        idx_used = (~raw & 63) if ((q & 1) ^ ((q >> 1) & 1)) else raw
        idx_p, q_p = idx_used, q
    # stage 3b
    if (old["vp"] >> 2) & 1:
        sin_abs = NCO_SINE_LUT[old["idx"]]
        cos_abs = NCO_SINE_LUT[63 - old["idx"]]
        q_reg = old["quad"]
    # stage 4
    if (old["vp"] >> 3) & 1:
        sin_neg = sign_extend((-old["sin_abs"]) & 0xFFFF, 16)
        cos_neg = sign_extend((-old["cos_abs"]) & 0xFFFF, 16)
        sin_abs2, cos_abs2, q_reg2 = old["sin_abs"], old["cos_abs"], old["q_reg"]
    # stage 5
    if (old["vp"] >> 4) & 1:
        q = old["q_reg2"]
        if q == 0:
            sin_out, cos_out = sign_extend(old["sin_abs2"], 16), sign_extend(old["cos_abs2"], 16)
        elif q == 1:
            sin_out, cos_out = sign_extend(old["sin_abs2"], 16), old["cos_neg"]
        elif q == 2:
            sin_out, cos_out = old["sin_neg"], old["cos_neg"]
        else:
            sin_out, cos_out = old["sin_neg"], sign_extend(old["cos_abs2"], 16)
    vp = ((old["vp"] << 1) | 1) & 0x3F
    ready = bool((old["vp"] >> 5) & 1)

    la_now = (with_off >> 24) & 0xFF
    if clk < 24 or (clk % 32 == 31) or clk in (23, 25):
        import math
        th = 2 * math.pi * la_now / 256.0
        p("%4d  %4d  %d  %4d  %4d   %4d     %4d  | %8d %8d | %9.0f %9.0f   (ready=%d)"
          % (clk, la_now, la_now >> 6, la_now & 63, idx_p, idx_p, q_reg2,
             cos_out, sin_out, 32767 * math.cos(th), 32767 * math.sin(th), ready))

with open(os.path.join(HERE, "..", "data", "m2_nco_trace.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
