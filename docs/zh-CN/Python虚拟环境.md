# 项目 Python 3.13 虚拟环境 / Project Python environment

项目根目录 `.venv` 已由本机系统 Python **3.13.14** 创建，`include-system-site-packages = false`。已通过 `sfw` 安装 37 个项目依赖包；环境中另有创建虚拟环境时提供的 pip。运行项目时明确使用 `.venv\Scripts\python.exe`。

The project uses `.venv`, created from the installed system Python 3.13.14. Host dependencies are installed in this environment. Use `.venv\Scripts\python.exe` for host software, analysis and tests; FPGA tools, MCU toolchains and native hardware drivers remain separate requirements.

## 依赖清单 / Dependencies

`requirements-local.txt` 引用现有 V65、V7 和 PyQt GUI 依赖，另含 pandas、pyserial、pytest、ruff、uv；`pyproject.toml` 的 dev 组同时参与安装。范围包括 NumPy、SciPy、matplotlib、HDF5、PyQt6/WebEngine、跟踪/聚类、CRC、USB Python 接口及测试工具。

`requirements-local.lock.txt` 保存本次 Windows x64、Python 3.13 环境的确切包版本，供同类环境复现。它不是跨操作系统的通用锁文件，不包含 Vivado、GCC/Make、Icarus、openEMS、CST 或 USB 原生驱动。

## 创建与安装 / Create and install

以下命令在项目根目录的 PowerShell 执行。本机 `.venv` 已创建，日常运行无需重建，也无需激活。

```powershell
# 仅首次创建时执行 / First-time creation only
python3.13 -m venv .venv

# 使用本机已有 uv，并经 sfw 安装 / Install through sfw
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
& .\.tools\sfw.exe uv pip install --python .venv/Scripts/python.exe --no-python-downloads -r requirements-local.txt --group dev --link-mode=copy
```

`.tools/sfw.exe` 按 [Socket 官方手动安装方式](https://docs.socket.dev/docs/socket-firewall-free)，从 [v1.15.4 发布页](https://github.com/SocketDev/sfw-free/releases/tag/v1.15.4) 下载 Windows x86_64 二进制，SHA256 已与发布资产 digest 核对。来源记录见 [sfw 安装来源](sfw安装来源.json)。本机已有 `uv.exe` 在 `$env:USERPROFILE\.local\bin`，命令只调整当前 PowerShell 会话的 PATH。首次实际安装未指定 `--link-mode=copy`，uv 因缓存位于 C 盘而环境位于 D 盘，自动回退到复制并成功完成；上述复现命令显式使用复制。

安装完成后，可使用环境自身的 uv 按版本快照复现：

```powershell
$env:Path = "$PWD\.venv\Scripts;$env:Path"
& .\.tools\sfw.exe uv pip install --python .venv/Scripts/python.exe --no-python-downloads -r requirements-local.lock.txt --link-mode=copy
```

`.venv/` 和 `.tools/` 已加入 `.gitignore`，包文件与本机工具二进制不纳入版本控制。

## 运行 / Run

```powershell
# V65 离线演示 / V65 offline demo
& .\.venv\Scripts\python.exe .\9_Firmware\9_3_GUI\GUI_V65_Tk.py --demo

# V7 界面 / V7 dashboard
& .\.venv\Scripts\python.exe .\9_Firmware\9_3_GUI\GUI_V7_PyQt.py

# 依赖一致性与 GUI 测试 / Dependencies and GUI tests
& .\.venv\Scripts\uv.exe pip check --python .venv/Scripts/python.exe
& .\.venv\Scripts\python.exe -B -m pytest .\9_Firmware\9_3_GUI\test_GUI_V65_Tk.py .\9_Firmware\9_3_GUI\test_v7.py -q --tb=short -p no:cacheprovider
```

V65 离线演示无需板卡。V7 地图使用在线资源，其离线可用性需另行确认。实时 USB 模式仍需对应设备及后端：FT2232H 使用 pyftdi/libusb，FT601 使用 ftd3xx/D3XX；后者未列入当前通用 GUI 依赖清单。

## 验证记录 / Verification

实际结果见 [虚拟环境安装记录](虚拟环境安装记录.json)、[模块导入探查](项目虚拟环境.json)、[虚拟环境验证](虚拟环境验证.json)。安装成功、可导入或可创建隐藏 Qt 应用，不等同于全部 GUI 功能、完整 CI 或真实硬件验证通过。

本次 `uv pip check` 检查环境中的 38 个发行包，依赖兼容；Qt 隐藏应用初始化和 WebEngine 导入通过，pytest/ruff 可运行。GUI pytest 实际为 **171 passed、3 failed、0 skipped、退出码 1**。三个失败仍为 `TestReplayEngineRawIQ` 清理临时 `.npy` 时的 Windows `WinError 32`，本轮没有修改回放或测试源码。与之前 Codex Python 环境相比，原来缺依赖导致的 5 项跳过本次已执行。
