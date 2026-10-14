#!/usr/bin/env python3
"""
M2 LO probe.

Hypothesis: the ~20 LSB DC offset in the golden outputs is NOT a truncation
artefact, but comes from the NCO quadrant decoding in nco_400m_enhanced.v:103

    wire [5:0] lut_index =
        (quadrant_w[0] ^ quadrant_w[1]) ? ~lut_address[5:0] : lut_address[5:0];

Per the quarter-wave symmetry the selector must be quadrant[0] alone
(63-r for q in {1,3}); using quadrant[0]^quadrant[1] instead selects 63-r
for q in {1,2}, which swaps sin/cos in quadrants 2 and 3 and makes the
complex LO waveform non-zero-mean.

Test: sweep the LO over one full cycle and check against an ideal cosine;
then re-run the whole DDC with an ideal LO substituted and compare the
output DC and the golden deviation.
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


def load_hex(path):
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            vals.append(int(line, 16) & 0xFF)
    return vals


# --------------------------------------------------------------------------
# 1. Sweep the real NCO over one full cycle
# --------------------------------------------------------------------------
p("=" * 72)
p("1) NCO waveform sweep (ftw = 2^24 -> walks 1 LUT address per clock)")
p("=" * 72)

FTW = 1 << 24
nco = fm.NCO()
raw = []
for k in range(1200):
    s, c, rdy = nco.step(FTW, phase_offset=0, phase_valid=True)
    if rdy:
        raw.append((c, s))

# locate address 0: max |cos| with cos>0
best, bi = -1e9, 0
for i in range(len(raw) - 300):
    if raw[i][0] > best and abs(raw[i][1]) < 400:
        best, bi = raw[i][0], i
p("found address-0 at raw index %d (cos=%d sin=%d)" % (bi, raw[bi][0], raw[bi][1]))

cos_w = [raw[bi + k][0] for k in range(256)]
sin_w = [raw[bi + k][1] for k in range(256)]

err_c = [cos_w[k] - A * math.cos(2 * math.pi * k / 256.0) for k in range(256)]
err_s = [sin_w[k] - A * math.sin(2 * math.pi * k / 256.0) for k in range(256)]
p("max |cos_model - A*cos| = %7.1f LSB  (%.2f%% FS)"
  % (max(abs(e) for e in err_c), 100 * max(abs(e) for e in err_c) / A))
p("max |sin_model - A*sin| = %7.1f LSB  (%.2f%% FS)"
  % (max(abs(e) for e in err_s), 100 * max(abs(e) for e in err_s) / A))
p("")
p("DC of LO over one cycle:  mean(cos)=%8.2f   mean(sin)=%8.2f   (ideal 0,0)"
  % (sum(cos_w) / 256.0, sum(sin_w) / 256.0))
mag = [cos_w[k] ** 2 + sin_w[k] ** 2 for k in range(256)]
p("|LO|^2 : min=%.3e max=%.3e  ideal A^2=%.3e   (spread %.2f%%)"
  % (min(mag), max(mag), A * A, 100 * (max(mag) - min(mag)) / (A * A)))
p("")
p(" k  quadrant  cos_model    A*cos     err    sin_model    A*sin     err")
for k in [0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176,
          192, 208, 224, 240, 255]:
    th = 2 * math.pi * k / 256.0
    p("%3d     %d      %8d  %8.0f %7.0f   %8d  %8.0f %7.0f" % (
        k, k >> 6, cos_w[k], A * math.cos(th), err_c[k],
        sin_w[k], A * math.sin(th), err_s[k]))

# --------------------------------------------------------------------------
# 2. Control experiment: ideal LO, everything else untouched
# --------------------------------------------------------------------------
p("")
p("=" * 72)
p("2) Control: same fixed-point DDC but with an IDEAL complex LO")
p("=" * 72)


class IdealNCO(fm.NCO):
    """Same pipeline/valid behaviour, but an ideal (mathematically exact) LO."""

    def __init__(self, ftw):
        super().__init__()
        self._ftw = ftw & 0xFFFFFFFF
        self._k = 0

    def step(self, ftw, phase_offset=0, phase_valid=True):
        _, _, rdy = super().step(ftw, phase_offset, phase_valid)
        # the LO sample consumed by the mixer for adc[k] is the NCO output
        # produced 4 clocks earlier; keep the identical alignment.
        ph = (self._k - 4) * self._ftw
        th = 2 * math.pi * ((ph % (1 << 32)) / float(1 << 32))
        self._k += 1
        return (int(round(A * math.sin(th))), int(round(A * math.cos(th))), rdy)


def run_chain(adc, nco_obj):
    chain = fm.SignalChain()
    chain.nco = nco_obj
    fir_i, cic_i = [], []
    cur = fm.NCO()  # placeholder
    for s in adc:
        r = chain.ddc_step(s)
        if r["cic_valid"]:
            cic_i.append(r["cic_i"])
            fo, fv = chain.fir_i.step(r["cic_i"], True)
            chain.fir_q.step(r["cic_q"], True)
            if fv:
                fir_i.append(fo)
            else:
                chain.ddc_interface.step(0, 0, False, False)
        chain.nco = cur  # keep object identity stable for the real NCO case
    return fir_i, cic_i


def run_chain2(adc, make_nco):
    """Feed a chosen NCO implementation through the standard DDC path."""
    chain = fm.SignalChain()
    if make_nco is not None:
        chain.nco = make_nco()
    ftw = fm.SignalChain.FTW_120MHZ
    fir_i, fir_q, cic_i = [], [], []
    for s in adc:
        r = chain.ddc_step(s, ftw)
        if r["cic_valid"]:
            cic_i.append(r["cic_i"])
            fo, fv = chain.fir_i.step(r["cic_i"], True)
            fq, _ = chain.fir_q.step(r["cic_q"], True)
            if fv:
                fir_i.append(fo)
                fir_q.append(fq)
            else:
                chain.ddc_interface.step(0, 0, False, False)
    return fir_i, fir_q, cic_i


adc = load_hex(os.path.join(COSIM, "adc_dc.hex"))

real_i, _, real_cic = run_chain2(adc, None)
ideal_i, _, ideal_cic = run_chain2(adc, lambda: IdealNCO(fm.SignalChain.FTW_120MHZ))

p("scenario: adc_dc.hex (constant 0x80, 16384 samples)")
p("  real  NCO : n_fir=%d  mean(fir_i[last1000])=%8.4f  mean(cic_i[last1000])=%8.4f"
  % (len(real_i), sum(real_i[-1000:]) / 1000.0, sum(real_cic[-1000:]) / 1000.0))
p("  ideal NCO : n_fir=%d  mean(fir_i[last1000])=%8.4f  mean(cic_i[last1000])=%8.4f"
  % (len(ideal_i), sum(ideal_i[-1000:]) / 1000.0, sum(ideal_cic[-1000:]) / 1000.0))

# --------------------------------------------------------------------------
# 3. Does the ideal LO still reproduce the golden?
# --------------------------------------------------------------------------
cmp_path = os.path.join(COSIM, "compare_dc.csv")
cols = {}
with open(cmp_path) as f:
    hdr = f.readline().strip().split(",")
    for h in hdr:
        cols[h] = []
    for line in f:
        line = line.strip()
        if line:
            for h, v in zip(hdr, line.split(",")):
                cols[h].append(int(v))
py = cols["py_i"]
n = min(len(py), len(real_i), len(ideal_i))
d_real = max(abs(py[k] - real_i[k]) for k in range(n))
d_ideal = max(abs(py[k] - ideal_i[k]) for k in range(n))
p("")
p("  max|golden py_i - real-NCO model|  = %d LSB   <-- must be 0" % d_real)
p("  max|golden py_i - ideal-NCO model| = %d LSB   <-- should be LARGE" % d_ideal)

with open(os.path.join(HERE, "..", "data", "m2_lo_probe.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
