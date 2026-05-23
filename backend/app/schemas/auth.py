from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr

UserRole = Literal["admin", "analyst", "viewer"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = "viewer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole


class TokenPayload(BaseModel):
    sub: str  # user id
    exp: int
