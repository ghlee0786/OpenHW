# R-025 · KiCad MCP 교체 설치 (mixelpixx/KiCAD-MCP-Server)

결정 근거: D-003 #52 (lead). 이 문서는 설치 기록만 남긴다.

## 결론

- mixelpixx/KiCAD-MCP-Server **v2.9.0**(MIT)을 사용자 홈 `C:/Users/gh/tools/kicad-mcp-server`에 설치했다. 설치 단계는 모두 종료 코드 0이다.
  - `npm install`, `npm run build`
  - 격리 venv 생성과 pip 설치
  - setup 사본(전역 줄 제외)
- `claude mcp add --scope local`로 `kicad`를 등록했다. `claude mcp list`는 main 경로와 pcb worktree 두 곳 모두 `✔ Connected`이다.
- pcb 칸용 설정 `orchestration/roles/pcb-kicad2.mcp.json`을 새로 만들었다.
  - 서버는 `kicad` 하나다. 기존 `pcb.mcp.json`에 kicad 하나뿐이므로, 보충 지시대로 kicad 서버만 바꿨다.
  - 기존 `pcb.mcp.json`은 그대로 두었다.
- 이 설정으로 서버를 stdio로 1회 기동했다. 종료 코드 0이고 도구 250개가 나왔다.
  - 백엔드는 IPC를 먼저 시도했지만, KiCad가 떠 있지 않아 연결이 거부됐다. 그래서 SWIG(pcbnew 10.0.8)로 대체돼 초기화됐다.
  - KiCad GUI는 열지 않았다.

## 출처 · 버전 · 해시

| 항목 | 값 |
|---|---|
| 저장소 | https://github.com/mixelpixx/KiCAD-MCP-Server.git (`--branch stable`) |
| 커밋 | `9dd467c2ba8df09a23490cc0b463f3942e908cae` (2026-11-11, "Merge pull request #532 … release/v2.9.0", 태그 v2.9.0) |
| 라이선스 | MIT (LICENSE 첫 줄 "MIT License", Copyright (c) 2024 mixelpixx) — Konnect(상업)는 제외 |
| package.json | `kicad-mcp` 2.9.0 |
| package-lock.json sha256 | `9e98ec58a70d2530311c4dd9fa84ae816465b075e5586500f3ed724c5c7e15f4` |
| dist/index.js sha256 (빌드 결과) | `7f8f2dfc0eee151c2d5a7f4dd9613f2f5b0da383a227ffe03b6ae630ed316df4` |
| requirements.txt sha256 | `43c4197de45688496540eafc1485464c91d36dfc29ea765d7856317ad1224248` |
| setup-windows.ps1 sha256 (원본) | `04fa1daa54b0986fefdc0d6fda8e9cd5353e7e4071e1d7b900dbaf5d3dca4d90` |
| Node | `C:/tools/node-v24.22.2-win-x64/node.exe` v24.22.2, sha256 `1c331340fa6cac5e4294725959070a143fa0507195a78ad77eed7943f719aac9` (기존 설치) |
| KiCad 번들 python | 3.11.5, `C:/Users/gh/AppData/Local/Programs/KiCad/10.0/bin/python.exe` sha256 `3d4273ea…aac31` · pcbnew 10.0.8 |
| 설치 크기 | node_modules 117M · .venv 237M · dist 1.3M |

clone 폴더의 `git status`에는 변경이 없다. dist, node_modules, .venv, windows-mcp-config.json은 원 저장소 .gitignore 대상이다.

## 설치 단계와 종료 코드

| # | 명령 | 종료 코드 | 비고 |
|---|---|---|---|
| 1 | `git clone --branch stable https://github.com/mixelpixx/KiCAD-MCP-Server.git C:/Users/gh/tools/kicad-mcp-server` | 0 | |
| 2 | `npm install --no-fund --no-audit` | 0 | 250 packages |
| 3 | `npm run build` (`tsc`) | 0 | `dist/index.js` 생성 |
| 4 | `<KiCad>/bin/python.exe -m venv --system-site-packages C:/Users/gh/tools/kicad-mcp-server/.venv` | 0 | KiCad 번들 python 기반이고 pcbnew는 시스템 사이트에서 읽는다 |
| 5 | `.venv/Scripts/python.exe -m pip install -r requirements.txt` | 0 | venv 안에만 설치하고 KiCad 번들 python에는 아무것도 넣지 않았다 |
| 6 | `.venv/Scripts/python.exe -c "import pcbnew,kipy,sexpdata,skip,fitz,colorlog,pydantic,dotenv"` | 0 | pcbnew 10.0.8 · kipy는 venv |
| 7 | setup-windows.ps1 사본 `-ClientType manual` (아래 「뺀 줄」) | 0 (4회째) | 1~3회는 종료 코드 1이었다. 원인은 아래 「실패 기록」 |

