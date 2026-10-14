"""Verify the selected project interpreter; preserve logs and actual outcomes."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'docs/zh-CN/environment'
OUT.mkdir(parents=True, exist_ok=True)
python = sys.executable
env = os.environ.copy()
env['QT_QPA_PLATFORM'] = 'offscreen'
env['MPLBACKEND'] = 'Agg'
env['PYTHONDONTWRITEBYTECODE'] = '1'
env['PYTHONUTF8'] = '1'
commands = [
    ('dependency_check', [str(ROOT/'.venv/Scripts/uv.exe'), 'pip','check','--python',python], ROOT),
    ('pytest_version', [python,'-m','pytest','--version'], ROOT),
    ('ruff_version', [python,'-m','ruff','--version'], ROOT),
    ('qt_application', [python,'-c', 'from PyQt6.QtWidgets import QApplication; from PyQt6.QtWebEngineWidgets import QWebEngineView; app=QApplication([]); print("Qt application and WebEngine imports OK"); app.quit()'], ROOT),
    ('gui_tests', [python,'-B','-m','pytest','test_GUI_V65_Tk.py','test_v7.py','-q','--tb=short','-p','no:cacheprovider'], ROOT/'9_Firmware/9_3_GUI'),
]
results = []
for name, command, cwd in commands:
    result = subprocess.run(command,cwd=cwd,env=env,text=True,encoding='utf-8',errors='replace',capture_output=True)
    log = result.stdout+result.stderr
    (OUT/(name+'.log')).write_text(log,encoding='utf-8')
    results.append({'check':name,'command':command,'cwd':str(cwd),'exit_code':result.returncode,
                    'log':str((OUT/(name+'.log')).relative_to(ROOT)),'tail':log[-4000:]})
    print(name, 'exit_code=',result.returncode, flush=True)
record = {'date':'2026-10-08','python':python,'version':sys.version,'checks':results,
          'scope':'依赖一致性、工具可运行、隐藏 Qt 初始化和无硬件 GUI 测试；不代表真实USB/射频/完整CI'}
(ROOT/'docs/zh-CN/虚拟环境验证.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
