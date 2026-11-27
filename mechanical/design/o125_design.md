# O-125 1단계 — 케이스 디자인 시안 A · B · C (덩어리)

- 스크립트: `python -I -B mechanical/fusion_run.py mechanical/design/o125_design.py --set DESIGN=A|B|C`
  - Fusion 새 로컬 문서에 내부 적층을 가져와 시안을 만들고, 간섭 확인과 내보내기까지 한다.
- 교차 확인: `python -I -B mechanical/fusion_run.py mechanical/design/o125_gap.py --readonly`. 시안 바디마다 내부 바디까지 최소 거리를 잰다.
- 내부 적층: main 995b872 보드 STEP(캐리어 · 전면, 3D 모델 포함)과 기준 적층(코어 · 센서 · 렌즈)이다. 자리 표시 · keep-in은 뺐다. 바디 179개.
  - 실측 바깥(mm): x −20.46…20, y −34…20, z −23.19…40.19.
  - 시안 안쪽 기준: x ±21, y −34.5…21, z −24…41.
- 좌표: 코어 중심 · 아랫면 원점, +Y 위, +Z 앞(광축). 보드 STEP · 렌더 메시와 같은 원점이다.
- 공통:
  - 나사 4개는 뒷면에 숨긴다(M2.5).
  - 바닥에 1/4"-20 인서트 보스(Ø6.4)를 둔다.
  - 상태 LED 광 파이프(Ø1.9)를 둔다.
  - 케이블 출구는 1곳이다. A · B는 바닥 오목 자리에 RJ45와 DC를 함께 두고, C는 뒤 글랜드다.
  - USB-C(옆)와 microSD(위)는 서비스 마개 자리다.
  - 앞면 아래에 「OpenHW」를 0.3 mm 음각한다.
  - STL은 바이너리, 곡면 오차 0.01 mm, 법선 5°, 최대 변 2 mm.
