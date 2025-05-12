import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
from pymongo import MongoClient

router = APIRouter()

client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
db = client['notes']
collection = db['notes']


class NoteRequest(BaseModel):
    title: str
    content: str
    color: int
    id: Optional[str] = None
    ownerId: str


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    color: int
    createdAt: datetime


@router.post("/notes")
async def insert(request: NoteRequest) -> NoteResponse:
    record = {
        "title": request.title,
        "content": request.content,
        "color": request.color,
        "ownerId": request.ownerId,
        "createdAt": datetime.now(timezone.utc)
    }
    result = collection.insert_one(record)
    inserted_note = collection.find_one({'_id': result.inserted_id})

    return NoteResponse(
        id=str(inserted_note['_id']),
        title=inserted_note['title'],
        content=inserted_note['content'],
        color=inserted_note['color'],
        createdAt=inserted_note['createdAt']
    )
