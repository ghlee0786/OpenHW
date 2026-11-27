# -*- coding: utf-8 -*-
"""V-006a(O-107): 참조 지정자가 실크(O-65)와 Fab(조립도 R-010)에 각각 몇 개 있는지 센다.

사용: KiCad python -I v006a_refs.py <보드.kicad_pcb> <out.json>
- 실크 참조: Reference 필드가 보이는 채로 F/B.SilkS, 또는 사용자 글자 ${REFERENCE} 가 F/B.SilkS
- Fab 참조: Reference 필드가 F/B.Fab, 또는 사용자 글자 ${REFERENCE} 가 F/B.Fab (숨김 아님)
- 필요 대상: 실장 부품(attr board_only 아님, 라이브러리 MountingHole·TestPoint·Fiducial·NetTie·Symbol 아님 — REN-002 감사와 같은 기준)
종료 코드 = 0 (판정은 v006a_pre.py), 입력 오류 100
"""
import sys, json
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
if len(sys.argv) != 3:
    print(__doc__); sys.exit(100)
b = pcbnew.LoadBoard(sys.argv[1])
NO_REF_LIBS = ('MountingHole', 'TestPoint', 'Fiducial', 'NetTie', 'Symbol')
rows = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    lib = str(fp.GetFPID().GetLibNickname())
    need = not fp.IsBoardOnly() and lib not in NO_REF_LIBS
    silk, fab = [], []
    f = fp.Reference()
    ln = b.GetLayerName(f.GetLayer())
    if f.IsVisible():
        if ln.endswith('.SilkS') or ln.endswith('.Silkscreen'):
            silk.append('field ' + ln)
        elif ln.endswith('.Fab'):
            fab.append('field ' + ln)
    for g in fp.GraphicalItems():
        if g.GetClass() in ('PCB_TEXT', 'FP_TEXT') and g.GetText() == '${REFERENCE}' and g.IsVisible():
            gl = b.GetLayerName(g.GetLayer())
            if gl.endswith('.SilkS') or gl.endswith('.Silkscreen'):
                silk.append('text ' + gl)
            elif gl.endswith('.Fab'):
                fab.append('text ' + gl)
    rows.append(dict(ref=ref, lib=lib, side='B' if fp.IsFlipped() else 'F', need=need, silk=silk, fab=fab))
need = [r for r in rows if r['need']]
R = dict(board=sys.argv[1], footprints=len(rows), need=len(need),
         silk=sum(1 for r in need if r['silk']), fab=sum(1 for r in need if r['fab']),
         no_silk=sorted(r['ref'] for r in need if not r['silk']), no_fab=sorted(r['ref'] for r in need if not r['fab']),
         rows=rows)
json.dump(R, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('풋프린트 %d · 대상 %d · 실크 참조 %d · Fab 참조 %d · 실크 없음 %d · Fab 없음 %d' % (len(rows), len(need), R['silk'], R['fab'], len(R['no_silk']), len(R['no_fab'])))
