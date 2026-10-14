原文：`docs/release-notes.html`  
原文 SHA256：`FD2E0DDC7F30A7FE41946B66B44B8F70F0F4DF03671CB56ED4F8A68013FD9732`  
翻译日期：2026-10-08。以下为原文全文中文译文；提交、标签、构建及测试状态均转述原文，不代表本次新增验证。`TBD` 原样保留为待定提交。原文未标明页面发布日期。源文不一致项见[审阅发现](审阅发现.md)。

导航：[AERIS-10 文档](index.md) · [架构](architecture.md) · [实现日志](implementation-log.md) · [上板调试](bring-up.md) · [报告](reports.md) · [发布说明](release-notes.md)

# 按关键提交整理的发布说明

可追溯性。

围绕主要上板调试、调试和文档提交编写的里程碑说明。

## 提交时间线

| 提交 | 标题 | 影响 |
| --- | --- | --- |
| `TBD` **v0.1.8-te0713-ft601-dev** | TE0713/TE0701 + UMFT601X-B FT601 集成开发比特流 | Trenz + UMFT601X-B FMC LPC 组合的首个时序无违例 FT601 USB 集成构建。封装模块 `radar_system_top_te0713_umft601x_dev` 实例化完整 `usb_data_interface`，使用合成测试数据（距离/多普勒/CFAR 数据包）。修复源同步时钟偏斜后实现时序收敛：输出用 `set_max_delay -datapath_only` 替代 `set_output_delay`，并移除仅作输出的 `ft601_be[*]` 上错误的 `set_input_delay`。WNS +0.059 ns，WHS +0.121 ns，DRC 0 错误。策略：`Performance_ExplorePostRoutePhysOpt`。Vivado 2025.2。比特流：`docs/artifacts/te0713-te0701-umft601x-dev-2026-03-21.bit`。 |
| `TBD` **v0.1.7-te0713-heartbeat** | TE0713/TE0701 最小心跳上板调试比特流 | 使用 `radar_system_top_te0713_dev` 和 `te0713_te0701_minimal.xdc`，为 Trenz TE0713 + TE0701 组合创建低风险上板调试产物。远程 Vivado 2025.2 构建完成，DRC 0 错误，WNS +17.863 ns，WHS +0.265 ns。用于 FT601 到货前、任何雷达路径集成前的首次上板镜像。 |
| `ed629e7` **v0.1.6-mti** | Build 25：MTI 对消器 + 直流陷波滤波器集成 | 新生产基线。WNS +0.132 ns，WHS +0.058 ns。9,252 LUT（6.87%）、12,488 FF（4.64%）、17 BRAM（4.66%）、142 DSP48E1（19.19%）、0.753 W。新增模块：`mti_canceller.v`（双脉冲对消器，H(z)=1-z^-1）、直流陷波滤波器（内嵌于 system_top）。新增两个主机寄存器：`host_mti_enable`（0x26）、`host_dc_notch_width`（0x27）。23/23 FPGA、20/20 MCU 通过，3/3 真实数据联合仿真精确匹配。 |
| `075ae1e` **v0.1.5-cfar** | Build 24：集成噪声计算流水线化的 CA-CFAR 检测器 | 先前生产基线。WNS +0.179 ns，WHS +0.056 ns。8,558 LUT、10,384 FF、17 BRAM、142 DSP48E1、0.754 W。CA/GO/SO CFAR 模式，采用 BRAM 幅值缓冲区和滑动窗口算法。主机可配置保护单元/训练单元/alpha/模式寄存器（0x21–0x25）。通过噪声计算流水线化修复 Build 23 时序失败。22/22 FPGA、20/20 MCU 通过。 |
| `e93bc33` **v0.1.4-prod-fixes** | 7 项生产质量修复：检测错误、数字增益、看门狗、移除无效代码 | 修复检测粘滞标志和幅值滞后，将 `cfar → threshold_detect` 重命名，增加主机可配置数字增益控制（2 的幂次移位）、多普勒/chirp 数量不匹配保护（限幅 + 错误标志）、抽取器看门狗超时，移除 `bypass_mode` 无效代码，增加距离模式寄存器（0x20）。新增真实数据联合仿真框架。22/22 FPGA 通过。 |
| `2efab23` **v0.1.4-build21** | Build 21：FFT 优化 + 端到端 RTL 修复 + Vivado DRC 修复 + MMCM LOCKED false_path 修复 | 新生产基线。WNS +0.156 ns，WHS +0.064 ns，WPWS +0.361 ns。6,192 LUT（4.6%）、9,064 FF（3.4%）、16 BRAM（4.4%）、139 DSP48E1（18.8%）、0.732 W。包括 4 周期 FFT 蝶形（20% 吞吐率提升）、桶形移位旋转因子（-1 DSP）、`data_pending` 标志的 Vivado DRC 多驱动修复、MMCM LOCKED XDC `false_path` 修复（`-from → -through`）。19/19 FPGA、20/20 MCU 通过。 |
| `0773001` | 端到端集成测试 + RTL 修复：混频器时序、USB 数据待处理标志、接收器翻转信号连接 | 新增 `tb_system_e2e.v`，12 组、46 项端到端检查。RTL 修复：TX/RX 混频器使能按 FSM 状态互斥；USB 写 FSM 的 `data_pending` 粘滞标志，流控制复位默认值为 `3'b001`；mode-00 的 STM32 翻转信号连接；动态帧检测。修复 USB 测试 21/22/56 和回归脚本 PASS/FAIL 解析。19/19 FPGA、20/20 MCU 通过。 |
| `a3e1996` | FFT 引擎：SHIFT 合并到 WRITE（4 周期蝶形）+ 桶形移位旋转因子索引 | SHIFT 状态合并到 WRITE，使蝶形从 5 周期缩短为 4 周期（吞吐率增益 20%）。基于乘法器的旋转因子索引改为桶形移位（释放 1 个 DSP48）。通过 FFT 测试平台验证；预期不会造成时序回归。 |
| `7cdfa48` | Gap 2 GUI 设置：运行时 chirp 时序、流控制门控、状态回读 | 运行时可配置 chirp 时序（6 个新操作码 0x10–0x15）、流控制门控（操作码 0x04 现在门控 USB 写 FSM）、CFAR 阈值连接（操作码 0x03 替代硬编码值）、状态回读（操作码 0xFF 返回 7 字数据包）。新增 4 组测试平台检查。18/18 FPGA、20/20 MCU 回归通过。 |
| `e5d1b3c` | Gap 4 USB 读取路径：带翻转 CDC 的主机到 FPGA 命令路径 | FT601 读取 FSM 的 `cmd_*` 输出经翻转 CDC 接到 `clk_100m` 命令解码寄存器。主机现在可设置雷达模式、触发 chirp、设置 CFAR 阈值、控制数据流。新增 3 组测试平台检查（55 项）。18/18 FPGA 回归通过。 |
| `c6103b3` **v0.1.3-build20** | Gap 7 MMCM 抖动清理器 + CIC CREG 流水线 + XDC 时钟名修复 | 为 ADC 时钟抖动清理增加 400 MHz MMCM、CIC 梳状级 DSP48E1 CREG 流水线，并修复 XDC 冲突生成时钟。Build 20：WNS +0.426 ns（较 Build 18 改善 7 倍）。全部时序满足。 |
| `f3bbf77` | Gap 3 安全架构 | IWDG 看门狗、`Emergency_Stop` PA 电源轨切断、最高温度保护、周期性 IDQ 回读、紧急状态顺序。新增 5 项 MCU 测试，20/20 通过。 |
| `c87dce0` | Gap 5 BRAM 异步复位修复 | 按照 Xilinx UG901 指南，将 chirp 存储器加载器 BRAM 异步复位改为同步复位模式。 |
| `3b7afba` **v0.1.2-build18** | Build 18 生产构建 | 生产基线：WNS +0.062 ns，WHS +0.059 ns。6,088 LUT、8,946 FF、16 BRAM、140 DSP48E1、0.631 W。 |
| `ed6f79c` **v0.1.1-build17** | FIR DSP48 流水线化 + 匹配滤波器 BRAM 迁移 | 含 DSP48 流水线改进的 Build 17 生产构建。 |
| `c466021` | 固件错误排查收尾（B12–B17） | 通过补充 MCU 回归覆盖，关闭 PA 校准、ADC 缓冲区、DIAG 宏、TIM3 PWM 和过时诊断问题。 |
| `49c9aa2` | SPI 平台修复及 FPGA B2/B3 时序工作 | 修复旧平台 SPI 仅发送路径，落实 chirp BRAM 迁移及多普勒 DSP48 流水线工作。 |
| `3b32f67` | ADF4382A SPI 和片选正确性 | 修复平台 SPI 操作函数连接，增加软件管理 CS 行为，加宽 SPI 片选存储以正确处理 STM32 引脚值。 |
| `3979693` | 首批 8 个固件错误修复并附测试 | 通过回归覆盖关闭 LO 初始化顺序、AD9523 顺序、同步触发、温度定时器、GPIO 映射及相关 MCU 问题。 |

