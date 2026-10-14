#!/usr/bin/env python3
"""M2 probe: dump per-stage values of the Python DDC for a few ADC inputs,
to locate the origin of the ~20 LSB DC offset seen in the golden outputs."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COSIM = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                     "9_Firmware", "9_2_FPGA", "tb", "cosim"))
sys.path.insert(0, COSIM)

import fpga_model as fm  # noqa: E402


def load_hex(path):
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            vals.append(int(line, 16) & 0xFF)
    return vals


adc = load_hex(os.path.join(COSIM, "adc_dc.hex"))
print("adc_dc.hex : first 8 =", adc[:8], " unique =", sorted(set(adc))[:6])
print("adc_to_signed(128) =", fm.Mixer.adc_to_signed(128))
print("adc_to_signed(first) =", fm.Mixer.adc_to_signed(adc[0]))
print()

chain = fm.SignalChain()
mix_i, mix_q, cic_i, cic_q, fir_i, fir_q = [], [], [], [], [], []
nco_ready_at = []
for k, s in enumerate(adc):
    r = chain.ddc_step(s)
    mix_i.append(r["mix_i"])
    mix_q.append(r["mix_q"])
    if r["cic_valid"]:
        cic_i.append(r["cic_i"])
        cic_q.append(r["cic_q"])
        fo_i, fv_i = chain.fir_i.step(r["cic_i"], True)
        fo_q, fv_q = chain.fir_q.step(r["cic_q"], True)
        if fv_i and fv_q:
            fir_i.append(fo_i)
            fir_q.append(fo_q)
            chain.ddc_interface.step(fo_i, fo_q, True, True)
        else:
            chain.ddc_interface.step(0, 0, False, False)


def mean(v, a, b):
    return sum(v[a:b]) / max(1, (b - a))


def stats(name, v):
    n = len(v)
    print("%-6s n=%5d  head=%s" % (name, n, v[:8]))
    print("        mean[200:1000]=%9.4f  mean[last1000]=%9.4f  min=%d max=%d"
          % (mean(v, 200, 1000), mean(v, n - 1000, n), min(v), max(v)))


stats("mix_i", mix_i)
stats("cic_i", cic_i)
stats("fir_i", fir_i)
print()
print("mix_i[2000:2016] =", mix_i[2000:2016])
print("cic_i[500:516]   =", cic_i[500:516])
print("fir_i[500:516]   =", fir_i[500:516])
print()
# where does the DC come from?  FIR DC gain = sum(coeff)/2^17
s = sum(fm.FIR_COEFFICIENTS)
print("sum(FIR coeff) = %d  -> FIR DC gain = %.6f" % (s, s / 2 ** 17))
print("implied CIC-output DC = %.4f" % (mean(fir_i, len(fir_i) - 1000, len(fir_i))
                                       / (s / 2 ** 17)))
