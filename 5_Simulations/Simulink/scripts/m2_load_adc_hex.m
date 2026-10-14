function adc = m2_load_adc_hex(path)
%M2_LOAD_ADC_HEX  Read an 8-bit ADC vector in hex (one code per line).
%   Blank lines and '//' comments are ignored. Returns raw integer codes
%   0..255 (NOT offset-shifted) -- the fixed-point chain does its own
%   offset-binary conversion, exactly like the RTL.

fid = fopen(path, 'r');
if fid < 0
    error('m2_load_adc_hex:open', 'cannot open %s', path);
end
c = onCleanup(@() fclose(fid));

vals = [];
while true
    ln = fgetl(fid);
    if ~ischar(ln), break; end
    ln = strtrim(ln);
    if isempty(ln) || startsWith(ln, '//'), continue; end
    vals(end+1, 1) = hex2dec(ln); %#ok<AGROW>
end
adc = mod(vals, 256);
end
