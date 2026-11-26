# P-001 PCBWay 공정 규칙과 캐리어 설계 규칙 제안

- 작성: pcb (Opus 5.5 medium) · 날짜·확인일: 2026-11-26 (모든 URL은 이날 공개 페이지로 확인, 로그인·견적·업로드 없음)
- 입력: D-002(모듈+캐리어), D-003 기본값(#2 위탁+턴키, #12 보드 5장), R-003(reCamera Core 2002, B2B 60P 0.5mm ×2, CSI 4레인·EPHY MDI가 B2B로 나옴), orch O-2~O-4
- 범위: 제조 공정 규칙 조사 + KiCad 설계 규칙 **제안**. 보드 파일 작성·견적은 하지 않았다.

## 1. 결론

1. **4층 1.6mm, 1oz/1oz, PCBWay 현행 표준 적층(7628)**을 기본으로 한다. 2층 1.6mm는 100Ω 차동을 만들 수 없다(§4.4).
2. **설계 규칙은 6/6mil 대신 0.15/0.16mm 이상, 드릴 0.30mm 이상**으로 둔다. 이것이 PCBWay의 추가 요금 없는 기준(6/6mil, 구멍 ≥0.3mm)이다.
3. **L1 표면 차동선 선폭/간격**
   - CSI·MDI 100Ω: 0.15/0.16mm
   - USB 90Ω: 0.20/0.16mm
   - 근거: 2D 정전계 계산이며, 솔더마스크를 넣으면 99Ω/91Ω, 빼면 110Ω/99Ω이다.
   - 최종값은 견적 때 PCBWay 임피던스 조정 결과로 확정한다.
4. **0.5mm 피치 BTB·FPC 조립:** PCBWay가 공개한 미세 피치 한계가 0.25mm라서 범위 안으로 본다(추론). 명시 문구는 없으므로 견적 때 확인한다.
5. **수량·리드타임**
   - PCB 제작 최소 수량은 5장이다.
   - 표준 사양이면 PCB 제작이 24h이고, Advanced 사양이면 4층이 5일이다. 4층이 24h 대상인지는 미확인이다.
   - 조립은 3~5일이며 부품·PCB가 갖춰진 뒤부터 센다. 턴키 부품 조달 시간은 따로 더해진다.

## 2. PCBWay 공정 규칙표

용어: 「표준」은 추가 요금이 없는 범위, 「옵션」은 추가 요금이나 검토가 붙는 범위다. 페이지마다 값이 다르면 모두 적었다.

| # | 항목 | 2층 | 4층 | 구분 | 출처 |
|---|---|---|---|---|---|
| 1 | 추가 요금 없는(24h) 사양 | FR-4, 두께 1.0/1.2/1.6, 완성 구리 1oz, 구멍 ≥0.3mm, 트랙/간격 ≥6/6mil, HASL, 초록 마스크·흰 실크. 캐스텔레이션·엣지 도금·임피던스 제어·블라인드/베리드 비아는 제외 | 같음(층수 명시 없음) | 표준 | [S1] |
| 2 | 최소 트랙/간격 | 가능 0.1mm(4mil), "6mil 이상 강력 권장" | 같음 | 4mil은 옵션 | [S2] |
| 2a | 외층 구리별(Advanced normal) | 1oz ≥5/6mil, 2oz ≥7/8mil | 같음, 내층 1oz ≥4/5mil | 옵션 표 | [S2] |
| 2b | 외층 분석표 | Normal: 1oz 0.12mm, 2oz 0.15mm. 최소: 1oz 0.10mm | 같음 | 권장 | [S3] |
| 3 | 드릴 | 현행: 0.15–6.0mm, <0.2mm 추가 요금. 구판: 0.2–6.3mm, <0.3mm 추가 요금 | 같음 | ≥0.3mm 표준 | [S2][S3] |
| 3a | 완성 구멍 공차 | PTH ±0.08mm, NPTH ±0.05mm | 같음 | 표준 | [S2] |
| 4 | 환형링 | 최소 0.15mm(6mil). Advanced 1oz: 비아 ≥5mil, 부품 ≥10mil | 같음 | 표준 최소 6mil | [S2] |
| 4a | 구멍 간 간격 | 부품 구멍 ≥16mil, 비아(≤0.45mm) ≥11mil | 같음 | 옵션 표 | [S2] |
| 5 | 비아 처리 | 텐팅 / 마스크 플러그 / 노출 중 선택, "Gerber대로 제작" | 같음 | 가격 차 미공개 | [S4] |
| 5a | 비아 인 패드 | 레진 충전·도금 캡 가능, "higher production cost" | 같음 | 옵션 | [S5] |
| 5b | 블라인드/베리드 | 해당 없음 | 가능, "significantly increase the cost" | 옵션(사용 안 함) | [S6] |
| 6 | 솔더마스크 | 댐 4mil(<2oz, 초록). 개구 ≥2mil. 초록·빨강·노랑·파랑 무료 | 같음 | 표준 | [S2] |
| 7 | 실크 | 최소 선폭 0.15mm, 글자 높이 0.8mm, 흰·검정 무료 | 같음 | 표준 | [S2] |
| 8 | 구리 두께 | 외층 1oz 표준(최대 8oz) | 내층 1/1.5/2oz… | 1oz 표준 | [S1][S2] |
| 9 | 보드 두께 | 0.2–3.2mm, 무료는 1.0/1.2/1.6 | 4층 최소 0.6mm | 1.6 표준 | [S1][S2] |
| 9a | 두께 공차 | ±10%(≥1.0mm), ±0.1mm(<1.0mm) | 같음 | 표준 | [S2] |
| 10 | 구리–외곽 | Normal 0.3mm, 최소 0.25mm. V-cut 0.35mm | 같음 | 권장 0.3 | [S3][S2] |
| 10a | 슬롯 | 도금 ≥0.5mm, 비도금 ≥0.8mm | 같음 | 옵션 표 | [S2] |
| 10b | 외형 공차 | CNC ±0.2mm, V-score ±0.5mm | 같음 | 표준 | [S2] |
| 11 | 표면 처리 | HASL 표준. ENIG는 추가 요금. 주문폼에 "HASL을 ENIG로 바꿀 수 있음(무료)" 체크 | 같음 | HASL 표준 | [S2][S4][S7] |
| 12 | 임피던스 제어 | 언급 없음 | ±10%, 50Ω 이하 ±5Ω. Advanced 옵션이며 검토 후 추가 비용. 구판에 "only sampling 100Ω differential". 임피던스 시험 보고서 무료 | 옵션 | [S2][S8][S9][S10] |
| 13 | 최소 수량 | 5 pcs | 5 pcs | 표준 | [S4] |
| 14 | 패널 | 단품 / 고객 패널 / PCBWay 패널. V-score·탭 라우팅(간격 ≥1.6mm). V-cut >10줄 등은 추가 요금 | 같음 | 단품 표준 | [S4][S7] |
| 14a | 소형 추가 요금 | 한 변 <20mm 또는 50×50mm 미만이면 추가 요금 | 같음 | — | [S7] |
| 15 | 빌드 시간 | Standard: 0–50pcs·<1m²는 24h | Advanced 표: 4층 <1m² 5일, Extra Urgent 48h | 4층의 24h 여부 미확인 | [S11] |
| 16 | 전기 시험 | 플라잉 프로브·AOI 무료 | 같음 | 표준 | [S2] |

### 2.1 4층 표준 적층 (현행, 관통 비아 전용)

출처: [S8]. 외층은 0.5oz 원박에 도금해 1oz로 만든다.

| 층 | 구성 | 두께 mm | Dk |
|---|---|---|---|
| L1 | 0.5oz → 1oz 도금 | 0.0175(원박) | — |
| PP | 7628 RC46% | 0.1960 → 적층 후 0.1855(잔동률 70%) / 0.1785(50%) / 0.1715(30%) | 4.74 |
| L2 | 1oz | 0.035 | — |
| Core | 1.1(동박 포함) | 1.030 | 4.6 |
| L3 | 1oz | 0.035 | — |
| PP | 7628 RC46% | 위와 같음 | 4.74 |
| L4 | 0.5oz → 1oz 도금 | 0.0175 | — |

- 완성 두께: 1.61mm ±10%(잔동률 70%)
- 다른 공칭 두께: 1.2mm는 코어 0.63, 1.0mm는 0.43, 0.8mm는 0.23이고 PP는 모두 같다.
- 구판 블로그(2017, PP 0.11mm, Dk 4.29/3.96)[S12]는 현행과 다르므로 쓰지 않는다.

### 2.2 조립(PCBA)

| 항목 | 값 | 출처 |
|---|---|---|
| 미세 피치 | 0.25mm pitch. 최소 패키지 01005. BGA 0.3mm(리지드) | [A1][A2] |
| 0.5mm BTB·FPC 커넥터 | 명시 문구 없음 → 미세 피치 한계 안이라 가능으로 추론, **견적 때 확인** | — |
| 턴키 / 키팅 / 콤보 | 콤보 가능: "You can supply some parts, and we source the rest" | [A1][A3] |
| 사급 부품 | 끊기지 않은 테이프·릴·트레이. IC·커넥터는 1~5개 여분, 0402 이하 수동부품은 최소 100개+50개 여분. BOM 라인번호 라벨. 중국까지 운송비는 고객 부담 | [A4][A5] |
| 최소 조립 수량 | helpcenter "MOQ is 1 piece", 능력표·견적은 5부터(상충) | [A6][A1] |
| 스텐실 | 조립 견적에 포함 | [A7] |
| 실장 | 한 면/양면, SMT·THT·혼합 | [A1] |
| 리드타임 | PCBA 3–5일, 빠르면 24h. 부품·PCB가 모두 갖춰진 뒤부터. 부품 조달은 단축 불가 | [A8][A3] |
| 파일 | Gerber RS274X, BOM xls/csv(턴키는 MPN), CPL(RefDes·X·Y·Rot·Side) | [A9] |
| 보드 크기 | 최소 10×10mm(작으면 패널), 최대 250×500mm. 50×100mm보다 작거나 직사각형이 아니면 패널 | [A1][A5] |
| 레일·피듀셜 | 가장자리–부품이 3mm(또는 3.5mm) 미만이면 레일 필요. 피듀셜은 단품·패널 모두 표시, 패널은 1.0mm 3개 | [A10][A3][A11] |
| 검사 | AOI 기본, X-ray 요청 시. FCT는 고객 절차·지그 필요 | [A12] |
| 부품–외곽 | 0.5mm 이상(블로그 2026-02). 오래된 글에는 3~5mm | [A13] |

## 3. KiCad 설계 규칙 제안 (여유값)

PCBWay 최저 한계가 아니라 추가 요금 없는 기준 위에 여유를 둔 값이다. 보드 설정 > 설계 규칙에 넣을 값이다.

| 항목 | 제안 | PCBWay 기준 | 여유 근거 |
|---|---|---|---|
| 최소 트랙 | 0.15mm(BTB·FPC 팬아웃 국부만), 기본 0.20mm | 6mil=0.152 표준 | 6mil 경계는 국부에서만 쓴다 |
| 최소 간격(구리–구리) | 0.16mm, 기본 0.20mm | 6mil 표준 | 6mil보다 0.008mm 크게 |
| 최소 비아 | 지름 0.60 / 드릴 0.30mm | 구멍 ≥0.3 표준, 링 ≥0.15 | 링 0.15는 표준 최소와 같다 → 기본 비아는 0.65/0.30(링 0.175) |
| 최소 PTH 드릴 | 0.30mm | ≥0.3 표준 | — |
| 최소 환형링 | 0.15mm | 6mil | 기본 비아는 0.175 |
| 구멍–구멍 | 0.45mm | 부품 16mil(0.41) | +0.04 |
| 구리–외곽 | 0.40mm(V-score 패널이면 0.50) | Normal 0.3, V-cut 0.35 | +0.1/+0.15 |
| 솔더마스크 확장 | 0.05mm | 개구 ≥2mil | 공개 권장값 없음 |
| 솔더마스크 최소 웹 | 0.10mm | 댐 4mil | 0.5mm 피치 패드 사이에 웹을 남기는 최소값. 웹이 안 서면 그 커넥터만 갱 개구로 처리 |
| 실크 선폭 / 글자 높이 | 0.15 / 1.0mm | 0.15 / 0.8 | 글자 +0.2 |
| 실크–패드 | 0.15mm | — | KiCad 기본 이상 |
| 부품–외곽(코트야드) | 1.0mm 이상. 3mm 안에 부품이 있으면 PCBWay 패널·레일 주문 | 0.5mm, 레일 3~3.5mm | — |
| 비아 처리 | 텐팅 기본, 시험점 비아는 노출 | Gerber대로 | — |
| 비아 인 패드 | 사용 안 함 | 옵션 | 비용 |
| 표면 처리 | ENIG(분기 B4) | HASL 표준 | 0.5mm BTB 평탄도 |
| 판 두께 | 1.6mm | 표준 | 모듈 BTB 짝 높이는 R-003에서 확인 |

**넷클래스 제안**

| 넷클래스 | 대상 | 층 | 선폭/간격(mm) | 쌍 사이 간격 | 비고 |
|---|---|---|---|---|---|
| Default | 일반 | 전층 | 0.20 / 0.20 | — | — |
| CSI_100 | CAM 4레인+CLK(B2B ↔ 센서 FPC) | L1(L2 GND 기준) | 0.15 / 0.16 | ≥0.45 | 쌍 내 길이차 목표 ≤0.1mm, 레인 간 ≤1mm(목표값, 근거는 센서 쪽 문서에서 확인 예정) |
| MDI_100 | EPHY TX±/RX±(B2B ↔ 자석·RJ45) | L1 | 0.15 / 0.16 | ≥0.45 | 자석 아래 GND 컷아웃은 트랜스 데이터시트에 따름 |
| USB_90 | USB D±(쓰는 경우) | L1 | 0.20 / 0.16 | ≥0.45 | — |
| PWR | 12V 입력·레귤레이터 | L1/L4 + L3 | ≥0.40 | 0.20 | 전류에 따라 다시 정함 |

층 배치: L1 신호(고속) · L2 GND 연속면 · L3 전원 · L4 신호(저속). 고속선은 L2를 끊는 곳 위로 지나가지 않는다.

## 4. 스택업·임피던스 계산 근거

### 4.1 방법
- 도구: `hardware/pcb/calc/microstrip_fd.py`. 2D 라플라스 유한차분(준정적, 무손실, 격자 약 4µm)이다.
  - 단선 Z0 = 1/(c·√(C·C0)), 차동 = 2·Z홀수이다.
  - 솔더마스크는 두께 0.015mm, Er 3.5의 덮개로 근사했다.
- 입력: §2.1 L1–L2 PP h=0.1855mm, Er 4.74, t=0.035mm(완성 1oz). 사다리꼴 식각은 무시했다.
- 검증: `python microstrip_fd.py --check` (종료 코드 0). 단선 결과가 Hammerstad-Jensen 식과 0.4~0.6% 차이다.
  - w=0.20: FD 61.60Ω, HJ 61.89Ω
  - w=0.30: FD 50.30Ω, HJ 50.62Ω
  - w=0.35: FD 46.31Ω, HJ 46.49Ω
- 원인이 확인된 실패 1회
  - 증상: 첫 실행에서 HJ보다 +7% 높았고 eeff가 2.85로 낮았다.
  - 원인: h가 격자에 맞지 않아 선로 밑에 4µm 공기층이 생겼다.
  - 수정: 격자를 h에 맞췄다.
  - 재시험: 위 결과로 통과했다.

### 4.2 결과 (`python microstrip_fd.py`, 종료 코드 0)

| w / s (mm) | Zdiff 마스크 없음 | Zdiff 마스크 0.015/3.5 |
|---|---|---|
| 0.14 / 0.16 | 113.5 | 102.4 |
| **0.15 / 0.16 (100Ω안)** | **109.5** | **99.1** |
| 0.17 / 0.20 | 110.4 | 101.1 |
| 0.18 / 0.16 | 103.8 | 94.6 |
| **0.20 / 0.16 (90Ω안)** | **99.5** | **91.0** |
| 0.22 / 0.20 | 99.9 | 92.4 |
| 0.25 / 0.20 | 94.3 | 87.7 |

단선 50Ω(참고): w=0.30mm에서 50.3Ω(마스크 없음).

민감도(마스크 없음):

| 조건 | 100Ω안 | 90Ω안 |
|---|---|---|
| 공칭 | 109.5 | 99.5 |
| 잔동률 30%, h=0.1715 | 108.4 | 96.8 |
| Er 4.4(주파수 상승·재질 차) | 112.8 | 102.5 |
| 마스크 0.015/3.5 | 99.1 | 91.0 |

### 4.3 해석
- PCBWay 문서는 솔더마스크 1회 인쇄로 차동 임피던스가 약 8Ω 내려간다고 적고 있다[S9]. 이 계산의 마스크 효과(-9~-10Ω)와 같은 크기다. 실제 보드에는 마스크가 있으므로 **마스크 포함 값을 목표에 맞췄다**.
- 마스크를 빼거나 Er 공차가 있어도 100Ω안은 +10~13%, 90Ω안은 +11~14% 안에 든다. 이 범위는 PCBWay 임피던스 제어 공차 ±10%의 경계 근처다. 그래서 임피던스 제어를 주문하면 PCBWay가 선폭을 조정하게 하는 것을 전제로 한다.
- 이 계산은 PCBWay 계산기나 Polar Si9000의 결과가 아니다. 제조사 확인값이 아니다.

### 4.4 2층 비교
- 2층 1.6mm는 기준면까지 약 1.53mm다. HJ 식으로 단선 50Ω에 w≈2.9mm, w=0.15mm면 단선 144Ω이다.
- 0.5mm 피치 BTB에서 나오는 차동선을 100Ω/90Ω으로 만들 수 없다. 그래서 2층은 고속선이 없는 보조 보드(예: IR LED 보드)에만 쓴다.

## 5. 분기점

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| B1 | 층수 | 4층 1.6mm 표준 적층 | 100Ω/90Ω 차동은 L2 GND 기준이 필요. 2층은 불가(§4.4) | 4층 1.2/1.0mm(PP 같아 선폭 그대로, BTB 높이에 맞출 때) |
| B2 | 규칙 기준 | 6/6mil·0.3mm 드릴 + 여유 | 추가 요금 없는 범위. 0.5mm 피치 팬아웃도 들어간다 | 팬아웃이 막히면 그 영역만 0.127/0.127(5mil, 옵션 비용) |
| B3 | 임피던스 | 계산 선폭으로 설계하고, 견적 때 임피던스 제어 옵션 가격을 보고 결정 | 설계는 어느 쪽이든 같다. CSI·MDI 배선이 짧아 무제어도 기능은 가능성 높음(미검증) | 처음부터 임피던스 제어 주문(PCBWay가 선폭 조정, 보고서 무료) |
| B4 | 표면 처리 | ENIG | 0.5mm BTB 60P 두 개의 평탄도·납땜성. HASL은 미세 피치에 불리 | HASL(무료). 견적에 "HASL→ENIG 무료 변경"이 적용되면 비용 차이 없음 |
| B5 | 조립 방식 | 콤보: 모듈은 조립 뒤 꽂고, 짝 BTB는 원품번 확인 후 턴키·불가면 사급 | D-003 #2. 짝 BTB 원품번이 미확인(R-003) | 짝 BTB 전부 사급(1~5개 여분) |
| B6 | 패널·레일 | 단품 주문. 가장자리 3mm 안에 부품이 있으면 PCBWay 패널(레일) | 5장 소량, 파일 단순 | 고객 패널 V-score + 레일 5mm |
| B7 | 비아 | 관통 비아만, 텐팅 | 현행 표준 적층은 관통 비아 전용, 비용 | 비아 인 패드(옵션) |

## 6. 미확인·견적 때 확인할 것
- 4층이 24h 빌드 대상인지(Advanced 표는 5일)
- 임피던스 제어 금액, 지금도 "100Ω 차동만 샘플링"인지, 90Ω도 되는지, TDR 쿠폰 유무
- 0.5mm BTB 60P·0.5mm FPC 조립 가능 여부(명시 문구 없음), 셋업비, 사급 발송 주소
- 표준 FR-4 브랜드·Tg·Dk 측정 주파수, 솔더마스크 두께·Er
- 2층 1.6mm 코어 구성(공개 페이지 없음)
- 내층 0.5oz 적층 존재 여부
- 페이지 사이 상충: 최소 조립 수량 1 대 5, 레일 기준 3 대 3.5mm, 드릴 추가 요금 기준 <0.2 대 <0.3mm. 보수적인 쪽(0.3mm)을 택했다.

## 7. 출처 (확인일 2026-11-26)
- [S1] https://www.pcbway.com/blog/News/Notice_of_Shortened_Lead_Time_for_Small_batch_PCB_Order.html (2018-09-03 공지)
- [S2] https://www.pcbway.com/capabilities.html
- [S3] https://www.pcbway.com/pcb_prototype/PCB_Manufacturing_tolerances.html (구판 기준)
- [S4] https://www.pcbway.com/orderonline.aspx
- [S5] https://www.pcbway.com/pcb_prototype/PCB_Via_in_Pad.html
- [S6] https://www.pcbway.com/pcb_prototype/Blind_vias_and_Buried_Vias.html
- [S7] https://www.pcbway.com/helpcenter/paymentproblems/What_PCBs_will_be_charged_of_extra_cost_.html
- [S8] https://www.pcbway.com/multi-layer-laminated-structure.html
- [S9] https://www.pcbway.com/pcb_prototype/Impedance_Control.html
- [S10] https://www.pcbway.com/oem/quality-control.html
- [S11] https://www.pcbway.com/quickturn-pcb-fabrication.html
- [S12] https://www.pcbway.com/blog/Engineering_Technical/stackup___pcbway.html (구판, 미사용)
- [S13] https://www.pcbway.com/pcb_prototype/impedance_calculator.html (외층에서 마스크 제외, Si9000 권장)
- [A1] https://www.pcbway.com/assembly-capabilities.html
- [A2] https://www.pcbway.com/helpcenter/pcb_assembly_ordering/What_s_the_min_package_you_can_assemble_.html
- [A3] https://www.pcbway.com/assembly-faq.html
- [A4] https://www.pcbway.com/assembly-special-remind.html
- [A5] https://www.pcbway.com/helpcenter/pcb_assembly_ordering/What_issues_should_be_paid_attention_to_for_customer_supplied_components_.html
- [A6] https://www.pcbway.com/helpcenter/pcb_assembly_ordering/What_s_the_min_quantity_of_assembly_.html
- [A7] https://www.pcbway.com/helpcenter/pcb_assembly_ordering/Should_I_submit_a_stencil_order_for_SMT_project_made_by_PCBWay_.html
- [A8] https://www.pcbway.com/pcb-assembly.html
- [A9] https://www.pcbway.com/assembly-file-requirements.html
- [A10] https://www.pcbway.com/helpcenter/pcb_assembly_ordering/What_are_the_requests_on_pcb_for_assembly_by_machine_.html
- [A11] https://www.pcbway.com/pcb_prototype/Panel_Requirements_for_Assembly.html
- [A12] https://www.pcbway.com/helpcenter/pcb_assembly_ordering/Can_you_do_test_after_assembly__What_documents_should_I_offer_.html
- [A13] https://www.pcbway.com/blog/PCB_Design_Layout/PCB_Layout_Best_Practices_for_Improved_Performance_and_Manufacturability_1d7f7e2e.html

수치는 조사 하위 에이전트가 WebFetch로 읽은 페이지 요약에서 왔다. 이미지로만 있는 표는 빠졌을 수 있다.
