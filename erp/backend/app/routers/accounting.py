from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import AccountingMapping
from app.paging import apply_sort, page_dict, parse_page_params
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    AccountingMappingCreate,
    AccountingMappingUpdate,
    AccountingMappingOut,
    AccountingMappingResolveOut,
)

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/mappings")
def list_mappings(
    transaction_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|transaction_type|status|coa_code|coa_name"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "desc",
    )
    stmt = select(AccountingMapping).where(AccountingMapping.is_active.is_(True))
    count_stmt = select(func.count(AccountingMapping.id)).where(AccountingMapping.is_active.is_(True))
    if transaction_type:
        stmt = stmt.where(AccountingMapping.transaction_type == transaction_type)
        count_stmt = count_stmt.where(AccountingMapping.transaction_type == transaction_type)
    if status:
        stmt = stmt.where(AccountingMapping.status == status)
        count_stmt = count_stmt.where(AccountingMapping.status == status)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": AccountingMapping.id,
            "transaction_type": AccountingMapping.transaction_type,
            "status": AccountingMapping.status,
            "coa_code": AccountingMapping.coa_code,
            "coa_name": AccountingMapping.coa_name,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(AccountingMapping.id.desc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.post("/mappings", response_model=AccountingMappingOut)
def create_mapping(
    body: AccountingMappingCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "finance")),
):
    row = AccountingMapping(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/mappings/{mapping_id}", response_model=AccountingMappingOut)
def update_mapping(
    mapping_id: int,
    body: AccountingMappingUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "finance")),
):
    row = db.get(AccountingMapping, mapping_id)
    if not row:
        raise HTTPException(404, "Mapping not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/mappings/{mapping_id}")
def delete_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "finance")),
):
    row = db.get(AccountingMapping, mapping_id)
    if not row:
        raise HTTPException(404, "Mapping not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}


@router.get("/mappings/resolve", response_model=AccountingMappingResolveOut)
def resolve_mapping(
    transaction_type: str = Query(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    stmt = select(AccountingMapping).where(
        AccountingMapping.is_active.is_(True),
        AccountingMapping.transaction_type == transaction_type,
    )
    if status:
        stmt = stmt.where(AccountingMapping.status == status)
    row = db.scalars(stmt).first()
    if row:
        return AccountingMappingResolveOut(
            coa_code=row.coa_code,
            coa_name=row.coa_name,
            found=True,
        )
    return AccountingMappingResolveOut(found=False)
