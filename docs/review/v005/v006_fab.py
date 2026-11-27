# -*- coding: utf-8 -*-
"""V-006: VD-001 조건 3 — R-010 「P-004 체크리스트」 16항 제조 산출물 자동 검사 (표준 라이브러리만).

사용: python -I v006_fab.py <보드 산출물 폴더 또는 zip> <out.json> --board carrier [--pcb <board.kicad_pcb 사본>] [--commit <sha>]
  폴더 안(하위 포함)에서 찾는 것 — 이름 규칙은 docs/review/vd001-format.md §3:
    Gerber *.gbr 11장(층은 파일 머리 주석 「TF.FileFunction」으로 식별 — 사용자 층 이름이 달라도 됨)
    드릴 *PTH.drl · *NPTH.drl · *drl_map.pdf   좌표 *top*pos*.csv · *bottom*pos*.csv (또는 front/back)
    BOM *pcbway*.csv (PCBWay 9열)   조립도 *.pdf (드릴 맵 제외)   README*(.md/.txt)   SHA256SUMS* 또는 README 안 sha256 + zip
  --pcb 를 주면 보드 파일(s-식)에서 외곽 크기·DNP·SMD/THT·구멍 수를 읽어 대조한다.
종료 코드 = 불합격 항목 수(사람 확인 항목 8 은 세지 않음). 입력 오류 100.
"""
import sys, os, re, io, csv, json, glob, zipfile, hashlib, tempfile, argparse, datetime

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--board', required=True)
ap.add_argument('--pcb'); ap.add_argument('--commit', default='')
A = ap.parse_args()
if not os.path.exists(A.src):
    print('입력 없음', A.src); sys.exit(100)
zips = []
if A.src.lower().endswith('.zip'):
    zips.append(A.src)
    D = tempfile.mkdtemp(prefix='v006fab_')
    zipfile.ZipFile(A.src).extractall(D)
else:
    D = A.src
    zips = glob.glob(os.path.join(D, '**', '*.zip'), recursive=True) + glob.glob(os.path.join(os.path.dirname(os.path.abspath(D)), A.board + '*.zip'))
FILES = [os.path.join(r, f) for r, _, fs in os.walk(D) for f in fs]
items = []


def add(no, title, ok, value='', limit='', ev=(), note='', verifiable=True):
    items.append(dict(cond='3', id='3.%02d' % no, board=A.board, title=title, verifiable=verifiable, value=value, limit=limit,
                      **{'pass': (bool(ok) if verifiable else None)}, evidence=[dict(label=os.path.basename(e), path=e) for e in ev], commit=A.commit, note=note))


def rel(p):
    return os.path.relpath(p, D)


def pick(pat, exclude=None):
    rx = re.compile(pat, re.I)
    return sorted(f for f in FILES if rx.search(os.path.basename(f)) and not (exclude and re.search(exclude, os.path.basename(f), re.I)))


# ---------- 보드 파일(선택) ----------
PCB = None
if A.pcb and os.path.exists(A.pcb):
    t = open(A.pcb, encoding='utf-8').read()
    fps = []
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', t):
        s = m.start()
        d, j = 0, s + 1
        while True:
            c = t[j]
            if c == '(':
                d += 1
            elif c == ')':
                d -= 1
                if d == 0:
                    break
            j += 1
        blk = t[s:j]
        ref = re.search(r'\(property "Reference" "([^"]*)"', blk)
        attr = re.search(r'\n\t\t\(attr ([^)]*)\)', blk)
        a = attr.group(1).split() if attr else []
        pads = re.findall(r'\(pad "[^"]*" (\w+)', blk)
        layer = re.search(r'\n\t\t\(layer "([^"]+)"\)', blk)
        fps.append(dict(ref=ref.group(1) if ref else '?', smd=('smd' in a), tht=('through_hole' in a), dnp=('dnp' in a),
                        no_bom=('exclude_from_bom' in a), no_pos=('exclude_from_pos_files' in a), side='bottom' if layer and layer.group(1).startswith('B.') else 'top',
                        npth=pads.count('np_thru_hole'), pth=pads.count('thru_hole')))
    vias = len(re.findall(r'\n\t\(via\b', t))
    edges = re.findall(r'\(gr_(line|rect|arc|circle)\s*\n?\s*\(start ([-\d.]+) ([-\d.]+)\)(?:\s*\n?\s*\(mid [-\d.]+ [-\d.]+\))?\s*\n?\s*\(end ([-\d.]+) ([-\d.]+)\)(.*?)\(layer "Edge.Cuts"\)', t, re.S)
    xs = [float(e[1]) for e in edges] + [float(e[3]) for e in edges]
    ys = [float(e[2]) for e in edges] + [float(e[4]) for e in edges]
    PCB = dict(fps=fps, vias=vias, w=(max(xs) - min(xs)) if xs else None, h=(max(ys) - min(ys)) if ys else None)

