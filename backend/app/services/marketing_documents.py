"""Konteks & render INVPL / Surat Jalan sesuai format marketing (Tong Hong)."""

from __future__ import annotations

import io
from datetime import date, timedelta
from decimal import Decimal
from html import escape
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from openpyxl import Workbook

from app.models import (
    Customer,
    DeliveryDetail,
    DeliveryHeader,
    Invoice,
    InvoiceDetail,
    MasterItem,
    PackingDetail,
    PackingHeader,
    PoDetail,
    PoHeader,
    ProductionDetail,
    ProductionOrder,
)
from app.services.document_numbers import invoice_display_number, surat_jalan_display_number

COMPANY_BLOCK = (
    "PT. TONG HONG TANNERY INDONESIA",
    "Kawasan Industri Modern II JL. Modern Industri XIV/W-1, Ds. Barengkok Kec. Kibin Serang-Banten",
    "Telp. 0254-8480870, Fax. 0254-8480743",
)

INVPL_DESC_DEFAULT = "DESCRIPTION: SHOE MAKING MATERIAL (COW LEATHER) :"


def _dec(v: Decimal | None) -> Decimal:
    return v if v is not None else Decimal(0)


def _thickness_mm(pod: PoDetail) -> str:
    if pod.thickness_text and str(pod.thickness_text).strip():
        return str(pod.thickness_text).strip()
    a, b = pod.thickness_min, pod.thickness_max
    if a is not None and b is not None:
        return f"{a}-{b}MM"
    if a is not None or b is not None:
        v = a if a is not None else b
        return f"{v}MM"
    return ""


def _item_description(pod: PoDetail) -> str:
    th = _thickness_mm(pod)
    mat = (pod.material_name or "").strip()
    if th and mat:
        return f"{th} {mat}"
    return th or mat or "—"


