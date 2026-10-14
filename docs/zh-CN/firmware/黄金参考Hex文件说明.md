# 黄金参考 Hex 文件

- 源路径：`9_Firmware/9_2_FPGA/tb/cosim/real_data/hex/STALE_NOTICE.md`；SHA256：`e2dcbba7caf775cfb5792cd3751dcb15651ba60b97ecd5256074d996b0a77012`。

原文：`9_Firmware/9_2_FPGA/tb/cosim/real_data/hex/STALE_NOTICE.md`。

这些 Hex 文件是**已提交版本库的黄金参考数据**，用于严格逐比特一致的真实数据回归测试（`tb_doppler_realdata.v`、`tb_fullchain_realdata.v`）。

## 何时重新生成

多普勒处理流水线发生变化时，应重新生成：

- `doppler_processor.v`（FFT 点数、窗函数、子帧结构）。
- `xfft_16.v` / `fft_engine.v`（蝶形运算、旋转因子查表）。
- `range_bin_decimator.v`（抽取模式、峰值检测逻辑）。
- `fft_twiddle_16.mem`（旋转因子 ROM）。

## 如何重新生成

```bash
cd 9_Firmware/9_2_FPGA
python3 tb/cosim/real_data/golden_reference.py
# 随后复制多普勒专用文件：
python3 -c "
import numpy as np, os, shutil
h = 'tb/cosim/real_data/hex'
# 根据距离 FFT npy 重新生成打包激励数据
ri = np.load(f'{h}/range_fft_all_i.npy')
rq = np.load(f'{h}/range_fft_all_q.npy')
with open(f'{h}/doppler_input_realdata.hex','w') as f:
    for c in range(32):
        for r in range(64):
            i=int(ri[c,r])&0xFFFF; q=int(rq[c,r])&0xFFFF
            f.write(f'{(q<<16)|i:08X}\n')
shutil.copy2(f'{h}/doppler_map_i.hex', f'{h}/doppler_ref_i.hex')
shutil.copy2(f'{h}/doppler_map_q.hex', f'{h}/doppler_ref_q.hex')
"
```

## 架构

这些文件针对**双路 16 点 FFT** 多普勒架构生成：2 个交错 PRI 子帧，每个子帧执行加 Hamming 窗的 16 点 FFT。

源数据：ADI CN0566 Phaser 雷达（10.525 GHz X 波段 FMCW，4 MSPS）。

本次仅翻译说明，未重新生成或覆盖黄金参考数据。
