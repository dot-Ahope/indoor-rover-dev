param([string]$Port = "COM5")
# rover_cli.ps1 - F405 UART5 debug console (Windows)
#   powershell -ExecutionPolicy Bypass -File rover_cli.ps1 [COM]
#   board cmds: b <mm/s> both | r <mm/s> right | l <mm/s> left | s stop | c clear-fault
#               e FG count | z reset count | ? help      script: q = quit (sends s)
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
try {
    $sp = [System.IO.Ports.SerialPort]::new($Port, 115200, 'None', 8, 'One')
    $sp.Encoding  = [System.Text.Encoding]::UTF8
    $sp.NewLine   = "`r`n"
    $sp.ReadTimeout = 100
    $sp.Open()
} catch {
    Write-Host "OPEN FAIL ${Port}: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "(port already open in another window? close it first)" -ForegroundColor Yellow
    exit 1
}

function Drain([int]$ms) {
    $out = ''
    $n = [Math]::Max(1, [int]($ms / 100))
    for ($i = 0; $i -lt $n; $i++) { Start-Sleep -Milliseconds 100; try { $out += $sp.ReadExisting() } catch {} }
    if ($out.Length -gt 0) { Write-Host -NoNewline $out }
    return $out.Length
}

Write-Host "$Port 115200 open. type ? for help, q to quit" -ForegroundColor Green
$sp.DiscardInBuffer()
$sp.Write("?`r`n")
$n = Drain 1500
if ($n -eq 0) {
    Write-Host ""
    Write-Host "[warn] board sent 0 bytes - UART5 TX may not be wired to this VCP" -ForegroundColor Yellow
}
while ($true) {
    $line = Read-Host "cli"
    if ($line -eq 'q') { $sp.Write("s`r`n"); Drain 500 | Out-Null; break }
    $sp.Write("$line`r`n")
    $n = Drain 1200
    if ($n -eq 0) { Write-Host "[warn] no response" -ForegroundColor Yellow }
}
$sp.Close()
Write-Host "closed (stop sent)" -ForegroundColor Green
