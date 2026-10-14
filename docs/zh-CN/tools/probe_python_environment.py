"""Read-only import probes. This is environment evidence, not a project test."""
import importlib
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='docs/zh-CN/本机Python环境.json')
parser.add_argument('--label', default='Codex bundled Python')
args = parser.parse_args()
results = {}
for name in ['numpy','matplotlib','pandas','scipy','tkinter','h5py','PyQt6','PyQt6.QtWebEngineWidgets',
             'pytest','ruff','serial','pyftdi','usb','ftd2xx','ftd3xx','sklearn','filterpy','crcmod','openEMS','CSXCAD']:
    try:
        module = importlib.import_module(name)
        results[name] = {'import_ok':True, 'version':str(getattr(module,'__version__','未由模块提供'))}
    except Exception as exc:
        results[name] = {'import_ok':False, 'error':type(exc).__name__+': '+str(exc)}
record = {'date':'2026-10-08','python_executable':sys.executable,'python_version':sys.version,
          'environment':args.label,
          'modules':results,'scope':'仅本次明确指定的解释器；不能外推到其他虚拟环境或系统安装'}
(ROOT/args.output).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
