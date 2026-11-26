"""R-017 PoC 총비용 추정표 CSV 생성 (5대, USD). 실행: python -I docs/research/r017/make_cost_csv.py docs/research/r017-poc-cost.csv"""
import collections
import csv
import sys

D = '2026-11-27'
R = [
    # 구분, 항목, 조건, 최소, 기준, 최대, 상태, 출처, 비고
    ('전장', 'PCBA 턴키 부품 (캐리어+전면, 스트링 B 포함)',
     'bom-full(main 533d1b8) 62품번, 5보드 실장 수량. 최소=수량×단가, 기준=MOQ 반영, 최대=기준×1.15(손실·마크업 가정)',
     99.15, 107.14, 123.21, '확인(단가)·추정(최대)', 'docs/research/bom-full.csv (LCSC·Digi-Key 2026-11-26~27)',
     'PCBWay 턴키 부품 마크업 미확인'),
    ('전장', '위탁 부품: VSMA1085400 ×20 + CLA216-ICR',
     '최소=VSMA 20×2.34 + CLA216 5×12. 기준=CLA216 6개(예비 1). 최대=VSMA 22×3.21 + CLA216 6개',
     106.80, 118.80, 142.62, '확인',
     'https://www.digikey.com/en/products/result?keywords=751-VSMA1085400CT-ND ; https://ko.commonlands.com/products/ir-cut-off-filter-switcher-m12-cla216', ''),
    ('전장', 'PCB 제작 2종 (40×40, 4층 1.6mm, ENIG 1U, 임피던스 제어, 5/5mil, 비아 0.2)',
     'PCBWay 공개 계산기 표시값. 최소=두 설계를 한 고객 패널 80×100에 넣어 5패널(각 10장) 174.00. 기준=Panel by Supplier 5장 ×2. 최대=패널+via-in-pad(POFV) ×2',
     174.00, 286.76, 460.10, '확인(계산기 표시값, 검토 후 확정)', 'https://www.pcbway.com/orderonline.aspx',
     '맨 PCB 10장/설계: 135.37~231.92'),
    ('전장', 'PCBA 조립비 2종 (스텐실 포함, 5장)',
     'PCBWay 공개 계산기. 최소=캐리어 $29 프로모션(전량 턴키, 1건 한정) + 전면 Combo 88. 기준=88+88. 최대=88+91.63+X-ray(JLC 단가 참고 41.00)',
     117.00, 176.00, 220.63, '확인(계산기)·X-ray 미확인',
     'https://www.pcbway.com/orderonline.aspx ; https://jlcpcb.com/help/article/pcb-assembly-price',
     'BGA 없음. 5장은 단면·양면 같은 값'),
    ('전장', '위탁 부품 처리비·중국 발송',
     'PCBWay는 금액 미공개. JLC 기준(신고가 2%, 최소 $10)과 DHL 공시 요금(0.5kg ₩161,800)을 참고',
     10.00, 40.00, 130.00, '미확인(범위)',
     'https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb ; https://mydhl.express.dhl/content/dam/downloads/kr/en/rate-guide/service_and_rate_guide_kr_en_2026.pdf',
     'Digi-Key→PCBWay 직배송이면 줄어듦'),
    ('모듈', 'reCamera Core 2002 8GB (101991223)', 'Seeed 60.63/개. 최소·기준 5개, 최대 6개(예비 1)',
     303.15, 303.15, 363.78, '확인', 'https://www.seeedstudio.com/reCamera-Core-2002-8GB-p-6433.html',
     'Digi-Key 31.25는 등록 오류 의심이라 쓰지 않음'),
    ('모듈', 'S401 GC2053 센서 보드 (100041077) → BXF4677 모듈 사용',
     '27.51/개. 최소 5개, 기준·최대 7개(분리 시험 1 + 예비 1, R-006 M1)',
     137.55, 192.57, 192.57, '확인', 'https://www.seeedstudio.com/reCamera-2002-Sensor-Board-GC2053-p-6556.html',
     'BXF4677 단품은 공개 판매처 없음'),
    ('광학', '렌즈 CIL093-F2.4-M12ANIR', '129.00/개(5개 할인 없음, 50개부터). 최소 5개, 기준·최대 6개(예비 1)',
     645.00, 774.00, 774.00, '확인',
     'https://ko.commonlands.com/collections/m12-lenses/products/glass-low-distortion-3mm-m12-lens',
     '본 도메인 429 → ko·de 미러 두 곳에서 같은 값'),
    ('외함', '3D 프린트 PETG 본체+앞 덮개 ×5',
     '재료 약 301~603g. 최소/기준=필라멘트 1kg 스풀(SUNLU 10.49 / MatterHackers 20.99). 최대=서비스 시작가 약 95 ×2종(미확인)',
     10.49, 20.99, 190.00, '확인(필라멘트)·미확인(서비스)',
     'https://www.prusa3d.com/product/prusament-petg-jet-black-1kg/ ; https://www.protolabs.com/help-center/pricing-and-payment-options/',
     '출력 시간 약 12~39h(추정). JLC3DP FDM 재료에 PETG 없음'),
    ('외함', 'Al H3 바깥 방열판 CNC + 흑색 아노다이즈 ×5',
     '최소=압출 방열판 봉(Wakefield 125349 22.60 ×2, 받침·아노다이즈 별도). 기준=PCBWay CNC 후기 41~90/개의 중간. 최대=SendCutSend 아노다이즈 예시 376.79/개',
     45.20, 327.50, 1883.95, '미확인(범위)',
     'https://www.pcbway.com/project/share/CNC_Heatsink_Project_8be431f1.html ; https://sendcutsend.com/services/anodizing',
     '업로드 견적 없이는 확정할 수 없음'),
    ('외함', '내부 Al 스프레더 CNC ×5', 'JLCCNC From $5 ~ Protolabs 약 $65/개',
     25.00, 175.00, 325.00, '미확인(범위)',
     'https://jlc3dp.com/ ; https://www.protolabs.com/help-center/pricing-and-payment-options/', ''),
    ('외함', 'PMMA 레이저 창 (3mm 3종 + 1.5mm ALS) ×5',
     '최소=Elecrow 특가 1 + 1/16in 원판. 기준=Pololu 최소 25 + 원판 7.79. 최대=Ponoko 50 ×2두께',
     4.59, 32.79, 100.00, '확인(단가표)·추정',
     'https://www.pololu.com/docs/0J24/2 ; https://www.elecrow.com/acrylic-cutting.html ; https://www.ponoko.com/laser-cutting/acrylic',
     '1.5mm는 원판을 사서 손으로 자름'),
    ('외함', '폼 링·개스킷 + Tflex P340 + 1.5mm 열 패드', 'Tflex A17747-04 9×9in 64.54 1장, 폼 시트, 1.5mm 패드',
     86.07, 103.56, 135.58, '확인(일부는 검색 요약)', 'https://www.digikey.com/en/products/result?keywords=A17747-04',
     '정확히 1.0mm인 폼은 미확인'),
    ('외함', '기구 하드웨어 (인서트·나사·너트·M1.6 스탠드오프·맞춤 17.6·고정제·창 접착)', '포장 단위 포함',
     142.58, 189.20, 305.81, '확인(일부)·미확인(M1.6 스탠드오프·맞춤)', 'https://www.zoro.com/ ; https://www.digikey.com/', ''),
    ('외부', '어댑터 Mean Well GST25A12-P1J ×5', '5+ 13.60 / 1+ 14.30',
     68.00, 68.00, 71.50, '확인', 'https://www.digikey.com/en/products/result?keywords=1866-2090-ND', '납기 17주'),
    ('외부', 'AC 코드 GlobTek 2313K3432M5701(R) ×5', '1+ 8.41',
     42.05, 42.05, 42.05, '확인', 'https://www.digikey.com/en/products/result?keywords=1939-1616-ND', 'KC 인증번호 미확인(R-009)'),
    ('하니스', 'GH 6P 하니스 ×6(예비 1): JST 압착 리드 AGHGH28K51 + 하우징 GHR-06V-S (R-017b, O-76)',
     '최소=리드 36×0.3424(25+) + 하우징 12×0.136(10+). 기준·최대=리드 50×0.326(50+) + 하우징 25×0.128(25+)',
     13.96, 19.50, 19.50, '확인(Digi-Key 재고 44,400 / 103,701)',
     'https://www.digikey.com/en/products/detail/jst-sales-america-inc/AGHGH28K51/6009448 ; https://www.digikey.com/en/products/detail/jst-sales-america-inc/GHR-06V-S/807818 ; https://www.farnell.com/datasheets/4803928.pdf',
     '28AWG 51mm(최단 표준, 35mm 맞춤 미확인). 정격 1.0A(28AWG GH 리드 도면, 검색 요약) ≥ 0.61A. 손으로 삽입하며 결선은 조립자가 정함. 차선(합계 제외): 자가 압착 Alpha Wire 197.28 + 압착기 51.95~1564.89'),
]
SHIP = [
    ('배송·관세(표시만)', '중국발 특송 (PCBWay·Seeed)',
     'DHL 공시 Zone1 0.5kg ₩161,800 / 1kg ₩184,400(정가, 할증 별도). 업체 협상 요금은 주문 화면에서만 보임',
     '미확인', 'https://mydhl.express.dhl/content/dam/downloads/kr/en/rate-guide/service_and_rate_guide_kr_en_2026.pdf'),
    ('배송·관세(표시만)', 'Digi-Key → 한국',
     '₩60,000(USD 50) 이상 무료, 미만 ₩20,000. CPT 조건(관세·VAT는 수입자 부담)',
     '확인', 'https://www.digikey.kr/en/help-support/delivery-information/delivery-time-and-cost'),
    ('배송·관세(표시만)', '한국 통관',
     '목록통관 USD 150(미국발 200) 이하 — 개인 자가사용·기업 샘플 한정. 넘으면 (과세가격+운임)에 관세 0~8% + VAT 10%',
     '확인(한도)·미확인(세율, 2차 출처)', 'https://www.customs.go.kr/kcs/cm/cntnts/cntntsView.do?mi=2821&cntntsId=819'),
]

