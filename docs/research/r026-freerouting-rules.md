# R-026 · Freerouting 규칙 누락 — 원인과 DSN 후처리

입력: pcb 브랜치 커밋 `b6842e9`의 `git archive` 사본(scratchpad). main(`fbc8388`)에는 `.kicad_pcb`가 없다. pcb 레인 파일은 읽기만 했다.
도구: KiCad 10.0.8 pcbnew(번들 python), Freerouting 2.5.0 + Temurin 25.0.5(전체 경로 `C:/Users/gh/tools/freerouting/download/jre25/jdk-25.0.5+8-jre/bin/java.exe`).
- Docker는 쓰지 않았다(O-106).
- Freerouting analytics는 명령줄 `--usage_and_diagnostic_data.disable_analytics=true`로 껐다. 전역 설정 파일은 건드리지 않았다.

## 원인 (근거: Freerouting 로그 「pre-existing clearance violation」, DSN 본문, pcbnew 구역 목록)

| # | 원인 | 근거 | 영향 |
|---|---|---|---|
| 1 | **DRU 조건용 규칙 구역이 DSN keepout으로 나간다.** KiCad `ExportSpecctraDSN`은 아무것도 금지하지 않는 규칙 구역(캐리어 DP_BRK 8·DP_TUNE 8·DP_TWIST 4, 전면 DP_BRK 6·K_A·K_B1·K_B2·K_C·K_D 등 12)도 `(keepout "" (polygon …))`로 내보낸다 | pcbnew `GetIsRuleArea()`이고 DoNotAllow* 모두 False인 구역이 캐리어 20·전면 12. DSN keepout F.Cu 28→11, B.Cu 9→6 | Freerouting이 고속 쌍 주변 전체를 장애물로 본다. 「FixedVia … <-> ObstacleArea」 위반이 생기고, 저속 배선이 그 구역을 지나지 못한다 |
| 2 | **내부층 GND_PWR가 DSN에 `(type power)`로 나간다.** 보드 층 형식이 power이기 때문이다. 그런데 이 층에는 기존 신호 트랙이 있다 | 로그 「Dedicated power layer 'GND_PWR' contains 17 signal wire(s)」 | Freerouting이 그 트랙을 면 위 이물질로 보고, 그 층을 배선에 쓰지 않는다 |
| 3 | **DRU 고속 간격 0.30이 DSN에 없다** (`hs_track_spacing`: 고속 트랙 ↔ 다른 트랙 0.30) | DSN class 규칙은 .kicad_pro 넷클래스 값(`clearance 200`)만 담는다 | 새 저속 트랙이 고속 쌍에 0.20까지 붙는다 → KiCad DRC 위반 |
| 4 | **가장자리 간격 0.40이 DSN에 없다** (`fab_copper_to_edge`) | DSN boundary에는 간격이 없고, Freerouting은 class 간격 0.20만 띄운다 | 가장자리 0.20~0.40 사이에 놓인 구리 → DRC 위반 |
| 5 | 쌍 규칙(diff_pair_gap·uncoupled·skew), 구역 조건 규칙, 층 금지(hs_outer_only) | Specctra DSN/Freerouting에는 KiCad DRU 조건식이 없다 | 고속 쌍은 잠금(fix)으로만 지킨다. 넣을 수 없음 |

.kicad_pro 넷클래스 폭·간격·비아(Default 0.20/0.20, CSI/MDI 0.15, USB 0.20, PWR_* 폭, 비아 0.65/0.30·0.80/0.40)는 KiCad가 DSN class 규칙과 `use_via`로 **이미 내보낸다**. 「트랙/간격 0.15/0.16」은 DRU 제작 최소값이고, 넷클래스 값(0.20/0.20)이 더 커서 DRC가 그 값으로 판정한다. 그래서 DSN에도 넷클래스 값을 그대로 둔다.

잠금: pcbnew `SetLocked(True)` 트랙·비아는 DSN에 `(type fix)`로 나간다(캐리어 hs 모드 fix 528 · route 398). 그래서 「고정 배선이 안 들어감」은 원인이 아니다.

## 수정 — `docs/research/r026/fr_rules.py`

`export <board> <dsn> <hs|all>`:
1. 잠금
   - `hs`: 고속·전원 넷클래스, IR 열 넷(IRA_SET·IRA_M·IRB_SET·IRB_M), GND 비아를 잠근다. pcb `freeroute.py`와 같은 범위다.
   - `all`: 기존 배선을 모두 잠근다.
2. 메모리에서 조건용 규칙 구역을 빼고 `ExportSpecctraDSN`을 돌린다(원인 1). 보드 파일에는 남는다(DRC에 필요). 원본 DSN은 `.orig`로 남긴다.
3. DSN 후처리
   - 고속 class(CSI_100·MDI_100·USB_90)의 `clearance 200`을 300으로 바꾼다(원인 3).
   - `layer GND_PWR (type power)`를 signal로 바꾼다(원인 2).
   - boundary 안쪽에 0.2mm 폭 keepout 띠를 모든 층에 둔다(원인 4).

`import <board> <ses> [base-drc.json]`은 다음 순서로 동작한다.
1. 기존 배선을 모두 잠근다.
2. `ImportSpecctraSES`로 가져온다.
3. 고정 대상 넷에 새로 생긴 배선을 지운다.
4. base-drc.json을 주면, 기준 신호 미연결 넷 밖에 새로 생긴 배선도 지운다.
5. 원래 잠금 상태로 되돌리고 면을 다시 채운 뒤 저장한다.

`drc_compare.py <base> <after>`: 종료 코드 0이면 합격이다. 조건은 다음과 같다.
- 위반 총수가 늘지 않는다.
- 종류별로도 늘지 않는다.
- 미연결이 줄어든다.
- parity가 늘지 않는다.

## 시험 결과 (2026-11-27 10:29~11:02)

Freerouting 명령은 아래와 같다. 2·3패스에서 이미 수렴했다. 15패스로도 돌렸는데 SES가 바이트 단위로 같았다.

```
java.exe -jar freerouting-2.5.0.jar -de <dsn> -do <ses> --router.autorouter.max_passes=3 -mt 4 \
  --gui.enabled=false --usage_and_diagnostic_data.disable_analytics=true
```

| 단계 | Freerouting 「pre-existing violations」(캐리어 / 전면) | 비고 |
|---|---|---|
| 후처리 없음(KiCad DSN 그대로 + 고속 300 + 가장자리 띠) | 1220 / 1026 | ObstacleArea 겹침, GND_PWR 「power layer contains 17 signal wires」 |
| + 조건용 구역 제외 + GND_PWR signal | **621 / 582** | power-plane 경고 없어짐. 나머지는 고정 항목끼리의 간격(같은 넷 비아, 고속 300 대 비아, USB-C 패드 간격 0.2 미만)이다. Freerouting도 「unfixable · fixed items」로 분류하고, 새 배선에는 영향이 없다 |
| 배선 뒤 | 621 / 582 (배선으로 늘어난 위반 0), Freerouting 미배선 208→76 · 195→76 | |

KiCad DRC 판정: `kicad-cli pcb drc --format json --severity-all --schematic-parity --exit-code-violations` → `drc_compare.py`. 기준은 b6842e9 사본이고, 커밋된 `hardware/pcb/drc/*-drc.json`과 같다.

| 실행 | 잠금 | 가져오기 거르기 | 캐리어 위반 · 미연결 | 전면 위반 · 미연결 | compare 종료 코드 |
|---|---|---|---|---|---|
| 기준 | — | — | 7 · 35 | 9 · 26 | — |
| 1 | hs / all | 없음 | 21~23 · 34 (track_width +14, items_not_allowed +2) | 24 · 21 (track_width +8, solder_mask_bridge +10) | 1 / 1 |
| 2 | all | 고정 대상 넷의 새 배선 제거 | 7 · 34 | 8 · 25 | **0 / 0** |
| 2 | hs | 같음 | 9 · 34 (track_not_centered_on_via +2) | 8 · 25 | 1 / 0 |
| 3 (**채택**) | all | + 기준 신호 미연결 넷 밖의 새 배선 제거 | **7 · 34** | **8 · 25** | **0 / 0** |
| 3 | hs | 같음 | 5 · 70 | 7 · 76 | 1 / 1 (풀어 둔 저속 배선을 Freerouting이 다시 놓았는데, 그것을 지워서 미연결이 늘었다) |

