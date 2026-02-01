# MasterLanguage

Immersive English learning via **Intensive Reading of Video** (视频精读).  
Backend (Python/FastAPI) and Frontend (React) are **separate**.  
**Config switch:** `APP_ENV=development` | `production`.  
**HA & fault tolerance:** health checks, rate limiting, connection pooling, graceful shutdown.

**部署开发环境：** 请直接查看下方的 **[Quick Start (develop environment)](#quick-start-develop-environment)**，按步骤即可在本地跑起后端与前端。

---

## Quick Start (develop environment)

Follow these steps to run the app locally for development.

### 1. Prerequisites

| Requirement | Version / Notes |
|-------------|-----------------|
| Python | 3.11+ |
| Node.js | 18+ (for frontend) |
| MySQL | 8 (local or Docker) |
| Redis | 6+ (local or Docker) |

### 2. Clone and backend setup

```bash
git clone <repo-url>
cd master_language/backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
pip install sqlacodegen pymysql   # for gen_models_from_db.py (optional)
```

### 3. Environment and database

- Copy env and edit `DATABASE_URL` and `REDIS_URL` to point to your MySQL and Redis:

```bash
cp .env.example .env
# Edit .env: DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/dbname?charset=utf8mb4
#            REDIS_URL=redis://localhost:6379/0
```

- Create the MySQL database (if it does not exist):

```sql
CREATE DATABASE IF NOT EXISTS master_language CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

- Create tables (from current SQLAlchemy models):

```bash
# From backend dir (MySQL and Redis must be running)
python scripts/init_db.py
```

- **Optional:** Sync models and DDL from an existing DB (generates `app/models/*.py` and `scripts/ddl/*.sql`):

```bash
python scripts/gen_models_from_db.py
```

### 4. Start backend

```bash
# From backend dir, with .venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health/ready  

### 5. Frontend setup and run

```bash
cd ../frontend
npm install
npm run dev
```

- App: http://localhost:5173  
- Ensure `VITE_API_BASE` (or `.env.development`) points to `http://localhost:8000` for API calls.

### 6. Optional: dev data

- **Activation code** (for registration): insert an unused code, e.g.  
  `INSERT INTO activation_code (id, code, status) VALUES (1, 'DEV001', 'unused');`  
  (use your DB’s id type; see `app.models.activation_code`.)
- **Admin user:** set `ADMIN_USER_IDS=1` in `.env` and ensure user id `1` exists (or add your user id).

### 7. Run tests (backend)

```bash
cd backend
# TESTING=1 is set by conftest.py for pytest
pytest tests/ -v
```

---

## Stack

| Layer   | Tech |
|---------|------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async MySQL), Redis |
| Frontend| React 18, Vite, TypeScript, React Router |
| DB      | MySQL 8 |
| Cache   | Redis 7 |

---

## Config: Dev ↔ Production

### Backend (`backend/.env` or env vars)

| Variable | Development | Production |
|----------|-------------|------------|
| `APP_ENV` | `development` | `production` |
| `DEBUG` | `true` | `false` |
| `DATABASE_URL` | `mysql+aiomysql://...@localhost:3306/...` | Your MySQL URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Your Redis URL |
| `JWT_SECRET_KEY` | dev placeholder | **Strong secret, 32+ chars** |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Your frontend origins |

Copy `backend/.env.example` to `backend/.env` and edit.

### Frontend

| Variable | Development | Production |
|----------|-------------|------------|
| `VITE_API_BASE` | `http://localhost:8000` | `https://api.masterlanguage.com` |

- `.env.development` / `.env.production` or build-time env.
- `frontend/.env.example` documents the switch.

---

## Run

For a full **step-by-step dev setup** (prerequisites, DB, Redis, backend, frontend), see [Quick Start (develop environment)](#quick-start-develop-environment) above.

### 1. With Docker Compose (recommended)

```bash
# Start MySQL, Redis, Backend, Frontend
docker compose up -d

# First time: create DB tables (run once)
docker compose run --rm backend python scripts/init_db.py

# Optional: add a dev activation code for testing registration
# docker compose exec db mysql -u master_language -pmaster_language master_language -e "INSERT INTO activation_code (code, status) VALUES ('DEV001', 'unused');"
```

- Backend: http://localhost:8000  
- Frontend: http://localhost:5173  
- API docs (dev only): http://localhost:8000/docs  

### 2. Local (without Docker)

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # or: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # edit DATABASE_URL, REDIS_URL
# Create DB and tables (MySQL + Redis must be running)
PYTHONPATH=. python scripts/init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**

```bash
cd frontend
npm install
# .env.development has VITE_API_BASE=http://localhost:8000
npm run dev
```

---

## HA & Fault Tolerance

- **`/health/live`** — liveness (process up).
- **`/health/ready`** — readiness (DB + Redis). Use in K8s/load balancer to stop sending traffic when dependencies are down.
- **DB:** `pool_pre_ping`, `pool_recycle`, connection pooling.
- **Redis:** used for rate limiting and sessions; app starts even if Redis is down; `/health/ready` reports it.
- **Rate limiting:** PRD §6.2 (activation, login, video, general). 429 with clear messages.
- **Graceful shutdown:** lifespan closes Redis on exit.

---

## PRD Coverage (summary)

- **Auth:** Activation (invite-only, burn code), Login, 3‑device limit with explicit “Device limit reached” modal.
- **Video feed:** Cards (thumbnail, title, difficulty, duration, completion), filters (difficulty, accent, topic).
- **Video detail:** Placeholder player; subtitle list for intensive reading (full player + loop/Cloze/Shadowing in future).
- **Rate limits:** Activation, Login (IP/UID), Video (IP/UID), General API; blocks and 429 as per PRD.

---

## Project layout

```
master_language/
├── backend/
│   ├── app/
│   │   ├── api/        # auth, videos, users
│   │   ├── config/     # settings (dev/prod)
│   │   ├── core/       # db, security, rate_limit
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   ├── scripts/
│   │   ├── ddl/              # DDL per table (from gen_models_from_db.py)
│   │   ├── init_db.py
│   │   └── gen_models_from_db.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/      # Login, Feed, VideoPage
│   │   ├── lib/        # auth helpers
│   │   └── config.ts   # API_BASE from VITE_API_BASE
│   ├── .env.development
│   ├── .env.production
│   └── Dockerfile
├── docker-compose.yml
├── Product Requirements.md
└── README.md
```

---

## IDE: "Import pydantic could not be resolved"

Pylance/Pyright can’t resolve `pydantic` until it’s installed and the right interpreter is selected.

1. **Install deps in the backend venv:**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
2. **In Cursor/VS Code:** `Ctrl+Shift+P` → “Python: Select Interpreter” → choose `backend\.venv\Scripts\python.exe` (or `backend/.venv/bin/python` on Mac/Linux).

`pyrightconfig.json` and `.vscode/settings.json` point the tools at `backend/.venv` once it exists.

---

## Production deploy (outline)

1. Set `APP_ENV=production`, `DEBUG=false`, strong `JWT_SECRET_KEY`, real `DATABASE_URL` and `REDIS_URL`.
2. Run DB migrations (Alembic) instead of `init_db`; reserve `init_db` for dev.
3. Build frontend: `VITE_API_BASE=https://api.masterlanguage.com npm run build`; serve `dist/` with Nginx or CDN.
4. Run backend with multiple workers: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`.
5. Put a load balancer in front; use `/health/ready` for readiness and `/health/live` for liveness.
