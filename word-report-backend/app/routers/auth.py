from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib
import secrets

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


MOCK_USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password": "admin123",
        "nickname": "管理员"
    }
}


def generate_token(username: str) -> str:
    random_str = secrets.token_hex(16)
    timestamp = str(int(datetime.now().timestamp()))
    raw_token = f"{username}:{timestamp}:{random_str}"
    return f"wr_{hashlib.sha256(raw_token.encode()).hexdigest()[:48]}"


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = MOCK_USERS.get(request.username)
    
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = generate_token(request.username)
    
    return LoginResponse(
        token=token,
        user={
            "id": user["id"],
            "username": user["username"],
            "nickname": user["nickname"]
        }
    )


@router.post("/logout")
async def logout():
    return {"message": "退出成功"}


@router.get("/me")
async def get_current_user():
    return {
        "id": 1,
        "username": "admin",
        "nickname": "管理员"
    }