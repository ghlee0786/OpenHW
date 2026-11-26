# P-003 보드 한 장을 처음부터: 규칙 동기화 → 넷리스트·배치 → 형상 내보내기 → 스크립트 배선 → 적용·GND 면 → DRC
# 사용: powershell -File run_board.ps1 <carrier|front> [pairs]   (pairs = 차동 쌍만, 디버그)
param([string]$Board, [string]$Mode = "")
$ErrorActionPreference = "Continue"
$root = (Resolve-Path "$PSScriptRoot\..\..\..").Path
Set-Location $root
$kpy = "C:\Users\gh\AppData\Local\Programs\KiCad\10.0\bin\python.exe"
$cli = "C:\Users\gh\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"
$work = Join-Path $root "hardware\pcb\route"
New-Item -ItemType Directory -Force $work | Out-Null
$pcb = "hardware\schematic\$Board\$Board.kicad_pcb"
python hardware/pcb/tools/sync_project.py | Out-Null
# O-74b 실크 사본: 1) 종류별(선폭 · 자기 패드 둘레 · 극성) → 배치 → 2) 그 보드에 하나뿐인 종류의 자리별(외곽 · 이웃 패드) → 다시 배치
& $kpy hardware/pcb/tools/silk_lib.py $Board 2>$null | Select-Object -Last 1
& $kpy hardware/pcb/tools/build_boards.py $Board 2>&1 | Where-Object { $_ -match "^$Board" }
& $kpy hardware/pcb/tools/silk_lib.py $Board $pcb 2>$null | Select-Object -Last 1
& $kpy hardware/pcb/tools/build_boards.py $Board 2>&1 | Where-Object { $_ -match "^$Board" }
& $kpy hardware/pcb/tools/silk.py $pcb "$work\$Board-silk-refs.json" refs 2>$null | Select-Object -Last 1
python hardware/pcb/tools/sync_project.py | Out-Null
& $kpy hardware/pcb/tools/route_export.py $pcb "$work\$Board-geom.json" 2>&1 | Where-Object { $_ -match '^pads' }
python -u hardware/pcb/tools/route.py "$work\$Board-geom.json" $Board "$work\$Board-routes.json" $Mode 2>&1 | Tee-Object "$work\$Board-route.log"
& $kpy hardware/pcb/tools/route_apply.py $pcb "$work\$Board-routes.json" 2>&1 | Select-Object -Last 1
# V-005 RQ-10~13 실크 정리(선폭 0.15 · 개구 0.15 · 외곽 0.30 · 참조 지정자 실크 · 극성 표시)
& $kpy hardware/pcb/tools/silk.py $pcb "$work\$Board-silk.json" check 2>$null | Select-Object -Last 1
# 보드 저장이 .kicad_pro 를 템플릿 넷클래스로 덮어쓰므로 다시 동기화 (O-30: .kicad_pro 는 pcb 소유)
python hardware/pcb/tools/sync_project.py | Out-Null
& $cli pcb drc --format json --severity-all --schematic-parity --exit-code-violations -o "hardware\pcb\drc\$Board-drc.json" $pcb | Out-Null
"drc exit=$LASTEXITCODE"
