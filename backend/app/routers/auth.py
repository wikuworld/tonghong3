from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.timeutil import app_now, utc_now
from app.db import SessionLocal, get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserCreate, UserOut, UserUpdate

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)


def verify_password(pw: str, pw_hash: str) -> bool:
    try:
        return pwd_context.verify(pw, pw_hash)
    except Exception:
        return False


def _create_access_token(sub: str, role: str) -> str:
    exp = utc_now() + timedelta(minutes=int(settings.jwt_exp_minutes))
    payload = {"sub": sub, "role": role, "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token tidak valid")
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token tidak valid") from e
    user = db.scalars(select(User).where(User.username == str(username))).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User tidak aktif")
    return user


def require_roles(*roles: str):
    """Dependency untuk membatasi akses berdasarkan role di JWT/user DB.

    Catatan: role 'admin' selalu diizinkan.
    """

    allowed = {r.strip() for r in roles if r and str(r).strip()}

    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role == "admin":
            return user
        if allowed and user.role not in allowed:
            raise HTTPException(status_code=403, detail="Akses ditolak (role)")
        return user

    return _dep


def ensure_bootstrap_admin() -> None:
    """Buat admin default jika tabel users masih kosong."""
    db = SessionLocal()
    try:
        n = db.scalar(select(func.count()).select_from(User)) or 0
        if n > 0:
            return
        u = User(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
            role="admin",
            is_active=True,
        )
        db.add(u)
        db.commit()
    finally:
        db.close()


@router.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    ensure_bootstrap_admin()
    username = (body.username or "").strip()
    password = body.password or ""
    if not username or not password:
        raise HTTPException(status_code=400, detail="username & password wajib")
    user = db.scalars(select(User).where(User.username == username)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Login gagal")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Login gagal")
    return TokenOut(access_token=_create_access_token(user.username, user.role))


@router.post("/auth/logout")
def logout() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("/auth/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin")),
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id.asc())).all())


@router.post("/auth/users", response_model=UserOut)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin")),
) -> User:
    username = (body.username or "").strip()
    if not username or not body.password:
        raise HTTPException(status_code=400, detail="username & password wajib")
    exists = db.scalars(select(User).where(User.username == username)).first()
    if exists:
        raise HTTPException(status_code=400, detail="username sudah ada")
    row = User(
        username=username,
        password_hash=hash_password(body.password),
        role=(body.role or "guest").strip(),
        is_active=bool(body.is_active),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/auth/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin")),
) -> User:
    row = db.get(User, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    if "role" in data:
        row.role = str(data["role"]).strip()
    if "is_active" in data:
        row.is_active = bool(data["is_active"])
    if data.get("password"):
        row.password_hash = hash_password(str(data["password"]))
    row.updated_at = app_now()
    db.commit()
    db.refresh(row)
    return row
