# V-006f 제조 산출물 검사기(`v006_fab.py`) 수정과 조건 3 판정 (review)

## 결론

pcb의 P-004 최종 산출물(레인 `t-20261127-154843-d387`, 커밋 e5558bb)을 고친 검사기로 돌렸다. 두 보드 모두 R-010 17항목 중 불합격 0이다(종료 0). 사람 확인은 보드마다 1건(3.08 극성·1번 핀 실크)이다.

| 보드 | 입력 | 종료 | 항목 | 불합격 | 사람 확인 |
|---|---|---|---|---|---|
| 캐리어 | `manufacturing/pcb/carrier/` 폴더 | 0 | 17 | 0 | 3.08 |
| 캐리어 | `manufacturing/pcb/carrier.zip` | 0 | 17 | 0 | 3.08 |
| 전면 | `manufacturing/pcb/front/` 폴더 | 0 | 17 | 0 | 3.08 |
| 전면 | `manufacturing/pcb/front.zip` | 0 | 17 | 0 | 3.08 |

결과 파일은 main 체크아웃의 `validation/runtime/vd001/results/cond3-review-carrier.json`, `cond3-review-front.json`에 썼다.

| 항목 | 캐리어 | 전면 |
|---|---|---|
| Gerber | 11장, 빠짐 0 | 11장, 빠짐 0 |
| 외곽 | 닫힘, 40.000 × 54.000 | 닫힘, 40.000 × 40.000 |
| 드릴 (보드와 대조) | PTH 477 · NPTH 10 | PTH 257 · NPTH 8 |
| 원점 | 왼쪽 아래 | 왼쪽 아래 |
| 좌표 행 = BOM 실장 수 | 64 | 66 |
| BOM | 73행 (SMD·Hybrid 64, THT 2, DNS 7) | 71행 (SMD·Hybrid 66, DNS 4, Manual 1) |
| BOM DNS = 보드 DNP | 7 | 4 |
| 조립도 | 앞·뒤 1쪽씩 | 앞·뒤 1쪽씩 |
| zip sha256 기록 | 일치 | 일치 |

제조사에 낸 것은 없다(파일 검사만).

## 고친 검사기 결함 (pcb가 알려 줌)

| # | 증상 | 원인 근거 | 고친 것 | 재시험 |
|---|---|---|---|---|
| 1 | 전면 3.05 「top 좌표 파일 2개」 | top 파일 패턴이 `(top|front).*pos`라 보드 이름 `front` 때문에 `front-bottom-pos.csv`도 잡혔다 | 면 이름은 `pos` 바로 옆에 붙은 것만 본다 | 시험 추가(파일 이름을 `front-top-pos`·`front-bottom-pos`로). 고치기 전 실패 → 후 통과 |
| 2 | 캐리어 3.06 「Type Hybrid (J3)」 불합격 | Type 값을 DNS·SMD·THT만 받았다. R-010이 인용한 PCBWay 양식은 「Surface mount, Thru-hole or Hybrid」다 | Hybrid를 받는다. 좌표 파일에 들어가는 실장 부품이라 SMD와 같이 센다 | 시험 추가. 고치기 전 실패 → 후 통과 |
| 3 | zip 하나만 입력하면 3.16 「기록 없음」 | zip은 자기 해시를 담을 수 없는데, 풀린 내용에서만 기록을 찾았다 | zip 입력이면 zip 옆(같은 폴더, `<보드>/`)의 `SHA256SUMS*`도 본다 | 시험 2건 추가(옆에 기록 있으면 통과, 없으면 불합격) |

## Type `Manual` 처리 (분기점)

- **사실:** `Manual`은 PCBWay 양식 값이 아니다. BOM 생성기 문서(`manufacturing/bom/README.md` B5)가 「우리가 추가한 값」으로 기록했고, PCBWay가 그대로 받는지는 미확인이라고 적었다. 차선책은 `DNS` + Notes다.
- **고른 것:** 기록된 프로젝트 값이므로 조건을 걸어 받는다.
  - Notes에 「Not soldered」가 있어야 한다.
  - 좌표 파일에 있으면 불합격이다.
  - 보드 실장 부품과의 대조에서는 뺀다(납땜하지 않는 기구 부품이라 보드에 SMD·THT 속성이 없다).
- **남기는 것:** `Manual` 행이 있으면 3.06 참고란에 「PCBWay 양식 밖 프로젝트 값 — 제조사 확인 전」이라고 적는다. 전면 MH1(CLA216-ICR 홀더)이 해당한다.
- **차선책:** `Manual`을 불합격으로 두고 BOM 생성기가 `DNS` + Notes로 내게 한다(research). 주문 단계에서 제조사가 `Manual`을 받지 않으면 이쪽으로 바꾼다.

## 고장 주입 (`test_v006_fab.py` 24건, 실패 0)

원래 16건에 8건을 더했다.

| 사례 | 기대 |
|---|---|
| m16 실장 부품의 Type을 Hybrid로 | 불합격 0 |
| m17 좌표 파일 이름 `front-top-pos` · `front-bottom-pos` | 불합격 0 |
| m18 좌표에 있는 실장 부품을 Type Manual로 | 3.06 불합격 |
| m19 보드·좌표에 없는 기구 부품 행, Manual + 「Not soldered」 | 불합격 0 |
| m20 Manual인데 Notes에 「Not soldered」 없음 | 3.06 불합격 |
| m21 알 수 없는 Type 값 | 3.06 불합격 |
| m22 zip 하나만 입력, 옆에 SHA256SUMS | 불합격 0 |
| m23 zip 하나만 입력, 해시 기록 없음 | 3.16 불합격 |

## 돌린 명령과 종료 코드

| 명령 | 종료 |
|---|---|
| `python -I docs/review/v005/test_v006_fab.py <캐리어 보드> <작업 폴더>` | 0 (24건) |
| `python -I docs/review/v005/v006_fab.py <d387>/manufacturing/pcb/carrier <out> --board carrier --pcb <보드> --commit e5558bb` | 0 |
| 같은 명령, 전면 | 0 |
| 같은 명령, `carrier.zip` · `front.zip` | 0 · 0 |

저장소 테스트(하네스 검사)는 돌리지 않았다.
