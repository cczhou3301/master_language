#!/usr/bin/env bash
# Generate Python IDL from idl/*.proto. Run from repo root.
# Requires: pip install grpcio-tools (in backend venv).
# Output: backend/app/idl/{proto_name}_pb2.py (one file per proto, same base name as proto).

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IDL_DIR="$REPO_ROOT/idl"
OUT_DIR="$REPO_ROOT/backend/app/idl"

if [ ! -d "$IDL_DIR" ]; then
  echo "idl folder not found: $IDL_DIR" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

if ! python -c "import grpc_tools.protoc" 2>/dev/null; then
  echo "grpcio-tools not installed. Run: pip install grpcio-tools" >&2
  exit 1
fi

cd "$REPO_ROOT"
python -m grpc_tools.protoc -I"$IDL_DIR" --python_out="$REPO_ROOT/backend/app" "$IDL_DIR"/*.proto
# Move *_pb2.py into backend/app/idl/ (one file per proto, same name as proto)
for f in "$REPO_ROOT/backend/app"/*_pb2.py; do
  [ -f "$f" ] || continue
  mv "$f" "$OUT_DIR/"
  echo "Generated: backend/app/idl/$(basename "$f")"
done
