# IDL (API contract)

This folder is the **single source of truth** for backend–frontend communication:

| What            | Where        | Role |
|-----------------|-------------|------|
| **Message shapes** | `*.proto`   | Request/response DTOs (Protocol Buffers) |
| **HTTP URLs**      | `api.yaml`  | REST endpoints: method + path → request/response message |

- **Proto** = *what* is sent (fields and types).
- **api.yaml** = *where* it is sent (method + path and which message names).

Backend implements the routes; frontend uses these definitions to call the API. For gRPC you would declare `service` and `rpc` in proto instead of REST + api.yaml.

## Layout

| File         | Contents |
|--------------|----------|
| `auth.proto` | ActivationStep1/2, LoginRequest/Response, DeviceInfo, DeviceLimitError |
| `user.proto` | UserProfile, LearningStats |
| `video.proto`| VideoCard, SubtitleLine, VideoDetail |
| `api.yaml`   | REST: method, path, request/response message names |

## Generate code

### Option 1: Scripts (repo root)

Scripts live in the **repo root** folder `scripts/`:

| Script           | Path (from repo root) | Purpose              |
|------------------|------------------------|----------------------|
| `gen_idl.ps1`    | `scripts/gen_idl.ps1`  | Generate Python IDL (Windows) |
| `gen_idl.sh`     | `scripts/gen_idl.sh`  | Generate Python IDL (Linux/macOS) |

**Run from repo root** (the directory that contains `idl/`, `backend/`, `scripts/`):

**Backend (Python)** – requires `pip install grpcio-tools` in backend venv:

```powershell
# Windows (PowerShell, from repo root)
.\scripts\gen_idl.ps1
```

```bash
# Linux/macOS (from repo root)
./scripts/gen_idl.sh
```

- **Python output**: `backend/app/idl/{proto_name}_pb2.py` — one file per proto, same base name as the proto (e.g. `auth.proto` → `auth_pb2.py`).
- **APIRouter** is declared in `backend/app/idl/router.py`: `auth_router`, `user_router`, `video_router`. Handlers are registered in `app.api.*`.
- Backend schemas can mirror proto messages; use generated classes with `google.protobuf.json_format` if desired.

**Frontend (TypeScript)** – install a protoc plugin (e.g. `ts-proto`) and run protoc or buf (see Option 2).

### Option 2: Buf (one command)

1. Install [buf](https://buf.build/docs/installation).
2. From repo root: `buf generate`
3. Edit `buf.gen.yaml` to add a TypeScript plugin (e.g. `ts-proto`) and set `out: frontend/src/idl`.

### Frontend TS (manual)

```bash
# Example with ts-proto (in frontend dir)
npm i -D ts-proto
npx protoc -I ../idl --ts_proto_out=src/idl ../idl/*.proto --ts_proto_opt=esModuleInterop=true
```

Generated types go in `frontend/src/idl/`. Use them for API request/response typing.
