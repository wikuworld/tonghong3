from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import AccountingMapping
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    AccountingMappingCreate,
    AccountingMappingUpdate,
    AccountingMappingOut,
    AccountingMappingResolveOut,
)

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/mappings", response_model=list[AccountingMappingOut])
def list_mappings(
    transaction_type: str = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(AccountingMapping).filter(AccountingMapping.is_active.is_(True))
    if transaction_type:
        query = query.filter(AccountingMapping.transaction_type == transaction_type)
    if status:
        query = query.filter(AccountingMapping.status == status)
    return query.order_by(AccountingMapping.id.desc()).all()


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
    row = db.query(AccountingMapping).get(mapping_id)
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
    row = db.query(AccountingMapping).get(mapping_id)
    if not row:
        raise HTTPException(404, "Mapping not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}


@router.get("/mappings/resolve", response_model=AccountingMappingResolveOut)
def resolve_mapping(
    transaction_type: str = Query(...),
    status: str = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(AccountingMapping).filter(
        AccountingMapping.is_active.is_(True),
        AccountingMapping.transaction_type == transaction_type,
    )
    if status:
        query = query.filter(AccountingMapping.status == status)
    row = query.first()
    if row:
        return AccountingMappingResolveOut(
            coa_code=row.coa_code,
            coa_name=row.coa_name,
            found=True,
        )
    return AccountingMappingResolveOut(found=False)
