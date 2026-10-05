from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from mrp_api.config import settings
from mrp_api.db import SessionLocal, get_db
from mrp_api.models import MrpUser
from mrp_api.schemas import LoginIn, TokenOut, UserOut
from mrp_api.timeutil import utc_now

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SHOPFLOOR_ROLES = ("operator", "lab", "packing", "gudang", "supervisor", "admin")
DEMO_USERS = (
    ("operator", "operator", "produksi"),
    ("packing", "packing", "packing"),
)


def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)


def verify_password(pw: str, pw_hash: str) -> bool:
    try:
        return pwd_context.verify(pw, pw_hash)
    except Exception:
        return False


def _jwt_secret() -> str:
    return settings.mrp_jwt_secret or settings.jwt_secret


def _create_access_token(sub: str, role: str) -> str:
    exp = utc_now() + timedelta(minutes=int(settings.jwt_exp_minutes))
    payload = {
        "sub": sub,
        "role": role,
        "exp": exp,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=settings.jwt_algorithm)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> MrpUser:
    try:
        payload = jwt.decode(
            token,
            _jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token tidak valid")
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token tidak valid") from e
    user = db.scalars(select(MrpUser).where(MrpUser.username == str(username))).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User tidak aktif")
    return user


def require_roles(*roles: str):
    allowed = {r.strip() for r in roles if r and str(r).strip()}

    def _dep(user: MrpUser = Depends(get_current_user)) -> MrpUser:
        if user.role == "admin":
            return user
        if allowed and user.role not in allowed:
            raise HTTPException(status_code=403, detail="Akses ditolak (role)")
        return user

    return _dep


def ensure_seed_users() -> None:
    db = SessionLocal()
    try:
        existing = {u.username for u in db.scalars(select(MrpUser)).all()}
        if settings.admin_username not in existing:
            db.add(
                MrpUser(
                    username=settings.admin_username,
                    password_hash=hash_password(settings.admin_password),
                    role="admin",
                    is_active=True,
                    department="MRP",
                )
            )
        for username, role, department in DEMO_USERS:
            if username in existing:
                continue
            db.add(
                MrpUser(
                    username=username,
                    password_hash=hash_password(settings.demo_users_password),
                    role=role,
                    is_active=True,
                    department=department,
                )
            )
        db.commit()
    finally:
        db.close()


@router.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    ensure_seed_users()
    username = (body.username or "").strip()
    password = body.password or ""
    if not username or not password:
        raise HTTPException(status_code=400, detail="username & password wajib")
    user = db.scalars(select(MrpUser).where(MrpUser.username == username)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Login gagal")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Login gagal")
    return TokenOut(access_token=_create_access_token(user.username, user.role))


@router.post("/auth/logout")
def logout() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/auth/me", response_model=UserOut)
def me(user: MrpUser = Depends(get_current_user)) -> MrpUser:
    return user


@router.get("/auth/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _user: MrpUser = Depends(require_roles("admin", "supervisor")),
) -> list[MrpUser]:
    return list(db.scalars(select(MrpUser).order_by(MrpUser.username)).all())