# ---------- 1·2 Gerber ----------
FF = {'Copper,L1,Top': 'F.Cu', 'Copper,L2,Inr': 'In1.Cu', 'Copper,L3,Inr': 'In2.Cu', 'Copper,L4,Bot': 'B.Cu', 'Paste,Top': 'F.Paste',
      'Paste,Bot': 'B.Paste', 'Legend,Top': 'F.Silkscreen', 'Legend,Bot': 'B.Silkscreen', 'Soldermask,Top': 'F.Mask',
      'Soldermask,Bot': 'B.Mask', 'Profile,NP': 'Edge.Cuts'}
gbrs = pick(r'\.gbr$')
found, bad_fmt = {}, []
for g in gbrs:
    head = open(g, encoding='utf-8', errors='replace').read()
    m = re.search(r'TF\.FileFunction,([A-Za-z]+(?:,[A-Za-z0-9]+)*)', head)
    key = None
    if m:
        f = m.group(1)
        key = next((v for k, v in FF.items() if f.startswith(k)), None)
    if key is None:  # 이름으로
        nm = os.path.basename(g)
        key = next((v for v in FF.values() if nm.endswith(v.replace('.', '_') + '.gbr')), None)
    found.setdefault(key, []).append(g)
    probs = []
    # RS-274X 판정 = 확장 명령 %FS·%MO 가 있다(조리개 %ADD 는 영역만 있는 층에서 없을 수 있다)
    if '%FSLAX46Y46*%' not in head:
        probs.append('형식 4.6 아님')
    if '%MOMM*%' not in head:
        probs.append('mm 아님')
    if re.search(r'^%T[FAOD]', head, re.M):
        probs.append('X2 속성 있음')
    if not head.rstrip().endswith('M02*'):
        probs.append('M02 끝 없음')
    if probs:
        bad_fmt.append('%s: %s' % (rel(g), ', '.join(probs)))
missing = [v for v in FF.values() if v not in found]
dup = [k for k, v in found.items() if k and len(v) > 1]
unknown = [rel(g) for g in found.get(None, [])]
add(1, 'Gerber 층 11장(F/In1/In2/B.Cu·Paste·Silkscreen·Mask·Edge.Cuts)', len(gbrs) == 11 and not missing and not dup and not unknown,
    '%d장, 빠짐 %s, 중복 %s, 모름 %s' % (len(gbrs), missing or 0, dup or 0, unknown or 0), '11장·빠짐 0', [rel(g) for g in gbrs][:11])
add(2, 'Gerber 형식 RS-274X·4.6·mm·X2 끔·M02', bool(gbrs) and not bad_fmt, len(bad_fmt), 0, [], '; '.join(bad_fmt[:6]))


