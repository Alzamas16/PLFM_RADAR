function [c, raw_gain] = m1_fir_coeffs()
%M1_FIR_COEFFS  32 抽头低通系数（提取自 fir_lowpass.v 的 18-bit 有符号常数）
%
%   [c, raw_gain] = M1_FIR_COEFFS()
%
%   返回
%     c        : 归一化到直流增益 1 的系数（浮点骨架用）
%     raw_gain : 归一化前的系数和，即 RTL 中 FIR 的直流增益
%                （bb_* * raw_gain 即换算到 RTL 的 18-bit 输出码域）
%
%   原始常数表与 fpga_model.py 的 FIR_COEFFICIENTS_HEX 逐项一致。

    hex = [ ...
        0x000AD, 0x000CE, 0x3FD87, 0x002A6, 0x000E0, 0x3F8C0, 0x00A45, 0x3FD82, ...
        0x3F0B5, 0x01CAD, 0x3EE59, 0x3E821, 0x04841, 0x3B340, 0x3E299, 0x1FFFF, ...
        0x1FFFF, 0x3E299, 0x3B340, 0x04841, 0x3E821, 0x3EE59, 0x01CAD, 0x3F0B5, ...
        0x3FD82, 0x00A45, 0x3F8C0, 0x000E0, 0x002A6, 0x3FD87, 0x000CE, 0x000AD];

    c   = double(hex(:));
    neg = c >= 2^17;                 % 18-bit 二进制补码
    c(neg) = c(neg) - 2^18;

    raw_gain = sum(c);
    c = c / raw_gain;                % 归一化：直流增益 1
end
