原文：`docs/implementation-log.html`  
原文 SHA256：`6548DD185FE7838B2A9A87268732012DA42C018625BC921AC38B05144BE67E80`  
翻译日期：2026-10-08。以下为原文全文中文译文；构建、测试、功耗、时序及“已完成”均是原文声明，不代表本次新增验证。原文未标明页面发布日期。源文不一致项见[审阅发现](审阅发现.md)。

导航：[AERIS-10 文档](index.md) · [架构](architecture.md) · [实现日志](implementation-log.md) · [上板调试](bring-up.md) · [报告](reports.md) · [发布说明](release-notes.md)

# 实现时间线与改进

工程日志。

关键固件、时序、调试和基础设施变更的汇总记录。

## 近期里程碑时间线

### Build 25 — MTI 对消器 + 直流陷波滤波器（ed629e7）

在距离单元抽取器与多普勒处理器之间集成 MTI 双脉冲对消器（`H(z) = 1 - z^{-1}`），用于去除地面杂波。直流陷波滤波器位于多普勒处理之后、CFAR 之前，将距 0 号单元 ±`host_dc_notch_width` 范围内的单元置零。新增两个主机寄存器：`host_mti_enable`（0x26）、`host_dc_notch_width`（0x27）。两者默认关闭/直通，以保持向后兼容。Build 25：WNS +0.132 ns，WHS +0.058 ns。9,252 LUT、12,488 FF、17 BRAM、142 DSP、0.753 W。23/23 FPGA 回归通过、29/29 MTI 独立检查通过、3/3 真实数据联合仿真精确匹配。

### Build 24 标记为 v0.1.5-cfar — CA-CFAR 生产基线（075ae1e）

集成支持 CA/GO/SO 模式的 CA-CFAR 检测器，替代旧阈值检测器。噪声计算流水线化（Build 23 修复）。WNS +0.179 ns，WHS +0.056 ns。8,558 LUT、10,384 FF、17 BRAM、142 DSP、0.754 W。CFAR 开销：+2,229 LUT、+1,281 FF、+1 BRAM、+3 DSP。包含幅值 BRAM 缓冲区、滑动窗口算法，以及主机可配置的保护单元/训练单元/alpha/模式寄存器（操作码 0x21–0x25）。

### Build 23 时序失败，已定位根因并修复（0745cc4）

Build 23 的 WNS 为 -0.309 ns，原因是 CFAR `noise_sum_comb → 交叉乘法 → alpha*noise DSP` 的组合路径。通过将噪声计算拆成 `ST_CFAR_THR` 和 `ST_CFAR_MUL` 流水级，将路径分散到 2 个时钟周期后修复。

### 7 项生产修复标记为 v0.1.4-prod-fixes（e93bc33）

检测错误修复（粘滞标志 + 滞后一个周期的幅值）、`cfar → threshold_detect` 重命名、数字增益控制（主机可配置的 2 的幂次移位）、多普勒/chirp 数量不匹配保护（限幅 + 错误标志）、抽取器看门狗（超时计数器）、移除 `bypass_mode` 无效代码、距离模式寄存器（0x20）。增加真实数据联合仿真框架。22/22 FPGA 回归通过。

### 真实数据联合仿真框架（0b06436）

增加三个真实数据测试平台：距离 FFT、多普勒和完整处理链。使用记录的 ADC 采集数据，将 RTL 输出与 Python 黄金参考比较。总计 5,137 项数据检查全部逐位精确匹配。在生产修复前标记为 `v0.1.4-pre-fixes`，作为回退保障。

### Build 21 标记为 v0.1.4-build21 — CFAR 集成前生产基线（2efab23）

