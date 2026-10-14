# AERIS-10 项目中文资料

已盘点本地仓库，并为容易直接读取的 Markdown、HTML 和说明类 TXT 建立中文译文。原文保留，译文中的历史测试结果、状态与性能仍代表原作者记录；本次核对结论单列于盘点报告。

本轮范围按你的最后指示执行：Markdown 与 HTML 为主，包含说明类 TXT 和纯文本 Licence；PDF、Word、Excel 暂停。范围缩小前已生成的 `reports/`、`tables/` 及 `表格中文对照.md` 保留但不属于本轮交付，不将其视作最终完整翻译。

## 建议阅读顺序

1. [项目盘点](项目盘点.md)：目录、现状、问题、验证边界。
   [Python 3.13 虚拟环境](Python虚拟环境.md)说明项目 `.venv`、依赖安装和运行方式；本次 GUI 测试为 171 通过、3 失败、无跳过。
   [本机工具与硬件条件](本机工具与硬件条件.md)明确哪些可用当前工具开展，哪些要补依赖，哪些需实物；主 README 同步包含全文。
2. [README 全文译文](README原文译文.md)：项目目标、结构、原文规格和入门说明。
3. [架构](web/architecture.md)与[固件实现盘点](firmware/实现与验证盘点.md)：理解硬件、处理链与软件边界。
4. [上板指南](web/bring-up.md)与[板卡到货记录表](web/board-day-worksheet.md)：了解原文规划的硬件验证步骤。
5. [网页文档审阅发现](web/审阅发现.md)与[本次检查记录](firmware/本次检查记录.md)：阅读状态矛盾与实际测试结果。

## Markdown 原文对应译文

| 英文原文 | 中文全文译文 |
|---|---|
| `README.md` | [项目说明](README原文译文.md) |
| `CONTRIBUTING.md` | [贡献指南](CONTRIBUTING原文译文.md) |
| `9_Firmware/9_2_FPGA/adc_clk_mmcm_integration.md` | [ADC 时钟 MMCM 集成](firmware/ADC时钟MMCM集成指南.md) |
| `9_Firmware/9_2_FPGA/constraints/README.md` | [FPGA 约束说明](firmware/FPGA约束文件说明.md) |
| `9_Firmware/9_2_FPGA/tb/cosim/real_data/hex/STALE_NOTICE.md` | [黄金参考 Hex 文件说明](firmware/黄金参考Hex文件说明.md) |
| `docs/artifacts/te0713-te0701-heartbeat-2026-03-21.md` | [TE0713 心跳产物](firmware/TE0713心跳上电调试产物.md) |
| `docs/artifacts/te0713-te0701-umft601x-dev-2026-03-21.md` | [FT601 开发比特流](firmware/FT601集成开发比特流.md) |

## HTML 原文对应译文

七个原网页均提供中文 Markdown 版本，并生成同名 `.html` 页面供浏览器阅读。

| 英文网页 | 中文 Markdown | 中文网页 |
|---|---|---|
| `docs/index.html` | [工程文档主页](web/index.md) | [网页](web/index.html) |
| `docs/architecture.html` | [架构与数据路径](web/architecture.md) | [网页](web/architecture.html) |
| `docs/implementation-log.html` | [实施日志](web/implementation-log.md) | [网页](web/implementation-log.html) |
| `docs/bring-up.html` | [上板调试](web/bring-up.md) | [网页](web/bring-up.html) |
| `docs/reports.html` | [测试报告](web/reports.md) | [网页](web/reports.html) |
| `docs/release-notes.html` | [发布说明](web/release-notes.md) | [网页](web/release-notes.html) |
| `docs/board-day-worksheet.html` | [板卡到货记录表](web/board-day-worksheet.md) | [网页](web/board-day-worksheet.html) |

## 其他容易读取的资料

- [GUI 版本说明](firmware/GUI版本说明.md)：`GUI_versions.txt` 全文翻译。
- [测试场景与匹配滤波参考数据](firmware/测试场景与匹配滤波参考数据.md)：两个说明类 TXT 的完整中文说明，保留原始数据值。
- [Licence 本地文本译文](Licence原文译文.md)：只翻译仓库文件实际文字，未校对官方许可证。
- [原文件清单](文件清单.csv)与[统计](盘点统计.json)：以本轮开始时的 Git 跟踪文件为基线，包含源文件 SHA256。

纯数据 TXT、CSV、HEX、MEM、程序代码、工程配置不做自然语言改写，避免改变可执行输入、协议与制造数据。未联网查询发布网站、GitHub CI、星标数量或官方许可文本。

## 译文同步检查

`翻译对应表.json` 记录原文、中文译文及原文 SHA256。源文更新后，可运行以下检查识别需要重新翻译的项目；检查本身不自动重译，也不改原文：

```powershell
& 'C:/Users/chx_g/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B docs/zh-CN/tools/check_translations.py
```

同步检查仅核对覆盖、文件指纹、围栏闭合及本地链接，不能代替逐句人工审阅或工程测试。原文不一致之处保留并加注，不在翻译中悄悄修正。
