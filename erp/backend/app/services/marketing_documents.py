"""Konteks & render INVPL / Surat Jalan sesuai format marketing (Tong Hong)."""

from __future__ import annotations

import base64
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
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from openpyxl import Workbook
import qrcode
from qrcode.constants import ERROR_CORRECT_M

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

INVPL_DESC_DEFAULT = "DESCRIPTION: SHOE MAKING MATERIAL (COW LEATHER)"
INVPL_TITLE = "INVOICE PACKING LIST"
INVPL_TITLE_FOC = "INVOICE PACKING LIST (FOC)"


def invpl_document_title(*, foc: bool = False) -> str:
    return INVPL_TITLE_FOC if foc else INVPL_TITLE


def apply_invpl_foc_title(ctx: dict[str, Any], foc: bool = False) -> dict[str, Any]:
    """Salin ctx dan set judul INVPL (+ FOC bila diminta). Tidak mengubah commercial invoice."""
    out = dict(ctx)
    out["foc"] = bool(foc)
    out["document_title"] = invpl_document_title(foc=bool(foc))
    return out


# Fallback bank INVPL (sama teks ringkas Proforma) bila invoice belum diisi.
INVPL_BANK_DEFAULT = {
    "bank_name": "BANK CTBC INDONESIA",
    "account_number": "2020357701 (USD)",
    "bank_address": "TAMARA CENTER 16th FLOOR, JL. JENDRAL SUDIRMAN KAV.24 JAKARTA",
    "bank_phone": "62-21-5237788/7245, Fax : 021-2500622",
}

SJ_SIGN_LABELS = ("RECEIVED BY", "APPROVED BY", "SECURITY", "DELIVERED BY")


def _dec(v: Decimal | None) -> Decimal:
    return v if v is not None else Decimal(0)


def _thickness_mm(pod: PoDetail) -> str:
    from app.services.thickness_format import display_po_thickness_mm

    return display_po_thickness_mm(pod)


def _item_description(pod: PoDetail) -> str:
    th = _thickness_mm(pod)
    mat = (pod.material_name or "").strip()
    if th and mat:
        return f"{th} {mat}"
    return th or mat or "—"


def _sj_item_text(pod: PoDetail | None) -> str:
    """ITEM SJ: thickness + material + emboss + color (satu sel)."""
    if not pod:
        return "—"
    parts: list[str] = []
    th = _thickness_mm(pod)
    mat = (pod.material_name or "").strip()
    emb = (pod.emboss or "").strip()
    color = (pod.color or "").strip()
    if th and mat:
        parts.append(f"{th} {mat}")
    elif th or mat:
        parts.append(th or mat)
    if emb:
        parts.append(emb)
    if color:
        parts.append(color)
    return " ".join(parts) if parts else "—"


def _sign4_html(*, compact: bool = False) -> str:
    pad = "<br/><br/>" if compact else "<br/><br/><br/>"
    cells = "".join(
        f'<div class="sign-box"><b>{lab}</b>{pad}<div class="sign-line">( &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; )</div></div>'
        for lab in SJ_SIGN_LABELS
    )
    return f'<div class="sign4">{cells}</div>'


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


def _customer_tel_fax(c: Customer | None) -> tuple[str, str]:
    """Tel / fax terpisah untuk meta SJ (fax belum ada kolom → kosong)."""
    if not c:
        return "", ""
    return (c.phone or "").strip(), ""


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


def _pod_chain_from_delivery_detail(db: Session, dd: DeliveryDetail):
    pod: PoDetail | None = None
    if dd.po_detail_id:
        pod = db.get(PoDetail, int(dd.po_detail_id))
    elif dd.production_detail_id:
        pd_row = db.get(ProductionDetail, int(dd.production_detail_id))
        if pd_row and pd_row.po_detail_id:
            pod = db.get(PoDetail, int(pd_row.po_detail_id))
    poh = db.get(PoHeader, pod.po_id) if pod and pod.po_id else None
    master = db.get(MasterItem, pod.master_item_id) if pod and pod.master_item_id else None
    return pod, poh, master


def sj_po_no_from_header(poh: PoHeader | None) -> str:
    """P.O. NO. di Surat Jalan = No. PO Customer yang diketik saat input SO.

    Fallback ke nomor SO internal hanya jika PO Customer kosong (data lama).
    """
    if not poh:
        return ""
    cust = (getattr(poh, "po_customer_ref", None) or "").strip()
    if cust:
        return cust
    return (getattr(poh, "po_number", None) or "").strip()