WNS +0.156 ns，WHS +0.064 ns，WPWS +0.361 ns。6,192 LUT（4.6%）、9,064 FF（3.4%）、16 BRAM（4.4%）、139 DSP48E1（18.8%）、0.732 W。包含 FFT 4 周期蝶形运算（20% 吞吐率提升）、桶形移位旋转因子（-1 DSP）、Gap 2 GUI 设置、端到端 RTL 修复（混频器时序、USB 数据待处理标志、接收器翻转信号连接）、`data_pending` 标志的 Vivado DRC 多驱动修复，以及 MMCM LOCKED XDC `false_path` 修正（`-from → -through`）。通过 `catch` 代码块包裹 `report_exceptions/check_timing`，修复构建脚本崩溃（Vivado 2025.2 问题）；全部 12 份关键报告和比特流成功生成。

### 端到端集成测试 + RTL 修复：混频器时序、USB 数据待处理标志、接收器连接（0773001）

新增端到端测试平台 `tb_system_e2e.v`，分 12 组执行 46 项检查，覆盖复位、TX、安全、RX、USB 读写、CDC、波束扫描、复位恢复、流控制、延迟预算和看门狗。端到端测试发现的 RTL 修复：chirp 控制器 TX/RX 混频器使能按 FSM 状态互斥；USB 写 FSM 增加 doppler/cfar `data_pending` 粘滞标志，流控制复位默认值改为仅距离数据（`3'b001`）；接收器接入 STM32 翻转信号，并支持动态帧检测。USB 单元测试 21/22/56 针对 `data_pending` 架构更新。加固回归脚本 PASS/FAIL 解析。19/19 FPGA、20/20 MCU 通过。

### FFT 引擎优化：4 周期蝶形 + 桶形移位旋转因子（a3e1996）

将 SHIFT 状态合并到 WRITE 阶段，使蝶形运算流水线由 5 周期缩短为 4 周期（吞吐率提升 20%）。用可变左移（桶形移位）替代基于乘法器的旋转因子索引计算，释放一个 DSP48 乘法器。两项变更均通过 FFT 测试平台验证。

### Gap 2：GUI 设置 — 运行时 chirp 时序、流控制、状态回读（7cdfa48）

雷达 chirp 时序参数（长/短 chirp、监听、保护周期、每个俯仰角的 chirp 数）现可通过 6 个新 USB 操作码（0x10–0x15）在运行时配置。流控制（操作码 0x04）分别门控 USB 写 FSM 的各数据流。CFAR 阈值（操作码 0x03）连接到实际比较逻辑（此前为硬编码）。状态回读（操作码 0xFF）返回含全部当前设置的 7 字数据包。CDC 通过逐位 2 级同步器（流控制）及翻转 CDC（状态请求）处理。新增 4 组测试平台检查。18/18 FPGA、20/20 MCU 通过。

### Gap 4：通过翻转 CDC 接通 USB 读取路径（e5d1b3c）

FT601 读取 FSM 的 `cmd_*` 输出通过翻转 CDC 连接到 `radar_system_top.v` 中 `clk_100m` 域的命令解码寄存器。主机现在可经 USB 设置雷达模式、触发 chirp、设置 CFAR 阈值和控制数据流。新增 3 组测试平台检查（总计 55 项检查）。18/18 FPGA 回归通过。

### Build 20 标记为 v0.1.3-build20 — 新生产基线（c6103b3）

WNS 从 Build 18 的 +0.062 ns 提升至 +0.426 ns，改善 7 倍。包含 400 MHz MMCM 抖动清理器、CIC 梳状级 DSP48E1 CREG 流水线和 XDC 时钟名修复。满足全部时序约束。6,092 LUT（4.5%）、9,024 FF（3.4%）、16 BRAM（4.4%）、140 DSP48E1（18.9%）、0.730 W。

### Build 19 时序失败的根因已定位并修复

Build 19 的 WNS 为 -0.011 ns，原因是冲突的 XDC `create_generated_clock` 阻止对 CDC 路径应用假路径。删除冲突约束并使用 Vivado 自动生成的 `clk_mmcm_out0` 后修复。

### Gap 3：安全架构已关闭（f3bbf77）

