# ADC 时钟 MMCM 集成指南

- 源路径：`9_Firmware/9_2_FPGA/adc_clk_mmcm_integration.md`；SHA256：`b0a17d092de56a81938fbec072bab2dcd90321c2f33883b7129a38d7b4695f85`。

原文：`9_Firmware/9_2_FPGA/adc_clk_mmcm_integration.md`。译文保留原文中的估计、建议及技术判断；其中数值和安全性论断不是本次验证结论。

## 概述

`adc_clk_mmcm.v` 是可以直接替换使用的 MMCME2_ADV 封装，用于以降低抖动的 PLL 环路替换 400 MHz ADC 数据时钟输出上的直接 BUFG。

### 当前时钟路径（Build 18）

```text
adc_dco_p/n → IBUFDS → BUFIO  （仅驱动 IDDR，延迟接近零）
                      → BUFG   （驱动所有 400 MHz 可编程逻辑）
```

### 新时钟路径（使用 MMCM）

```text
adc_dco_p/n → IBUFDS → BUFIO  （保持不变，仅驱动 IDDR）
                      → MMCME2 CLKIN1 → CLKOUT0 → BUFG  （400 MHz 可编程逻辑）
                                      → CLKFBOUT → BUFG → CLKFBIN （反馈）
```

## 预期时序改善

| 参数 | 之前（Build 18） | 之后（估计） |
|---|---|---|
| 输入抖动 | 50 ps | 50 ps（不变） |
| 输出抖动（MMCM） | 不适用 | 约 20–30 ps |
| 时钟不确定度 | 43 ps | 约 25 ps |
| WNS（建立时间，400 MHz） | +0.062 ns | 约 +0.08 至 +0.10 ns |
| WHS（保持时间，100 MHz） | +0.059 ns | 不变 |

改善来自 Vivado 时序分析中时钟不确定度的降低。MMCM 的 PLL 环路衰减输入抖动，因此 Vivado 从时序预算中扣除的不确定度更少。

## MMCM 配置

```text
CLKIN1          = 400 MHz（2.500 ns）
DIVCLK_DIVIDE   = 1
CLKFBOUT_MULT_F = 2.0 → VCO = 800 MHz
CLKOUT0_DIVIDE_F = 2.0 → 输出 = 400 MHz
BANDWIDTH       = HIGH（最大抖动滤波）
```

800 MHz 的 VCO 频率处于 Artix-7 -2 速度等级的范围内（600–1200 MHz）。

## 资源开销

| 资源 | 数量 | 说明 |
|---|---|---|
| MMCME2_ADV | 1 | 原为 0/10，现在为 1/10 |
| BUFG | +1（反馈） | 原为 4/32，现在为 5/32 |
| FF | 0 | 不增加可编程逻辑寄存器 |

## 集成步骤

### 步骤 1：修改 `ad9484_interface_400m.v`

用 `adc_clk_mmcm` 替换 BUFG 实例：

```verilog
// 删除这些行（65–69）：
//   BUFG bufg_dco (
//       .I(adc_dco),
//       .O(adc_dco_buffered)
//   );
//   assign adc_dco_bufg = adc_dco_buffered;

// 改为添加以下内容：
wire mmcm_locked;
wire adc_dco_mmcm;

adc_clk_mmcm mmcm_inst (
    .clk_in       (adc_dco),       // 来自 IBUFDS 输出
    .reset_n      (reset_n),
    .clk_400m_out (adc_dco_mmcm),  // 抑制抖动后的 400 MHz
    .mmcm_locked  (mmcm_locked)
);

// 所有可编程逻辑均使用 MMCM 输出
wire adc_dco_buffered = adc_dco_mmcm;
assign adc_dco_bufg = adc_dco_buffered;
```

### 步骤 2：根据 MMCM 锁定状态控制复位（推荐）

在 `ad9484_interface_400m.v` 中修改复位同步器，要求 MMCM 已锁定：

```verilog
// 将复位同步器的输入从以下内容：
//   always @(posedge adc_dco_buffered or negedge reset_n) begin
//       if (!reset_n)
//           reset_sync_400m <= 2'b00;
//       else
//           reset_sync_400m <= {reset_sync_400m[0], 1'b1};
//   end

// 改成：
wire reset_n_gated = reset_n & mmcm_locked;

always @(posedge adc_dco_buffered or negedge reset_n_gated) begin
    if (!reset_n_gated)
        reset_sync_400m <= 2'b00;
    else
        reset_sync_400m <= {reset_sync_400m[0], 1'b1};
end
```

这可确保 400 MHz 时钟域在 MMCM 锁定、时钟稳定前始终处于复位状态。若不这样处理，上电后最初约 10 µs 内（MMCM 锁定前）可能出现带毛刺的时钟边沿。

### 步骤 3：添加约束文件

将 `constraints/adc_clk_mmcm.xdc` 添加到 Vivado 工程。取消约束的注释，并按实际实例层级调整路径。

需要取消注释的关键约束：

1. `create_generated_clock`（或确认 Vivado 会自动创建）。
2. `adc_dco_p` 与 `clk_400m_mmcm` 之间的 `set_max_delay`。
3. `clk_400m_mmcm` 与其他时钟域之间的 `set_false_path`。
4. `LOCKED` 输出上的 `set_false_path`。

### 步骤 4：添加到构建脚本

在 Tcl 构建脚本中添加新源文件：

```tcl
read_verilog adc_clk_mmcm.v
read_xdc constraints/adc_clk_mmcm.xdc
```

### 步骤 5：验证

构建完成后：

1. 检查 `report_clocks`：应显示新的 MMCM 派生时钟。
2. 检查 `report_clock_interaction`：确认没有意外的跨域关系。
3. 检查 `adc_dco_p` / MMCM 时钟组的 WNS：应有所改善。
4. 硬件调试时在 ILA 中检查 MMCM 锁定状态。

## BUFIO 兼容性说明

此次修改**不影响**用于 IDDR 采集的 BUFIO 路径。BUFIO 只驱动 IOB 原语（IDDR），不能经过 MMCM。BUFIO 继续使用原始 IBUFDS 输出，插入延迟接近零；对于源同步 DDR 采集，这种方式是正确的。

从 BUFIO 时钟域到 BUFG 时钟域的重新寄存（`ad9484_interface_400m.v` 的第 105–108 行）现在由原始 `adc_dco_p` 时钟跨到 MMCM 派生时钟。由于两者频率一致，且 MMCM 锁定于输入时钟，原文认为这是安全的单寄存器传输。XDC 中的 `set_max_delay` 约束可确保 Vivado 对其验证。

## 仿真

在定义 `SIMULATION`（iverilog）时，模块直接透传时钟，并模拟约 4096 周期的锁定延迟。这与当前测试平台行为一致，无需修改任何测试平台。

## 回退

若要回退，只需恢复 `ad9484_interface_400m.v` 中原来的 BUFG，并从工程中移除 `adc_clk_mmcm.v` 与 `constraints/adc_clk_mmcm.xdc`。其他文件不受影响。

## 本次盘点核对注

当前源码已包含 `mmcm_inst`，200T 构建脚本已引用 MMCM 源文件与 XDC。上面的行号、资源量、抖动估计及跨域安全性说明属于原文内容；本次未执行 Vivado 或板上验证。
