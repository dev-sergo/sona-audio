import json
import os
import tempfile
from datetime import datetime, timezone

import aiosqlite
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from server.config import settings
from server.services.llm_service import summarize_note
from server.services.whisper_service import transcribe

router = APIRouter()


@router.post("/notes")
async def create_note(
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
):
    if file:
        ext = os.path.splitext(file.filename or "audio")[1].lower() or ".ogg"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        try:
            result = await transcribe(tmp_path)
            full_text = result["text"]
        finally:
            os.unlink(tmp_path)
    elif text:
        full_text = text
    else:
        raise HTTPException(
            400,
            detail={"error": "no_input", "message": "Provide 'file' or 'text'"},
        )

    meta = await summarize_note(full_text)
    now = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "INSERT INTO notes (title, summary, full_text, tags, created_at) VALUES (?, ?, ?, ?, ?)",
            (meta.get("title"), meta.get("summary"), full_text, json.dumps(meta.get("tags", [])), now),
        ) as cur:
            note_id = cur.lastrowid
        await db.commit()

    return {
        "id": note_id,
        "title": meta.get("title"),
        "summary": meta.get("summary"),
        "tags": meta.get("tags", []),
        "full_text": full_text,
        "created_at": now,
    }


@router.get("/notes")
async def list_notes(limit: int = 10, offset: int = 0, search: str | None = None):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        if search:
            q = f"%{search}%"
            async with db.execute(
                "SELECT id, title, tags, created_at FROM notes "
                "WHERE title LIKE ? OR full_text LIKE ? "
                "ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (q, q, limit, offset),
            ) as cur:
                rows = await cur.fetchall()
        else:
            async with db.execute(
                "SELECT id, title, tags, created_at FROM notes "
                "ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ) as cur:
                rows = await cur.fetchall()

        async with db.execute("SELECT COUNT(*) FROM notes") as cur:
            total = (await cur.fetchone())[0]

    notes = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d["tags"] or "[]")
        notes.append(d)

    return {"notes": notes, "total": total}


@router.get("/notes/{note_id}")
async def get_note(note_id: int):
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)) as cur:
            row = await cur.fetchone()

    if row is None:
        raise HTTPException(
            404,
            detail={"error": "not_found", "message": f"Note {note_id} not found"},
        )

    d = dict(row)
    d["tags"] = json.loads(d["tags"] or "[]")
    return d


@router.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        await db.commit()
    return {"deleted": note_id}
