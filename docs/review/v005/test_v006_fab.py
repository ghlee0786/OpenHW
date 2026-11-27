# -*- coding: utf-8 -*-
"""v006_fab.py 고장 주입 시험 — pcb 산출물이 커밋되기 전이라 가짜 산출물 묶음을 만든다.

사용: python -I test_v006_fab.py <보드 .kicad_pcb (사본)> <작업 폴더> [--kicad-cli 경로]
  1) 보드 사본의 aux 원점을 외곽 왼쪽 아래로 옮긴 뒤 kicad-cli 로 R-010 명령대로 Gerber·드릴·좌표·조립도 PDF 를 만든다
     (회전은 0~360 으로 바꾸고, BOM 은 보드 속성으로 PCBWay 9열을 만든다 — pcb 산출물 흉내)
  2) 정상 묶음은 불합격 0 이어야 하고, 위반을 하나씩 넣은 묶음 15개는 그 항목이 불합격이어야 한다
종료 0 = 전부 통과.
"""
import sys, os, re, csv, json, shutil, zipfile, hashlib, subprocess, argparse

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('pcb'); ap.add_argument('work')
# 기본값: 환경 변수 KICAD_BIN 폴더, 없으면 사용자 설치 기본 자리(%LOCALAPPDATA%) 의 kicad-cli
_kbin = os.environ.get('KICAD_BIN') or os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'KiCad', '10.0', 'bin')
ap.add_argument('--kicad-cli', default=os.path.join(_kbin, 'kicad-cli.exe'))
A = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.abspath(A.work)
if os.path.isdir(W):
    shutil.rmtree(W)
os.makedirs(W)
B = os.path.splitext(os.path.basename(A.pcb))[0]

# ---- 보드 사본 + 원점 ----
src = os.path.dirname(os.path.abspath(A.pcb))
bd = os.path.join(W, 'board')
shutil.copytree(src, bd)
pcb = os.path.join(bd, os.path.basename(A.pcb))
t = open(pcb, encoding='utf-8').read()
pts = [(float(a), float(b)) for a, b in re.findall(r'\(gr_(?:line|rect|arc)\s*\(start ([-\d.]+) ([-\d.]+)\)(?:(?!\(gr_).)*?\(layer "Edge.Cuts"\)', t, re.S)]
pts += [(float(a), float(b)) for a, b in re.findall(r'\(end ([-\d.]+) ([-\d.]+)\)(?:(?!\(gr_).)*?\(layer "Edge.Cuts"\)', t, re.S)]
x0, y1 = min(p[0] for p in pts), max(p[1] for p in pts)
t = re.sub(r'\(aux_axis_origin [-\d.]+ [-\d.]+\)', '(aux_axis_origin %g %g)' % (x0, y1), t)
open(pcb, 'w', encoding='utf-8').write(t)

G = os.path.join(W, 'good', B)
os.makedirs(os.path.join(G, 'gerber'))