def _invpl_line_dict(
    *,
    no: int,
    pod: PoDetail | None,
    poh: PoHeader | None,
    master: MasterItem | None,
    qty: Decimal,
    rolls,
    pcs,
    nw,
    gw,
    remark_line: str,
    is_export: bool,
) -> dict[str, Any]:
    unit_price = pod.unit_price if pod else None
    amount: Decimal | None = None
    if unit_price is not None:
        amount = (qty * unit_price).quantize(Decimal("0.01"))
    po_no = (poh.po_number or "").strip() if poh else ""
    exim = ""
    if is_export and master and (master.exim_material_code or "").strip():
        exim = master.exim_material_code.strip()
    return {
        "no": no,
        "po_no": po_no,
        "item": _item_description(pod) if pod else "—",
        "exim_code": exim,
        "color": (pod.color or "").strip() if pod else "",
        "qty": qty,
        "unit": "S/F",
        "unit_price": unit_price,
        "amount": amount,
        "rolls": rolls,
        "pcs": pcs,
        "nw": nw,
        "gw": gw,
        "remark": remark_line,
        "is_claim": bool(poh and (poh.po_category or "").lower() == "claim"),
    }


def gather_invpl_rows(
    db: Session, packing_id: int | None = None, *, delivery_id: int | None = None
) -> dict[str, Any]:
    dh: DeliveryHeader | None = None
    if delivery_id is not None:
        dh = db.get(DeliveryHeader, delivery_id)
        if not dh:
            raise ValueError("delivery_not_found")
        if packing_id is None and dh.packing_id:
            packing_id = int(dh.packing_id)

    ph: PackingHeader | None = None
    if packing_id:
        ph = db.get(PackingHeader, int(packing_id))
    if not ph and not dh:
        raise ValueError("packing_not_found")

    cust: Customer | None = None
    inv: Invoice | None = None
    if dh:
        if dh.customer_id:
            cust = db.get(Customer, dh.customer_id)
        inv = db.scalars(select(Invoice).where(Invoice.delivery_id == dh.id).limit(1)).first()
    elif ph:
        cust, dh = _resolve_customer_delivery_packing(db, ph)
        if dh:
            inv = db.scalars(select(Invoice).where(Invoice.delivery_id == dh.id).limit(1)).first()

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
        if not bill_to and ph and ph.production_id:
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

    delivery_details: list[DeliveryDetail] = []
    if dh:
        delivery_details = list(
            db.scalars(
                select(DeliveryDetail)
                .where(DeliveryDetail.delivery_id == dh.id)
                .order_by(DeliveryDetail.id.asc())
            ).all()
        )

    if delivery_details:
        for i, dd in enumerate(delivery_details, 1):
            pod, poh, master = _pod_chain_from_delivery_detail(db, dd)
            qty = _dec(dd.qty)
            rolls = dd.qty_roll
            pcs = dd.qty_pcs
            nw = dd.weight
            gw = nw
            po_no = (poh.po_number or "").strip() if poh else ""
            remark_line = po_no
            if i - 1 < len(inv_details):
                idet = inv_details[i - 1]
                if idet.net_weight is not None:
                    nw = idet.net_weight
                if idet.gross_weight is not None:
                    gw = idet.gross_weight
                if (idet.remark or "").strip():
                    remark_line = (idet.remark or "").strip()
            if gw is None:
                gw = nw
            line = _invpl_line_dict(
                no=i,
                pod=pod,
                poh=poh,
                master=master,
                qty=qty,
                rolls=rolls,
                pcs=pcs,
                nw=nw,
                gw=gw,
                remark_line=remark_line,
                is_export=is_export,
            )
            if line.pop("is_claim"):
                is_claim_order = True
            lines_out.append(line)
            total_qty += qty
            if line["amount"] is not None:
                total_amt += line["amount"]
            total_roll += int(rolls or 0)
            total_pcs += int(pcs or 0)
            if nw is not None:
                total_nw += nw
            if gw is not None:
                total_gw += gw
    elif ph:
        pkd_list = db.scalars(
            select(PackingDetail)
            .where(PackingDetail.packing_id == ph.id)
            .order_by(PackingDetail.id.asc())
        ).all()
        dd_by_pd: dict[int, DeliveryDetail] = {}
        for dd in delivery_details:
            if dd.production_detail_id:
                dd_by_pd[int(dd.production_detail_id)] = dd
        for i, pkd in enumerate(pkd_list, 1):
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
            rolls = dd.qty_roll if dd else None
            pcs = dd.qty_pcs if dd else None
            nw = dd.weight if dd and dd.weight is not None else None
            gw = nw
            po_no = (poh.po_number or "").strip() if poh else ""
            remark_line = po_no
            if i - 1 < len(inv_details):
                idet = inv_details[i - 1]
                if idet.net_weight is not None:
                    nw = idet.net_weight
                if idet.gross_weight is not None:
                    gw = idet.gross_weight
                if (idet.remark or "").strip():
                    remark_line = (idet.remark or "").strip()
                elif not remark_line:
                    remark_line = po_no
            if gw is None:
                gw = nw
            line = _invpl_line_dict(
                no=i,
                pod=pod,
                poh=poh,
                master=master,
                qty=qty,
                rolls=rolls,
                pcs=pcs,
                nw=nw,
                gw=gw,
                remark_line=remark_line or po_no,
                is_export=is_export,
            )
            if line.pop("is_claim"):
                is_claim_order = True
            lines_out.append(line)
            total_qty += qty
            if line["amount"] is not None:
                total_amt += line["amount"]
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
    packing_number = ""
    if ph:
        packing_number = (ph.packing_number or str(ph.id)).strip()
    elif dh:
        packing_number = (dh.delivery_number or f"SJ-{dh.id}").strip()

    bank_name = (inv.bank_name or "").strip() if inv else ""
    account_number = (inv.account_number or "").strip() if inv else ""
    bank_address = (inv.bank_address or "").strip() if inv else ""
    bank_phone = (inv.bank_phone or "").strip() if inv else ""
    if not bank_name:
        bank_name = INVPL_BANK_DEFAULT["bank_name"]
        account_number = account_number or INVPL_BANK_DEFAULT["account_number"]
        bank_address = bank_address or INVPL_BANK_DEFAULT["bank_address"]
        bank_phone = bank_phone or INVPL_BANK_DEFAULT["bank_phone"]

    inv_raw = (inv.invoice_number or "").strip() if inv else ""
    ph_for_cat: PoHeader | None = None
    if delivery_details:
        _pod, _poh, _ = _pod_chain_from_delivery_detail(db, delivery_details[0])
        ph_for_cat = _poh
    invoice_no = invoice_display_number(inv_raw, ph_for_cat, doc_date=doc_date) if inv_raw else ""

    return {
        "packing_number": packing_number,
        "invoice_no": invoice_no,
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
        "bank_name": bank_name,
        "account_number": account_number,
        "bank_address": bank_address,
        "bank_phone": bank_phone,
        "description_line": INVPL_DESC_DEFAULT,
        "claim_title_suffix": " (Non)" if is_claim_order else "",
        "document_title": INVPL_TITLE,
    }


