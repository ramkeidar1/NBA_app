from fastapi import APIRouter, HTTPException, Request, Response, status

from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.cache.supabase import get_supabase
from app.schemas.auth import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_COOKIE_OPTS: dict = {
    "httponly": True,
    "samesite": "lax",
    "secure": False,  # set True behind HTTPS in production
    "max_age": 60 * 60 * 24 * 7,  # 7 days in seconds
    "path": "/auth/refresh",
}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: LoginRequest) -> UserOut:
    client = get_supabase()
    existing = client.table("users").select("id").eq("email", body.email).execute()
    if existing.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed = hash_password(body.password)
    result = (
        client.table("users")
        .insert({"email": body.email, "hashed_password": hashed})
        .execute()
    )
    row = result.data[0]
    return UserOut(id=row["id"], email=row["email"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response) -> TokenResponse:
    client = get_supabase()
    result = client.table("users").select("id, email, hashed_password").eq("email", body.email).execute()

    if not result.data or not verify_password(body.password, result.data[0]["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = result.data[0]
    access_token = create_access_token(user["id"])
    refresh_token = create_refresh_token(user["id"])

    response.set_cookie(value=refresh_token, key=_REFRESH_COOKIE, **_COOKIE_OPTS)
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request) -> TokenResponse:
    token = request.cookies.get(_REFRESH_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        payload = decode_refresh_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    return TokenResponse(access_token=create_access_token(payload.sub))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(key=_REFRESH_COOKIE, path="/auth/refresh")
