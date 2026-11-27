# P-003: route both boards (O-48: run as a normal program in an hc terminal, not a Claude background shell)
# Usage: hc run --bg --name openhw-pcb-route --cwd <lane> -- powershell -NoProfile -ExecutionPolicy Bypass -File hardware/pcb/tools/run_all.ps1
# Per board: hardware/pcb/route/<board>-full.out, checkpoints hardware/pcb/route/<board>-routes.json.{pairs,signals}.json
$root = (Resolve-Path "$PSScriptRoot\..\..\..").Path
Set-Location $root
foreach ($b in 'front', 'carrier') {
    "== $b start $(Get-Date -Format 'HH:mm:ss')"
    powershell -NoProfile -ExecutionPolicy Bypass -File hardware/pcb/tools/run_board.ps1 $b *> "hardware\pcb\route\$b-full.out"
    Get-Content "hardware\pcb\route\$b-full.out" -Encoding UTF8 | Select-Object -Last 4
    "== $b end $(Get-Date -Format 'HH:mm:ss')"
}
"ALL DONE"
