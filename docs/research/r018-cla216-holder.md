# R-018 CLA216-ICR 렌즈 홀더 판정 (O-75)

- 배정: orch t18r R-018 (O-75) · 작성 research t18s · 확인일 2026-11-27 · 레인 t-20261127-032020-1c02 (main dd13a7f 기준)
- 범위: 공개 자료만 봤다(제품 페이지, 공식 도면, 제품 사진). 구매·문의는 하지 않았다.

## 결론: (a) CLA216-ICR만으로 충분하다 — 별도 M12 홀더는 필요 없다

- **CLA216-ICR은 M12×0.5 암나사가 있는 렌즈 홀더에 IR-cut 전환기가 일체로 들어간 부품이다.** 렌즈 CIL093은 CLA216에 바로 나사로 끼운다.
- 기존 기구 기준(mechanical `stack-reference.md` §3)이 맞다. 여기서 CLA216은 높이 7.6, 귀 두께 3.4인 홀더이고, 그 위에 CIL093을 끼우며, 초점 조건은 MBFL 2.85와 s−p ≤ 0.885다.
- **R-017의 「M12 렌즈 홀더 BOM 누락」 판단은 틀렸다.** 근거로 쓴 FAQ 문장이 도면·사진과 맞지 않는다(아래 2절). R-017 비용표의 홀더 행(기준 $27)은 R-017b에서 뺀다.
- 적층 변화량 Z = 0. 전면 보드의 구멍과 나사도 바뀌지 않는다(Ø1.7, 간격 20.0 그대로).

## 1. 근거 (원문)

| # | 자료 | 내용 | 판정 |
|---|---|---|---|
| E1 | 공식 도면 `IR_Cut-Off_Filter_Switcher_20mm_Hole_Spacing_7.6mm_Height.webp?v=1758130556` (Shopify CDN, 제품 페이지 이미지. 받은 파일 sha256 7827f26d…) | **단면 A-A(3:1)에 안쪽 나사가 그려져 있고 치수 「M12x0.5」가 붙어 있다.** 같은 단면에 「(Minimum MBFL: 2.85)」와 전체 높이 7.6이 있다 | 암나사 있음. 최소 MBFL은 렌즈를 받는 부품에만 의미가 있는 규격이다 |
| E2 | 같은 도면 평면도 | 바닥 공동 14.1, 몸체 15.9, 구멍 간격 20.0, (24.4) 귀, 구멍 (Ø1.7), 필터 창 (5.0)×(7.2). 「0.3mm thick IR Cut off filter T=50%@645nm+/-10nm / 0.21mm thick dummy glass」 | R-007 판독값과 같다 |
| E3 | 제품 사진 `IRCutOffFilterExchangerSwitcher_bc03d57c…jpg?v=1677871895` (sha256 6f908898…) | 왼쪽은 CLA216 단품으로, 둥근 보스 안쪽에 나사산이 보인다. 오른쪽은 **M12 렌즈가 CLA216에 바로 끼워진 조립 상태**이고 다른 홀더는 없다 | 렌즈를 바로 끼운다 |
| E4 | 제품 사진 `IMG_7852_1.jpg?v=1677871895` (sha256 5f43c562…) | CLA216 두 개. 둘 다 보스 안쪽 나사산과 필터 창이 보인다 | 같음 |
| E5 | 제품 설명 (de 미러, 상품 JSON `body_html`) | 「Der CLA216-ICR ist ein M12-Objektiv-IR-Sperrfilter-Wechsler (Switcher) mit einer Höhe von 7,6 mm.」 (M12 렌즈용 IR-cut 필터 전환기, 높이 7.6mm.) 0.30mm IRC와 0.21mm 더미 유리, 3.3V H-브리지, 60mm 2핀 1.25mm JST | 「홀더」라는 말은 없지만 「M12 렌즈용」, 높이 7.6 |
| E6 | 제품 페이지 FAQ (de 미러 HTML의 JSON-LD) | 「Das CLA216-ICR ist mit jedem Commonlands M12-Objektiv kompatibel, das in der Variante M12ANIR bestellt wurde. Kombinieren Sie es mit dem Objektiv und einem Commonlands CLA019- oder CLA024-Objektivhalter, um eine komplette Baugruppe zu erhalten.」 | **E1·E3과 맞지 않는다.** 아래 2절 |

- URL:
  - 제품 페이지: https://de.commonlands.com/products/ir-cut-off-filter-switcher-m12-cla216 (본 도메인 commonlands.com은 HTTP 429. ja·ko 미러도 같은 페이지)
  - 도면: https://cdn.shopify.com/s/files/1/0273/9273/7398/files/IR_Cut-Off_Filter_Switcher_20mm_Hole_Spacing_7.6mm_Height.webp?v=1758130556

## 2. FAQ 문장 해석

- FAQ는 CLA019(구멍 간격 18mm)와 CLA024(22mm)를 「홀더」로 묶으라고 한다. 그런데 CLA216 자체가 간격 20mm 귀와 M12 암나사를 갖고 있다(E1·E3).
- 그 두 홀더는 간격이 달라서 CLA216의 Ø1.7 구멍과 맞지도 않는다.
- 도면에 「Minimum MBFL 2.85」가 렌즈를 CLA216에 바로 끼우는 기준으로 정의돼 있다. 위에 홀더를 하나 더 얹으면 이 규격은 의미가 없어진다.
- 따라서 FAQ는 **다른 제품(나사 없는 필터 전환기)의 문구를 옮겨 온 것**으로 본다(추정). 도면과 사진을 근거로 판정한다.
- 판정은 바뀌지 않지만, 나중에 Commonlands에 연락할 일이 생기면 확인 질문 후보로 남긴다(지금은 연락하지 않음).

