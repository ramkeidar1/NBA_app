from pydantic import BaseModel, EmailStr
from uuid import UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    email: EmailStr


class TokenPayload(BaseModel):
    sub: str  # user id
    exp: int
