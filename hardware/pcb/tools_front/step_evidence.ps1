# G-002 step evidence from the SAVED board (orch: window capture only for status-bar numbers).
# Usage: powershell -File step_evidence.ps1 <carrier|front> <step-name>
# Writes <G-002>/<step>-top.png, -bottom.png (kicad-cli pcb render) and <step>-copper.svg (F.Cu,In1,In2,B.Cu,Edge.Cuts)
param([string]$Board, [string]$Step)
$root = (Resolve-Path "$PSScriptRoot\..\..\..").Path
$cli = "C:\Users\gh\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"
$pcb = Join-Path $root "hardware\schematic\$Board\$Board.kicad_pcb"
$out = "C:\workspace_python\OpenHW\validation\runtime\kicad-gui\G-002"
New-Item -ItemType Directory -Force $out | Out-Null
& $cli pcb render --side top --quality basic -w 1600 -h 2000 -o "$out\$Step-top.png" $pcb | Out-Null
"render top exit=$LASTEXITCODE"
& $cli pcb render --side bottom --quality basic -w 1600 -h 2000 -o "$out\$Step-bottom.png" $pcb | Out-Null
"render bottom exit=$LASTEXITCODE"
& $cli pcb export svg --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,Edge.Cuts" --mode-single --page-size-mode 2 -o "$out\$Step-copper.svg" $pcb | Out-Null
"svg exit=$LASTEXITCODE"
