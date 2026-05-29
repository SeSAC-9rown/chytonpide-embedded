$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Stop-ProjectProcess {
    param([string]$Pattern)

    Get-CimInstance Win32_Process |
        Where-Object {
            $_.ProcessId -ne $PID -and
            $_.CommandLine -like "*sensor-anomaly-pipeline*" -and
            $_.CommandLine -like $Pattern
        } |
        ForEach-Object {
            Write-Host "Stopping PID $($_.ProcessId): $Pattern"
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

Write-Host "[1/2] Stopping local app processes..."
Stop-ProjectProcess "*consumer.main*"
Stop-ProjectProcess "*api.main*"
Stop-ProjectProcess "*vite*"

Write-Host "[2/2] Stopping Kafka containers..."
docker compose down | Out-Host

Write-Host "Sensor anomaly pipeline stopped."

