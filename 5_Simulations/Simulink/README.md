# AERIS-10 Simulink 参考模型 —— 建模方案

> 状态：**方案阶段（未建模）**　编写日期：2026-10-13
> 目录：`5_Simulations/Simulink/`
> 上游依据：`9_Firmware/9_2_FPGA/`（RTL）、`9_Firmware/9_2_FPGA/tb/cosim/`（行为级模型与黄金数据）

---

## 0. 一句话结论

**Simulink 能建、工具齐全（零安装成本），但"复现工程"这个说法需要修正：**

仓库里已经存在一套**行为级的完整参考模型**——`tb/cosim/fpga_model.py`（1418 行，逐位精确的 Python 定点模型）和 `tb/cosim/radar_scene.py`（676 行，雷达场景生成器），覆盖了 **ADC 输入 → CFAR 检测点** 的全链。

因此 Simulink 的价值**不是**"从零复现"，而必须落在 Python 模型做不到的三件事上（见 §3）。本方案就是围绕这三件事设计的。

---

## 1. 已有资产盘点（决定方案走向）

### 1.1 行为级模型（已存在，质量高）

| 文件 | 行数 | 作用 |
|---|---|---|
| `tb/cosim/fpga_model.py` | 1418 | **逐位精确**定点模型：`NCO` → `Mixer` → `CICDecimator` → `FIRFilter` → `DDCInputInterface` → `FFTEngine` → `FreqMatchedFilter` → `MatchedFilterChain` → `RangeBinDecimator` → `DopplerProcessor` → `SignalChain` |
| `tb/cosim/radar_scene.py` | 676 | 场景级模型：目标距离/速度/RCS、延迟、多普勒、AWGN、杂波、ADC 8-bit 量化；含 5 个标准场景 |
| `tb/cosim/gen_chirp_mem.py` | 206 | 生成 10 个啁啾 `.mem`（4 段 I/Q + 短啁啾） |
| `tb/cosim/gen_mf_cosim_golden.py` / `gen_doppler_golden.py` / `gen_multiseg_golden.py` | — | 黄金参考生成器 |
| `tb/cosim/compare.py` / `compare_mf.py` / `compare_doppler.py` | 449/330/340 | RTL ↔ Python 比对器，输出 CSV |
| `tb/cosim/real_data/golden_reference.py` | — | 真实数据集黄金参考 |

### 1.2 现成的测试向量与黄金输出（可直接复用）

- **输入向量**：`tb/cosim/adc_{dc, single_target, multi_target, noise_only, sine_1mhz}.hex`
- **黄金输出**：`mf_golden_py_{dc, impulse, tone5, chirp}_{i,q}.hex`、`doppler_golden_py_{stationary, moving, two_targets}.{csv,hex}`
- **比对结果**：`compare_*.csv`（14 个）
- **查找表**：`9_2_FPGA/*.mem`（15 个，含 `long_chirp_lut.mem`、`fft_twiddle_1024.mem`、`fft_twiddle_16.mem`）

> **这是本方案最重要的便利**：Simulink 模型的**验收标准是现成的**，不需要另立标准。让 Simulink 侧吃同一份 `.hex` 输入，输出与 `.csv` 黄金列逐点比对即可。

### 1.3 MATLAB 侧资产（几乎为零）

- 全仓 `.slx` / `.mdl`：**0 个**
- `.m` 脚本：6 个，其中 `5_Simulations/Matlab/Antenna_array.m` 是**第三方示例**（1.943 GHz / FR4 / strip-fed slot），与本项目 10.5 GHz 无关，**不可作为基线**
- 唯一有价值的 Python 基线：`5_Simulations/array_pattern_Kaiser25dB_like.py`（16×32 阵、Kaiser β=1.65、−25 dB 副瓣）

---

## 2. 系统参数基准表（建模必须用这一版）

来源：`tb/cosim/radar_scene.py`（行为级权威）+ RTL 模块头实测。

