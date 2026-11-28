# SIM 결과 JSON 공통 형식 (orch O-81, SIM-001a·b·VD-001 HTML 공용)
파일: hardware/sim/results/<시험 ID>.json (예: SIM-A1-tps26600-inrush.json). UTF-8, 한 시험 = 한 파일.
```json
{
  "id": "SIM-A1",
  "title": "TPS26600 기동 돌입전류",
  "owner": "schematic",
  "circuit": {"board": "carrier", "refs": ["U1", "C5"], "schematic_commit": "656b50a"},
  "model": {"source": "TI PSpice TPS26600 Rev B | 데이터시트 동작 모델", "url": "...", "license": "...", "behavioral": false, "basis": "데이터시트 쪽·그림"},
  "criteria_commit": "<기준을 먼저 커밋한 sha>",
  "checks": [
    {"name": "돌입 피크 전류", "op": "<=", "limit": 1.5, "unit": "A", "value": 0.82, "corner": "최악(±1%, 22nF+10%)", "pass": true}
  ],
  "verdict": "pass",
  "waveforms": ["hardware/sim/png/SIM-A1-inrush.png"],
  "netlist": "hardware/sim/SIM-A1.cir",
  "tool": {"name": "ngspice", "version": "...", "sha256": "..."},
  "notes": "가정·한계"
}
```
- verdict = 모든 checks.pass 이면 "pass", 하나라도 false면 "fail", 실행 불가면 "error"(notes에 원인).
- op: "<=", ">=", "==", "between"(limit=[lo, hi]).
- 실행 스크립트 하나가 results/*.json 전부를 다시 만들고, 종료 코드 = fail+error 수.

## ID 규칙 (O-92 추가 — 레인 간 파일 이름 충돌 방지)
- schematic(전원 경로 SIM-001a): SIM-A*(입력 보호)·SIM-B*(5V 벅)·SIM-C*(레일·순서)·SIM-D*
- firmware(부하·제어 SIM-001b): SIM-L1~L8 (예전 SIM-B1~B8 → L1~L8로 이름 바꿈)
- 회로 파일(.cir)·PNG도 같은 ID 접두. 새 묶음은 orch가 접두를 정해 준다.