원인 6 (실행 1, 근거는 DRC 항목): Freerouting은 미연결이 남은 고정 대상 넷(5V_SYS·VIN·12V_IR·USB_DN·EPHY_TXN·IRB_SET)도 이었다. 이때 넷클래스 폭을 지키지 못했다(1.5mm 폭을 0.25mm로 이음, USB 0.15mm). 고속 넷을 내부층에 놓았고, IR 열 패드 마스크 개구부 안에 비아를 놓았다. → 가져오기에서 이 넷들의 잠기지 않은 새 배선을 지운다.

원인 7 (실행 2): 잠금 all인데도 새 트랙이 231·245개 생겼다. 대부분 이미 이어진 저속 넷(USB_DET·CAM_RESET 등)에 덧놓인 중복이다. Freerouting이 잠긴 기존 배선의 끝점을 연결로 보지 못하는 것으로 추정한다. **확인하지 않았다.** 근거는 기존 `track_not_centered_on_via` 5·6건 같은 끝점 어긋남이다. 그래서 기준 DRC에서 신호 미연결이 있던 넷의 새 배선만 남긴다(캐리어 16넷, 전면 12넷).

### 채택 결과와 한계

- 캐리어는 위반 7→7(종류별로도 같음), 미연결 35→34다. `/BUCK_FB` 신호 미연결 1건이 줄었다. 새 트랙·비아 59개.
- 전면은 위반 9→8, 미연결 26→25다. `/IR_CTRL` 1건이 줄었다. 새 트랙·비아 69개.
- **합격 조건(위반 늘지 않음 · 미연결 줄어듦)은 두 보드 모두 만족한다.** 다만 줄어든 미연결은 보드마다 1건뿐이다.
  - 남은 미연결: 캐리어는 신호 22 + 구역(GND 섬) 12, 전면은 신호 16 + 구역 9.
  - Freerouting도 76건을 잇지 못했다. 원인(밀집, 고정 배선 끝점 인식)은 60분 안에 판정하지 못했다.
- 지시의 잠금 범위(hs: 고속·전원·열·GND 비아만 잠금, 저속은 풀어 둠)는 캐리어에서 불합격이다(`track_not_centered_on_via` +2). 그래서 **잠금 all을 채택했다.** all은 hs가 잠그는 것을 모두 포함하고, 기존 저속 배선도 잠근다.

## 전달 — SES와 가져오기 명령

파일(이 레인 `docs/research/r026/`):

| 파일 | sha256 |
|---|---|
| `ses/carrier.ses` | `0e8489617614a47c8ce802fb15f384811fe2fce831f173e9a656eba8eafd5eaa` |
| `ses/front.ses` | `1ad91c22b61d6c5c3fecfa52e0520298db52ddcb6487ec5e607ae9d7d1a5f131` |
| `ses/carrier.dsn` (후처리된 입력) | `86305cb4011cd873ee04f5c3ca86605cc989329782cb3ba17f38ac913d858327` |
| `ses/front.dsn` | `9263eaacf4e29460a7e8509aad099bd7344fc27976117519379abce1aacc0b8a` |
| `drc/base-*-drc.json` · `drc/after-*-drc.json` | 기준 DRC와 판정 DRC |

**적용 조건:** SES는 b6842e9의 `hardware/schematic/<보드>/<보드>.kicad_pcb`에서 만들었다. `ImportSpecctraSES`는 보드의 트랙·비아를 SES 내용으로 **모두 바꾼다.** 그래서 이후 보드 배선이 바뀌었다면 그 변경이 사라진다. 적용 전에 보드의 트랙·비아가 b6842e9와 같은지 확인해야 한다.
- 같은지 보려면 트랙·비아 수를 비교하면 된다. 캐리어 977, 전면 961.
- 가져오기는 기존 트랙·비아를 잠시 모두 잠갔다가 원래 잠금 상태로 되돌린다(아래 원인 8).

원인 8 (원본 상태 보드 시험, 11:03): `ImportSpecctraSES`는 잠기지 않은 트랙·비아를 지우고, SES의 `fix` 배선은 다시 넣지 않는다. 그래서 잠금 없는 b6842e9 사본에 그대로 가져오니 트랙이 59개만 남았다(캐리어 위반 7→2, 미연결 35→154, compare 1). → `import`가 가져오기 전에 모두 잠그고, 가져온 뒤 원래 잠금 상태로 되돌린다. 새 배선은 UUID로 가린다.