### 2.1 波形与系统

| 参数 | 值 | 来源 |
|---|---|---|
| 载频 `f_c` | 10.5 GHz | `radar_scene.py:31` |
| 波长 | 28.57 mm | `radar_scene.py:33` |
| 中频 `f_IF`（接收） | 120 MHz | `radar_scene.py:36` |
| 调频带宽 `BW` | 20 MHz | `radar_scene.py:37` |
| ADC | 8 bit, 400 MSPS, LVDS（AD9484） | `ad9484_interface_400m.v`；`radar_scene.py:42` |
| 长啁啾 | 30 µs | `T_LONG_CHIRP`；`T1_SAMPLES = 3600` @120 MHz |
| 短啁啾 | 0.5 µs | `T_SHORT_CHIRP`；`T2_SAMPLES = 60` @120 MHz |
| 长 PRI | 167 µs（30 发 + 137 收） | `radar_scene.py:50` |
| 短 PRI | 175 µs | `radar_scene.py:51` |
| 帧结构 | 32 chirp = 2 子帧 × 16（参差 PRI） | `CHIRPS_PER_FRAME / SUBFRAME` |
| 保护段 | 175.4 µs（21048 点 @120 MHz） | `GUARD_SAMPLES` |
| 扫描角范围 | 俯仰 31、方位 50 | `ELEVATION_MAX / AZIMUTH_MAX` |
| 距离分辨率 | 7.5 m | `radar_scene.py:64` |
| 最大不模糊距离 | ≈ 20.55 km | `radar_scene.py:65` |

### 2.2 处理链位宽（RTL 实测）

| 级 | 参数 | 值 |
|---|---|---|
| NCO | 相位累加/FTW | 32 bit；`PHASE_INC_120MHZ = 0x4CCCCCCD` |
| NCO | 正弦 LUT / 输出 | 1/4 波 64 项 / signed 16 bit |
| NCO | 流水级数 / 延迟 | 6 级 / 6 周期 |
| 相位抖动 | LFSR 位宽 | 8 bit（`lfsr_dither_enhanced`） |
| 混频器 | 位宽 | 18 bit |
| CIC | 级数 / 抽取 / 梳延迟 | 5 / 4 / 1 |
| CIC | 累加位宽 / 梳位宽 | 48 / 28 |
| FIR | 抽头 / 系数 / 数据 / 累加 | 32 / 18 / 18 / 36 |
| DDC 输出 | I/Q | signed 18 bit |
| AGC | 增益范围 | −7 … +7（左移放大 / 右移衰减） |
| AGC | 目标峰值 / attack / decay / holdoff | 200 / 1 / 1 / 4 |
| 匹配滤波 | FFT 长度 | 1024（overlap-save，10 态 FSM） |
| 距离抽取 | 输入 → 输出 / 因子 | 1024 → 64 / 16 |
| 多普勒 | 子帧 FFT / 总 bin | 16 / 32（2 子帧） |
| 多普勒 | 窗函数 | Hamming（`WINDOW_TYPE = 0`） |
| MTI | 距离单元 / 位宽 | 64 / 16 |
| CFAR | 类型 / 单元 | CA-CFAR，64 距离 × 32 多普勒 |
| CFAR | 幅度位宽 / α 位宽 | 17 / 8（Q4.4，`ALPHA_FRAC_BITS = 4`） |
| CFAR | 保护 / 训练单元上限 | 8 / 16 |

### 2.3 采样率流转（关键）

```
ADC 400 MSPS (8 bit)
  └─ DDC 混频(NCO 120 MHz) + 相位抖动
       └─ CIC ÷4  ──►  100 MSPS   ← FS_SYS，后续全部处理在此域
            └─ FIR 低通(32 抽头)
                 └─ AGC
                      └─ 匹配滤波(FFT 1024)
                           └─ 距离抽取 ÷16  ──►  64 距离单元
                                └─ 多普勒 FFT(2×16)
                                     └─ MTI
                                          └─ CA-CFAR  ──►  检测点 (距离, 速度)
```

