function out = m2_ddc_fixed(adc_u8, varargin)
%M2_DDC_FIXED  Bit-accurate *fixed-point* DDC of the AERIS-10 receiver (M2).
%
%   Faithful MATLAB port of the DDC portion of
%   tb/cosim/fpga_model.py, which is the model that produced the golden
%   `py_*` columns of tb/cosim/compare_*.csv.
%
%   Chain (all widths per README section 2.2):
%
%     ADC 8-bit unsigned
%       -> Mixer  18-bit signed : adc_signed = adc*512 - 0xFF00
%       -> NCO    FTW=0x4CCCCCCD, 6-stage pipeline, 64-entry 1/4-wave LUT
%       -> Mixer  34-bit product, CIC input = product >> 16  (floor)
%       -> CIC    5 stages, R=4, M=1, 48-bit wrapping integrators,
%                 28-bit combs, >>10 (floor), saturate to 18-bit
%       -> FIR    32 taps, 36-bit accumulator, >>17 (floor), sat 18-bit
%       -> DDC interface: 18 -> 16 bit,  adc_i = ddc_i[17:2] + ddc_i[1]
%
%   TRUNCATION POLICY (M2 decision): strict RTL semantics everywhere --
%   every truncation is an arithmetic right shift (floor toward -inf, i.e.
%   Python `>>` / Verilog `>>>`), never round-half-up, and saturation is
%   applied exactly where the RTL applies it.
%
%   NOTE - the NCO quadrant decode is reproduced *bug-compatible*: the RTL
%   (nco_400m_enhanced.v:103) selects the complemented LUT index with
%       (quadrant[0] ^ quadrant[1])
%   whereas quarter-wave symmetry requires quadrant[0] alone. Quadrants 2
%   and 3 therefore have sin/cos interchanged. This is deliberate: the
%   golden data contains the defect, and M2 must match it. See
%   docs/M2_report.txt.
%
%   out = m2_ddc_fixed(adc_u8)
%   out = m2_ddc_fixed(adc_u8, 'FTW', 0x4CCCCCCD, 'PhaseOffset', 0)
%
%   adc_u8 : vector of 8-bit unsigned ADC codes (0..255)
%
%   out.fir_i/out.fir_q : 18-bit FIR raw output   == golden 'py_i'/'py_q'
%   out.cic_i/out.cic_q : 18-bit CIC output
%   out.mix_i/out.mix_q : 18-bit mixer output (== product >> 16)
%   out.bb_i /out.bb_q  : 16-bit DDC-interface output
%   out.sin  /out.cos   : 16-bit NCO outputs aligned to the mixer

p = inputParser;
p.addParameter('FTW',         double(hex2dec('4CCCCCCD')));
p.addParameter('PhaseOffset', 0);
p.parse(varargin{:});
FTW  = mod(round(p.Results.FTW), 2^32);
Poff = mod(round(p.Results.PhaseOffset), 2^16);

adc_u8 = double(adc_u8(:));
N = numel(adc_u8);

LUT = m2_nco_lut();
C   = m2_fir_coeffs();

% ---------------------------------------------------------------- state ---
nco = nco_init();
mx  = mx_init();
ci  = cic_init();   cq = cic_init();
fi  = fir_init();   fq = fir_init();
dif = dif_init();

% ------------------------------------------------------- output buffers ---
% 16384 ADC samples -> 4093 CIC outputs -> 4087 FIR outputs -> 4085 baseband
cap = ceil(N / 4) + 8;
cic_ib = zeros(cap, 1);  cic_qb = zeros(cap, 1);  n_cic = 0;
fir_ib = zeros(cap, 1);  fir_qb = zeros(cap, 1);  n_fir = 0;
bb_ib  = zeros(cap, 1);  bb_qb  = zeros(cap, 1);  n_bb  = 0;
mix_ib = zeros(N, 1);    mix_qb = zeros(N, 1);
sin_b  = zeros(N, 1);    cos_b  = zeros(N, 1);