新增 IWDG 看门狗配置、`Emergency_Stop` PA 电源轨切断、最高温度保护、周期性 IDQ 回读和紧急状态顺序处理。新增 5 项 MCU 测试，20/20 MCU 回归通过。

### Gap 5：BRAM 异步复位已修复（c87dce0）

按照 Xilinx UG901 指南，将 chirp 存储器加载器 BRAM 的异步复位改为同步复位模式，防止生产目标上的 BRAM 推断失败。

### Build 18 标记为 v0.1.2-build18 — 先前生产基线

WNS +0.062 ns，WHS +0.059 ns。6,088 LUT、8,946 FF、16 BRAM、140 DSP48E1、0.631 W。全部时序满足。

### 固件错误排查已完成并有回归覆盖

全部 17 个已审计 MCU 固件错误已修复、通过回归测试并推送，包括 LO 初始化顺序、SPI 片选处理、PA 校准逻辑、TIM3 PWM 上板调试和过时诊断不一致。20/20 MCU 测试通过。

### FPGA 时序/资源清理阶段完成

chirp BRAM 迁移、多普勒 DSP48 流水线化、CIC 流水级划分、匹配滤波器回归修复以及完整 FPGA 回归，使活动基线达到 18/18 测试通过。

## 代码质量和验证升级

- FPGA 回归：23/23 测试套件通过，覆盖匹配滤波器、多普勒、CIC、CDC、USB（含读取路径）、FFT、NCO、FIR、距离抽取器、模式控制器、系统顶层集成、系统端到端、CFAR 独立测试和 MTI 独立测试。
- MCU 回归：20/20 测试通过（15 个错误修复测试 + 5 个 Gap 3 安全测试）。
- 架构缺口 1–7 全部关闭。Gap 1（CFAR）作为 CA-CFAR 检测器集成（Build 24）。增加 MTI 对消器和直流陷波滤波器（Build 25）。Gaps 2–7 在 Build 21 之前关闭。
- USB 主机到 FPGA 命令路径完整接通：读取 FSM、翻转 CDC，以及模式/触发/CFAR/流控制命令解码。GUI 设置（chirp 时序、流门控、状态回读）全面可用。
- 安全架构：IWDG 看门狗、紧急停止 PA 电源切断、温度保护、IDQ 回读、状态顺序处理。

## 构建历史和时序改进

- **Build 25（v0.1.6-mti）**：当前生产基线。WNS +0.132 ns，WHS +0.058 ns。MTI 对消器 + 直流陷波滤波器。9,252 LUT、12,488 FF、142 DSP48E1。0.753 W。
- **Build 24（v0.1.5-cfar）**：先前生产基线。WNS +0.179 ns，WHS +0.056 ns。CA-CFAR 检测器（CA/GO/SO）。8,558 LUT、142 DSP48E1。0.754 W。
- **Build 21（v0.1.4-build21）**：CFAR 集成前基线。WNS +0.156 ns，WHS +0.064 ns。FFT 4 周期蝶形 + 桶形移位旋转因子。139 DSP48E1（-1）。0.732 W。
- **Build 20（v0.1.3-build20）**：先前生产基线。WNS +0.426 ns，WHS +0.058 ns。400 MHz MMCM + CIC CREG 流水线。0.730 W。
- **Build 19**：失败（WNS -0.011 ns）。根因：冲突的 XDC 生成时钟阻止假路径应用。
- **Build 18（v0.1.2-build18）**：先前基线。WNS +0.062 ns，WHS +0.059 ns。0.631 W。
- **Build 17（v0.1.1-build17）**：FIR DSP48 流水线化 + 匹配滤波器 BRAM 迁移。
- 远程 Vivado 构建基础设施运行于 Ubuntu 24.04，使用 Vivado 2025.2，目标为 XC7A200T-2FBG484I。

在每次主要提交或上板调试门禁时更新本页。
