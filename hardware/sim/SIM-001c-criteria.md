# SIM-001c — 새 항목 합격 기준 (실행 전에 커밋)

- 배정: orch t18r SIM-001c (O-92·O-93) · 레인 `t-20261127-041440-3ed1` · 2026-11-27
- 할 일:
  - C-018/C-019 회로(R6 6.04 kΩ · R17 4.7 kΩ · C19 4.7 nF · Q1 게이트 1 kΩ + 4.7 nF)로 L2·L3·L5·L6을 **기준 `7cab389` 그대로** 다시 돌린다.
  - 새 항목 **L9 · L10**(센서 레일 끄는/켜는 순서)을 더한다. 새 항목의 기준이 이 문서다.
- eFuse 한계는 SIM-001b′ 적용 메모(`3a22c52`)와 같이 "시험 회로의 ILIM"으로 해석한다. R6 6.04 kΩ의 ILIM 값은 C-019 계약 판에서 읽어 JSON에 적는다.
- **ID:** O-92에 따라 firmware 묶음은 SIM-L*이다. 결과는 `hardware/sim/results/SIM-L9.json` · `SIM-L10.json`이다.

## 근거 — GC2053 전원 순서 (GC2053 CSP Datasheet AE-2M-3043 V1.1 사본, §9.2 · §9.3 p.24–25)

- **끌 때 (§9.3):**
  - t1 "From AVDD28 pull down to DVDD12 pull down" ≥ 0
  - t0 "From DVDD12 pull down to IOVDD pull down" ≥ 0
  - → **AVDD가 먼저(또는 같이), IOVDD가 마지막**
  - t2 "From RESETB pull low to PWDN pull low" ≥ 0
- **켤 때 (§9.2):**
  - t1 "From IOVDD to AVDD28" ≥ **50 µs**
  - t0 "From IOVDD to DVDD12" ≥ 50 µs
- **우리 보드와의 대응 (가정):** 모듈 BXF4677은 AVDD 2.8 V · DVDD 1.2 V · DOVDD 1.8 V를 안에서 만든다(Seeed 배포 승인서 V1.0 "电源电压").
  - 보드의 `CAM_AVDD`(모듈 12·16번)와 `CAM_IOVDD`(14번)는 그 LDO들의 3.3 V 입력이다.
  - 모듈 안 LDO 지연·문턱을 모르므로 **보드 레일의 90 % 지점으로 순서를 대신 본다.**
  - DVDD12가 어느 입력에서 나오는지 모르므로 DVDD는 판정하지 않는다.

## SIM-L9 CAM_EN 끄는 순서 (CAM_EN 1 → 0)

| check | op | 한계 | 단위 | 근거 |
|---|---|---|---|---|
| CAM_IOVDD < 90 % 시각 − CAM_AVDD < 90 % 시각 (IOVDD가 마지막) | >= | 0 | s | §9.3 t1·t0 ≥ 0 |
| CAM_AVDD < 90 % 시각 − CAM_RESET < 0.54 V 시각 (리셋이 먼저) | >= | 0 | s | §9.3 t2 ≥ 0 (PWDN은 모듈 안 — RESETB로 대신) |
| 끄는 동안 CORE_3V3 최저 전압 | >= | 3.135 | V | 코어 +3V3 −5 %. 다른 부하에 영향 없음 |
| 끄는 동안 CORE_3V3 쪽으로 되돌아가는 전류 최대 (레일 → CORE_3V3, Q1·Q2 바디 다이오드 경유) | <= | 1e-3 | A | 꺼지는 레일이 코어 레일을 밀어 올리지 않음 |

## SIM-L10 CAM_EN 켜는 순서 (CAM_EN 0 → 1)

| check | op | 한계 | 단위 | 근거 |
|---|---|---|---|---|
| CAM_AVDD ≥ 90 % 시각 − CAM_IOVDD ≥ 90 % 시각 | >= | 50e-6 | s | §9.2 t1 ≥ 50 µs (모듈 LDO 지연은 모르는 채 보드 레일로 대신 — 보수적) |
| 켜는 동안 CORE_3V3 최저 전압 (레일 돌입) | >= | 3.135 | V | 코어 +3V3 −5 % |
| CORE_3V3 돌입 피크 전류 | <= | 1.0 | A | 코어 SY80004 Imax 1 A 공유 (계약 3.1절) |

- **모델:**
  - AO3401A(Q1·Q2): 데이터시트 수치(VGS(th) · RDS(on) · Ciss)를 실행 전에 확인해 JSON `model.basis`에 적는다.
  - 모듈 부하: `CAM_IOVDD` · `CAM_AVDD` 각각 GC2053 동작 전류(IIOVDD 2.5 mA · IAVDD 18 mA · IDVDD 39 mA, §2.3 최대)를 3.3 V 입력 쪽 전류로 근사한다. DVDD 39 mA를 어느 레일에 둘지는 모르므로 두 레일 모두에 넣은 경우와 한쪽에만 넣은 경우를 다 보고, 나쁜 쪽으로 판정한다.
  - CORE_3V3: 이상 전원 3.3 V + 경로 0.1 Ω(가정) + 코어 쪽 용량 22 µF(가정).
- **판정:** 모든 check가 pass면 "pass", 하나라도 false면 "fail", 실행이 안 되면 "error". 형식은 orch O-81이다.
