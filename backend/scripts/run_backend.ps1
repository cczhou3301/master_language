# 启动 backend（不依赖 Activate.ps1）
# 在 backend 目录执行: .\scripts\run_backend.ps1
$here = Split-Path $PSScriptRoot -Parent
Set-Location $here

$py = Join-Path $here ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$env:PYTHONPATH = $here
& $py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