---

## 3. Simulink 的定位：只做 Python 模型做不到的事

> **原则**：Python 侧 `fpga_model.py` 已是逐位精确模型且已接入 CI；**任何与它等价的重复劳动都不做。**

| 优先级 | 增量价值 | 为什么 Python 做不到 | 交付物 |
|---|---|---|---|
| **P1** | **定点字长敏感性分析** | `fpga_model.py` 硬编码 18/36/48 bit，无法做位宽搜索。Fixed-Point Designer 可系统扫描位宽 → SQNR / 溢出门限曲线 | 字长-精度曲线报告，回答"为什么必须是 18 bit" |
| **P2** | **HDL 生成 ↔ 手写 RTL 交叉验证** | HDL Coder 从同一模型生成 Verilog，与手写 RTL 构成**两条独立实现**；两者同时正确才可信 | 生成的 Verilog + 与 RTL 的对照报告 |
| **P3** | **ADC 之前的链路预算** | Python 从 ADC 开始，不含 RF。RF Blockset 建模增益/噪声/压缩点，才能对 3 km / 20 km 距离方程给数字 | 链路预算表 + 灵敏度曲线 |
| **P4** | **参数扫描与可视化** | 交互式 scope、批量参数扫描，便于产出论文/答辩用图 | 图表集 |

### 明确不做

- ❌ 全波电磁（10.5 GHz 互耦、波导阵）→ 属 CST / openEMS
- ❌ 替代 Python 模型做日常回归 → 属 pytest / `compare_*.py`
- ❌ 真实 FPGA 时序收敛、ADC 实测、外场指标 → 必须要硬件

---

## 4. 模型架构（三层）

```
L1 场景层   目标(距离/速度/RCS) → 延迟 + 多普勒 + 噪声/杂波 → 8-bit ADC @400MSPS
            等价物: radar_scene.py
            实现: MATLAB 脚本生成向量，或 Simulink 内建目标/信道模块
                 │
                 ▼
L2 处理链层 ★核心    DDC(NCO+混频) → CIC÷4 → FIR → AGC
                    → 匹配滤波 → 距离抽取÷16 → 多普勒 → MTI → CA-CFAR
                    等价物: fpga_model.py
                 │
                 ▼
L3 定点/HDL 层   逐级定点化 → 位宽扫描 → HDL Coder 生成 Verilog
```

**建议先做 L2，且从浮点双精度版本起步**，再用 L3 逐级替换为定点——这样每一级的定点误差可单独归因。

---

## 5. 模块映射表（RTL ↔ Simulink）

| RTL 文件 | Simulink 模块 | 库 |
|---|---|---|
| `nco_400m_enhanced.v` | NCO（相位累加 + 1/4 波 LUT） | DSP System Toolbox |
| `ddc_400m.v` | Downconverter / 复数混频 | DSP System Toolbox |
| `cic_decimator_4x_enhanced.v` | CIC Decimation（5 级，R=4，M=1） | DSP System Toolbox |
| `fir_lowpass.v` | FIR Decimation / Discrete FIR Filter（32 抽头） | DSP System Toolbox |
| `rx_gain_control.v` | AGC / 变增益（含饱和） | DSP System Toolbox |
| `matched_filter_processing_chain.v` | Matched Filter / Pulse Compression（FFT 1024） | Phased Array / Radar Toolbox |
| `range_bin_decimator.v` | Decimator（÷16） | DSP System Toolbox |
| `doppler_processor.v` | FFT + Range-Doppler Processing | DSP + Phased Array Toolbox |
| `mti_canceller.v` | MTI Filter | Phased Array Toolbox |
| `cfar_ca.v` | CFAR Detector（CA） | Phased Array Toolbox |
| `plfm_chirp_controller.v` | 波形源：直接读 `long_chirp_lut.mem` | — |
| `radar_mode_controller.v` | Stateflow 状态机 | Stateflow |
| `chirp_memory_loader_param.v` | 由 `.mem` 驱动的波形查找 | — |

