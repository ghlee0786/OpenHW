# R-029 · 100BASE-TX MDI 차동쌍 — 쌍 안 길이 차·비결합 길이의 공개 근거

- 확인일 2026-11-27. 문서만 조사했고 시뮬레이션은 하지 않았다.
- 대상 (캐리어 MDI TX, O-119):
  - (가) 비결합 ≤ 6 mm + 쌍 안 길이 차 1.677 mm (약 11 ps)
  - (나) 쌍 안 길이 차 0 + 비결합 약 9 mm

## 결론

**근거 문서상으로는 (나)가 낫다.**
- 공개 문서 가운데 쌍 안 길이 차에 1.7 mm보다 작은 고정 한도를 두는 것이 **있다**. TI SNLA387이 100M MDI에 대해 50 mil(1.27 mm)을 「should」로 권고한다.
- 반면 비결합 길이의 수치 한도는 찾은 문서 어디에도 **없다**.

다만 이 50 mil은 범용 체크리스트의 권고다. SG2002 문서에는 MDI 수치가 없고, 다른 PHY 업체 문서(Microchip)는 120 mil(3.05 mm)을 준다. 그래서 「강한 규범」이라기보다 **보수적 권고 1건**으로 읽힌다.

| 판단 항목 | 답 |
|---|---|
| 1.7 mm보다 작은 쌍 안 길이 차 고정 한도를 제시하는 근거 문서 | **있음** — TI SNLA387 p.2: 「The traces should be length-matched within 20 mils for 1G transmissions and within 50 mils for 100M or 10M transmissions.」(50 mil = 1.27 mm < 1.677 mm) |
| 그 한도와 어긋나는 다른 공개 문서 | 있음 — Microchip ATSAMA5D27-WLSOM1 §7.3.2.2: 「ETH_TX_P and ETH_TX_N should be matched in length to within 120 mils.」(3.05 mm > 1.677 mm, (가)도 만족) |
| SG2002 · 코어 모듈 문서의 MDI 수치 | **없음** — SG2002 Hardware Design User Guide의 EPHY 절에는 직렬 저항·ESD만 있다 |
| 비결합(분리) 구간 길이 수치 한도 | **없음** — SG2002 문서·TI SNLA387·TI DP83822·Microchip 문서 모두 수치가 없다. DP83822의 「constant coupling distance」 같은 정성 요구뿐이다 |

## 1. SG2002 · 코어 모듈 문서 (우선 출처)

`hardware/datasheets/sophgo/02_SG2002_Hardware_Design_User_Guide_EN.docx` (V1.0, 2023-12-16, BSD 2-Clause, 저장소 보관본)
- §2.5.1 EPHY-RJ45 (본문 문단 469): 「The main chip has a built-in 100MB PHY, which can be directly connected to the network port. The network differential lines between the main chip and the network transformer should be in series with a resistor of 5.1R or less to enhance resistance to network surges and to reduce network EMI. Add ESD devices when necessary.」
  - 쌍 안 길이 차·비결합 수치는 **없다**.
- §3.10 RJ45 with RMII/RGMII Routing (문단 690–694): 「When routing the RMII module, refer to the reference board or follow the PHY chip manufacturer's requirements.」 이 절은 RMII 쪽 내용이고 MDI 수치는 없다.
- 참고(MDI 아님): MIPI 절(문단 655)은 「The differential pair inner P/N lengths should be controlled within 20 mils」라고 한다. MIPI CSI 규칙이라 MDI에 옮겨 쓰지 않는다.
- 코어 모듈(reCamera Core 2002) 회로도 PDF는 회로만 담고 있어 레이아웃 지침이 없다(`hardware/datasheets/INDEX.md` 목록 기준).

## 2. PHY 업체 공개 앱노트·문서

### TI SNLA387 「Ethernet PHY PCB Design Layout Checklist」 (June 2021)

- 원본: https://www.ti.com/lit/pdf/snla387 · 받은 파일 sha256 `6c8682fdb4e3db76352a8d77abec00bcfe4d1b2b84553bf81194aa6f89162b12` (7쪽). 라이선스 표기가 없어 저장소에는 보관하지 않는다(D-003 #14).
- p.2 「MDI Traces」:
  > The total length of each MDI trace should be less than 2 inches, or 2000 mils. The traces should be length-matched within 20 mils for 1G transmissions and within 50 mils for 100M or 10M transmissions. The number of vias and stubs on the MDI traces should be kept to a minimum.
  > The typical impedance should be a 100 Ohm differential with a +/- 10% control.
- p.3 「Signal Routing」:
  > different differential pairs must have at least 30 mils of separation between the pairs.
  > As mentioned in the previous topics, traces should be length matched. To match the trace lengths, different routing techniques can be used. It is recommended to apply those techniques on the same end of the length-matched pair.
