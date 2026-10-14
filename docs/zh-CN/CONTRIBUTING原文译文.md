# PLFM_RADAR（AERIS-10）贡献指南

原文：`CONTRIBUTING.md`；指纹见 `源文件基线.json`。这是原文规则的全文翻译，不表示本轮已经通过这些检查。

感谢关注项目。本指南介绍如何提交修改供审查和合并。

## 开始参与

1. 分叉仓库，从 `develop` 创建主题分支。`main` 仅用于生产版本发布。
2. 不要将 Vivado 工程、位流、构建日志等生成结果纳入版本控制。

### 包安装安全要求

因供应链攻击风险，所有包安装必须使用 `sfw`（安全防火墙）前缀：

- Python：`sfw uv pip install <package>`，不得直接使用 pip。
- Node/JS：`sfw npm install <package>`。
- Rust/Cargo：`sfw cargo <command>`。

不得运行缺少 `sfw` 前缀的包安装命令。

## 仓库布局

| 路径 | 内容 |
|---|---|
| `4_Schematics and Boards Layout/` | KiCad 原理图、Gerber、BOM/CPL |
| `9_Firmware/9_1_Microcontroller/` | STM32 C/C++ 固件与单元测试 |
| `9_Firmware/9_2_FPGA/` | Verilog RTL、约束、测试平台、构建脚本 |
| `9_Firmware/9_3_GUI/` | Python 雷达界面（Tkinter/PyQt6）及命令行工具 |
| `9_Firmware/tests/cross_layer/` | Python 系统不变量与协议契约测试 |
| `docs/` | GitHub Pages 文档站点 |

## 代码标准与工具

Python GUI、脚本和测试用 `uv` 管理依赖，严格执行 `ruff` 检查；提交前运行 `uv run ruff check .`，用 `pytest` 测试。

Verilog 的 `radar_system_top.v` 是操作码、位宽、复位默认值和有效范围的唯一事实来源。测试平台必须包含对抗性验证，主动测试边界、竞争条件、非预期输入顺序及运行期间复位。仿真使用 `iverilog`。

MCU C/C++ 使用 `make test` 进行主机端单元测试（原文标注 cpputest）。每次增加代码，都必须验证跨模块、跨进程和跨芯片的系统不变量成立。

## AI 使用政策

允许使用 AI，但代码质量和控制必须由提交修改的维护者负责，而不能依赖代理。维护者对提交内容承担全部责任。

1. 人承担责任：提交工程师须像对自己编写的代码一样，对 AI 生成代码完全负责。每个 PR 都必须能够由人理解并解释。
2. 必须审查：不得提交未经阅读的 AI 原始输出。AI 代码与手写代码适用同样的审查标准。
3. 提交前运行完整 CI：所有 AI 辅助修改在提交前必须通过本地完整 CI，包括 lint、单元、回归和跨层测试。

## 运行测试套件

原文称 GitHub Actions 在每个 PR 上运行四项主要任务，推送前应在本地运行。

### Python 和静态检查

```bash
uv run ruff check .
cd 9_Firmware/9_3_GUI
uv run pytest test_GUI_V65_Tk.py test_v7.py -v
```

### FPGA 回归

```bash
cd 9_Firmware/9_2_FPGA
bash run_regression.sh
```

原文写为“五个阶段”，但括号实际列出六项：静态检查、修改模块、集成、信号处理、基础设施，以及 P0 对抗性测试。原文要求全部通过；译文保留这个计数差异。

### MCU 单元测试

```bash
cd 9_Firmware/9_1_Microcontroller/tests
make clean && make
```

### 跨层契约测试

```bash
uv run pytest 9_Firmware/tests/cross_layer/test_cross_layer_contract.py -v
```

## 合并前 CI 清单

所有 PR 必须通过 CI。

| 任务 | 检查内容 |
|---|---|
| `python-tests` | ruff 无错误，pytest 通过 |
| `mcu-tests` | make all 退出码为 0 |
| `fpga-regression` | run_regression.sh 退出码为 0 |
| `cross-layer-tests` | pytest 退出码为 0 |

## 重要说明

- 除非维护者明确要求，否则不提供旧版本兼容。
- FPGA RTL `radar_system_top.v` 是操作码、位宽、复位默认值和有效范围的唯一事实来源，其余各层必须与其一致。
- 必须开展对抗性测试，每个测试都要主动尝试破坏代码。
- 测试平台时序：在 `@(posedge clk)` 后使用阻塞赋值驱动被测设计输入之前，始终加入 `#1` 延迟。
- 预取 FIFO：`wr_full` 在写入 DEPTH+1 次之后置位，并非 DEPTH 次。

## 推送前清单

- [ ] `uv run ruff check .`，无静态检查错误。
- [ ] `uv run pytest test_GUI_V65_Tk.py test_v7.py -v`，全部通过。
- [ ] `cd 9_Firmware/9_2_FPGA && bash run_regression.sh`，原文所称全部 5 阶段通过。
- [ ] `cd 9_Firmware/9_1_Microcontroller/tests && make clean && make`，通过。
- [ ] `uv run pytest 9_Firmware/tests/cross_layer/test_cross_layer_contract.py`，通过。
- [ ] `git diff --check`，无空白字符问题。
- [ ] PR 目标分支为 `develop`。

## 问题反馈

通过 GitHub issue 提出问题，使讨论对所有人可见。
