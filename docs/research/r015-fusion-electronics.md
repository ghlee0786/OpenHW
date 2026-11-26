# R-015 Fusion Electronics 교차 검토 가능성 · KiCad → Fusion 기구 연동

- 배정: orch t18r R-015 (사용자 지시 2026-11-27) · 작성 research t18s · 확인일 2026-11-27
- 범위: 공식 문서와 포럼 근거만 봤다. **Fusion은 조작하지 않았다**(mechanical 소관). 설치·계정·외부 연락도 하지 않았다.
- 표에 「(요약)」이 붙은 항목은 forums.autodesk.com과 www.autodesk.com 본문이 403으로 막혀 검색 결과 요약으로만 확인한 것이다.

## 결론

1. **Fusion Electronics로 KiCad를 전기 쪽 교차 검토하는 경로는 쓰지 않는다.**
   - 가져오기 기능 자체는 공식으로 있다. 하지만 지원 범위는 「**KiCad v7 files or higher**」라고만 적혀 있고, KiCad 10 파일을 지원하는지는 확인하지 못했다.
   - KiCad의 넷 클래스와 `.kicad_dru` 규칙이 Fusion으로 넘어가는지는 문서에 없다. 그래서 Fusion DRC는 KiCad 원본 규칙으로 판정한 결과가 아니고, 판정 기준으로 쓸 수 없다.
   - 층 대응, 차동쌍, 존, 3D 모델의 손실 범위는 공식 문서에 없다(미확인). 공식 문서가 밝힌 손실은 격자 설정 하나뿐이다.
2. **전기 판정은 KiCad `kicad-cli`가 맡는다** (`pcb drc --schematic-parity --refill-zones --exit-code-violations`, `sch erc`).
3. **Fusion은 기구 검토에만 쓴다.** KiCad 10에서 보드별 STEP을 내보내 Fusion에 가져오고, 2보드 적층·간섭·외함 검토를 한다(아래 「기구 연동 절차」).
4. **라이선스:** 개인용(Personal, 2027-01-28부터 「Starter」로 이름이 바뀜)은 「not for use in primary employment, company environments」 조건 때문에 **이 PoC에 쓸 수 없다**. 상용 구독이나 Fusion for Startups(등록 법인)가 필요하다. 이 PC의 Fusion 라이선스 종류는 사용자가 확인할 일이다(tool-status.md에 「4일 후 만료 안내」가 기록돼 있음).

## 1. Fusion Electronics의 KiCad 가져오기

| 항목 | 내용 | 근거 |
|---|---|---|
| 지원 여부 | 데이터 패널 Upload에서 「KiCad Design Files」를 고른다. 프로젝트 파일을 고르면 관련 회로도·보드 파일을 자동으로 함께 가져온다 | https://help.autodesk.com/cloudhelp/ENU/Fusion-ECAD/files/ECD-KICAD-IMPORTER-DO.htm |
| 지원 버전 | 원문: 「Fusion only supports the import of KiCad v7 files or higher.」 — 8·9·10을 명시한 문장은 없다 → **KiCad 10은 미확인** | https://help.autodesk.com/cloudhelp/ENU/Fusion-ECAD/files/ECD-KICAD-IMPORTER.htm (직접 다시 확인함) |
| 파일 대응 | .kicad_pro→.fprj · .kicad_sch→.fsch · .kicad_pcb→.fbrd · .kicad_mod→.flbr. 심볼 라이브러리(.kicad_sym)는 대응 형식이 없다 | 같은 쪽 |
| 회로도 | 「KiCad schematic files are combined into one file and translated into different sheets」. 계층 시트는 Sheets 방식(참조 부호 유지) 또는 Modules 방식으로 펼쳐진다 | 같은 쪽 |
| 공식 손실 | 「Fusion does not import grid setting preferences from KiCad files.」 이 밖의 손실 항목은 적혀 있지 않다 | 같은 쪽 |
| 층(4층·내층) · 차동쌍 · 넷 클래스·규칙 · 존 재충전 · 커스텀 패드 · 실크 글꼴 | 공식 문서에 없다 → **미확인** | — |
| 3D 모델 | 가져온 뒤 다시 직접 연결해야 한다는 사용자 보고가 있다 (요약) | https://forums.autodesk.com/t5/fusion-electronics-forum/import-kicad-symbol-with-3d-model/td-p/13604027 |
| 알려진 문제 | KiCad 8 파일을 KiCad 7에서 다시 저장해야 들어갔다는 보고, 보드 열기 실패, 무한 로딩 (요약) | https://forums.autodesk.com/t5/fusion-electronics-forum/uploaded-pcb-files-from-kicad-won-t-open/td-p/13686057 · https://forums.autodesk.com/t5/fusion-electronics-forum/kicad-import-is-totally-not-working/td-p/13326908 |
| 구버전으로 저장 | KiCad는 상위 버전 파일을 하위 버전 형식으로 저장하지 못한다. 10→7 변환 우회로는 없다 (요약) | https://forum.kicad.info/t/can-a-project-edited-with-newer-version-of-kicad-opened-with-older-version/25302 |
| 중간 형식 | KiCad 10이 내보내는 형식은 IPC-2581, ODB++, GenCAD, Specctra DSN, Hyperlynx, IDF, VRML과 3D 형식이다. **EAGLE 내보내기는 없다**(가져오기만 됨). Fusion이 IPC-2581·ODB++를 가져오는지는 미확인이다 | https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html |

