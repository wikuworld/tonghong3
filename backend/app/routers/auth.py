from fastapi import APIRouter

from app.schemas import LoginIn, TokenOut

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenOut)
def login(_body: LoginIn) -> TokenOut:
    """Stub auth — ganti dengan JWT nyata jika perlu."""
    return TokenOut(access_token="dev-token")


@router.post("/auth/logout")
def logout() -> dict[str, str]:
    return {"status": "ok"}
