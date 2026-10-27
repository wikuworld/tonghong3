"""Konteks & render INVPL / Surat Jalan sesuai format marketing (Tong Hong)."""

from __future__ import annotations

import base64
import io
from datetime import date, timedelta
from decimal import Decimal
from html import escape
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
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

# Logo letterhead (sama Sales Contract)
_LOGO_PATH = Path(__file__).resolve().parents[3] / "frontend" / "public" / "logo-tonghong.png"
_LOGO_ASPECT = 127 / 258
_LOGO_WIDTH_MM = 22
# Sama packing list FG: NW = qty(SF)×0,11 ; GW = NW + rolls×0,3
_NW_PER_SF = Decimal("0.11")
_GW_PER_ROLL = Decimal("0.3")


def _logo_bytes() -> bytes | None:
    try:
        data = _LOGO_PATH.read_bytes()
    except OSError:
        return None
    return data or None


def _logo_data_uri() -> str:
    raw = _logo_bytes()
    if not raw:
        return ""
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def packing_derived_weights(
    *,
    qty: Decimal | float | int | None = None,
    rolls: int | None = None,
    weight_net: Decimal | float | int | None = None,
    weight_gross: Decimal | float | int | None = None,
) -> tuple[Decimal | None, Decimal | None]:
    """N.W / G.W dari packing. Fallback: NW=qty×0.11, GW=NW+rolls×0.3."""
    nw = Decimal(str(weight_net)) if weight_net is not None else None
    gw = Decimal(str(weight_gross)) if weight_gross is not None else None
    q = Decimal(str(qty)) if qty is not None else Decimal(0)
    r = int(rolls or 0)
    if nw is None:
        nw = (q * _NW_PER_SF).quantize(Decimal("0.01"))
    if gw is None:
        gw = (nw + Decimal(r) * _GW_PER_ROLL).quantize(Decimal("0.01"))
    return nw, gw


def _packing_detail_for_delivery_line(
    db: Session, dd: DeliveryDetail, ph: PackingHeader | None
) -> PackingDetail | None:
    if getattr(dd, "packing_detail_id", None):
        pkd = db.get(PackingDetail, int(dd.packing_detail_id))
        if pkd:
            return pkd
    if ph and getattr(dd, "production_detail_id", None):
        return db.scalars(
            select(PackingDetail)
            .where(
                PackingDetail.packing_id == ph.id,
                PackingDetail.production_detail_id == int(dd.production_detail_id),
            )
            .limit(1)
        ).first()
    return None


def _fetch_mrp_packing_nw_gw(ph: PackingHeader | None) -> tuple[Decimal | None, Decimal | None]:
    """Return (net_weight, gross_weight) dari header packing MRP bila ada."""
    mid = getattr(ph, "mrp_packing_id", None) if ph else None
    if not mid:
        return None, None
    try:
        from app.services.delivery_customs_bc27_xlsx import fetch_mrp_packing_weights

        gw, nw = fetch_mrp_packing_weights(int(mid))
        return nw, gw
    except Exception:  # noqa: BLE001 — jangan gagalkan cetak INVPL
        return None, None


def _distribute_header_weights(
    lines: list[dict[str, Any]],
    header_nw: Decimal | None,
    header_gw: Decimal | None,
) -> None:
    """Sebar N.W/G.W header packing ke baris menurut proporsi qty (jika belum ada berat packing per baris)."""
    if header_nw is None and header_gw is None:
        return
    if not lines:
        return
    has_packing_line = any(bool(ln.get("_from_packing")) for ln in lines)
    for ln in lines:
        ln.pop("_from_packing", None)
    if has_packing_line:
        return
    total_qty = sum((_dec(ln.get("qty")) for ln in lines), Decimal(0))
    if total_qty <= 0:
        n = len(lines)
        share_nw = (header_nw / n).quantize(Decimal("0.01")) if header_nw is not None else None
        share_gw = (header_gw / n).quantize(Decimal("0.01")) if header_gw is not None else None
        for ln in lines:
            if header_nw is not None:
                ln["nw"] = share_nw
            if header_gw is not None:
                ln["gw"] = share_gw
        return
    allocated_nw = Decimal(0)
    allocated_gw = Decimal(0)
    for i, ln in enumerate(lines):
        last = i == len(lines) - 1
        ratio = _dec(ln.get("qty")) / total_qty
        if header_nw is not None:
            if last:
                ln["nw"] = (header_nw - allocated_nw).quantize(Decimal("0.01"))
            else:
                part = (header_nw * ratio).quantize(Decimal("0.01"))
                ln["nw"] = part
                allocated_nw += part
        if header_gw is not None:
            if last:
                ln["gw"] = (header_gw - allocated_gw).quantize(Decimal("0.01"))
            else:
                part = (header_gw * ratio).quantize(Decimal("0.01"))
                ln["gw"] = part
                allocated_gw += part