venv에만 설치된 패키지(`pip freeze --local` 주요 항목)는 다음과 같다.
- kicad-python 0.9.2 (kipy), kicad-skip 0.2.5, sexpdata 1.0.2
- pymupdf 2.2, CairoSVG 2.9.1, colorlog 6.12.0, pydantic 2.14.4, python-dotenv 1.2.4
- protobuf 5.29.6, pynng 0.9.0

나머지 의존성은 pip가 함께 설치했다. pillow와 requests는 KiCad 번들 python에 이미 있는 판을 그대로 쓴다.

## setup-windows.ps1 — 읽은 결과와 뺀 줄

원본 512줄을 모두 읽었다. **PATH나 전역 설정(레지스트리, 환경 변수 영구 설정, Claude Desktop·Cline 설정 파일 쓰기)을 바꾸는 줄은 없다.**
- 8단계는 설정 예시를 clone 폴더 안의 `windows-mcp-config.json`에 쓰고 경로를 안내만 한다.
- 9단계는 그 프로세스 안에서만 `$env:`를 설정하고, 서버를 2초간 띄웠다가 종료한다.

뺀 줄과 바꾼 줄은 다음과 같다(사본 `setup-windows-noglobal-bom.ps1` sha256 `76fcb6da…71bbe`, scratchpad).

| 원본 줄 | 내용 | 처리 | 이유 |
|---|---|---|---|
| 292–315 | Step 6: `& $kicad.PythonExe -m pip install -r requirements.txt` | **뺌** | KiCad 번들 python에 패키지를 설치하는 것은 사용자 홈 격리가 아니다. 대신 venv(위 4·5단계)를 썼다 |
| 73 | `$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path` | 절대 경로 `"C:/Users/gh/tools/kicad-mcp-server"`로 바꿈 | 사본이 scratchpad에 있어 기준 경로가 달라지기 때문 |
| (파일 앞) | UTF-8 BOM 추가 | 추가 | Windows PowerShell 5.1이 박스 문자를 cp949로 읽지 않게 하려고 |

사본 실행 결과: KiCad 10.0 [OK], pcbnew 10.0.8 [OK], Node v24.22.2 [OK], Project Build [OK], Configuration Generated [OK], Server started (PID 102192) → 종료, 종료 코드 0. 「Python Dependencies [ERROR]」는 Step 6을 뺐기 때문에 나오는 표시이고, 판정 조건에는 들어가지 않는다.

### 실패 기록 (setup 사본)

| 회 | 종료 코드 | 원인 (근거) | 고친 것 |
|---|---|---|---|
| 1 | 1 | `-SkipBuild`를 주면 `ProjectBuilt=false`가 돼 성공 판정 조건을 채우지 못한다(스크립트 488–491줄) | `-SkipBuild`를 뺐다 |
| 2 | 1 | 「Build completed but dist/index.js not found」. sed 치환에서 `\U`·`\t`가 대소문자 변환과 탭으로 해석돼 73줄이 `"C:SERSGH	OOLS…"`로 깨졌다 | 줄을 다시 썼다 |
| 3 | 1 | 같은 원인. Python heredoc 안의 `\U` 이스케이프로 줄을 고치는 데 실패해 사본이 그대로였다 | 앞으로 슬래시 경로로 다시 썼다 |
| 4 | 0 | — | — |

2·3회째에는 `Push-Location`이 실패해 npm install·build가 현재 폴더(clone 폴더)에서 돌았다. clone 밖에 생긴 파일은 없다.

## MCP 설정 (env)

`claude mcp add`와 `pcb-kicad2.mcp.json`에 같은 command·args·env를 넣었다.