---

## 6. 验证判据（三级，全部复用现成数据）

| 级别 | 比对对象 | 输入 | 判据 |
|---|---|---|---|
| **V0** 自洽 | Simulink 浮点链 ↔ Simulink 定点链 | 内建 | 归一化误差 < 1 LSB |
| **V1** 对 Python 黄金 | `mf_golden_py_*.hex`、`doppler_golden_py_*.{csv,hex}` | `tb/cosim/adc_*.hex` | **逐点误差 ≤ 1 LSB**（与现有 `compare_*.py` 同口径） |
| **V2** 对 RTL | `compare_*.csv` 的 `rtl_i / rtl_q` 列 | 同上 | 同一容差；差异需能归因到定点位宽 |

**验收以 V1 为主**——因为 Python 模型本身已被 CI 认定与 RTL 一致，V1 通过即等于间接通过 V2。

---

## 7. 目录结构

```
5_Simulations/Simulink/
├── README.md              本方案文档
├── models/                Simulink 模型（.slx），后续生成
├── scripts/               MATLAB 建模/扫描脚本（.m），后续编写
├── data/                  从 tb/cosim 导入的向量与黄金数据副本
└── docs/                  后续分析报告
```

---

## 8. 里程碑

| 阶段 | 内容 | 通过标志 | 状态 |
|---|---|---|---|
| **M0** | 环境确认：MATLAB MCP 连通、license 正常、能读写 `tb/cosim` | MATLAB 能执行脚本并打印版本 | ✅ 已完成 |
| **M1** | L2 浮点链骨架 + 波形源读 `long_chirp_lut.mem` | 跑通 `adc_dc.hex`、`adc_sine_1mhz.hex` 两个最简场景 | ✅ 已完成（见 §11） |
| **M2** | 定点化 DDC（NCO/混频/CIC/FIR，按 §2.2 位宽） | 与 `compare_*.csv` 逐点 ≤1 LSB | ✅ 已完成（见 §12；判据对 Python 参考成立，对 RTL 列受既有失配限制） |
| **M3** | 定点化匹配滤波 + 距离抽取 + 多普勒 | 与 `mf_golden_py_*`、`doppler_golden_py_*` 对齐 | ⏳ |
| **M4** | MTI + CA-CFAR | 检测点与 Python 一致 | ⏳ |
| **M5** | 位宽扫描报告 + HDL Coder 生成对照 | 产出 §3 中 P1/P2 两份交付物 | ⏳ |

M1→M2 是最难的一步（定点化），后续基本是复制既有流程。

---

## 9. 风险与待确认口径

### 9.1 本次实测发现的 3 处不一致（建模前必须定口径）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| **1** | `plfm_chirp_controller.v:36-38` 声明 `F_START = 30 MHz`、`F_END = 10 MHz`（**下降调频**），但 `long_chirp_lut.mem` 实测是 **10 → 30 MHz 上升调频**（分段质心 11.60 → 28.40 MHz，3600 点 @120 MSPS = 30 µs） | 本次用 FFT 分段测频实测 | 三个参数在本模块内**从未被引用**（死参数），故不影响功能；但会误导建模者把扫频方向写反 |
| **2** | DAC 侧啁啾落在 **10–30 MHz**，ADC 侧 IF 是 **120 MHz** | `long_chirp_lut.mem` 实测；`radar_scene.py:36` | 两者分属不同频域，需 ADF4382 双路本振规划才能确认映射；**建模仿真时必须先确定 TX IF → RX IF 的 LO 关系** |
| **3** | `ddc_400m.v` 中 `IF_FREQ = 120000000` 与 `PHASE_WIDTH = 32` 均**声明但未使用**（实际调谐字走 `PHASE_INC_120MHZ`） | 全文件符号检索仅命中声明行 | 重复定义源，后续改频率可能改错地方 |