- 해석
  - 「length-matched pair」와 Figure 2-2(길이 맞춤 구불길)로 보아, 50 mil은 **쌍 안(P/N) 길이 맞춤**이다.
  - 표현은 「should」이고, 특정 PHY가 아닌 TI PHY 전반의 체크리스트다.
  - **비결합 길이 수치는 없다.**

### TI DP83822 데이터시트 (10/100 PHY) — SNLS505H, 2016-07, 개정 2026-07

- 받은 곳: https://www.ti.com/document-viewer/lit/html/SNLS505G/GUID-85CA4DFA-D571-485D-87D3-A0B539485866 (PDF로 받음, 131쪽, sha256 `d73d83c018e6dab3f935ea45ca1771bbc34c030b6b24de45fccd1dfa6998a2d3`, 보관하지 않음)
- §9.4.1.1 Signal Traces (p.112–113):
  > Within the differential pairs, trace lengths must be run parallel to each other and matched in length. Matched lengths minimize delay differences, avoiding an increase in common mode noise and emissions.
  > Differential pairs must always have a constant coupling distance between them.
- 정성 요구만 있고 **수치 한도는 없다**. 쌍 안 길이 차와 비결합 길이 모두 마찬가지다.
- 길이 차가 공통 모드 잡음·방사를 늘린다는 근거는 이 문서가 준다. (나)의 「쌍 안 차 0」은 이 문장과 바로 맞고, (가)의 비결합 ≤6 mm는 「constant coupling distance」와 맞는다. 두 문장이 각각 다른 안을 지지한다.

### Microchip ATSAMA5D27-WLSOM1 문서 §7.3.2.2 「Design Layout Recommendations」 (10/100 PHY 인터페이스)

- https://onlinedocs.microchip.com/oxy/GUID-9E8FA63D-EDB0-4DC2-AB0C-B3693CFF2928-en-US-8/GUID-4DB04365-3AA6-4438-B7BC-770E2763D509.html (페이지 표기 © 1998–2024, 리비전 표기 없음)
  > ETH_TX_P and ETH_TX_N should be matched in length to within 120 mils.
  > ETH_RX_P and ETH_RX_N should be matched in length to within 120 mils.
  > Recommended differential impedance for net: 100Ω ± 5%.
- 120 mil = 3.05 mm다. 쌍 안 P/N을 명시한 한도이고, **비결합 길이 수치는 없다**.

### IEEE 802.3 (Clause 25, 100BASE-TX)

- MDI 단자에서의 신호 특성을 다룬다. PCB 배선의 쌍 안 길이 차나 비결합 길이 한도는 이번에 원문으로 **확인하지 못했다**(인용 없음).

## 3. 수치 비교 (참고 계산 — 판정 근거는 위 원문)

| 항목 | (가) | (나) | TI SNLA387 | Microchip |
|---|---|---|---|---|
| 쌍 안 길이 차 | 1.677 mm (약 66 mil, 약 11 ps) | 0 | ≤ 50 mil (1.27 mm) — (가) 초과 | ≤ 120 mil (3.05 mm) — 둘 다 만족 |
| 비결합 길이 | ≤ 6 mm | 약 9 mm | 수치 없음 | 수치 없음 |

- 물리 규모: 100BASE-TX는 125 Mbaud(MLT-3)이라 한 심볼이 8 ns다.
  - 11 ps는 심볼의 약 0.14 %다.
  - 9 mm 비결합 구간의 지연은 약 60 ps(6.6 ps/mm 가정)로, 3 ns급 상승 시간보다 훨씬 짧다.
  - 두 안 모두 신호 품질상 차이는 작을 것으로 보이지만, **확인하지 않았다**. 시뮬레이션·측정이 없다.
- 프로젝트 규칙과의 관계: (나)를 고르면 비결합 9 mm가 현재 MDI 비결합 한도 6 mm(D-003 #28)를 넘는다. 그래서 규칙 완화를 D-003에 기록해야 한다. (가)는 쌍 안 길이 차 예외를 기록해야 한다(O-119).

## 분기점 · 선택 · 이유 · 차선책

| 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|
| 「강한 근거」 판단 | TI 50 mil을 「있음(권고 수준)」으로 적음 | 원문이 100M MDI에 고정 수치를 「should」로 준다. 다만 범용 체크리스트이고, 다른 업체 문서는 120 mil이다 | 「없음」으로 보기(SG2002 문서에 수치가 없다는 점 우선) |
| 출처 우선순위 | SG2002 문서 → PHY 업체 문서 → IEEE | 지시 순서. SG2002 문서에는 MDI 수치가 없다 | — |
| TI PDF 보관 | 링크·sha256만 | 라이선스 표기가 없다(D-003 #14) | — |
