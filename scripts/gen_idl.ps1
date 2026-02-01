# Generate Python IDL from idl/*.proto. Run from repo root.
# Requires: pip install grpcio-tools (in backend venv).
# Output: backend/app/idl/{proto_name}_pb2.py (one file per proto, same base name as proto).

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$IdlDir = Join-Path $RepoRoot "idl"
$OutDir = Join-Path $RepoRoot "backend" "app" "idl"

if (-not (Test-Path $IdlDir)) {
    Write-Error "idl folder not found: $IdlDir"
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Protos = Get-ChildItem -Path $IdlDir -Filter "*.proto"
if ($Protos.Count -eq 0) {
    Write-Error "No .proto files in idl/"
}

# Use Python's grpc_tools.protoc (pip install grpcio-tools)
$Python = "python"
$Protoc = & $Python -c "import grpc_tools.protoc; print(grpc_tools.protoc.__file__)" 2>$null
if (-not $Protoc) {
    Write-Error "grpcio-tools not installed. Run: pip install grpcio-tools"
}

Push-Location $RepoRoot
try {
    & $Python -m grpc_tools.protoc `
        -I"$IdlDir" `
        --python_out="$RepoRoot/backend/app" `
        ($Protos.FullName)
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    # Move *_pb2.py into backend/app/idl/ (one file per proto, same name as proto)
    $AppDir = Join-Path $RepoRoot "backend" "app"
    Get-ChildItem -Path $AppDir -Filter "*_pb2.py" | ForEach-Object {
        Move-Item -Path $_.FullName -Destination (Join-Path $OutDir $_.Name) -Force
        Write-Host "Generated: backend/app/idl/$($_.Name)"
    }
} finally {
    Pop-Location
}
