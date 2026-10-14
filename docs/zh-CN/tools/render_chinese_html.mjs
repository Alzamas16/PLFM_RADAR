// Build local HTML readers for the active Markdown translations.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const base = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const markedPath = process.argv[2];
if (!markedPath) throw new Error('Supply the bundled marked/lib/marked.esm.js path.');
const { marked } = await import(pathToFileURL(path.resolve(markedPath)).href);
const manifest = JSON.parse(await fs.readFile(path.join(base, '翻译对应表.json'), 'utf8'));
const root = path.resolve(base, '../..');
const files = new Set(manifest.map(row => path.resolve(root, row.translation)));
for (const extra of ['README.md','项目盘点.md','本机工具与硬件条件.md','Python虚拟环境.md','web/审阅发现.md','firmware/实现与验证盘点.md','firmware/本次检查记录.md']) {
  files.add(path.join(base, extra));
}
const outputs = new Map([...files].map(f => [f, f === path.join(base, 'README.md') ? path.join(base, 'index.html') : f.replace(/\.md$/, '.html')]));
const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const style = `:root{color-scheme:light}body{margin:0;color:#182635;background:#f6f8fa;font:17px/1.8 system-ui,"Microsoft YaHei",sans-serif}header{padding:14px 5%;background:#123750;color:white}header a{color:white}main{max-width:1080px;margin:30px auto;padding:32px;background:white}h1,h2,h3{line-height:1.4;color:#123750}a{color:#005b93}p,li{overflow-wrap:anywhere}table{border-collapse:collapse;display:block;overflow-x:auto;margin:24px 0;width:100%}th,td{border:1px solid #cbd5df;padding:9px 12px;vertical-align:top}th{background:#eaf0f5}pre{background:#f0f3f6;padding:16px;overflow-x:auto}code{font-family:Consolas,monospace}img{max-width:100%;height:auto}blockquote{margin-left:0;padding-left:20px;border-left:3px solid #ccd5df}footer{font-size:14px;color:#566573;margin-top:40px}@media(max-width:700px){main{margin:0;padding:20px}body{font-size:16px}}`;
for (const [source, output] of outputs) {
  const md = await fs.readFile(source, 'utf8');
  const title = md.match(/^#\s+(.+)$/m)?.[1] || 'AERIS-10 中文资料';
  let body = marked.parse(md, { gfm: true });
  body = body.replace(/href="([^"#]+)(#[^"]*)?"/g, (match, href, anchor='') => {
    if (/^(?:[a-z]+:|\/\/)/i.test(href)) return match;
    const target = path.resolve(path.dirname(source), decodeURIComponent(href));
    const localized = outputs.get(target);
    if (!localized) return match;
    return `href="${path.relative(path.dirname(output), localized).split(path.sep).join('/').split('/').map(encodeURIComponent).join('/')}${anchor}"`;
  });
  const home = path.relative(path.dirname(output), path.join(base,'index.html')).split(path.sep).join('/') || 'index.html';
  const mdLink = encodeURIComponent(path.basename(source));
  const html = `<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><style>${style}</style></head><body><header><a href="${home}">中文资料目录</a> · <a href="${mdLink}">查看 Markdown</a></header><main>${body}<footer>本地中文对照 · 2026-10-08。原文中的历史测试与性能不代表本轮硬件验证。</footer></main></body></html>\n`;
  await fs.writeFile(output, html, 'utf8');
}
console.log(`Rendered ${outputs.size} active Chinese HTML readers.`);
