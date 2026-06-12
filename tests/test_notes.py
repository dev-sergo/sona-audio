import pytest
from unittest.mock import patch, AsyncMock


_FAKE_META = {
    "title": "Track idea",
    "summary": "A short description of the idea.",
    "tags": ["music", "rap"],
}


@pytest.mark.asyncio
async def test_create_note_from_text(client):
    with patch("server.routes.notes.summarize_note", new=AsyncMock(return_value=_FAKE_META)):
        resp = await client.post("/notes", data={"text": "want to record an uptempo rap track"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Track idea"
    assert body["tags"] == ["music", "rap"]
    assert "id" in body


@pytest.mark.asyncio
async def test_list_notes(client):
    with patch("server.routes.notes.summarize_note", new=AsyncMock(return_value=_FAKE_META)):
        await client.post("/notes", data={"text": "first note"})
        await client.post("/notes", data={"text": "second note"})

    resp = await client.get("/notes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 2
    assert isinstance(body["notes"], list)


@pytest.mark.asyncio
async def test_get_note_by_id(client):
    with patch("server.routes.notes.summarize_note", new=AsyncMock(return_value=_FAKE_META)):
        create = await client.post("/notes", data={"text": "note to read back"})
    note_id = create.json()["id"]

    resp = await client.get(f"/notes/{note_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == note_id


@pytest.mark.asyncio
async def test_get_note_not_found(client):
    resp = await client.get("/notes/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_search_notes(client):
    with patch("server.routes.notes.summarize_note", new=AsyncMock(return_value=_FAKE_META)):
        await client.post("/notes", data={"text": "dark trap idea for a beat"})

    resp = await client.get("/notes?search=dark+trap")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_create_note_no_input(client):
    resp = await client.post("/notes")
    assert resp.status_code == 400
