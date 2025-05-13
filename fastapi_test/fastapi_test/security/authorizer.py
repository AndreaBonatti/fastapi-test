from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from fastapi_test.fastapi_test.security.auth_utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    return payload["sub"]
