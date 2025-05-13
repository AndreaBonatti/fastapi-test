import os
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from pymongo import MongoClient

from fastapi_test.fastapi_test.security.authorizer import get_current_user_id

router = APIRouter()

client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
db = client['notes']
notes = db['notes']


class NoteRequest(BaseModel):
    title: str
    content: str
    color: int
    id: Optional[str] = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    color: int
    createdAt: datetime


@router.post("/notes", response_model=NoteResponse)
async def insert_note(request: NoteRequest, owner_id: str = Depends(get_current_user_id)):
    record = {
        "title": request.title,
        "content": request.content,
        "color": request.color,
        "ownerId": owner_id,
        "createdAt": datetime.now(timezone.utc)
    }
    result = notes.insert_one(record)
    inserted_note = notes.find_one({'_id': result.inserted_id})

    return NoteResponse(
        id=str(inserted_note['_id']),
        title=inserted_note['title'],
        content=inserted_note['content'],
        color=inserted_note['color'],
        createdAt=inserted_note['createdAt']
    )


@router.get("/notes", response_model=list[NoteResponse])
async def get_notes_by_owner_id(owner_id: str = Depends(get_current_user_id)):
    result = notes.find({'ownerId': owner_id})
    return [
        NoteResponse(
            id=str(note["_id"]),
            title=note["title"],
            content=note["content"],
            color=note["color"],
            createdAt=note["createdAt"]
        )
        for note in result
    ]


@router.delete("/notes/{note_id}", response_model=dict[str, str])
async def delete_note_by_id(note_id: str, owner_id: str = Depends(get_current_user_id)):
    try:
        object_id = ObjectId(note_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID format!")

    note = notes.find_one({'_id': object_id, 'ownerId': owner_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or access denied!")

    result = notes.delete_one({'_id': object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Deletion failed unexpectedly.")

    return {"message": "Note deleted successfully!"}