def gather_invpl_for_delivery(db: Session, delivery_id: int) -> dict[str, Any]:
    return gather_invpl_rows(db, packing_id=None, delivery_id=delivery_id)


CI_REASON_MESSAGES: dict[str, str] = {
    "delivery_not_found": "Delivery tidak ditemukan.",
    "no_packing": "Delivery belum terhubung ke packing — commercial invoice tidak tersedia.",
    "packing_not_found": "Packing tidak ditemukan.",
    "invpl_not_printed": "INVPL belum ditandai dicetak — commercial invoice hanya setelah INVPL.",
    "local_wait_h_plus_1": "Pengiriman dalam kota: commercial invoice baru boleh dicetak mulai H+1 tanggal kirim.",
    "outtown_wait_delivery_date": "Commercial invoice belum boleh dicetak sebelum tanggal pengiriman.",
}


def commercial_invoice_eligibility(db: Session, delivery_id: int) -> tuple[bool, str]:
    """Aturan cetak CI sejajar SJ: tidak wajib tandai INVPL; dalam kota H+1; luar kota mulai tanggal kirim."""
    from app.models import DeliveryDetail

    dh = db.get(DeliveryHeader, delivery_id)
    if not dh:
        return False, "delivery_not_found"
    details = list(
        db.scalars(select(DeliveryDetail).where(DeliveryDetail.delivery_id == delivery_id)).all()
    )
    pid = dh.packing_id
    if pid:
        ph = db.get(PackingHeader, int(pid))
        if not ph:
            return False, "packing_not_found"
    elif not details:
        return False, "no_packing"

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
    if not dh:
        raise ValueError("delivery_not_found")
    ctx = gather_invpl_for_delivery(db, delivery_id)
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
      <div><b>INV. NO:</b> {escape(ctx.get('invoice_no') or '—')}</div>
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
  <h2 class="title">{escape(ctx.get('document_title', INVPL_TITLE))}</h2>
  <div class="stars">*******************</div>
  <p class="desc">{escape(ctx['description_line'])}</p>
  <table class="grid"><thead>{thead}</thead><tbody>{rows_html}</tbody></table>
  <p class="words"><b>SAY TOTAL IN WORDS:</b> {escape(ctx['amount_in_words'])}</p>
  <div class="footer-bank">
    <div><b>TERM OF PAYMENT:</b> {escape(ctx['term_of_payment'] or '—')}</div>
    <div><b>OUR ADVISING BANK:</b> {escape(ctx['bank_name'] or '—')}</div>
    <div><b>ACCOUNT NO.:</b> {escape(ctx['account_number'] or '—')}</div>
    <div><b>BANK ADDRESS:</b> {escape(ctx['bank_address'] or '—')}</div>
    <div><b>BANK CONTACT:</b> {escape(ctx['bank_phone'] or '—')}</div>
  </div>
  <div class="sign">
    <p>Authorized signature:</p>
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
    small = ParagraphStyle(name="invpl_s", parent=styles["Normal"], fontSize=7, leading=9)
    center_small = ParagraphStyle(name="invpl_cs", parent=small, alignment=1)
    title_style = ParagraphStyle(
        name="invpl_t", parent=styles["Heading2"], alignment=1, fontSize=12, spaceAfter=2
    )
    story: list[Any] = []
    for line in COMPANY_BLOCK:
        story.append(Paragraph(f"<b>{escape(line)}</b>", center_small))
    story.append(Spacer(1, 2 * mm))
    meta = (
        f"<b>DATE:</b> {escape(ctx['doc_date_fmt'])} &nbsp;&nbsp; "
        f"<b>INV. NO:</b> {escape(ctx.get('invoice_no') or '—')}"
    )
    story.append(Paragraph(meta, ParagraphStyle("invpl_mr", parent=small, alignment=2)))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(f"<b>TO:</b> {escape(ctx['customer_name'])}", small))
    story.append(Paragraph(escape(ctx["customer_address"] or ""), small))
    story.append(Paragraph(escape(ctx["customer_phone_line"]), small))
    if ctx["is_export"] and ctx.get("bill_to_block"):
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"<b>BILL TO:</b> {escape(ctx['bill_to_block'])}", small))
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(escape(str(ctx.get("document_title", INVPL_TITLE))), title_style)
    )
    story.append(Paragraph("*******************", center_small))
    story.append(Paragraph(escape(ctx["description_line"]), small))
    story.append(Spacer(1, 2 * mm))

    is_export = ctx["is_export"]
    table_data: list[list[Any]] = []
    head = ["P.O. NO.", "ITEM"]
    if is_export:
        head.append("EXIM")
    head.extend(
        [
            "QTY",
            "UNIT",
            "U. PRICE (USD)",
            "AMOUNT (USD)",
            "ROLLS",
            "PIECES",
            "N.W. (KGS)",
            "G.W. (KGS)",
        ]
    )
    table_data.append(head)
    for ln in ctx["lines"]:
        item = (ln.get("item") or "")
        if ln.get("color"):
            item = f"{item} {ln['color']}".strip()
        row: list[Any] = [
            Paragraph(escape((ln["po_no"] or "")[:20]), small),
            Paragraph(escape(item[:90]), small),
        ]
        if is_export:
            row.append((ln.get("exim_code") or "")[:12])
        up = ln["unit_price"]
        am = ln["amount"]
        row.extend(
            [
                f"{ln['qty']:.2f}" if ln["qty"] is not None else "",
                ln["unit"] or "S/F",
                f"{up:.4f}" if up is not None else "",
                f"{am:.2f}" if am is not None else "",
                str(ln["rolls"] or ""),
                str(ln["pcs"] or ""),
                f"{ln['nw']:.1f}" if ln.get("nw") is not None else "",
                f"{ln['gw']:.1f}" if ln.get("gw") is not None else "",
            ]
        )
        table_data.append(row)

    t = ctx["totals"]
    total_row: list[Any] = ["TOTAL", ""]
    if is_export:
        total_row.append("")
    total_row.extend(
        [
            f"{t['qty']:.2f}",
            "",
            "",
            f"{t['amount']:.2f}",
            str(t["rolls"]),
            str(t["pcs"]),
            f"{t['nw']:.1f}" if t["nw"] else "",
            f"{t['gw']:.1f}" if t["gw"] else "",
        ]
    )
    table_data.append(total_row)

    col_count = len(table_data[0])
    full_w = landscape(A4)[0] - 24 * mm
    weights = [1.1, 3.2] + ([0.8] if is_export else []) + [0.8, 0.6, 1.1, 1.1, 0.7, 0.7, 0.8, 0.8]
    s = sum(weights[:col_count])
    cws = [full_w * (w / s) for w in weights[:col_count]]
    tbl = Table(table_data, colWidths=cws, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                ("FONTSIZE", (0, 0), (-1, -1), 6.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(f"<b>SAY TOTAL IN WORDS:</b> {escape(ctx['amount_in_words'])}", small))
    story.append(Paragraph(f"<b>TERM OF PAYMENT:</b> {escape(ctx['term_of_payment'] or '—')}", small))
    story.append(Paragraph(f"<b>OUR ADVISING BANK:</b> {escape(ctx['bank_name'] or '—')}", small))
    story.append(Paragraph(f"<b>ACCOUNT NO.:</b> {escape(ctx['account_number'] or '—')}", small))
    story.append(Paragraph(f"<b>BANK ADDRESS:</b> {escape(ctx['bank_address'] or '—')}", small))
    story.append(Paragraph(f"<b>BANK CONTACT:</b> {escape(ctx['bank_phone'] or '—')}", small))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Authorized signature:", small))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("<b>(CHIU PO HAO)</b>", small))
    story.append(Paragraph("Director", small))
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
        pod, poh, _master = _pod_chain_from_delivery_detail(db, dd)
        if ph_for_cat is None and poh is not None:
            ph_for_cat = poh
        # P.O. NO. = No. PO Customer (input manual SO); fallback nomor SO internal bila kosong.
        po_no = sj_po_no_from_header(poh)
        mat = _item_description(pod) if pod else "—"
        thick = _thickness_mm(pod) if pod else ""
        color = (pod.color or "").strip() if pod else ""
        emboss = (pod.emboss or "").strip() if pod else ""
        item = _sj_item_text(pod)
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
                "item": item,
                "material": mat,
                "thickness": thick,
                "emboss": emboss,
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

    tel, fax = _customer_tel_fax(cust)
    dn_raw = (dh.delivery_number or str(dh.id)).strip()
    inv_raw = (inv.invoice_number or "").strip() if inv else ""
    return {
        "delivery_number": surat_jalan_display_number(
            dn_raw, ph_for_cat, doc_date=dh.delivery_date
        )
        if dn_raw
        else "",
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
        "customer_tel": tel,
        "customer_fax": fax,
        "invoice_no": invoice_display_number(
            inv_raw, ph_for_cat, doc_date=inv.invoice_date if inv else dh.delivery_date
        )
        if inv_raw
        else "",
        "lines": lines_out,
        "totals": {"qty": t_qty, "rolls": t_roll, "pcs": t_pcs},
        "is_export": bool(cust and cust.is_export_customer),
    }


def _sj_body_rows(ctx: dict[str, Any], *, min_rows: int = 8) -> str:
    rows_html = ""
    lines = list(ctx.get("lines") or [])
    for ln in lines:
        item = ln.get("item") or ln.get("material") or ""
        rows_html += (
            f"<tr><td class='c'>{ln['no']}</td>"
            f"<td>{escape(str(item))}</td>"
            f"<td class='r'>{ln['qty']:.2f}</td>"
            f"<td class='r'>{ln['rolls'] or ''}</td>"
            f"<td class='r'>{ln['pcs'] or ''}</td>"
            f"<td>{escape(str(ln.get('po_no') or ''))}</td></tr>"
        )
    for _ in range(max(0, min_rows - len(lines))):
        rows_html += "<tr>" + "".join("<td>&nbsp;</td>" for _ in range(6)) + "</tr>"
    t = ctx["totals"]
    rows_html += (
        f"<tr class='total'><td colspan='2'><b>TOTAL</b></td>"
        f"<td class='r'><b>{t['qty']:.2f}</b></td>"
        f"<td class='r'><b>{t['rolls']}</b></td>"
        f"<td class='r'><b>{t['pcs']}</b></td><td></td></tr>"
    )
    return rows_html


def _sj_qr_png_bytes(payload: str, *, box_size: int = 4, border: int = 1) -> bytes:
    """PNG QR untuk nomor surat jalan (scan-out di Delivery)."""
    code = (payload or "").strip()
    if not code:
        return b""
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=box_size, border=border)
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _sj_qr_data_uri(payload: str) -> str:
    raw = _sj_qr_png_bytes(payload)
    if not raw:
        return ""
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def _sj_meta_html(ctx: dict[str, Any]) -> str:
    addr = escape(ctx.get("customer_address") or "").replace("\n", "<br/>")
    tel = escape(ctx.get("customer_tel") or "")
    fax = escape(ctx.get("customer_fax") or "")
    sj_no = (ctx.get("delivery_number") or "").strip()
    qr_uri = _sj_qr_data_uri(sj_no)
    qr_html = (
        f'<div class="meta-sj-qr"><img src="{qr_uri}" alt="QR {escape(sj_no)}" width="78" height="78"/></div>'
        if qr_uri
        else ""
    )
    return f"""
  <div class="grid-2">
    <div class="meta-box">
      <div><b>DELIVERY TO:</b> {escape(ctx['customer_name'])}</div>
      <div><b>ADDRESS:</b> {addr}</div>
      <div><b>TELP. NO.:</b> {tel or '—'}</div>
      <div><b>FAX. NO.:</b> {fax or '—'}</div>
      <div><b>INV. NO.:</b> {escape(ctx.get('invoice_no') or '—')}</div>
    </div>
    <div class="meta-box meta-box--sj">
      <div class="meta-sj-row">
        <div class="meta-sj-fields">
          <div><b>SURAT JALAN NO:</b> {escape(sj_no)}</div>
          <div><b>BC NO.:</b> {escape(ctx.get('bc_number') or '')}</div>
          <div><b>TANGGAL (Date):</b> {escape(ctx['delivery_date_fmt'])}</div>
          <div><b>CAR NO.:</b> {escape(ctx.get('vehicle_number') or '')}</div>
          <div><b>DRIVER'S NAME:</b> {escape(ctx.get('driver_name') or '')}</div>
        </div>
        {qr_html}
      </div>
    </div>
  </div>
"""