## 带标签发布

- **v0.1.7-te0713-heartbeat** — TE0713/TE0701 首次上电基线。最小心跳顶层、DRC 无错误、WNS +17.863 ns、WHS +0.265 ns。产物跟踪路径：`docs/artifacts/te0713-te0701-heartbeat-2026-03-21.bit`。
- **v0.1.6-mti**（ed629e7）— 当前生产基线。WNS +0.132 ns，WHS +0.058 ns。MTI 对消器 + 直流陷波滤波器。9,252 LUT、12,488 FF、142 DSP48E1、17 BRAM。0.753 W。
- **v0.1.5-cfar**（075ae1e）— 先前生产基线。WNS +0.179 ns。噪声计算流水线化的 CA-CFAR 检测器（CA/GO/SO 模式）。
- **v0.1.4-prod-fixes**（e93bc33）— 7 项生产修复 + 真实数据联合仿真框架。WNS 与 Build 21 相同（仅仿真变更）。
- **v0.1.4-build21**（2efab23）— CFAR 集成前生产基线。WNS +0.156 ns，WHS +0.064 ns。含 FFT 优化、端到端 RTL 修复、Vivado DRC 修复、MMCM LOCKED XDC 修复。139 DSP48E1（较 Build 20 减少 1）。
- **v0.1.3-build20**（c6103b3）— 先前生产基线。WNS +0.426 ns，全部时序满足。包括 Gaps 3、5、7。
- **v0.1.2-build18**（3b7afba）— 先前生产基线。WNS +0.062 ns。
- **v0.1.1-build17**（ed6f79c）— FIR DSP48 + BRAM 迁移构建。
- **v0.1.0-bringup** — 初始上板调试标签。

