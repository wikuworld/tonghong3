"""Tanda Terima Dokumen Tagihan — PDF/HTML batch dari beberapa invoice."""

from __future__ import annotations

import io
import re
from datetime import date
from decimal import Decimal
from html import escape
from typing import Any, Optional

from fastapi import HTTPException
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeliveryHeader, Invoice
from app.services.accounts_receivable_report import invoice_qty
from app.services.marketing_documents import COMPANY_BLOCK
from app.timeutil import app_now

_RECEIPT_RE = re.compile(r"^(\d{1,4})/(\d{2})/(\d{4})$")


def _dec(v: Any) -> Decimal:
    if v is None or v == "":
        return Decimal(0)
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal(0)


def _fmt_date_short(d: date | None) -> str:
    if not d:
        return ""
    months = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )
    return f"{d.day:02d}-{months[d.month - 1]}"


def _fmt_date_long_en(d: date | None) -> str:
    if not d:
        return ""
    months = (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
    return f"{months[d.month - 1]} {d.day}, {d.year}"


def _fmt_money(v: Decimal | float | None) -> str:
    n = float(_dec(v))
    # id-ID style with $ prefix like sample
    whole = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {whole}"


def allocate_tanda_terima_number(db: Session, *, on_date: date | None = None) -> str:
    """Format sample: 056/09/2026 (seq / MM / YYYY)."""
    d = on_date or app_now().date()
    mm = f"{d.month:02d}"
    yyyy = str(d.year)
    suffix = f"/{mm}/{yyyy}"
    rows = db.scalars(
        select(Invoice.receipt_no).where(Invoice.receipt_no.is_not(None)).where(Invoice.receipt_no.like(f"%{suffix}"))
    ).all()
    max_seq = 0
    for raw in rows:
        s = (raw or "").strip()
        # allow optional "NO. " prefix
        s = re.sub(r"^NO\.\s*", "", s, flags=re.I)
        m = _RECEIPT_RE.match(s)
        if m and m.group(2) == mm and m.group(3) == yyyy:
            max_seq = max(max_seq, int(m.group(1)))
    return f"{max_seq + 1:03d}/{mm}/{yyyy}"


def gather_tanda_terima_ctx(
    db: Session,
    invoice_ids: list[int],
    *,
    received_by: str | None = None,
    received_date: date | None = None,
    receipt_no: str | None = None,
    stamp_invoices: bool = True,
) -> dict[str, Any]:
    if not invoice_ids:
        raise HTTPException(status_code=400, detail="Pilih minimal satu invoice")
    ids = [int(x) for x in invoice_ids]
    invoices = list(
        db.scalars(select(Invoice).where(Invoice.id.in_(ids)).order_by(Invoice.invoice_date.asc(), Invoice.id.asc())).all()
    )
    if len(invoices) != len(set(ids)):
        found = {int(i.id) for i in invoices}
        missing = [i for i in ids if i not in found]
        raise HTTPException(status_code=404, detail=f"Invoice tidak ditemukan: {missing}")

    cust_keys = {(inv.customer_id, (inv.customer_name or "").strip().upper()) for inv in invoices}
    if len({k[0] or k[1] for k in cust_keys}) > 1:
        raise HTTPException(status_code=400, detail="Tanda terima hanya untuk satu customer yang sama")

    cust_name = (invoices[0].customer_name or "").strip() or "—"
    cust_id = invoices[0].customer_id
    recv_date = received_date or app_now().date()
    recv_by = (received_by or "").strip() or None
    number = (receipt_no or "").strip() or allocate_tanda_terima_number(db, on_date=recv_date)

    lines: list[dict[str, Any]] = []
    total_amt = Decimal(0)
    for i, inv in enumerate(invoices, 1):
        qty = invoice_qty(db, inv)
        # Prefer delivery date for DELIVERY DATE column
        del_date = inv.invoice_date
        if inv.delivery_id:
            dh = db.get(DeliveryHeader, int(inv.delivery_id))
            if dh and dh.delivery_date:
                del_date = dh.delivery_date
        amt = _dec(inv.total_amount)
        # Show balance-aware amount? Sample uses invoice amount. Use total_amount.
        total_amt += amt
        lines.append(
            {
                "no": i,
                "delivery_date": del_date,
                "delivery_date_fmt": _fmt_date_short(del_date),
                "invoice_no": inv.invoice_number or f"#{inv.id}",
                "qty": float(qty),
                "qty_fmt": f"{float(qty):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "amount": float(amt),
                "amount_fmt": _fmt_money(amt),
            }
        )
        if stamp_invoices:
            inv.receipt_no = number
            if recv_by:
                inv.received_by = recv_by
            inv.received_date = recv_date

    return {
        "document_title": "TANDA TERIMA DOKUMEN TAGIHAN",
        "receipt_no": number,
        "receipt_no_display": f"NO. {number}",
        "customer_name": cust_name,
        "customer_id": cust_id,
        "received_by": recv_by,
        "received_date": recv_date,
        "received_date_fmt": _fmt_date_long_en(recv_date),
        "company_lines": list(COMPANY_BLOCK),
        "lines": lines,
        "total_amount": float(total_amt),
        "total_amount_fmt": _fmt_money(total_amt),
        "invoice_ids": [int(i.id) for i in invoices],
    }


def render_tanda_terima_html(ctx: dict[str, Any]) -> str:
    company = "<br/>".join(escape(x) for x in ctx.get("company_lines") or [])
    rows = ""
    for ln in ctx["lines"]:
        rows += (
            "<tr>"
            f"<td class='c'>{ln['no']}</td>"
            f"<td class='c'>{escape(ln['delivery_date_fmt'])}</td>"
            f"<td>{escape(ln['invoice_no'])}</td>"
            f"<td class='r'>{escape(ln['qty_fmt'])}</td>"
            f"<td class='r'>{escape(ln['amount_fmt'])}</td>"
            "</tr>"
        )
    rows += (
        "<tr class='total'>"
        "<td colspan='4'><b>TOTAL</b></td>"
        f"<td class='r'><b>{escape(ctx['total_amount_fmt'])}</b></td>"
        "</tr>"
    )
    body = f"""
<div class="doc">
  <div class="head">
    <div class="company"><b>{company}</b></div>
  </div>
  <h1>{escape(ctx['document_title'])}</h1>
  <div class="no red">{escape(ctx['receipt_no_display'])}</div>
  <div class="cust red"><b>{escape(ctx['customer_name'])}</b></div>
  <table class="grid">
    <thead>
      <tr>
        <th></th><th>DELIVERY DATE</th><th>INVOICE NO</th><th>QTY DELIVERY</th><th>AMOUNT (USD)</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="sigs">
    <div class="sig">
      <div>Submitted By,</div>
      <div class="space"></div>
      <div>Nama jelas : ............................</div>
      <div><b>PT. TONG HONG TANNERY INDONESIA</b></div>
    </div>
    <div class="sig">
      <div class="red">{escape(ctx['received_date_fmt'])}</div>
      <div>Received By</div>
      <div class="space"></div>
      <div>Nama jelas : ............................</div>
      <div><b>{escape(ctx['customer_name'])}</b></div>
    </div>
  </div>
</div>
"""
    style = """
    body { font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: #111; margin: 18px; }
    h1 { text-align: center; font-size: 18px; text-decoration: underline; margin: 18px 0 8px; }
    .no { text-align: center; font-weight: bold; margin-bottom: 12px; }
    .cust { margin: 8px 0 10px; }
    .red { color: #c00; }
    table.grid { width: 100%; border-collapse: collapse; }
    table.grid th, table.grid td { border: 1px solid #333; padding: 6px 8px; }
    table.grid th { background: #f3f3f3; }
    .c { text-align: center; }
    .r { text-align: right; }
    .sigs { display: flex; justify-content: space-between; margin-top: 28px; gap: 24px; }
    .sig { width: 46%; }
    .space { height: 64px; }
    @media print { body { margin: 8mm; } }
    """
    return f"""<!DOCTYPE html><html lang="id"><head><meta charset="utf-8"/>
<title>{escape(ctx.get('document_title') or 'Tanda Terima')}</title>
<style>{style}</style></head><body>{body}
<script>window.print&&window.print()</script>
</body></html>"""


def render_tanda_terima_pdf(ctx: dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    company_style = ParagraphStyle(
        "ttCompany",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        alignment=1,
    )
    title_style = ParagraphStyle(
        "ttTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=1,
        spaceAfter=6,
        textColor=colors.black,
    )
    red_center = ParagraphStyle(
        "ttRedCenter",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=1,
        textColor=colors.HexColor("#cc0000"),
        spaceAfter=8,
    )
    red_left = ParagraphStyle(
        "ttRedLeft",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#cc0000"),
        spaceAfter=8,
    )
    normal = styles["Normal"]
    story: list[Any] = []
    for line in ctx.get("company_lines") or []:
        story.append(Paragraph(escape(line), company_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<u>{escape(ctx['document_title'])}</u>", title_style))
    story.append(Paragraph(escape(ctx["receipt_no_display"]), red_center))
    story.append(Paragraph(escape(ctx["customer_name"]), red_left))

    data = [["", "DELIVERY DATE", "INVOICE NO", "QTY DELIVERY", "AMOUNT (USD)"]]
    for ln in ctx["lines"]:
        data.append(
            [
                str(ln["no"]),
                ln["delivery_date_fmt"],
                ln["invoice_no"],
                ln["qty_fmt"],
                ln["amount_fmt"],
            ]
        )
    data.append(["TOTAL", "", "", "", ctx["total_amount_fmt"]])
    table = Table(data, colWidths=[12 * mm, 32 * mm, 55 * mm, 35 * mm, 40 * mm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.94, 0.94, 0.94)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (3, 1), (4, -1), "RIGHT"),
                ("SPAN", (0, -1), (3, -1)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 20))

    left = [
        Paragraph("Submitted By,", normal),
        Spacer(1, 48),
        Paragraph("Nama jelas : ............................", normal),
        Paragraph("<b>PT. TONG HONG TANNERY INDONESIA</b>", normal),
    ]
    right = [
        Paragraph(f'<font color="#cc0000"><b>{escape(ctx["received_date_fmt"])}</b></font>', normal),
        Paragraph("Received By", normal),
        Spacer(1, 40),
        Paragraph("Nama jelas : ............................", normal),
        Paragraph(f"<b>{escape(ctx['customer_name'])}</b>", normal),
    ]
    sig = Table([[left, right]], colWidths=[90 * mm, 90 * mm])
    sig.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(sig)
    doc.build(story)
    return buf.getvalue()