% ============================================================ main loop ===
for n = 1:N
    % ---- NCO ------------------------------------------------------------
    [nco, s_out, c_out, ready] = nco_step(nco, FTW, Poff, true, LUT);
    sin_b(n) = s_out;  cos_b(n) = c_out;

    % ---- Mixer ----------------------------------------------------------
    [mx, mi, mq, mv] = mx_step(mx, adc_u8(n), c_out, s_out, ready, true);
    if mv, mix_ib(n) = mi;  mix_qb(n) = mq;  end

    % ---- CIC (I and Q are separate instances) ---------------------------
    [ci, coi, cvi] = cic_step(ci, mi, mv);
    [cq, coq, cvq] = cic_step(cq, mq, mv);

    if cvi && cvq
        n_cic = n_cic + 1;
        cic_ib(n_cic) = coi;  cic_qb(n_cic) = coq;

        % ---- FIR: clocked ONLY when the CIC produces a valid sample -------
        [fi, foi, fvi] = fir_step(fi, coi, C);
        [fq, foq, fvq] = fir_step(fq, coq, C);

        if fvi && fvq
            n_fir = n_fir + 1;
            fir_ib(n_fir) = foi;  fir_qb(n_fir) = foq;

            % ---- DDC input interface (18 -> 16 bit) ----------------------
            [dif, bi, bq, bv] = dif_step(dif, foi, foq, true, true);
            if bv
                n_bb = n_bb + 1;
                bb_ib(n_bb) = bi;  bb_qb(n_bb) = bq;
            end
        else
            % advance the interface pipeline with an invalid beat
            [dif, ~, ~, ~] = dif_step(dif, 0, 0, false, false);
        end
    end
end

out.fir_i = fir_ib(1:n_fir);   out.fir_q = fir_qb(1:n_fir);
out.cic_i = cic_ib(1:n_cic);   out.cic_q = cic_qb(1:n_cic);
out.bb_i  = bb_ib(1:n_bb);     out.bb_q  = bb_qb(1:n_bb);
out.mix_i = mix_ib;            out.mix_q = mix_qb;
out.sin   = sin_b;             out.cos   = cos_b;
out.n_in  = N;  out.n_cic = n_cic;  out.n_fir = n_fir;  out.n_bb = n_bb;
out.fs_in = 400e6;  out.fs_out = 100e6;
out.ftw   = FTW;    out.ftw_norm = FTW / 2^32;
end


% =====================================================================
% fixed-point helpers
% =====================================================================
function v = sgnext(x, bits)
% two's-complement reinterpretation of the low `bits` bits of x
m = 2^bits;
x = mod(x, m);                       % MATLAB mod handles negative operands
v = x - m * (x >= m / 2);
end

function y = arshift(x, s)
% arithmetic right shift == Python >> == Verilog >>> (floor toward -inf)
y = floor(x / 2^s);
end

function b = getbit(x, i)
% bit i of a non-negative integer-valued double
b = mod(floor(x / 2^i), 2);
end

