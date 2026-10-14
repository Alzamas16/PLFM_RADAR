# AERIS-10 FPGA 约束文件

- 源路径：`9_Firmware/9_2_FPGA/constraints/README.md`；SHA256：`cbf5b7c2907e6d7615aa3e2070b60b2d1f71d880f825a909b61c5b0c3e8f8fc6`。

原文：`9_Firmware/9_2_FPGA/constraints/README.md`。全文译文忠实保留原文，包括相互矛盾的默认值表述；文末列出本次源码核对结果。

## 四个目标

| 文件 | 器件 | 封装 | 用途 |
|---|---|---|---|
| `xc7a50t_ftg256.xdc` | XC7A50T-2FTG256I | FTG256（256 球 BGA） | 50T 量产板 |
| `xc7a200t_fbg484.xdc` | XC7A200T-2FBG484I | FBG484（484 球 BGA） | 200T 高配开发板 |
| `te0712_te0701_minimal.xdc` | XC7A200T-2FBG484I | FBG484（484 球 BGA） | Trenz 开发分离目标（最小时钟/复位 + LED/状态） |
| `te0713_te0701_minimal.xdc` | XC7A200T-2FBG484C | FBG484（484 球 BGA） | Trenz 备用 SoM 目标（最小时钟 + FMC 状态输出） |

## 为什么有四个文件

50T 量产板使用 FTG256 封装的 XC7A50T。200T 高配开发板使用 XC7A200T，提供更多逻辑、BRAM 和 DSP 资源。两种器件的封装和引脚名称完全不同，因此各自需要约束文件。

Trenz TE0712/TE0701 路径使用与 200T 相同的 FPGA 型号，但板级引脚分配和外设不同。开发目标被拆分为独立的顶层封装 `radar_system_top_te0712_dev.v` 和最小约束文件，以避免调试时意外混入量产引脚分配。

Trenz TE0713/TE0701 路径用于 TE0712 交货周期过长的情况。TE0713 使用 XC7A200T-2FBG484C（商业温度等级），需要独立的时钟映射，因此具有专用开发顶层和 XDC。

## USB 接口架构（USB_MODE）

雷达系统支持两种 USB 数据接口，在**编译时**通过 `radar_system_top.v` 中的 `USB_MODE` 参数选择：

| USB_MODE | 接口 | 总线宽度 | 时钟速度 | 板级目标 |
|---|---|---|---|---|
| 0 | FT601（USB 3.0） | 32 位 | 100 MHz | 200T 高配开发板 |
| 1（默认） | FT2232H（USB 2.0） | 8 位 | 60 MHz | 50T 量产板 |

### USB_MODE 的工作方式

`radar_system_top.v` 包含 Verilog `generate` 块，根据 `USB_MODE` 参数只实例化一个 USB 接口模块：

```verilog
generate
if (USB_MODE == 0) begin : gen_ft601
    usb_data_interface usb_inst (...)         // FT601，32 位
    // FT2232H 端口连接到非活动状态
end else begin : gen_ft2232h
    usb_data_interface_ft2232h usb_inst (...) // FT2232H，8 位
    // FT601 端口连接到非活动状态
end
endgenerate
```

两个接口共享相同的内部雷达数据总线和主机命令接口。未使用接口的 I/O 引脚连接到安全的非活动状态：低有效信号置高，高有效信号置低，双向总线置为高阻态。

### 各板级目标如何传递 USB_MODE

通过**封装模块**覆盖默认值：

- **50T 量产板**：`radar_system_top_50t.v` 使用 `.USB_MODE(1)` 实例化核心，将 FT2232H 的 60 MHz `CLKOUT` 映射到共用端口 `ft601_clk_in`。FT601 输入固定为非活动状态，输出接到 `_nc` 导线。

  ```verilog
  // radar_system_top_50t.v 中：
  radar_system_top #(
      .USB_MODE(1)
  ) u_core ( ... );
  ```

- **200T 开发板**：直接使用 `radar_system_top` 作为顶层模块。由于量产板是主要目标，`USB_MODE` 默认为 `1`（FT2232H）。构建 FT601 时以 `.USB_MODE(0)` 覆盖。

### 各 USB 接口的 RTL 文件

| 文件 | 用途 |
|---|---|
| `usb_data_interface.v` | FT601 USB 3.0 模块（32 位，USB_MODE=0） |
| `usb_data_interface_ft2232h.v` | FT2232H USB 2.0 模块（8 位，USB_MODE=1） |
| `radar_system_top.v` | 包含 USB_MODE generate 块的核心模块 |
| `radar_system_top_50t.v` | 50T 封装：设 USB_MODE=1，并固定未使用的 FT601 端口状态 |

### FT2232H 引脚映射（50T，Bank 35，VCCO=3.3V）

U6（FT2232HQ）与 U42（XC7A50T）之间均直接连接。仅使用通道 A（245 同步 FIFO 模式），通道 B 未连接。

