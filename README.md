[![GitHub stars](https://img.shields.io/github/stars/NawfalMotii79/PLFM_RADAR?style=social)](https://github.com/NawfalMotii79/PLFM_RADAR/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/NawfalMotii79/PLFM_RADAR?style=social)](https://github.com/NawfalMotii79/PLFM_RADAR/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/NawfalMotii79/PLFM_RADAR?style=social)](https://github.com/NawfalMotii79/PLFM_RADAR/watchers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware: CERN-OHL-P](https://img.shields.io/badge/Hardware-CERN--OHL--P-blue.svg)](https://ohwr.org/cern_ohl_p_v2.txt)

# AERIS-10: Open Source Pulse Linear Frequency Modulated Phased Array Radar<br>AERIS-10 开源脉冲线性调频相控阵雷达

[![Hardware: CERN-OHL-P](https://img.shields.io/badge/Hardware-CERN--OHL--P-blue.svg)](https://ohwr.org/cern_ohl_p_v2.txt)
[![Software: MIT](https://img.shields.io/badge/Software-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange)](https://github.com/NawfalMotii79/PLFM_RADAR)
[![Features: Work in Progress](https://img.shields.io/badge/Features-Work_in_Progress-yellow)](https://github.com/NawfalMotii79/PLFM_RADAR/issues)
[![Frequency: 10.5GHz](https://img.shields.io/badge/Frequency-10.5GHz-blue)](https://github.com/NawfalMotii79/PLFM_RADAR)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/NawfalMotii79/PLFM_RADAR/pulls)


AERIS-10 is an open-source, low-cost 10.5 GHz phased array radar system featuring Pulse Linear Frequency Modulated (LFM) modulation. Available in two versions (3km and 20km range), it's designed for researchers, drone developers, and serious SDR enthusiasts who want to explore and experiment with phased array radar technology.<br>
AERIS-10 是一个开源、低成本的 10.5 GHz 相控阵雷达系统，采用脉冲线性调频（LFM）调制。它提供两个版本，标称探测距离分别为 3 km 和 20 km，面向希望探索和试验相控阵雷达技术的研究人员、无人机开发者和资深软件定义无线电（SDR）爱好者。

![AERIS-10 Antenna Array](https://raw.githubusercontent.com/NawfalMotii79/PLFM_RADAR/main/8_Utils/Antenna_Array.jpg)

[中文资料目录](docs/zh-CN/README.md) · [项目盘点](docs/zh-CN/项目盘点.md)

英文正文保留，中文逐段、逐条紧接在原文下方。性能、测试状态、许可证说明和社区数量均为原文陈述，未作硬件实测或联网核实。原文型号与版本要求的差异见中文译注。

## 项目 Python 3.13 虚拟环境 / Project Python environment

项目根目录 `.venv` 已由本机系统 Python **3.13.14** 创建，`include-system-site-packages = false`。已通过 `sfw` 安装 37 个项目依赖包；环境中另有创建虚拟环境时提供的 pip。运行项目时明确使用 `.venv\Scripts\python.exe`。

The project uses `.venv`, created from the installed system Python 3.13.14. Host dependencies are installed in this environment. Use `.venv\Scripts\python.exe` for host software, analysis and tests; FPGA tools, MCU toolchains and native hardware drivers remain separate requirements.

### 依赖清单 / Dependencies

`requirements-local.txt` 引用现有 V65、V7 和 PyQt GUI 依赖，另含 pandas、pyserial、pytest、ruff、uv；`pyproject.toml` 的 dev 组同时参与安装。范围包括 NumPy、SciPy、matplotlib、HDF5、PyQt6/WebEngine、跟踪/聚类、CRC、USB Python 接口及测试工具。

`requirements-local.lock.txt` 保存本次 Windows x64、Python 3.13 环境的确切包版本，供同类环境复现。它不是跨操作系统的通用锁文件，不包含 Vivado、GCC/Make、Icarus、openEMS、CST 或 USB 原生驱动。

### 创建与安装 / Create and install

以下命令在项目根目录的 PowerShell 执行。本机 `.venv` 已创建，日常运行无需重建，也无需激活。

```powershell
## 仅首次创建时执行 / First-time creation only
python3.13 -m venv .venv

## 使用本机已有 uv，并经 sfw 安装 / Install through sfw
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
& .\.tools\sfw.exe uv pip install --python .venv/Scripts/python.exe --no-python-downloads -r requirements-local.txt --group dev --link-mode=copy
```

`.tools/sfw.exe` 按 [Socket 官方手动安装方式](https://docs.socket.dev/docs/socket-firewall-free)，从 [v1.15.4 发布页](https://github.com/SocketDev/sfw-free/releases/tag/v1.15.4) 下载 Windows x86_64 二进制，SHA256 已与发布资产 digest 核对。来源记录见 [sfw 安装来源](docs/zh-CN/sfw安装来源.json)。本机已有 `uv.exe` 在 `$env:USERPROFILE\.local\bin`，命令只调整当前 PowerShell 会话的 PATH。首次实际安装未指定 `--link-mode=copy`，uv 因缓存位于 C 盘而环境位于 D 盘，自动回退到复制并成功完成；上述复现命令显式使用复制。

安装完成后，可使用环境自身的 uv 按版本快照复现：

```powershell
$env:Path = "$PWD\.venv\Scripts;$env:Path"
& .\.tools\sfw.exe uv pip install --python .venv/Scripts/python.exe --no-python-downloads -r requirements-local.lock.txt --link-mode=copy
```

`.venv/` 和 `.tools/` 已加入 `.gitignore`，包文件与本机工具二进制不纳入版本控制。

### 运行 / Run

```powershell
## V65 离线演示 / V65 offline demo
& .\.venv\Scripts\python.exe .\9_Firmware\9_3_GUI\GUI_V65_Tk.py --demo

## V7 界面 / V7 dashboard
& .\.venv\Scripts\python.exe .\9_Firmware\9_3_GUI\GUI_V7_PyQt.py

## 依赖一致性与 GUI 测试 / Dependencies and GUI tests
& .\.venv\Scripts\uv.exe pip check --python .venv/Scripts/python.exe
& .\.venv\Scripts\python.exe -B -m pytest .\9_Firmware\9_3_GUI\test_GUI_V65_Tk.py .\9_Firmware\9_3_GUI\test_v7.py -q --tb=short -p no:cacheprovider
```

V65 离线演示无需板卡。V7 地图使用在线资源，其离线可用性需另行确认。实时 USB 模式仍需对应设备及后端：FT2232H 使用 pyftdi/libusb，FT601 使用 ftd3xx/D3XX；后者未列入当前通用 GUI 依赖清单。

### 验证记录 / Verification

实际结果见 [虚拟环境安装记录](docs/zh-CN/虚拟环境安装记录.json)、[模块导入探查](docs/zh-CN/项目虚拟环境.json)、[虚拟环境验证](docs/zh-CN/虚拟环境验证.json)。安装成功、可导入或可创建隐藏 Qt 应用，不等同于全部 GUI 功能、完整 CI 或真实硬件验证通过。

本次 `uv pip check` 检查环境中的 38 个发行包，依赖兼容；Qt 隐藏应用初始化和 WebEngine 导入通过，pytest/ruff 可运行。GUI pytest 实际为 **171 passed、3 failed、0 skipped、退出码 1**。三个失败仍为 `TestReplayEngineRawIQ` 清理临时 `.npy` 时的 Windows `WinError 32`，本轮没有修改回放或测试源码。与之前 Codex Python 环境相比，原来缺依赖导致的 5 项跳过本次已执行。

## Local tools and hardware requirements<br>本机工具与硬件条件

**项目 `.venv` 已使用系统 Python 3.13.14 并安装 GUI、数值分析与测试依赖，可以开展文档整理、离线分析、GUI 演示/回放和 Python 测试。GUI 测试实际为 171 通过、3 失败，尚未全部通过。RTL、FPGA、MCU、openEMS/QucsStudio 仍需对应工具；烧录、真实通信和射频性能验证需要硬件。**

核查日期：2026-10-08。本节当前 Python 状态以项目 `.venv`（系统 Python 3.13.14）为准；之前 Codex bundled Python 3.12.14 的探查仅作历史记录。工具检查包含 PATH、Windows 卸载注册表和明确的可执行文件路径；“未检出”不等于已穷尽所有便携安装。安装记录也不等于已具备许可证、工程适配或测试通过。

### 一 本机已有工具可以开展的工作

| 工作 | 已确认的本机工具 | 可以完成的内容与边界 |
|---|---|---|
| Markdown/HTML/TXT 翻译和项目盘点 | Git、PowerShell 7、Codex Python/Node、marked | 读取文本、生成中文对照与 HTML、核对源指纹/本地链接。本轮已执行，工程性能不由这些检查验证。 |
| 协议、源码和历史输出静态核对 | Git、Python 3.13.14、NumPy 2.5.3、pandas 3.0.6 | 比较操作码、字段布局、数值及已有数据，阅读 ADC/DDC/匹配滤波/检测代码；不能代替 RTL 仿真或真实 USB 抓取。 |
| Python 阵列因子图、过孔示意图与 DAC 激励 CSV | 项目环境 NumPy、pandas、matplotlib 3.11.2、SciPy 1.18.1 均可导入 | 依赖已具备，可开展计算与绘图；本轮没有重新执行这些生成脚本。阵列因子近似不能当作全波验证。 |
| V65/V7 离线界面、HDF5、跟踪与回放 | Tk、matplotlib、h5py 3.16.0、PyQt6 6.11.0/WebEngine、scikit-learn、filterpy、crcmod 均已安装且可导入 | 隐藏 Qt 应用初始化与 WebEngine 导入通过；V65/V7 运行入口可用。没有完成可见界面全流程或真实设备验证。 |
| GUI/协议无硬件测试与 Python 检查工具 | `.venv` 的 pytest 9.1.1、ruff 0.16.10、uv 0.12.23 可运行 | 实际 GUI pytest 为 171 通过、3 失败、0 跳过、退出码 1；失败是 Windows `.npy` 文件占用。全仓 ruff、跨层和完整 CI 未执行，不能称全部通过。 |
| MATLAB 天线与射频模型准备、离线计算 | 已实际启动 MATLAB R2026a Update 5；可见 Antenna、RF、RF PCB、Phased Array、Radar、Signal Processing 等工具箱 | 可开展参数计算、天线/RF 模型建立及已有数据分析。仓库 `Matlab/Antenna_array.m` 和 `Slotted_DielectricFilled_Waveguide.m` 的整套求解未在本轮执行，不承诺无需脚本适配即可复现全部结果。 |
| CST 电磁建模的环境准备 | CST Studio Suite 2026 安装记录及可执行文件已确认 | 本机已有 CST，无需先重复安装；许可证与求解未测试，仓库也没有已确认可直接运行的 `.cst` 工程。把 openEMS/MATLAB 模型转为 CST 属于后续建模任务。 |

MATLAB 可启动是实际运行证据；CST 与 Visual Studio 的存在性主要来自安装记录和文件探查，验证程度不同。Office 虽已安装，但 Word/Excel 仍按本轮范围暂停处理。

### 二 需要补充或配置工具才能完成的工作

| 工作 | 当前缺口 | 需要补充或确认的条件 | 是否必须有硬件 |
|---|---|---|---|
| 完整 CI 与动态跨层契约检查 | Python dev 依赖已安装；动态跨层部分仍缺 C++/Icarus，GUI 仍有 3 项失败 | 补动态测试工具并解决既有失败；完整 CI 还包含 MCU 和 RTL，不能仅凭 Python 包安装判断通过。 | 主机测试不需要 |
| MCU 主机单元测试 | make、GCC/C++ 命令未检出；Visual Studio 已登记，但未查到其 C++ 组件路径 | 当前 `tests/Makefile` 按 C11/C++17 的 `cc/c++` 与 POSIX 命令组织，需兼容工具链及 Windows 入口适配。Visual Studio 的安装记录不能直接证明这套 Makefile 可运行。 | 否，使用主机 mock |
| FPGA RTL 仿真与回归 | iverilog、vvp 未检出 | 补 Icarus Verilog，并适配 `run_regression.sh` 的 shell/POSIX 依赖。当前任务遵守 PowerShell 约束，不直接执行 Bash 回归脚本。 | 仿真不需要 |
| FPGA 综合、布局布线、时序与 `.bit` 生成 | Vivado 未在 PATH/安装记录中检出 | 配置 Vivado 与目标 Artix-7 器件支持，确认 50T/200T/Trenz 顶层和 XDC 配对。仅生成 bit 不需要板卡。 | 生成不需要；烧录及板上验证需要 |
| openEMS 天线/抗混叠滤波全波仿真 | 项目 `.venv` 缺 openEMS/CSXCAD；MATLAB `InitFDTD/RunOpenEMS` 未找到 | 补原生求解器、CSXCAD 和对应绑定/路径；先处理 AAF 脚本的 macOS 硬编码路径，以及 MATLAB 仿真脚本清理目录的逻辑。本轮没有执行这些脚本。 | 否 |
| QucsStudio 电路仿真 | 未检出 QucsStudio；源 `.sch` 首行标注 QucsStudio 5.8 | 提供兼容 QucsStudio 环境及器件模型；`QPA2962.sch` 引用仓库外的 Windows `.s2p` 路径，需先确认实际模型。安装工具本身不能修复缺失输入。 | 否 |
| PCB、制造与 DWG 图纸专项审查 | 未检出 KiCad/EAGLE 等对应 EDA 命令或安装记录；DWG 阅读环境未专项验证 | 按实际 `.sch/.brd` 或 KiCad 文件选兼容 EDA，并配置 DWG 阅读/编辑工具；Git/文本读取不能完成电气规则和制造可行性校验。 | 文件审查不需要；板卡实测需要 |

仓库 `CONTRIBUTING.md` 要求包安装使用 `sfw` 前缀；本轮已将官方 `sfw` 放在项目 `.tools/sfw.exe` 并核对 SHA256，所有项目依赖经其包装安装。`.venv/` 与 `.tools/` 已忽略，系统 Python 包没有作为安装目标。具体命令和版本快照见 [Python 虚拟环境](docs/zh-CN/Python虚拟环境.md)。

### 三 需要硬件才能完成的工作

| 工作 | 必需实物与工具 | 纯软件能够先做的准备 |
|---|---|---|
| STM32 整板烧录、上电/断电时序、温控和功放偏置校准 | 实际 STM32/电源/射频板、合适调试下载器、供电及电压/电流测量；还需 ARM 工具链和匹配 HAL/CubeMX 工程 | 阅读管理逻辑与主机 mock 测试。仓库没有确认完整可直接烧录的 CubeMX 工程，安装编译器不等于具备整板固件。 |
| FPGA 心跳、JTAG 烧录、实际时钟与复位 | 确认型号的 FPGA 板/Trenz 模块载板、合适 JTAG 接口、供电及 Vivado Hardware Manager | 确认 bit 来源、目标顶层、引脚约束及历史时序。 |
| 真实 USB 数据、吞吐、持续采集和板卡自检 | FT2232H 或 FT601 对应实物、连接板与线缆；FT2232H 的 pyftdi/pyusb 已安装，仍需确认原生 USB 后端；FT601 另需 ftd3xx/D3XX | 使用 mock/demo、离线数据和协议逻辑检查。pyftdi 不能当作 FT601 支持。当前项目环境未安装 ftd3xx，未验证原生后端及实物连接。 |
| ADC/DAC、时钟同步、射频链增益/噪声、阵列幅相校准 | 对应转换器、时钟、射频和天线板，适合频段的信号源、示波器/频谱分析/网络分析及校准连接条件 | 波形计算、离线处理、仿真与寄存器/时序审查，不能替代实际电气与射频测量。 |
| 3 km/20 km 探测距离、波束扫描、GPS/IMU 与整机目标跟踪 | 完整雷达、阵列、功放、定位/姿态模块及实际测量场景 | 先确认算法和测试方法；仿真与历史文档不能证明这些指标已达到。 |

本轮未确认有哪些板卡或仪器已经在你手中，因此只说明“任务需要什么”，不将硬件写成已缺失或已具备。

### 本地证据

- [Windows 工具探查](docs/zh-CN/本机Windows工具.json)：PATH、安装记录、CST 文件、Visual Studio C++ 组件探查。
- [项目虚拟环境导入探查](docs/zh-CN/项目虚拟环境.json)、[安装记录](docs/zh-CN/虚拟环境安装记录.json)、[本次验证](docs/zh-CN/虚拟环境验证.json)：以当前 `.venv` 为准。
- [之前 Codex Python 探查](docs/zh-CN/本机Python环境.json)：历史环境，不能套用于当前项目 `.venv`。
- [MATLAB 探查](docs/zh-CN/本机MATLAB环境.json)：实际版本、工具箱、函数路径和最小模型对象创建；不包含仓库求解结果。
- [固件实现与验证盘点](docs/zh-CN/firmware/实现与验证盘点.md)、[GUI 实际测试记录](docs/zh-CN/firmware/本次检查记录.md)。

以上分类区分环境能力和任务完成证据。下一轮可以先从 MATLAB 模型核对、Python 离线逻辑及文档状态统一开始；完整工程验证须补齐对应工具和输入。

## 📡 Overview<br>📡 概述

The AERIS-10 project aims to democratize radar technology by providing a fully open-source, modular, and hackable radar system. Whether you're a university researcher, a drone startup, or an advanced maker, AERIS-10 offers a platform for experimenting with beamforming, pulse compression, Doppler processing, and target tracking.<br>
AERIS-10 项目希望通过完全开源、模块化、可供修改的雷达系统，让更多人接触雷达技术。大学研究人员、无人机初创企业和高级创客可以用这个平台试验波束成形、脉冲压缩、多普勒处理和目标跟踪。

## 🔬 Key Features<br>🔬 主要功能

- **Open Source Hardware & Software** - Complete schematics, PCB layouts, firmware, and software available<br>
  **开源硬件和软件**：原文称提供完整的原理图、PCB 布局、固件和软件。
- **Dual Version Availability**:<br>
  **提供两个版本**：
  - **AERIS-10N (Nexus)**: 3km range with 8x16 patch antenna array<br>
    **AERIS-10N（Nexus）**：采用 8×16 贴片天线阵列，标称探测距离 3 km。
  - **AERIS-10E (Extended)**: 20km range with 32x16 dielectric-filled slotted waveguide array<br>
    **AERIS-10E（Extended）**：采用 32×16 介质填充缝隙波导阵列，标称探测距离 20 km。
- **Full Electronic Beam Steering** - ±45° electronic steering in elevation and azimuth<br>
  **全电子波束转向**：俯仰和方位方向均为 ±45°。
- **Advanced Signal Processing** - On-board FPGA handles pulse compression, Doppler FFT, MTI, and CFAR<br>
  **高级信号处理**：板载 FPGA 完成脉冲压缩、多普勒 FFT、MTI 和 CFAR。
- **Python GUI** - User-friendly interface with map integration<br>
  **Python 图形界面**：提供集成地图的用户界面。
- **GPS/IMU Integration** - Real-time position and attitude correction<br>
  **GPS/IMU 集成**：实时位置与姿态修正。
- **Modular Design** - Separate power management, frequency synthesis, and RF boards<br>
  **模块化设计**：独立的电源管理、频率合成和射频电路板。

## 🏗️ System Architecture<br>🏗️ 系统架构

![AERIS-10 System Diagram](https://raw.githubusercontent.com/NawfalMotii79/PLFM_RADAR/main/8_Utils/RADAR_V6_V2.png)

### Hardware Components<br>硬件组成

The AERIS-10 main sub-systems are:<br>
AERIS-10 的主要子系统如下：

- **Power Management Board** - Supplies all necessary voltage levels to the electronics components with proper filtering and sequencing (sequencing ensured by the microcontroller)<br>
  **电源管理板**：为各电子元件提供所需电压，并进行适当滤波和时序控制；时序由微控制器保证。

- **Frequency Synthesizer Board** - Uses a high-performance Low Jitter Clock Generator (AD9523-1) that supplies phase-aligned clock references for:<br>
  **频率合成板**：采用高性能、低抖动时钟发生器 AD9523-1，为以下器件提供相位对齐的参考时钟：
  - RX and TX Frequency Synthesizers (ADF4382)<br>
    接收和发射频率合成器（ADF4382）。
  - DAC<br>
    数模转换器（DAC）。
  - ADC<br>
    模数转换器（ADC）。
  - FPGA<br>
    现场可编程门阵列（FPGA）。

- **Main Board** containing:<br>
  **主板**包含以下部分：
  - **DAC** - Generates the RADAR Chirps<br>
    **DAC**：产生雷达线性调频信号。
  - **2x Microwave Mixers (LTC5552)** - For up-conversion and IF-down-conversion<br>
    **两个 LTC5552 微波混频器**：完成上变频和中频下变频。
  - **4x 4-Channel Phase Shifters (ADAR1000)** - For RX and TX chain beamforming<br>
    **四个四通道 ADAR1000 移相器**：完成接收和发射链路波束成形。
  - **16x Front End Chips (ADTR1107)** - Used for both Low Noise Amplifying (RX) and Power Amplifying (TX) stages<br>
    **十六个 ADTR1107 前端芯片**：兼用于接收链低噪声放大和发射链功率放大。
  - **XC7A50T FPGA** - Handles RADAR Signal Processing on the upstream FTG256 board:<br>
    **XC7A50T FPGA**：位于上游 FTG256 板，负责以下雷达信号处理功能：
    - PLFM Chirps generation via the DAC<br>
      通过 DAC 产生 PLFM 线性调频信号。
    - Raw ADC data read<br>
      读取 ADC 原始数据。
    - Hybrid Automatic Gain Control (AGC) — cross-layer FPGA/STM32/GUI loop<br>
      混合自动增益控制（AGC）：跨 FPGA/STM32/GUI 的闭环。
    - I/Q Baseband Down-Conversion<br>
      I/Q 基带下变频。
    - Decimation<br>
      抽取。
    - Filtering<br>
      滤波。
    - Forward FFT<br>
      正向 FFT。
    - Pulse Compression<br>
      脉冲压缩。
    - Doppler, MTI and CFAR processing<br>
      多普勒、MTI 和 CFAR 处理。
    - USB Interface<br>
      USB 接口。
  - **STM32F746xx Microcontroller** - Used for:<br>
    **STM32F746xx 微控制器**负责：
    - Power-up and power-down sequencing (see Power Management Excel File)<br>
      上电与断电时序（参见电源管理 Excel 表）。
    - FPGA communication<br>
      与 FPGA 通信。
    - Setup and Interface with:<br>
      以下器件的配置和接口连接：
      - Clock Generator (AD9523-1)<br>
        时钟发生器（AD9523-1）。
      - 2x Frequency Synthesizers (ADF4382)<br>
        两个频率合成器（ADF4382）。
      - 4x 4-Channel Phase Shifters (ADAR1000) for RADAR pulse sequencing<br>
        四个四通道 ADAR1000 移相器，用于雷达脉冲时序。
      - 2x ADS7830 8-channel I²C ADCs (Main Board, U88 @ 0x48 / U89 @ 0x4A) for 16x Idq measurement, one per PA channel, each sensed through a 5 mΩ shunt on the PA board and an INA241A3 current-sense amplifier (x50) on the Main Board<br>
        两个八通道 I²C ADC ADS7830：主板 U88 地址 0x48、U89 地址 0x4A，测量 16 个功放通道的静态电流 Idq。每个通道使用功放板上的 5 mΩ 分流电阻和主板上的 INA241A3 电流检测放大器（50 倍增益）。
      - 2x DAC5578 8-channel I²C DACs (Main Board, U7 @ 0x48 / U69 @ 0x49) for 16x Vg control, one per PA channel; closed-loop calibrated at boot to the target Idq<br>
        两个八通道 I²C DAC DAC5578：主板 U7 地址 0x48、U69 地址 0x49，控制 16 个功放通道的栅极电压 Vg；启动时通过闭环校准到目标 Idq。
      - GPS module (UM982) for GUI map centering and per-detection position tagging<br>
        UM982 GPS 模块：用于界面地图居中及每次检测的位置标记。
      - GY-85 IMU for pitch/roll correction of target coordinates<br>
        GY-85 IMU：修正目标坐标中的俯仰和横滚。
      - BMP180 Barometer<br>
        BMP180 气压计。
      - Stepper Motor<br>
        步进电机。
      - 1x ADS7830 8-channel I²C ADC (Main Board, U10) reading 8 thermistors for thermal monitoring; a single GPIO (EN_DIS_COOLING) switches the cooling fans on when any channel exceeds the threshold<br>
        一个八通道 I²C ADC ADS7830（主板 U10）：读取八个热敏电阻进行温度监测；任一通道超过阈值时，通过单个 GPIO `EN_DIS_COOLING` 打开冷却风扇。
      - RF switches<br>
        射频开关。

- **16x Power Amplifier Boards** - Used only for AERIS-10E version, featuring 10Watt QPA2962 GaN amplifier for extended range<br>
  **十六块功率放大器板**：仅用于 AERIS-10E，采用 10 W 的 QPA2962 GaN 放大器以延长探测距离。

- **Antenna Arrays**:<br>
  **天线阵列**：
  - **AERIS-10N (Nexus)** - 8x16 patch antenna array<br>
    **AERIS-10N（Nexus）**：8×16 贴片天线阵列。
  - **AERIS-10X (Extended)** - 32x16 dielectric-filled slotted waveguide antenna array<br>
    **AERIS-10X（Extended）**：32×16 介质填充缝隙波导天线阵列。译注：原文此处使用 X，与前文 E 的命名不一致。

- **Miscellaneous Components**:<br>
  **其他组件**：
  - Slip-Ring<br>
    滑环。
  - Stepper Motor and drivers<br>
    步进电机及其驱动器。
  - Cooling Fans<br>
    冷却风扇。
  - Enclosure<br>
    外壳。

### Processing Pipeline<br>处理流程

1. **Waveform Generation** - DAC creates LFM chirps<br>
   **波形生成**：DAC 产生 LFM 线性调频信号。
2. **Up/Down Conversion** - LTC5552 mixers handle frequency translation<br>
   **上下变频**：LTC5552 混频器完成频率转换。
3. **Beam Steering** - ADAR1000 phase shifters control 16 elements<br>
   **波束转向**：ADAR1000 移相器控制 16 个阵元。
4. **Signal Processing (FPGA)**:<br>
   **FPGA 信号处理**：
   - Raw ADC data capture<br>
     采集 ADC 原始数据。
   - I/Q baseband down-conversion<br>
     I/Q 基带下变频。
   - Decimation & filtering (CIC/FIR)<br>
     抽取与滤波（CIC/FIR）。
   - Pulse compression<br>
     脉冲压缩。
   - Doppler FFT processing<br>
     多普勒 FFT 处理。
   - MTI & CFAR detection<br>
     MTI 与 CFAR 检测。
5. **System Management (STM32)**:<br>
   **STM32 系统管理**：
   - Power sequencing<br>
     电源时序。
   - Peripheral configuration<br>
     外设配置。
   - GPS/IMU integration<br>
     GPS/IMU 集成。
   - Stepper motor control<br>
     步进电机控制。
6. **Visualization (Python GUI)**:<br>
   **Python GUI 可视化**：
   - Real-time target plotting<br>
     实时目标绘图。
   - Map integration<br>
     地图集成。
   - Radar control interface<br>
     雷达控制界面。

![AERIS-10 Dashboard](https://raw.githubusercontent.com/NawfalMotii79/PLFM_RADAR/main/8_Utils/GUI_V6.gif)
<!-- V6 GIF removed — V6 is deprecated. V65 Tk and V7 PyQt6 are the active GUIs. -->

译注：原文展示 V6 界面动画，但上方 HTML 注释写明 V6 已弃用，当前使用 V65 Tk 和 V7 PyQt6。本地动画见 `9_Firmware/9_3_GUI/GUI_V6.gif`。

## 📊 Technical Specifications<br>📊 技术规格

| Parameter<br>参数 | AERIS-10N (Nexus)<br>AERIS-10N（Nexus） | AERIS-10X (Extended)<br>AERIS-10X（Extended） |
|-----------|-------------------|----------------------|
| **Frequency**<br>**频率** | 10.5 GHz | 10.5 GHz |
| **Max Range**<br>**最大距离** | 3 km | 20 km |
| **Antenna**<br>**天线** | 8x16 Patch Array<br>8×16 贴片阵列 | 32x16 Slotted Waveguide<br>32×16 缝隙波导 |
| **Beam Steering**<br>**波束转向** | Electronic (±45°)<br>电子扫描（±45°） | Electronic (±45°)<br>电子扫描（±45°） |
| **Mechanical Scan**<br>**机械扫描** | 360° (stepper motor)<br>360°（步进电机） | 360° (stepper motor)<br>360°（步进电机） |
| **Output Power**<br>**输出功率** | ~1W×16<br>约 1 W×16 | 10W×16 (GaN amplifier)<br>10 W×16（GaN 放大器） |
| **Processing**<br>**处理** | FPGA + STM32 | FPGA + STM32 |

## 🚀 Getting Started<br>🚀 入门

### 🧹 Repository File Placement Policy<br>🧹 仓库文件存放规则

To keep the repository root clean and make artifacts easy to find, place generated files in the following locations:<br>
为保持仓库根目录整洁并便于查找产物，生成文件应放在以下位置：

- **Published reports (tracked, GitHub Pages):** `docs/`<br>
  **已发布报告（纳入版本控制，用于 GitHub Pages）**：`docs/`。
  - Example: `docs/AERIS_Simulation_Report_v2.pdf`<br>
    例如：`docs/AERIS_Simulation_Report_v2.pdf`。
- **Simulation-generated outputs (local, gitignored):** `5_Simulations/generated/`<br>
  **仿真生成结果（本地文件，由 Git 忽略）**：`5_Simulations/generated/`。
  - Plots, scenario outputs, temporary analysis directories<br>
    图表、场景输出和临时分析目录。
- **FPGA/Vivado generated artifacts (local, gitignored):** `9_Firmware/9_2_FPGA/reports/`<br>
  **FPGA/Vivado 生成产物（本地文件，由 Git 忽略）**：`9_Firmware/9_2_FPGA/reports/`。
  - VCD/VVP dumps, temporary CSVs, local report snapshots<br>
    VCD/VVP、临时 CSV 和本地报告快照。
- **Reusable FPGA automation scripts (tracked):** `9_Firmware/9_2_FPGA/scripts/`<br>
  **可复用 FPGA 自动化脚本（纳入版本控制）**：`9_Firmware/9_2_FPGA/scripts/`。
  - TCL flows, helper scripts used by build/bring-up<br>
    TCL 流程及构建、上板辅助脚本。

**Do not leave generated artifacts in the repository root.**<br>
**不要把生成产物留在仓库根目录。**

### Prerequisites<br>前置条件

- Basic understanding of radar principles<br>
  基本雷达原理知识。
- Experience with PCB assembly (for hardware build)<br>
  构建硬件时所需的 PCB 装配经验。
- Python 3.8+ for the GUI software<br>
  GUI 软件需要 Python 3.8+。译注：`pyproject.toml` 实际声明 `>=3.12`，要求不一致。
- FPGA development tools (Vivado) for signal processing modifications<br>
  修改信号处理时需要 Vivado 等 FPGA 开发工具。

### Hardware Assembly<br>硬件装配

1. **Order PCBs**: Production outputs are under `/4_Schematics and Boards Layout/4_7_Production Files`<br>
   **订购 PCB**：制造输出位于 `4_Schematics and Boards Layout/4_7_Production Files/`。
2. **Source Components**: BOM/CPL files are co-located under `/4_Schematics and Boards Layout/4_7_Production Files`<br>
   **采购元件**：BOM/CPL 与制造输出位于同一目录。
3. **Assembly**: Use the schematics in `/4_Schematics and Boards Layout/4_6_Schematics` together with the production outputs above; a standalone assembly guide is not currently tracked<br>
   **装配**：配合使用 `4_Schematics and Boards Layout/4_6_Schematics/` 中的原理图及上述制造文件；当前没有纳入版本控制的独立装配指南。
4. **Antenna**: Choose appropriate array files for your target variant<br>
   **天线**：按目标版本选择合适的阵列文件。
5. **Enclosure**: Mechanical drawings currently live in `/8_Utils/Mechanical_Drawings`<br>
   **外壳**：机械图纸当前位于 `8_Utils/Mechanical_Drawings/`。

## 📜 License<br>📜 许可证

This project is open-source but uses **different licenses for hardware and software** to ensure proper legal coverage.<br>
项目开源，但**硬件和软件采用不同许可证**，以覆盖各自需要。以下为原文说明的翻译；仓库实际文本见 [Licence 本地文本译文](docs/zh-CN/Licence原文译文.md)，本次没有核实其是否与官方版本一致。

### Hardware Documentation<br>硬件文档
The hardware design files—including:<br>
硬件设计文件包括：

- Schematics and PCB layouts (in `/4_Schematics and Boards Layout`)<br>
  原理图与 PCB 布局（位于 `4_Schematics and Boards Layout/`）。
- Bill of Materials (BOM) files<br>
  物料清单（BOM）。
- Gerber files and manufacturing outputs<br>
  Gerber 文件与制造输出。
- Mechanical drawings and enclosure designs<br>
  机械图纸与外壳设计。

are licensed under the **CERN Open Hardware Licence Version 2 – Permissive (CERN-OHL-P)** .<br>
上述文件采用 **CERN 开放硬件许可证第 2 版宽松型（CERN-OHL-P）**。

This is a hardware-specific license that:<br>
原文称，该硬件专用许可证具有以下特点：

- ✅ Clearly defines "Hardware," "Documentation," and "Products"<br>
  ✅ 明确界定“硬件”“文档”和“产品”。
- ✅ Includes explicit patent protection for contributors and users<br>
  ✅ 包含面向贡献者和用户的明确专利保护。
- ✅ Provides stronger liability limitations (important for high-power RF)<br>
  ✅ 提供更强的责任限制（与高功率射频相关）。
- ✅ Aligns with professional open-hardware standards (CERN, OSHWA)<br>
  ✅ 与 CERN、OSHWA 等开放硬件规范相符。

You may use, modify, and sell products based on these designs, provided you:<br>
原文称，可以使用、修改并销售基于这些设计的产品，条件如下：

- Maintain the original copyright notices<br>
  保留原版权声明。
- Distribute any modified designs under the same license<br>
  以同一许可证分发修改后的设计。
- Make your modifications available in Source format<br>
  以源文件形式提供修改。

### Software and Firmware<br>软件和固件
The software components—including:<br>
软件组件包括：

- FPGA code (VHDL/Verilog in `/9_Firmware`)<br>
  FPGA 代码（`9_Firmware/` 中的 VHDL/Verilog）。
- Microcontroller firmware (STM32)<br>
  微控制器固件（STM32）。
- Python GUI and utilities<br>
  Python GUI 与工具。

remain under the **MIT License** for maximum flexibility.<br>
上述组件继续采用 **MIT 许可证**，以保留较大使用灵活性。

### Full License Texts<br>完整许可证文本

- The complete CERN-OHL-P license text is in the `LICENSE` file<br>
  原文称完整 CERN-OHL-P 文本位于 `LICENSE` 文件。译注：本地实际文件名为 `Licence`，没有同名 `LICENSE` 文件。
- MIT license terms apply to software where not otherwise specified<br>
  软件在没有其他声明时适用 MIT 条款。

### Why This Change?<br>为什么更改许可证
Originally, the entire project used the MIT license. The community (special thanks to gmaynez!) pointed out that MIT lacks legal protections needed for physical hardware. The switch to CERN-OHL-P ensures the project is properly protected while maintaining the same permissive spirit.<br>
项目最初整体使用 MIT。社区（原文特别感谢 gmaynez）指出 MIT 缺少实体硬件所需的法律保护；原文称改用 CERN-OHL-P 可以在保留宽松精神的同时提供适当保护。

## 📚 Documentation<br>📚 文档

Comprehensive documentation is available in the `/docs` folder and served via GitHub Pages at [https://NawfalMotii79.github.io/PLFM_RADAR/docs/](https://NawfalMotii79.github.io/PLFM_RADAR/docs/):<br>
完整文档位于 `docs/`，原文提供的发布地址为 [GitHub Pages](https://NawfalMotii79.github.io/PLFM_RADAR/docs/)。

- [System Architecture](/docs/architecture.html)<br>
  [系统架构中文译文](docs/zh-CN/web/architecture.md)
- [Implementation Log](/docs/implementation-log.html)<br>
  [实施日志中文译文](docs/zh-CN/web/implementation-log.md)
- [Hardware Bring-Up Guide](/docs/bring-up.html)<br>
  [硬件上板指南中文译文](docs/zh-CN/web/bring-up.md)
- [Test Reports](/docs/reports.html)<br>
  [测试报告中文译文](docs/zh-CN/web/reports.md)
- [Release Notes](/docs/release-notes.html)<br>
  [发布说明中文译文](docs/zh-CN/web/release-notes.md)

## 🤝 Contributing<br>🤝 参与贡献

We welcome contributions! Please see our [Contributing Guidelines](/CONTRIBUTING.md) for details on repo layout, branch workflow, and basic PR checks.<br>
欢迎贡献。仓库布局、分支流程和基本 PR 检查见 [贡献指南中文译文](docs/zh-CN/CONTRIBUTING原文译文.md)。

Areas where help is especially appreciated:<br>
特别欢迎以下方向的帮助：

- **RF Engineers**: Review designs, optimize antenna performance<br>
  **射频工程师**：审查设计，优化天线性能。
- **FPGA Developers**: Optimize signal processing pipeline<br>
  **FPGA 开发者**：优化信号处理链。
- **Software Developers**: Enhance Python GUI and SDK<br>
  **软件开发者**：改进 Python GUI 和 SDK。
- **Beta Testers**: University researchers, drone startups, advanced makers<br>
  **测试参与者**：大学研究人员、无人机初创企业和高级创客。

## 📞 Contact & Collaboration<br>📞 联系与合作

I welcome serious inquiries from researchers, engineers, and potential collaborators. However, due to the high volume of interest in this project, please understand that I cannot guarantee a response to every message.<br>
作者欢迎研究人员、工程师及潜在合作方的认真咨询，但因关注人数较多，不能保证回复每条消息。

- **Technical questions or bug reports**: Please [open a GitHub issue](https://github.com/NawfalMotii79/PLFM_RADAR/issues) so the whole community can benefit from the discussion.<br>
  **技术问题和缺陷报告**：通过 [GitHub issue](https://github.com/NawfalMotii79/PLFM_RADAR/issues) 提出，便于整个社区参与讨论。
- **Collaboration, licensing, or business inquiries**: 📧 nawfal.motii.33 [at] gmail [dot] com<br>
  **合作、许可及商业咨询**：📧 `nawfal.motii.33 [at] gmail [dot] com`。

## 💰 Sponsors<br>💰 赞助

![PCBWay Sponsor Logo](https://raw.githubusercontent.com/NawfalMotii79/PLFM_RADAR/main/8_Utils/PCBWAY.jpg)

原文列出 PCBWay 赞助商标志，本地图片见 `8_Utils/PCBWAY.jpg`。

---

**Star ⭐ this repository if you're interested in open-source radar technology!**<br>
**如果对开源雷达技术感兴趣，请为仓库点星 ⭐。**

*Note: This is an active development project. Some features are still in progress. Check the issues page for known limitations and upcoming features.*<br>
*注意：项目仍在积极开发，一些功能尚未完成；已知限制和后续功能见 issue 页面。*

## 19,000 stars – Thank you<br>19,000 个星标：致谢

This project started in a small workshop in Morocco. Today, 19,000 engineers on GitHub have starred it.<br>
这个项目始于摩洛哥的一间小工作室。今天，GitHub 上已有 19,000 名工程师为它点星。译注：这是原作者的致谢文字，星标数量未作现时核实。

I am genuinely humbled.<br>
我深感荣幸。

**What this tells me:**<br>
**这让我看到：**

- Open source radar matters<br>
  开源雷达有价值。
- Affordable sensing is needed<br>
  人们需要可负担的感知技术。
- Engineers want to build, not just buy<br>
  工程师希望亲手构建，而不只是购买。

Thank you to everyone who starred, forked, opened issues, submitted PRs, and shared this project.<br>
感谢每一位点星、分叉、提出 issue、提交 PR 和分享项目的人。

The work continues.<br>
工作仍在继续。

**Nawfal Motii**
ABAC INDUSTRY
(http://www.abacindustry.com)