# 외곽 닫힘
def gerber_segments(path):
    segs, x, y, mode = [], None, None, 'G01'
    for ln in open(path, encoding='utf-8', errors='replace'):
        ln = ln.strip()
        for g in re.findall(r'G0[123]', ln):
            mode = g
        m = re.match(r'(?:G0[123])?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])\*', ln)
        if not m:
            continue
        nx = int(m.group(1)) / 1e6 if m.group(1) is not None else x
        ny = int(m.group(2)) / 1e6 if m.group(2) is not None else y
        if m.group(5) == '1' and x is not None:
            segs.append(((x, y), (nx, ny), mode))
        x, y = nx, ny
    return segs


edge_ok, edge_note, bbox = False, '', None
if found.get('Edge.Cuts'):
    segs = gerber_segments(found['Edge.Cuts'][0])
    deg = {}
    for a, b_, mode in segs:
        if mode != 'G01' and a == b_:
            continue  # 완전한 원은 스스로 닫힘
        for p in (a, b_):
            k = (round(p[0], 3), round(p[1], 3))
            deg[k] = deg.get(k, 0) + 1
    odd = [k for k, v in deg.items() if v % 2]
    pts = [p for s in segs for p in s[:2]]
    if pts:
        bbox = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
    edge_ok = bool(segs) and not odd
    edge_note = '선분 %d, 홀수 끝점 %d%s' % (len(segs), len(odd), (' 예: %s' % odd[:3]) if odd else '')
    if PCB and PCB['w'] and bbox:
        dw, dh = abs((bbox[2] - bbox[0]) - PCB['w']), abs((bbox[3] - bbox[1]) - PCB['h'])
        edge_note += ', 크기 %.3f×%.3f (보드 %.3f×%.3f)' % (bbox[2] - bbox[0], bbox[3] - bbox[1], PCB['w'], PCB['h'])
        edge_ok = edge_ok and dw < 0.05 and dh < 0.05
add(2, 'Edge.Cuts 외곽 닫힘·보드 크기', edge_ok, edge_note, '홀수 끝점 0', [rel(found['Edge.Cuts'][0])] if found.get('Edge.Cuts') else [])
items[-1]['id'] = '3.02b'

# ---------- 3 드릴 ----------
pth, npth = pick(r'(?<!N)PTH\.drl$'), pick(r'NPTH\.drl$')
maps = pick(r'drl_map\.pdf$|drill.*map.*\.pdf$')
dprob, holes = [], {}
for name, fl in (('PTH', pth), ('NPTH', npth)):
    if len(fl) != 1:
        dprob.append('%s 파일 %d개' % (name, len(fl))); continue
    tx = open(fl[0], encoding='utf-8', errors='replace').read()
    if 'METRIC' not in tx:
        dprob.append('%s METRIC 없음' % name)
    co = re.findall(r'^X(-?[\d.]+)Y(-?[\d.]+)', tx, re.M)
    if co and not all('.' in a and '.' in b_ for a, b_ in co):
        dprob.append('%s 좌표 decimal 아님' % name)
    holes[name] = [(float(a), float(b_)) for a, b_ in co]
if not maps:
    dprob.append('드릴 맵 PDF 없음')
note3 = 'PTH %d · NPTH %d 구멍' % (len(holes.get('PTH', [])), len(holes.get('NPTH', [])))
if PCB:
    ep = PCB['vias'] + sum(f['pth'] for f in PCB['fps'])
    en = sum(f['npth'] for f in PCB['fps'])
    note3 += ' (보드: PTH %d · NPTH %d)' % (ep, en)
    if 'PTH' in holes and len(holes['PTH']) != ep:
        dprob.append('PTH 수 %d ≠ 보드 %d' % (len(holes['PTH']), ep))
    if 'NPTH' in holes and len(holes['NPTH']) != en:
        dprob.append('NPTH 수 %d ≠ 보드 %d' % (len(holes['NPTH']), en))
add(3, '드릴 Excellon·mm·decimal·PTH/NPTH 2파일·드릴 맵', not dprob, note3, '문제 0', [rel(x) for x in pth + npth + maps], '; '.join(dprob))

