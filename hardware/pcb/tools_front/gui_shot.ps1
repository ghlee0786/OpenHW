# P-003 GUI 스크린샷 (G-001 방식): pcbnew로 보드를 열고, 명령줄로 활성 문서가 이 레인인지 확인한 뒤 창만 찍고 닫는다.
# 키 입력은 보내지 않는다. 사용: powershell -File gui_shot.ps1 <board.kicad_pcb> <out.png>
param([string]$Board, [string]$Out)
$ErrorActionPreference = "Stop"
$pb = "C:\Users\gh\AppData\Local\Programs\KiCad\10.0\bin\pcbnew.exe"
$Board = (Resolve-Path $Board).Path
if (Get-Process pcbnew -ErrorAction SilentlyContinue) { throw "pcbnew가 이미 떠 있다 — 단일 작성자 원칙으로 중단" }
$p = Start-Process $pb -ArgumentList "`"$Board`"" -PassThru
for ($i = 0; $i -lt 60 -and -not $p.MainWindowTitle; $i++) { Start-Sleep 1; $p.Refresh() }
Start-Sleep 4; $p.Refresh()
$cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
if ($cmd -notlike "*$Board*") { throw "활성 문서 불일치: $cmd" }
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W2 { [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
public struct R { public int L,T,Ri,B; } }
"@
$h = $p.MainWindowHandle; [W2]::ShowWindow($h, 3) | Out-Null; Start-Sleep 3
$r = New-Object W2+R; [W2]::GetWindowRect($h, [ref]$r) | Out-Null
$bmp = New-Object Drawing.Bitmap ($r.Ri - $r.L), ($r.B - $r.T); $g = [Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size); New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null; $bmp.Save($Out)
"title=$($p.MainWindowTitle) pid=$($p.Id) doc=$Board shot=$Out"
$p.CloseMainWindow() | Out-Null; Start-Sleep 3
if (-not $p.HasExited) { "경고: 창이 닫히지 않음(저장 확인 창일 수 있음) — 키 입력 없이 둔다" }
