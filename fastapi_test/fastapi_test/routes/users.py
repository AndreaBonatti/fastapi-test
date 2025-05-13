import os

from fastapi import APIRouter
from pymongo import MongoClient

router = APIRouter()

client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
db = client['notes']
collection = db['users']