def run(*a):
    r = subprocess.run([A.kicad_cli] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace')
    assert r.returncode == 0, (a, r.stdout[-500:], r.stderr[-500:])


run('pcb', 'export', 'gerbers', '-l', 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts', '--no-x2',
    '--no-protel-ext', '--precision', '6', '--use-drill-file-origin', '-o', os.path.join(G, 'gerber') + '/', pcb)
run('pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'plot', '--excellon-units', 'mm', '--excellon-zeros-format', 'decimal',
    '--excellon-oval-format', 'alternate', '--excellon-separate-th', '--generate-map', '--map-format', 'pdf', '-o', os.path.join(G, 'gerber') + '/', pcb)
for side, nm in (('front', 'top'), ('back', 'bottom')):
    out = os.path.join(G, '%s-%s-pos.csv' % (B, nm))
    run('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--use-drill-file-origin', '--smd-only', '--exclude-dnp', '--side', side, '-o', out, pcb)
    rows = list(csv.reader(open(out, encoding='utf-8', newline='')))
    for r in rows[1:]:
        r[5] = '%.6f' % (float(r[5]) % 360)
    csv.writer(open(out, 'w', encoding='utf-8', newline='')).writerows(rows)
run('pcb', 'export', 'pdf', '-l', 'F.Fab,Edge.Cuts', '--sp', '--cdnp', '--mode-single', '-o', os.path.join(G, '%s-assembly-top.pdf' % B), pcb)
run('pcb', 'export', 'pdf', '-l', 'B.Fab,Edge.Cuts', '--sp', '--cdnp', '--mirror', '--mode-single', '-o', os.path.join(G, '%s-assembly-bottom.pdf' % B), pcb)

# BOM (보드 속성으로)
grp = {}
for m in re.finditer(r'\n\t\(footprint "([^"]+)"(.*?)\n\t\)', t, re.S):
    blk = m.group(2)
    ref = re.search(r'\(property "Reference" "([^"]*)"', blk).group(1)
    val = re.search(r'\(property "Value" "([^"]*)"', blk).group(1)
    at = re.search(r'\n\t\t\(attr ([^)]*)\)', blk)
    a = at.group(1).split() if at else []
    if 'exclude_from_bom' in a or not ({'smd', 'through_hole'} & set(a)):
        continue
    typ = 'DNS' if 'dnp' in a else ('SMD' if 'smd' in a else 'THT')
    grp.setdefault((val, m.group(1).split(':')[-1], typ), []).append(ref)
with open(os.path.join(G, '%s-pcbway.csv' % B), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Item #', '*Designator', '*Qty', 'Manufacturer', '*Mfg Part #', 'Description / Value', '*Package/Footprint ', 'Type', 'Your Instructions / Notes'])
    for i, ((val, fpn, typ), refs) in enumerate(sorted(grp.items()), 1):
        w.writerow([i, ','.join(sorted(refs)), len(refs), 'X', 'MPN-%d' % i, val, fpn, typ, '' if typ == 'DNS' else 'Turnkey'])
README = '''# %s 제출 묶음 (시험용 가짜)
층 순서: L1: F.Cu  L2: In1.Cu  L3: In2.Cu  L4: B.Cu
패널: 단품(panel 없음)
폼: 4 layers, FR-4 TG150, 1.6mm, 6/6mil, 0.3mm, ENIG 1U", 1oz/1oz, Tenting
X-ray: U2 1회
위탁(Consigned): 없음
게이트: G1 BTB 결합, G2 홀더 — 확인 전 발주 금지
''' % B
open(os.path.join(G, 'README.md'), 'w', encoding='utf-8').write(README)


def pack(d):
    z = d + '.zip'
    if os.path.exists(z):
        os.remove(z)
    with zipfile.ZipFile(z, 'w') as zf:
        for r, _, fs in os.walk(d):
            for f in fs:
                if f != 'SHA256SUMS':
                    zf.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), d))
    h = hashlib.sha256(open(z, 'rb').read()).hexdigest()
    open(os.path.join(d, 'SHA256SUMS'), 'w').write('%s  %s\n' % (h, os.path.basename(z)))


pack(G)


def mutate(name, fn):
    d = os.path.join(W, name, B)
    shutil.copytree(G, d)
    fn(d)
    pack(d)
    return d


def edit(path, f):
    s = open(path, encoding='utf-8', errors='replace').read()
    open(path, 'w', encoding='utf-8').write(f(s))


def gp(d, suf):
    return [os.path.join(d, 'gerber', x) for x in os.listdir(os.path.join(d, 'gerber')) if x.endswith(suf)][0]


def inner2(d):
    for x in os.listdir(os.path.join(d, 'gerber')):
        p = os.path.join(d, 'gerber', x)
        if x.endswith('.gbr') and 'Copper,L3,Inr' in open(p, encoding='utf-8', errors='replace').read(2000):
            return p


def pos(d, side):
    return os.path.join(d, '%s-%s-pos.csv' % (B, side))


def bom(d):
    return os.path.join(d, '%s-pcbway.csv' % B)


def csv_edit(path, f):
    rows = list(csv.reader(open(path, encoding='utf-8', newline='')))
    rows = f(rows)
    csv.writer(open(path, 'w', encoding='utf-8', newline='')).writerows(rows)


