# GUI 版本说明

- 源路径：`9_Firmware/9_3_GUI/GUI_versions.txt`；SHA256：`0c844ec7706fbc89cfcee5fe8e6d995e06d8b97114ef7fd3d9dbf634abfb692c`。

原文：`9_Firmware/9_3_GUI/GUI_versions.txt`。以下完整翻译原版本说明；原文重复的 V3 条目保持重复，V1 的空说明保持空。

```text
GUI_V1 ==> 
GUI_V2 ==> 添加 STM32 USB CDC
GUI_V3 ==> 在 STM32 USB 数据包中添加俯仰角，并对仰角进行俯仰修正
GUI_V3 ==> 添加 Google_Map、实时目标绘图、Chirp duration_2
GUI_V4 ==> 添加俯仰修正

GUI_V5 ==> 添加 Mercury 颜色

GUI_V6 ==> 添加 USB3 FT601 支持 [已弃用，被 V65/V7 取代]

GUI_V65_Tk ==> 板卡上电调试面板（FT2232H 读取、实时距离-多普勒热力图、CFAR 叠加、瀑布图、主机命令、HDF5 记录、回放、演示模式）
radar_protocol ==> 协议层（数据包解析、命令构建、FT2232H 连接、数据记录器、采集线程）
smoke_test ==> 板卡上电调试冒烟测试主机脚本（通过操作码 0x30 触发 FPGA 自检）
```

本次核对：当前还存在 `GUI_V7_PyQt.py` 与 `v7/` 模块目录，但原版本文件没有单独列出其条目；不在全文译文中自行补写版本历史。
