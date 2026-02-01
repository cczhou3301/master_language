"""
Generate SQLAlchemy models from the current database (introspection).
Run from backend dir: python scripts/gen_models_from_db.py
Requires: pip install sqlacodegen pymysql. DB must be reachable (sync URL).
Output:
  - app/models/{table_name}.py — one file per table, filename = table name.
  - scripts/ddl/{table_name}.sql — DDL (SHOW CREATE TABLE) for each whitelisted table, for quick start.
Uses app.models.base for Base; app.utils.id_generator for generate_bigint_id.
Only tables in TABLE_WHITELIST are generated; if TABLE_WHITELIST is empty, all tables are generated.
Generated files are overwritten each run, so re-run after RDS/schema changes to sync models.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Tables to generate model files for. If non-empty, only these tables are generated.
# If empty, all tables from DB introspection are generated.
TABLE_WHITELIST: set[str] = {
    "user",
    "activation_code",
    "user_device",
    "video",
    "subtitle_line",
    "user_vocabulary",
    "user_sentence",
}


def get_sync_url() -> str:
    from app.config import get_settings

    url = get_settings().DATABASE_URL
    if "aiomysql" in url:
        return url.replace("mysql+aiomysql://", "mysql+pymysql://", 1)
    return url


def _debug_print_url(url: str) -> None:
    """Print URL with password masked. Use from main() when DEBUG=1 or in debugger."""
    import re as re_mod

    masked = re_mod.sub(r"(:[^:@]+)(@)", r":****\2", url) if "@" in url else url
    print("DEBUG get_sync_url:", masked)


def main() -> int:
    import os

    out_dir = BACKEND / "app" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    sync_url = get_sync_url()
    if os.environ.get("DEBUG"):
        _debug_print_url(sync_url)
    combined_file = out_dir / "_combined.py"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sqlacodegen",
            "--outfile",
            str(combined_file),
            sync_url,
        ],
        cwd=str(BACKEND),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return 1

    text = combined_file.read_text(encoding="utf-8")

    # Remove sqlacodegen's Base and top-level boilerplate
    text = re.sub(r"^# coding:.*\n", "", text)
    text = re.sub(r"^Base = declarative_base\(\)\n", "", text, count=1)
    text = re.sub(r"^metadata = Base\.metadata\n\n?", "", text, count=1)
    text = re.sub(r"^class Base\([^)]*\):\s*\n\s*pass\s*\n\n?", "", text, count=1)
    text = re.sub(r"^from sqlalchemy\.orm import declarative_base\n", "", text, count=1)
    text = re.sub(
        r"from sqlalchemy\.orm import (.*?)declarative_base,?\s*",
        r"from sqlalchemy.orm import \1",
        text,
    )
    text = re.sub(r'^"""[\s\S]*?"""\s*\n\n', "", text, count=1)
    text = re.sub(r"^from __future__ import annotations\s*\n", "", text, count=1)
    while re.match(r"^(from |import )", text.lstrip()):
        text = re.sub(r"^[^\n]+\n", "", text.lstrip(), count=1)
    text = text.lstrip()

    # Split into class blocks: class ClassName(Base): ... (until next class or EOF)
    class_blocks = list(
        re.finditer(r"class (\w+)\(Base\):.*?(?=\nclass |\Z)", text, re.DOTALL)
    )
    table_class_pairs: list[tuple[str, str]] = []  # (table_name, class_name)

    for m in class_blocks:
        decl = m.group(0)
        class_name = m.group(1)
        tb = re.search(r'__tablename__\s*=\s*["\']([^"\']+)["\']', decl)
        table_name = tb.group(1) if tb else class_name.lower()

        if TABLE_WHITELIST and table_name not in TABLE_WHITELIST:
            continue

        # id primary key -> BIGINT(unsigned=True), default=generate_bigint_id
        decl = re.sub(
            r"(\s+)id: Mapped\[int\] = mapped_column\(Integer, primary_key=True\)",
            r"\1id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, default=generate_bigint_id)",
            decl,
        )
        # *_id FK columns -> BIGINT(unsigned=True)
        decl = re.sub(
            r"(\s+)(\w+_id): Mapped\[int\] = mapped_column\(Integer,",
            r"\1\2: Mapped[int] = mapped_column(BIGINT(unsigned=True),",
            decl,
        )
        decl = re.sub(
            r"(\s+)(\w+_id): Mapped\[int \| None\] = mapped_column\(Integer,",
            r"\1\2: Mapped[int | None] = mapped_column(BIGINT(unsigned=True),",
            decl,
        )

        # Add type: ignore for relationship lines (forward-ref model names)
        def add_relationship_ignore(m: re.Match) -> str:
            line = m.group(0).rstrip()
            if "# type: ignore" not in line:
                line += "  # type: ignore[name-defined]"
            return line + "\n"
        decl = re.sub(r"^\s+\w+: Mapped\[[^\]]+\] = relationship\([^)]+\)\s*$", add_relationship_ignore, decl, flags=re.MULTILINE)

        # Per-file header: include all symbols sqlacodegen may emit (Index, ForeignKeyConstraint, text, datetime, DATETIME, TINYINT, Optional)
        header = f'''"""
