# 데이터시트·참고 설계 보관 목록 (R-005, D-003 #14)

- 기준: D-003 #14. **공개 라이선스가 명시된 자료만** 이 폴더에 원본 그대로 둔다. Confidential 자료와 라이선스가 표기되지 않은 자료는 링크와 sha256만 남긴다.
- 확인일 **2026-11-26** · 작성 research t18s (R-005)
- 내려받기: 모두 공식 저장소에서 받았고 커밋을 고정했다. 내용은 수정하지 않았다.
- sha256: 앞선 조사(R-001·R-003·R-004·C-001)에서 기록한 값과 일치하는지 대조했다.
- 커밋 고정:

| 저장소 | 커밋 |
|---|---|
| sophgo/sophgo-hardware | `d20275b5083f6369b8acb9d04b57c099f5bbdc19` |
| sophgo/sophgo-doc | `5e9555e2102fe82ee1a552fa8e07963913bce7ac` (TRM은 릴리스 `sg2002-trm-v1.02` 자산) |
| Seeed-Studio/OSHW-reCamera-Series | `f5fcf0abce794806ffbd7a274686f022bb0acd4b` |
| antmicro/hardware-components | `2efa39671a166337538e6bef02a3d69a87babb95` |

## 보관한 원본

### sophgo/ — BSD 2-Clause (「Copyright (c) 2023, Sophgo Technologies」, `LICENSE.sophgo-hardware` · `LICENSE.sophgo-doc`)

| 파일 | 원본 URL | 리비전 | sha256 | 앞선 기록과 대조 |
|---|---|---|---|---|
| sg2002_trm_en_v1.02.pdf | https://github.com/sophgo/sophgo-doc/releases/download/sg2002-trm-v1.02/sg2002_trm_en_v1.02.pdf | v1.02, 2025-02-27 | 26ed9508ab701ba89226f2a74b0a1faa355cba251695233b7a89c2a2a21bda00 | 일치 (R-001) |
| 01_SG2002_Datasheet_V1.0_EN.docx | https://github.com/sophgo/sophgo-hardware/blob/master/SG200X/04_SG2002/01_SG2002_Datasheet/01_SG2002_Datasheet_V1.0_EN.docx | Preliminary 1.0-alpha, 2023-12-15 | 59b537396a7fd280a7a7525f713b75a574d1b32f1bf057c788b12b6a6f2418d0 | 일치 (R-001) |
| 02_SG2002_Hardware_Design_User_Guide_EN.docx | …/SG200X/04_SG2002/02_SG2002_Hardware_Design_User_Guide/02_SG2002_Hardware_Design_User_Guide_EN.docx | V1.0 (1.0-alpha), 2023-12-16 | 9774fd0dd64b6da6a0ba1dfb560851f707f9745e84750c59b94748377b0e9655 | 일치 (R-001) |
| 04_SG2002_PINOUT.xlsx | …/SG200X/04_SG2002/04_SG2002_PINOUT.xlsx | V0.1, 2023-12-11 | a20e1d2f02b0350a333ff16538cc59c13372b88c8a96f9737a3ef4f5ff57c148 | 일치 (R-001) |
| SG2002_38_2L_SCH.pdf | …/SG200X/04_SG2002/06_SG2002_38_2L_SCH&PCB/SG2002_38_2L_SCH.pdf | 파일명 V13 20230323 | 733b2e42d59d577632bab3d7db101c3be2a60e475d0a53e2dfda381cf7058ace | 일치 (R-001) |
| SG2002_38板_4L_SCH.pdf | …/SG200X/04_SG2002/07_SG2002_38_4L_SCH&PCB/SG2002_38板_4L_SCH.pdf | V1.3 20230301 | bf902176ce0f6ba17797d72313839aeb83e78fe5c451d6b46559d2008f50edb2 | 일치 (R-001) |

### seeed/recamera-2002/ — 참고 전용 (O-4 / D-003 #16: 참고만 하고 캐리어·전면 보드는 독자 설계)

**라이선스:**
- 코어 회로도 PDF의 표제란은 **CC BY-SA 4.0**이다(R-003 판독).
- 저장소 `LICENSE`는 **Apache License 2.0**이다(사본을 함께 보관).
- B301·S401 KiCad 파일 안에는 파일 단위 라이선스 문구가 없어 저장소 라이선스를 따른다고 본다.
- 이 폴더의 파일은 수정하지 않은 원본 사본이다. 사본을 둔다고 우리 설계가 파생물이 되지는 않는다. 이 파일을 **고쳐서 우리 설계에 쓰면** CC BY-SA 공유 조건이 붙을 수 있으므로(O-4), 열람·대조용으로만 쓴다.

