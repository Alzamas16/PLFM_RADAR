"""Render the English README with Chinese directly beneath each text block."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'docs/zh-CN'
SNAPSHOT = BASE / 'sources/README.en.md'
TRANSLATIONS = BASE / 'README逐行译文.json'


def read_pairs():
    data = json.loads(TRANSLATIONS.read_text(encoding='utf-8'))
    digest = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
    if data['source_sha256'] != digest:
        raise ValueError('English snapshot changed; review line translation mappings first.')
    lines = SNAPSHOT.read_text(encoding='utf-8').splitlines()
    pairs = {int(key): value for key, value in data['translations'].items()}
    signatures = {'**Nawfal Motii**', 'ABAC INDUSTRY', '(http://www.abacindustry.com)'}
    expected = {
        number for number, line in enumerate(lines, 1)
        if line.strip() and not line.startswith(('[![', '![', '<!--'))
        and line.strip() not in signatures | {'---'}
        and not re.fullmatch(r'\|[-| ]+\|', line)
    }
    if set(pairs) != expected:
        raise ValueError(f'Translation coverage mismatch: {sorted(set(pairs) ^ expected)}')
    return lines, pairs


def render_pair(line, translation):
    if line.startswith('|'):
        cells = line.strip('|').split('|')
        if not isinstance(translation, list) or len(translation) != len(cells):
            raise ValueError('Table translation must match its English columns.')
        return '|' + '|'.join(
            cell.rstrip() + '<br>' + zh + ' ' if zh else cell
            for cell, zh in zip(cells, translation)
        ) + '|'
    if not isinstance(translation, str) or not translation.strip():
        raise ValueError('Text translation is empty or not a string.')
    if line.startswith('#'):
        return line + '<br>' + translation
    marker = re.match(r'^(\s*)(?:- |\d+\. )', line)
    indent = ' ' * marker.end() if marker else ''
    return line + '<br>\n' + indent + translation


def validate_readme(merged):
    """Require every source block, its translation and the original section order."""
    lines, pairs = read_pairs()
    errors = []
    cursor = 0
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        expected = render_pair(line, pairs[number]) if number in pairs else line
        found = merged.find(expected, cursor)
        if found == -1:
            errors.append(f'英文源第 {number} 行的原文或紧邻译文缺失')
        else:
            cursor = found + len(expected)
    if '**中文对照**' in merged:
        errors.append('仍有按章节汇总的中文对照标签')
    return errors


def environment_section():
    environment = (BASE / 'Python虚拟环境.md').read_text(encoding='utf-8')
    environment = re.sub(r'(?m)^(#{1,3})( )', r'\1#\2', environment)
    return re.sub(
        r'(?<!!)\[([^\]]+)\]\(([^)]+)\)',
        lambda match: match.group(0) if re.match(r'^[a-z]+:', match[2])
        else f'[{match[1]}](docs/zh-CN/{match[2]})', environment,
    ).strip()


def machine_section():
    machine = (BASE / '本机工具与硬件条件.md').read_text(encoding='utf-8')
    machine = re.sub(r'(?m)^(#{1,3})( )', r'\1#\2', machine)
    machine = machine.replace(
        '## 本机工具与硬件条件',
        '## Local tools and hardware requirements<br>本机工具与硬件条件', 1,
    )
    return re.sub(
        r'(?<!!)\[([^\]]+)\]\(([^)]+)\)',
        lambda match: match.group(0) if re.match(r'^[a-z]+:', match[2])
        else f'[{match[1]}](docs/zh-CN/{match[2]})', machine,
    ).strip()


def main():
    lines, pairs = read_pairs()
    result = []
    for number, line in enumerate(lines, 1):
        if line == '## 📡 Overview':
            result += [environment_section(), '', machine_section(), '']
        previous = lines[number - 2] if number > 1 else ''
        is_list = re.match(r'^\s*(?:- |\d+\. )', line)
        previous_list = re.match(r'^\s*(?:- |\d+\. )', previous)
        if previous.strip() and (line.startswith('#') or (is_list and not previous_list)):
            result.append('')
        result.append(render_pair(line, pairs[number]) if number in pairs else line)
        if line.startswith('![AERIS-10 Antenna Array]'):
            result += ['', '[中文资料目录](docs/zh-CN/README.md) · [项目盘点](docs/zh-CN/项目盘点.md)', '',
                       '英文正文保留，中文逐段、逐条紧接在原文下方。性能、测试状态、许可证说明和社区数量均为原文陈述，未作硬件实测或联网核实。原文型号与版本要求的差异见中文译注。']
        if line.startswith('<!-- V6 GIF removed'):
            result += ['', '译注：原文展示 V6 界面动画，但上方 HTML 注释写明 V6 已弃用，当前使用 V65 Tk 和 V7 PyQt6。本地动画见 `9_Firmware/9_3_GUI/GUI_V6.gif`。']
        if line.startswith('![PCBWay Sponsor Logo]'):
            result += ['', '原文列出 PCBWay 赞助商标志，本地图片见 `8_Utils/PCBWAY.jpg`。']
    merged = '\n'.join(result).rstrip() + '\n'
    errors = validate_readme(merged)
    if errors:
        raise ValueError('; '.join(errors))
    (ROOT / 'README.md').write_text(merged, encoding='utf-8', newline='\n')
    record = {
        'source': 'README.md',
        'reason': '用户要求中文直接位于对应英文原文的下一行',
        'english_snapshot': 'docs/zh-CN/sources/README.en.md',
        'original_sha256': hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        'merged_sha256': hashlib.sha256((ROOT / 'README.md').read_bytes()).hexdigest(),
        'english_content_preserved': True,
        'section_pairs': sum(line.startswith('#') for line in lines),
        'layout': '英文在上、中文在下；段落和列表逐条对应，标题和表格用 <br> 换行',
        'translation_pairs': len(pairs),
        'line_translations': 'docs/zh-CN/README逐行译文.json',
    }
    (BASE / 'README合并记录.json').write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n',
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
