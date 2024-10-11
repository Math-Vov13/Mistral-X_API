from fastapi import APIRouter, status, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import jwt

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from src.API import database
from src.API import scheme

from os import environ as env


SECRET_KEY= env.get("SECRET_KEY", "abcd")
ALGORITHM= "HS256"

bcrypt= CryptContext(schemes= ["bcrypt"])

router = APIRouter(prefix= "/token", tags= ["Token"])

async def generate_user_token(id: int, username: str, expires_time: float=100):
    payload = {
        "sub": username,
        "id": id,
        "expires": datetime.now(timezone.utc).timestamp() + (expires_time / 60)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm= ALGORITHM)

async def read_user_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms= ALGORITHM)


@router.post("", include_in_schema= True, status_code=status.HTTP_201_CREATED,
            summary= "",
            description= "")
async def create_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    print(form_data)
    print(bcrypt.hash(form_data.password))
    return {"access_token": await generate_user_token(form_data.username, form_data.client_id), "token_type": "bearer"}