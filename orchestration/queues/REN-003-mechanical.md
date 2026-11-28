[orch t18r → mechanical] 배정 REN-003 · Fusion 재질·로컬 렌더 (사용자 지시 B, lead 전달 2026-11-27) — main c9ca2a7 이후 새 레인
■ 흐름: M-010 run_case로 가져온 KiCad STEP(3D 모델 포함) → Fusion 360에서 부품·보드·케이스에 Appearance: PCB 녹색 솔더마스크·금 도금(ENIG) 패드·실크 흰색·IC 검정 에폭시·커넥터 금속/플라스틱·외함(설계 재질 흑색 PETG에 맞는 무광 플라스틱 — lead 예시는 ABS/PC)·PMMA 투명 창·알루미늄 흑색 아노다이즈 방열판·폼·패드. 부품별 재질 배정은 이름 규칙 표로(스크립트로 재현).
■ Fusion 렌더: 로컬 렌더만 — 클라우드 렌더 크레딧·유료 사용 금지. 제품 샷(앞·뒤·3/4·분해·창 너머·커넥터 면) 2560×1440 이상. Blender 렌더도 같은 재질 체계로 맞춤(색·거칠기 값 표 공유).
■ 지금: pcb 최종 STEP 전이라 중간 커밋 STEP(be3125d·6df2865 또는 최신 WIP)으로 재질·카메라·조명 세팅 완성 → 최종 STEP 오면 교체·재렌더.
■ 보관: O-100(main validation/runtime/vd001/render/fusion/·blender/ + 대표본 docs/renders 커밋, 개당 <20MB), manifest에 사람 확인 항목.
■ 주의: Fusion 창에 '4일 후 만료' 표시 — 만료 전에 끝내고, 만료되면 D-003 #34 차선(CadQuery+Blender)으로. 결제·유료 애드온 금지. 완료: 커밋 → hc send t18r → 셸 루트.