# ---------- 5 좌표 ----------
# 면 이름은 pos 바로 옆에 붙은 것만 본다 — 보드 이름이 front 면 「front-bottom-pos.csv」가 top 으로도 잡히던 것을 막는다 (V-006f)
top = pick(r'(top|front)[-_ ]?pos[^/]*\.csv$|pos[-_ ]?(top|front)[^/]*\.csv$')
bot = pick(r'(bottom|back)[-_ ]?pos[^/]*\.csv$|pos[-_ ]?(bottom|back)[^/]*\.csv$')
pos_rows, pprob = {}, []
KH = ['Ref', 'Val', 'Package', 'PosX', 'PosY', 'Rot', 'Side']
PH = ['Designator', 'Footprint', 'Mid X', 'Mid Y', 'Ref X', 'Ref Y', 'Pad X', 'Pad Y', 'TB', 'Rotation', 'Comment']
for side, fl in (('top', top), ('bottom', bot)):
    if len(fl) != 1:
        pprob.append('%s 좌표 파일 %d개' % (side, len(fl))); continue
    rows = list(csv.reader(open(fl[0], encoding='utf-8-sig', newline='')))
    if not rows:
        pprob.append('%s 빈 파일' % side); continue
    h = [c.strip() for c in rows[0]]
    if h == KH:
        ix = dict(ref=0, x=3, y=4, rot=5, side=6)
    elif h[:len(PH)] == PH:
        ix = dict(ref=0, x=2, y=3, rot=9, side=8)
    else:
        pprob.append('%s 머리글 다름 %s' % (side, h)); continue
    out = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        try:
            x, y, rot = float(r[ix['x']]), float(r[ix['y']]), float(r[ix['rot']])
        except ValueError:
            pprob.append('%s 숫자 아님 %s' % (side, r[0])); continue
        sv = r[ix['side']].strip().lower()
        if sv not in ({'top', 't', 'front'} if side == 'top' else {'bottom', 'b', 'back'}):
            pprob.append('%s 파일에 면 %s (%s)' % (side, sv, r[0]))
        if not (0 <= rot < 360):
            pprob.append('%s 회전 %g 범위 밖(0~360) %s' % (side, rot, r[0]))
        out.append(dict(ref=r[ix['ref']].strip(), x=x, y=y, rot=rot))
    pos_rows[side] = out
pprob = sorted(set(pprob))
pos_all = {r['ref'] for v in pos_rows.values() for r in v}

# ---------- 4 원점 ----------
oprob = []
if bbox:
    if abs(bbox[0]) > 0.05 or abs(bbox[1]) > 0.05:
        oprob.append('Gerber 외곽 최소 (%.3f, %.3f) ≠ (0,0)' % (bbox[0], bbox[1]))
    W, H = bbox[2], bbox[3]
    for k, hl in holes.items():
        o = [p for p in hl if not (-0.05 <= p[0] <= W + 0.05 and -0.05 <= abs(p[1]) <= H + 0.05)]
        if o:
            oprob.append('%s 구멍 %d개가 외곽 밖' % (k, len(o)))
    for s, rr in pos_rows.items():
        o = [r['ref'] for r in rr if not (-0.05 <= r['x'] <= W + 0.05 and -0.05 <= r['y'] <= H + 0.05)]
        if o:
            oprob.append('%s 좌표 %d개가 0~보드 크기 밖(예 %s)' % (s, len(o), o[:3]))
else:
    oprob.append('외곽 없음')
add(4, '원점 = 보드 왼쪽 아래(Gerber·드릴·좌표 같은 원점)', not oprob, '; '.join(oprob) or '맞음', '외곽 최소 (0,0)·좌표 0~W/H', [])

