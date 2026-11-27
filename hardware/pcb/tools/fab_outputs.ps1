# P-004 manufacturing outputs (R-010 checklist, review docs/review/vd001-format.md section 3). Run in an hc terminal after both boards pass DRC.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File hardware/pcb/tools/fab_outputs.ps1 [-Boards carrier,front]
#   -Boards: boards to regenerate (default both). A board left out is only read for its KiCad BOM csv (temp folder, no repo file changes).
#   KiCad tools: environment KICAD_BIN (folder with kicad-cli.exe and python.exe), default %LOCALAPPDATA%\Programs\KiCad\10.0\bin
# Writes manufacturing/pcb/<board>/ (gerber + drill, top/bottom pos, pcbway bom, assembly pdf, step, README.md, SHA256SUMS) and manufacturing/pcb/<board>.zip
# Files only: no upload, no quote, no login.
param([string[]]$Boards = @("carrier", "front"))
$ErrorActionPreference = "Continue"
$root = (Resolve-Path "$PSScriptRoot\..\..\..").Path
Set-Location $root
$bin = if ($env:KICAD_BIN) { $env:KICAD_BIN } else { Join-Path $env:LOCALAPPDATA "Programs\KiCad\10.0\bin" }
$kpy = Join-Path $bin "python.exe"
$cli = Join-Path $bin "kicad-cli.exe"
$fab = Join-Path $root "manufacturing\pcb"
$tmp = Join-Path $env:TEMP "openhw-fab-bom"
New-Item -ItemType Directory -Force $fab, $tmp | Out-Null
$layers = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
foreach ($b in "carrier", "front") {
    if ($Boards -notcontains $b) {
        & $cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP}' --labels 'Refs,Value,Footprint,Qty,DNP' --group-by 'Value,Footprint,${DNP}' --ref-range-delimiter '""' -o "$tmp\$b-kicad-bom.csv" "hardware\schematic\$b\$b.kicad_sch" | Out-Null
        "== $b (bom csv only) exit=$LASTEXITCODE"
        continue
    }
    $pcb = "hardware\schematic\$b\$b.kicad_pcb"
    $out = Join-Path $fab $b
    if (Test-Path $out) { Remove-Item -Recurse -Force $out }
    New-Item -ItemType Directory -Force "$out\gerber" | Out-Null
    "== $b"
    & $kpy hardware/pcb/tools/fab.py $pcb $out $b 2>$null | Select-Object -Last 1
    python hardware/pcb/tools/sync_project.py | Out-Null
    & $cli pcb drc --format json --severity-all --schematic-parity --exit-code-violations -o "hardware\pcb\drc\$b-drc.json" $pcb | Out-Null
    "drc exit=$LASTEXITCODE"
    & $cli pcb export gerbers --layers $layers --no-x2 --no-protel-ext --precision 6 --use-drill-file-origin -o "$out\gerber" $pcb | Out-Null
    "gerbers exit=$LASTEXITCODE"
    & $cli pcb export drill --format excellon --excellon-units mm --excellon-zeros-format decimal --excellon-separate-th --drill-origin plot --generate-map --map-format pdf -o "$out\gerber" $pcb | Out-Null
    "drill exit=$LASTEXITCODE"
    & $cli pcb export pdf --layers "F.Fab,Edge.Cuts" --sp --cdnp --mode-single -o "$out\$b-assembly-top.pdf" $pcb | Out-Null
    & $cli pcb export pdf --layers "B.Fab,Edge.Cuts" --sp --cdnp --mirror --mode-single -o "$out\$b-assembly-bottom.pdf" $pcb | Out-Null
    "assembly pdf exit=$LASTEXITCODE"
    & $cli pcb export step --user-origin "100x100mm" --subst-models -f -o "hardware\pcb\step\$b.step" $pcb 2>&1 | Select-String -Pattern "model|Model" | Select-Object -First 5
    "step exit=$LASTEXITCODE"
    Copy-Item "hardware\pcb\step\$b.step" "$out\$b.step"
    & $cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP}' --labels 'Refs,Value,Footprint,Qty,DNP' --group-by 'Value,Footprint,${DNP}' --ref-range-delimiter '""' -o "$tmp\$b-kicad-bom.csv" "hardware\schematic\$b\$b.kicad_sch" | Out-Null
    "kicad bom exit=$LASTEXITCODE"
}
# PCBWay BOM: research R-011 generator and bom-full.csv from main (read-only copies in TEMP, not committed here)
cmd /c "git show main:manufacturing/bom/make_pcbway_bom.py > `"$tmp\make_pcbway_bom.py`""
cmd /c "git show main:manufacturing/bom/inputs/bom-full.csv > `"$tmp\bom-full.csv`""
python -I "$tmp\make_pcbway_bom.py" --bom-full "$tmp\bom-full.csv" --kicad-carrier "$tmp\carrier-kicad-bom.csv" --kicad-front "$tmp\front-kicad-bom.csv" --out $tmp
"pcbway bom exit=$LASTEXITCODE"
foreach ($b in $Boards) {
    $out = Join-Path $fab $b
    Copy-Item "$tmp\$b-pcbway.csv" "$out\$b-pcbway.csv"
    Copy-Item "hardware\pcb\fab-readme-$b.md" "$out\README.md"
    $zip = Join-Path $fab "$b.zip"
    if (Test-Path $zip) { Remove-Item -Force $zip }
    Compress-Archive -Path "$out\*" -DestinationPath $zip
    "zip $b exit=$?"
    "{0}  {1}" -f (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower(), "$b.zip" | Set-Content -Encoding ascii "$out\SHA256SUMS"
}
"== end"
