"""Kurs USD/IDR — input EXIM, effective date (CR §3.8)."""

from __future__ import annotations

from typing import Optional

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ExchangeRate
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["exchange-rates"])


class ExchangeRateIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    idr_per_usd: Decimal
    effective_date: date
    notes: Optional[str] = None
    created_by: Optional[str] = None


class ExchangeRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    idr_per_usd: Decimal
    effective_date: date
    notes: Optional[str] = None
    created_by: Optional[str] = None


@router.get("/exchange-rates", response_model=list[ExchangeRateOut])
def list_rates(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[ExchangeRate]:
    return list(
        db.scalars(select(ExchangeRate).order_by(ExchangeRate.effective_date.desc())).all()
    )


@router.post("/exchange-rates", response_model=ExchangeRateOut)
def create_rate(
    body: ExchangeRateIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "exim", "finance", "marketing")),
) -> ExchangeRate:
    row = ExchangeRate(
        idr_per_usd=body.idr_per_usd,
        effective_date=body.effective_date,
        notes=body.notes,
        created_by=body.created_by or "exim",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/exchange-rates/latest", response_model=ExchangeRateOut)
def latest_rate(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ExchangeRate:
    row = db.scalars(
        select(ExchangeRate).order_by(ExchangeRate.effective_date.desc()).limit(1)
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Belum ada kurs")
    return row
