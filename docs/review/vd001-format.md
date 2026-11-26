# VD-001 HTML 입력 형식 (V-006, review)

VD-001 가상 설계 완료 보고는 HTML 한 장이다.

- 생성기: `docs/review/v005/v006_vd001_html.py`
- 출력: `validation/runtime/vd001/index.html`(gitignore)
- 각 칸은 아래 형식의 결과 파일을 정해진 자리에 두고, orch가 생성기를 한 번 돌린다.
- 제조사 견적·비용 항목은 넣지 않는다(D-003 #39, 최후 단계).

```
python -I docs/review/v005/v006_vd001_html.py [--vd validation/runtime/vd001] [--sim hardware/sim/results] [--root .]
```

- 종료 코드 = 불합격 항목 수 + 결과 파일이 없는 조건 수
  - 사람 확인 항목(verifiable 아니오)은 세지 않는다.
  - 사람 확인 항목은 HTML에서 사용자가 체크해야 통과다. 체크는 브라우저 localStorage에만 남는다.

## 1. 조건 결과 파일 — `validation/runtime/vd001/results/cond<N>-<칸>[-<보드>].json`

조건 번호 N은 다음과 같다(VD-001 계획).

| N | 조건 | 담당 |
|---|---|---|
| 1 | 회로 ERC 0 · netcompare 0 · 계약 일치 | schematic |
| 2 | PCB DRC 0 · 미연결 0 · parity 0 · 완화는 D-003 기록분만 · V-005 최종 | review |
| 3 | 제조 산출물 R-010 16항 | review |
| 4 | 임피던스 · 길이/skew · 전원 전류(IPC-2152) · 전압 강하 · 열 연결 | research |
| 5 | 3D 모델 빠짐 0 · 조립 간섭 0 · 최소 틈 · 플러그 삽입 · 광축 · LED 가림 · BTB 높이 | mechanical |

7(회로 시뮬레이션)은 §2 형식을 쓴다.

```json
{
  "cond": "2",
  "owner": "review",
  "title": "PCB DRC·미연결·parity·완화 기록·V-005 최종",
  "commit": "<판정한 입력 커밋 sha>",
  "generated": "2026-11-27T05:00:00",
  "command": "bash docs/review/v005/run_v005.sh <sha>",
  "exit_code": 0,
  "items": [
    {"cond": "2", "id": "2.A1", "board": "carrier", "title": "DRC 위반", "verifiable": true,
     "value": 0, "limit": 0, "pass": true,
     "evidence": [{"label": "drc_carrier.json", "path": "validation/runtime/v005/<sha>/drc_carrier.json"}],
     "commit": "<sha>", "note": ""},
    {"cond": "2", "id": "2.H1", "board": "carrier", "title": "기구 키 커넥터 1번 핀 표시 불필요?", "verifiable": false,
     "value": "-", "limit": "사람 확인", "pass": null, "evidence": [{"label": "그림", "path": "validation/runtime/v005/<sha>/index.html"}]}
  ]
}
```

**필드 규칙**

- **필수:** `id`, `title`, `verifiable`, `pass`
- **`pass`:** 기계 항목은 `true`/`false`, 사람 항목은 `null`
- **`board`:** `carrier` · `front` · `-`(보드와 무관)
- **`evidence[].path`:**
  - 저장소 루트 기준 상대 경로 또는 URL이다.
  - 커밋 증거는 `{"label": "커밋", "path": "commit:<sha>"}`로 쓴다.
- **`exit_code`:** 그 칸 판정 스크립트의 종료 코드(= 불합격 수)
- **보드별 파일:** 한 조건을 보드마다 나눠도 된다(`cond3-review-carrier.json` · `cond3-review-front.json`). 생성기가 합친다.
- **이 형식을 내는 스크립트:**
  - 조건 2: `v006_cond2.py`가 `run_v005.sh` 결과에서 만든다(`validation/runtime/v005/<sha>/cond2.json`). 생성기에는 복사해 넣는다.
  - 조건 3: `v006_fab.py`의 출력 json이 이 형식이다.

## 2. SIM 결과 — `hardware/sim/results/<시험 ID>.json` (orch O-81 공통 형식 그대로)

- 필드: `id` · `title` · `owner` · `circuit{board,refs,schematic_commit}` · `model{source,url,license,behavioral,basis}` · `criteria_commit` · `checks[{name,op,limit,unit,value,corner,pass}]` · `verdict` · `waveforms[]` · `netlist` · `tool{name,version,sha256}` · `notes`
- `verdict`는 `pass` · `fail` · `error` 중 하나다. 생성기는 `fail`과 `error`를 불합격으로 센다.
- 파형 PNG는 `waveforms`의 저장소 상대 경로다. HTML에 작은 그림으로 넣는다.

## 3. 제조 산출물 자리 (조건 3, pcb P-004 → review 검사)

`v006_fab.py`가 보드마다 찾는 이름 규칙이다. 폴더 대신 zip 하나를 줘도 된다.

```
manufacturing/pcb/<보드>/
  gerber/<보드>-*.gbr (11장: F/In1/In2/B.Cu · F/B.Paste · F/B.Silkscreen · F/B.Mask · Edge.Cuts — 층은 머리 주석 TF.FileFunction으로 식별)
  gerber/<보드>-PTH.drl · <보드>-NPTH.drl · *-drl_map.pdf
  <보드>-top-pos.csv · <보드>-bottom-pos.csv   (KiCad csv 머리글 Ref,Val,Package,PosX,PosY,Rot,Side 또는 PCBWay 템플릿, mm, 회전 0~360)
  <보드>-pcbway.csv                            (PCBWay 9열, make_pcbway_bom.py)
  <보드>-assembly-*.pdf                        (F.Fab/B.Fab, 드릴 맵 제외 PDF를 조립도로 본다)
  README.md                                    (층 순서 「L1: F.Cu」…「L4: B.Cu」, 패널, 폼 옵션 4·1.6·ENIG·TG·1oz·Tenting, X-ray, 위탁, G1·G2)
  SHA256SUMS                                   (<sha256>  <보드>.zip)
manufacturing/pcb/<보드>.zip
```

- **원점:** aux 원점을 외곽 왼쪽 아래에 둔다. 그래서 Gerber 외곽 최소가 (0,0)이고, 드릴·좌표 값은 0~보드 크기 안이다.
- **690ff78 사본 실행 결과:** aux 원점이 (100,100)으로 보드 가운데였다. kicad-cli 좌표 회전에 −90이 나왔다. 둘 다 이 검사에서 불합격이 되므로 pcb가 P-004에서 맞춰야 한다.

## 4. 렌더 — `validation/runtime/vd001/render/manifest.json`

```json
[
  {"kind": "pcb-front", "board": "carrier", "title": "캐리어 앞", "path": "validation/runtime/vd001/render/carrier_top.png", "sha256": "...", "source": "kicad-cli pcb render --quality high", "input_sha256": "<STEP/보드 해시>"}
]
```

- `kind`: `pcb-front` · `pcb-back` · `assembly` · `section` · `exploded` · `enclosure`(외함 완성) · `turntable`(mp4)
- manifest에 없는 kind는 HTML에 「자리(아직 없음)」로 보인다.
- 렌더 확인은 사람 눈(verifiable 아니오)이다.

## 5. bring-up 으로 넘기는 남은 위험 — `validation/runtime/vd001/risks.json`

```json
[
  {"id": "RISK-01", "title": "MDI 10BASE-T 극성 자동 보정 근거 없음", "source": "D-003 #31 / O-47", "owner": "firmware", "bringup": "F-005 7절 링크 시험", "status": "open", "note": ""}
]
```

- orch가 원장의 대기 목록에서 뽑아 만든다.
- 필드: `id`, `title`, `source`(원장 · 결정 번호), `owner`, `bringup`(확인할 절차 위치), `status`, `note`
