# -*- coding: utf-8 -*-
"""一人一码密码生成器：生成 N 个专属密码
输出：①密码表.txt（发货清单，明文，自己保存）②自动嵌入 index.html 的 PW_HASHES（只存哈希）
增量追加：不会覆盖已生成的旧密码"""
import re, random, sys
from pathlib import Path

ROOT = Path(__file__).parent
HTML = ROOT / "index.html"
LIST = ROOT / "密码表.txt"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 50

def djb2(s):
    h = 5381
    for c in s:
        h = ((h << 5) + h + ord(c)) & 0xFFFFFFFF
    return format(h, 'x')

# 读取现有哈希（增量）+ 现有明文清单
html = HTML.read_text(encoding='utf-8')
m = re.search(r'PW_HASHES\s*=\s*\[(.*?)\];', html, re.S)
existing = set(re.findall(r'"([0-9a-f]+)"', m.group(1))) if m else set()
old_plain = []
if LIST.exists():
    old_plain = [ln.split('|')[1].strip() for ln in LIST.read_text(encoding='utf-8').splitlines()
                 if '|' in ln]

# 生成新密码：8位数字、去重、哈希不与现有重复
new = []
while len(new) < N:
    p = ''.join(random.choices('0123456789', k=8))
    if djb2(p) not in existing:
        existing.add(djb2(p)); new.append(p)

# 写入 HTML（整体替换 PW_HASHES 数组）
all_hashes = sorted(existing)
block = 'PW_HASHES = [\n' + ''.join(f'  "{h}",\n' for h in all_hashes) + '];'
if m:
    html = html[:m.start()] + block + html[m.end():]
else:
    raise SystemExit('index.html 中找不到 PW_HASHES，请检查')
HTML.write_text(html, encoding='utf-8')

# 写密码表（发货清单）
lines = ['══════ 密码表（发货用 · 自己保存 · 勿发买家）══════',
         '用法：客户下单 → 取一个未用的密码发给TA → 在状态栏标记',
         '作废：告诉我密码序号，我从H5里移除并重新推送', '']
used = {ln for ln in (LIST.read_text(encoding='utf-8') if LIST.exists() else '').splitlines()
        if '已用' in ln}
import datetime
for i, p in enumerate(old_plain + new, 1):
    tag = '✓已用' if f'{i}|' in ''.join(used) else '可用'
    lines.append(f'{i:03d} | {p} | {tag} | 发货日期:____ 买家:____')
LIST.write_text('\n'.join(lines), encoding='utf-8')

print(f'新增 {N} 个密码（总 {len(all_hashes)} 个已嵌入 H5）')
print(f'发货清单: {LIST}')
print('前5个新密码:', ' '.join(new[:5]))
