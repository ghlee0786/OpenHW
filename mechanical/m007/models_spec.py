# M-007 대체 3D 모델 사양 (CAD 독립). 몸체 XY = KiCad 표준 풋프린트 F.Fab 외곽(풋프린트 로컬 좌표), 리드 = 패드 범위 두께 0.15, 높이 = 데이터시트.
# 원점 = 풋프린트 원점, 회전 0, 단위 mm, +Z = 부품 윗면 방향(보드 윗면 기준). KiCad 3D 설정: offset 0, rotation 0, scale 1 (뒷면 실장은 KiCad 가 뒤집음).
import os
KICAD_FP = os.environ.get('KICAD10_FOOTPRINT_DIR') or os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\share\kicad\footprints')   # KiCad 10 설치
MODELS = [
    # 파일 이름, 풋프린트(라이브러리/이름), 높이, 높이 근거, 쓰는 자리
    ('USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'Connector_USB.pretty/USB_C_Receptacle_HRO_TYPE-C-31-M-12', 3.26,
     'HRO TYPE-C-31-M-12 REV A (2020-12-08) 측면도 3.26 — https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948 (원문 확인 2026-11-27)', '캐리어 J3'),
    ('RJ45_Hanrun_HR911105A_Horizontal', 'Connector_RJ.pretty/RJ45_Hanrun_HR911105A_Horizontal', 13.50,
     'HanRun HR911105A REV A/2 p2 높이 13.50 — https://datasheet.lcsc.com/datasheet/pdf/0ad5e0c00dfc47fb8e582f15f877f290.pdf?productCode=C12074 (원문 확인 2026-11-27)', '캐리어 J5'),
    ('L_Bourns_SRP7028A_7.3x6.6mm', 'Inductor_SMD.pretty/L_Bourns_SRP7028A_7.3x6.6mm', 3.0,
     'Bourns SRP7028A 높이 2.8 ±0.2 → 최대 3.0 — Farnell 사본 https://www.farnell.com/datasheets/2907623.pdf (2차 출처)', '캐리어 L1'),
    ('SOT-523', 'Package_TO_SOT_SMD.pretty/SOT-523', 0.90,
     'SOT-523 전체 높이 A 0.60–0.90 (최대) — Union-IC Outline SOT523 Rev.02 https://union-ic.com/upload/file/Outline%20Drawing/Outline-SOT523.pdf (2차 출처)', '캐리어 Q3·Q4, 전면 Q3·Q5·Q7'),
    ('Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm', 'Oscillator.pretty/Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm', 0.80,
     'SiTime 2.0×1.6 QFN 높이 0.75 (유통사 표기, 미확인) → 0.80 여유 — https://www.sitime.com/datasheet/SiT8008', '전면 X1'),
]