_SJ_TABLE_HEAD = (
    "<thead><tr>"
    "<th>NO.</th><th>ITEM</th><th>QTY (S/F)</th><th>ROLLS</th><th>PIECES</th><th>P.O. NO.</th>"
    "</tr></thead>"
)


def render_sj_html(ctx: dict[str, Any]) -> str:
    company = "<br/>".join(escape(x) for x in COMPANY_BLOCK)
    export_note = ""
    if ctx.get("is_export"):
        export_note = (
            '<p class="note">'
            + escape("Catatan: untuk transaksi ekspor, cetak Surat Jalan bersifat opsional.")
            + "</p>"
        )
    body = f"""
<div class="doc">
  <div class="company"><b>{company}</b></div>
  <h2 class="title">SURAT JALAN (DELIVERY SHEET)</h2>
  {export_note}
  {_sj_meta_html(ctx)}
  <table class="grid">{_SJ_TABLE_HEAD}<tbody>{_sj_body_rows(ctx)}</tbody></table>
  {_sign4_html()}
  <p class="foot-note"><b>NOTE :</b> WHITE(1) ACC, RED(2) CUSTOMER, YELLOW(3) EXIM, GREEN(4) WAREHOUSE, BLUE(5) SECURITY.</p>
</div>
"""
    style = """
    body { font-family: Arial, Helvetica, sans-serif; margin: 14px; font-size: 11px; color: #111; }
    .doc { max-width: 820px; margin: 0 auto; border: 1px solid #333; padding: 12px; }
    .company { text-align: center; margin-bottom: 8px; line-height: 1.35; }
    .title { text-align: center; font-size: 15px; margin: 8px 0 12px; letter-spacing: 0.5px; }
    .note { font-size: 10px; color: #444; margin: 6px 0; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0; margin: 0 0 10px; border: 1px solid #333; }
    .meta-box { padding: 8px 10px; line-height: 1.45; border-right: 1px solid #333; }
    .meta-box:last-child { border-right: none; }
    .meta-sj-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
    .meta-sj-fields { flex: 1 1 auto; min-width: 0; }
    .meta-sj-qr { flex: 0 0 auto; margin-left: auto; text-align: right; }
    .meta-sj-qr img { width: 78px; height: 78px; display: block; image-rendering: pixelated; }
    table.grid { width: 100%; border-collapse: collapse; margin-top: 0; font-size: 10px; }
    table.grid th, table.grid td { border: 1px solid #333; padding: 5px 4px; vertical-align: top; }
    table.grid th { background: #f0f0f0; text-align: center; }
    td.r { text-align: right; }
    td.c { text-align: center; }
    tr.total td { background: #f5f5f5; font-weight: bold; }
    .sign4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0; margin-top: 0; border: 1px solid #333; border-top: none; }
    .sign-box { text-align: center; font-size: 10px; padding: 8px 4px 12px; border-right: 1px solid #333; min-height: 72px; }
    .sign-box:last-child { border-right: none; }
    .sign-line { margin-top: 8px; font-size: 9px; }
    .foot-note { margin-top: 10px; font-size: 9px; }
    @media print { body { margin: 8px; } .doc { border: none; padding: 0; } }
    """
    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"/><title>Surat Jalan</title>
