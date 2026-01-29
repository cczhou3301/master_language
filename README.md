# MasterLanguage

Immersive English learning via **Intensive Reading of Video** (视频精读).  
Backend (Python/FastAPI) and Frontend (React) are **separate**.  
**Config switch:** `APP_ENV=development` | `production`.  
**HA & fault tolerance:** health checks, rate limiting, connection pooling, graceful shutdown.

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

### 1. With Docker Compose (recommended)

```bash
# Start MySQL, Redis, Backend, Frontend
docker compose up -d

# First time: create DB tables (run once)
docker compose run --rm backend python scripts/init_db.py

# Optional: add a dev activation code for testing registration
# docker compose exec db mysql -u master_language -pmaster_language master_language -e "INSERT INTO activation_codes (code, status) VALUES ('DEV001', 'unused');"
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
│   │   └── init_db.py
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