function v = adc_to_signed(a)
% RTL: adc_signed = {1'b0,adc,9'b0} - {1'b0,8'hFF,9'b0}/2 = a*512 - 0xFF00
v = sgnext(a * 512 - 65280, 18);
end


% =====================================================================
% NCO -- nco_400m_enhanced.v / fpga_model.NCO  (6-stage pipeline)
% =====================================================================
function st = nco_init()
st.acc = 0; st.accum_reg = 0; st.with_off = 0;
st.idx = 0; st.quad = 0;
st.sin_abs = 0; st.cos_abs = hex2dec('7FFF'); st.quad_reg = 0;
st.sin_neg = 0; st.cos_neg = -hex2dec('7FFF');
st.sin_abs2 = 0; st.cos_abs2 = hex2dec('7FFF'); st.quad_reg2 = 0;
st.sin_out = 0; st.cos_out = hex2dec('7FFF');
st.vp = 0;
end

function [st, sin_out, cos_out, ready] = nco_step(st, ftw, poff, pvalid, LUT)
M32 = 2^32;
o = st;                                    % NBA snapshot of the old state
if pvalid
    old_accum = st.acc;
    st.acc = mod(st.acc + ftw, M32);
    st.accum_reg = old_accum;
    % Python samples old_phase_accum_reg *after* the NBA assignment above,
    % so phase_with_offset uses THIS cycle's pre-update accumulator.
    st.with_off = mod(old_accum + poff * 2^16, M32);
end

% Stage 3a: register LUT index + quadrant  (gated by vp[1])
if getbit(o.vp, 1)
    la  = mod(floor(o.with_off / 2^24), 256);
    q   = floor(la / 64);
    raw = mod(la, 64);
    if mod(getbit(q, 0) + getbit(q, 1), 2)   % RTL: quadrant_w[0] ^ quadrant_w[1]
        st.idx = 63 - raw;                   % == ~raw & 63
    else
        st.idx = raw;
    end
    st.quad = q;
end

% Stage 3b: LUT read  (gated by vp[2])
if getbit(o.vp, 2)
    st.sin_abs  = LUT(o.idx + 1);
    st.cos_abs  = LUT(63 - o.idx + 1);
    st.quad_reg = o.quad;
end

% Stage 4: pre-computed negations  (gated by vp[3])
if getbit(o.vp, 3)
    st.sin_neg  = sgnext(-o.sin_abs, 16);
    st.cos_neg  = sgnext(-o.cos_abs, 16);
    st.sin_abs2 = o.sin_abs;  st.cos_abs2 = o.cos_abs;  st.quad_reg2 = o.quad_reg;
end

% Stage 5: quadrant MUX  (gated by vp[4])
if getbit(o.vp, 4)
    switch o.quad_reg2
        case 0,    st.sin_out = sgnext(o.sin_abs2, 16); st.cos_out = sgnext(o.cos_abs2, 16);
        case 1,    st.sin_out = sgnext(o.sin_abs2, 16); st.cos_out = o.cos_neg;
        case 2,    st.sin_out = o.sin_neg;              st.cos_out = o.cos_neg;
        otherwise, st.sin_out = o.sin_neg;              st.cos_out = sgnext(o.cos_abs2, 16);
    end
end

st.vp = mod(2 * o.vp + double(pvalid), 64);
ready = logical(getbit(o.vp, 5));
sin_out = st.sin_out;
cos_out = st.cos_out;
end


% =====================================================================
% Mixer -- 3-cycle DSP48E1 pipeline (AREG/MREG/PREG)
% =====================================================================
function st = mx_init()
st.adc = 0; st.cos = 0; st.sin = 0;
st.mreg_i = 0; st.mreg_q = 0;
st.preg_i = 0; st.preg_q = 0;
st.vp = 0;
end

function [st, mi, mq, mv] = mx_step(st, adc, cos_out, sin_out, nco_ready, adc_valid)
o = st;
st.adc = adc_to_signed(adc);
st.cos = sgnext(cos_out, 16);
st.sin = sgnext(sin_out, 16);

st.mreg_i = o.adc * o.cos;
st.mreg_q = o.adc * o.sin;
st.preg_i = o.mreg_i;
st.preg_q = o.mreg_q;

v_in = double(nco_ready && adc_valid);
st.vp = mod(2 * o.vp + v_in, 8);
mv = logical(getbit(o.vp, 2));

if mv
    mi = sgnext(arshift(st.preg_i, 16), 18);
    mq = sgnext(arshift(st.preg_q, 16), 18);
else
    mi = 0;  mq = 0;
end
end


% =====================================================================
% CIC decimator -- cic_decimator_4x_enhanced.v
% =====================================================================
function st = cic_init()
st.int_s   = zeros(1, 5);     % 48-bit wrapping integrators
st.din_d   = 0;               % CREG=1 delay
st.cnt     = 0;               % decimation counter
st.dv_d    = false;
st.dv_c    = false;
st.samp    = 0;               % integrator_4 sampled, 28-bit
st.comb    = zeros(1, 5);     % 28-bit combs
st.cd      = zeros(1, 5);     % comb delay line (COMB_DELAY = 1)
st.ts      = 0;               % temp_scaled_output (comb[5] >>> 10)
st.sat_pos = false;
st.sat_neg = false;
st.tp      = 0;               % temp_output (18-bit)
st.dovp    = false;
st.dout    = 0;
st.dov     = false;
end

function [st, dout, dvalid] = cic_step(st, din, dvalid_in)
M48 = 2^48;
o = st;

din_c = mod(sgnext(din, 18), M48);

% ---- integrator chain (48-bit modular) ----
if dvalid_in
    st.din_d    = sgnext(din_c, 48);
    st.int_s(1) = mod(o.int_s(1) + o.din_d, M48);
    for i = 2:5
        st.int_s(i) = mod(o.int_s(i) + o.int_s(i-1), M48);
    end
end

% ---- decimation control ----
if dvalid_in
    if o.cnt == 3                          % DECIMATION - 1
        st.cnt  = 0;
        st.dv_d = true;
        st.samp = sgnext(st.int_s(5), 28); % NEW integrator value, 28-bit
    else
        st.cnt  = o.cnt + 1;
        st.dv_d = false;
    end
else
    st.dv_d = false;
end

st.dv_c = o.dv_d;

% ---- comb section (runs on the decimated stream) ----
if o.dv_c
    for i = 1:5
        if i == 1
            inp = o.samp;
        else
            inp = o.comb(i-1);
        end
        st.comb(i) = sgnext(inp - o.cd(i), 28);
        st.cd(i)   = inp;
    end
    st.ts      = arshift(sgnext(o.comb(5), 28), 10);   % >>10, floor
    st.sat_pos = (o.ts > 131071);
    st.sat_neg = (o.ts < -131072);
    st.tp      = sgnext(o.ts, 18);
    st.dovp    = true;
else
    st.dovp = false;
end

% ---- output MUX with saturation ----
if o.dovp
    if o.sat_pos
        st.dout = 131071;
    elseif o.sat_neg
        st.dout = -131072;
    else
        st.dout = o.tp;
    end
    st.dov = true;
else
    st.dov = false;
end

dout   = st.dout;
dvalid = st.dov;
end


% =====================================================================
% FIR -- fir_lowpass.v, 32 taps, 5-level adder tree, 6-cycle latency
% =====================================================================
function st = fir_init()
st.dl  = zeros(1, 32);
st.l0  = zeros(1, 16);
st.l1  = zeros(1, 8);
st.l2  = zeros(1, 4);
st.l3  = zeros(1, 2);
st.acc = 0;
st.dout = 0;
st.dov  = false;
st.vp   = 0;
end

function [st, dout, dvalid] = fir_step(st, din, C)
o = st;
din = sgnext(din, 18);

% stage 0: shift the delay line (only ever called with data_valid = 1)
st.dl = [din, o.dl(1:31)];
prod  = st.dl .* C;                        % combinational, exact in double

if getbit(o.vp, 0)
    st.l0 = prod(1:2:31) + prod(2:2:32);
end
if getbit(o.vp, 1)
    st.l1 = o.l0(1:2:15) + o.l0(2:2:16);
end
if getbit(o.vp, 2)
    st.l2 = o.l1(1:2:7) + o.l1(2:2:8);
end
if getbit(o.vp, 3)
    st.l3 = [o.l2(1) + o.l2(2), o.l2(3) + o.l2(4)];
end
if getbit(o.vp, 4)
    st.acc = o.l3(1) + o.l3(2);
end

if getbit(o.vp, 5)                         % output stage
    accum = o.acc;
    if accum > 2^34 - 1
        st.dout = 131071;
    elseif accum < -2^34
        st.dout = -131072;
    else
        st.dout = sgnext(arshift(accum, 17), 18);
    end
    st.dov = true;
else
    st.dov = false;
end

st.vp = mod(2 * o.vp + 1, 128);
dout   = st.dout;
dvalid = st.dov;
end


% =====================================================================
% DDC input interface -- ddc_input_interface.v  (18 -> 16 bit rounding)
% =====================================================================
function st = dif_init()
st.vi = false;  st.vq = false;  st.vs = false;
st.bi = 0;      st.bq = 0;      st.adc_valid = false;
end

function [st, bi, bq, bv] = dif_step(st, di, dq, vi, vq)
o = st;
st.vs        = st.vi && st.vq;
st.adc_valid = o.vs;
st.vi = vi;
st.vq = vq;

if o.vs
    d_i = sgnext(di, 18);
    d_q = sgnext(dq, 18);
    % adc = ddc[17:2] + ddc[1]   (round-half-up over the two dropped bits)
    ti = mod(arshift(d_i, 2), 2^16);
    ri = mod(arshift(d_i, 1), 2);
    tq = mod(arshift(d_q, 2), 2^16);
    rq = mod(arshift(d_q, 1), 2);
    st.bi = sgnext(ti + ri, 16);
    st.bq = sgnext(tq + rq, 16);
end

bi = st.bi;  bq = st.bq;  bv = st.adc_valid;
end
