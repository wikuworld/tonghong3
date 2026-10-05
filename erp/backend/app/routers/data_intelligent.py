"""Unduh dan unggah peta relasi master Data Intelligent."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.auth import require_roles
from app.services.data_intelligent import apply_web, apply_workbook, export_workbook, gap_page, summary, workspace

router = APIRouter(prefix="/masters/data-intelligent", tags=["data-intelligent"])


@router.get("/summary")
def data_intelligent_summary(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("marketing")),
) -> dict:
    return {"counts": summary(db)}


@router.get("/workspace")
def data_intelligent_workspace(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("marketing")),
) -> dict:
    return workspace(db)


@router.get("/gaps")
def data_intelligent_gaps(
    sheet: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    q: str = Query(""),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("marketing")),
) -> dict:
    try:
        return gap_page(db, sheet, page=page, page_size=page_size, q=q)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class WebApplyIn(BaseModel):
    sheets: dict[str, list[dict]] = Field(default_factory=dict)


@router.post("/apply")
def data_intelligent_apply(
    body: WebApplyIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("marketing")),
) -> dict:
    try:
        result = apply_web(db, body.model_dump())
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.get("/export")
def data_intelligent_export(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("marketing")),
) -> Response:
    data = export_workbook(db)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="data_intelligent.xlsx"'},
    )


@router.post("/import")
async def data_intelligent_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("marketing")),
) -> dict:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="File kosong")
    try:
        result = apply_workbook(db, raw)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return result