| 파일 | 원본 경로 (저장소 기준) | 리비전 | sha256 | 대조 |
|---|---|---|---|---|
| reCamera_Core_2002w_8GB_v1.2_SCH_PDF_241014.pdf | hardware/recamera-2002/core/c1-2002/static/ | v1.2 (표제란 Rev V1.0, 2024-04-25, KiCad 8) | 95fbc621d666f3c9db3df467e3d64d9fc67bd8b9fef037d9294c199add89358f | 일치 (C-001) |
| BTB_Connector.png | hardware/recamera-2002/core/c1-2002/static/ | — | 7f7a0bc1d9a9f5909df8b2ed7d0768b26f4350ed32a82a62e016a0cac5477484 | 일치 (C-001) |
| reCamera 2002 POE Board.kicad_sch | hardware/recamera-2002/base/b301-poe/PCB/ | B301 | ffa71db8f849c79ce4b08a2f287bac91736d2c5e440610b0763145eba4eface9 | 새로 기록 (하위 시트 2개는 저장소에 없음, R-003) |
| reCamera 2002 POE Board.kicad_pcb | 〃 | B301 | b4b974b3ba8f8bc0fdc734af4925cf7ff8678d039a9a0372eb0d25f4211adf1f | 일치 (R-003) |
| reCamera 2002 POE Board.kicad_pro | 〃 | B301 | 3dccd692f68d81f92d613c0e384f814aad8ef37c225c5be89bd96029c26bb6af | 새로 기록 |
| reCamera 2002 S4 GC2053 Sensor Board_V1.0_SCH&PCB_250905.kicad_sch | hardware/recamera-2002/sensors/s401-gc2053/PCB/ | V1.0 250905 | 3da62d3bbdffc5ec534d0eaecf454a42428d96376bc9756c7aacaaff6a2174ba | 새로 기록 |
| reCamera 2002 S4 GC2053 Sensor Board_V1.0_SCH&PCB_250905.kicad_pcb | 〃 | V1.0 250905 | 783d3aa32e72bae44b4b5a6dbdda2ef9bebc6cd54c0ea310ea8ed9533be2aeb2 | 새로 기록 |
| reCamera 2002 S4 GC2053 Sensor Board_V1.0_SCH&PCB_250905.kicad_pro | 〃 | V1.0 250905 | 0e3b1b3203f9ae80c258111b1321daf576bf536ccd3dee40116b120ded941c59 | 새로 기록 |
| LICENSE | 저장소 루트 | Apache 2.0 | c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4 | — |

원본 저장소: https://github.com/Seeed-Studio/OSHW-reCamera-Series

### antmicro/ — Apache License 2.0 (`LICENSE`)

| 파일 | 원본 | 용도 | sha256 |
|---|---|---|---|
| Camera_Lens_20mm.kicad_mod | https://github.com/antmicro/hardware-components/blob/main/kicad-footprints/camera-lens-20mm/Camera_Lens_20mm.kicad_mod | M12 홀더 20mm 간격 풋프린트(R-002 O5 출발점, CLA216-ICR 구멍 지름은 도면과 대조 필요) | e18175993e787adcf379a6693e3ee9bdd34bfb1af1cb89e79d755a1ac324495d |
| LICENSE | 저장소 루트 | Apache 2.0 | 8964450587bf48768e17ad42cb7e4786d14b2c967dbf7f4209a843e76f4c479a |

참고: R-002에 적은 출처 antmicro/ov9281-camera-board에는 이 풋프린트 파일이 없다. 실제 원본은 위 hardware-components 저장소다.

## 링크·해시만 (Confidential 또는 라이선스 미표기 — 원본은 보관하지 않음)

| 자료 | URL | 리비전 | sha256 | 사유 |
|---|---|---|---|---|
| Lite-On LTR-329ALS-01 데이터시트 | https://datasheet.lcsc.com/datasheet/pdf/27381a4a4485d42352acd1f1e01ec243.pdf?productCode=C284894 | DS86-2014-0006 Rev B (2014-09-04) | b3f859b6d99c0ed19e27dc05c37ca77fc2f47c44782e75a2bb8780b8f3b68e04 | 라이선스 미표기 · 근거 정리는 docs/research/r005-ltr329.md |
| SG2002 TRM (중) | https://github.com/sophgo/sophgo-doc/releases/download/sg2002-trm-v1.02/sg2002_trm_cn_v1.02.pdf | v1.02 | 5381ffcfd344810db122544a004b49b4a207c2562c6033a841f2d686d7fc70f2 | BSD지만 영문판과 중복이라 보관하지 않음 |
| SG2002 Datasheet (중, docx) | sophgo-hardware …/01_SG2002_Datasheet_V1.0_CN.docx | 1.0-alpha | cbe115b6bf8511621a93fb1e9f00d5a917a9163fbdde3c95b951c33f8d3f3c9e | 중복 |
| SG2002 풋프린트 Allegro | sophgo-hardware …/11_SG2002_PCB_Package/qfn88_9d0x9d0_0d35_e.dra | — | eb3585666d5992fff7b2ad3a5136e276bbb283d4686ae697b5d1bfd8b1b81757 | 모듈 경로(D-002)라 직접 쓰지 않음 |
| LicheeRV Nano 회로도 70418 | https://dl.sipeed.com/shareURL/LICHEE/LicheeRV_Nano (02_Schematic) | 70418 | 7fdc7cbcda36a676ef73e3525f61e9ddec7507cca76828490225143696284efe | 라이선스 미표기 |
| Milk-V Duo 256M 회로도 | https://github.com/milkv-duo/duo-files/tree/main/duo-256M/hardware | v1.01 | 65135f0d556b4d321b2a4b02f100e2032d2ee39bfaf4fc07d5e8cfe63512eaa7 | LICENSE 없음 |
| Allwinner V851SX Datasheet | TinyVision 미러 (R-001) | Rev 1.2 | d7bcdee2de8728fe92ae71a81264033ec8c98428ad435261fa642b186294e260 | Confidential |
| GC2053 CSP Datasheet | https://taoic.oss-cn-hangzhou.aliyuncs.com/6446/product/XTW2020_1589249333000.pdf (제3자 사본) | V1.1 (2018-12-12) | V-001 기록 (396a3370…) | 「GC Confidential」 |
| 宝信发 BXF4677-GC2053 모듈 승인서 | https://files.seeedstudio.com/wiki/reCamera/reCamera_hq_poe/lens_document.pdf | V1.0 (2025-06-20 도면) | 미기록 | 라이선스 미표기 |
| 그 밖의 부품 데이터시트 (TI·Vishay·ams OSRAM·Diodes·HanRun·Hirose·Commonlands 등) | 각 연구 문서(R-002·R-004·R-006)의 URL | 각 문서 | 각 문서 | 제조사 저작물로 라이선스 미표기 |
