function out = m1_ddc_float(adc_u8, varargin)
%M1_DDC_FLOAT  浮点版接收机 DDC 前端骨架（M1 阶段）。
%
%   对应 RTL 链：  nco_400m_enhanced.v -> ddc_400m.v(mixer)
%                 -> cic_decimator_4x_enhanced.v -> fir_lowpass.v
%                 -> ddc_input_interface.v
%
%   out = M1_DDC_FLOAT(adc_u8)
%   out = M1_DDC_FLOAT(adc_u8, 'FTW_Norm', 0.3, 'CIC_R', 4, 'CIC_N', 5)
%
%   输入
%     adc_u8 : 8-bit 无符号 ADC 原始码（offset binary，中点 128）
%
%   可选参数（Name-Value）
%     FTW_Norm   本振归一化频率 f/fs（默认 0.3，即 120 MHz / 400 MHz）
%     CIC_R      CIC 抽取因子（默认 4，来源 cic_decimator_4x_enhanced.v）
%     CIC_N      CIC 级数（默认 5）
%     FIR_Scale  FIR 输出缩放（默认 1）
%     PhaseBits  NCO 相位量化位数（默认 0 = 理想浮点相位）
%                >0 时复刻 nco_400m_enhanced.v 的相位截断行为：
%                32-bit 累加器只取高 PhaseBits 位作为 LUT 地址。
%                RTL 实际为 8 bit；该截断会引入杂散与直流偏置，
%                正是 compare_dc.csv 中 ~20 LSB 偏置的来源，也是
%                RTL（含 LFSR 抖动）与 Python 模型之间的主要差异之一。
%
%   输出结构体
%     bb_i, bb_q   : 抽取 + 低通后的基带 I/Q，速率 fs_out = 100 MHz
%     cic_i, cic_q : CIC ÷4 之后、FIR 之前
%     mix_i, mix_q : 混频器输出（仍为 400 MHz 域）
%     fir_gain     : FIR 归一化前的直流增益（= sum(原始 18-bit 系数)）
%                    把 bb_* 乘以 fir_gain 即换算到 RTL 的 18-bit 码域
%     n_in, n_out, fs_in, fs_out, ftw_norm, phase_bits
%
%   注：本函数是"浮点骨架"，用于 M1 阶段打通链路与核对物理行为；
%       位宽精确的定点版本在 M2 阶段按 README §2.2 建立。

    ip = inputParser;
    ip.addParameter('FTW_Norm',  0.3);
    ip.addParameter('CIC_R',     4);
    ip.addParameter('CIC_N',     5);
    ip.addParameter('FIR_Scale', 1);
    ip.addParameter('PhaseBits', 0);
    ip.parse(varargin{:});
    p = ip.Results;

    adc_u8 = double(adc_u8(:));

    % ---- L1 场景层：8-bit offset-binary -> 归一化实数样本 ---------------
    x = (adc_u8 - 127.5) / 128;              % 约 ±1 满量程

    % ---- NCO：复本振 e^{-j2*pi*(f/fs)*n} -------------------------------
    n  = (0:numel(x) - 1).';
    ph = p.FTW_Norm * n;                     % 归一化相位（周期 = 1）
    if p.PhaseBits > 0
        q  = 2^p.PhaseBits;
        ph = floor(ph * q) / q;              % 复刻相位截断（LUT 地址截位）
    end
    lo = exp(-1j * 2 * pi * ph);

    % ---- Mixer：复下变频 ------------------------------------------------
    mix   = x .* lo;
    mix_i = real(mix);
    mix_q = imag(mix);

    % ---- CIC ÷R：N 级、每级长度 R 的滑动平均（与 CIC 频响等价） --------
    %      H(z) = ((1 - z^-R)/(1 - z^-1))^N
    cic_i = mix_i;
    cic_q = mix_q;
    for s = 1:p.CIC_N
        cic_i = filter(ones(1, p.CIC_R) / p.CIC_R, 1, cic_i);
        cic_q = filter(ones(1, p.CIC_R) / p.CIC_R, 1, cic_q);
    end
    cic_i_d = cic_i(1:p.CIC_R:end);
    cic_q_d = cic_q(1:p.CIC_R:end);

    % ---- FIR 低通：32 抽头，系数取自 fir_lowpass.v ----------------------
    [c, raw_gain] = m1_fir_coeffs();
    bb_i = p.FIR_Scale * filter(c, 1, cic_i_d);
    bb_q = p.FIR_Scale * filter(c, 1, cic_q_d);

    out = struct( ...
        'bb_i',     bb_i,  'bb_q', bb_q, ...
        'cic_i',    cic_i_d, 'cic_q', cic_q_d, ...
        'mix_i',    mix_i, 'mix_q', mix_q, ...
        'fir_gain', raw_gain, ...
        'n_in',     numel(x), ...
        'n_out',    numel(bb_i), ...
        'fs_in',    400e6, ...
        'fs_out',   400e6 / p.CIC_R, ...
        'ftw_norm', p.FTW_Norm, ...
        'phase_bits', p.PhaseBits);
end
