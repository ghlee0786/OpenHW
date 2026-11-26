#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ev_check.py 식 단위 시험 — 공개 값·이전 검토값과 대조. 종료 코드 = 실패 수.
실행: python.exe -I tests/test_formulas.py   (KiCad 동봉 Python, pcbnew 필요: ev_check 가 import 한다)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ev_check as ev  # noqa: E402

H, T, ER = 0.1855, 0.035, 4.74   # P-001 §2.1 / 보드 stackup L1–In1
cases = [
    # (이름, 계산값, 기대값, 허용 오차)
    ('IPC-2141A w0.15 s0.16 (V-005 A6 109.1)', ev.ipc2141_microstrip_zdiff(0.15, 0.16, H, T, ER), 109.1, 0.05),
    ('IPC-2141A w0.15 s0.17 (V-005 A6 110.6)', ev.ipc2141_microstrip_zdiff(0.15, 0.17, H, T, ER), 110.6, 0.05),
    ('IPC-2141A w0.20 s0.16 (V-005 A6 96.4)', ev.ipc2141_microstrip_zdiff(0.20, 0.16, H, T, ER), 96.4, 0.05),
    ('IPC-2141A w0.20 s0.17 (V-005 A6 97.7)', ev.ipc2141_microstrip_zdiff(0.20, 0.17, H, T, ER), 97.7, 0.05),
    ('IPC-2152 맞춤 예제 10 A, ΔT20 → 513 mil² (smps.us)', ev.ipc2152_area_mil2(10.0, 20.0), 513.0, 1.0),
    ('IPC-2152 역함수 왕복', ev.ipc2152_current_a(ev.ipc2152_area_mil2(1.84, 10.0) * ev.MIL ** 2, 10.0), 1.84, 1e-9),
    ('IPC-2152 ΔT 역산 왕복', ev.ipc2152_dt_k(1.0, 0.15 * 0.035), None, None),
    ('IPC-2221 외층 0.78 mm 1oz ΔT10 → 2.0 A (netclasses.md §3.1)', ev.ipc2221_current_a(0.78 * 0.035, 10, True), 2.0, 0.02),
    ('IPC-2221 외층 0.53 mm 1oz ΔT10 → 1.5 A (netclasses.md §3.1)', ev.ipc2221_current_a(0.53 * 0.035, 10, True), 1.5, 0.02),
    ('비아 원통 0.30/25µm = π·t·(d−t)', ev.via_barrel_area_mm2(0.30, 0.025), 3.14159265 * 0.025 * 0.275, 1e-9),
]
fails = 0
for name, got, exp, tol in cases:
    if exp is None:
        ok = abs(ev.ipc2152_current_a(0.15 * 0.035, got) - 1.0) < 1e-6
        print('%s %-55s ΔT=%.3f K' % ('통과' if ok else '실패', name, got))
    else:
        ok = abs(got - exp) <= tol
        print('%s %-55s 계산 %.4f 기대 %.4f ±%g' % ('통과' if ok else '실패', name, got, exp, tol))
    fails += 0 if ok else 1

# 저항망 풀이: 1 Ω 두 개 병렬 + 1 Ω 직렬 → 1 A 일 때 강하 1.5 V, 병렬 가지 0.5 A
class G:
    pass
g = G()
g.n = 3
g.edges = [(0, 1, 1.0, {'kind': 'track', 'id': 'a'}), (0, 1, 1.0, {'kind': 'track', 'id': 'b'}),
           (1, 2, 1.0, {'kind': 'track', 'id': 'c'})]
cur, drops, ur = ev.solve_network(g, [0], [([2], 1.0)])
I = {info['id']: i for info, i in cur}
ok = abs(drops[0] - 1.5) < 1e-9 and abs(I['a'] - 0.5) < 1e-9 and abs(I['c'] - 1.0) < 1e-9 and not ur
print('%s 저항망 풀이 (강하 %.3f V, 가지 %.3f A)' % ('통과' if ok else '실패', drops[0], I['a']))
fails += 0 if ok else 1
print('실패 %d' % fails)
sys.exit(fails)