## 架构缺口状态

| # | 缺口 | 状态 |
| --- | --- | --- |
| 3 | 安全架构 | 完成（f3bbf77） |
| 5 | BRAM 异步复位 | 完成（c87dce0） |
| 7 | 400 MHz MMCM | 完成（c6103b3，Build 20） |
| 4 | USB 读取路径 | 完成（e5d1b3c） |
| 2 | GUI 设置 | 完成（7cdfa48） |
| 6 | CDC-15 USB 总线 | 上板调试后处理 |
| 1 | CFAR 实际实现 | 完成（075ae1e，Build 24；MTI 位于 ed629e7） |

## 在 GitHub 中打开

- [ed629e7](https://github.com/JJassonn69/PLFM_RADAR/commit/ed629e7)：MTI 对消器 + 直流陷波滤波器（v0.1.6-mti）
- [075ae1e](https://github.com/JJassonn69/PLFM_RADAR/commit/075ae1e)：Build 24 报告（v0.1.5-cfar）
- [0745cc4](https://github.com/JJassonn69/PLFM_RADAR/commit/0745cc4)：CFAR 噪声计算流水线化（时序修复）
- [f71923b](https://github.com/JJassonn69/PLFM_RADAR/commit/f71923b)：集成 CA-CFAR 检测器
- [e93bc33](https://github.com/JJassonn69/PLFM_RADAR/commit/e93bc33)：生产修复 1–7（v0.1.4-prod-fixes）
- [0b06436](https://github.com/JJassonn69/PLFM_RADAR/commit/0b06436)：真实数据联合仿真（v0.1.4-pre-fixes）
- [2efab23](https://github.com/JJassonn69/PLFM_RADAR/commit/2efab23)：Build 21：FFT 优化 + DRC 修复 + XDC 修复（v0.1.4-build21）
- [0773001](https://github.com/JJassonn69/PLFM_RADAR/commit/0773001)：端到端测试 + RTL 修复
- [a3e1996](https://github.com/JJassonn69/PLFM_RADAR/commit/a3e1996)：FFT 引擎优化
- [7cdfa48](https://github.com/JJassonn69/PLFM_RADAR/commit/7cdfa48)：Gap 2 GUI 设置
- [e5d1b3c](https://github.com/JJassonn69/PLFM_RADAR/commit/e5d1b3c)：Gap 4 USB 读取路径
- [c6103b3](https://github.com/JJassonn69/PLFM_RADAR/commit/c6103b3)：Gap 7 MMCM + CREG（v0.1.3-build20）
- [f3bbf77](https://github.com/JJassonn69/PLFM_RADAR/commit/f3bbf77)：Gap 3 安全架构
- [c87dce0](https://github.com/JJassonn69/PLFM_RADAR/commit/c87dce0)：Gap 5 BRAM 复位
- [c466021](https://github.com/JJassonn69/PLFM_RADAR/commit/c466021)：固件错误 B12–B17
- [49c9aa2](https://github.com/JJassonn69/PLFM_RADAR/commit/49c9aa2)：SPI + FPGA 时序
- [3b32f67](https://github.com/JJassonn69/PLFM_RADAR/commit/3b32f67)：ADF4382A SPI
- [3979693](https://github.com/JJassonn69/PLFM_RADAR/commit/3979693)：首批 8 个错误修复

主要硬件验证里程碑合并时，及时更新本页。
