[orch t18r → schematic] 배정 C-013 · 회로도 라벨 겹침 정리 (lead 2026-11-27, O-32 남은 것 — 원장 '발주 패키지 직전 정리 목록') — main(533d1b8 이후, C-012 포함)에서 새 레인
■ 범위: 두 보드 회로도의 라벨·글자·심벌 필드 겹침과 Rev 표기 정리(가독성만). 넷·연결·부품·DNP·UUID 변경 0. 생성기(boards.py)로 고치는 게 맞으면 생성기를 고치되 UUID가 바뀌지 않게(C-012처럼 HEAD 파일 최소 수정 + 생성기 출력과 UUID 제외 동일 확인).
■ 판정: ERC --exit-code-violations 두 보드 종료 0, netcompare C-012(f56945b) 대비 차이 0(종료 0), 겹침 수 전후(스크립트로 센 수치 — 글자 경계 상자 교차), 그림 앞뒤 비교 PNG(kicad-cli sch export svg → PNG) validation/runtime/kicad-gui/C-013/.
■ 주의: pcb 레인 파일 건드리지 않음, GUI 안 씀. 완료: 커밋 → hc send t18r.