# ---------- 6·7 BOM · DNP ----------
boms = pick(r'pcbway.*\.csv$|bom.*\.csv$', exclude=r'pos')
BH = ['Item #', '*Designator', '*Qty', 'Manufacturer', '*Mfg Part #', 'Description / Value', '*Package/Footprint ', 'Type', 'Your Instructions / Notes']
bprob, bom_ref, bom_dns, bom_smd, bom_tht, notes_bad = [], set(), set(), set(), set(), []
bom_manual = set()   # Type Manual (프로젝트 값) — 보드·좌표 대조에서 뺀다
if len(boms) != 1:
    bprob.append('BOM 파일 %d개' % len(boms))
else:
    rows = list(csv.reader(open(boms[0], encoding='utf-8-sig', newline='')))
    if not rows or rows[0] != BH:
        bprob.append('머리글이 PCBWay 9열과 다름: %s' % (rows[0] if rows else '없음'))
    for r in rows[1:]:
        if len(r) < 9 or not r[1].strip():
            continue
        refs = [x.strip() for x in r[1].split(',') if x.strip()]
        try:
            q = int(r[2])
        except ValueError:
            q = -1
        if q != len(refs):
            bprob.append('수량 %s ≠ 참조 %d (%s)' % (r[2], len(refs), r[1][:30]))
        dup = bom_ref.intersection(refs)
        if dup:
            bprob.append('참조 중복 %s' % sorted(dup))
        bom_ref.update(refs)
        typ = r[7].strip().upper()
        # Type 값: PCBWay 양식(R-010) 「Surface mount, Thru-hole or Hybrid」+ DNS. Hybrid = SMD 몸체에 THT 다리, 좌표 파일에 들어가는 실장 부품 → SMD 와 같이 센다
        # Manual = 프로젝트가 더한 값(manufacturing/bom/README.md B5: 납땜하지 않는 기구 부품, PCBWay 가 받는지는 미확인).
        #   Notes 에 「Not soldered」가 있을 때만 받고, 보드 실장 부품·좌표와의 대조에서 뺀다(좌표에 있으면 불합격)
        {'DNS': bom_dns, 'SMD': bom_smd, 'HYBRID': bom_smd, 'THT': bom_tht, 'MANUAL': bom_manual}.get(typ, set()).update(refs)
        if typ == 'MANUAL' and not re.search(r'not soldered', r[8], re.I):
            bprob.append('Type Manual 인데 Notes 에 「Not soldered」 없음 (%s)' % r[1][:20])
        if typ not in ('DNS', 'SMD', 'THT', 'HYBRID', 'MANUAL'):
            bprob.append('Type %s — PCBWay 양식 값(SMD·THT·Hybrid·DNS)도 프로젝트 값(Manual)도 아님 (%s)' % (r[7], r[1][:20]))
        if typ != 'DNS' and not re.search(r'Turnkey|Consigned|Combo', r[8], re.I):
            notes_bad.append(r[1][:20])
placed = bom_ref - bom_dns
if PCB:
    # 부품 = BOM 제외가 아니고 종류가 SMD 또는 THT (종류 없음 = 시험점 같은 맨 패드는 부품이 아님)
    pcb_bom = {f['ref'] for f in PCB['fps'] if not f['no_bom'] and (f['smd'] or f['tht'])}
    pcb_dnp = {f['ref'] for f in PCB['fps'] if f['dnp'] and not f['no_bom'] and (f['smd'] or f['tht'])}
    if bom_ref and (bom_ref - bom_manual) != pcb_bom:
        bprob.append('BOM 참조 ≠ 보드(BOM에만 %s, 보드에만 %s)' % (sorted((bom_ref - bom_manual) - pcb_bom)[:6], sorted(pcb_bom - bom_ref)[:6]))
if pos_all & bom_manual:
    bprob.append('Type Manual 인데 좌표 파일에 있음 %s' % sorted(pos_all & bom_manual))
