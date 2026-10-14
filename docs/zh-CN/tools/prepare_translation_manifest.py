"""Record original-source hashes, using the initial read-only inventory."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'docs/zh-CN'
hashes = {r['path']: r['sha256'] for r in json.loads((BASE/'源文件基线.json').read_text(encoding='utf-8'))}
pairs = [
    ('README.md', 'README原文译文.md'),
    ('CONTRIBUTING.md', 'CONTRIBUTING原文译文.md'),
    ('Licence', 'Licence原文译文.md'),
    ('9_Firmware/9_2_FPGA/adc_clk_mmcm_integration.md', 'firmware/ADC时钟MMCM集成指南.md'),
    ('9_Firmware/9_2_FPGA/constraints/README.md', 'firmware/FPGA约束文件说明.md'),
    ('9_Firmware/9_2_FPGA/tb/cosim/real_data/hex/STALE_NOTICE.md', 'firmware/黄金参考Hex文件说明.md'),
    ('docs/artifacts/te0713-te0701-heartbeat-2026-03-21.md', 'firmware/TE0713心跳上电调试产物.md'),
    ('docs/artifacts/te0713-te0701-umft601x-dev-2026-03-21.md', 'firmware/FT601集成开发比特流.md'),
    ('9_Firmware/9_3_GUI/GUI_versions.txt', 'firmware/GUI版本说明.md'),
    ('9_Firmware/9_2_FPGA/tb/cosim/scenario_info.txt', 'firmware/测试场景与匹配滤波参考数据.md'),
    ('9_Firmware/9_2_FPGA/tb/mf_golden_summary.txt', 'firmware/测试场景与匹配滤波参考数据.md'),
]
for name in ['index','architecture','implementation-log','bring-up','reports','release-notes','board-day-worksheet']:
    pairs.append((f'docs/{name}.html', f'web/{name}.md'))
entries = [{'source': s, 'translation': 'docs/zh-CN/'+t, 'source_sha256': hashes[s],
            'scope': '英文说明全文中文对照；数据值、命令与标识符保留'} for s,t in pairs]
record_path = BASE/'README合并记录.json'
if record_path.exists():
    record = json.loads(record_path.read_text(encoding='utf-8'))
    entries[0].update(source_sha256=record['merged_sha256'],
                      english_snapshot=record['english_snapshot'],
                      original_sha256=record['original_sha256'])
(BASE/'翻译对应表.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'{len(entries)} sources; {len({e["translation"] for e in entries})} translation files')