| 키 | 값 | 이유 |
|---|---|---|
| command | `C:/tools/node-v24.22.2-win-x64/node.exe` | pcb 칸의 PATH에 기대지 않으려고 절대 경로를 썼다 |
| args | `C:/Users/gh/tools/kicad-mcp-server/dist/index.js` | |
| KICAD_PYTHON | `C:/Users/gh/tools/kicad-mcp-server/.venv/Scripts/python.exe` | 서버는 `<root>/.venv`를 먼저 찾는다(src/server.ts 128–137). 명시해 두면 의도가 분명하다 |
| PYTHONPATH | `C:/Users/gh/AppData/Local/Programs/KiCad/10.0/bin/Lib/site-packages` | pcbnew.py 위치. setup 스크립트가 만든 값과 같다 |
| KICAD_BACKEND | `auto` | IPC를 먼저 쓰고, 안 되면 SWIG로 대체한다 (python/kicad_api/factory.py) |
| KICAD_AUTO_LAUNCH | `false` | 서버가 KiCad GUI를 스스로 띄우지 않게 한다. pcb 칸이 단일 작성자다 |
| NODE_ENV · LOG_LEVEL | `production` · `info` | setup 스크립트 기본값 |
| PYTHONIOENCODING | `utf-8` | 기존 pcb.mcp.json과 같다 |
| PYTHONUTF8 | `1` | 이 값이 없으면 전역 `fp-lib-table`(한글 설명)을 cp949로 읽다가 실패해 **풋프린트 라이브러리 0개**가 된다(로그 「'cp949' codec can't decode byte 0xeb」). 넣은 뒤에는 155개를 불러온다 |

회로도 쓰기 보호: 서버 기본값이 `KICAD_ALLOW_OPEN_SCHEMATIC_EDITS=false`이다. 그래서 KiCad에 열려 있는 회로도를 디스크에서 고치는 것은 거부된다. 기존 iQreu의 `KICAD_MCP_ENABLE_SCH_EDIT=0`에 해당하므로 따로 설정하지 않았다.

## 등록 (`claude mcp add --scope local`)

```
cd C:/workspace_python/OpenHW
claude mcp add --scope local kicad -e KICAD_PYTHON=… -e PYTHONPATH=… -e KICAD_BACKEND=auto -e KICAD_AUTO_LAUNCH=false -e NODE_ENV=production -e LOG_LEVEL=info -e PYTHONIOENCODING=utf-8 -e PYTHONUTF8=1 -- C:/tools/node-v24.22.2-win-x64/node.exe C:/Users/gh/tools/kicad-mcp-server/dist/index.js
→ Added stdio MCP server kicad … to local config / File modified: C:\Users\gh\.claude.json [project: C:/workspace_python/OpenHW]   (종료 코드 0)

cd C:/workspace_python/OpenHW/.harness-worktrees/t-20261126-171922-251f
claude mcp add --scope local kicad … (같은 인자)
→ MCP server kicad already exists in local config   (종료 코드 1)
```

- **pcb worktree는 main 경로와 같은 local 항목을 쓴다.** `~/.claude.json`의 `projects`에서 `kicad`를 가진 키는 `C:/workspace_python/OpenHW` 하나뿐이다.
- worktree에서도 `claude mcp get kicad`가 같은 항목(Scope: Local config, ✔ Connected)을 보여 준다. 두 번째 add가 1로 끝난 것은 이미 등록돼 있다는 뜻이고 실패가 아니다.
- 등록 전 두 경로 모두 `claude mcp get kicad` 결과는 「No MCP server named "kicad"」였다. 기존에 local로 등록된 kicad는 없었다.

`claude mcp list` 출력(kicad 줄, 두 경로 모두 종료 코드 0):

```
[C:/workspace_python/OpenHW]
kicad: C:/tools/node-v24.22.2-win-x64/node.exe C:/Users/gh/tools/kicad-mcp-server/dist/index.js - ✔ Connected
[C:/workspace_python/OpenHW/.harness-worktrees/t-20261126-171922-251f]
kicad: C:/tools/node-v24.22.2-win-x64/node.exe C:/Users/gh/tools/kicad-mcp-server/dist/index.js - ✔ Connected
```

pcb 칸은 `--strict-mcp-config --mcp-config orchestration/roles/pcb.mcp.json`으로 떠 있어 위 local 등록을 읽지 않는다. 그래서 `pcb-kicad2.mcp.json`을 따로 두었다. orch가 pcb 칸을 재시작할 때 `--mcp-config orchestration/roles/pcb-kicad2.mcp.json`으로 바꾼다.

## 시험 — stdio 1회 기동

- 스크립트: scratchpad `r025/stdio_probe.py`
  - `pcb-kicad2.mcp.json`의 `mcpServers.kicad`를 그대로 읽어 실행한다.
  - `initialize` → `notifications/initialized` → `tools/list` 순서로 보낸다.
  - 종료 코드: 0 = 도구 목록을 받음, 1 = 응답이 없거나 오류
- 명령: `python -I stdio_probe.py <lane>/orchestration/roles/pcb-kicad2.mcp.json tools.json`
- 결과: **종료 코드 0**
  - serverInfo `kicad-mcp-server` 2.9.0, protocol 2025-06-18, **도구 250개**, 0.6~0.8초
  - 처음 몇 개: `list_tool_categories`, `get_category_tools`, `search_tools`, `create_project`, `open_project`, `open_board`, `reload_board`, `save_board` …
- 서버 로그 `~/.kicad-mcp/logs/kicad_interface-<pid>.log`:
  - 「Connecting to KiCAD via IPC... Connection refused」 다음 「Successfully imported pcbnew module」, 「KiCAD interface initialized (backend: SWIG)」
  - 「Loaded 155 footprint libraries」, 「Loaded 223 symbol libraries」, 「Warm-up complete: pcbnew 10.0.8」
- IPC 연결 거부는 KiCad가 실행 중이 아니었기 때문이다(tasklist에 kicad.exe·pcbnew.exe 없음).
  - `kicad_common.json`의 `api.enable_server`는 이미 `true`다. R-014 당시에는 false였다.
  - pcb 칸이 KiCad를 열면 IPC로 붙는다. 이 부분은 이번에 시험하지 않았다.
- stdin을 닫은 뒤 10초 안에 스스로 끝나지 않아 프로브가 종료시켰다.
  - 이후 `kicad-mcp-server` 또는 `kicad_interface` 명령줄을 가진 프로세스는 0개였다.
  - setup 9단계의 시험 서버도 남지 않았다.
- 경고 「JLCPCB API credentials not found」는 JLCPCB API 키가 없다는 뜻이다. 키를 넣지 않았고, 계정 가입·로그인 금지 범위이므로 그대로 둔다.

## 분기점 · 선택 · 이유 · 차선책

| 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|
| Python 의존성 위치 | `--system-site-packages` 격리 venv (KiCad 번들 python 기반) | 사용자 홈 격리 지시. KiCad 번들 python을 건드리지 않고도 pcbnew를 쓸 수 있다 | KiCad 번들 python에 requirements를 직접 설치(원 스크립트 Step 6) |
| setup-windows.ps1 실행 | 사본에서 Step 6만 빼고 실행 | 전역 줄은 없었다. 격리를 지키려고 KiCad python pip 설치만 뺐다 | 실행하지 않고 수동 단계만 기록 |
| node 경로 | 절대 경로 | strict-mcp-config 칸의 PATH와 상관없이 같은 실행 파일을 쓰려고 | `node`(PATH) |
| PYTHONUTF8 | `1` 추가 | 이 값이 없으면 풋프린트 라이브러리 0개(cp949 오류) | 전역 fp-lib-table 설명을 ASCII로 수정(KiCad 설정 변경이 필요해 택하지 않음) |
| 백엔드 | `auto` | IPC 실시간을 먼저 쓰고, KiCad가 없으면 SWIG로 대체 | `ipc` 고정(KiCad가 없으면 실패) |
| pcb worktree 등록 | main 경로 항목을 공유(두 번째 add는 already exists) | Claude Code가 worktree의 local 항목을 main 저장소 키로 묶는다 | `~/.claude.json`을 직접 고쳐 worktree 키를 추가(전역 파일 수작업이라 택하지 않음) |
| pcb-kicad2.mcp.json 서버 구성 | `kicad` 하나 | 기존 pcb.mcp.json에 kicad 하나뿐이다(보충 지시) | — |

## 되돌리기

- local 등록: main 경로에서 `claude mcp remove kicad -s local`.
- 설치: `C:/Users/gh/tools/kicad-mcp-server` 폴더를 지우면 된다. 생기는 것은 venv, node_modules, dist가 전부다.
- 로그·데이터: 서버가 `~/.kicad-mcp/`(logs, data/jlcpcb_parts.db)를 만든다.