INVPL_DESC_DEFAULT = "DESCRIPTION: SHOE MAKING MATERIAL (COW LEATHER)"
INVPL_TITLE = "INVOICE PACKING LIST"
INVPL_TITLE_FOC = "INVOICE PACKING LIST (FOC)"
SJ_TITLE = "SURAT JALAN (DELIVERY SHEET)"
SJ_TITLE_FOC = "SURAT JALAN (DELIVERY SHEET) (FOC)"


def invpl_document_title(*, foc: bool = False) -> str:
    return INVPL_TITLE_FOC if foc else INVPL_TITLE


def sj_document_title(ctx: dict[str, Any] | None = None, *, foc: bool = False) -> str:
    on = foc or bool((ctx or {}).get("is_foc"))
    return SJ_TITLE_FOC if on else SJ_TITLE


def apply_invpl_foc_title(ctx: dict[str, Any], foc: bool = False) -> dict[str, Any]:
    """Salin ctx dan set judul INVPL (+ FOC bila diminta). Tidak mengubah commercial invoice."""
    out = dict(ctx)
    out["foc"] = bool(foc)
    out["document_title"] = invpl_document_title(foc=bool(foc))
    return out


# Fallback bank INVPL (sama teks ringkas Proforma) bila invoice belum diisi.
INVPL_BANK_DEFAULT = {
    "bank_name": "BANK CTBC INDONESIA",
    "account_number": "(USD) 2020357701",
    "bank_address": "TAMARA CENTER 16TH FLOOR, JL. JENDERAL SUDIRMAN KAV. 24 JAKARTA",
    "bank_phone": "021-5237788/7245",
    "bank_fax": "021-2500622",
}

# Margin cetak A4 (aman printer; selaras HTML @page & PDF SimpleDocTemplate)
INVPL_MARGIN_LR_MM = 12
INVPL_MARGIN_TB_MM = 10

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
    """ITEM SJ/INVPL: thickness + material + emboss + color (satu sel)."""
    if not pod:
        return "—"
    parts: list[str] = []
    th = _thickness_mm(pod)
    mat = (getattr(pod, "material_name", None) or "").strip()
    emb = (getattr(pod, "emboss", None) or "").strip()
    color = (getattr(pod, "color", None) or "").strip()
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


def _invpl_bank_tel_fax(ctx: dict[str, Any]) -> tuple[str, str]:
    """TELP / FAX bank untuk footer INVPL (template Excel)."""
    tel = (ctx.get("bank_phone") or "").strip()
    fax = (ctx.get("bank_fax") or "").strip()
    if fax:
        return tel, fax
    # Legacy: "… / …, Fax : …" atau "… Fax : …"
    low = tel.lower()
    if "fax" in low:
        parts = tel.split(",", 1) if "," in tel else None
        if parts and "fax" in parts[1].lower():
            left, right = parts[0].strip(), parts[1]
            idx = right.lower().find("fax")
            fax_part = right[idx:].split(":", 1)[-1].strip() if idx >= 0 else ""
            return left, fax_part
        idx = low.find("fax")
        return tel[:idx].rstrip(" ,;"), tel[idx:].split(":", 1)[-1].strip()
    return tel, fax or INVPL_BANK_DEFAULT.get("bank_fax", "")


def _invpl_account_display(account: str | None) -> str:
    """Normalisasi tampilan ACCOUNT NO. → '(USD) 2020357701'."""
    raw = (account or "").strip()
    if not raw:
        return "—"
    if raw.upper().startswith("(USD)"):
        return raw
    if raw.upper().endswith("(USD)"):
        num = raw[: -len("(USD)")].strip()
        return f"(USD) {num}" if num else raw
    return raw


def _invpl_item_text(ln: dict[str, Any]) -> str:
    """ITEM cetak: deskripsi lengkap; EXIM digabung bila ada (export)."""
    base = (ln.get("item") or "").strip()
    color = (ln.get("color") or "").strip()
    # Data lama: item tanpa warna → append COLOR bila belum tercakup
    if color and color.upper() not in base.upper():
        base = f"{base} {color}".strip() if base else color
    exim = (ln.get("exim_code") or "").strip()
    if exim:
        base = f"{base} [{exim}]".strip() if base else exim
    return base or "—"


def _fmt_invpl_qty(v: Decimal | float | int | None) -> str:
    if v is None:
        return ""
    d = Decimal(str(v)).quantize(Decimal("0.01"))
    return f"{d:,.2f}"


def _fmt_invpl_money(v: Decimal | float | int | None, *, places: int = 2) -> str:
    if v is None:
        return ""
    q = Decimal(1).scaleb(-places)
    d = Decimal(str(v)).quantize(q)
    return f"{d:,.{places}f}"


