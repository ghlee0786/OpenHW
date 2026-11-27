# G-002: screenshot of the already open pcbnew window (no key input). Usage: powershell -File win_shot.ps1 <out.png>
param([string]$Out)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class WS { [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
public struct R { public int L, T, Ri, B; } }
"@
$p = Get-Process pcbnew -ErrorAction Stop | Where-Object { $_.MainWindowTitle -match "PCB" } | Select-Object -First 1
$h = $p.MainWindowHandle
[WS]::ShowWindow($h, 3) | Out-Null
[WS]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 800
$r = New-Object WS+R
[WS]::GetWindowRect($h, [ref]$r) | Out-Null
$bmp = New-Object Drawing.Bitmap ($r.Ri - $r.L), ($r.B - $r.T)
[Drawing.Graphics]::FromImage($bmp).CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null
$bmp.Save($Out)
"saved $Out ($($p.MainWindowTitle))"
