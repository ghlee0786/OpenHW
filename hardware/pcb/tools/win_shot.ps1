# G-002: screenshot of the already open pcbnew window (no key input). Usage: powershell -File win_shot.ps1 <out.png>
# Uses PrintWindow(PW_RENDERFULLCONTENT) so it also works when the shell cannot read the screen (CopyFromScreen "handle is invalid").
param([string]$Out)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class WS { [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
[DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
public struct R { public int L, T, Ri, B; } }
"@
$p = Get-Process pcbnew -ErrorAction Stop | Where-Object { $_.MainWindowTitle -match "PCB" } | Select-Object -First 1
$h = $p.MainWindowHandle
[WS]::ShowWindow($h, 3) | Out-Null
Start-Sleep -Milliseconds 800
$r = New-Object WS+R
[WS]::GetWindowRect($h, [ref]$r) | Out-Null
$bmp = New-Object Drawing.Bitmap ($r.Ri - $r.L), ($r.B - $r.T)
$g = [Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$ok = [WS]::PrintWindow($h, $hdc, 2)
$g.ReleaseHdc($hdc)
New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null
$bmp.Save($Out)
"saved $Out ok=$ok ($($p.MainWindowTitle))"
