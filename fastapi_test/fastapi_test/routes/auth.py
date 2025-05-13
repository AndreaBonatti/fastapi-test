import os

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient

from fastapi_test.fastapi_test.security.auth_utils import create_access_token, create_refresh_token, decode_token
from fastapi_test.fastapi_test.security.hash_encoder import encode, matches

router = APIRouter()

client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
db = client['notes']
users = db['users']


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserRegisterResponse(BaseModel):
    message: str
    user: dict


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserLoginResponse(BaseModel):
    message: str
    data: TokenData


@router.post("/auth/register", response_model=UserRegisterResponse)
def register(request: UserRegisterRequest):
    existing_user = users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered!")

    hashed_password = encode(request.password)

    result = users.insert_one({
        "email": request.email,
        "password": hashed_password
    })

    inserted_user = users.find_one({'_id': result.inserted_id})
    if inserted_user:
        return {
            "message": "User registered successfully!",
            "user": {
                "id": str(inserted_user["_id"]),
                "email": inserted_user["email"]
            }
        }
    else:
        raise HTTPException(status_code=500, detail="Impossible register the user!")


@router.post("/auth/login", response_model=UserLoginResponse)
async def login(request: LoginRequest):
    existing_user = users.find_one({"email": request.email})
    if not existing_user or not matches(request.password, existing_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials!")

    user_id = str(existing_user["_id"])
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    return {
        "message": "User login successfully!",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }


@router.post("/auth/refresh")
async def refresh(request: Request):
    data = await request.json()
    token = data.get("refresh_token")

    if not token:
        raise HTTPException(status_code=400, detail="Refresh token missing")

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload.get("sub")
    new_access_token = create_access_token({"sub": user_id})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