add(6, 'BOM PCBWay 9열·수량=참조 수·Type·참조 집합=좌표+THT', not bprob and pos_all == (bom_smd - bom_dns) | (pos_all & bom_tht),
    '%d행 참조 %d (SMD·Hybrid %d·THT %d·DNS %d·Manual %d), 좌표 %d' % (len(bom_ref), len(bom_ref), len(bom_smd), len(bom_tht), len(bom_dns), len(bom_manual), len(pos_all)), '문제 0',
    [rel(b) for b in boms], '; '.join(bprob[:6] + (['참고: Type Manual %s 은 PCBWay 양식 밖 프로젝트 값(BOM README B5) — 제조사 확인 전' % sorted(bom_manual)] if bom_manual and not bprob else [])
                                    + (['좌표에만 %s' % sorted(pos_all - (bom_smd | bom_tht))[:6]] if pos_all - (bom_smd | bom_tht) else [])
                                    + (['BOM SMD인데 좌표에 없음 %s' % sorted((bom_smd - bom_dns) - pos_all)[:6]] if (bom_smd - bom_dns) - pos_all else [])))
dprob7 = []
if pos_all & bom_dns:
    dprob7.append('DNS가 좌표에 있음 %s' % sorted(pos_all & bom_dns))
if PCB:
    if bom_dns != pcb_dnp:
        dprob7.append('BOM DNS ≠ 보드 DNP (BOM에만 %s, 보드에만 %s)' % (sorted(bom_dns - pcb_dnp), sorted(pcb_dnp - bom_dns)))
add(7, 'DNP 일치: BOM DNS = 보드 DNP, 좌표에 없음', bool(boms) and not dprob7, len(bom_dns), '집합 같음', [], '; '.join(dprob7))
# 5 (BOM 뒤에 판정: 행 수 = BOM SMD 실장 수)
if PCB:
    for s, rr in pos_rows.items():
        exp = {f['ref'] for f in PCB['fps'] if f['side'] == s and f['smd'] and not f['dnp'] and not f['no_pos']}
        got = {r['ref'] for r in rr}
        if got != exp:
            pprob.append('%s 좌표 ≠ 보드 %s 면 SMD 실장(좌표에만 %s, 보드에만 %s)' % (s, s, sorted(got - exp)[:5], sorted(exp - got)[:5]))
smd_placed = bom_smd - bom_dns
add(5, '좌표 csv·mm·면별 2파일·면 열·회전 0~360·행 수 = BOM SMD 실장 수', not pprob and bool(boms) and len(pos_all) == len(smd_placed),
    '좌표 %d / BOM SMD 실장 %d' % (len(pos_all), len(smd_placed)), '같음·문제 0', [rel(x) for x in top + bot], '; '.join(pprob[:8]))

# ---------- 8 극성 (사람) ----------
add(8, '극성·1번 핀 실크 — V-005 S9 기계 판정 + 사람 확인(H1·H2)', None, '-', '사람 확인', ['validation/runtime/v005/<커밋>/index.html'], verifiable=False)

# ---------- 9 조립도 ----------
pdfs = [p for p in pick(r'\.pdf$') if not re.search(r'drl_map|drill', os.path.basename(p), re.I)]
pages = {}
for p in pdfs:
    pages[rel(p)] = len(re.findall(rb'/Type\s*/Page(?![s\w])', open(p, 'rb').read()))
add(9, '조립도 PDF 있음·쪽 수(앞·뒤 Fab)', bool(pdfs) and all(v >= 1 for v in pages.values()) and sum(pages.values()) >= 2,
    ', '.join('%s %d쪽' % kv for kv in pages.items()) or '없음', '앞·뒤 합 ≥2쪽', list(pages))

