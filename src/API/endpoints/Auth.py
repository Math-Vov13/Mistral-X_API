from fastapi import APIRouter, status, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import jwt

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from os import environ as env
from src.Core.config import CONFIG

load_dotenv()


SECRET_KEY= env.get("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
bcrypt= CryptContext(schemes= ["bcrypt"], deprecated="auto")

router = APIRouter(prefix= "/token", tags= ["Token"])


async def generate_user_token(id: int, username: str, expires_time: float=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES):
    payload = {
        "sub": username,
        "id": id,
        "expires": (datetime.now().utcnow() + timedelta(minutes= expires_time)).timestamp()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm= CONFIG.ALGORITHM)

async def read_user_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms= CONFIG.ALGORITHM)


@router.post("", include_in_schema= True, status_code=status.HTTP_201_CREATED,
            summary= "",
            description= "")
async def create_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    print(form_data)
    print(bcrypt.hash(form_data.password))
    return {"access_token": await generate_user_token(form_data.username, form_data.client_id), "token_type": "bearer"}