## 3. 초점 조건 (기존 기구 식 그대로)

mechanical `stack-reference.md` §3.1의 식을 그대로 인용한다. 이 판정으로 바뀌는 항은 없다.

- ③ 초점: 렌즈 뒤끝 = 상면 + MBFL이고, 이것이 홀더 바닥 + 최소 MBFL 2.85 이상이어야 한다.
  - p + 0.835 + 2.9(최악 MBFL) ≥ s + 2.85 → **s − p ≤ 0.885** (공칭 MBFL 3.2면 ≤ 1.185)
- 기준안 (a′): p 0.75, s 1.5 → s − p = 0.75 → 최악 여유 0.135, 공칭 여유 0.435
- CIL093 MBFL 3.2±0.3(R-007 ①)과 CLA216 최소 MBFL 2.85(E1)는 같은 바닥 기준면을 쓴다. 그래서 **추가 홀더가 없는 지금 적층이 도면 규격의 직접 적용**이다.

### (참고) 홀더가 필요했다면 — O-75b 기본 적층과 비교

O-75b 기본 적층은 「M12 홀더를 전면 보드에 따로 고정하고, ICR을 홀더와 센서 사이에 끼우는」 구조다. CLA216에는 자체 암나사가 있어 이 구조가 적용되지 않는다. 그래도 별도 홀더를 쓰는 다른 ICR이라면 어떻게 되는지 적어 둔다.

- 렌즈 뒤끝은 별도 홀더의 최소 MBFL 기준면으로 정해진다. 그 아래 ICR 두께(필터 0.3 + 구동부)만큼 센서면이 멀어진다.
- CIL093의 MBFL 3.2±0.3로는 ICR 몸체 높이(수 mm)를 흡수할 수 없다. 렌즈를 홀더 안쪽까지 넣어도 필요한 상거리가 MBFL을 넘는다.
- 따라서 이 렌즈로는 「홀더 + 아래쪽 별도 ICR」 적층이 성립하지 않는다(계산 정성, 수치 미산출).
- 이 점에서도 ICR 일체형 홀더인 CLA216이 맞는 선택이다.

## 4. 참고: 다른 Commonlands M12 홀더 (필요 없음, 기록만)

| 품번 | 구멍 간격 | 높이 | 재질 | 가격 · 재고 (2026-11-27) | 출처 |
|---|---|---|---|---|---|
| CLA019-LCP | 18mm | 12mm | LCP | $4.50 · 재고 208~295(페이지마다 다름) | https://www.commonlands.com/cla019-lcp (검색 요약) |
| CLA024-LCP | 22mm | 12mm | LCP | 미확인 | https://commonlands.com/cla024 (검색 요약) |
| CLA020-PC | 20mm | 10.0mm | 흑색 PC | $4.50 · **품절** | https://de.commonlands.com/collections/board-lens-accessories/products/m12-lens-mount-20mm-spacing (직접 확인) |
| CLA021 | 20mm | 7.4(또는 7)mm | LCP | 미확인 | https://commonlands.com/products/m12-lens-mount-20mm-spacing-cla021 (검색 요약) |

## 5. 후속 조치

| 대상 | 조치 |
|---|---|
| R-017 비용표 | 「M12 렌즈 홀더 (BOM 누락)」 행을 뺀다 → R-017b에서 반영 |
| bom-full · 회로도 · 기구 | 바꿀 것 없음 (MH1 = CLA216-ICR, `M12_Holder_20mm_CLA216-ICR` 풋프린트 유지) |
| G2 실측 | R-007의 남은 확인 항목은 그대로다: 공동 깊이 1.2~1.25, BXF4677 강판 귀 여부 |

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| H1 | FAQ와 도면·사진의 불일치 | 도면(M12x0.5 표기, 최소 MBFL)과 사진(렌즈 직결)을 따른다 | 치수가 들어간 공식 도면이 1차 근거다. FAQ는 간격이 맞지 않는 홀더를 가리켜 내적 모순이 있다 | 제조사 확인 (지금은 연락 금지라 후보로만 남김) |
| H2 | R-017 스크립트 커밋 위치 | R-017 레인(t-20261127-025109-aefa)의 `docs/research/r017/`에 넣는다(R-017b와 함께) | 비용 CSV가 그 레인에만 있다. 이 레인에서 같은 파일을 새로 만들고 R-017b에서 고치면 병합 때 양쪽 추가 충돌이 난다 | 이 레인에 넣기 (orch 원지시) |

## 돌린 명령

- `curl`로 제품 페이지(de/ja/ko 200, 본 도메인 429), 상품 JSON, 도면 webp, 사진 2장을 받았다(scratchpad). 종료 0
- `python -I`(PIL)로 webp→png 변환 후 육안 판독했다
- 저장소 검사 명령: 문서만 추가해서 돌리지 않았다