def _fmt_invpl_int(v: int | None) -> str:
    if v is None:
        return ""
    return f"{int(v):,}"


def _fmt_invpl_weight(v: Decimal | float | int | None) -> str:
    if v is None:
        return ""
    d = Decimal(str(v)).quantize(Decimal("0.1"))
    return f"{d:,.1f}"


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
    """P.O. NO. di Surat Jalan / INVPL = No. PO Customer (bukan No. SO).

    Hanya mapping cetak; tidak mengubah po_customer_ref / po_number di DB.
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
    # Sama seperti Surat Jalan: kolom PO NO ← po_customer_ref.
    po_no = sj_po_no_from_header(poh)
    exim = ""
    if is_export and master and (master.exim_material_code or "").strip():
        exim = master.exim_material_code.strip()
    return {
        "no": no,
        "po_no": po_no,
        # Template Excel: ITEM = thickness + material + emboss + color (satu sel)
        "item": _sj_item_text(pod) if pod else "—",
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
    mrp_nw, mrp_gw = _fetch_mrp_packing_nw_gw(ph)

    delivery_details: list[DeliveryDetail] = []
    if dh:
        delivery_details = list(
            db.scalars(
                select(DeliveryDetail)
                .where(DeliveryDetail.delivery_id == dh.id)
                .order_by(DeliveryDetail.id.asc())
            ).all()
        )

    def _resolve_line_weights(
        *,
        qty: Decimal,
        rolls,
        pkd: PackingDetail | None,
        dd: DeliveryDetail | None,
        inv_idx: int,
    ) -> tuple[Decimal | None, Decimal | None, bool]:
        """Priority: packing weight_net → delivery.weight → formula; GW dari packing/formula."""
        from_packing = bool(pkd and pkd.weight_net is not None)
        weight_net = pkd.weight_net if from_packing else None
        if weight_net is None and dd is not None and dd.weight is not None:
            weight_net = dd.weight
        weight_gross = None
        inv_nw = inv_gw = None
        if 0 <= inv_idx < len(inv_details):
            idet = inv_details[inv_idx]
            if idet.net_weight is not None:
                inv_nw = idet.net_weight
            if idet.gross_weight is not None:
                inv_gw = idet.gross_weight
        # Invoice override hanya jika sudah terisi; packing tetap sumber utama bila invoice kosong
        seed_nw = inv_nw if inv_nw is not None else weight_net
        seed_gw = inv_gw if inv_gw is not None else weight_gross
        nw, gw = packing_derived_weights(
            qty=qty, rolls=rolls, weight_net=seed_nw, weight_gross=seed_gw
        )
        return nw, gw, from_packing

    if delivery_details:
        for i, dd in enumerate(delivery_details, 1):
            pod, poh, master = _pod_chain_from_delivery_detail(db, dd)
            qty = _dec(dd.qty)
            rolls = dd.qty_roll
            pcs = dd.qty_pcs
            pkd = _packing_detail_for_delivery_line(db, dd, ph)
            if rolls is None and pkd is not None and pkd.qty_roll is not None:
                rolls = pkd.qty_roll
            if pcs is None and pkd is not None and pkd.qty_pcs is not None:
                pcs = pkd.qty_pcs
            nw, gw, from_packing = _resolve_line_weights(
                qty=qty, rolls=rolls, pkd=pkd, dd=dd, inv_idx=i - 1
            )
            po_no = sj_po_no_from_header(poh)
            remark_line = po_no
            if i - 1 < len(inv_details):
                idet = inv_details[i - 1]
                if (idet.remark or "").strip():
                    remark_line = (idet.remark or "").strip()
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
            line["_from_packing"] = from_packing
            lines_out.append(line)
            total_qty += qty
            if line["amount"] is not None:
                total_amt += line["amount"]
            total_roll += int(rolls or 0)
            total_pcs += int(pcs or 0)
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
            rolls = dd.qty_roll if dd and dd.qty_roll is not None else pkd.qty_roll
            pcs = dd.qty_pcs if dd and dd.qty_pcs is not None else pkd.qty_pcs
            nw, gw, from_packing = _resolve_line_weights(
                qty=qty, rolls=rolls, pkd=pkd, dd=dd, inv_idx=i - 1
            )
            po_no = sj_po_no_from_header(poh)
            remark_line = po_no
            if i - 1 < len(inv_details):
                idet = inv_details[i - 1]
                if (idet.remark or "").strip():
                    remark_line = (idet.remark or "").strip()
                elif not remark_line:
                    remark_line = po_no
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
            line["_from_packing"] = from_packing
            lines_out.append(line)
            total_qty += qty
            if line["amount"] is not None:
                total_amt += line["amount"]
            total_roll += int(rolls or 0)
            total_pcs += int(pcs or 0)

    _distribute_header_weights(lines_out, mrp_nw, mrp_gw)
    for ln in lines_out:
        if ln.get("nw") is not None:
            total_nw += _dec(ln["nw"])
        if ln.get("gw") is not None:
            total_gw += _dec(ln["gw"])

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
    bank_fax = ""
    if not bank_name:
        bank_name = INVPL_BANK_DEFAULT["bank_name"]
        account_number = account_number or INVPL_BANK_DEFAULT["account_number"]
        bank_address = bank_address or INVPL_BANK_DEFAULT["bank_address"]
        bank_phone = bank_phone or INVPL_BANK_DEFAULT["bank_phone"]
        bank_fax = INVPL_BANK_DEFAULT.get("bank_fax", "")
    if not account_number:
        account_number = INVPL_BANK_DEFAULT["account_number"]

    inv_raw = (inv.invoice_number or "").strip() if inv else ""
    ph_for_cat: PoHeader | None = None
    if delivery_details:
        _pod, _poh, _ = _pod_chain_from_delivery_detail(db, delivery_details[0])
        ph_for_cat = _poh
    invoice_no = invoice_display_number(inv_raw, ph_for_cat, doc_date=doc_date) if inv_raw else ""

    cust_tel, cust_fax = _customer_tel_fax(cust)

    return {
        "packing_number": packing_number,
        "invoice_no": invoice_no,
        "doc_date": doc_date,
        "doc_date_fmt": _fmt_date_en(doc_date),
        "customer_name": cust_name,
        "customer_address": cust_addr,
        "customer_phone_line": _customer_phone_fax(cust),
        "customer_tel": cust_tel,
        "customer_fax": cust_fax,
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
        "bank_fax": bank_fax,
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
    """Cetak INVPL / Commercial Invoice — layout template Excel Tong Hong, A4."""
    bill_html = ""
    if ctx.get("is_export") and ctx.get("bill_to_block"):
        bill_html = (
            f'<div class="billto"><b>BILL TO:</b><br/>'
            f'{escape(ctx["bill_to_block"]).replace(chr(10), "<br/>")}</div>'
        )

    # Kolom sesuai template Excel (COLOR/REMARK digabung ke ITEM)
    cols = [
        "P.O. NO.",
        "ITEM",
        "QTY",
        "UNIT",
        "U. PRICE (USD)",
        "AMOUNT (USD)",
        "ROLLS",
        "PIECES",
        "N.W. (KGS)",
        "G.W. (KGS)",
    ]
    thead = "<tr>" + "".join(f"<th>{escape(c)}</th>" for c in cols) + "</tr>"
    rows_html = ""
    for ln in ctx["lines"]:
        cells = [
            escape(ln.get("po_no") or ""),
            escape(_invpl_item_text(ln)),
            _fmt_invpl_qty(ln.get("qty")),
            escape(ln.get("unit") or "S/F"),
            _fmt_invpl_money(ln.get("unit_price"), places=2),
            _fmt_invpl_money(ln.get("amount"), places=2),
            _fmt_invpl_int(ln.get("rolls")),
            _fmt_invpl_int(ln.get("pcs")),
            _fmt_invpl_weight(ln.get("nw")),
            _fmt_invpl_weight(ln.get("gw")),
        ]
        rows_html += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"

    t = ctx["totals"]
    foot = [
        "TOTAL",
        "",
        _fmt_invpl_qty(t.get("qty")),
        "",
        "",
        _fmt_invpl_money(t.get("amount"), places=2),
        _fmt_invpl_int(t.get("rolls")),
        _fmt_invpl_int(t.get("pcs")),
        _fmt_invpl_weight(t.get("nw")) if t.get("nw") else "",
        _fmt_invpl_weight(t.get("gw")) if t.get("gw") else "",
    ]
    rows_html += (
        "<tr class='total'>"
        + "".join(f"<td><b>{escape(str(x))}</b></td>" for x in foot)
        + "</tr>"
    )

    cust_tel = (ctx.get("customer_tel") or "").strip()
    cust_fax = (ctx.get("customer_fax") or "").strip()
    if not cust_tel and ctx.get("customer_phone_line"):
        # Fallback konteks lama: "TELP. NO. : …"
        raw = str(ctx["customer_phone_line"])
        cust_tel = raw.split(":", 1)[-1].strip() if ":" in raw else raw
    tel_line = f"TELP. NO.: {escape(cust_tel)}" if cust_tel else "TELP. NO.:"
    fax_line = f"FAX. NO.: {escape(cust_fax)}" if cust_fax else "FAX. NO.:"

    bank_tel, bank_fax = _invpl_bank_tel_fax(ctx)
    account_disp = _invpl_account_display(ctx.get("account_number"))

    company_html = "<br/>".join(escape(x) for x in COMPANY_BLOCK)
    logo_uri = _logo_data_uri()
    logo_html = (
        f'<div class="logo"><img src="{logo_uri}" alt="Tong Hong Tannery"/></div>'
        if logo_uri
        else '<div class="logo"></div>'
    )
    body = f"""
