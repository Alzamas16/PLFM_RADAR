function v = m1_load_hex(fp, bits)
%M1_LOAD_HEX  读取仿真用 .hex 向量文件。
%
%   v = M1_LOAD_HEX(fp)        % 默认按 8-bit offset-binary 解码
%   v = M1_LOAD_HEX(fp, 16)    % 按 16-bit 二进制补码解码
%
%   自动忽略空行与以 // 开头的注释行（$readmemh 风格）。
%
%   解码约定
%     8-bit  : 返回 double，已减去中点 127.5（即直流零点映射到 0）
%     16-bit : 返回 double，已按补码还原为带符号值
%
%   参见 9_Firmware/9_2_FPGA/tb/cosim/*.hex

    if nargin < 2
        bits = 8;
    end

    txt   = fileread(fp);
    lines = regexp(txt, '\r\n|\n|\r', 'split');

    raw = zeros(numel(lines), 1);
    n   = 0;
    for k = 1:numel(lines)
        ln = strtrim(lines{k});
        if isempty(ln) || strncmp(ln, '//', 2)
            continue
        end
        n = n + 1;
        raw(n) = hex2dec(ln);
    end
    raw = raw(1:n);

    if bits == 8
        v = double(raw) - 127.5;
    else
        half = 2^(bits - 1);
        v    = double(raw);
        idx  = v >= half;
        v(idx) = v(idx) - 2^bits;
    end
end
