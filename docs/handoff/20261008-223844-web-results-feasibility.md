# 网页结果展示可行性评估

日期：2026-10-08（Asia/Shanghai）。

## 当前目标与范围

用户询问后续能否用网页展示项目结果。本轮完成源码层面的可行性评估，没有实施网页迁移，没有运行 GUI、性能测试或硬件验证。

## 已读取证据

- `9_Firmware/9_3_GUI/GUI_V7_PyQt.py`：PyQt6 桌面入口。
- `9_Firmware/9_3_GUI/v7/__init__.py`：模型、协议及处理模块与 Qt 界面导入分开；Qt 相关导入有 ImportError 降级。
- `9_Firmware/9_3_GUI/v7/models.py`：数据类，RadarTarget.to_dict 支持字典序列化。
- `9_Firmware/9_3_GUI/v7/processing.py`：NumPy 处理逻辑，不直接导入 PyQt6。
- `9_Firmware/9_3_GUI/v7/hardware.py`：复用 radar_protocol.py 的 FT2232H/FT601 协议与采集类。
- `9_Firmware/9_3_GUI/v7/workers.py`：采集与回放 worker 使用 QThread、pyqtSignal；迁移时需要适配。
- `9_Firmware/9_3_GUI/v7/map_widget.py`：Leaflet HTML/JavaScript 嵌入 QWebEngineView，通过 Qt bridge 通讯。
- `9_Firmware/9_3_GUI/v7/dashboard.py`：Qt 控件与 matplotlib Qt canvas 展示；本轮仅读取定义和关键调用位置，未全文审查。
- 官方资料核对：FastAPI WebSockets（https://fastapi.tiangolo.com/advanced/websockets/）；Plotly JavaScript Heatmaps（https://plotly.com/javascript/heatmaps/）。

## 关键判断与建议

- 网页展示具备源码基础；此为架构可行性判断，不代表已有可运行网页版本。
- 建议设备所在计算机运行 Python 采集/处理服务，浏览器负责图表和目标展示。
- 建议先做离线回放的只读展示，再接入实时采集；控制功能待展示链路验证后按需要迁移。
- 技术候选：FastAPI + WebSocket，Plotly.js 图表，提取现有 Leaflet 地图。并未决定最终选型。
- 高频数据应在后端处理并为显示适当降采样；性能和刷新率必须实测。

## 被否决方案及理由

- 不把浏览器直接 USB 连接作为首选：现有驱动与协议实现位于 Python，沿用本地采集服务更便于复用和验证。
- 不把现有嵌入式地图当成已存在的网页服务：setHtml 与 localhost base URL 不等同于 HTTP 服务。
- 不承诺直接替换全部 GUI：worker、控件、绘图与 Qt bridge 仍有耦合，需要迁移适配。
- 本轮不自行开始重写：用户当前提出可行性问题，尚未要求实施。

## 未决问题

- 首阶段需要离线报告、回放，还是实时仪表盘？
- 是否需要参数下发、启动/停止等控制功能？
- 数据规模、目标刷新率、同机或局域网访问，以及离线地图需求尚未明确。
- Qt 解耦、浏览器性能、驱动兼容性和实际硬件链路均未验证。

## 文件改动

仅新增本交接记录；应用行为未改变。工作区原有修改保持原样。