"""Read-only source inventory for the Chinese project review."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import subprocess
import fitz
import openpyxl

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/zh-CN'
WORK = ROOT / '5_Simulations/generated/project_review_20261008'
WORK.mkdir(parents=True, exist_ok=True)
paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
paths = sorted(p for p in paths if p)
rows = []
pdfs = []
workbooks = []
for name in paths:
    p = ROOT / name
    data = p.read_bytes()
    row = {'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
           'extension': p.suffix.lower(), 'category': name.split('/')[0]}
    rows.append(row)
    if p.suffix.lower() == '.pdf':
        with fitz.open(p) as d:
            pages = [page.get_text() for page in d]
            pdfs.append({**row, 'pages': len(d), 'text_pages': sum(bool(t.strip()) for t in pages),
                         'first_pages': '\n'.join(pages[:2])[:6500]})
    if p.suffix.lower() == '.xlsx':
        w = openpyxl.load_workbook(p, read_only=True, data_only=False)
        sheets = []
        for sheet in w:
            cells = [{'cell': c.coordinate, 'text': c.value} for r in sheet for c in r
                     if isinstance(c.value, str) and not c.value.startswith('=')]
            sheets.append({'name': sheet.title, 'rows': sheet.max_row, 'columns': sheet.max_column, 'texts': cells})
        workbooks.append({'path': name, 'sheets': sheets})
        w.close()
with (OUT / '文件清单.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(OUT / '源文件基线.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
(WORK / 'pdf_extract.json').write_text(json.dumps(pdfs, ensure_ascii=False, indent=2), encoding='utf-8')
(WORK / 'workbook_extract.json').write_text(json.dumps(workbooks, ensure_ascii=False, indent=2), encoding='utf-8')
summary = {'files': len(rows), 'bytes': sum(r['bytes'] for r in rows),
           'categories': dict(Counter(r['category'] for r in rows)),
           'extensions': dict(Counter(r['extension'] for r in rows)),
           'pdf_pages': sum(p['pages'] for p in pdfs)}
(OUT / '盘点统计.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
print('PDF extraction and workbook text extraction saved to', WORK)
