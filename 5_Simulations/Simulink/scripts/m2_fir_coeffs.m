function [c, raw_gain] = m2_fir_coeffs()
%M2_FIR_COEFFS  32 raw 18-bit signed coefficients of fir_lowpass.v.
%
%   Unlike m1_fir_coeffs.m (which normalises by the DC gain and is used by
%   the floating-point M1 chain), this returns the *raw* integer
%   coefficients exactly as the fixed-point RTL/FIR uses them.
%
%   The FIR output is   fir_out = accumulator >> 17,
%   so the DC gain of the fixed filter is sum(c)/2^17 = 231944/131072
%   = 1.769592... (the filter is NOT unity-DC-gain in the fixed-point
%   domain -- the excess is absorbed by the 18->16 DDC interface rounding).
%
%   Returns a 1x32 row vector of doubles plus the raw DC gain sum(c).

hex = [ ...
    0x000AD, 0x000CE, 0x3FD87, 0x002A6, 0x000E0, 0x3F8C0, 0x00A45, 0x3FD82, ...
    0x3F0B5, 0x01CAD, 0x3EE59, 0x3E821, 0x04841, 0x3B340, 0x3E299, 0x1FFFF, ...
    0x1FFFF, 0x3E299, 0x3B340, 0x04841, 0x3E821, 0x3EE59, 0x01CAD, 0x3F0B5, ...
    0x3FD82, 0x00A45, 0x3F8C0, 0x000E0, 0x002A6, 0x3FD87, 0x000CE, 0x000AD ];

c = double(hex(:)).';
neg = c >= 2^17;
c(neg) = c(neg) - 2^18;      % 18-bit two's complement
raw_gain = sum(c);
end