## 2. Fusion의 DRC·ERC

| 항목 | 내용 | 근거 |
|---|---|---|
| ERC | Schematic Validate 도구 모음에서 ERC를 실행하고, 결과는 ERC Errors 패널에 나온다 | https://help.autodesk.com/cloudhelp/ENU/Fusion-ECAD/files/ECD-RUN-ERC-TSK.htm |
| DRC | 규칙은 Design Rules 대화상자에서 정하고 `.edru` 파일로 저장한다 | https://help.autodesk.com/cloudhelp/ENU/Fusion-ECAD/files/ECD-DESIGN-RULES.htm |
| KiCad 규칙이 넘어가는지 | 문서에 없다 → **미확인**. 규칙을 Fusion에 손으로 다시 넣어야 할 가능성이 높아, 원본(KiCad `carrier.kicad_dru` · `front.kicad_dru`)과 이중 관리가 된다 | — |

## 3. 라이선스 (2026-11 기준)

| 구분 | 내용 | 근거 |
|---|---|---|
| 개인용 | 「For personal, non-commercial projects only. … not for use in primary employment, company environments」 → **사용 불가**. 전자 설계 제한은 비교표 현재 판 기준 2 sheets/schematic, 4 signal layers, 보드 면적 무제한이다(예전 표기는 2층, 80 cm²) | https://www.autodesk.com/products/fusion-360/personal · https://www.autodesk.com/products/fusion-360/personal/compare |
| 상용 구독 | 월 $85, 연 $680, 3년 $2,040. 최대 999시트, 64개 신호층 | 같은 비교표 |
| 2027-01-28 요금제 개편 | Starter(비상용) · Standard $680 · Professional $1,150 · Enterprise $2,250 (요약) | https://www.autodesk.com/campaigns/fusion-plans · https://www.autodesk.com/products/fusion-360/blog/introducing-new-autodesk-fusion-plans-what-you-need-to-know/ |
| Fusion for Startups | 등록 법인, 사용자 10명 이하, 3년. 용역사·컨설팅사는 제외. 매출과 가격 조건의 현재 값은 **미확인** | https://www.autodesk.com/products/fusion-360/startups |

## 4. 기구 연동 절차 (KiCad → STEP → Fusion)

### 4.1 내보내기

KiCad 10.0.8 `kicad-cli pcb export step`. 아래 옵션은 이 PC에서 `--help`로 직접 확인했다(종료 0). 공식 문서: https://docs.kicad.org/10.0/en/cli/cli.html

```
kicad-cli pcb export step --subst-models --no-dnp --user-origin <공통원점> --include-silkscreen -f -o carrier.step hardware/pcb/<…>/carrier.kicad_pcb
kicad-cli pcb export step --subst-models --no-dnp --user-origin <공통원점> --include-silkscreen -f -o front.step   hardware/pcb/<…>/front.kicad_pcb
```

