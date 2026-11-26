# REN-002 대체 3D 모델 사양 + 풋프린트 → 모델 연결 표 (CAD 독립).
# 규칙은 M-007 과 같다: 원점 = 풋프린트 원점, 회전·오프셋 0, 배율 1, mm, +Z = 부품 윗면(보드 윗면 기준). 몸체 XY = 풋프린트 F.Fab 외곽, 리드 = 패드 범위 두께 0.15.
# 경로 (보드 파일 기준): ${KIPRJMOD}/../../../mechanical/models/<파일>.step
OPENHW_FP = 'hardware/libraries/openhw.pretty'      # pcb 저장소 안 경로 (감사 때 꺼낸 pcbsrc 기준)
MODEL_DIR = '${KIPRJMOD}/../../../mechanical/models'

# 새로 만드는 것 (M-007 5종은 mechanical/m007/models_spec.py)
NEW = [
    # 파일 이름, openhw 풋프린트 이름, 높이, 높이 근거, 쓰는 자리
    ('BTB_ST-BTB-058060-A_2x30_P0.5mm', 'BTB_ST-BTB-058060-A_2x30_P0.5mm', 4.0,
     '[가정] 짝 결합 높이 8.00 (D-003 #20, M-006 3사 높이표)의 절반 — 플러그 단품 높이 원문 없음. 렌더·외형용', '캐리어 J1 (HCTL HC-PBB05-2-60-M-H4.0)'),
    ('BTB_ST-BTB-058060-B_2x30_P0.5mm', 'BTB_ST-BTB-058060-B_2x30_P0.5mm', 4.0,
     '[가정] 위와 같음 (소켓 단품 높이 원문 없음)', '전면 J1 (HC-PBB05-2-60-F-H4.0, 뒷면)'),
    ('Vishay_VSMA1085600_3.4x3.4mm', 'Vishay_VSMA1085600_3.4x3.4mm', 2.445,
     'Vishay VSMA1085400 데이터시트 Rev 1.4 높이 2.445 (R-007 ③, stack-reference §2 led_h) — https://www.vishay.com/docs/80294/', '전면 D_IR_A1·A2·B1·B2'),
    ('Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm', 'Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm', 0.9,
     'Hirose DF30 카탈로그: 24핀 DS 리셉터클 7.02 × 4.4, 결합 높이 0.9 (리셉터클 단품은 그 이하 → 결합 높이를 외형 상한으로) — https://www.mouser.com/datasheet/2/185/ed_DF30_20210203-2301922.pdf', '전면 J3'),
    ('Lite-On_LTR-329ALS-01_2x2mm_P1.2mm', 'Lite-On_LTR-329ALS-01_2x2mm_P1.2mm', 0.7,
     'Lite-On LTR-329ALS-01: 2.0 × 2.0 × 0.7 (Mouser 제품 소개·Arrow 높이 0.7 최대, 2차 출처 — 원문 도면 수치 미확인) — https://www.arrow.com/en/products/ltr-329als-01_1/lite-on-technology.html', '전면 U3'),
    ('Everlight_ALS-PT19_1.7x0.8mm', 'Everlight_ALS-PT19_1.7x0.8mm', 0.6,
     'Everlight ALS-PT19-315C/L177/TR8 데이터시트: 1.7(L) × 0.8(W) × 0.6(H) — https://www.mouser.com/datasheet/2/813/ALS_PT19_315C_L177_TR8-2525651.pdf', '전면 Q4 (대체 부품)'),
    ('M12_Holder_20mm_CLA216-ICR', 'M12_Holder_20mm_CLA216-ICR', None,
     'M-008 cla216_spec.py: 스페이서 1.5 + CLA216 높이 7.6 (R-007 도면 판독) + ICR 리드 — 홀더 축 = 풋프린트 원점', '전면 MH1'),
]

# 풋프린트(라이브러리:이름) → 모델 파일. 감사에서 빠진 것 전부 (pcb 23fd8da 기준 12종 19개)
LINK = {
    'Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal': 'RJ45_Hanrun_HR911105A_Horizontal',
    'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12': 'USB_C_Receptacle_HRO_TYPE-C-31-M-12',
    'Inductor_SMD:L_Bourns_SRP7028A_7.3x6.6mm': 'L_Bourns_SRP7028A_7.3x6.6mm',
    'Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm': 'Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm',
    'Package_TO_SOT_SMD:SOT-523': 'SOT-523',
    **{'openhw:' + fp: name for name, fp, *_ in NEW},
}
