[orch t18r → mechanical] 배정 REN-001 · VD-001 끝점 — 최종 3D 렌더 (사용자 목표, lead 2026-11-27) — M-006/M-007과 같은 새 레인
■ 입력: M-007 전체 조립 STEP(캐리어·코어 모듈·전면·센서 블록·CLA216·렌즈·하니스·외함·SK 444+받침대·PMMA 창·폼). PCB 최종 커밋 전에는 현재 배선본으로 장면·재질·카메라를 먼저 만들고, 최종 STEP 오면 한 명령으로 교체·재렌더.
■ PCB 렌더: kicad-cli pcb render(레이트레이싱 quality high) 두 보드 앞·뒤·기울임 — 3D 모델 빠짐 0 상태(M-007 대체 모델이 pcb에 연결된 뒤 최종).
■ 제품 렌더: Blender 5.2(blender-render 스킬) — STEP→메시 변환은 무료 도구(FreeCAD/OCC/cadquery 등) 설치 허용(사용자 홈 격리·공식·버전·sha256 기록). 스튜디오 제품 샷: 앞·뒤·3/4·분해·단면·창 너머 렌즈/LED가 보이는 컷. 재질: 흑색 PETG 질감·흑색 아노다이즈 Al·PMMA 투명·PCB 녹색 마스크·금 도금(ENIG)·실크 흰색. 2560×1440 PNG, 턴테이블 MP4 약 8초. 장면 생성은 스크립트(bpy)로 재현 가능하게 커밋, 큰 산출물(PNG·MP4)은 validation/runtime/vd001/render/(gitignore) + 해시 목록 커밋.
■ 판정: 기계 — 파일 수·해상도·길이·입력 STEP 해시 일치(종료 코드). 사람 눈(verifiable 아니오) — VD-001 HTML에 모음(review V-006 형식).
■ GUI 단일 작성자: Fusion·Blender GUI는 mechanical만. 결제·유료 애드온 금지. 완료: 커밋 → hc send t18r → 셸 루트.