### 9.2 其他风险

| 风险 | 说明 |
|---|---|
| license 未实测 | 已核实安装目录与工具箱清单，**尚未实际启动 MATLAB 验证 license checkout** |
| 工作量 | M1–M5 是持续投入，不是一次性任务；建议按里程碑分批验收 |
| 冗余风险 | 若最终只是把 `fpga_model.py` 翻译一遍，则价值为负——**必须锚定 §3 的 P1/P2** |
| 波形方向 | 若问题 1/2 的口径未定，匹配滤波参考的共轭方向可能写反，表现为脉压峰值位置偏移 |

---

## 10. 数据源清单（可复现）

| 类别 | 路径 |
|---|---|
| RTL | `9_Firmware/9_2_FPGA/*.v` |
| 行为级模型 | `9_Firmware/9_2_FPGA/tb/cosim/{fpga_model,radar_scene}.py` |
| 测试向量 | `9_Firmware/9_2_FPGA/tb/cosim/adc_*.hex` |
| 黄金输出 | `9_Firmware/9_2_FPGA/tb/cosim/{mf,doppler,multiseg}_golden_*, *_golden_py_*` |
| 比对结果 | `9_Firmware/9_2_FPGA/tb/cosim/compare_*.csv` |
| 查找表 | `9_Firmware/9_2_FPGA/*.mem` |
| 天线阵基线 | `5_Simulations/array_pattern_Kaiser25dB_like.py` |
| 中文盘点 | `docs/zh-CN/firmware/实现与验证盘点.md`、`docs/zh-CN/firmware/测试场景与匹配滤波参考数据.md` |

---

## 11. M1 完成记录（2026-10-13）

### 11.1 交付物

| 类型 | 路径 |
|---|---|
| 测试向量 | `data/adc_dc.hex`、`data/adc_sine_1mhz.hex`（16384 点 8-bit offset-binary）、`data/long_chirp_lut.mem`（3600 项） |
| 黄金比对 | `data/compare_dc.csv`、`data/compare_sine_1mhz.csv`（列：`idx,rtl_i,py_i,err_i,rtl_q,py_q,err_q`） |
| MATLAB 脚本 | `scripts/m1_load_hex.m`、`scripts/m1_fir_coeffs.m`、`scripts/m1_ddc_float.m`、`scripts/m1_run.m` |
| 报告与图 | `docs/M1_report.txt`、`docs/m1_fig1_adc_dc.png`、`m1_fig2_adc_sine_1mhz.png`、`m1_fig3_synth_120mhz.png`、`m1_fig4_long_chirp_lut.png` |

浮点链签名：`out = m1_ddc_float(adc_u8, 'FTW_Norm',0.3, 'CIC_R',4, 'CIC_N',5, 'FIR_Scale',1, 'PhaseBits',0)`

### 11.2 验收结果（全部 PASS）

```
adc_dc.hex         in=16384 out=4096  reject=-74.1 dB [PASS]
adc_sine_1mhz.hex  in=16384 out=4096  reject=-50.4 dB [PASS]（控制实验 -73.9 dB）
synth 120MHz       DC(Q)=-0.3991 expect -0.4000 err=0.233% [PASS]
long_chirp_lut     centroid 11.7 -> 28.3 MHz  trend +16.67 [PASS]
```

- **CIC 单音抑制实测 −74.1 dB，与理论值完全吻合**，链路结构正确。
- 合成带内单音复现解析解 `Q(DC) = −0.4`，误差 0.233%。
- `long_chirp_lut.mem` 分段质心 **11.7 → 28.3 MHz 上升调频**，**确认 §9.1 问题 1 的修正结论**（RTL 中 F_START/F_END 为死参数，实际波形是 10→30 MHz 上升）。

### 11.3 本轮新增的三条关键约束（M2 定点化的输入）

