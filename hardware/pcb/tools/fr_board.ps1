# P-003 Freerouting finish for low-speed nets (O-51/O-54). Run in an hc terminal (O-48), not a Claude background shell.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File hardware/pcb/tools/fr_board.ps1 <carrier|front> [maxPasses]
# Steps: lock fixed sets + export DSN -> Freerouting (headless) -> import SES + refill zones -> sync project -> DRC
param([string]$Board, [int]$Passes = 30, [string]$Lock = "")
$root = (Resolve-Path "$PSScriptRoot\..\..\..").Path
Set-Location $root
$kpy = "C:\Users\gh\AppData\Local\Programs\KiCad\10.0\bin\python.exe"
$cli = "C:\Users\gh\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe"
$java = "C:\Users\gh\tools\freerouting\download\jre25\jdk-25.0.5+8-jre\bin\java.exe"
$jar = "C:\Users\gh\tools\freerouting\download\freerouting-2.5.0.jar"
$work = Join-Path $root "hardware\pcb\route"
$pcb = "hardware\schematic\$Board\$Board.kicad_pcb"
$dsn = "$work\$Board.dsn"
$ses = "$work\$Board.ses"
"== $Board export $(Get-Date -Format 'HH:mm:ss')"
& $kpy hardware/pcb/tools/freeroute.py export $pcb $dsn "$work\$Board-fixed.txt" $Lock 2>&1 | Where-Object { $_ -match '^DSN' }
"== $Board freerouting $(Get-Date -Format 'HH:mm:ss')"
if (Test-Path $ses) { Remove-Item $ses -Force -Confirm:$false }
& $java -jar $jar -de $dsn -do $ses -mp $Passes -mt 8 --gui.enabled=false *> "$work\$Board-freerouting.log"
"freerouting exit=$LASTEXITCODE ses=$(Test-Path $ses)"
Get-Content "$work\$Board-freerouting.log" | Select-Object -Last 6
if (Test-Path $ses) {
    "== $Board import $(Get-Date -Format 'HH:mm:ss')"
    & $kpy hardware/pcb/tools/freeroute.py import $pcb $ses 2>&1 | Where-Object { $_ -match '^SES' }
    python hardware/pcb/tools/sync_project.py | Out-Null
    & $cli pcb drc --format json --severity-all --schematic-parity --exit-code-violations -o "hardware\pcb\drc\$Board-drc.json" $pcb | Out-Null
    "drc exit=$LASTEXITCODE"
}
"== $Board end $(Get-Date -Format 'HH:mm:ss')"