- 덩어리 시안이다. 방열(#26), 나사 보스, 가스킷, 커넥터 마개 상세는 3단계(고른 시안)에서 다룬다.

| 시안 | 형태 | 바깥 X×Y×Z mm (쉘·유리) | 간섭 mm³ (verifiable 예) | 최소 거리 mm (플라스틱 · 알루미늄 · 앞유리) | 음각 면 z |
|---|---|---|---|---|---|
| A | 둥근 박스(세로 R5 · 둘레 R3) · 앞 2/3 무광 흑색 플라스틱 + 뒤 1/3 알루미늄 쉘(위·옆 통합 핀 홈) · 분할선 0.6 · 앞면 IR 투과 검정 유리 한 장(아래 7 mm 턱) · 벽 브래킷 | 48.0 × 61.5 × 71.5 | 0 | 1.586 · 0.815 · 1.315 | 43.5 |
| B | 퍽/큐브(세로 R6 · 둘레 R3.6) · 윗판 알루미늄 세로 핀 7장 · 앞면 유리(아래 9 mm 턱) + 광축 원형 렌즈 링(별도 바디 LENS_RING, 앞으로 2.5 → Z 72.2) | 48.4 × 70.9 × 69.7 | 0 | 0.814 · 4.2 · 1.315 | 43.5 |
| C | 원통 불릿(바깥 Ø 약 76 · 앞뒤 R4) · 위쪽 차양 22 mm · 뒤 케이블 글랜드(알루미늄) · 앞 베젤 8 mm 안에 유리 | 79.1 × 77.6 × 102.0 | 0 | 0.815 · 3.305 · 1.315 | 43.5 |

## 산출 (main 체크아웃 `validation/runtime/vd001/design/<시안>/`, gitignore)

| 파일 | 바이트 | sha256 |
|---|---|---|
| `A/A.step` | 511092 | `c4db7f5dbd75b637dca020e079cc4110c9234ec7cb4c263554de96c9359505da` |
| `A/A_SHELL_PLASTIC.stl` | 11236284 | `c19bd93cfec24512f2491068739b13e4bb8b6f4e134cc696bb3c0c603a337353` |
| `A/A_SHELL_ALU.stl` | 18457684 | `236b902cbc724eed7d8aabb0cf2d7c9d459178728a9760af5eddb054fdf2ac51` |
| `A/A_FRONT_GLASS_IR.stl` | 4124684 | `175b103f8c2ea5fad4c0fece169ea34bcf92f5afc392735f2d2be9b33bb2b6df` |
| `A/A_LIGHT_PIPE.stl` | 863884 | `43b3e8135d3e1fa696e01f45b01f4c57f2a210ab9f029e146cfa27f1d552b6a8` |
| `A/A_WALL_BRACKET.stl` | 2629684 | `65fd2f897f0c181bb9521b3235d72efe0f965259dfe08e623ef2608a1410f66f` |
| `B/B.step` | 432108 | `be6f5de9a1b15d9bcb285027a15aa70cb427e84b0122c9c76fd3df63e92d151f` |
| `B/B_SHELL_PLASTIC.stl` | 32968184 | `dcab24525e12a302074391745a7ebc17d7f18b3384fd6f242dd584b8745dd357` |
| `B/B_SHELL_ALU.stl` | 298884 | `21f48273b430c6cb719c6f777f34a1c9dd58cb9dfbc6dff5d721aa60e6848287` |
| `B/B_FRONT_GLASS_IR.stl` | 4236684 | `bf2a966bfcec0f4c146cfc4a7d6d4cf4d0e49bd8e5785fac1ba8100d3453803d` |
| `B/B_LIGHT_PIPE.stl` | 863884 | `115611b6690aab0d509946135520efd3ba89881ad3ac20c137a33aec85affdc3` |
| `B/B_LENS_RING.stl` | 216084 | `57c35ee9015edf51a0a4d69244bd4389ad684324f48c854f3e772a9d4dbfcd77` |
| `C/C.step` | 305410 | `c7a4ba2c4a8bfdc6df6fa54f342f47b19bdf9de9d55c4d7ec5caf006aa714e82` |
| `C/C_SHELL_PLASTIC.stl` | 20878784 | `6390de90e448c370d2949cdaec61f54bae9a819beeb9b6cad4a101b896743c1e` |
| `C/C_SHELL_ALU.stl` | 1008084 | `85272449a09fbfd68d9510b78deb72e6fac5655bc69c8148acc20dbfcfd369fb` |
| `C/C_FRONT_GLASS_IR.stl` | 71884 | `a3b6c9c367391df99b4c08d0163c410de84f30cb1ee43653a7673c1da2a889c0` |
| `C/C_LIGHT_PIPE.stl` | 863884 | `9caad7ce6474479201202230c84d1f454193a9eb20fe237d95fade3d16185cd9` |

- 그 밖에 `<시안>_iso.png`(Fusion 뷰포트 확인용), `result.json`, `gap.json`.
- 보기 판단(예쁨 · 비례)은 사람 확인 항목이다(verifiable 아니오). 2단계 히어로 렌더(schematic)로 고른다.

## 고친 것 (같은 원인 각 1회)

1. Fusion API: `MoveFeatureInput.defineAsTranslate` 없음 → 0에서 만든 BRep을 `TemporaryBRepManager.transform`으로 옮김.
2. 얇은 유리 판에 R5 모깎기가 실패 → 세로 모서리 r, 앞뒤 둘레 r2(두께 절반 · 0.6r 이하)로 나눔.
3. 음각 면 고르기:
   - 넓은 +Z 면을 고르니 안쪽 뒷벽이 뽑혔다. 평면 법선은 바깥 방향 보장이 없다. → 글자 자리(x 0, y)를 품는 Z 평면 중 가장 앞쪽 면으로 고름.
   - B · C는 안쪽 공간이 앞까지 뚫려 평평한 앞면이 없었다. → 앞벽 2 mm를 두고 유리 자리만 뚫음.
4. C 차양이 쉘과 0.05 mm 떨어져 별도 바디가 됨 → 쉘 벽에 0.5 겹침.
5. orch 요청: B 렌즈 링을 SHELL_ALU에서 떼어 LENS_RING(`B_LENS_RING.stl`)으로 따로 냄.
- 처음 보고한 A · B 해시는 3번 · 5번 수정 전 것이다(그때 음각은 안쪽 면에 들어감). 위 표가 최종이다.