| 信号 | FT2232H 引脚 | FPGA 焊球 | 方向 |
|---|---|---|---|
| FT_D[7:0] | ADBUS[7:0] | K1,J3,H3,G4,F2,D1,C3,C1 | 双向 |
| FT_RXF# | ACBUS0 | A2 | 输入（FIFO 非空） |
| FT_TXE# | ACBUS1 | B2 | 输入（FIFO 非满） |
| FT_RD# | ACBUS2 | A3 | 输出（读选通） |
| FT_WR# | ACBUS3 | A4 | 输出（写选通） |
| FT_SIWUA | ACBUS4 | A5 | 输出（立即发送） |
| FT_CLKOUT | ACBUS5 | C4（MRCC） | 输入（60 MHz 时钟） |
| FT_OE# | ACBUS6 | B7 | 输出（总线方向） |

## Bank 电压分配

### XC7A50T-FTG256（50T 量产板）

| Bank | VCCO | 信号 |
|---|---|---|
| 0 | 3.3V | JTAG、Flash CS |
| 14 | 3.3V | ADC LVDS（LVDS_33）、SPI Flash |
| 15 | 3.3V | DAC、时钟、STM32 3.3V SPI、DIG 总线 |
| 34 | 1.8V | ADAR1000 控制、SPI 1.8V 侧 |
| 35 | 3.3V | FT2232H USB 2.0（8 位数据 + 控制，15 个信号） |

### XC7A200T-FBG484（200T 高配开发板）

| Bank | VCCO | 已用/可用 | 信号 |
|---|---|---|---|
| 13 | 3.3V | 17/35 | 超出主 Bank 容量的调试信号（多普勒单元、距离单元、状态） |
| 14 | 2.5V | 19/50 | ADC LVDS_25 + DIFF_TERM、ADC 掉电控制 |
| 15 | 3.3V | 27/50 | 系统时钟（100M、120M）、DAC、RF、STM32 3.3V SPI、DIG 总线 |
| 16 | 3.3V | 50/50 | FT601 USB 3.0（32 位数据 + 字节使能 + 控制） |
| 34 | 1.8V | 19/50 | ADAR1000 波束形成器控制、SPI 1.8V 侧 |
| 35 | 3.3V | 50/50 | 状态输出（波束位置、chirp、多普勒数据总线） |

## 目标间的信号差异

| 信号 | 50T 量产板（FTG256） | 200T 开发板（FBG484） |
|---|---|---|
| USB 接口 | FT2232H USB 2.0（8 位，Bank 35） | FT601 USB 3.0（32 位，Bank 16） |
| USB_MODE | 1（通过 `radar_system_top_50t` 封装） | 0（`radar_system_top` 默认值） |
| USB 时钟 | FT2232H CLKOUT 输出 60 MHz | FT601 输出 100 MHz |
| `dac_clk` | 未连接（DAC 由 AD9523 直接提供时钟） | 已布线，由 FPGA 驱动 DAC |
| `ft601_be` 宽度 | 不适用（FT601 未使用，端口固定） | `[3:0]`（RTL 已更新） |
| ADC LVDS 标准 | LVDS_33（3.3V Bank） | LVDS_25（2.5V Bank，质量更好） |
| 状态/调试输出 | 无物理引脚（已注释） | 全部布线到 Bank 35 + 13 |

## 如何构建

### 快速参考

```bash
# 在 FPGA 源目录（9_Firmware/9_2_FPGA）运行：

# 50T 量产构建（FT2232H，USB_MODE=1）：
vivado -mode batch -source scripts/50t/build_50t.tcl 2>&1 | tee build_50t/vivado.log

# 200T 开发构建（FT601，USB_MODE=0）：
vivado -mode batch -source scripts/200t/build_200t.tcl \
  -log build/build.log -journal build/build.jou
```

构建脚本自动选择正确的顶层模块和约束：

| 构建脚本 | 顶层模块 | 约束 | USB_MODE |
|---|---|---|---|
| `scripts/50t/build_50t.tcl` | `radar_system_top_50t` | `xc7a50t_ftg256.xdc` | 1（FT2232H） |
| `scripts/200t/build_200t.tcl` | `radar_system_top` | `xc7a200t_fbg484.xdc` | 0（FT601） |

**无需**手动设置 `USB_MODE`。顶层模块选择负责处理：

- `radar_system_top_50t` 内部强制 USB_MODE=1。
- `radar_system_top` 默认 USB_MODE=1（FT2232H，量产默认值）。

## 如何在 Vivado 中选择约束

Vivado 工程中同一时刻应只启用一个目标 XDC：

1. 将两个文件添加到工程：`File > Add Sources > Add Constraints`。
2. 在 Sources 面板中，右击不需要的 XDC，选择 `Set File Properties > Enabled = false`，或将其从活动约束集中移除。
3. 也可以建立两个独立约束集并在它们之间切换。

对于基于 Tcl 的流程：

```tcl
# 量产目标：
read_xdc constraints/xc7a200t_fbg484.xdc

# 上游目标：
read_xdc constraints/xc7a50t_ftg256.xdc

# Trenz TE0712/TE0701 分离目标：
read_xdc constraints/te0712_te0701_minimal.xdc

# Trenz TE0713/TE0701 分离目标：
read_xdc constraints/te0713_te0701_minimal.xdc
```

