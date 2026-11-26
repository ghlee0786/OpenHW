"""M-008 확인 한 명령: 전면 풋프린트 코트야드(json) → Fusion 01_check (M007_assembly 문서가 열려 있어야 함) → 결과 표 출력.
종료 코드 = 새 바디가 낀 간섭 수 (의도: 새 홀더 ↔ 새 스페이서·리드·패드 맞닿음은 부피 0 이라 안 잡힘)."""
import json, os, re, math, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(LANE, 'validation', 'runtime', 'vd001')
FCLI = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion360', 'scripts', 'fusion_cli.py')
t = open(os.path.join(OUT, 'pcbsrc', 'hardware', 'schematic', 'front', 'front.kicad_pcb'), encoding='utf-8').read()
fps = []
for m in re.finditer(r'\n\t\(footprint "([^"]+)"', t):
    s = m.start() + 1; e = t.find('\n\t(footprint', s); blk = t[s:e if e > 0 else len(t)]
    ref = re.search(r'\(property "Reference" "([^"]+)"', blk).group(1)
    lay = re.search(r'\(layer "([^"]+)"\)', blk).group(1)
    at = re.search(r'\n\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
    X0, Y0 = float(at.group(1)), float(at.group(2)); th = math.radians(float(at.group(3) or 0))
    b = None
    for it in re.finditer(r'\n\t\t\((fp_line|fp_rect|fp_poly)(.*?)\n\t\t\)', blk, re.S):
        if '.CrtYd"' not in it.group(2):
            continue
        for x, y in re.findall(r'\((?:start|end|xy) ([-\d.]+) ([-\d.]+)\)', it.group(2)):
            x, y = float(x), float(y)
            X = X0 + x * math.cos(th) + y * math.sin(th) - 100; Y = -(Y0 - x * math.sin(th) + y * math.cos(th) - 100)
            b = [X, X, Y, Y] if b is None else [min(b[0], X), max(b[1], X), min(b[2], Y), max(b[3], Y)]
    fps.append((ref, b, lay))
json.dump(fps, open(os.path.join(OUT, 'm008_front_fp.json'), 'w', encoding='utf-8'))
r = subprocess.run([sys.executable, FCLI, 'run', os.path.join(HERE, 'scripts', '01_check.py')], capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout.strip()[-400:], r.stderr.strip()[-400:])
if r.returncode:
    sys.exit(99)
res = json.load(open(os.path.join(OUT, 'm008_check.json'), encoding='utf-8'))
print('## 새 바디 ↔ 주변 최소 틈 (3 mm 안)')
for x in res['near']:
    print('%-16s ↔ %-40s %7.3f %s' % (x['new'], x['other'], x['min_mm'], '← 겹침/맞닿음' if x['min_mm'] <= 0.0 else ''))
bad = [x for x in res['near'] if x['min_mm'] <= 0.0 and not (x['new'], x['other'].split('/')[-1]) in
       {('CLA216_M008', 'SPACER_M008'), ('SPACER_M008', 'CLA216_M008'), ('CLA216_M008', 'LENS_CIL093'), ('FPC_M008', 'SENSOR_BLOCK_BXF4677')}]
print('겹침·맞닿음 (새 바디 기준, 의도 제외: 홀더↔스페이서·렌즈 나사, FPC↔센서 블록):', len(bad), [(x['new'], x['other']) for x in bad])
sys.exit(len(bad))
