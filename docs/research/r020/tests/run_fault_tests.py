#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""고장 주입 시험. 원본 보드의 사본에 고장을 넣어 ev_check.py 가 잡는지 종료 코드로 확인한다.

  A  캐리어 /12V_IN_RAW 트랙 전부를 0.40 mm 로 좁힘          → 기대: 원본 + 1 (그 넷 트랙 항목 불합격)
  B  전면 CSI_L1 P/N 트랙 폭 0.15 → 0.21 mm (중심선 그대로)    → 기대: 원본 + 1 (CSI_L1 임피던스 불합격)
  C  전면 /12V_IR 트랙 전부 삭제 (미배선)                      → 기대: 원본과 같음, 그 넷 항목은 「미배선」으로 따로 셈 (멈추지 않음)
  AB A+B 동시                                                 → 기대: 원본 + 2
  D  캐리어 탈출·보정 영역(DP_BRK·DP_TUNE) 삭제 — D-003 #63 ② 가 빠지면 ① 셈법이 됨
                                                              → 기대: 원본보다 많음, 새 불합격은 모두 「비결합」 항목이고 MDI_RX 가 들어 있음
  E  캐리어 꼬임 영역(DP_TWIST) 삭제 — 꼬임 비아 높이가 판정에 들어감(review 합의 (c)의 반대)
                                                              → 기대: 원본보다 많음, MDI_RX 「쌍 안 길이 차」 새 불합격
  G  한도 표기: MDI_TX 만 D-003 #62 (다) 1.27·7, MDI_RX 는 #28 0·6 (원본 결과의 한도 문자열)

실행 (KiCad 동봉 Python):
  python.exe -I tests/run_fault_tests.py --carrier <carrier.kicad_pcb> --front <front.kicad_pcb> --workdir <빈 작업 폴더>
