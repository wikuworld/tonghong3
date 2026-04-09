"""Cetak Surat Jalan & INVPL (format marketing Tong Hong: HTML + PDF + Excel INVPL)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.auth import get_current_user
from app.services import marketing_documents as md

router = APIRouter(tags=["documents"])


def _invpl_ctx(db: Session, packing_id: int) -> dict:
    try:
        return md.gather_invpl_rows(db, packing_id)
    except ValueError as e:
        if str(e) == "packing_not_found":
            raise HTTPException(status_code=404, detail="Packing tidak ditemukan") from e
        raise


def _sj_ctx(db: Session, delivery_id: int) -> dict:
    try:
        return md.gather_sj_rows(db, delivery_id)
    except ValueError as e:
        if str(e) == "delivery_not_found":
            raise HTTPException(status_code=404, detail="Delivery tidak ditemukan") from e
        raise


@router.get("/documents/surat-jalan/{delivery_id}/pdf")
def document_surat_jalan_pdf(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    ctx = _sj_ctx(db, delivery_id)
    data = md.render_sj_pdf(ctx)
    fn = f"surat_jalan_{ctx['delivery_number']}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/surat-jalan/{delivery_id}")
def document_surat_jalan(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> HTMLResponse:
    ctx = _sj_ctx(db, delivery_id)
    return HTMLResponse(md.render_sj_html(ctx))


@router.get("/documents/invpl/{packing_id}/xlsx")
def document_invpl_xlsx(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    ctx = _invpl_ctx(db, packing_id)
    data = md.render_invpl_xlsx(ctx)
    fn = f"invpl_{ctx['packing_number']}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/invpl/{packing_id}/pdf")
def document_invpl_pdf(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    ctx = _invpl_ctx(db, packing_id)
    data = md.render_invpl_pdf(ctx)
    fn = f"invpl_{ctx['packing_number']}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/invpl/{packing_id}")
def document_invpl(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> HTMLResponse:
    ctx = _invpl_ctx(db, packing_id)
    return HTMLResponse(md.render_invpl_html(ctx))
