"""계약 v1.11 §4(캐리어)·§5(전면) BTB 핀표를 JSON으로 뽑는다. 실행: python -I contract_pins.py <hw-fw-contract.md> <out.json>"""
import json
import re
import sys

t = open(sys.argv[1], encoding='utf-8').read().splitlines()
out = {'carrier': {}, 'front': {}}
sec = None
for i, l in enumerate(t, 1):
    if l.startswith('## 4.'):
        sec = 'carrier'
    elif l.startswith('## 5.'):
        sec = 'front'
    elif l.startswith('### 5.1') or l.startswith('## 6'):
        sec = None
    if sec and re.match(r'\|\s*\d+\s*\|\s*\d+\s*\|', l):
        c = [x.strip() for x in l.strip('|').split('|')]
        out[sec][c[0]] = {'core': c[1], 'net': c[2], 'use': c[5], 'line': i}
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False)
print({k: len(v) for k, v in out.items()})
