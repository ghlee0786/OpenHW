#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""고장 주입 시험. 원본 보드의 사본에 고장을 넣어 ev_check.py 가 잡는지 종료 코드로 확인한다.

  A  캐리어 /12V_IN_RAW 트랙 전부를 0.40 mm 로 좁힘          → 기대: 원본 + 1 (그 넷 트랙 항목 불합격)
  B  전면 CSI_L1 P/N 트랙 폭 0.15 → 0.21 mm (중심선 그대로)    → 기대: 원본 + 1 (CSI_L1 임피던스 불합격)
  C  전면 /12V_IR 트랙 전부 삭제 (미배선)                      → 기대: 원본과 같음, 그 넷 항목은 「미배선」으로 따로 셈 (멈추지 않음)
  AB A+B 동시                                                 → 기대: 원본 + 2

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
    if n == 0:
        raise SystemExit('고장 %s: 바꿀 트랙이 없다' % kind)
    pcbnew.SaveBoard(dst, b)
    return n


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
    print('고장 A 트랙 %d개, B 트랙 %d개, C 트랙 %d개 변경' %
          (make_fault(a.carrier, fa, 'A'), make_fault(a.front, fb, 'B'), make_fault(a.front, fc, 'C')))
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
    sys.exit(main())