w = csv.writer(open(sys.argv[1], 'w', encoding='utf-8-sig', newline=''), lineterminator='\n')
w.writerow(['구분', '항목', '조건', '최소_USD_5대', '기준_USD_5대', '최대_USD_5대', '기준_USD_대당', '상태', '출처', '확인일', '비고'])
t = [0.0, 0.0, 0.0]
sub = collections.OrderedDict()
for g, i, c, a, b, m, s, u, n in R:
    for k, v in enumerate((a, b, m)):
        t[k] += v
        sub.setdefault(g, [0.0, 0.0, 0.0])[k] += v
    w.writerow([g, i, c, f'{a:.2f}', f'{b:.2f}', f'{m:.2f}', f'{b / 5:.2f}', s, u, D, n])
for g, i, c, s, u in SHIP:
    w.writerow([g, i, c, '', '', '', '', s, u, D, '합계에 넣지 않음'])
w.writerow(['합계', '배송·관세 제외', '', f'{t[0]:.2f}', f'{t[1]:.2f}', f'{t[2]:.2f}', f'{t[1] / 5:.2f}', '', '', D,
            f'대당 최소 {t[0] / 5:.2f} · 최대 {t[2] / 5:.2f}'])
print('total', [round(x, 2) for x in t], 'per unit', [round(x / 5, 2) for x in t])
for g, v in sub.items():
    print(g, [round(x, 2) for x in v], 'per unit', [round(x / 5, 2) for x in v])
