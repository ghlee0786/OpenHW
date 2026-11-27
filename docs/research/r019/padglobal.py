"""KiCad pcbnew로 보드를 읽기 전용으로 열어 BTB(J1) 패드 전역 좌표·넷, 장착 구멍, 외형 bbox를 JSON으로 쓴다."""
import pcbnew,sys,json
b=pcbnew.LoadBoard(sys.argv[1])
mm=lambda v: round(pcbnew.ToMM(v),4)
out={'holes':[],'bbox':None,'J1':None}
bb=b.GetBoardEdgesBoundingBox(); out['bbox']=[mm(bb.GetX()),mm(bb.GetY()),mm(bb.GetRight()),mm(bb.GetBottom())]
for fp in b.GetFootprints():
    ref=fp.GetReference(); pads=list(fp.Pads())
    if len(pads)>=40 and ref=='J1':
        out['J1']={'fp':str(fp.GetFPID().GetUniStringLibItemName()),'layer':fp.GetLayerName(),'pos':[mm(fp.GetPosition().x),mm(fp.GetPosition().y)],'rot':fp.GetOrientationDegrees(),
          'pads':[[p.GetNumber(),mm(p.GetPosition().x),mm(p.GetPosition().y),p.GetNetname(),p.GetAttribute()] for p in pads]}
    for p in pads:
        if p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH or ('Hole' in str(fp.GetFPID().GetUniStringLibItemName()) and p.GetDrillSize().x>0):
            out['holes'].append([ref,mm(p.GetPosition().x),mm(p.GetPosition().y),mm(p.GetDrillSize().x)])
json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(sys.argv[2], out['J1']['layer'] if out['J1'] else None, out['bbox'], len(out['holes']))