## 各目标的顶层模块

| 目标 | 顶层模块 | USB_MODE | USB 接口 | 说明 |
|---|---|---|---|---|
| 50T 量产板（FTG256） | `radar_system_top_50t` | 1 | FT2232H（8 位） | 封装设 USB_MODE=1，并固定 FT601 端口 |
| 200T 开发板（FBG484） | `radar_system_top` | 0（覆盖） | FT601（32 位） | 构建脚本覆盖默认 USB_MODE=1 |
| Trenz TE0712/TE0701 | `radar_system_top_te0712_dev` | 0（覆盖） | FT601（32 位） | 最小上电调试封装 |
| Trenz TE0713/TE0701 | `radar_system_top_te0713_dev` | 0（覆盖） | FT601（32 位） | 备用 SoM 封装 |

## Trenz 分离状态

- `constraints/te0712_te0701_minimal.xdc` 当前包含原文标为已验证的 TE0712 引脚：
  - `clk_100m` → `R4`（TE0712 `CLK1B[0]`，50 MHz 源）。
  - `reset_n` → `T3`（TE0712 复位引脚）。
- `user_led` 和 `system_status` 现通过 TE0712 B16 封装引脚映射到 TE0701 FMC LA 线路；这是 GPIO 导出路径，并非 TE0701 板载 LED D1..D8。
- 引脚分配完成后已移除临时的 `NSTD-1`/`UCIO-1` 严重级别降级。

### 当前 GPIO 导出映射

| 端口 | TE0712 封装引脚 | TE0712 网络 | TE0701 FMC 网络 |
|---|---|---|---|
| `user_led[0]` | `A19` | `B16_L17_N` | `FMC_LA14_N` |
| `user_led[1]` | `A18` | `B16_L17_P` | `FMC_LA14_P` |
| `user_led[2]` | `F20` | `B16_L18_N` | `FMC_LA13_N` |
| `user_led[3]` | `F19` | `B16_L18_P` | `FMC_LA13_P` |
| `system_status[0]` | `F18` | `B16_L15_P` | `FMC_LA5_N` |
| `system_status[1]` | `E18` | `B16_L15_N` | `FMC_LA5_P` |
| `system_status[2]` | `C22` | `B16_L20_P` | `FMC_LA6_N` |
| `system_status[3]` | `B22` | `B16_L20_N` | `FMC_LA6_P` |

说明：最终硬件签核前，必须结合 TE0701 连接器方向和 I/O Planner 核对 FMC 方向及 N/P 标注。

## Trenz 批处理构建

使用分离开发目标专用脚本：

```bash
vivado -mode batch -source scripts/build_te0712_dev.tcl

# TE0713/TE0701 目标
vivado -mode batch -source scripts/build_te0713_dev.tcl
```

输出：

- 工程目录：`vivado_te0712_dev/`。
- 报告：`vivado_te0712_dev/reports/`。
- 顶层模块：`radar_system_top_te0712_dev`。
- 约束文件：`constraints/te0712_te0701_minimal.xdc`。

TE0713 输出：

- 工程目录：`vivado_te0713_dev/`。
- 报告：`vivado_te0713_dev/reports/`。
- 顶层模块：`radar_system_top_te0713_dev`。
- 约束文件：`constraints/te0713_te0701_minimal.xdc`。

## 注意事项

- **USB_MODE 仅在编译时选择**，不能在运行时切换 USB 接口。各板级目标实际只连接一个 USB 芯片。
- 50T 量产构建必须使用 `radar_system_top_50t` 作为顶层。原文此处称，直接使用 `radar_system_top` 会默认选择 FT601（USB_MODE=0），而 50T 板上没有对应物理连接。
- 200T XDC 引脚分配是新 PCB 的**建议**方案，PCB 设计者应遵循此分配。
- 200T 的 Bank 16（FT601）已用满 50/50 引脚，没有扩展余量。
- 200T 的 Bank 35（状态/调试）也已用满 50/50。新增调试信号应使用 Bank 13 的空闲引脚，剩余 18 个。
- 50T 的 Bank 35 用于 FT2232H（15 个信号），剩余引脚可用于后续扩展。
- 时钟输入布置在 MRCC（跨区域时钟能力）引脚上，以确保正确接入时钟树。FT2232H CLKOUT（60 MHz）位于 C4（`IO_L12N_T1_MRCC_35`）。

## 本次盘点核对注

1. 源码 `radar_system_top.v` 第 145 行默认 `USB_MODE=1`，200T 构建脚本第 113 行使用 `set_property generic {USB_MODE=0} [current_fileset]`。原文差异表及注意事项中“默认 0”的表述与源码不一致。
2. 原文 Tcl 注释将 200T 标为“量产”、50T 标为“上游”，与文中板级分类不一致；本译文保留原注释，实际构建应按对应脚本、顶层和 XDC 确认。
3. 这些引脚、电压、跳线及 GPIO 映射未在本次盘点中进行板上验证。