<div class="doc">
  <div class="letterhead">
    {logo_html}
    <div class="company"><b>{company_html}</b></div>
  </div>
  <div class="rule"></div>
  <div class="to-meta">
    <div class="to-block">
      <div><b>TO:</b></div>
      <div class="to-name">{escape(ctx['customer_name'])}</div>
      <div class="addr">{escape(ctx.get('customer_address') or '').replace(chr(10), '<br/>')}</div>
      <div>{tel_line}</div>
      <div>{fax_line}</div>
    </div>
    <div class="meta-right">
      <div><b>DATE:</b> {escape(ctx['doc_date_fmt'])}</div>
      <div><b>INV. NO:</b> {escape(ctx.get('invoice_no') or '—')}</div>
    </div>
  </div>
  {bill_html}
  <h2 class="title">{escape(ctx.get('document_title', INVPL_TITLE))}</h2>
  <div class="stars">****************************************</div>
  <p class="desc">{escape(ctx.get('description_line') or INVPL_DESC_DEFAULT)}</p>
  <table class="grid"><thead>{thead}</thead><tbody>{rows_html}</tbody></table>
  <p class="words"><b>SAY TOTAL IN WORDS:</b> {escape(ctx['amount_in_words'])}</p>
  <div class="footer-bank">
    <div><b>TERM OF PAYMENT:</b> {escape(ctx.get('term_of_payment') or '—')}</div>
    <div><b>BANK:</b> {escape(ctx.get('bank_name') or '—')}</div>
    <div><b>ACCOUNT NO.:</b> {escape(account_disp)}</div>
    <div><b>BANK ADDRESS:</b> {escape(ctx.get('bank_address') or '—')}</div>
    <div><b>TELP. NO:</b> {escape(bank_tel or '—')}</div>
    <div><b>FAX. NO:</b> {escape(bank_fax or '—')}</div>
  </div>
  <div class="sign">
    <p><b>AUTHORIZED SIGNATURE</b></p>
    <p class="sign-space">&nbsp;</p>
    <p><b>(CHIU PO HAO)</b></p>
    <p>Director</p>
  </div>
