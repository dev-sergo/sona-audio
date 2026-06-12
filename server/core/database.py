import aiosqlite
from pathlib import Path
from server.config import settings


async def init_db():
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(settings.db_path) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id          TEXT PRIMARY KEY,
                type        TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'pending',
                progress    REAL DEFAULT 0,
                result      TEXT,
                error       TEXT,
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT,
                summary     TEXT,
                full_text   TEXT NOT NULL,
                tags        TEXT,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audio_files (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id      TEXT,
                filename    TEXT NOT NULL,
                path        TEXT NOT NULL,
                size_bytes  INTEGER,
                created_at  TEXT NOT NULL
            );
        """)
        await db.commit()