| # | 结论 | 依据 |
|---|---|---|
| **1** | **CIC 对单音的抑制 ≠ 对噪声的抑制。** 对 120 MHz 归一化 0.3 单音，5 级 R=4 CIC 衰减 −74.1 dB；但对白噪声功率增益仅 **0.111（−9.6 dB）**（各级输出相关，噪声功率不按级数线性叠加）。故 `adc_sine_1mhz` 的 −50.4 dB 是 **8-bit ADC 量化噪底决定的物理下限**，不是链路缺陷。控制实验（同频无量化理想正弦）得 −73.9 dB 即证。 | `m1_run.m` 控制实验 + 噪底预测 `qn*sqrt(0.1109)`，`qn=(1/128)/sqrt(12)=2.2553e-3` |
| **2** | **NCO 相位截断产生的是恒定相位旋转，不产生 DC。** `NCO_SINE_LUT` 用 64 项 / 1/4 波，相位截断相当于固定相位偏移（均值 0.5 LSB 相位），混频后只旋转输出、不引入直流项。M2 建模时必须把"相位截断杂散"与"路径增益截断偏置"分开处理。 | `PhaseBits=8` 场景 vs 理想场景，DC 分量无差异 |
| **3** | ~~黄金输出的 ~20 LSB DC 偏置来自定点截断~~ **已被 M2 推翻（见 §12.3）**：该 DC 来自 NCO 象限译码缺陷，定点截断几乎不贡献（理想本振对照实验 FIR DC 仅 −2.0）。 | ~~`compare.py` 列定义 + `fpga_model.py` 符号检索~~ → §12.3 理想本振隔离实验 |

> 因此 M1 的判定口径定为：**浮点链只需证明"信号被正确搬运与抑制"**；与黄金逐点对齐是 M2 的验收指标，不能拿来判 M1。

### 11.4 M2 启动前需确认的口径

1. **DC 偏置处理策略**：逐点 ≤1 LSB 意味着 M2 必须复现 CIC/FIR 的截断与饱和行为（含 `>>10` / `>>17` 的 floor 语义与 18-bit 饱和），而不是用 round-half-up。是否按"严格复刻 floor 语义"实现？
2. **NCO 幅度量化粒度**：`NCO_SINE_LUT` 是 64 项 16-bit 表，M2 需确认表项是满幅 `32767` 还是 `32768` 定标。
3. **§9.1 问题 2（TX 10–30 MHz vs RX IF 120 MHz 的 LO 映射）**仍未有结论，M3 匹配滤波参考方向依赖此项。

---

## 12. M2 完成记录（2026-10-13）

### 12.1 口径与交付物

用户确认口径 = **严格复刻 RTL 的 floor 截断语义**（CIC `>>10`、FIR `>>17`，逐级饱和与 RTL 一致）。NCO LUT 定标自查解决：64 项满幅 **32767**（非 32768），`lut(k+1)=round(32767*sin(kπ/128))`，最大表项 `0x7FF5=32757`。验收基准 = 18-bit FIR 原始输出（黄金 `py_i` 列，即 `fir_i_raw`）。

| 类型 | 路径 |
|---|---|
| 权威参考重跑 | `scripts/m2_ref_python.py` → `data/ref_py_{dc,sine_1mhz}.csv`（复现黄金 `py_i`，max diff = 0） |
| 定点模型 | `scripts/m2_ddc_fixed.m`（NCO→Mixer→CIC(I/Q)→FIR→DDC interface，逐拍流水线级建模） |
| 主驱动 | `scripts/m2_run.m`、辅助 `m2_load_adc_hex.m`、`m2_fir_coeffs.m`（raw 18-bit 系数，raw_gain=231944）、`m2_nco_lut.m` |
| 探针脚本 | `m2_probe.py` / `m2_nco_trace.py` / `m2_nco_waveform.py` / `m2_lo_probe.py` |
| 报告与图 | `docs/M2_report.txt`、`docs/m2_fig1_adc_dc.png`、`m2_fig2_adc_sine_1mhz.png`、`m2_fig3_nco_lo_defect.png`、`m2_fig4_dc_origin.png` |

