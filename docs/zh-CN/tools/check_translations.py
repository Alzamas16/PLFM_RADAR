"""Check translation coverage, fingerprints and generated local HTML links."""
import hashlib
import json
from pathlib import Path
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from merge_readme import validate_readme

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'docs/zh-CN'
baseline = json.loads((BASE/'源文件基线.json').read_text(encoding='utf-8'))
manifest = json.loads((BASE/'翻译对应表.json').read_text(encoding='utf-8'))
errors = []
source_changes = []
authorized_changes = []
merge_path = BASE/'README合并记录.json'
merge = json.loads(merge_path.read_text(encoding='utf-8')) if merge_path.exists() else None
authorized_path = BASE/'授权修改记录.json'
authorized_records = json.loads(authorized_path.read_text(encoding='utf-8')) if authorized_path.exists() else []
for row in baseline:
    p = ROOT/row['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
        source_changes.append(row['path'])
        for allowed in authorized_records:
            if (allowed['source'] == row['path'] and allowed['original_sha256'] == row['sha256']
                    and p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == allowed['current_sha256']):
                authorized_changes.append(row['path'])
        if row['path'] == 'README.md' and merge and p.is_file():
            snapshot = ROOT/merge['english_snapshot']
            if (hashlib.sha256(p.read_bytes()).hexdigest() == merge['merged_sha256']
                    and snapshot.is_file() and hashlib.sha256(snapshot.read_bytes()).hexdigest() == row['sha256']):
                authorized_changes.append(row['path'])
                merged_text = p.read_text(encoding='utf-8')
                for error in validate_readme(merged_text):
                    errors.append({'source':'README.md','error':error})
for row in manifest:
    source = ROOT/row['source']
    target = ROOT/row['translation']
    if not source.is_file():
        errors.append({'source':row['source'], 'error':'原文不存在'})
    elif hashlib.sha256(source.read_bytes()).hexdigest() != row['source_sha256']:
        errors.append({'source':row['source'], 'error':'原文已变更，需要复核译文'})
    if not target.is_file():
        errors.append({'translation':row['translation'], 'error':'译文不存在'})
    else:
        text = target.read_text(encoding='utf-8')
        if not re.search(r'[\u4e00-\u9fff]', text):
            errors.append({'translation':row['translation'], 'error':'没有中文'})
        # Fenced code may use a language tag; every opening fence must be closed.
        opened = False
        for line in text.splitlines():
            if line.strip().startswith('```'):
                opened = not opened
        if opened:
            errors.append({'translation':row['translation'], 'error':'代码围栏未闭合'})
expected = {r['path'] for r in baseline if Path(r['path']).suffix in {'.md','.html'}}
missing = sorted(expected-{r['source'] for r in manifest})
for name in missing:
    errors.append({'source':name, 'error':'未覆盖的原 Markdown/HTML'})
active = {ROOT/r['translation'] for r in manifest}
active |= {BASE/p for p in ['README.md','项目盘点.md','本机工具与硬件条件.md','Python虚拟环境.md','web/审阅发现.md','firmware/实现与验证盘点.md','firmware/本次检查记录.md']}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for key,value in attrs:
            if (tag == 'a' and key == 'href') or (tag in {'img','script'} and key == 'src'):
                self.links.append(value)

html_count = 0
link_count = 0
for md in sorted(active):
    html = md.with_suffix('.html') if md.name != 'README.md' else md.with_name('index.html')
    if not html.is_file():
        errors.append({'file':str(html.relative_to(ROOT)), 'error':'中文 HTML 未生成'})
        continue
    html_count += 1
    parser = Links()
    parser.feed(html.read_text(encoding='utf-8'))
    for href in parser.links:
        split = urlsplit(href)
        if split.scheme or split.netloc or not split.path:
            continue
        link_count += 1
        if split.path.startswith('/'):
            target = ROOT/unquote(split.path.lstrip('/'))
        else:
            target = html.parent/unquote(split.path)
        if not target.exists():
            errors.append({'file':str(html.relative_to(ROOT)), 'link':href, 'error':'本地链接目标不存在'})
# The merged README is the user's primary entry. Check its local Markdown links.
root_readme = (ROOT/'README.md').read_text(encoding='utf-8')
for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', root_readme):
    split = urlsplit(href)
    if split.scheme or split.netloc or not split.path:
        continue
    link_count += 1
    target = ROOT/unquote(split.path.lstrip('/'))
    if not target.exists():
        errors.append({'file':'README.md', 'link':href, 'error':'主入口本地链接目标不存在'})
if (ROOT/'README.zh-CN.md').exists():
    errors.append({'file':'README.zh-CN.md','error':'用户要求不保留独立文件'})
for heading in ['一 本机已有工具可以开展的工作','二 需要补充或配置工具才能完成的工作','三 需要硬件才能完成的工作']:
    if heading not in root_readme:
        errors.append({'file':'README.md','error':'本机工作分类缺失：'+heading})
original_headings = re.findall(r'(?m)^#{1,3} .+$', (BASE/'sources/README.en.md').read_text(encoding='utf-8'))
if len(original_headings) != 21:
    errors.append({'file':'README.md','error':'英文快照的原21个章节数量变化'})
for error in validate_readme(root_readme):
    errors.append({'file':'README.md','error':error})
result = {'date':'2026-10-08', 'baseline_files':len(baseline), 'source_files_changed':source_changes,
          'authorized_source_changes':authorized_changes,
          'unauthorized_source_changes':sorted(set(source_changes)-set(authorized_changes)),
          'covered_sources':len(manifest), 'translation_files':len({r['translation'] for r in manifest}),
          'original_markdown_html_count':len(expected), 'uncovered_markdown_html':missing,
          'html_readers':html_count, 'local_links_checked':link_count, 'errors':errors,
          'scope':'结构/覆盖/指纹/链接检查；不验证逐句翻译、远程链接、工程测试或硬件性能'}
(BASE/'校验记录.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors or set(source_changes)-set(authorized_changes) else 0)