# ---------- 10~16 문서 ----------
readmes = pick(r'^readme', exclude=r'\.(pdf|csv|gbr|drl)$')
rt = '\n'.join(open(r, encoding='utf-8', errors='replace').read() for r in readmes)
lay = all(re.search(r'L%d\s*[:=]\s*%s' % (i, re.escape(n)), rt) for i, n in ((1, 'F.Cu'), (2, 'In1.Cu'), (3, 'In2.Cu'), (4, 'B.Cu')))
add(10, '층 순서 L1:F.Cu L2:In1.Cu L3:In2.Cu L4:B.Cu 를 README 에', lay, 'README %d개' % len(readmes), '4줄 모두', [rel(r) for r in readmes])
dims = '%.2f×%.2f mm' % (bbox[2] - bbox[0], bbox[3] - bbox[1]) if bbox else '?'
add(11, '패널 결정 기록(외형 %s, 조립용 ≥50×100 이면 단품)' % dims, bool(re.search(r'패널|panel', rt, re.I)), dims, 'README 에 패널 결정', [rel(r) for r in readmes])
need12 = ['4', '1.6', 'ENIG', 'TG', '1oz', 'Tenting']
miss12 = [k for k in need12 if not re.search(re.escape(k), rt, re.I)]
add(12, '주문 폼 옵션(4L·FR-4 TG·1.6mm·6/6mil·0.3mm·ENIG·1/1oz·Tenting·임피던스) 기록', not miss12, '빠짐 %s' % (miss12 or 0), '빠짐 0', [rel(r) for r in readmes])
add(13, 'X-ray 대상·횟수 기록', bool(re.search(r'X-?ray', rt, re.I)), '', 'README 에 X-ray', [rel(r) for r in readmes])
add(14, '위탁 목록·BOM Notes(Turnkey/Consigned/Combo)', bool(boms) and not notes_bad and bool(re.search(r'위탁|Consign|Kitted', rt, re.I)),
    'Notes 빈 행 %d' % len(notes_bad), '0·README 위탁 기록', [rel(b) for b in boms], ', '.join(notes_bad[:6]))
add(15, '게이트 G1·G2 기록(발주 금지 조건)', bool(re.search(r'\bG1\b', rt)) and bool(re.search(r'\bG2\b', rt)), '', 'README 에 G1·G2', [rel(r) for r in readmes])
sums = pick(r'^sha256sums')
st = rt + '\n'.join(open(s, encoding='utf-8', errors='replace').read() for s in sums)
if A.src.lower().endswith('.zip'):
    # zip 은 자기 해시를 담을 수 없다 → 기록은 zip 옆에 있다: 같은 폴더 또는 <보드>/ 의 SHA256SUMS* (V-006f)
    _zd = os.path.dirname(os.path.abspath(A.src))
    for _f in glob.glob(os.path.join(_zd, 'SHA256SUMS*')) + glob.glob(os.path.join(_zd, A.board, 'SHA256SUMS*')):
        st += '\n' + open(_f, encoding='utf-8', errors='replace').read()
zok, znote = False, '제출 zip 없음'
if zips:
    zs = {os.path.basename(z): hashlib.sha256(open(z, 'rb').read()).hexdigest() for z in zips}
    zok = all(h in st for h in zs.values())
    znote = ', '.join('%s %s…%s' % (k, v[:8], '' if v in st else ' (기록 없음)') for k, v in zs.items())
add(16, '제출 zip sha256 기록 일치', zok, znote, 'README/SHA256SUMS 에 같은 값', [os.path.basename(z) for z in zips])

fails = [i for i in items if i['verifiable'] and not i['pass']]
R = dict(cond='3', owner='review', board=A.board, title='제조 산출물 R-010 16항', commit=A.commit, source=A.src,
         generated=datetime.datetime.now().isoformat(timespec='seconds'), command='python -I docs/review/v005/v006_fab.py %s' % A.src,
         exit_code=len(fails), items=items)
json.dump(R, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for i in items:
    print('%s  %s %s — %s %s' % ('사람' if not i['verifiable'] else ('통과' if i['pass'] else '불합격'), i['id'], i['title'], i['value'], ('(' + i['note'] + ')') if i['note'] else ''))
print('조건 3 [%s] 불합격 %d' % (A.board, len(fails)))
sys.exit(len(fails))
