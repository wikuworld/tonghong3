"""Cetak Surat Jalan & INVPL (HTML untuk browser print)."""

from __future__ import annotations

from html import escape
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Customer, DeliveryDetail, DeliveryHeader, PackingDetail, PackingHeader
from app.routers.auth import get_current_user

router = APIRouter(tags=["documents"])


def _html_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; color: #111; }}
    h1 {{ font-size: 18px; margin-bottom: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; font-size: 13px; }}
    th {{ background: #f4f4f5; }}
    .meta {{ font-size: 13px; margin: 4px 0; }}
    @media print {{ body {{ margin: 12px; }} }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


@router.get("/documents/surat-jalan/{delivery_id}")
def document_surat_jalan(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> HTMLResponse:
    dh = db.get(DeliveryHeader, delivery_id)
    if not dh:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    cust = db.get(Customer, dh.customer_id) if dh.customer_id else None
    details = db.scalars(
        select(DeliveryDetail)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .order_by(DeliveryDetail.id.asc())
    ).all()
    rows_html = ""
    for i, d in enumerate(details, 1):
        rows_html += f"<tr><td>{i}</td><td>{escape(str(d.production_detail_id or ''))}</td>"
        rows_html += f"<td>{escape(str(d.qty or ''))}</td>"
        rows_html += f"<td>{escape(str(d.qty_roll or ''))}</td>"
        rows_html += f"<td>{escape(str(d.qty_pcs or ''))}</td>"
        rows_html += f"<td>{escape(str(d.weight or ''))}</td></tr>"
    body = f"""
<h1>SURAT JALAN</h1>
<p class="meta"><b>No.</b> {escape(dh.delivery_number or str(dh.id))}</p>
<p class="meta"><b>Tanggal</b> {escape(str(dh.delivery_date or ''))}</p>
<p class="meta"><b>Tujuan</b> {escape((dh.destination or '')[:500])}</p>
<p class="meta"><b>Kendaraan</b> {escape(dh.vehicle_number or '')} &nbsp; <b>Supir</b> {escape(dh.driver_name or '')}</p>
<p class="meta"><b>Customer</b> {escape(cust.name if cust else '')}</p>
<table>
  <thead><tr><th>#</th><th>Prod. detail</th><th>Qty</th><th>Roll</th><th>Pcs</th><th>Berat</th></tr></thead>
  <tbody>{rows_html or '<tr><td colspan="6">(belum ada baris)</td></tr>'}</tbody>
</table>
<p class="meta" style="margin-top:24px;">Dibuat dari sistem Tonghong — cetak dari browser (Ctrl+P).</p>
"""
    return HTMLResponse(_html_page("Surat Jalan", body))


@router.get("/documents/surat-jalan/{delivery_id}.xlsx")
def document_surat_jalan_xlsx(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    dh = db.get(DeliveryHeader, delivery_id)
    if not dh:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    cust = db.get(Customer, dh.customer_id) if dh.customer_id else None
    details = db.scalars(
        select(DeliveryDetail)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .order_by(DeliveryDetail.id.asc())
    ).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Surat Jalan"
    ws.append(["No SJ", dh.delivery_number or dh.id])
    ws.append(["Tanggal", str(dh.delivery_date or "")])
    ws.append(["Customer", cust.name if cust else ""])
    ws.append(["Tujuan", dh.destination or ""])
    ws.append([])
    ws.append(["#", "Production detail", "Qty", "Roll", "Pcs", "Berat"])
    for i, d in enumerate(details, 1):
        ws.append([i, d.production_detail_id or "", float(d.qty or 0), d.qty_roll or 0, d.qty_pcs or 0, float(d.weight or 0)])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    fn = f"surat_jalan_{dh.delivery_number or dh.id}.xlsx"
    return Response(
        content=buf.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/surat-jalan/{delivery_id}.pdf")
def document_surat_jalan_pdf(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    dh = db.get(DeliveryHeader, delivery_id)
    if not dh:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    cust = db.get(Customer, dh.customer_id) if dh.customer_id else None
    details = db.scalars(
        select(DeliveryDetail)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .order_by(DeliveryDetail.id.asc())
    ).all()

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 18 * mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(18 * mm, y, "SURAT JALAN")
    y -= 10 * mm
    c.setFont("Helvetica", 10)
    c.drawString(18 * mm, y, f"No: {dh.delivery_number or dh.id}")
    y -= 6 * mm
    c.drawString(18 * mm, y, f"Tanggal: {dh.delivery_date or ''}")
    y -= 6 * mm
    c.drawString(18 * mm, y, f"Customer: {(cust.name if cust else '')}")
    y -= 6 * mm
    c.drawString(18 * mm, y, f"Tujuan: {(dh.destination or '')[:90]}")
    y -= 10 * mm

    c.setFont("Helvetica-Bold", 9)
    c.drawString(18 * mm, y, "#")
    c.drawString(26 * mm, y, "Prod. detail")
    c.drawString(70 * mm, y, "Qty")
    c.drawString(90 * mm, y, "Roll")
    c.drawString(105 * mm, y, "Pcs")
    c.drawString(120 * mm, y, "Berat")
    y -= 5 * mm
    c.setFont("Helvetica", 9)
    for i, d in enumerate(details, 1):
        if y < 20 * mm:
            c.showPage()
            y = h - 18 * mm
            c.setFont("Helvetica", 9)
        c.drawString(18 * mm, y, str(i))
        c.drawString(26 * mm, y, str(d.production_detail_id or ""))
        c.drawRightString(85 * mm, y, str(d.qty or ""))
        c.drawRightString(102 * mm, y, str(d.qty_roll or ""))
        c.drawRightString(117 * mm, y, str(d.qty_pcs or ""))
        c.drawRightString(140 * mm, y, str(d.weight or ""))
        y -= 5 * mm
    c.showPage()
    c.save()
    buf.seek(0)
    fn = f"surat_jalan_{dh.delivery_number or dh.id}.pdf"
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )

@router.get("/documents/invpl/{packing_id}")
def document_invpl(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> HTMLResponse:
    ph = db.get(PackingHeader, packing_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    details = db.scalars(
        select(PackingDetail)
        .where(PackingDetail.packing_id == packing_id)
        .order_by(PackingDetail.id.asc())
    ).all()
    rows_html = ""
    for i, d in enumerate(details, 1):
        rows_html += f"<tr><td>{i}</td><td>{escape(str(d.production_detail_id or ''))}</td>"
        rows_html += f"<td>{escape(str(d.qty_packed or ''))}</td></tr>"
    body = f"""
<h1>INVOICE PACKING LIST (INVPL)</h1>
<p class="meta"><b>No. Packing</b> {escape(ph.packing_number or str(ph.id))}</p>
<p class="meta"><b>Production ID</b> {escape(str(ph.production_id or ''))} &nbsp; <b>QC ID</b> {escape(str(ph.qc_header_id or ''))}</p>
<p class="meta"><b>Status</b> {escape(ph.status or '')}</p>
<table>
  <thead><tr><th>#</th><th>Production detail</th><th>Qty packed</th></tr></thead>
  <tbody>{rows_html or '<tr><td colspan="3">(belum ada baris)</td></tr>'}</tbody>
</table>
<p class="meta" style="margin-top:24px;">Dibuat dari sistem Tonghong — cetak dari browser (Ctrl+P).</p>
"""
    return HTMLResponse(_html_page("INVPL", body))


@router.get("/documents/invpl/{packing_id}.xlsx")
def document_invpl_xlsx(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    ph = db.get(PackingHeader, packing_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    details = db.scalars(
        select(PackingDetail)
        .where(PackingDetail.packing_id == packing_id)
        .order_by(PackingDetail.id.asc())
    ).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "INVPL"
    ws.append(["No Packing", ph.packing_number or ph.id])
    ws.append(["Production ID", ph.production_id or ""])
    ws.append(["QC ID", ph.qc_header_id or ""])
    ws.append(["Status", ph.status or ""])
    ws.append([])
    ws.append(["#", "Production detail", "Qty packed"])
    for i, d in enumerate(details, 1):
        ws.append([i, d.production_detail_id or "", float(d.qty_packed or 0)])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    fn = f"invpl_{ph.packing_number or ph.id}.xlsx"
    return Response(
        content=buf.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/documents/invpl/{packing_id}.pdf")
def document_invpl_pdf(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Response:
    ph = db.get(PackingHeader, packing_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    details = db.scalars(
        select(PackingDetail)
        .where(PackingDetail.packing_id == packing_id)
        .order_by(PackingDetail.id.asc())
    ).all()

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 18 * mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(18 * mm, y, "INVOICE PACKING LIST (INVPL)")
    y -= 10 * mm
    c.setFont("Helvetica", 10)
    c.drawString(18 * mm, y, f"No Packing: {ph.packing_number or ph.id}")
    y -= 6 * mm
    c.drawString(18 * mm, y, f"Production ID: {ph.production_id or ''}   QC ID: {ph.qc_header_id or ''}")
    y -= 6 * mm
    c.drawString(18 * mm, y, f"Status: {ph.status or ''}")
    y -= 10 * mm

    c.setFont("Helvetica-Bold", 9)
    c.drawString(18 * mm, y, "#")
    c.drawString(26 * mm, y, "Prod. detail")
    c.drawString(80 * mm, y, "Qty packed")
    y -= 5 * mm
    c.setFont("Helvetica", 9)
    for i, d in enumerate(details, 1):
        if y < 20 * mm:
            c.showPage()
            y = h - 18 * mm
            c.setFont("Helvetica", 9)
        c.drawString(18 * mm, y, str(i))
        c.drawString(26 * mm, y, str(d.production_detail_id or ""))
        c.drawRightString(110 * mm, y, str(d.qty_packed or ""))
        y -= 5 * mm
    c.showPage()
    c.save()
    buf.seek(0)
    fn = f"invpl_{ph.packing_number or ph.id}.pdf"
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )
