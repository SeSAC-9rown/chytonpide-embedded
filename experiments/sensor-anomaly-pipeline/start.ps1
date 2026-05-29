param(
    [int]$Limit = 240,
    [double]$Interval = 0.001,
    [switch]$NoFaultInjection,
    [switch]$KeepDatabase
)

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
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

Write-Host "[1/8] Stopping old local app processes..."
Stop-ProjectProcess "*consumer.main*"
Stop-ProjectProcess "*api.main*"
Stop-ProjectProcess "*vite*"

Write-Host "[2/8] Ensuring Python virtual environment..."
if (!(Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -r requirements.txt | Out-Host

Write-Host "[3/8] Preparing public sensor dataset..."
$datasetArgs = @("scripts\download_public_dataset.py", "--limit", "5000")
if (!$NoFaultInjection) {
    $datasetArgs += "--inject-demo-faults"
}
.\.venv\Scripts\python.exe @datasetArgs | Out-Host

Write-Host "[4/8] Training Isolation Forest model..."
.\.venv\Scripts\python.exe scripts\train_isolation_forest.py | Out-Host

Write-Host "[5/8] Starting Kafka and Kafka UI..."
docker compose up -d | Out-Host

if (!$KeepDatabase) {
    Write-Host "[6/8] Resetting SQLite database..."
    Remove-Item -LiteralPath "data\sensor_anomaly.db" -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "[6/8] Keeping existing SQLite database..."
}

Write-Host "[7/8] Starting consumer, API, and dashboard..."
Start-Process -FilePath ".\.venv\Scripts\python.exe" `
    -ArgumentList @("-m", "consumer.main") `
    -WorkingDirectory $Root `
    -RedirectStandardOutput "consumer-dev.out.log" `
    -RedirectStandardError "consumer-dev.err.log" `
    -WindowStyle Hidden

Start-Sleep -Seconds 10

.\.venv\Scripts\python.exe -m producer.simulator --limit $Limit --interval $Interval *> producer-dev.log
Start-Sleep -Seconds 5

Start-Process -FilePath ".\.venv\Scripts\python.exe" `
    -ArgumentList @("-m", "api.main") `
    -WorkingDirectory $Root `
    -RedirectStandardOutput "api-dev.out.log" `
    -RedirectStandardError "api-dev.err.log" `
    -WindowStyle Hidden

Start-Process -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory (Join-Path $Root "dashboard") `
    -RedirectStandardOutput (Join-Path $Root "dashboard-dev.out.log") `
    -RedirectStandardError (Join-Path $Root "dashboard-dev.err.log") `
    -WindowStyle Hidden

Write-Host "[8/8] Verifying services..."
Start-Sleep -Seconds 6

$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
$dashboardRequest = [System.Net.HttpWebRequest]::Create("http://localhost:5173")
$dashboardResponse = $dashboardRequest.GetResponse()
$dashboardStatus = $dashboardResponse.StatusCode.value__
$dashboardResponse.Close()

$summary = .\.venv\Scripts\python.exe -c "from collections import Counter; from common.config import settings; from common.storage import SensorStorage; s=SensorStorage(settings.database_path); a=s.get_recent_anomalies(1000); print({'readings': len(s.get_recent_readings(1000)), 'anomalies': len(a), 'types': dict(Counter(x['anomaly_type'] for x in a))})"

Write-Host ""
Write-Host "Started sensor anomaly pipeline."
Write-Host "API health: $($health.status)"
Write-Host "Dashboard status: $dashboardStatus"
Write-Host "Data summary: $summary"
Write-Host ""
Write-Host "Dashboard: http://localhost:5173"
Write-Host "FastAPI:    http://localhost:8000/docs"
Write-Host "Kafka UI:   http://localhost:8080"
Write-Host ""
Write-Host "Stop with:  .\stop.ps1"