def _small_num_to_words(n: int) -> str:
    ones = (
        "ZERO",
        "ONE",
        "TWO",
        "THREE",
        "FOUR",
        "FIVE",
        "SIX",
        "SEVEN",
        "EIGHT",
        "NINE",
        "TEN",
        "ELEVEN",
        "TWELVE",
        "THIRTEEN",
        "FOURTEEN",
        "FIFTEEN",
        "SIXTEEN",
        "SEVENTEEN",
        "EIGHTEEN",
        "NINETEEN",
    )
    tens = ("", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY")
    if n < 20:
        return ones[n]
    if n < 100:
        t, o = divmod(n, 10)
        return tens[t] + (f" {ones[o]}" if o else "")
    if n < 1000:
        h, r = divmod(n, 100)
        base = f"{ones[h]} HUNDRED"
        return base + (f" {_small_num_to_words(r)}" if r else "")
    if n < 1_000_000:
        th, r = divmod(n, 1000)
        base = f"{_small_num_to_words(th)} THOUSAND"
        return base + (f" {_small_num_to_words(r)}" if r else "")
    if n < 1_000_000_000:
        m, r = divmod(n, 1_000_000)
        base = f"{_small_num_to_words(m)} MILLION"
        return base + (f" {_small_num_to_words(r)}" if r else "")
    return str(n)


def usd_amount_in_words(amount: Decimal) -> str:
    amount = amount.quantize(Decimal("0.01"))
    whole = int(amount)
    cents = int((amount - whole) * 100)
    w = _small_num_to_words(whole)
    if cents:
        c = _small_num_to_words(cents)
        return f"{w} POINT {c} UNITED STATES DOLLARS ONLY"
    return f"{w} POINT (ZERO) UNITED STATES DOLLARS ONLY"


def _fmt_date_en(d: date | None) -> str:
    if not d:
        return ""
    return d.strftime("%b %d, %Y").replace(" 0", " ")


def _customer_phone_fax(c: Customer | None) -> str:
    if not c:
        return ""
    p = (c.phone or "").strip()
    if p:
        return f"TELP. NO. : {p}"
    return ""


def _resolve_customer_delivery_packing(
    db: Session, ph: PackingHeader
) -> tuple[Customer | None, DeliveryHeader | None]:
    dh = db.scalars(
        select(DeliveryHeader)
        .where(DeliveryHeader.packing_id == ph.id)
        .order_by(DeliveryHeader.id.desc())
    ).first()
    if dh and dh.customer_id:
        return db.get(Customer, dh.customer_id), dh
    if ph.production_id:
        pr = db.get(ProductionOrder, ph.production_id)
        if pr and pr.po_id:
            hdr = db.get(PoHeader, pr.po_id)
            if hdr and hdr.customer_id:
                return db.get(Customer, hdr.customer_id), dh
    return None, dh


def gather_invpl_rows(
    db: Session, packing_id: int, *, delivery_id: int | None = None
) -> dict[str, Any]:
    ph = db.get(PackingHeader, packing_id)
    if not ph:
        raise ValueError("packing_not_found")

    dh: DeliveryHeader | None = None
    cust: Customer | None = None
    inv: Invoice | None = None
    if delivery_id is not None:
        dh_fixed = db.get(DeliveryHeader, delivery_id)
        if not dh_fixed:
            raise ValueError("delivery_not_found")
        if dh_fixed.packing_id is None or int(dh_fixed.packing_id) != int(packing_id):
            raise ValueError("delivery_packing_mismatch")
        dh = dh_fixed
        if dh.customer_id:
            cust = db.get(Customer, dh.customer_id)
        inv = db.scalars(select(Invoice).where(Invoice.delivery_id == dh.id).limit(1)).first()
    else:
        cust, dh = _resolve_customer_delivery_packing(db, ph)
        if dh:
            inv = db.scalars(select(Invoice).where(Invoice.delivery_id == dh.id).limit(1)).first()

    pkd_list = db.scalars(
        select(PackingDetail)
        .where(PackingDetail.packing_id == packing_id)
        .order_by(PackingDetail.id.asc())
    ).all()

    dd_by_pd: dict[int, DeliveryDetail] = {}
    if dh:
        dds = db.scalars(
            select(DeliveryDetail).where(DeliveryDetail.delivery_id == dh.id)
        ).all()
        for dd in dds:
            if dd.production_detail_id:
                dd_by_pd[int(dd.production_detail_id)] = dd

    inv_details: list[InvoiceDetail] = []
    if inv:
        inv_details = list(
            db.scalars(
                select(InvoiceDetail)
                .where(InvoiceDetail.invoice_id == inv.id)
                .order_by(InvoiceDetail.id.asc())
            ).all()
        )

    is_export = bool(cust and cust.is_export_customer)
    bill_to = ""
    if is_export:
        bill_to = (cust.billing_address or "").strip() if cust else ""
        if not bill_to and ph.production_id:
            pr = db.get(ProductionOrder, ph.production_id)
            if pr and pr.po_id:
                hdr = db.get(PoHeader, pr.po_id)
                if hdr and (hdr.billing_address or "").strip():
                    bill_to = hdr.billing_address.strip()

    lines_out: list[dict[str, Any]] = []
    total_qty = Decimal(0)
    total_amt = Decimal(0)
    total_roll = 0
    total_pcs = 0
    total_nw = Decimal(0)
    total_gw = Decimal(0)
    is_claim_order = False

    for i, pkd in enumerate(pkd_list, 1):
        pd_row: ProductionDetail | None = None
        pod: PoDetail | None = None
        poh: PoHeader | None = None
        master: MasterItem | None = None
        if pkd.production_detail_id:
            pd_row = db.get(ProductionDetail, pkd.production_detail_id)
            if pd_row and pd_row.po_detail_id:
                pod = db.get(PoDetail, pd_row.po_detail_id)
                if pod and pod.po_id:
                    poh = db.get(PoHeader, pod.po_id)
                if pod and pod.master_item_id:
                    master = db.get(MasterItem, pod.master_item_id)

        dd = dd_by_pd.get(int(pkd.production_detail_id or 0), None)
        qty = _dec(dd.qty if dd and dd.qty is not None else pkd.qty_packed)
        unit_price = pod.unit_price if pod else None
        amount: Decimal | None = None
        if unit_price is not None:
            amount = (qty * unit_price).quantize(Decimal("0.01"))
        rolls = dd.qty_roll if dd else None
        pcs = dd.qty_pcs if dd else None
        nw: Decimal | None = None
        gw: Decimal | None = None

        po_no = (poh.po_number or "").strip() if poh else ""
        if poh and (poh.po_category or "").lower() == "claim":
            is_claim_order = True

        remark_line = ""
        if i - 1 < len(inv_details):
            idet = inv_details[i - 1]
            if idet.net_weight is not None:
                nw = idet.net_weight
            if idet.gross_weight is not None:
                gw = idet.gross_weight
            remark_line = (idet.remark or "").strip()
        if not remark_line:
            # Default remark otomatis dari no PO agar commercial invoice tetap terisi.
            remark_line = po_no
        if nw is None and dd and dd.weight is not None:
            nw = dd.weight
        if gw is None:
            gw = nw

        exim = ""
        if is_export and master and (master.exim_material_code or "").strip():
            exim = master.exim_material_code.strip()

        color = (pod.color or "").strip() if pod else ""

        lines_out.append(
            {
                "no": i,
                "po_no": po_no,
                "item": _item_description(pod) if pod else "—",
                "exim_code": exim,
                "color": color,
                "qty": qty,
                "unit": "S/F",
                "unit_price": unit_price,
                "amount": amount,
                "rolls": rolls,
                "pcs": pcs,
                "nw": nw,
                "gw": gw,
                "remark": remark_line,
            }
        )
        total_qty += qty
        if amount is not None:
            total_amt += amount
        total_roll += int(rolls or 0)
        total_pcs += int(pcs or 0)
        if nw is not None:
            total_nw += nw
        if gw is not None:
            total_gw += gw

    if inv and inv.total_amount is not None:
        total_amt = inv.total_amount
    amount_words = (inv.total_in_words or "").strip() if inv and inv.total_in_words else ""
    if not amount_words:
        amount_words = usd_amount_in_words(total_amt)

    doc_date: date | None = None
    if inv and inv.invoice_date:
        doc_date = inv.invoice_date
    elif dh and dh.delivery_date:
        doc_date = dh.delivery_date
    else:
        doc_date = date.today()

    cust_name = (cust.name or "").strip() if cust else "—"
    cust_addr = (cust.address or "").strip() if cust else ""

    return {
        "packing_number": (ph.packing_number or str(ph.id)).strip(),
        "doc_date": doc_date,
        "doc_date_fmt": _fmt_date_en(doc_date),
        "customer_name": cust_name,
        "customer_address": cust_addr,
        "customer_phone_line": _customer_phone_fax(cust),
        "is_export": is_export,
        "bill_to_block": bill_to,
        "lines": lines_out,
        "totals": {
            "qty": total_qty,
            "amount": total_amt,
            "rolls": total_roll,
            "pcs": total_pcs,
            "nw": total_nw,
            "gw": total_gw,
        },
        "total_amount": total_amt,
        "amount_in_words": amount_words,
        "term_of_payment": (inv.term_of_payment or "").strip() if inv else "",
        "bank_name": (inv.bank_name or "").strip() if inv else "",
        "account_number": (inv.account_number or "").strip() if inv else "",
        "bank_address": (inv.bank_address or "").strip() if inv else "",
        "bank_phone": (inv.bank_phone or "").strip() if inv else "",
        "description_line": INVPL_DESC_DEFAULT,
        "claim_title_suffix": " (Non)" if is_claim_order else "",
    }


CI_REASON_MESSAGES: dict[str, str] = {
    "delivery_not_found": "Delivery tidak ditemukan.",
    "no_packing": "Delivery belum terhubung ke packing — commercial invoice tidak tersedia.",
    "packing_not_found": "Packing tidak ditemukan.",
    "invpl_not_printed": "INVPL belum ditandai dicetak — commercial invoice hanya setelah INVPL.",
    "local_wait_h_plus_1": "Pengiriman dalam kota: commercial invoice baru boleh dicetak mulai H+1 tanggal kirim.",
    "outtown_wait_delivery_date": "Commercial invoice belum boleh dicetak sebelum tanggal pengiriman.",
}


def commercial_invoice_eligibility(db: Session, delivery_id: int) -> tuple[bool, str]:
    """Aturan: INVPL sudah dicetak; dalam kota H+1; luar kota mulai tanggal kirim."""
    dh = db.get(DeliveryHeader, delivery_id)
    if not dh:
        return False, "delivery_not_found"
    pid = dh.packing_id
    if not pid:
        return False, "no_packing"
    ph = db.get(PackingHeader, int(pid))
    if not ph:
        return False, "packing_not_found"
    if ph.invpl_printed_at is None:
        return False, "invpl_not_printed"

    dday = dh.delivery_date or date.today()
    zone = (dh.delivery_zone or "outtown").strip().lower()
    today = date.today()
    if zone == "local":
        if today < dday + timedelta(days=1):
            return False, "local_wait_h_plus_1"
    else:
        if today < dday:
            return False, "outtown_wait_delivery_date"
    return True, ""


def commercial_invoice_eligibility_message(code: str) -> str:
    return CI_REASON_MESSAGES.get(code, code)


def gather_commercial_invoice_ctx(db: Session, delivery_id: int) -> dict[str, Any]:
    dh = db.get(DeliveryHeader, delivery_id)
    if not dh or not dh.packing_id:
        raise ValueError("delivery_not_found")
    ctx = gather_invpl_rows(db, int(dh.packing_id), delivery_id=delivery_id)
    suf = (ctx.get("claim_title_suffix") or "").strip()
    ctx["document_title"] = f"COMMERCIAL INVOICE{suf}"
    return ctx


def render_commercial_invoice_html(ctx: dict[str, Any]) -> str:
    """Sama layout INVPL, judul commercial invoice (+ (Non) untuk klaim)."""
    ctx2 = dict(ctx)
    ctx2.setdefault("document_title", "COMMERCIAL INVOICE")
    return render_invpl_html(ctx2)


def render_commercial_invoice_pdf(ctx: dict[str, Any]) -> bytes:
    ctx2 = dict(ctx)
    ctx2.setdefault("document_title", "COMMERCIAL INVOICE")
    return render_invpl_pdf(ctx2)


def render_invpl_html(ctx: dict[str, Any]) -> str:
    is_export = ctx["is_export"]
    bill_html = ""
    if is_export and ctx.get("bill_to_block"):
        bill_html = (
            f'<div class="billto"><b>BILL TO:</b><br/>{escape(ctx["bill_to_block"]).replace(chr(10), "<br/>")}</div>'
        )

    cols = ["NO", "PO NO", "ITEM"]
    if is_export:
        cols.append("EXIM CODE")
    cols.extend(["COLOR", "Q'TY", "UNIT", "UNIT PRICE (USD)", "AMOUNT (USD)", "ROLLS", "PCS", "N.W (KGS)", "G.W (KGS)", "REMARK"])

    thead = "<tr>" + "".join(f"<th>{escape(c)}</th>" for c in cols) + "</tr>"
    rows_html = ""
    for ln in ctx["lines"]:
        cells = [
            str(ln["no"]),
            escape(ln["po_no"] or ""),
            escape(ln["item"] or ""),
        ]
        if is_export:
            cells.append(escape(ln.get("exim_code") or ""))
        up = ln["unit_price"]
        am = ln["amount"]
        cells.extend(
            [
                escape(ln["color"] or ""),
                f"{ln['qty']:.2f}" if ln["qty"] is not None else "",
                escape(ln["unit"] or "S/F"),
                f"{up:.4f}" if up is not None else "",
                f"{am:.2f}" if am is not None else "",
                str(ln["rolls"] or "") if ln["rolls"] is not None else "",
                str(ln["pcs"] or "") if ln["pcs"] is not None else "",
                f"{ln['nw']:.1f}" if ln.get("nw") is not None else "",
                f"{ln['gw']:.1f}" if ln.get("gw") is not None else "",
                escape(ln.get("remark") or ""),
            ]
        )
        rows_html += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"

    t = ctx["totals"]
    ncol = len(cols)
    o = 1 if is_export else 0
    foot = [""] * ncol
    foot[0] = "TOTAL"
    foot[4 + o] = f"{t['qty']:.2f}"
    foot[7 + o] = f"{t['amount']:.2f}"
    foot[8 + o] = str(t["rolls"])
    foot[9 + o] = str(t["pcs"])
    foot[10 + o] = f"{t['nw']:.1f}" if t["nw"] else ""
    foot[11 + o] = f"{t['gw']:.1f}" if t["gw"] else ""
    rows_html += "<tr class='total'>" + "".join(f"<td><b>{escape(str(x))}</b></td>" for x in foot) + "</tr>"

    meta_right = f"""
    <div class="meta-right">
      <div><b>DATE:</b> {escape(ctx['doc_date_fmt'])}</div>
      <div><b>PL. NO.:</b> {escape(ctx['packing_number'])}</div>
    </div>
    """

    company_html = "<br/>".join(escape(x) for x in COMPANY_BLOCK)
    body = f"""
<div class="doc">
  <div class="header-row">
    <div class="company"><b>{company_html}</b></div>
    {meta_right}
  </div>
  <div class="two-col">
    <div>
      <div><b>TO:</b></div>
      <div>{escape(ctx['customer_name'])}</div>
      <div class="addr">{escape(ctx['customer_address']).replace(chr(10), '<br/>')}</div>
      <div>{escape(ctx['customer_phone_line'])}</div>
    </div>
  </div>
  {bill_html}
  <h2 class="title">{escape(ctx.get('document_title', 'INVOICE PACKING LIST'))}</h2>
  <div class="stars">*******************</div>
  <p class="desc">{escape(ctx['description_line'])}</p>
  <table class="grid"><thead>{thead}</thead><tbody>{rows_html}</tbody></table>
  <p class="words"><b>SAY TOTAL IN WORDS:</b> {escape(ctx['amount_in_words'])}</p>
  <div class="footer-bank">
    <div><b>TERM OF PAYMENT:</b> {escape(ctx['term_of_payment'] or '—')}</div>
    <div><b>OUR ADVICEING BANK:</b> {escape(ctx['bank_name'] or '—')}</div>
    <div><b>ACCOUNT NO.:</b> {escape(ctx['account_number'] or '—')}</div>
    <div><b>BANK ADDRESS:</b> {escape(ctx['bank_address'] or '—')}</div>
    <div><b>BANK CONTACT:</b> {escape(ctx['bank_phone'] or '—')}</div>
  </div>
  <div class="sign">
    <p>Authorize signature:</p>
    <p><br/><br/></p>
    <p><b>(CHIU PO HAO)</b></p>
    <p>Director</p>
  </div>
</div>
"""
    style = """
    body { font-family: Arial, Helvetica, sans-serif; margin: 16px; color: #111; font-size: 11px; }
    .doc { max-width: 1100px; margin: 0 auto; }
    .header-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
    .company { flex: 1; text-align: center; font-size: 12px; line-height: 1.35; }
    .meta-right { text-align: right; min-width: 200px; font-size: 11px; }
    .two-col { margin-top: 12px; }
    .addr { margin: 4px 0; white-space: pre-wrap; }
    .billto { margin: 10px 0; padding: 8px; border: 1px solid #333; background: #fafafa; }
    .title { text-align: center; margin: 16px 0 4px; font-size: 14px; }
    .stars { text-align: center; letter-spacing: 2px; margin-bottom: 8px; }
    .desc { font-weight: bold; margin: 8px 0; }
    table.grid { border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 9px; }
    table.grid th, table.grid td { border: 1px solid #333; padding: 4px 3px; vertical-align: top; }
    table.grid th { background: #e8e8e8; }
    tr.total td { background: #f0f0f0; }
    .words { margin-top: 12px; font-size: 10px; }
    .footer-bank { margin-top: 14px; line-height: 1.5; font-size: 10px; }
    .sign { margin-top: 28px; text-align: right; font-size: 10px; }
    @media print { body { margin: 8px; } }
    """
    doc_title = str(ctx.get("document_title", "INVPL"))
    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"/><title>{escape(doc_title)}</title>
<style>{style}</style></head><body>{body}</body></html>"""


def render_invpl_xlsx(ctx: dict[str, Any]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "INVPL"
    for i, line in enumerate(COMPANY_BLOCK, 1):
        ws.append([line])
    ws.append([])
    ws.append(["TO", ctx["customer_name"]])
    for part in (ctx["customer_address"] or "").split("\n"):
        if part.strip():
            ws.append(["", part.strip()])
    ws.append(["", ctx["customer_phone_line"]])
    if ctx["is_export"] and ctx.get("bill_to_block"):
        ws.append(["BILL TO", ctx["bill_to_block"]])
    ws.append([])
    ws.append(["DATE", ctx["doc_date_fmt"]])
    ws.append(["PL. NO.", ctx["packing_number"]])
    ws.append([])
    ws.append([ctx["description_line"]])
    is_export = ctx["is_export"]
    head = ["NO", "PO NO", "ITEM"]
    if is_export:
        head.append("EXIM CODE")
    head.extend(
        ["COLOR", "QTY", "UNIT", "UNIT PRICE USD", "AMOUNT USD", "ROLLS", "PCS", "NW", "GW", "REMARK"]
    )
    ws.append(head)
    for ln in ctx["lines"]:
        row = [ln["no"], ln["po_no"], ln["item"]]
        if is_export:
            row.append(ln.get("exim_code") or "")
        row.extend(
            [
                ln["color"],
                float(ln["qty"]) if ln["qty"] is not None else None,
                ln["unit"],
                float(ln["unit_price"]) if ln["unit_price"] is not None else None,
                float(ln["amount"]) if ln["amount"] is not None else None,
                ln["rolls"],
                ln["pcs"],
                float(ln["nw"]) if ln.get("nw") is not None else None,
                float(ln["gw"]) if ln.get("gw") is not None else None,
                ln.get("remark") or "",
            ]
        )
        ws.append(row)
    t = ctx["totals"]
    o = 1 if is_export else 0
    total_row = [""] * len(head)
    total_row[0] = "TOTAL"
    total_row[4 + o] = float(t["qty"])
    total_row[7 + o] = float(t["amount"])
    total_row[8 + o] = t["rolls"]
    total_row[9 + o] = t["pcs"]
    total_row[10 + o] = float(t["nw"]) if t["nw"] else None
    total_row[11 + o] = float(t["gw"]) if t["gw"] else None
    ws.append([])
    ws.append(total_row)
    ws.append(["SAY TOTAL IN WORDS", ctx["amount_in_words"]])
    ws.append(["TERM OF PAYMENT", ctx["term_of_payment"]])
    ws.append(["BANK", ctx["bank_name"]])
    ws.append(["ACCOUNT", ctx["account_number"]])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def render_invpl_pdf(ctx: dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )
    styles = getSampleStyleSheet()
    small = ParagraphStyle(name="s", parent=styles["Normal"], fontSize=7, leading=8)
    story: list[Any] = []
    for line in COMPANY_BLOCK:
        story.append(Paragraph(escape(line), small))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(f"<b>TO:</b> {escape(ctx['customer_name'])}", small))
    story.append(Paragraph(escape(ctx["customer_address"] or ""), small))
    story.append(Paragraph(escape(ctx["customer_phone_line"]), small))
    if ctx["is_export"] and ctx.get("bill_to_block"):
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"<b>BILL TO:</b> {escape(ctx['bill_to_block'])}", small))
    story.append(Spacer(1, 2 * mm))
    story.append(
        Paragraph(
            f"<b>DATE:</b> {escape(ctx['doc_date_fmt'])} &nbsp; <b>PL. NO.:</b> {escape(ctx['packing_number'])}",
            small,
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(f"<b>{escape(str(ctx.get('document_title', 'INVOICE PACKING LIST')))}</b>", styles["Heading2"])
    )
    story.append(Paragraph(escape(ctx["description_line"]), small))

    is_export = ctx["is_export"]
    table_data: list[list[str]] = []
    head = ["NO", "PO", "ITEM"]
    if is_export:
        head.append("EXIM")
    head.extend(["COLOR", "QTY", "U", "U.PRICE", "AMOUNT", "RLL", "PCS", "NW", "GW", "RMK"])
    table_data.append(head)
    for ln in ctx["lines"]:
        row = [
            str(ln["no"]),
            (ln["po_no"] or "")[:14],
            (ln["item"] or "")[:42],
        ]
        if is_export:
            row.append((ln.get("exim_code") or "")[:12])
        up = ln["unit_price"]
        am = ln["amount"]
        row.extend(
            [
                (ln["color"] or "")[:16],
                f"{ln['qty']:.2f}" if ln["qty"] is not None else "",
                ln["unit"] or "S/F",
                f"{up:.2f}" if up is not None else "",
                f"{am:.2f}" if am is not None else "",
                str(ln["rolls"] or ""),
                str(ln["pcs"] or ""),
                f"{ln['nw']:.1f}" if ln.get("nw") is not None else "",
                f"{ln['gw']:.1f}" if ln.get("gw") is not None else "",
                (ln.get("remark") or "")[:10],
            ]
        )
        table_data.append(row)
    t = ctx["totals"]
    total_row = ["", "", "TOTAL"]
    if is_export:
        total_row.append("")
    total_row.extend(
        [
            "",
            f"{t['qty']:.2f}",
            "",
            "",
            f"{t['amount']:.2f}",
            str(t["rolls"]),
            str(t["pcs"]),
            f"{t['nw']:.1f}" if t["nw"] else "",
            f"{t['gw']:.1f}" if t["gw"] else "",
            "",
        ]
    )
    table_data.append(total_row)

    col_count = len(table_data[0])
    full_w = landscape(A4)[0] - 24 * mm
    cw = full_w / col_count
    tbl = Table(table_data, colWidths=[cw] * col_count, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(f"<b>SAY TOTAL IN WORDS:</b> {escape(ctx['amount_in_words'])}", small))
    story.append(Paragraph(escape(f"TERM: {ctx['term_of_payment']} | BANK: {ctx['bank_name']}"), small))
    story.append(Paragraph(escape(f"ACCT: {ctx['account_number']} | {ctx['bank_address']}"), small))
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def gather_sj_rows(db: Session, delivery_id: int) -> dict[str, Any]:
    dh = db.get(DeliveryHeader, delivery_id)
    if not dh:
        raise ValueError("delivery_not_found")
    cust = db.get(Customer, dh.customer_id) if dh.customer_id else None
    inv = db.scalars(select(Invoice).where(Invoice.delivery_id == dh.id).limit(1)).first()

    details = db.scalars(
        select(DeliveryDetail)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .order_by(DeliveryDetail.id.asc())
    ).all()

    lines_out: list[dict[str, Any]] = []
    t_qty = Decimal(0)
    t_roll = 0
    t_pcs = 0
    ph_for_cat: PoHeader | None = None
    extra_header_remark = (dh.destination or "").strip()
    for i, dd in enumerate(details, 1):
        pod: PoDetail | None = None
        poh: PoHeader | None = None
        pd_row: ProductionDetail | None = None
        if dd.production_detail_id:
            pd_row = db.get(ProductionDetail, dd.production_detail_id)
            if pd_row and pd_row.po_detail_id:
                pod = db.get(PoDetail, pd_row.po_detail_id)
                if pod and pod.po_id:
                    poh = db.get(PoHeader, pod.po_id)
        if ph_for_cat is None and poh is not None:
            ph_for_cat = poh
        po_no = (poh.po_number or "").strip() if poh else ""
        mat = _item_description(pod) if pod else "—"
        thick = _thickness_mm(pod) if pod else ""
        color = (pod.color or "").strip() if pod else ""
        po_line_remark = (pod.detail_remark or "").strip() if pod else ""
        base_remark = po_no or ""
        if po_line_remark:
            base_remark = f"{base_remark} | {po_line_remark}" if base_remark else po_line_remark
        if extra_header_remark:
            base_remark = f"{base_remark} | {extra_header_remark}" if base_remark else extra_header_remark
        lines_out.append(
            {
                "no": i,
                "po_no": po_no,
                "material": mat,
                "thickness": thick,
                "color": color,
                "qty": _dec(dd.qty),
                "rolls": dd.qty_roll,
                "pcs": dd.qty_pcs,
                "remark": base_remark,
            }
        )
        t_qty += _dec(dd.qty)
        t_roll += int(dd.qty_roll or 0)
        t_pcs += int(dd.qty_pcs or 0)

    dn_raw = (dh.delivery_number or str(dh.id)).strip()
    inv_raw = (inv.invoice_number or "").strip() if inv else ""
    return {
        "delivery_number": surat_jalan_display_number(dn_raw, ph_for_cat) if dn_raw else "",
        "delivery_date": dh.delivery_date,
        "delivery_date_fmt": _fmt_date_en(dh.delivery_date),
        "destination": (dh.destination or "").strip(),
        "vehicle_number": (dh.vehicle_number or "").strip(),
        "driver_name": (dh.driver_name or "").strip(),
        "bc_number": (dh.bc_number or "").strip(),
        "bc_date_fmt": _fmt_date_en(dh.bc_date) if dh.bc_date else "",
        "customer_name": (cust.name or "").strip() if cust else "—",
        "customer_address": (cust.address or "").strip() if cust else "",
        "customer_phone_line": _customer_phone_fax(cust),
        "invoice_no": invoice_display_number(inv_raw, ph_for_cat),
        "lines": lines_out,
        "totals": {"qty": t_qty, "rolls": t_roll, "pcs": t_pcs},
        "is_export": bool(cust and cust.is_export_customer),
    }


def render_sj_html(ctx: dict[str, Any]) -> str:
    rows_html = ""
    for ln in ctx["lines"]:
        rows_html += (
            f"<tr><td>{ln['no']}</td>"
            f"<td>{escape(ln['po_no'])}</td>"
            f"<td>{escape(ln['material'])}</td>"
            f"<td>{escape(ln['thickness'])}</td>"
            f"<td>{escape(ln['color'])}</td>"
            f"<td class='r'>{ln['qty']:.2f}</td>"
            f"<td class='r'>{ln['rolls'] or ''}</td>"
            f"<td class='r'>{ln['pcs'] or ''}</td>"
            f"<td>{escape(ln['remark'])}</td></tr>"
        )
    t = ctx["totals"]
    rows_html += (
        f"<tr class='total'><td colspan='5'><b>TOTAL</b></td>"
        f"<td class='r'><b>{t['qty']:.2f}</b></td>"
        f"<td class='r'><b>{t['rolls']}</b></td>"
        f"<td class='r'><b>{t['pcs']}</b></td><td></td></tr>"
    )

    company = "<br/>".join(escape(x) for x in COMPANY_BLOCK)
    export_note = ""
    if ctx.get("is_export"):
        export_note = f'<p class="note">{escape("Catatan: untuk transaksi ekspor, cetak Surat Jalan bersifat opsional.")}</p>'

    body = f"""
<div class="doc">
  <div class="top"><span class="page">Page 1</span></div>
  <div class="company"><b>{company}</b></div>
  <h2 class="title">SURAT JALAN (DELIVERYSHEET)</h2>
  {export_note}
  <div class="grid-2">
    <div>
      <div><b>DELIVERED TO:</b> {escape(ctx['customer_name'])}</div>
      <div><b>ADDRESS:</b> {escape(ctx['customer_address']).replace(chr(10), '<br/>')}</div>
      <div>{escape(ctx['customer_phone_line'])}</div>
      <div><b>INV. NO.:</b> {escape(ctx['invoice_no'] or '—')}</div>
    </div>
    <div class="right">
      <div><b>SURAT JALAN NO.:</b> {escape(ctx['delivery_number'])}</div>
      <div><b>NO. BC:</b> {escape(ctx['bc_number'] or '—')}</div>
      <div><b>DATE BC:</b> {escape(ctx['bc_date_fmt'] or '—')}</div>
      <div><b>CAR NO.:</b> {escape(ctx['vehicle_number'])}</div>
      <div><b>DRIVER'S NAME:</b> {escape(ctx['driver_name'])}</div>
      <div><b>DATE:</b> {escape(ctx['delivery_date_fmt'])}</div>
    </div>
  </div>
  <table class="grid">
    <thead><tr><th>NO.</th><th>PO NO</th><th>Material name</th><th>Thickness (MM)</th><th>Color</th>
    <th>Quantity (S/F)</th><th>Rolls</th><th>Pieces</th><th>Remark</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  <div class="sign4">
    <div><b>RECEIVED BY</b><br/><br/><br/></div>
    <div><b>APPROVED BY</b><br/><br/><br/></div>
    <div><b>SECURITY</b><br/><br/><br/></div>
    <div><b>DELIVERED BY</b><br/><br/><br/></div>
  </div>
  <p class="foot-note"><b>NOTE :</b> WHITE(1) ACC, RED(2) CUSTOMER, YELLOW(3) EXIM, GREEN(4) WAREHOUSE, BLUE(5) SECURITY.</p>
</div>
"""
    style = """
    body { font-family: Arial, sans-serif; margin: 14px; font-size: 11px; color: #111; }
    .doc { max-width: 800px; margin: 0 auto; }
    .top { text-align: right; margin-bottom: 4px; }
    .company { text-align: center; margin-bottom: 8px; line-height: 1.35; }
    .title { text-align: center; font-size: 14px; margin: 8px 0; }
    .note { font-size: 10px; color: #444; margin: 6px 0; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0; }
    .right { text-align: left; }
    table.grid { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 10px; }
    table.grid th, table.grid td { border: 1px solid #333; padding: 5px; }
    table.grid th { background: #eaeaea; }
    td.r { text-align: right; }
    tr.total td { background: #f5f5f5; font-weight: bold; }
    .sign4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-top: 24px; text-align: center; font-size: 10px; }
    .foot-note { margin-top: 16px; font-size: 9px; }
    @media print { body { margin: 8px; } }
    """
    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"/><title>Surat Jalan</title>
<style>{style}</style></head><body>{body}</body></html>"""


def render_sj_pdf(ctx: dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 14 * mm
    c.setFont("Helvetica", 8)
    c.drawRightString(w - 18 * mm, y, "Page 1")
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 11)
    for line in COMPANY_BLOCK:
        c.drawCentredString(w / 2, y, line)
        y -= 4 * mm
    y -= 2 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(w / 2, y, "SURAT JALAN (DELIVERYSHEET)")
    y -= 8 * mm
    c.setFont("Helvetica", 9)
    c.drawString(18 * mm, y, f"DELIVERED TO: {ctx['customer_name'][:55]}")
    c.drawString(110 * mm, y, f"SURAT JALAN NO.: {ctx['delivery_number']}")
    y -= 5 * mm
    addr = (ctx["customer_address"] or "")[:80]
    c.drawString(18 * mm, y, f"ADDRESS: {addr}")
    c.drawString(110 * mm, y, f"NO. BC: {ctx['bc_number'] or '—'}")
    y -= 5 * mm
    c.drawString(18 * mm, y, ctx["customer_phone_line"][:70])
    c.drawString(110 * mm, y, f"DATE BC: {ctx['bc_date_fmt'] or '—'}")
    y -= 5 * mm
    c.drawString(18 * mm, y, f"INV. NO.: {ctx['invoice_no'] or '—'}")
    c.drawString(110 * mm, y, f"CAR NO.: {ctx['vehicle_number'][:20]}")
    y -= 5 * mm
    c.drawString(110 * mm, y, f"DRIVER: {ctx['driver_name'][:30]}")
    y -= 5 * mm
    c.drawString(110 * mm, y, f"DATE: {ctx['delivery_date_fmt']}")
    y -= 10 * mm
    if ctx.get("is_export"):
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(18 * mm, y, "Catatan: untuk ekspor, SJ opsional.")
        y -= 5 * mm
        c.setFont("Helvetica", 9)

    cols = ("NO", "PO", "MATERIAL", "THK", "COLOR", "QTY", "RLL", "PCS", "RMK")
    x0 = 12 * mm
    colw = (w - 24 * mm) / len(cols)
    c.setFont("Helvetica-Bold", 7)
    for i, lab in enumerate(cols):
        c.drawString(x0 + i * colw, y, lab)
    y -= 4 * mm
    c.setFont("Helvetica", 7)
    for ln in ctx["lines"]:
        if y < 28 * mm:
            c.showPage()
            y = h - 18 * mm
            c.setFont("Helvetica", 7)
        row = [
            str(ln["no"]),
            (ln["po_no"] or "")[:10],
            (ln["material"] or "")[:22],
            (ln["thickness"] or "")[:8],
            (ln["color"] or "")[:12],
            f"{ln['qty']:.2f}",
            str(ln["rolls"] or ""),
            str(ln["pcs"] or ""),
            "",
        ]
        for i, cell in enumerate(row):
            c.drawString(x0 + i * colw, y, cell)
        y -= 3.5 * mm
    t = ctx["totals"]
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x0, y, "TOTAL")
    c.drawString(x0 + 5 * colw, y, f"{t['qty']:.2f}")
    c.drawString(x0 + 6 * colw, y, str(t["rolls"]))
    c.drawString(x0 + 7 * colw, y, str(t["pcs"]))
    y -= 16 * mm
    c.setFont("Helvetica", 8)
    c.drawString(18 * mm, y, "RECEIVED BY")
    c.drawString(58 * mm, y, "APPROVED BY")
    c.drawString(98 * mm, y, "SECURITY")
    c.drawString(138 * mm, y, "DELIVERED BY")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


def render_sj_dotmatrix_html(ctx: dict[str, Any]) -> str:
    """Cetak fisik dot matrix — layout ringkas (5.5in × 8.5in)."""
    rows_html = ""
    for ln in ctx["lines"]:
        rows_html += (
            f"<tr>"
            f"<td>{ln['no']}</td>"
            f"<td>{escape(ln['po_no'])}</td>"
            f"<td>{escape(str(ln['material'] or '')[:28])}</td>"
            f"<td class='r'>{ln['qty']:.2f}</td>"
            f"<td class='r'>{ln['rolls'] or ''}</td>"
            f"<td class='r'>{ln['pcs'] or ''}</td>"
            f"</tr>"
        )
    t = ctx["totals"]
    rows_html += (
        f"<tr class='total'><td colspan='3'><b>TOTAL</b></td>"
        f"<td class='r'><b>{t['qty']:.2f}</b></td>"
        f"<td class='r'><b>{t['rolls']}</b></td>"
        f"<td class='r'><b>{t['pcs']}</b></td></tr>"
    )
    company = " | ".join(COMPANY_BLOCK)
    body = f"""
<div class="doc">
  <div class="company"><b>{escape(company)}</b></div>
  <h2 class="title">SURAT JALAN (DELIVERY SHEET)</h2>
  <div class="meta">
    <div><b>TO:</b> {escape(str(ctx['customer_name'] or '')[:40])}</div>
    <div><b>SJ NO:</b> {escape(ctx['delivery_number'])} &nbsp; <b>DATE:</b> {escape(ctx['delivery_date_fmt'])}</div>
    <div><b>CAR:</b> {escape(ctx['vehicle_number'])} &nbsp; <b>DRIVER:</b> {escape(ctx['driver_name'])}</div>
  </div>
  <table class="grid">
    <thead><tr><th>NO</th><th>PO NO</th><th>MATERIAL</th><th>QTY SF</th><th>ROLL</th><th>PCS</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  <div class="sign4">
    <div>RECEIVED BY</div><div>APPROVED BY</div><div>SECURITY</div><div>DELIVERED BY</div>
  </div>
  <p class="foot-note"><b>NOTE:</b> WHITE(1) ACC, RED(2) CUSTOMER, YELLOW(3) EXIM, GREEN(4) WAREHOUSE, BLUE(5) SECURITY.</p>
</div>
"""
    style = """
    @page { size: 5.5in 8.5in; margin: 0.25in; }
    body { font-family: 'Courier New', Courier, monospace; margin: 0; font-size: 9px; color: #000; }
    .doc { width: 5in; margin: 0 auto; }
    .company { text-align: center; font-size: 8px; line-height: 1.2; margin-bottom: 4px; }
    .title { text-align: center; font-size: 11px; margin: 4px 0 8px; }
    .meta { margin-bottom: 6px; line-height: 1.35; }
    table.grid { width: 100%; border-collapse: collapse; font-size: 8px; }
    table.grid th, table.grid td { border: 1px solid #000; padding: 2px 3px; }
    td.r { text-align: right; }
    tr.total td { font-weight: bold; }
    .sign4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-top: 12px; text-align: center; font-size: 7px; }
    .foot-note { margin-top: 8px; font-size: 7px; }
    @media print { body { margin: 0; } }
    """
    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"/><title>Surat Jalan Dot Matrix</title>
<style>{style}</style></head><body>{body}
<script>window.onload=function(){{window.print();}}</script></body></html>"""
