"""Cetak Surat Jalan & INVPL (HTML untuk browser print)."""

from __future__ import annotations

from html import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Customer, DeliveryDetail, DeliveryHeader, PackingDetail, PackingHeader

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
def document_surat_jalan(delivery_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
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


@router.get("/documents/invpl/{packing_id}")
def document_invpl(packing_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
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
