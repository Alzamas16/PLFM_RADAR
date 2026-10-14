#!/usr/bin/env python3
"""
M2 reference harness: run the *authoritative* Python fixed-point model
(fpga_model.py) on the two simplest ADC vectors and dump the results to
text, so the MATLAB port (m2_ddc_fixed.m) has an independent ground truth.

Outputs (written next to this script, in ../data/):
  ref_py_dc.csv        idx,fir_i,fir_q,cic_i,cic_q
  ref_py_sine_1mhz.csv idx,fir_i,fir_q,cic_i,cic_q
  ref_py_summary.txt   lengths + comparison against compare_*.csv
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COSIM = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                     "9_Firmware", "9_2_FPGA", "tb", "cosim"))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, COSIM)

from fpga_model import SignalChain  # noqa: E402


def load_hex(path):
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            vals.append(int(line, 16) & 0xFF)
    return vals


def load_cmp(path):
    """Load compare_*.csv -> dict of columns."""
    cols = {}
    with open(path) as f:
        hdr = f.readline().strip().split(",")
        for h in hdr:
            cols[h] = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            for h, v in zip(hdr, line.split(",")):
                cols[h].append(int(v))
    return cols


def run(name):
    adc = load_hex(os.path.join(COSIM, "adc_%s.hex" % name))
    chain = SignalChain()
    res = chain.process_adc_block(adc)

    out = os.path.join(DATA, "ref_py_%s.csv" % name)
    with open(out, "w") as f:
        f.write("idx,fir_i,fir_q,cic_i,cic_q\n")
        for k in range(len(res["fir_i_raw"])):
            f.write("%d,%d,%d,%d,%d\n" % (
                k,
                res["fir_i_raw"][k], res["fir_q_raw"][k],
                res["cic_i_raw"][k], res["cic_q_raw"][k],
            ))

    lines = []
    lines.append("scenario = %s" % name)
    lines.append("n_adc_in   = %d" % len(adc))
    lines.append("n_cic_out  = %d" % len(res["cic_i_raw"]))
    lines.append("n_fir_out  = %d" % len(res["fir_i_raw"]))
    lines.append("n_bb_out   = %d" % len(res["baseband_i"]))
    lines.append("fir_i[0:8] = %s" % str(res["fir_i_raw"][:8]))
    lines.append("fir_q[0:8] = %s" % str(res["fir_q_raw"][:8]))
    lines.append("fir_i[-4:] = %s" % str(res["fir_i_raw"][-4:]))
    if res["fir_i_raw"]:
        nz = [v for v in res["fir_i_raw"] if v != 0]
        lines.append("fir_i nonzero count = %d" % len(nz))
        lines.append("fir_i mean(last 1000) = %.4f" % (
            sum(res["fir_i_raw"][-1000:]) / min(1000, len(res["fir_i_raw"]))))

    cmp_path = os.path.join(COSIM, "compare_%s.csv" % name)
    if os.path.exists(cmp_path):
        cols = load_cmp(cmp_path)
        pv = cols["py_i"]
        lines.append("compare_%s.csv rows = %d" % (name, len(pv)))
        n = min(len(pv), len(res["fir_i_raw"]))
        d = max(abs(pv[k] - res["fir_i_raw"][k]) for k in range(n))
        lines.append("max|py_i - fir_i_raw| over first %d = %d" % (n, d))
        lines.append("py_i[0:8]  = %s" % str(pv[:8]))

    with open(os.path.join(DATA, "ref_py_summary_%s.txt" % name), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("-" * 60)


if __name__ == "__main__":
    for nm in ("dc", "sine_1mhz"):
        run(nm)
