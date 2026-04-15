"""Skema request/response API v1."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic import field_validator


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Customers ---
class CustomerCreate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    skep_kb_number: Optional[str] = None
    customs_office_code: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    is_export_customer: bool = False
    bill_to: Optional[str] = None
    wilayah_province_code: Optional[str] = None
    wilayah_regency_code: Optional[str] = None
    wilayah_district_code: Optional[str] = None
    wilayah_village_code: Optional[str] = None


class CustomerUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    skep_kb_number: Optional[str] = None
    customs_office_code: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    is_export_customer: Optional[bool] = None
    bill_to: Optional[str] = None
    wilayah_province_code: Optional[str] = None
    wilayah_regency_code: Optional[str] = None
    wilayah_district_code: Optional[str] = None
    wilayah_village_code: Optional[str] = None


class CustomerOut(ORMBase):
    id: int
    code: Optional[str] = None
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    skep_kb_number: Optional[str] = None
    customs_office_code: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    is_export_customer: bool = False
    bill_to: Optional[str] = None
    wilayah_province_code: Optional[str] = None
    wilayah_regency_code: Optional[str] = None
    wilayah_district_code: Optional[str] = None
    wilayah_village_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Buyer price lists ---
class BuyerPriceListCreate(BaseModel):
    buyer_code: str
    title: Optional[str] = None
    period_label: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    source_label: Optional[str] = None
    currency: str = "USD"


class BuyerPriceListUpdate(BaseModel):
    title: Optional[str] = None
    period_label: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    source_label: Optional[str] = None
    currency: Optional[str] = None


class BuyerPriceSheetSave(BaseModel):
    """Simpan urutan kolom + baris sheet (cells JSON per baris)."""

    column_keys: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)


class BuyerPriceResolveIn(BaseModel):
    """Kriteria pencocokan baris di sheet list harga buyer (harga di server)."""

    buyer_code: str
    material_name: Optional[str] = None
    color: Optional[str] = None
    style_article: Optional[str] = None
    thickness_text: Optional[str] = None
    color_family: Optional[str] = None

    @field_validator("color_family")
    @classmethod
    def validate_color_family(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        raw = str(v).strip().lower()
        if raw not in {"black", "color", "fluorescent"}:
            raise ValueError("color_family harus black, color, atau fluorescent")
        return raw


class BuyerPriceResolveOut(BaseModel):
    unit_price: Optional[Decimal] = None
    matched: bool = False
    price_column: Optional[str] = None
    score: int = 0
    detail: str = ""


# --- Customs (AJU) ---
class CustomsDeclarationCreate(BaseModel):
    nomor_aju: str
    kode_dokumen: Optional[str] = None
    source_label: Optional[str] = None
    versi_template: Optional[str] = None


class CustomsDeclarationUpdate(BaseModel):
    kode_dokumen: Optional[str] = None
    source_label: Optional[str] = None
    versi_template: Optional[str] = None


class CustomsSheetData(BaseModel):
    column_keys: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)


class CustomsSheetsSave(BaseModel):
    """Per sheet: urutan kolom + baris; mengganti seluruh `customs_aju_sheet_rows` untuk deklarasi ini."""

    sheets: dict[str, CustomsSheetData] = Field(default_factory=dict)


# --- PO ---
class PoHeaderCreate(BaseModel):
    po_number: Optional[str] = None
    customer_id: Optional[int] = None
    customer_code: Optional[str] = None
    po_category: str = "production"
    buyer: Optional[str] = None
    order_date: Optional[date] = None
    etd: Optional[date] = None
    remark: Optional[str] = None
    status: str = "draft"
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    brand_id: Optional[int] = None
    marketing_excel_date_serial: Optional[int] = None
    po_customer_ref: Optional[str] = None
    order_type_label: Optional[str] = None
    brand_name_snapshot: Optional[str] = None
    customer_name_snapshot: Optional[str] = None
    customs_declaration_id: Optional[int] = None

    @field_validator("po_category")
    @classmethod
    def validate_po_category(cls, v: str) -> str:
        raw = (v or "").strip().lower()
        alias = {
            "produksi": "production",
            "sample": "sample",
            "claim": "claim",
            "return": "return",
            "subkon": "subcont",
            "subcont": "subcont",
            "subcontract": "subcont",
            "suede": "suede",
        }
        out = alias.get(raw, raw)
        if out not in {"production", "sample", "claim", "return", "subcont", "suede"}:
            raise ValueError("po_category tidak valid")
        return out


class PoHeaderUpdate(BaseModel):
    po_number: Optional[str] = None
    customer_id: Optional[int] = None
    customer_code: Optional[str] = None
    po_category: Optional[str] = None
    buyer: Optional[str] = None
    order_date: Optional[date] = None
    etd: Optional[date] = None
    remark: Optional[str] = None
    status: Optional[str] = None
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    brand_id: Optional[int] = None
    marketing_excel_date_serial: Optional[int] = None
    po_customer_ref: Optional[str] = None
    order_type_label: Optional[str] = None
    brand_name_snapshot: Optional[str] = None
    customer_name_snapshot: Optional[str] = None
    customs_declaration_id: Optional[int] = None
    material_followup_remark: Optional[str] = None
    material_followup_done: Optional[bool] = None

    @field_validator("po_category")
    @classmethod
    def validate_po_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        raw = (v or "").strip().lower()
        alias = {
            "produksi": "production",
            "sample": "sample",
            "claim": "claim",
            "return": "return",
            "subkon": "subcont",
            "subcont": "subcont",
            "subcontract": "subcont",
            "suede": "suede",
        }
        out = alias.get(raw, raw)
        if out not in {"production", "sample", "claim", "return", "subcont", "suede"}:
            raise ValueError("po_category tidak valid")
        return out


class PoDetailCreate(BaseModel):
    master_item_id: Optional[int] = None
    thi_line_ref: Optional[str] = None
    material_name: Optional[str] = None
    color: Optional[str] = None
    color_family: Optional[str] = None
    thickness_min: Optional[Decimal] = None
    thickness_max: Optional[Decimal] = None
    thickness_text: Optional[str] = None
    emboss: Optional[str] = None
    vir_softness_type: Optional[str] = None
    softness: Optional[str] = None
    color_reference: Optional[str] = None
    backing: Optional[str] = None
    quantity_order: Optional[Decimal] = None
    style_article: Optional[str] = None
    model: Optional[str] = None
    line_etd: Optional[date] = None
    rtd_text: Optional[str] = None
    etd_excel_serial: Optional[int] = None
    stock_wh_qty: Optional[Decimal] = None
    balance_qty: Optional[Decimal] = None
    system_reference: Optional[str] = None
    detail_remark: Optional[str] = None
    marketing_outstanding_remark: Optional[str] = None
    unit_price: Optional[Decimal] = None
    copied_from_detail_id: Optional[int] = None

    @field_validator("color_family")
    @classmethod
    def validate_detail_color_family(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not str(v).strip()):
            return None
        raw = str(v).strip().lower()
        if raw not in {"black", "color", "fluorescent"}:
            raise ValueError("color_family tidak valid")
        return raw


class PoDetailUpdate(BaseModel):
    master_item_id: Optional[int] = None
    thi_line_ref: Optional[str] = None
    material_name: Optional[str] = None
    color: Optional[str] = None
    color_family: Optional[str] = None
    thickness_min: Optional[Decimal] = None
    thickness_max: Optional[Decimal] = None
    thickness_text: Optional[str] = None
    emboss: Optional[str] = None
    vir_softness_type: Optional[str] = None
    softness: Optional[str] = None
    color_reference: Optional[str] = None
    backing: Optional[str] = None
    quantity_order: Optional[Decimal] = None
    style_article: Optional[str] = None
    model: Optional[str] = None
    line_etd: Optional[date] = None
    rtd_text: Optional[str] = None
    etd_excel_serial: Optional[int] = None
    stock_wh_qty: Optional[Decimal] = None
    balance_qty: Optional[Decimal] = None
    system_reference: Optional[str] = None
    detail_remark: Optional[str] = None
    marketing_outstanding_remark: Optional[str] = None
    unit_price: Optional[Decimal] = None
    copied_from_detail_id: Optional[int] = None

    @field_validator("color_family")
    @classmethod
    def validate_detail_color_family_upd(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not str(v).strip()):
            return None
        raw = str(v).strip().lower()
        if raw not in {"black", "color", "fluorescent"}:
            raise ValueError("color_family tidak valid")
        return raw


class PoHeaderOut(ORMBase):
    id: int
    po_number: Optional[str] = None
    customer_id: Optional[int] = None
    customer_code: Optional[str] = None
    po_category: Optional[str] = None
    buyer: Optional[str] = None
    order_date: Optional[date] = None
    etd: Optional[date] = None
    remark: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    brand_id: Optional[int] = None
    marketing_excel_date_serial: Optional[int] = None
    po_customer_ref: Optional[str] = None
    order_type_label: Optional[str] = None
    brand_name_snapshot: Optional[str] = None
    customer_name_snapshot: Optional[str] = None
    customs_declaration_id: Optional[int] = None
    mkt_workflow_stage: Optional[str] = None
    mkt_workflow_updated_at: Optional[datetime] = None
    rekap_printed_at: Optional[datetime] = None
    material_followup_remark: Optional[str] = None
    material_followup_done: Optional[bool] = None

    @computed_field
    @property
    def so_number(self) -> Optional[str]:
        return self.po_number


class PoDetailDeliveryOut(ORMBase):
    id: int
    po_detail_id: Optional[int] = None
    sequence_no: int
    qty: Optional[Decimal] = None
    delivery_date: Optional[date] = None


class DeliveryScheduleItem(BaseModel):
    sequence_no: int
    qty: Optional[Decimal] = None
    delivery_date: Optional[date] = None


class DeliverySchedulesPayload(BaseModel):
    schedules: list[DeliveryScheduleItem] = Field(default_factory=list)


class PoDetailOut(ORMBase):
    id: int
    po_id: Optional[int] = None
    master_item_id: Optional[int] = None
    thi_line_ref: Optional[str] = None
    material_name: Optional[str] = None
    color: Optional[str] = None
    color_family: Optional[str] = None
    thickness_min: Optional[Decimal] = None
    thickness_max: Optional[Decimal] = None
    thickness_text: Optional[str] = None
    emboss: Optional[str] = None
    vir_softness_type: Optional[str] = None
    softness: Optional[str] = None
    color_reference: Optional[str] = None
    backing: Optional[str] = None
    quantity_order: Optional[Decimal] = None
    style_article: Optional[str] = None
    model: Optional[str] = None
    created_at: Optional[datetime] = None
    line_etd: Optional[date] = None
    rtd_text: Optional[str] = None
    etd_excel_serial: Optional[int] = None
    stock_wh_qty: Optional[Decimal] = None
    balance_qty: Optional[Decimal] = None
    system_reference: Optional[str] = None
    detail_remark: Optional[str] = None
    marketing_outstanding_remark: Optional[str] = None
    unit_price: Optional[Decimal] = None
    copied_from_detail_id: Optional[int] = None
    delivery_schedules: list[PoDetailDeliveryOut] = Field(default_factory=list)


# --- Production ---
class ProductionCreate(BaseModel):
    production_number: Optional[str] = None
    po_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "planned"


class ProductionDetailCreate(BaseModel):
    po_detail_id: Optional[int] = None
    qty_planned: Optional[Decimal] = None
    qty_actual: Optional[Decimal] = None
    lot_number: Optional[str] = None
    batch_number: Optional[str] = None
    status: str = "pending"


class ProductionDetailUpdate(BaseModel):
    po_detail_id: Optional[int] = None
    qty_planned: Optional[Decimal] = None
    qty_actual: Optional[Decimal] = None
    lot_number: Optional[str] = None
    batch_number: Optional[str] = None
    status: Optional[str] = None


# --- QC ---
class QcHeaderCreate(BaseModel):
    qc_number: Optional[str] = None
    production_id: Optional[int] = None
    po_id: Optional[int] = None
    qc_date: Optional[date] = None
    operator_name: Optional[str] = None


class QcDetailCreate(BaseModel):
    production_detail_id: Optional[int] = None
    roll_number: Optional[str] = None
    batch_number: Optional[str] = None
    thickness_actual: Optional[Decimal] = None
    softness_actual: Optional[str] = None
    thickness_min: Optional[Decimal] = None
    thickness_max: Optional[Decimal] = None
    softness_standard: Optional[str] = None
    result: Optional[str] = None
    is_ok: Optional[bool] = None
    device_id: Optional[str] = None
    port: Optional[str] = None
    raw_value: Optional[str] = None
    remark: Optional[str] = None
    measured_at: Optional[datetime] = None
    qty_checked: Optional[Decimal] = None
    qty_reject: Optional[Decimal] = None
    reject_reason: Optional[str] = None


class QcDetailUpdate(BaseModel):
    production_detail_id: Optional[int] = None
    roll_number: Optional[str] = None
    batch_number: Optional[str] = None
    thickness_actual: Optional[Decimal] = None
    softness_actual: Optional[str] = None
    thickness_min: Optional[Decimal] = None
    thickness_max: Optional[Decimal] = None
    softness_standard: Optional[str] = None
    result: Optional[str] = None
    is_ok: Optional[bool] = None
    device_id: Optional[str] = None
    port: Optional[str] = None
    raw_value: Optional[str] = None
    remark: Optional[str] = None
    measured_at: Optional[datetime] = None
    qty_checked: Optional[Decimal] = None
    qty_reject: Optional[Decimal] = None
    reject_reason: Optional[str] = None


# --- Delivery ---
class DeliveryHeaderCreate(BaseModel):
    """packing_id wajib — kirim hanya dari packing yang sudah selesai (done)."""

    packing_id: int
    delivery_number: Optional[str] = None
    customer_id: Optional[int] = None
    delivery_date: Optional[date] = None
    driver_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    destination: Optional[str] = None
    bc_number: Optional[str] = None
    bc_date: Optional[date] = None
    status: str = "draft"


class DeliveryHeaderUpdate(BaseModel):
    delivery_number: Optional[str] = None
    customer_id: Optional[int] = None
    delivery_date: Optional[date] = None
    driver_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    destination: Optional[str] = None
    bc_number: Optional[str] = None
    bc_date: Optional[date] = None
    status: Optional[str] = None
    packing_id: Optional[int] = None


class DeliveryDetailCreate(BaseModel):
    production_detail_id: Optional[int] = None
    qty: Optional[Decimal] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight: Optional[Decimal] = None


class DeliveryDetailUpdate(BaseModel):
    production_detail_id: Optional[int] = None
    qty: Optional[Decimal] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight: Optional[Decimal] = None


# --- Invoice ---
class InvoiceCreate(BaseModel):
    """delivery_id wajib — invoice hanya setelah delivery terkirim (status sent)."""

    delivery_id: int
    invoice_number: Optional[str] = None
    packing_list_number: Optional[str] = None
    po_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    invoice_date: Optional[date] = None
    description: Optional[str] = None
    term_of_payment: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    bank_address: Optional[str] = None
    bank_phone: Optional[str] = None
    total_amount: Optional[Decimal] = None
    total_in_words: Optional[str] = None
    due_date: Optional[date] = None
    tax_invoice_no: Optional[str] = None
    tax_invoice_date: Optional[date] = None
    receipt_no: Optional[str] = None
    received_by: Optional[str] = None
    received_date: Optional[date] = None
    nopen: Optional[str] = None
    nomor_aju: Optional[str] = None
    payment_date: Optional[date] = None
    payment_bank_account: Optional[str] = None
    payment_proof_url: Optional[str] = None
    payment_status: str = "unpaid"


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    packing_list_number: Optional[str] = None
    po_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    invoice_date: Optional[date] = None
    description: Optional[str] = None
    term_of_payment: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    bank_address: Optional[str] = None
    bank_phone: Optional[str] = None
    total_amount: Optional[Decimal] = None
    total_in_words: Optional[str] = None
    due_date: Optional[date] = None
    tax_invoice_no: Optional[str] = None
    tax_invoice_date: Optional[date] = None
    receipt_no: Optional[str] = None
    received_by: Optional[str] = None
    received_date: Optional[date] = None
    nopen: Optional[str] = None
    nomor_aju: Optional[str] = None
    payment_date: Optional[date] = None
    payment_bank_account: Optional[str] = None
    payment_proof_url: Optional[str] = None
    payment_status: Optional[str] = None


class InvoiceDetailCreate(BaseModel):
    item_description: Optional[str] = None
    color: Optional[str] = None
    qty: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    roll: Optional[int] = None
    pcs: Optional[int] = None
    net_weight: Optional[Decimal] = None
    gross_weight: Optional[Decimal] = None
    remark: Optional[str] = None


# --- Master Item & Master Price (sheet Excel) ---
class MasterItemCreate(BaseModel):
    item_code: str
    thickness_mm: Optional[Decimal] = None
    thickness_range: Optional[str] = None
    material_name: Optional[str] = None
    emboss: Optional[str] = None
    color: Optional[str] = None
    softness: Optional[str] = None
    color_reference: Optional[str] = None
    backing: Optional[str] = None
    quantity_order_default: Optional[Decimal] = None
    style_article: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    exim_material_code: Optional[str] = None
    color_standard: Optional[str] = None
    model_takedown: Optional[str] = None


class MasterItemOut(ORMBase):
    id: int
    item_code: str
    thickness_mm: Optional[Decimal] = None
    thickness_range: Optional[str] = None
    material_name: Optional[str] = None
    emboss: Optional[str] = None
    color: Optional[str] = None
    softness: Optional[str] = None
    color_reference: Optional[str] = None
    backing: Optional[str] = None
    quantity_order_default: Optional[Decimal] = None
    style_article: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    exim_material_code: Optional[str] = None
    color_standard: Optional[str] = None
    model_takedown: Optional[str] = None
    created_at: Optional[datetime] = None


class MasterPriceOut(ORMBase):
    id: int
    line_no: Optional[int] = None
    material_category: Optional[str] = None
    material_type: Optional[str] = None
    material_name: Optional[str] = None
    thickness_range: Optional[str] = None
    price_white_usd: Optional[Decimal] = None
    price_black_usd: Optional[Decimal] = None
    price_color_usd: Optional[Decimal] = None
    price_metallic_usd: Optional[Decimal] = None
    remark: Optional[str] = None
    price_tier: Optional[str] = None
    created_at: Optional[datetime] = None


class LoginIn(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORMBase):
    id: int
    username: str
    role: str
    is_active: bool
    department: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    is_active: bool = True
    department: Optional[str] = None


class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    department: Optional[str] = None


class NotificationOut(ORMBase):
    id: int
    user_id: int
    title: str
    message: Optional[str] = None
    category: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    route_path: Optional[str] = None
    route_query: Optional[dict[str, Any]] = None
    is_read: bool
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


class SpecialPriceCreate(BaseModel):
    buyer_code: str
    material_pattern: Optional[str] = None
    emboss_pattern: Optional[str] = None
    color_pattern: Optional[str] = None
    discount_type: str = "percentage"
    discount_value: Decimal
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool = True


class SpecialPriceUpdate(BaseModel):
    buyer_code: Optional[str] = None
    material_pattern: Optional[str] = None
    emboss_pattern: Optional[str] = None
    color_pattern: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: Optional[bool] = None


class SpecialPriceOut(ORMBase):
    id: int
    buyer_code: str
    material_pattern: Optional[str] = None
    emboss_pattern: Optional[str] = None
    color_pattern: Optional[str] = None
    discount_type: str
    discount_value: Decimal
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool
    created_at: Optional[datetime] = None


class CustomerSpecialPriceCreate(BaseModel):
    customer_id: int
    buyer_code: str
    material_pattern: Optional[str] = None
    price_override: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool = True


class CustomerSpecialPriceUpdate(BaseModel):
    customer_id: Optional[int] = None
    buyer_code: Optional[str] = None
    material_pattern: Optional[str] = None
    price_override: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: Optional[bool] = None


class CustomerSpecialPriceOut(ORMBase):
    id: int
    customer_id: int
    buyer_code: str
    material_pattern: Optional[str] = None
    price_override: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool
    created_at: Optional[datetime] = None
    customer: Optional[CustomerOut] = None


class BrandOut(ORMBase):
    id: int
    customer_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None


class CustomerBrandMappingCreate(BaseModel):
    brand_id: int
    is_default: bool = False


class CustomerBrandMappingUpdate(BaseModel):
    is_default: Optional[bool] = None


class CustomerBrandMappingOut(ORMBase):
    id: int
    customer_id: int
    brand_id: int
    is_default: bool
    created_at: Optional[datetime] = None
    brand: Optional[BrandOut] = None


class BrandConstraintCreate(BaseModel):
    allowed_brand_ids: list[int]


class BrandConstraintUpdate(BaseModel):
    allowed_brand_ids: Optional[list[int]] = None


class BrandConstraintOut(ORMBase):
    id: int
    customer_id: int
    allowed_brand_ids: list[int]
    created_at: Optional[datetime] = None


def row_to_dict(obj: Any) -> dict[str, Any]:
    """Serialisasi sederhana untuk respons fleksibel."""
    if obj is None:
        return {}
    out: dict[str, Any] = {}
    for c in obj.__table__.columns:
        v = getattr(obj, c.key)
        if isinstance(v, Decimal):
            v = float(v) if v is not None else None
        out[c.key] = v
    return out


class SubconInvoiceCreate(BaseModel):
    po_id: int
    invoice_type: str
    invoice_number: Optional[str] = None
    amount: Decimal
    description: Optional[str] = None


class SubconInvoiceUpdate(BaseModel):
    invoice_type: Optional[str] = None
    invoice_number: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SubconInvoiceOut(ORMBase):
    id: int
    po_id: int
    invoice_type: str
    invoice_number: Optional[str] = None
    amount: Decimal
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    po_number: Optional[str] = None
    customer_name: Optional[str] = None


class PpicsAssignmentCreate(BaseModel):
    po_id: int
    ppic_user_id: int
    notes: Optional[str] = None


class PpicsAssignmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class PpicsAssignmentOut(ORMBase):
    id: int
    po_id: int
    ppic_user_id: int
    status: str
    notes: Optional[str] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    po_number: Optional[str] = None
    customer_name: Optional[str] = None
    ppic_username: Optional[str] = None
