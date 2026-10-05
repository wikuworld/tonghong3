from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, String, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from mrp_api.db import Base


class MrpUser(Base):
    __tablename__ = "mrp_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="operator")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    department: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class MrpRolePermission(Base):
    __tablename__ = "mrp_role_permissions"
    __table_args__ = (
        UniqueConstraint("role", "module_key", "action", name="uq_mrp_role_permissions_key"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(32))
    module_key: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(32))
    allowed: Mapped[bool] = mapped_column(Boolean, default=True)
