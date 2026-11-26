"""bom-full.csv -> PCBWay 공식 BOM 템플릿 9열, 보드별 CSV 2개.

실행:  python -I make_pcbway_bom.py            (기본 입력은 inputs/, 출력은 이 폴더)
       python -I make_pcbway_bom.py --bom-full <bom-full.csv> --kicad-carrier <csv> --kicad-front <csv> --out <dir>

입력:
  - bom-full.csv : research R-008 레인의 전체 BOM (21열, Reference 열이 "[캐리어] C1,C2" 꼴)
  - <board>-kicad-bom.csv : kicad-cli sch export bom 결과 (열 Refs, Value, Footprint, Qty, DNP)
출력:
  - carrier-pcbway.csv, front-pcbway.csv (PCBWay 템플릿 9열, 보드 1장 기준 수량)
검사 (종료 코드):
  0 = 보드마다 참조 지정자 집합과 DNP 집합이 KiCad BOM과 같다
  1 = 하나라도 다르다 (차이를 stderr에 적는다)
  2 = 입력 파일·형식 오류
규칙:
  - 시험점(TP*)은 부품이 아니라 BOM에서 뺀다. 검사에서는 KiCad 쪽 TP도 같이 빼고, 뺀 개수를 출력한다.
  - DNP 행은 Type=DNS, Notes 맨 앞에 "DNS - do not purchase/place".
  - bom-full AssemblyNotes에 '위탁'이 있으면 Notes에 "Consigned", 아니면 "Turnkey".
  - 회로도 밖 부품(모듈·S401·렌즈·케이블·어댑터 등, Reference가 보드 접두어가 아닌 행)은 PCBA BOM에 넣지 않고 목록만 출력한다.
  - 출력은 ASCII만 쓴다 (비 ASCII 문자는 치환하거나 지운다).
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOARDS = {'carrier': '[캐리어]', 'front': '[전면]'}
HEADER = ['Item #', '*Designator', '*Qty', 'Manufacturer', '*Mfg Part #', 'Description / Value',
          '*Package/Footprint ', 'Type', 'Your Instructions / Notes']
THT_FP = ('BarrelJack_XKB_DC-005-5A-2.0_Horizontal', 'RJ45_Hanrun_HR911105A_Horizontal')
HYBRID_FP = ('USB_C_Receptacle_HRO_TYPE-C-31-M-12',)
MANUAL_FP = ('M12_Holder_20mm_CLA216-ICR',)
ASCII_MAP = {'µ': 'u', 'μ': 'u', '≥': '>=', '≤': '<=', '±': '+/-', '°': 'deg', '×': 'x', '–': '-', '—': '-',
             '−': '-', '·': ';', '²': '2', 'Ω': 'ohm', '’': "'", '“': '"', '”': '"'}


WORD_MAP = {'재고': 'stock'}


def ascii_only(s):
    for k, v in WORD_MAP.items():
        s = s.replace(k, v)
    s = ''.join(ASCII_MAP.get(c, c) for c in s)
    return s.encode('ascii', 'ignore').decode('ascii').strip()


def split_refs(text):
    return [r.strip() for r in text.split(',') if r.strip()]


def is_tp(ref):
    return re.fullmatch(r'TP\d+', ref) is not None


def ref_key(ref):
    m = re.match(r'([A-Za-z_]+?)(\d*)$', ref)
    return (m.group(1), int(m.group(2) or 0)) if m else (ref, 0)


def load_kicad(path):
    refs, dnp = set(), set()
    with open(path, encoding='utf-8-sig', newline='') as f:
        rd = csv.DictReader(f)
        if not {'Refs', 'DNP'} <= set(rd.fieldnames or []):
            raise ValueError(f'{path}: Refs/DNP 열이 없다')
        for r in rd:
            for ref in split_refs(r['Refs']):
                refs.add(ref)
                if r['DNP'].strip():
                    dnp.add(ref)
    return refs, dnp


def load_bom_full(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    head = rows[0]
    if len(head) != 21 or head[0] != 'Reference':
        raise ValueError(f'{path}: 21열 bom-template 형식이 아니다')
    col = {k: i for i, k in enumerate(head)}
    return col, rows[1:]


def part_type(footprint, dnp):
    if dnp:
        return 'DNS'
    fp = footprint.split(':')[-1]
    if fp in MANUAL_FP:
        return 'Manual'
    if fp in THT_FP:
        return 'THT'
    if fp in HYBRID_FP:
        return 'Hybrid'
    return 'SMD'


def build(board, col, rows):
    tag = BOARDS[board]
    out, refs, dnp = [], set(), set()
    for r in rows:
        ref_field = r[col['Reference']]
        if not ref_field.startswith(tag + ' '):
            continue
        refs_part = ref_field[len(tag) + 1:]
        if refs_part.startswith('TP'):
            continue  # 시험점 요약 행 (부품 아님)
        rlist = sorted(split_refs(refs_part), key=ref_key)
        notes_src = r[col['AssemblyNotes']]
        is_dnp = notes_src.startswith('DNP')
        refs.update(rlist)
        if is_dnp:
            dnp.update(rlist)
        notes = []
        if is_dnp:
            notes.append('DNS - do not purchase/place')
        notes.append('Consigned' if '위탁' in notes_src else 'Turnkey')
        if 'G1' in notes_src:
            notes.append('Gate G1: BTB mating check before production')
        if part_type(r[col['Footprint']], False) == 'Manual':
            notes.append('Not soldered: mechanical part, customer mounts')
        dist = r[col['Distributor']]
        if dist:
            notes.append('Source: ' + dist)
        out.append({
            'refs': rlist,
            'mfr': r[col['Manufacturer']],
            'mpn': r[col['MPN']],
            'desc': r[col['Value']],
            'pkg': r[col['Package']],
            'type': part_type(r[col['Footprint']], is_dnp),
            'notes': '; '.join(notes),
        })
    out.sort(key=lambda x: ref_key(x['refs'][0]))
    return out, refs, dnp


def offboard(col, rows):
    tags = tuple(t + ' ' for t in BOARDS.values())
    return [r[col['Reference']] + ' | ' + r[col['MPN']] for r in rows if not r[col['Reference']].startswith(tags)]


def write(path, items):
    with open(path, 'w', encoding='ascii', newline='') as f:
        w = csv.writer(f, lineterminator='\r\n')
        w.writerow(HEADER)
        for i, it in enumerate(items, 1):
            w.writerow([i, ','.join(it['refs']), len(it['refs']), ascii_only(it['mfr']), ascii_only(it['mpn']),
                        ascii_only(it['desc']), ascii_only(it['pkg']), it['type'], ascii_only(it['notes'])])


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--bom-full', default=os.path.join(HERE, 'inputs', 'bom-full.csv'))
    ap.add_argument('--kicad-carrier', default=os.path.join(HERE, 'inputs', 'carrier-kicad-bom.csv'))
    ap.add_argument('--kicad-front', default=os.path.join(HERE, 'inputs', 'front-kicad-bom.csv'))
    ap.add_argument('--out', default=HERE)
    a = ap.parse_args()
    try:
        col, rows = load_bom_full(a.bom_full)
        kicad = {'carrier': load_kicad(a.kicad_carrier), 'front': load_kicad(a.kicad_front)}
    except (OSError, ValueError, KeyError) as e:
        print(f'입력 오류: {e}', file=sys.stderr)
        return 2
    ok = True
    for board in BOARDS:
        items, refs, dnp = build(board, col, rows)
        k_refs, k_dnp = kicad[board]
        tps = {r for r in k_refs if is_tp(r)}
        k_refs, k_dnp = k_refs - tps, k_dnp - tps
        path = os.path.join(a.out, f'{board}-pcbway.csv')
        write(path, items)
        placed = sum(len(i['refs']) for i in items if i['type'] != 'DNS')
        print(f'{board}: 행 {len(items)} · 참조 {len(refs)} (실장 {placed}, DNS {len(dnp)}) · KiCad 참조 {len(k_refs)} (TP {len(tps)}개 제외) -> {path}')
        for name, mine, theirs in (('참조 지정자', refs, k_refs), ('DNP', dnp, k_dnp)):
            if mine != theirs:
                ok = False
                print(f'  불일치 [{board} {name}] BOM에만: {sorted(mine - theirs, key=ref_key)} / KiCad에만: {sorted(theirs - mine, key=ref_key)}', file=sys.stderr)
            else:
                print(f'  일치 [{name}] {len(mine)}개')
    print('PCBA BOM에서 뺀 회로도 밖 부품:')
    for line in offboard(col, rows):
        print('  ' + line)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