<style>{style}</style></head><body>{body}</body></html>"""


def render_sj_pdf(ctx: dict[str, Any]) -> bytes:
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
    small = ParagraphStyle(name="sj_s", parent=styles["Normal"], fontSize=8, leading=10)
    center = ParagraphStyle(name="sj_c", parent=small, alignment=1)
    title = ParagraphStyle(name="sj_t", parent=styles["Heading2"], alignment=1, fontSize=12, spaceAfter=6)
    story: list[Any] = []
    for line in COMPANY_BLOCK:
        story.append(Paragraph(f"<b>{escape(line)}</b>", center))
    story.append(Paragraph("SURAT JALAN (DELIVERY SHEET)", title))

    left = (
        f"<b>DELIVERY TO:</b> {escape(ctx['customer_name'])}<br/>"
        f"<b>ADDRESS:</b> {escape(ctx.get('customer_address') or '')}<br/>"
        f"<b>TELP. NO.:</b> {escape(ctx.get('customer_tel') or '—')}<br/>"
        f"<b>FAX. NO.:</b> {escape(ctx.get('customer_fax') or '—')}<br/>"
        f"<b>INV. NO.:</b> {escape(ctx.get('invoice_no') or '—')}"
    )
    sj_no = (ctx.get("delivery_number") or "").strip()
    right_text = (
        f"<b>SURAT JALAN NO:</b> {escape(sj_no)}<br/>"
        f"<b>BC NO.:</b> {escape(ctx.get('bc_number') or '')}<br/>"
        f"<b>TANGGAL (Date):</b> {escape(ctx['delivery_date_fmt'])}<br/>"
        f"<b>CAR NO.:</b> {escape(ctx.get('vehicle_number') or '')}<br/>"
        f"<b>DRIVER'S NAME:</b> {escape(ctx.get('driver_name') or '')}"
    )
    right_cell: Any = Paragraph(right_text, small)
    qr_png = _sj_qr_png_bytes(sj_no)
    if qr_png:
        qr_img = RLImage(io.BytesIO(qr_png), width=22 * mm, height=22 * mm)
        right_inner = Table(
            [[Paragraph(right_text, small), qr_img]],
            colWidths=[62 * mm, 24 * mm],
        )
        right_inner.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        right_cell = right_inner
    meta = Table(
        [[Paragraph(left, small), right_cell]],
        colWidths=[90 * mm, 90 * mm],
    )
    meta.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(meta)
    story.append(Spacer(1, 2 * mm))

    data: list[list[Any]] = [["NO.", "ITEM", "QTY (S/F)", "ROLLS", "PIECES", "P.O. NO."]]
    lines = list(ctx.get("lines") or [])
    for ln in lines:
        item = ln.get("item") or ln.get("material") or ""
        data.append(
            [
                str(ln["no"]),
                Paragraph(escape(str(item)[:120]), small),
                f"{ln['qty']:.2f}",
                str(ln["rolls"] or ""),
                str(ln["pcs"] or ""),
                Paragraph(escape(str(ln.get("po_no") or "")[:24]), small),
            ]
        )
    for _ in range(max(0, 8 - len(lines))):
        data.append(["", "", "", "", "", ""])
    t = ctx["totals"]
    data.append(["", "TOTAL", f"{t['qty']:.2f}", str(t["rolls"]), str(t["pcs"]), ""])
    page_w = A4[0] - 28 * mm
    cws = [page_w * x for x in (0.07, 0.42, 0.14, 0.11, 0.11, 0.15)]
    tbl = Table(data, colWidths=cws, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (4, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(tbl)

    sign_cells = []
    for lab in SJ_SIGN_LABELS:
        sign_cells.append(
            Paragraph(f"<b>{lab}</b><br/><br/><br/><br/>( &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; )", center)
        )
    sign = Table([sign_cells], colWidths=[page_w / 4] * 4)
    sign.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(sign)
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "<b>NOTE :</b> WHITE(1) ACC, RED(2) CUSTOMER, YELLOW(3) EXIM, GREEN(4) WAREHOUSE, BLUE(5) SECURITY.",
            ParagraphStyle("sj_n", parent=small, fontSize=7),
        )
    )
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def render_sj_dotmatrix_html(ctx: dict[str, Any]) -> str:
    """Cetak fisik dot matrix — layout mengikuti form SURAT JALAN."""
    company = "<br/>".join(escape(x) for x in COMPANY_BLOCK)
    body = f"""
