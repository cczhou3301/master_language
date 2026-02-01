# Backend scripts

## gen_dto_from_idl.py

Generate Pydantic DTO classes from IDL (proto-generated *_pb2 modules; run repo IDL generation first if needed). **Do not hand-edit DTOs**; regenerate after proto/IDL changes. APIRouters now live in `app.core.router`.

- **Run** (from `backend` dir): `python scripts/gen_dto_from_idl.py`
- **Requires**: Backend venv with `protobuf` and `pydantic` (same as app).
- **Output**: `app/dto/{auth,user,video}_dto.py` and `app/dto/__init__.py` — one file per idl module, Pydantic `BaseModel` classes mirroring proto messages.

## gen_models_from_db.py

Generate SQLAlchemy models from the current database (introspection). **Do not hand-write model classes**; regenerate after schema changes. Each run **overwrites** generated model files, so RDS/schema changes are reflected when you re-run the script.

- **Run** (from `backend` dir): `python scripts/gen_models_from_db.py`
- **Requires**: `pip install sqlacodegen pymysql`; DB must be reachable (sync URL from `DATABASE_URL`).
- **Output**: `app/models/{table_name}.py` — **one file per table**, filename = table name (e.g. `users.py`, `videos.py`, `user_vocabulary.py`).
- **Uses**: `app.models.base` for `Base`; `app.utils.id_generator` for `generate_bigint_id`.
- **Legacy**: Removes old hand-written model files (e.g. `user.py`, `content.py`) that are not table-named.

## init_db.py

Create all tables (dev only; use Alembic in production). Run from backend: `python scripts/init_db.py` (or set `PYTHONPATH`).