종료 코드 = 기대와 다른 경우 수 (0 = 모두 기대대로).
원본 보드 파일은 읽기만 한다. 고장 보드는 --workdir 아래에만 쓴다.
"""
import argparse
import json
import os
import subprocess
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def make_fault(src, dst, kind):
    b = pcbnew.LoadBoard(src)
    n = 0
    for t in list(b.GetTracks()):
        if t.GetClass() == 'PCB_VIA':
            continue
        net = t.GetNetname()
        if kind == 'A' and net == '/12V_IN_RAW':
            t.SetWidth(pcbnew.FromMM(0.40)); n += 1
        elif kind == 'B' and net in ('/CAM_RX0_1P', '/CAM_RX0_1N'):
            t.SetWidth(pcbnew.FromMM(0.21)); n += 1
        elif kind == 'C' and net == '/12V_IR':
            b.Remove(t); n += 1
    names = {'D': ('DP_BRK', 'DP_TUNE'), 'E': ('DP_TWIST',)}.get(kind, ())
    if names:  # 트랙을 지운 보드(C)에서 Zones() 를 다시 훑으면 SWIG 객체가 깨진다 — 영역 고장에서만 훑는다
        for z in [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName() in names]:
            b.Remove(z); n += 1
    if n == 0:
        raise SystemExit('고장 %s: 바꿀 트랙이 없다' % kind)
    pcbnew.SaveBoard(dst, b)
    return n


def make_fault_proc(src, dst, kind):
    """고장 보드를 별도 프로세스에서 만든다 — 한 프로세스에서 LoadBoard 를 여러 번 하면 SWIG 객체가 깨진다(R-030 기록)."""
    p = subprocess.run([sys.executable, '-I', os.path.abspath(__file__), '--make', kind, src, dst],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode != 0:
        raise SystemExit('고장 %s 만들기 실패: %s' % (kind, p.stderr[-500:]))
    return int([ln for ln in p.stdout.splitlines() if ln.strip().isdigit()][-1])   # SWIG 경고 줄이 섞여 나온다


def run(carrier, front, cfg, tag, workdir):
    js = os.path.join(workdir, 'result-%s.json' % tag)
    cmd = [sys.executable, '-I', os.path.join(ROOT, 'ev_check.py'), '--config', cfg,
           '--board', 'carrier=' + carrier, '--board', 'front=' + front, '--json-out', js]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    with open(js, encoding='utf-8') as f:
        res = json.load(f)
    with open(os.path.join(workdir, 'stdout-%s.txt' % tag), 'w', encoding='utf-8') as f:
        f.write(p.stdout)
    return p.returncode, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--carrier', required=True)
    ap.add_argument('--front', required=True)
    ap.add_argument('--config', default=os.path.join(ROOT, 'ev_config.json'))
    ap.add_argument('--workdir', required=True)
    a = ap.parse_args()
    os.makedirs(a.workdir, exist_ok=True)
    fa = os.path.join(a.workdir, 'carrier-faultA.kicad_pcb')
    fb = os.path.join(a.workdir, 'front-faultB.kicad_pcb')
    fc = os.path.join(a.workdir, 'front-faultC.kicad_pcb')
    fd = os.path.join(a.workdir, 'carrier-faultD.kicad_pcb')
    fe = os.path.join(a.workdir, 'carrier-faultE.kicad_pcb')
    print('고장 A 트랙 %d개, B 트랙 %d개, C 트랙 %d개, D 영역 %d개, E 영역 %d개 변경' %
          (make_fault_proc(a.carrier, fa, 'A'), make_fault_proc(a.front, fb, 'B'), make_fault_proc(a.front, fc, 'C'),
           make_fault_proc(a.carrier, fd, 'D'), make_fault_proc(a.carrier, fe, 'E')))
    rc0, r0 = run(a.carrier, a.front, a.config, 'base', a.workdir)
    base_fail = {(i['target'], i['metric']) for i in r0['items'] if i['result'] == '불합격'}

    def new_fails(r):
        return [i for i in r['items'] if i['result'] == '불합격' and (i['target'], i['metric']) not in base_fail]
    bad = 0
    checks = []
    rcA, rA = run(fa, a.front, a.config, 'A', a.workdir)
    nA = new_fails(rA)
    checks.append(('A 12V_IN_RAW 0.40mm', rcA, rc0 + 1,
                   len(nA) == 1 and nA[0]['target'] == 'carrier:/12V_IN_RAW' and '트랙' in nA[0]['metric'], nA))
    rcB, rB = run(a.carrier, fb, a.config, 'B', a.workdir)
    nB = new_fails(rB)
    checks.append(('B CSI_L1 폭 0.21', rcB, rc0 + 1,
                   len(nB) == 1 and nB[0]['target'] == 'front:CSI_L1' and nB[0]['area'] == '①임피던스', nB))
    rcC, rC = run(a.carrier, fc, a.config, 'C', a.workdir)
    unrC = [i for i in rC['items'] if i['result'] == '미배선' and i['target'].startswith('front:/12V_IR')]
    checks.append(('C 전면 12V_IR 삭제', rcC, rc0, len(unrC) >= 1 and not new_fails(rC), unrC))
    rcAB, rAB = run(fa, fb, a.config, 'AB', a.workdir)
    checks.append(('AB 동시', rcAB, rc0 + 2, len(new_fails(rAB)) == 2, new_fails(rAB)))
    rcD, rD = run(fd, a.front, a.config, 'D', a.workdir)
    nD = new_fails(rD)
    checks.append(('D 탈출·보정 영역 삭제', rcD, rc0 + len(nD),
                   len(nD) >= 1 and all('비결합' in d['metric'] for d in nD) and any(d['target'] == 'carrier:MDI_RX' for d in nD), nD))
    rcE, rE = run(fe, a.front, a.config, 'E', a.workdir)
    nE = new_fails(rE)
    checks.append(('E 꼬임 영역 삭제', rcE, rc0 + len(nE),
                   any(d['target'] == 'carrier:MDI_RX' and '쌍 안 길이 차' in d['metric'] for d in nE), nE))
    lim = {(i['target'], i['metric'].split(' (')[0]): i['limit'] for i in r0['items']}
    k_mm, k_unc = '쌍 안 길이 차 mm', '비결합 mm, 꼬임 영역 밖'
    g_ok = ('1.27' in lim.get(('carrier:MDI_TX', k_mm), '') and '#62' in lim.get(('carrier:MDI_TX', k_mm), '')
            and lim.get(('carrier:MDI_TX', k_unc), '').startswith('≤ 7')
            and lim.get(('carrier:MDI_RX', k_mm), '').startswith('0 ')
            and lim.get(('carrier:MDI_RX', k_unc), '') == '≤ 6')
    checks.append(('G 한도 표기 TX#62·RX#28', 0, 0, g_ok,
                   [{'result': '한도', 'target': k[0], 'metric': k[1], 'value': v} for k, v in lim.items() if 'MDI' in k[0] and k[1] in (k_mm, k_unc)]))
    print('원본 종료 코드 %d (불합격 %d, 미배선 %d)' % (rc0, r0['fails'], r0['unrouted_items']))
    ok0 = rc0 == min(r0['fails'], 125)
    bad += 0 if ok0 else 1
    for name, rc, exp, extra, detail in checks:
        ok = rc == exp and extra
        bad += 0 if ok else 1
        print('%s %-22s 종료 코드 %d (기대 %d) · 새 항목: %s' % ('통과' if ok else '실패', name, rc, exp,
              '; '.join('[%s] %s %s = %s' % (d['result'], d['target'], d['metric'], d['value']) for d in detail)))
    print('기대와 다른 경우 %d' % bad)
    return bad


if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == '--make':
        print(make_fault(sys.argv[3], sys.argv[4], sys.argv[2]))
        sys.exit(0)
    sys.exit(main())
