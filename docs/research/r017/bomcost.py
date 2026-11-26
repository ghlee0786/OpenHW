"""R-017 전장 부품값: bom-full.csv의 [캐리어]/[전면] 실장 행을 MPN별로 합쳐 5보드 비용(최소=수량x단가, 기준=MOQ 반영)을 낸다.

실행: python -I docs/research/r017/bomcost.py docs/research/bom-full.csv <출력.txt>
"""
import csv,re,sys,collections
rows=list(csv.reader(open(sys.argv[1],encoding='utf-8-sig',newline='')))
c={k:i for i,k in enumerate(rows[0])}
agg=collections.OrderedDict()
for r in rows[1:]:
    ref=r[c['Reference']]
    if not (ref.startswith('[캐리어]') or ref.startswith('[전면]')): continue
    m=re.search(r'5보드 실장 (\d+)',r[c['Quantity']]);
    q=int(m.group(1)) if m else 0
    if q==0: continue
    mpn=r[c['MPN']]
    price=float(re.match(r'[\d.]+',r[c['UnitPrice']]).group(0))
    moq=re.match(r'\d+',r[c['MOQ']] or '1'); moq=int(moq.group(0)) if moq else 1
    cons='위탁' in r[c['AssemblyNotes']] and 'VSMA' not in mpn or ('VSMA' in mpn)
    a=agg.setdefault(mpn,{'q':0,'price':price,'moq':moq,'refs':[],'cons':cons,'board':set()})
    a['q']+=q; a['refs'].append(ref); a['board'].add(ref.split(']')[0][1:])
# VSMA 10+ tier
tiers={'VSMA1085400':2.34,'AL8860MP-13':1.0868,'HC-PBB05-2-60-M-H4.0-G1-R-P-04':1.133,'HC-PBB05-2-60-F-H4.0-G1-R-P-04':1.078}
tot={'min':0,'base':0}; cons_tot={'min':0,'base':0}
out=[]
for mpn,a in agg.items():
    p=tiers.get(mpn,a['price']) if a['q']>=10 else a['price']
    mn=a['q']*p; bs=max(a['q'],a['moq'])*p
    k=cons_tot if a['cons'] else tot
    k['min']+=mn; k['base']+=bs
    out.append((mpn,a['q'],a['moq'],p,round(mn,4),round(bs,4),'위탁' if a['cons'] else '턴키'))
o=open(sys.argv[2],'w',encoding='utf-8')
for x in out: o.write('\t'.join(map(str,x))+'\n')
o.write(f"turnkey min {tot['min']:.2f} base {tot['base']:.2f} | consigned min {cons_tot['min']:.2f} base {cons_tot['base']:.2f} | lines {len(out)}\n")
