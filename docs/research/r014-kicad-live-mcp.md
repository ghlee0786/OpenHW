# R-014 KiCad 실시간 작업 (IPC API · MCP)

- 배정: orch t18r R-014 (사용자 질문 2026-11-27: 「KiCad 창이 대기만 하는데 MCP로 바로 작업·수정·화면 갱신이 되게 하라」) · 작성 research t18s · 확인일 2026-11-27
- 범위: 조사와 읽기만 했다. 열린 KiCad 창은 건드리지 않았다(GUI 단일 작성자는 pcb). 설치와 설정 변경은 하지 않았다. 바꿔야 할 것은 아래 「변경 목록」에만 적었고, 결정은 사용자가 한다.

## 결론

1. **창이 대기만 하는 직접 원인은 이 PC의 KiCad 설정에서 IPC API 서버가 꺼져 있는 것이다.**
   - 근거: `%APPDATA%\kicad\10.0\kicad_common.json`에 `"api": {"enable_server": false, …}`가 있다.
   - 그 결과 `%TEMP%\kicad\` 소켓 폴더가 없다. MCP는 KiCad와 연결되지 않고, kicad-cli로 파일만 다룰 수 있다.
   - 이미 설치된 MCP(iQreu/kicad-mcp)는 실시간 편집에 IPC API(kipy)를 쓴다. 그 서버 안내문도 「requires a running KiCad PCB editor with the API enabled」라고 적고 있다.
2. **설정을 켜고 KiCad를 다시 시작한 뒤, PCB 편집기에 보드를 열어 두면 지금 MCP 그대로 실시간 편집이 된다.** 새 MCP 서버는 필요 없다.
   - 실시간으로 되는 것: 배치, 트랙, 비아, 존과 재충전, 외곽선, 선택, 저장. 한 번 호출이 실행 취소 한 단계가 된다.
3. **KiCad 10의 한계 (설정을 켜도 남는 것):**
   - 회로도 편집기는 IPC를 지원하지 않는다.
   - IPC로 DRC를 실행할 수 없다. DRC는 kicad-cli로 파일에 대해 돌린다.
   - 라우터와 오토라우팅이 없다.
   - 회로도→PCB 넷리스트 반영(F8)이 없다.
   - 헤드리스 모드가 없다(KiCad GUI가 떠 있어야 한다).
   - 위 기능들은 KiCad 11에서 들어온다(헤드리스 `kicad-cli api-server`, 회로도 API, `ImportNetlist`). KiCad 11은 아직 nightly다.
4. **주의:** 지금 열려 있는 pcbnew 창 2개(PID 150640, 49484, 2026-11-27 01:21 시작)는 다른 세션 scratchpad의 `kicad-view/front.kicad_pcb`와 `carrier.kicad_pcb` **사본**을 열고 있다. 저장소의 `hardware/pcb/outline/*`이 아니다. 실시간 편집을 하려면 pcb 담당이 **자기 레인의 보드 파일**을 열어야 한다.

## 1. 이 PC에서 확인한 것 (읽기만)

| 항목 | 값 | 확인 방법 |
|---|---|---|
| KiCad | 10.0.8, `C:/Users/gh/AppData/Local/Programs/KiCad/10.0` | `kicad-cli` 버전, `pcbnew.Version()` |
| IPC 서버 설정 | **`api.enable_server: false`** · `api.interpreter_path: …\KiCad\10.0\bin\pythonw.exe` | `%APPDATA%\kicad\10.0\kicad_common.json`을 JSON으로 읽음 |
| IPC 소켓 | `%TEMP%\kicad\` 폴더 없음 → 서버가 안 떠 있음 | `Get-ChildItem` |
| 실행 중인 KiCad | `kicad.exe` 없음. `pcbnew.exe` 2개(단독 실행, scratchpad 사본을 엶). `kicad-cli.exe` 3개 | `Get-CimInstance Win32_Process` |
| 번들 Python의 kipy | **없음** (`No module named 'kipy'`. kicad-python, pynng, protobuf도 없음). SWIG `pcbnew` 모듈은 있음(10.0.8) | `…\KiCad\10.0\bin\python.exe -I -c "import kipy"` |
| MCP 서버 | iQreu/kicad-mcp, 커밋 7a5ee2e(2026-07-14), MIT, 별도 venv `C:/Users/gh/.local/share/openhw-tools/kicad-mcp` | `git log`, `LICENSE`, INSTALL-AUDIT.md |
| MCP venv 패키지 | kicad-python **0.9.0** · pynng 0.9.0 · protobuf 5.29.6 · mcp 1.30.0 · fastmcp 3.4.11 | `importlib.metadata` |
| MCP 역할 설정 | `orchestration/roles/pcb.mcp.json`(review, schematic도 같음): `KICAD_ROOT=…/KiCad/10.0` · `KICAD_MCP_ENABLE_SCH_EDIT=0` | 파일 읽기 |
| 이전 검증 (main) | e1ae0ad: 역할 MCP 설정을 실제 설치 경로로 맞춤. 93e9b82 `docs/research/tool-status.md`: 「initialize/tools/list 55개 및 kicad_status 성공 … PCB Editor가 열리지 않아 GUI IPC false. GUI 읽기/편집, ERC/DRC/출력 실검증은 미수행」 | `git show` |
| smoke-result.json | `ipc_connected: false` · `api_enabled_in_settings: null`(그때는 설정 파일이 아직 없었음) · 진단: 「No KiCad process is running」 | 파일 읽기 |

- 그러니까 이전 검증은 「서버가 뜨고 도구 목록이 나온다」까지만 했다. **실시간 연결은 한 번도 성공한 적이 없다.** 지금은 KiCad 창이 떠 있지만 설정이 꺼져 있어 연결되지 않는다.

## 2. KiCad 10 IPC API 구조와 켜는 법

| 항목 | 내용 | 근거 |
|---|---|---|
| 구조 | KiCad GUI가 서버이고, Protocol Buffers 메시지를 NNG로 보낸다. 외부 앱과 플러그인이 클라이언트다 | https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/ |
| 공식 Python 클라이언트 | PyPI `kicad-python`, import 이름은 `kipy`. 최신 **0.9.2 (2026-11-26)**, 「KiCad 9.0 or higher」. 일부 기능은 10.0.6, 10.0.7 이상을 요구한다 | https://pypi.org/project/kicad-python/ |
| 켜는 법 (UI) | KiCad 10 매뉴얼: Preferences → Plugins → **「Enable KiCad API」** (「When enabled, you can use plugins that interact with KiCad's IPC API.」) | https://docs.kicad.org/10.0/en/kicad/kicad.html |
| 설정 키 | `kicad_common.json`의 `api.enable_server`(기본값 false) · `api.interpreter_path` | https://gitlab.com/kicad/code/kicad/-/raw/10.0/common/settings/common_settings.cpp |
| 소켓 (Windows) | 「created by KiCad in the user's temporary directory when KiCad is launched」 → `%TEMP%\kicad\api.sock`. 인스턴스가 여러 개면 둘째부터 `api-<PID>.sock`. kipy 기본 주소는 `ipc://{tempdir}\kicad\api.sock`이고 `KICAD_API_SOCKET`으로 바꿀 수 있다 | https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/ · https://gitlab.com/kicad/code/kicad/-/raw/10.0/common/api/api_server.cpp |
| GUI 필요 | 원문: 「The IPC API in KiCad 9 and 10 only supports communication with a running instance of the KiCad GUI.」 프로젝트 관리자만 떠 있으면 「no handler available」이 나므로, **PCB 편집기에 보드가 열려 있어야** 한다 | for-addon-developers 페이지(직접 다시 확인함) · https://github.com/nmlsports/kicad-mcp |
| 헤드리스 | 「Support for running in headless mode through kicad-cli was added for KiCad 11.」 KiCad 10에는 없다 | 같은 페이지 |
| 번들 Python의 kipy | **외부 MCP 서버에는 필요 없다**(MCP는 자기 venv의 kicad-python을 쓴다). KiCad 안에서 도는 IPC 플러그인(`plugin.json`)을 쓸 때만 관계있고, 그때는 KiCad가 플러그인마다 venv를 자동으로 만든다 | for-addon-developers 페이지 |
| 로그 | `kicad_advanced`에 `EnableAPILogging=1`을 넣으면 `logs/api.log`에 남는다(문제 진단용) | 같은 페이지 |

## 3. 열린 pcbnew에서 실시간으로 되는 것과 한계 (KiCad 10, kicad-python 0.9.x)

| 작업 | IPC 실시간 | 지금 MCP(iQreu)의 도구 | 비고 · 근거 |
|---|---|---|---|
| 풋프린트 배치·이동·회전 | 예 (`update_items`) | `place_footprint(s)` · `move_footprint` · `remove_footprint` | 라이브러리에서 새 풋프린트를 꺼내 놓는 `PlaceFootprintFromLibrary`는 KiCad 11 proto에만 있다. KiCad 10.0.x에서는 풋프린트를 고칠 때 3D 모델이 빠지는 등 손실이 보고됐다(nmlsports README) → **첫 시험에서 확인 필요** |
| 트랙·비아 | 예 (`create_items`) | `add_track(s)` · `add_via` · `remove_items` | 좌표로 지정한 선분이다. **대화형 라우터나 푸시앤쇼브가 아니다** |
| 존 생성·재충전 | 예 (`refill_zones`) | `add_copper_zone` · `refill_zones` | 재충전 중에는 「KiCad is busy」 → 서버가 자동으로 다시 시도한다 |
| 실크·도형·외곽선 | 예 (도형·텍스트 생성) | `draw_board_outline` (Edge.Cuts) | 실크 전용 도구는 없다. kipy로는 가능하지만 이 MCP에는 노출돼 있지 않다 |
| 선택·하이라이트 | 예 | `select_items` · `get_selection` · `clear_selection` | — |
| 실행 취소 | 예 (`begin_commit`/`push_commit` → 한 단계) | 호출 1회 = 실행 취소 1단계 (README) | 사람이 Ctrl+Z로 되돌릴 수 있다 |
| 저장·되돌리기 | 예 (`save` · `save_as` · `revert`) | `save_board` | **편집은 메모리에만 있고, 저장해야 파일이 바뀐다** |
| 화면 갱신 | 자동 (변경이 바로 편집기에 그려진다) | — | 줌·팬 명령은 없다 |
| 스택업·넷·넷 클래스 읽기 | 예 | `board_info` · `list_nets` · `list_netclasses` | 넷 클래스 쓰기(`set_netclass`)는 파일 쪽 도구다 |
| **DRC** | **아니오** (10.0 proto에는 마커를 넣는 `InjectDrcError`만 있다) | `run_drc` = kicad-cli를 파일에 대해 실행. 경로를 안 주면 먼저 저장한다 | 결과는 GUI의 DRC 마커로 뜨지 않는다 · https://gitlab.com/kicad/code/kicad/-/raw/10.0/api/proto/board/board_commands.proto |
| **라우팅·오토라우팅** | **아니오** | 없음 | KiCad 11에 외부 라우터 결과 가져오기(`ImportSpecctraSession`)가 들어온다 |
| **회로도 편집기** | **아니오**: 「KiCad 9 and 10 only support IPC API plugins in the PCB Editor」 | `sch_*`는 **파일 편집**이고 기본값으로 꺼져 있다(`KICAD_MCP_ENABLE_SCH_EDIT=0`) | 파일을 고친 뒤 eeschema에서 다시 열어야 보인다(자동 다시 읽기 없음) |
| 회로도→PCB 반영 (F8) | **아니오** (`ImportNetlist`는 KiCad 11) | 없음 | 사람이 GUI에서 F8을 누르거나 pcb 담당이 처리한다 |
| 출력·플롯 | 아니오 (「no support for plotting or exporting」) | `export_*` = kicad-cli | — |

## 4. IPC를 쓰는 MCP 서버들 (README 기준, 실행해 보지는 않음)

| 이름 | 라이선스 | 방식 | KiCad | 유지 상태 (확인일 기준) | 메모 |
|---|---|---|---|---|---|
| **iQreu/kicad-mcp** (설치돼 있음) https://github.com/iQreu/kicad-mcp | MIT | **IPC(kipy)로 실시간 PCB** + kicad-cli + 회로도 파일 편집(선택) | 10 | 커밋 10개, 릴리스 없음, 별 0. 설치본은 7a5ee2e(2026-07-14) | 도구 55개. 여러 인스턴스일 때 `api.sock*`를 자동으로 찾는다 |
| belaszalontai/kipilot-mcp https://github.com/belaszalontai/kipilot-mcp | Apache-2.0 | IPC 전용 | 10 (회로도는 11) | v0.4.0 (2026-10-29), 별 약 19 | Windows 패키징을 검증했다고 적혀 있다. 도구 144개 |
| tim-programmer/kicad10-mcp https://github.com/tim-programmer/kicad10-mcp | MIT | IPC + kicad-cli + 회로도 s-expr | 10 | 릴리스 없음, push 2026-11-23 | 모든 편집을 commit으로 감싼다 |
| nmlsports/kicad-mcp https://github.com/nmlsports/kicad-mcp | MIT | IPC 편집 + 읽기 | 9+ (10.0.6 시험) | push 2026-10-01 | KiCad 10 손실 문제를 문서로 정리해 두었다 |
| turbyho/kicad-workbench https://github.com/turbyho/kicad-workbench | MIT | kicad-cli + pcbnew + `ipc_*` | 10.0.6 전용 | 0.2.0 (2026-11-20) | Windows에서 시험하지 않았다고 적혀 있다 |
| havamal-65/KiCad-MCP https://github.com/havamal-65/KiCad-MCP | MIT | IPC 우선 → SWIG 브리지 → 파일 | 9/10 | push 2026-10-10 | Windows 설치기 있음(서명 안 됨) |
| mixelpixx/KiCAD-MCP-Server https://github.com/mixelpixx/KiCAD-MCP-Server | MIT | **SWIG가 주**, IPC는 실험 단계 | 9/10 | v2.9.0 (2026-11-12), 별 약 3.6k | SWIG는 KiCad 11에서 빠진다 |
| Orchis-ai-LLC/Konnect-EDA https://github.com/Orchis-ai-LLC/Konnect-EDA | **비공개 소스** (1.0 이후 기업은 유료) | IPC 실시간 + 회로도 s-expr | 10→11 | v0.15.0 (2026-11-21) | 라이선스 때문에 제외 |
| 파일·CLI 전용 (실시간 아님) | — | Seeed-Studio/kicad-mcp-server(MIT) · lamaalrajih/kicad-mcp(MIT, 2025-10 이후 멈춤) · ProductOfAmerica/mcp-server-kicad(GPL-3.0) · oaslananka/kicad-mcp-pro(AGPL-3.0) · biosshot/kicad-copilot(MIT) | 9/10 | — | 창에 바로 반영되지 않는다 |

- SWIG `pcbnew` 바인딩은 KiCad 9부터 deprecated다. 「The current plan is to remove the SWIG bindings in KiCad 11.0」 → 새 도구는 IPC 기반이어야 오래 쓸 수 있다. https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/
- 자세한 비교의 출처 URL은 위 표의 저장소 README와 GitHub releases이고, 확인일은 2026-11-27이다.

## 5. 변경 목록 (사용자 결정, 지금은 하지 않았음)

| # | 무엇 | 출처·버전 | 바꾸는 곳 | 필수 |
|---|---|---|---|---|
| C1 | **KiCad API 켜기**: Preferences → Plugins → 「Enable KiCad API」를 켠 뒤 **KiCad를 다시 시작** | KiCad 10.0.8 매뉴얼 | `%APPDATA%\kicad\10.0\kicad_common.json`의 `api.enable_server` false→true (UI로 바꾸면 이 값이 써진다) | **필수** |
| C2 | pcb 담당이 **자기 레인의 보드 파일을 PCB 편집기로 연다**. 지금 열린 scratchpad 사본 창 2개는 연 세션이 정리한다 | — | 운영 절차 | **필수** |
| C3 | 인스턴스가 여러 개면 대상 소켓을 지정한다: `KICAD_API_SOCKET=ipc://%TEMP%\kicad\api-<PID>.sock` | kipy, iQreu README | pcb.mcp.json의 `env` (이 MCP는 자동으로 찾지만 대상을 확정하려면 지정) | 선택 |
| C4 | MCP venv의 kicad-python을 0.9.0 → 0.9.2 (2026-11-26)로 올린다 | https://pypi.org/project/kicad-python/ | `C:/Users/gh/.local/share/openhw-tools/kicad-mcp/.venv` | 선택 (0.9.0으로도 10.0.8과 동작할 것으로 보지만 미확인) |
| C5 | 문제 진단용 API 로그 | KiCad dev-docs | `%APPDATA%\kicad\10.0\kicad_advanced`에 `EnableAPILogging=1` | 선택 |
| — | 번들 Python에 kipy 설치 | — | — | **불필요** (외부 MCP는 자기 venv를 쓴다) |

### 켠 뒤 첫 확인 순서 (pcb 담당, 보드 **사본**으로)

1. `kicad_status` → `ipc_connected: true`와 연결된 보드 경로를 확인한다.
2. `board_info` · `list_footprints`로 읽기를 확인한다.
3. 시험 트랙 1개를 `add_track`으로 그어 화면에 바로 보이는지 확인한 뒤, Ctrl+Z로 한 단계에 사라지는지 확인한다.
4. 풋프린트 1개를 `move_footprint`로 회전·이동해 3D 모델과 필드가 유지되는지 확인한다(KiCad 10 손실 보고 항목).
5. `save_board`와 `run_drc`(kicad-cli) 종료 코드를 확인한다.

- 3번과 4번의 화면 확인은 사람 눈이 필요하다(verifiable 아니오). 나머지는 도구 반환값으로 판정한다.

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| K1 | MCP 서버 | **지금 설치된 iQreu/kicad-mcp를 유지**하고 설정만 켠다 | 이미 IPC(kipy) 기반이고 Windows용이다. 역할 설정과 감사 기록도 있다. 원인은 서버가 아니라 KiCad 설정이다 | KiPilot(Apache-2.0, 도구 144개, Windows 검증, 릴리스 있음). 설치는 사용자 결정 |
| K2 | 회로도 실시간 편집 | KiCad 10에서는 하지 않는다. 파일 편집은 기본값(꺼짐)을 유지한다 | API가 없다. 파일 편집 후 다시 열어야 하므로 실시간이 아니고, 단일 작성자 규칙과도 부딪친다 | KiCad 11 정식판이 나오면 다시 검토 |
| K3 | DRC | kicad-cli를 **저장된 파일**에 대해 돌린다 | IPC로는 실행할 수 없다. 종료 코드가 판정 기준이다 | GUI에서 사람이 DRC 실행 |
| K4 | 번들 Python kipy | 설치하지 않는다 | 외부 MCP에는 필요 없다 | IPC 플러그인을 만들게 되면 KiCad가 venv를 자동으로 만든다 |

## 돌린 명령 (모두 읽기 전용)

- `python -I`로 `kicad_common.json` 읽기: 종료 0
- KiCad 번들 `python.exe -I -c "import kipy"` (모듈 없음), `import pcbnew` (10.0.8): 종료 0
- MCP venv의 `importlib.metadata` 버전 조회: 종료 0
- `Get-CimInstance Win32_Process`, `tasklist`, `%TEMP%\kicad` 폴더 확인: 종료 0
- 웹 조사: 서브에이전트 1개. dev-docs IPC 페이지와 iQreu 저장소는 직접 다시 확인했다
- 저장소 검사 명령: 문서만 추가했으므로 돌리지 않았다