Model: {table_name}. Generated by scripts/gen_models_from_db.py. Do not edit by hand.
Regenerate: python scripts/gen_models_from_db.py
"""
from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, ForeignKeyConstraint, Index, Integer, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.id_generator import generate_bigint_id
from .base import Base

'''
        footer = f'\n\n__all__ = ["{class_name}"]\n'
        file_content = header + decl.rstrip() + footer

        out_file = out_dir / f"{table_name}.py"
        out_file.write_text(file_content, encoding="utf-8")
        table_class_pairs.append((table_name, class_name))
        print(f"Written {out_file.name}")

    combined_file.unlink(missing_ok=True)

    # Remove legacy hand-written model files that are not table-named (e.g. user.py, content.py)
    generated_tables = {t for t, _ in table_class_pairs}
    keep = {"base", "__init__"} | generated_tables
    for f in out_dir.glob("*.py"):
        if f.stem not in keep:
            f.unlink()
            print(f"Removed legacy {f.name}")

    # Write or update __init__.py to export all model classes from table-named modules
    _write_models_init(out_dir, table_class_pairs)

    # Dump DDL for whitelisted tables into scripts/ddl/{table_name}.sql (quick start)
    if table_class_pairs:
        table_names = [t for t, _ in table_class_pairs]
        _dump_ddl_for_tables(sync_url, table_names)

    return 0


DDL_OUT_DIR = BACKEND / "scripts" / "ddl"


def _dump_ddl_for_tables(sync_url: str, table_names: list[str]) -> None:
    """Dump SHOW CREATE TABLE for each table into scripts/ddl/{table_name}.sql."""
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        print("Skip DDL dump: sqlalchemy not available for sync engine.", file=sys.stderr)
        return
    DDL_OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(sync_url)
    for table_name in table_names:
        if not re.match(r"^[a-zA-Z0-9_]+$", table_name):
            continue
        try:
            with engine.connect() as conn:
                r = conn.execute(text(f"SHOW CREATE TABLE `{table_name}`"))
                row = r.fetchone()
                if not row:
                    continue
                # SHOW CREATE TABLE returns (Table, Create Table, ...); index 1 is the DDL
                create_sql = row[1] if len(row) > 1 else str(row)
            header = f"-- DDL for table `{table_name}` (from DB via gen_models_from_db.py). Quick start.\n"
            header += "-- Regenerate: python scripts/gen_models_from_db.py\n\n"
            content = header + create_sql.rstrip() + "\n"
            out_file = DDL_OUT_DIR / f"{table_name}.sql"
            out_file.write_text(content, encoding="utf-8")
            print(f"Written {out_file}")
        except Exception as e:
            print(f"Skip DDL for {table_name}: {e}", file=sys.stderr)
    engine.dispose()


def _write_models_init(out_dir: Path, table_class_pairs: list[tuple[str, str]]) -> None:
    """Update app/models/__init__.py to import from each table-named module."""
    lines = [
        '"""Models: generated from DB by scripts/gen_models_from_db.py. One file per table."""',
        "from __future__ import annotations",
        "",
        "from app.utils.id_generator import generate_bigint_id",
        "from .base import Base",
        "",
    ]
    exports = ["Base", "generate_bigint_id"]

    for table_name, class_name in table_class_pairs:
        lines.append(f"from .{table_name} import {class_name}")
        exports.append(class_name)

    lines.append("")
    lines.append("__all__ = [")
    for e in exports:
        lines.append(f'    "{e}",')
    lines.append("]")

    init_file = out_dir / "__init__.py"
    init_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated {init_file}")


if __name__ == "__main__":
    sys.exit(main())
