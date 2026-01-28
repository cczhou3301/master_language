# 在任意目录执行: cd c:\data\code\cursor\master_language\backend; .\scripts\install_deps.ps1
$backend = Split-Path $PSScriptRoot -Parent
Set-Location $backend

# 使用 PATH 中的 python（先 activate .venv 可装到 venv：.\.venv\Scripts\Activate.ps1）
Write-Host "Installing from requirements.txt ..."
python -m pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) { Write-Host "Done." } else { Write-Host "Install failed. Run: pip install -r requirements.txt" }