원본 상태 사본에 다시 시험한 결과는 다음과 같다. 위 명령 그대로이고, `drc/after-*-drc.json`이 이 결과다.
- 캐리어: 기존 977개 모두 유지, 새 배선 395개 중 336개 제거, 위반 7→7, 미연결 35→34, compare **0**
- 전면: 기존 961개 유지, 새 배선 391개 중 322개 제거, 위반 9→8, 미연결 26→25, compare **0**
- 줄어든 신호 미연결은 캐리어 `/BUCK_FB` 1, 전면 `/IR_CTRL` 1이다. 늘어난 넷은 0이다.
- 남긴 새 배선은 캐리어 59(F 28 · B 28 · GND_PWR 2 · 비아 1), 전면 69(B 52 · F 8 · GND_PWR 8 · 비아 1)다.
  - 일부는 미연결이 그대로 남은 넷(USB_VBUS 등)에 놓인 부분 배선이다.
  - DRC가 track_dangling으로 잡지 않아 위반 수에는 들어가지 않는다.
  - 적용할 때 단일 작성자가 눈으로 볼 것: **verifiable 아니오**.

가져오기는 각 보드의 단일 작성자 레인에서만 한다. 캐리어는 pcb, 전면은 schematic이다. KiCad GUI에 그 보드가 열려 있으면 먼저 닫는다.

```
<KiCad>/bin/python.exe docs/research/r026/fr_rules.py import hardware/schematic/carrier/carrier.kicad_pcb docs/research/r026/ses/carrier.ses docs/research/r026/drc/base-carrier-drc.json
<KiCad>/bin/kicad-cli.exe pcb drc --format json --severity-all --schematic-parity --exit-code-violations -o <out.json> hardware/schematic/carrier/carrier.kicad_pcb
python docs/research/r026/drc_compare.py docs/research/r026/drc/base-carrier-drc.json <out.json>     # 0 이면 합격
```

전면은 `carrier`를 `front`로 바꿔 같은 명령을 쓴다. 같은 결과를 다시 만들려면 `fr_rules.py export <board> <dsn> all`(보드 사본에서), Freerouting(위 명령), import 순서로 돌린다.

## 분기점 · 선택 · 이유 · 차선책

| 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|
| 입력 보드 | pcb 브랜치 `b6842e9`의 git archive | main `fbc8388`에는 `.kicad_pcb`가 없다. pcb worktree의 미커밋 상태는 쓰지 않았다 | pcb worktree 파일 직접 복사(단일 작성자 진행 중이라 택하지 않음) |
| 잠금 범위 | all(기존 배선 전부) | hs는 캐리어 불합격(+2). all은 hs의 잠금을 포함한다 | hs. 전면은 hs도 합격했다(9→8 · 26→25) |
| 고정 대상 넷의 새 배선 | 가져올 때 지움 | Freerouting이 넷클래스 폭·쌍·층 규칙을 지키지 못한다(원인 6) | DSN에서 그 넷을 network에서 빼기(핀 넷 정보가 사라져 위험) |
| 중복 새 배선 | 기준 신호 미연결 넷만 남김 | 이미 이어진 넷의 덧배선은 위반은 아니지만 고리·스텁이 된다(원인 7) | 그대로 둠(DRC는 같다. 실행 2) |
| 고속 간격 | DSN 고속 class clearance 300 | DRU hs_track_spacing 0.30. 고속↔비아에도 300이 걸려 보수적이다 | class_class 규칙(Freerouting 지원 미확인) |
| 가장자리 | boundary 안쪽 0.2mm keepout 띠 | Freerouting class 간격 0.2 + 띠 0.2 = 0.4 | boundary 축소 |
| GND_PWR | DSN에서 signal로 | 기존 신호 트랙 17개가 있다. 이 층에 새 트랙은 캐리어 2·전면 8개였고 DRC 위반은 없다 | power 유지(기존 트랙이 Freerouting 위반이 됨) |
| analytics | 명령줄로 끔 | 외부 전송을 막으려고. 전역 설정 파일은 건드리지 않았다 | — |
| 패스 수 | 3 | 3패스와 15패스의 SES가 바이트 단위로 같다 | 15 |

Docker는 쓰지 않았다(O-106). Freerouting은 Temurin 25 전체 경로로 직접 실행했다. 원본 보드와 pcb 레인 파일은 바꾸지 않았다.