</div>
"""
    lr = INVPL_MARGIN_LR_MM
    tb = INVPL_MARGIN_TB_MM
    style = f"""
    @page {{ size: A4 portrait; margin: {tb}mm {lr}mm; }}
    body {{
      font-family: Arial, Helvetica, sans-serif;
      margin: 0;
      color: #111;
      font-size: 10px;
    }}
    .doc {{ width: 100%; max-width: 186mm; margin: 0 auto; }}
    .letterhead {{
      display: grid;
      grid-template-columns: 26mm 1fr;
      align-items: center;
      gap: 6px;
      margin-bottom: 4px;
    }}
    .logo img {{ width: 22mm; height: auto; display: block; }}
    .company {{ text-align: center; font-size: 10.5px; line-height: 1.35; }}
    .rule {{ border-top: 2.2px solid #000; margin: 4px 0 8px; }}
    .to-meta {{
      display: grid;
      grid-template-columns: 1fr 48mm;
      gap: 8px;
      align-items: start;
      margin-bottom: 6px;
    }}
    .to-name {{ font-weight: bold; margin-top: 2px; }}
    .addr {{ margin: 3px 0; white-space: pre-wrap; }}
    .meta-right {{ text-align: right; font-size: 10px; line-height: 1.5; }}
    .billto {{ margin: 6px 0; padding: 5px; border: 1px solid #333; }}
    .title {{
      text-align: center;
      margin: 10px 0 2px;
      font-size: 14px;
      font-weight: bold;
      letter-spacing: 0.5px;
    }}
    .stars {{ text-align: center; letter-spacing: 1px; margin-bottom: 6px; font-size: 9px; }}
    .desc {{ font-weight: bold; margin: 4px 0 6px; font-size: 10px; }}
    table.grid {{
      border-collapse: collapse;
      width: 100%;
      margin-top: 2px;
      font-size: 7.5px;
      table-layout: fixed;
    }}
    table.grid th, table.grid td {{
      border: 1px solid #222;
      padding: 3px 2px;
      vertical-align: top;
      word-wrap: break-word;
    }}
    table.grid th {{ background: #ececec; font-size: 7px; text-align: center; }}
    table.grid td:nth-child(3),
    table.grid td:nth-child(5),
    table.grid td:nth-child(6),
    table.grid td:nth-child(7),
    table.grid td:nth-child(8),
    table.grid td:nth-child(9),
    table.grid td:nth-child(10) {{ text-align: right; }}
    table.grid td:nth-child(4) {{ text-align: center; }}
    tr.total td {{ background: #f3f3f3; }}
    .words {{ margin-top: 8px; font-size: 9px; }}
    .footer-bank {{ margin-top: 8px; line-height: 1.5; font-size: 9px; }}
    .sign {{ margin-top: 18px; text-align: left; font-size: 9px; }}
    .sign-space {{ height: 14mm; }}
    @media print {{
      body {{ margin: 0; }}
      .doc {{ max-width: none; width: 100%; }}
    }}
    """
    doc_title = str(ctx.get("document_title", "INVPL"))
    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"/><title>{escape(doc_title)}</title>
<style>{style}</style></head><body>{body}</body></html>"""


def render_invpl_xlsx(ctx: dict[str, Any]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "INVPL"
    for line in COMPANY_BLOCK:
        ws.append([line])
    ws.append([])
    ws.append(["TO", ctx["customer_name"]])
    for part in (ctx.get("customer_address") or "").split("\n"):
        if part.strip():
            ws.append(["", part.strip()])
    cust_tel = (ctx.get("customer_tel") or "").strip()
    cust_fax = (ctx.get("customer_fax") or "").strip()
    if not cust_tel and ctx.get("customer_phone_line"):
        raw = str(ctx["customer_phone_line"])
        cust_tel = raw.split(":", 1)[-1].strip() if ":" in raw else raw
    ws.append(["", f"TELP. NO.: {cust_tel}"])
    ws.append(["", f"FAX. NO.: {cust_fax}"])
    if ctx.get("is_export") and ctx.get("bill_to_block"):
        ws.append(["BILL TO", ctx["bill_to_block"]])
    ws.append([])
    ws.append(["DATE", ctx["doc_date_fmt"]])
    ws.append(["INV. NO", ctx.get("invoice_no") or ""])
    ws.append([])
    ws.append([ctx.get("document_title") or INVPL_TITLE])
    ws.append([ctx.get("description_line") or INVPL_DESC_DEFAULT])
    head = [
        "P.O. NO.",
        "ITEM",
        "QTY",
        "UNIT",
        "U. PRICE (USD)",
        "AMOUNT (USD)",
        "ROLLS",
        "PIECES",
        "N.W. (KGS)",
        "G.W. (KGS)",
    ]
    ws.append(head)
    for ln in ctx["lines"]:
        ws.append(
            [
                ln.get("po_no") or "",
                _invpl_item_text(ln),
                float(ln["qty"]) if ln.get("qty") is not None else None,
                ln.get("unit") or "S/F",
                float(ln["unit_price"]) if ln.get("unit_price") is not None else None,
                float(ln["amount"]) if ln.get("amount") is not None else None,
                ln.get("rolls"),
                ln.get("pcs"),
                float(ln["nw"]) if ln.get("nw") is not None else None,
                float(ln["gw"]) if ln.get("gw") is not None else None,
            ]
        )
    t = ctx["totals"]
    total_row = [
        "TOTAL",
        "",
        float(t["qty"]) if t.get("qty") is not None else None,
        "",
        "",
        float(t["amount"]) if t.get("amount") is not None else None,
        t.get("rolls"),
        t.get("pcs"),
        float(t["nw"]) if t.get("nw") else None,
        float(t["gw"]) if t.get("gw") else None,
    ]
    ws.append([])
    ws.append(total_row)
    bank_tel, bank_fax = _invpl_bank_tel_fax(ctx)
    ws.append(["SAY TOTAL IN WORDS", ctx["amount_in_words"]])
    ws.append(["TERM OF PAYMENT", ctx.get("term_of_payment") or ""])
    ws.append(["BANK", ctx.get("bank_name") or ""])
    ws.append(["ACCOUNT NO.", _invpl_account_display(ctx.get("account_number"))])
    ws.append(["BANK ADDRESS", ctx.get("bank_address") or ""])
    ws.append(["TELP. NO", bank_tel])
    ws.append(["FAX. NO", bank_fax])
    ws.append([])
    ws.append(["AUTHORIZED SIGNATURE"])
    ws.append(["(CHIU PO HAO)"])
    ws.append(["Director"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def render_invpl_pdf(ctx: dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    page_w, _page_h = A4
    margin_lr = INVPL_MARGIN_LR_MM * mm
    margin_tb = INVPL_MARGIN_TB_MM * mm
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=margin_lr,
        rightMargin=margin_lr,
        topMargin=margin_tb,
        bottomMargin=margin_tb,
    )
    styles = getSampleStyleSheet()
    small = ParagraphStyle(name="invpl_s", parent=styles["Normal"], fontSize=7, leading=9)
    tiny = ParagraphStyle(name="invpl_tiny", parent=styles["Normal"], fontSize=6, leading=7.5)
    center_small = ParagraphStyle(name="invpl_cs", parent=small, alignment=1)
    title_style = ParagraphStyle(
        name="invpl_t",
        parent=styles["Heading2"],
        alignment=1,
        fontSize=12,
        spaceAfter=1,
        spaceBefore=4,
    )
    story: list[Any] = []
    content_w = page_w - 2 * margin_lr

    company_paras = [Paragraph(f"<b>{escape(line)}</b>", center_small) for line in COMPANY_BLOCK]
    logo_raw = _logo_bytes()
    if logo_raw:
        logo_h = _LOGO_WIDTH_MM * _LOGO_ASPECT * mm
        logo_img = RLImage(io.BytesIO(logo_raw), width=_LOGO_WIDTH_MM * mm, height=logo_h)
        logo_img.hAlign = "LEFT"
        letterhead = Table(
            [[logo_img, company_paras]],
            colWidths=[(_LOGO_WIDTH_MM + 2) * mm, content_w - (_LOGO_WIDTH_MM + 2) * mm],
        )
        letterhead.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        story.append(letterhead)
    else:
        for line in COMPANY_BLOCK:
            story.append(Paragraph(f"<b>{escape(line)}</b>", center_small))

    # Garis tebal letterhead
    rule = Table([[""]], colWidths=[content_w])
    rule.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 0), (-1, 0), 1.6, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(rule)

    cust_tel = (ctx.get("customer_tel") or "").strip()
    cust_fax = (ctx.get("customer_fax") or "").strip()
    if not cust_tel and ctx.get("customer_phone_line"):
        raw = str(ctx["customer_phone_line"])
        cust_tel = raw.split(":", 1)[-1].strip() if ":" in raw else raw
    to_paras = [
        Paragraph("<b>TO:</b>", small),
        Paragraph(f"<b>{escape(ctx['customer_name'])}</b>", small),
        Paragraph(escape(ctx.get("customer_address") or "").replace("\n", "<br/>"), small),
        Paragraph(f"TELP. NO.: {escape(cust_tel)}", small),
        Paragraph(f"FAX. NO.: {escape(cust_fax)}", small),
    ]
    meta_paras = [
        Paragraph(f"<b>DATE:</b> {escape(ctx['doc_date_fmt'])}", small),
        Paragraph(f"<b>INV. NO:</b> {escape(ctx.get('invoice_no') or '—')}", small),
    ]
    to_meta = Table(
        [[to_paras, meta_paras]],
        colWidths=[content_w - 45 * mm, 45 * mm],
    )
    to_meta.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(to_meta)

    if ctx.get("is_export") and ctx.get("bill_to_block"):
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"<b>BILL TO:</b> {escape(ctx['bill_to_block'])}", small))

    story.append(Paragraph(escape(str(ctx.get("document_title", INVPL_TITLE))), title_style))
    story.append(Paragraph("****************************************", center_small))
    story.append(
        Paragraph(
            f"<b>{escape(ctx.get('description_line') or INVPL_DESC_DEFAULT)}</b>",
            small,
        )
    )
    story.append(Spacer(1, 2 * mm))

    head = [
        "P.O. NO.",
        "ITEM",
        "QTY",
        "UNIT",
        "U. PRICE\n(USD)",
        "AMOUNT\n(USD)",
        "ROLLS",
        "PIECES",
        "N.W.\n(KGS)",
        "G.W.\n(KGS)",
    ]
    table_data: list[list[Any]] = [head]
    for ln in ctx["lines"]:
        table_data.append(
            [
                Paragraph(escape((ln.get("po_no") or "")[:22]), tiny),
                Paragraph(escape(_invpl_item_text(ln)[:120]), tiny),
                _fmt_invpl_qty(ln.get("qty")),
                ln.get("unit") or "S/F",
                _fmt_invpl_money(ln.get("unit_price"), places=2),
                _fmt_invpl_money(ln.get("amount"), places=2),
                _fmt_invpl_int(ln.get("rolls")),
                _fmt_invpl_int(ln.get("pcs")),
                _fmt_invpl_weight(ln.get("nw")),
                _fmt_invpl_weight(ln.get("gw")),
            ]
        )

    t = ctx["totals"]
    table_data.append(
        [
            "TOTAL",
            "",
            _fmt_invpl_qty(t.get("qty")),
            "",
            "",
            _fmt_invpl_money(t.get("amount"), places=2),
            _fmt_invpl_int(t.get("rolls")),
            _fmt_invpl_int(t.get("pcs")),
            _fmt_invpl_weight(t.get("nw")) if t.get("nw") else "",
            _fmt_invpl_weight(t.get("gw")) if t.get("gw") else "",
        ]
    )

    weights = [1.15, 3.2, 0.85, 0.55, 0.9, 1.0, 0.7, 0.8, 0.75, 0.75]
    s = sum(weights)
    cws = [content_w * (w / s) for w in weights]
    tbl = Table(table_data, colWidths=cws, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                ("BACKGROUND", (0, -1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
                ("FONTSIZE", (0, 0), (-1, 0), 5.5),
                ("FONTSIZE", (0, 1), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("ALIGN", (3, 1), (3, -1), "CENTER"),
                ("ALIGN", (4, 1), (9, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 3 * mm))

    bank_tel, bank_fax = _invpl_bank_tel_fax(ctx)
    account_disp = _invpl_account_display(ctx.get("account_number"))
    story.append(Paragraph(f"<b>SAY TOTAL IN WORDS:</b> {escape(ctx['amount_in_words'])}", small))
    story.append(
        Paragraph(f"<b>TERM OF PAYMENT:</b> {escape(ctx.get('term_of_payment') or '—')}", small)
    )
    story.append(Paragraph(f"<b>BANK:</b> {escape(ctx.get('bank_name') or '—')}", small))
    story.append(Paragraph(f"<b>ACCOUNT NO.:</b> {escape(account_disp)}", small))
    story.append(
        Paragraph(f"<b>BANK ADDRESS:</b> {escape(ctx.get('bank_address') or '—')}", small)
    )
    story.append(Paragraph(f"<b>TELP. NO:</b> {escape(bank_tel or '—')}", small))
    story.append(Paragraph(f"<b>FAX. NO:</b> {escape(bank_fax or '—')}", small))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("<b>AUTHORIZED SIGNATURE</b>", small))
    story.append(Spacer(1, 12 * mm))
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
        "is_foc": bool(getattr(dh, "is_foc", False)),
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


def _sj_letterhead_html() -> str:
    """Logo kiri atas + blok perusahaan (sama aset INVPL)."""
    company = "<br/>".join(escape(x) for x in COMPANY_BLOCK)
    logo_uri = _logo_data_uri()
    logo_html = (
        f'<div class="logo"><img src="{logo_uri}" alt="Tong Hong Tannery"/></div>'
        if logo_uri
        else '<div class="logo"></div>'
    )
    return f"""<div class="header-row">
    {logo_html}
    <div class="company"><b>{company}</b></div>
  </div>"""


def render_sj_html(ctx: dict[str, Any]) -> str:
    export_note = ""
    if ctx.get("is_export"):
        export_note = (
            '<p class="note">'
            + escape("Catatan: untuk transaksi ekspor, cetak Surat Jalan bersifat opsional.")
            + "</p>"
        )
    body = f"""
<div class="doc">
  {_sj_letterhead_html()}
  <h2 class="title">{escape(sj_document_title(ctx))}</h2>
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
    .header-row { display: grid; grid-template-columns: 28mm 1fr; align-items: center; gap: 8px; margin-bottom: 8px; }
    .logo img { width: 24mm; height: auto; display: block; }
    .company { text-align: center; line-height: 1.35; }
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
<html lang="id"><head><meta charset="utf-8"/><title>{escape(sj_document_title(ctx))}</title>
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
    page_w = A4[0] - 28 * mm
    company_paras = [Paragraph(f"<b>{escape(line)}</b>", center) for line in COMPANY_BLOCK]
    logo_raw = _logo_bytes()
    if logo_raw:
        logo_h = _LOGO_WIDTH_MM * _LOGO_ASPECT * mm
        logo_img = RLImage(io.BytesIO(logo_raw), width=_LOGO_WIDTH_MM * mm, height=logo_h)
        logo_img.hAlign = "LEFT"
        letterhead = Table(
            [[logo_img, company_paras]],
            colWidths=[(_LOGO_WIDTH_MM + 2) * mm, page_w - (_LOGO_WIDTH_MM + 2) * mm],
        )
        letterhead.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        story.append(letterhead)
    else:
        for line in COMPANY_BLOCK:
            story.append(Paragraph(f"<b>{escape(line)}</b>", center))
    story.append(Paragraph(escape(sj_document_title(ctx)), title))

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
    body = f"""
<div class="doc">
  {_sj_letterhead_html()}
  <h2 class="title">{escape(sj_document_title(ctx))}</h2>
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
    .header-row { display: grid; grid-template-columns: 22mm 1fr; align-items: center; gap: 4px; margin-bottom: 4px; }
    .logo img { width: 20mm; height: auto; display: block; }
    .company { text-align: center; font-size: 9px; line-height: 1.25; }
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