<div class="doc">
  <div class="company"><b>{company}</b></div>
  <h2 class="title">SURAT JALAN (DELIVERY SHEET)</h2>
  {_sj_meta_html(ctx)}
  <table class="grid">{_SJ_TABLE_HEAD}<tbody>{_sj_body_rows(ctx, min_rows=10)}</tbody></table>
  {_sign4_html(compact=True)}
  <p class="foot-note"><b>NOTE:</b> WHITE(1) ACC, RED(2) CUSTOMER, YELLOW(3) EXIM, GREEN(4) WAREHOUSE, BLUE(5) SECURITY.</p>
</div>
"""
    style = """
    @page { size: A4 portrait; margin: 0.35in; }
    body { font-family: 'Courier New', Courier, monospace; margin: 0; font-size: 9px; color: #000; }
    .doc { width: 100%; max-width: 190mm; margin: 0 auto; }
    .company { text-align: center; font-size: 9px; line-height: 1.25; margin-bottom: 4px; }
    .title { text-align: center; font-size: 12px; margin: 6px 0 8px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0; margin: 0 0 6px; border: 1px solid #000; }
    .meta-box { padding: 4px 6px; line-height: 1.35; border-right: 1px solid #000; font-size: 8px; }
    .meta-box:last-child { border-right: none; }
    .meta-sj-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 6px; }
    .meta-sj-fields { flex: 1 1 auto; min-width: 0; }
    .meta-sj-qr { flex: 0 0 auto; margin-left: auto; text-align: right; }
    .meta-sj-qr img { width: 64px; height: 64px; display: block; image-rendering: pixelated; }
    table.grid { width: 100%; border-collapse: collapse; font-size: 8px; }
    table.grid th, table.grid td { border: 1px solid #000; padding: 2px 3px; vertical-align: top; }
    table.grid th { text-align: center; }
    td.r { text-align: right; }
    td.c { text-align: center; }
    tr.total td { font-weight: bold; }
    .sign4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0; border: 1px solid #000; border-top: none; }
    .sign-box { text-align: center; font-size: 7px; padding: 6px 2px 10px; border-right: 1px solid #000; min-height: 48px; }
    .sign-box:last-child { border-right: none; }
    .sign-line { margin-top: 4px; }
    .foot-note { margin-top: 6px; font-size: 7px; }
    @media print { body { margin: 0; } }
    """
    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"/><title>Surat Jalan Dot Matrix</title>
<style>{style}</style></head><body>{body}
<script>window.onload=function(){{window.print();}}</script></body></html>"""