| 옵션 | 쓰는 이유 |
|---|---|
| `--subst-models` | 풋프린트의 VRML 모델을 같은 이름의 STEP/IGS 모델로 바꾼다. KiCad 기본 라이브러리 부품에는 필수다 |
| `--no-dnp` | DNP 부품(D_IR_B1·B2 등)을 3D에서 뺀다. 실장 상태와 같아진다. 최대 외형을 보려면 빼지 않은 판도 하나 만든다 |
| `--user-origin` · `--drill-origin` · `--grid-origin` | 두 보드가 **같은 기준점**(예: 장착 구멍 중심 또는 BTB 기준)으로 나와야 Fusion에서 적층 정렬이 단순해진다. 기준점은 pcb 담당이 정한다 |
| `--include-silkscreen` · `--include-soldermask` | 두께 없는 면으로 들어간다. 색 구분과 식별용이다(선택) |
| `--include-tracks` · `--include-pads` · `--include-zones` | 동박까지 넣는다. 파일이 커지고 시간이 걸린다. 기구 검토에는 보통 필요 없다 |
| `--board-only` · `--component-filter J1,MH1` | 기판만, 또는 특정 부품만 넣은 가벼운 판 |
| 색상 | CLI에는 색 옵션이 없다. 부품 STEP 모델에 들어 있는 색이 그대로 나간다. 9.0.4에서 부품 색이 빠지던 문제(#21865)는 9.0.8에서 고쳐졌다 → 10.0.8은 고쳐진 판으로 본다. 다만 실제 출력은 미확인이다 · https://gitlab.com/kicad/code/kicad/-/issues/21865 |

- 다른 형식: glb, stl, brep, xao, ply, u3d, 3dpdf도 같은 계열 옵션으로 나온다. IDF(.emn/.emp)는 GUI의 File → Export에만 있고 CLI에는 없다. Fusion은 기본 기능으로 IDF를 읽지 못한다(유료 서드파티 애드인만 있음).

### 4.2 Fusion에서 (mechanical 담당)

1. 두 STEP을 Fusion에 올린다. AP214 RGB 색은 면 외관으로 들어오는 것으로 보고된다(포럼 요약, 공식 문서는 미확인).
2. 같은 원점으로 내보냈으면 Z 방향 적층 간격만 준다. 간격은 r007-mech-dims.md의 BTB 결합 높이, 모듈 두께 등 확정된 값을 쓴다.
3. Inspect → Interference로 간섭을 본다. 렌즈, 홀더(CLA216), BTB, RJ45, DC 잭 높이가 대상이다.
4. 가져온 STEP은 원본과 연결되지 않는 형상이다. Fusion의 2D↔3D PCB 동기화는 Fusion Electronics 보드에만 된다. **보드가 바뀌면 KiCad에서 다시 내보내 교체**한다. STEP 파일에는 원본 커밋 해시를 기록한다.

## 5. 그 밖의 무료 교차 검토 수단 (참고)

| 수단 | 요지 |
|---|---|
| `kicad-cli pcb drc --schematic-parity --refill-zones --exit-code-violations` · `sch erc` | 원본 규칙으로 판정하고 종료 코드가 남는다 → **판정 기준** |
| Siemens Vu2581 / ODB++ Viewer (무료, 로컬) | KiCad `pcb export ipc2581` / `odb` 결과를 다른 렌더러로 다시 보는 육안 교차 확인. 설치는 사용자 결정 · https://resources.sw.siemens.com/en-US/download-free-viewer-for-ipc-2581/ |
| KiCanvas · Altium 365 Viewer | 웹 업로드 방식이라 외부 업로드 금지 규칙에 걸린다 → 제외 |

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| F1 | 전기 교차 검토 도구 | Fusion 가져오기를 쓰지 않는다. 판정은 kicad-cli | KiCad 10 지원과 규칙 이전이 미확인이고 문제 보고가 반복된다. 설계 원본은 KiCad로 유지한다 | mechanical이 **사본**으로 시험 가져오기를 한 번 해 보고, 층·넷 수만 비교(판정에는 쓰지 않음) |
| F2 | 기구 연동 형식 | STEP (`--subst-models --no-dnp` + 공통 원점) | 공식 CLI라 재현할 수 있고 색 문제는 고쳐졌다. Fusion이 기본 기능으로 읽는다 | GLB/STL(가벼운 확인용), GUI IDF(애드인 필요) |
| F3 | 동박 포함 | 기본은 빼고, 필요할 때만 `--include-*` | 파일 크기와 시간. 기구 간섭에는 부품과 기판만 있으면 된다 | 차폐·방열 검토 때 동박 포함 판 |
| F4 | 라이선스 | 개인용 제외. 상용 또는 Startups 중 사용자가 결정 | 개인용 조건이 회사 환경을 금지한다 | — |

## 돌린 명령

- `kicad-cli pcb export step --help` (KiCad 10.0.8): 종료 0. 옵션 목록을 확인했고, 실제 내보내기는 하지 않았다.
- 웹 조사: 서브에이전트 1개와 공식 도움말 직접 확인 1회. 저장소 검사 명령은 문서만 추가했으므로 돌리지 않았다.
