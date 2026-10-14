"""Record the interpreter, installed versions and authorized ignore change."""
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'docs/zh-CN'
assert Path(sys.prefix).resolve() == (ROOT/'.venv').resolve(), 'Use the project venv interpreter.'
assert sys.version_info[:2] == (3,13), 'The requested system Python 3.13 is required.'
uv = ROOT/'.venv/Scripts/uv.exe'
freeze = subprocess.run([str(uv),'pip','freeze','--python',sys.executable],capture_output=True,text=True,check=True)
(ROOT/'requirements-local.lock.txt').write_text('# Windows x64 / system Python 3.13 project venv snapshot\n'+freeze.stdout,encoding='utf-8')
packages = sorted([{'name': d.metadata['Name'], 'version':d.version} for d in importlib.metadata.distributions()],key=lambda p:p['name'].lower())
inputs = ['requirements-local.txt','pyproject.toml',
          '9_Firmware/9_3_GUI/requirements_dashboard.txt','9_Firmware/9_3_GUI/requirements_v7.txt',
          '9_Firmware/9_3_GUI/requirements_pyqt_gui.txt']
record = {'created_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
          'python_version':sys.version,'python_executable':sys.executable,'base_prefix':sys.base_prefix,
          'venv_prefix':sys.prefix,'include_system_site_packages':False,
          'installation_gate':'Socket Firewall Free v1.15.4; asset SHA256 verified',
          'installation_command':'sfw uv pip install --python .venv/Scripts/python.exe --no-python-downloads -r requirements-local.txt --group dev',
          'inputs':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
          'packages':packages,'installed_distribution_count':len(packages),
          'lock_file':'requirements-local.lock.txt',
          'lock_sha256':hashlib.sha256((ROOT/'requirements-local.lock.txt').read_bytes()).hexdigest()}
(BASE/'虚拟环境安装记录.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
baseline = {r['path']:r for r in json.loads((BASE/'源文件基线.json').read_text(encoding='utf-8'))}
authorized = [{'source':'.gitignore','original_sha256':baseline['.gitignore']['sha256'],
               'current_sha256':hashlib.sha256((ROOT/'.gitignore').read_bytes()).hexdigest(),
               'reason':'用户要求在项目目录创建虚拟环境并安装依赖；排除 .venv 和本地 .tools 二进制'}]
(BASE/'授权修改记录.json').write_text(json.dumps(authorized,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'python':sys.version.split()[0],'installed_distributions':len(packages),'lock_file':'requirements-local.lock.txt'},ensure_ascii=False))
