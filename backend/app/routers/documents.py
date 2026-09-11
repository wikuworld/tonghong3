"""Cetak Surat Jalan & INVPL (format marketing Tong Hong: HTML + PDF + Excel INVPL)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.auth import get_current_user, require_roles
from app.schemas import TandaTerimaBatchIn
from app.services import marketing_documents as md
from app.services import proforma_invoice_documents as pi
from app.services import sales_contract_documents as sc
from app.services import tanda_terima_documents as tt
from app.services.audit import log_change

router = APIRouter(tags=["documents"])


def _invpl_ctx(
    db: Session,
    packing_id: int,
    *,
    delivery_id: int | None = None,
    foc: bool = False,
) -> dict:
    try:
        ctx = md.gather_invpl_rows(db, packing_id, delivery_id=delivery_id)
    except ValueError as e:
        if str(e) == "packing_not_found":
            raise HTTPException(status_code=404, detail="Packing tidak ditemukan") from e
        if str(e) == "delivery_not_found":
            raise HTTPException(status_code=404, detail="Delivery tidak ditemukan") from e
        raise
    return md.apply_invpl_foc_title(ctx, foc)


def _invpl_ctx_delivery(db: Session, delivery_id: int, *, foc: bool = False) -> dict:
    try:
        ctx = md.gather_invpl_for_delivery(db, delivery_id)
    except ValueError as e:
        if str(e) == "delivery_not_found":
            raise HTTPException(status_code=404, detail="Delivery tidak ditemukan") from e
        if str(e) == "packing_not_found":
            raise HTTPException(status_code=404, detail="Packing tidak ditemukan") from e
        raise
    return md.apply_invpl_foc_title(ctx, foc)

def _sj_ctx(db: Session, delivery_id: int) -> dict:
    try:
        return md.gather_sj_rows(db, delivery_id)
    except ValueError as e:
        if str(e) == "delivery_not_found":
            raise HTTPException(status_code=404, detail="Delivery tidak ditemukan") from e
        raise


def _commercial_invoice_ctx(db: Session, delivery_id: int) -> dict:
    ok, code = md.commercial_invoice_eligibility(db, delivery_id)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail=md.commercial_invoice_eligibility_message(code),
        )
    try:
        return md.gather_commercial_invoice_ctx(db, delivery_id)
    except ValueError as e:
        if str(e) == "delivery_not_found":
            raise HTTPException(status_code=404, detail="Delivery tidak ditemukan") from e
        if str(e) == "delivery_packing_mismatch":
            raise HTTPException(status_code=400, detail="Delivery tidak cocok dengan packing") from e
        if str(e) == "packing_not_found":
            raise HTTPException(status_code=404, detail="Packing tidak ditemukan") from e
        raise


@router.get("/documents/commercial-invoice/{delivery_id}/pdf")
def document_commercial_invoice_pdf(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    ctx = _commercial_invoice_ctx(db, delivery_id)
    data = md.render_commercial_invoice_pdf(ctx)
    fn = f"commercial_invoice_delivery_{delivery_id}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/commercial-invoice/{delivery_id}")
def document_commercial_invoice(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> HTMLResponse:
    ctx = _commercial_invoice_ctx(db, delivery_id)
    return HTMLResponse(md.render_commercial_invoice_html(ctx))


@router.get("/documents/sales-contract/{po_id}/pdf")
def document_sales_contract_pdf(
    po_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    try:
        ctx = sc.gather_sales_contract_ctx(db, po_id)
    except ValueError as e:
        if str(e) == "po_not_found":
            raise HTTPException(status_code=404, detail="PO tidak ditemukan") from e
        raise
    data = sc.render_sales_contract_pdf(ctx)
    fn = f"sales_contract_{ctx['po_number']}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/sales-contract/{po_id}/docx")
def document_sales_contract_docx(
    po_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    try:
        ctx = sc.gather_sales_contract_ctx(db, po_id)
    except ValueError as e:
        if str(e) == "po_not_found":
            raise HTTPException(status_code=404, detail="PO tidak ditemukan") from e
        raise
    data = sc.render_sales_contract_docx(ctx)
    fn = f"sales_contract_{ctx['po_number']}.docx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


def _proforma_invoice_ctx(db: Session, po_id: int) -> dict:
    try:
        return pi.gather_proforma_invoice_ctx(db, po_id)
    except ValueError as e:
        if str(e) == "po_not_found":
            raise HTTPException(status_code=404, detail="PO tidak ditemukan") from e
        raise


def _proforma_invoice_ctx_multi(
    db: Session,
    po_ids: list[int],
    po_detail_ids: list[int] | None = None,
) -> dict:
    try:
        return pi.gather_proforma_invoice_ctx_multi(db, po_ids, po_detail_ids=po_detail_ids)
    except ValueError as e:
        msg = str(e)
        if msg == "po_not_found":
            raise HTTPException(status_code=404, detail="PO tidak ditemukan") from e
        if msg == "details_not_found":
            raise HTTPException(
                status_code=400,
                detail="Tidak ada baris PO yang cocok dengan pilihan",
            ) from e
        if msg == "customer_mismatch":
            raise HTTPException(
                status_code=400,
                detail="PI multi-SO hanya untuk customer yang sama",
            ) from e
        if msg == "po_ids_required":
            raise HTTPException(status_code=400, detail="Pilih minimal satu SO") from e
        raise


def _parse_batch_po_ids(body: dict) -> list[int]:
    po_ids = body.get("po_ids") if isinstance(body, dict) else None
    if not isinstance(po_ids, list) or not po_ids:
        raise HTTPException(status_code=400, detail="po_ids wajib diisi")
    return [int(x) for x in po_ids]


def _parse_batch_po_detail_ids(body: dict) -> list[int] | None:
    raw = body.get("po_detail_ids") if isinstance(body, dict) else None
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise HTTPException(status_code=400, detail="po_detail_ids harus berupa list")
    out = [int(x) for x in raw if x is not None]
    return out or None


@router.get("/documents/proforma-invoice/{po_id}/pdf")
def document_proforma_invoice_pdf(
    po_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
) -> Response:
    ctx = _proforma_invoice_ctx(db, po_id)
    pi.persist_proforma_invoice_record(db, ctx, actor=getattr(user, "username", None))
    db.commit()
    data = pi.render_proforma_invoice_pdf(ctx)
    safe = str(ctx.get("pi_number") or ctx["po_number"]).replace("/", "-")
    fn = f"proforma_invoice_{safe}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/proforma-invoice/{po_id}/docx")
def document_proforma_invoice_docx(
    po_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
) -> Response:
    ctx = _proforma_invoice_ctx(db, po_id)
    pi.persist_proforma_invoice_record(db, ctx, actor=getattr(user, "username", None))
    db.commit()
    data = pi.render_proforma_invoice_docx(ctx)
    safe = str(ctx.get("pi_number") or ctx["po_number"]).replace("/", "-")
    fn = f"proforma_invoice_{safe}.docx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.post("/documents/proforma-invoice/batch/pdf")
def document_proforma_invoice_batch_pdf(
    body: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Response:
    """Cetak 1 PI dari checklist outstanding. Body: { po_ids, po_detail_ids? }."""
    po_ids = _parse_batch_po_ids(body)
    po_detail_ids = _parse_batch_po_detail_ids(body)
    ctx = _proforma_invoice_ctx_multi(db, po_ids, po_detail_ids=po_detail_ids)
    pi.persist_proforma_invoice_record(db, ctx, actor=getattr(user, "username", None))
    db.commit()
    data = pi.render_proforma_invoice_pdf(ctx)
    safe = str(ctx.get("pi_number") or "batch").replace("/", "-")
    fn = f"proforma_invoice_{safe}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.post("/documents/proforma-invoice/batch/docx")
def document_proforma_invoice_batch_docx(
    body: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Response:
    po_ids = _parse_batch_po_ids(body)
    po_detail_ids = _parse_batch_po_detail_ids(body)
    ctx = _proforma_invoice_ctx_multi(db, po_ids, po_detail_ids=po_detail_ids)
    pi.persist_proforma_invoice_record(db, ctx, actor=getattr(user, "username", None))
    db.commit()
    data = pi.render_proforma_invoice_docx(ctx)
    safe = str(ctx.get("pi_number") or "batch").replace("/", "-")
    fn = f"proforma_invoice_{safe}.docx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


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


@router.get("/documents/surat-jalan/{delivery_id}/dotmatrix")
def document_surat_jalan_dotmatrix(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> HTMLResponse:
    ctx = _sj_ctx(db, delivery_id)
    return HTMLResponse(md.render_sj_dotmatrix_html(ctx))


@router.get("/documents/invpl/{packing_id}/xlsx")
def document_invpl_xlsx(
    packing_id: int,
    foc: bool = Query(False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Response:
    ctx = _invpl_ctx(db, packing_id, foc=foc)
    data = md.render_invpl_xlsx(ctx)
    fn = f"invpl_{ctx['packing_number']}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/invpl/{packing_id}/pdf")
def document_invpl_pdf(
    packing_id: int,
    foc: bool = Query(False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Response:
    ctx = _invpl_ctx(db, packing_id, foc=foc)
    data = md.render_invpl_pdf(ctx)
    fn = f"invpl_{ctx['packing_number']}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/invpl/{packing_id}")
def document_invpl(
    packing_id: int,
    foc: bool = Query(False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> HTMLResponse:
    ctx = _invpl_ctx(db, packing_id, foc=foc)
    return HTMLResponse(md.render_invpl_html(ctx))


@router.get("/documents/invpl-by-delivery/{delivery_id}/xlsx")
def document_invpl_by_delivery_xlsx(
    delivery_id: int,
    foc: bool = Query(False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Response:
    ctx = _invpl_ctx_delivery(db, delivery_id, foc=foc)
    data = md.render_invpl_xlsx(ctx)
    fn = f"invpl_{ctx['packing_number']}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/invpl-by-delivery/{delivery_id}/pdf")
def document_invpl_by_delivery_pdf(
    delivery_id: int,
    foc: bool = Query(False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Response:
    ctx = _invpl_ctx_delivery(db, delivery_id, foc=foc)
    data = md.render_invpl_pdf(ctx)
    fn = f"invpl_{ctx['packing_number']}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/invpl-by-delivery/{delivery_id}")
def document_invpl_by_delivery(
    delivery_id: int,
    foc: bool = Query(False),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> HTMLResponse:
    ctx = _invpl_ctx_delivery(db, delivery_id, foc=foc)
    return HTMLResponse(md.render_invpl_html(ctx))


@router.post("/documents/tanda-terima/batch/html")
def document_tanda_terima_batch_html(
    body: TandaTerimaBatchIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> HTMLResponse:
    ctx = tt.gather_tanda_terima_ctx(
        db,
        body.invoice_ids,
        received_by=body.received_by,
        received_date=body.received_date,
        receipt_no=body.receipt_no,
        stamp_invoices=body.stamp_invoices,
    )
    log_change(
        db,
        entity_type="tanda_terima",
        entity_id=None,
        action="print_html",
        after={"receipt_no": ctx["receipt_no"], "invoice_ids": ctx["invoice_ids"]},
        actor=user.username,
    )
    db.commit()
    return HTMLResponse(tt.render_tanda_terima_html(ctx))


@router.post("/documents/tanda-terima/batch/pdf")
def document_tanda_terima_batch_pdf(
    body: TandaTerimaBatchIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> Response:
    ctx = tt.gather_tanda_terima_ctx(
        db,
        body.invoice_ids,
        received_by=body.received_by,
        received_date=body.received_date,
        receipt_no=body.receipt_no,
        stamp_invoices=body.stamp_invoices,
    )
    log_change(
        db,
        entity_type="tanda_terima",
        entity_id=None,
        action="print_pdf",
        after={"receipt_no": ctx["receipt_no"], "invoice_ids": ctx["invoice_ids"]},
        actor=user.username,
    )
    db.commit()
    data = tt.render_tanda_terima_pdf(ctx)
    safe = str(ctx["receipt_no"]).replace("/", "-")
    fn = f"tanda_terima_{safe}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )
