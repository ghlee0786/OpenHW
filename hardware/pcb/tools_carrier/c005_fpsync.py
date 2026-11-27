"""캐리어: 보드 부품을 실크 사본 라이브러리의 같은 풋프린트로 바꿔 끼운다 (KiCad pcbnew, GUI 닫고).

silk_lib.py 2단계가 사본의 실크를 자리 기준으로 다시 자른 뒤(외곽 0.30 등), 보드 부품도 같은 그림이 되게 한다(lib_footprint_mismatch 0).
자리 · 방향 · 면 · 참조/값 글자 자리 · 패드 넷 · 회로도 경로 · 속성은 그대로 옮긴다. 판정은 뒤의 kicad-cli DRC(parity · 불일치 · 미연결).
사용: <KiCad>/bin/python.exe c005_fpsync.py <carrier.kicad_pcb> <사본 폴더(…/lib/silk/carrier)> <참조> [참조 …]
"""
import sys
from pathlib import Path

import pcbnew

path, libroot, refs = sys.argv[1], Path(sys.argv[2]), sys.argv[3:]
b = pcbnew.LoadBoard(path)
fps = {f.GetReference(): f for f in b.GetFootprints()}
for ref in refs:
    old = fps[ref]
    fpid = old.GetFPID()
    lib, name = str(fpid.GetLibNickname()), str(fpid.GetLibItemName())
    new = pcbnew.FootprintLoad(str(libroot / f"{lib}.pretty"), name)
    if new is None:
        raise SystemExit(f"사본 없음: {lib}:{name}")
    new.SetFPID(fpid)
    b.Add(new)  # Flip 은 보드에 올린 뒤에만 된다(보드 밖 풋프린트는 죽는다)
    new.SetPosition(old.GetPosition())
    if old.IsFlipped():
        new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    new.SetOrientation(old.GetOrientation())
    new.SetPath(old.GetPath())
    new.SetSheetfile(old.GetSheetfile())
    new.SetSheetname(old.GetSheetname())
    new.SetAttributes(old.GetAttributes())
    new.SetLocked(old.IsLocked())
    for getter in ("Reference", "Value"):
        o, n = getattr(old, getter)(), getattr(new, getter)()
        n.SetText(o.GetText())
        n.SetLayer(o.GetLayer())
        n.SetVisible(o.IsVisible())
        n.SetPosition(o.GetPosition())
        n.SetTextAngle(o.GetTextAngle())
        n.SetTextSize(o.GetTextSize())
        n.SetTextThickness(o.GetTextThickness())
        n.SetMirrored(o.IsMirrored())
        n.SetKeepUpright(o.IsKeepUpright())
    for of in old.GetFields():
        nm = of.GetName()
        if nm in ("Reference", "Value"):
            continue
        nfs = {f.GetName(): f for f in new.GetFields()}
        if nm not in nfs:
            new.SetField(nm, of.GetText())
            nfs = {f.GetName(): f for f in new.GetFields()}
        nf = nfs[nm]
        nf.SetText(of.GetText())
        nf.SetVisible(of.IsVisible())
        nf.SetLayer(of.GetLayer())
        nf.SetPosition(of.GetPosition())
    opads = [q for q in old.Pads()]
    miss = 0
    for p in new.Pads():
        cand = [q for q in opads if q.GetNumber() == p.GetNumber()]
        if not cand:
            miss += 1
            continue
        q = min(cand, key=lambda q: (q.GetPosition().x - p.GetPosition().x) ** 2 + (q.GetPosition().y - p.GetPosition().y) ** 2)
        d = max(abs(q.GetPosition().x - p.GetPosition().x), abs(q.GetPosition().y - p.GetPosition().y))
        if d > 2000:
            raise SystemExit(f"{ref} 패드 {p.GetNumber()} 자리가 다름 {pcbnew.ToMM(d):.4f}mm — 바꾸지 않음")
        p.SetNet(q.GetNet())
        p.SetPinFunction(q.GetPinFunction())
        p.SetPinType(q.GetPinType())
    b.Delete(old)  # Remove 는 swig 형 변환을 깨뜨린다
    print(ref, f"{lib}:{name}", "패드", len(list(new.Pads())), "못 맞춘 패드", miss)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(path)