### 12.2 验收结果（VERDICT PASS）

```
dc          model vs Python ref  max 0 LSB, bit-exact 100%  [PASS]   vs golden py_i max 0 LSB [PASS]
sine_1mhz   model vs Python ref  max 0 LSB, bit-exact 100%  [PASS]   vs golden py_i max 0 LSB [PASS]
```

- MATLAB 定点 DDC 对生成黄金 `py_*` 列的权威 Python 模型**逐位一致（0 LSB，两场景全记录）**。
- 对黄金 `rtl_i` 列的偏差完全等于黄金自身的 rtl-vs-py 失配（dc: max 48/rms 1.09/99.7% ≤1 LSB；sine: max 428/rms 70.4/1.2% ≤1 LSB）——本移植**自身零误差**。
- **判据表述修正**：「逐点 ≤1 LSB」对 Python 参考成立；对 RTL 列在 sine 场景不成立，这是 cosim 既有的 RTL/Python 失配（非整数时延之外的相位/幅度失配，lag 扫描 lag=0 最小），带入 M3 解决。

### 12.3 核心发现：M1 结论 3 被推翻——NCO 象限译码缺陷（真实硬件缺陷）

`nco_400m_enhanced.v:103`：

```verilog
wire [5:0] lut_index = (quadrant_w[0] ^ quadrant_w[1]) ? ~lut_address[5:0] : lut_address[5:0];
```

四分之一波对称只应使用 `quadrant_w[0]`；误用 XOR 使象限 1、2（而非 1、3）取反索引 → **象限 2、3 的 sin/cos 互换，复数本振不再是解析信号**。实测相位表（256 拍窗，FTW=0x4CCCCCCD）：

| 象限 | 实测 LO 相位 | 理想 |
|---|---|---|
| q0 | 1.4° ✅ | 0° |
| q1 | 91.4° ✅ | 90° |
| **q2** | **268.6° ❌** | 180° |
| **q3** | **358.6° ❌** | 270° |

**证据链（理想本振隔离实验，`m2_lo_probe.py`）**：同一定点链、仅换理想 cos/sin，FIR DC 从 **+20.2 → −2.0**（与黄金偏差 0 → 27 LSB）。DC 与穿透都来自本振，不是截断。

**双重后果定量闭环**：

1. **~20 LSB DC**：缺陷本振在 FTW 实际访问的 10 个离散相位上有效 DC ≈ +0.048（4.8% FS）→ mixer DC +12.314 → CIC +11.800 → FIR +20.200（FIR 定点 DC 增益 231944/2^17=1.7696）。
2. **1 MHz 输入穿透**：`adc×LO` 的直流项把输入直接搬到基带，**绕过 CIC 阻带**（119/121 MHz 的 ~−76 dB 完全失效）。预测 FIR rms = 50×512×0.0481×1.7696/√2 ≈ 1541，实测 **1597**；输出主峰实测 **1.004 MHz**（即输入频率，0 dB 绝对主导）。

**建议**：该缺陷应反馈 RTL 维护者（`quadrant_w[0]^quadrant_w[1]` → `quadrant_w[0]`）。修复后预计 DC 归零、带外抑制恢复，Simulink 模型与 Python 模型均保留 bug-compatible 分支以便对照。

### 12.4 遗留到 M3

| 项 | 说明 |
|---|---|
| RTL vs Python sine 失配（rms 70.4 LSB） | 非时延问题；两侧幅度均与本振有效 DC 成比例，疑为 RTL LUT 与 Python LUT 的细微差异，脉压前必须解决（chirp 场景幅度量级相同） |
| §9.1 问题 2 | TX/RX LO 映射仍待定，匹配滤波参考共轭方向依赖此项 |
| M3 内容 | 定点化匹配滤波 + 距离抽取 + 多普勒，对齐 `mf_golden_py_*`、`doppler_golden_py_*` |