def bom_dns_one(rows):
    for r in rows[1:]:
        if r[7] == 'SMD' and int(r[2]) == 1:
            r[7] = 'DNS'; r[8] = ''
            return rows


def zip_tamper(d):
    pass


MUT = [
    ('m01_no_In2', '3.01', lambda d: os.remove(inner2(d))),
    ('m02_fmt35', '3.02', lambda d: edit(gp(d, 'F_Cu.gbr'), lambda s: s.replace('%FSLAX46Y46*%', '%FSLAX35Y35*%'))),
    ('m03_x2', '3.02', lambda d: edit(gp(d, 'B_Cu.gbr'), lambda s: s.replace('%MOMM*%', '%MOMM*%\n%TF.FileFunction,Copper,L4,Bot*%'))),
    ('m04_edge_open', '3.02b', lambda d: edit(gp(d, 'Edge_Cuts.gbr'), lambda s: re.sub(r'\n[^\n]*D01\*', '', s, count=1))),
    ('m05_no_npth', '3.03', lambda d: os.remove(os.path.join(d, 'gerber', '%s-NPTH.drl' % B))),
    ('m06_inch', '3.03', lambda d: edit(os.path.join(d, 'gerber', '%s-PTH.drl' % B), lambda s: s.replace('METRIC', 'INCH'))),
    ('m07_origin', '3.04', lambda d: csv_edit(pos(d, 'top'), lambda rows: [rows[0]] + [r[:3] + ['%.6f' % (float(r[3]) - 60)] + r[4:] for r in rows[1:]])),
    ('m08_neg_rot', '3.05', lambda d: csv_edit(pos(d, 'bottom'), lambda rows: [rows[0], rows[1][:5] + ['-90.000000'] + rows[1][6:]] + rows[2:])),
    ('m09_drop_row', '3.05', lambda d: csv_edit(pos(d, 'top'), lambda rows: rows[:-1])),
    ('m10_bom8', '3.06', lambda d: csv_edit(bom(d), lambda rows: [r[:8] for r in rows])),
    ('m11_dns', '3.07', lambda d: csv_edit(bom(d), bom_dns_one)),
    ('m12_no_asm', '3.09', lambda d: [os.remove(os.path.join(d, x)) for x in os.listdir(d) if 'assembly' in x]),
    ('m13_no_layers', '3.10', lambda d: edit(os.path.join(d, 'README.md'), lambda s: s.replace('L3: In2.Cu', 'L3: ?'))),
    ('m14_no_G2', '3.15', lambda d: edit(os.path.join(d, 'README.md'), lambda s: s.replace('G2', 'Gx'))),
]


def check(d):
    out = d + '.json'
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v006_fab.py'), d, out, '--board', B, '--pcb', pcb],
                       capture_output=True, text=True, encoding='utf-8')
    R = json.load(open(out, encoding='utf-8'))
    failed = [i['id'] for i in R['items'] if i['verifiable'] and not i['pass']]
    return r.returncode, failed, r.stdout


CASES = []
rc, failed, so = check(G)
CASES.append(('정상 묶음 불합격 0 · 종료 0', rc == 0 and not failed, failed, so))
for name, exp, fn in MUT:
    d = mutate(name, fn)
    rc, failed, so = check(d)
    CASES.append(('%s → %s 불합격 · 종료 코드 = 불합격 수' % (name, exp), exp in failed and rc == len(failed), failed, so))
# 15: zip 을 기록 뒤에 바꿈
d = os.path.join(W, 'm15_zip', B)
shutil.copytree(G, d)
pack(d)
with zipfile.ZipFile(d + '.zip', 'a') as zf:
    zf.writestr('extra.txt', 'tamper')
rc, failed, so = check(d)
CASES.append(('m15_zip_tamper → 3.16 불합격', '3.16' in failed and rc == len(failed), failed, so))
fail = 0
for n, ok, f, so in CASES:
    print('%s  %s  (불합격 %s)' % ('통과' if ok else '실패', n, f))
    if not ok:
        fail += 1
        print(so[-2500:])
print('사례 %d · 실패 %d · 폴더 %s' % (len(CASES), fail, W))
sys.exit(1 if fail else 0)
