"""Skema request/response API v1."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic import field_validator


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Customers ---
class CustomerContactIn(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class CustomerContactOut(ORMBase):
    id: int
    customer_id: Optional[int] = None
    name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class CustomerCreate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    skep_kb_number: Optional[str] = None
    customs_office_code: Optional[str] = None
    address: Optional[str] = None
    billing_address: Optional[str] = None
    remark: Optional[str] = None
    is_active: bool = True
    is_export_customer: bool = False
    wilayah_province_code: Optional[str] = None
    wilayah_regency_code: Optional[str] = None
    wilayah_district_code: Optional[str] = None
    wilayah_village_code: Optional[str] = None
    payment_terms: Optional[str] = None
    default_currency: Optional[str] = None
    tax_mode: Optional[str] = None
    reference_quotation: Optional[str] = None
    contacts: list[CustomerContactIn] = Field(default_factory=list)


class CustomerUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    skep_kb_number: Optional[str] = None
    customs_office_code: Optional[str] = None
    address: Optional[str] = None
    billing_address: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None
    is_export_customer: Optional[bool] = None
    wilayah_province_code: Optional[str] = None
    wilayah_regency_code: Optional[str] = None
    wilayah_district_code: Optional[str] = None
    wilayah_village_code: Optional[str] = None
    payment_terms: Optional[str] = None
    default_currency: Optional[str] = None
    tax_mode: Optional[str] = None
    reference_quotation: Optional[str] = None
    contacts: Optional[list[CustomerContactIn]] = None


class CustomerOut(ORMBase):
    id: int
    code: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    skep_kb_number: Optional[str] = None
    customs_office_code: Optional[str] = None
    address: Optional[str] = None
    billing_address: Optional[str] = None
    remark: Optional[str] = None
    is_active: bool = True
    is_export_customer: bool = False
    wilayah_province_code: Optional[str] = None
    wilayah_regency_code: Optional[str] = None
    wilayah_district_code: Optional[str] = None
    wilayah_village_code: Optional[str] = None
    payment_terms: Optional[str] = None
    default_currency: Optional[str] = None
    tax_mode: Optional[str] = None
    reference_quotation: Optional[str] = None
    contacts: list[CustomerContactOut] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CustomerPageOut(BaseModel):
    items: list[CustomerOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0



# --- Buyer price lists ---
class BuyerPriceListCreate(BaseModel):
    brand_id: int
    buyer_code: str
    title: Optional[str] = None
    period_label: Optional[str] = None
    period_start: date
    period_end: date
    currency: str = "USD"


class BuyerPriceListUpdate(BaseModel):
    title: Optional[str] = None
    period_label: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
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
    emboss: Optional[str] = None
    factory_code: Optional[str] = None
    as_of: Optional[date] = None

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
    factory_code: Optional[str] = None
    buyer: Optional[str] = None
    order_date: Optional[date] = None
    etd: Optional[date] = None
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
    # Hanya untuk penomoran SO otomatis (tidak disimpan ke DB).
    material_group: Optional[str] = None

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

    @field_validator("material_group")
    @classmethod
    def validate_material_group(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        mg = (v or "").strip().lower()
        if mg not in {"pu", "suede"}:
            raise ValueError("material_group tidak valid")
        return mg


class PoHeaderUpdate(BaseModel):
    po_number: Optional[str] = None
    customer_id: Optional[int] = None
    customer_code: Optional[str] = None
    po_category: Optional[str] = None
    factory_code: Optional[str] = None
    buyer: Optional[str] = None
    order_date: Optional[date] = None
    etd: Optional[date] = None
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
    color_standard: Optional[str] = None
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
    color_swatch_recipe_id: Optional[int] = None
    delivery_schedules: Optional[list["DeliveryScheduleItem"]] = None

    @field_validator("color_family")
    @classmethod
    def validate_detail_color_family(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not str(v).strip()):
            return None
        raw = str(v).strip().lower()
        if raw not in {"black", "color", "fluorescent"}:
            raise ValueError("color_family tidak valid")
        return raw

    @field_validator("quantity_order")
    @classmethod
    def quantity_order_must_be_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("quantity_order must be greater than 0")
        return v

    @field_validator("unit_price")
    @classmethod
    def unit_price_must_be_non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("unit_price must be greater than or equal to 0")
        return v


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
    color_standard: Optional[str] = None
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
    color_swatch_recipe_id: Optional[int] = None

    @field_validator("color_family")
    @classmethod
    def validate_detail_color_family_upd(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not str(v).strip()):
            return None
        raw = str(v).strip().lower()
        if raw not in {"black", "color", "fluorescent"}:
            raise ValueError("color_family tidak valid")
        return raw


class MrpSyncStatusOut(BaseModel):
    """Hasil sync ERP→MRP pada response Confirm (transient, bukan kolom DB)."""

    ok: bool = True
    error: Optional[str] = None
    attempts: int = 1


class PoHeaderOut(ORMBase):
    id: int
    po_number: Optional[str] = None
    customer_id: Optional[int] = None
    customer_code: Optional[str] = None
    po_category: Optional[str] = None
    factory_code: Optional[str] = None
    buyer: Optional[str] = None
    order_date: Optional[date] = None
    etd: Optional[date] = None
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
    item_revised_at: Optional[datetime] = None
    item_revised_has_update: bool = False
    item_revised_has_delete: bool = False
    material_followup_remark: Optional[str] = None
    material_followup_done: Optional[bool] = None
    stuck_reason: Optional[str] = None
    material_hint: Optional[str] = None
    lot_hint: Optional[str] = None
    detail_line_count: Optional[int] = None
    etd_display: Optional[str] = None
    reply_etd_display: Optional[str] = None
    mrp_sync_error: Optional[str] = None
    mrp_sync: Optional[MrpSyncStatusOut] = None

    @computed_field
    @property
    def so_number(self) -> Optional[str]:
        return self.po_number


class PoHeaderPageOut(BaseModel):
    items: list[PoHeaderOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0
    stage_counts: Optional[dict[str, int]] = None


class PoMaterialHintItemOut(BaseModel):
    po_id: int
    detail_line_count: int = 0
    material_hint: Optional[str] = None
    lot_hint: Optional[str] = None
    etd_display: Optional[str] = None
    reply_etd_display: Optional[str] = None


class PoMaterialHintsOut(BaseModel):
    items: list[PoMaterialHintItemOut] = Field(default_factory=list)


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


class PoMarketingReviseHeader(BaseModel):
    """Revisi marketing: tidak mengubah customer, brand, nomor PO, tanggal order, status, harga."""

    etd: Optional[date] = None
    delivery_address: Optional[str] = None
    material_followup_remark: Optional[str] = None
    material_followup_done: Optional[bool] = None


class PoMarketingReviseLine(BaseModel):
    detail_id: int
    line_etd: Optional[date] = None
    detail_remark: Optional[str] = None
    marketing_outstanding_remark: Optional[str] = None
    rtd_text: Optional[str] = None
    delivery_schedules: Optional[list[DeliveryScheduleItem]] = None


class PoMarketingReviseBody(BaseModel):
    header: Optional[PoMarketingReviseHeader] = None
    lines: Optional[list[PoMarketingReviseLine]] = None


class MarketingOutstandingSnapshotFilter(BaseModel):
    balance_filter: str = "exclude_zero"
    computed_balance: bool = True
    po_q: Optional[str] = None
    shipment_status: str = "all"
    material_status: Optional[str] = None
    factory_code: Optional[str] = None
    customer_ids: Optional[str] = None
    po_category: Optional[str] = None
    material_group: Optional[str] = None
    mkt_stage_min: Optional[str] = None
    order_date_from: Optional[str] = None
    order_date_to: Optional[str] = None


class MarketingOutstandingSnapshotCreate(BaseModel):
    label: Optional[str] = None
    filters: MarketingOutstandingSnapshotFilter = Field(default_factory=MarketingOutstandingSnapshotFilter)


class MarketingOutstandingSnapshotListItem(ORMBase):
    id: int
    label: Optional[str] = None
    row_count: int = 0
    created_at: Optional[datetime] = None
    created_by_username: Optional[str] = None


class MarketingOutstandingSnapshotDetailOut(MarketingOutstandingSnapshotListItem):
    filter_params_json: Optional[dict[str, Any]] = None
    rows_json: list[dict[str, Any]] = Field(default_factory=list)


class MarketingOutstandingLineOut(BaseModel):
    """Satu baris lembar outstanding marketing (JSON API)."""

    order_date: Optional[str] = None
    thi_order: Optional[str] = None
    customer_name: Optional[str] = None
    customer_id: Optional[int] = None
    brand: Optional[str] = None
    order_type: Optional[str] = None
    no_po: Optional[str] = None
    po_customer_ref: Optional[str] = None
    material_name: Optional[str] = None
    thickness: Optional[str] = None
    emboss: Optional[str] = None
    softness_type: Optional[str] = None
    color: Optional[str] = None
    softness: Optional[str] = None
    qty_sf: Optional[str] = None
    unit_price: Optional[str] = None
    color_reference: Optional[str] = None
    color_standard: Optional[str] = None
    backing: Optional[str] = None
    model: Optional[str] = None
    style_article: Optional[str] = None
    rtd_text: Optional[str] = None
    etd: Optional[str] = None
    line_etd: Optional[str] = None
    stock_wh_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    system_reference: Optional[str] = None
    lot_no: Optional[str] = None
    detail_remark: Optional[str] = None
    remark_system: Optional[str] = None
    remark_marketing: Optional[str] = None
    material_followup_remark_header: Optional[str] = None
    material_followup_done_header: Optional[bool] = None
    followup_status: Optional[str] = None
    status_material: Optional[str] = None
    delivered_qty: Optional[str] = None
    production_status: Optional[str] = None
    po_id: int
    po_detail_id: int
    po_status: Optional[str] = None
    mkt_stage: Optional[str] = None
    mrp_alloc_status: Optional[str] = None
    mrp_qty_processed: Optional[str] = None
    mrp_qty_remaining: Optional[str] = None
    mrp_qty_ship_remaining: Optional[str] = None
    mrp_qty_wip: Optional[str] = None
    po_category: Optional[str] = None
    factory_code: Optional[str] = None
    plan_slots: list[dict[str, Any]] = Field(default_factory=list)
    delivery_1_qty: Optional[str] = None
    delivery_1_date: Optional[str] = None
    delivery_2_qty: Optional[str] = None
    delivery_2_date: Optional[str] = None
    delivery_3_qty: Optional[str] = None
    delivery_3_date: Optional[str] = None
    delivery_4_qty: Optional[str] = None
    delivery_4_date: Optional[str] = None
    delivery_5_qty: Optional[str] = None
    delivery_5_date: Optional[str] = None
    delivery_6_qty: Optional[str] = None
    delivery_6_date: Optional[str] = None
    delivery_7_qty: Optional[str] = None
    delivery_7_date: Optional[str] = None
    delivery_8_qty: Optional[str] = None
    delivery_8_date: Optional[str] = None
    delivery_9_qty: Optional[str] = None
    delivery_9_date: Optional[str] = None
    delivery_10_qty: Optional[str] = None
    delivery_10_date: Optional[str] = None
    delivery_11_qty: Optional[str] = None
    delivery_11_date: Optional[str] = None
    delivery_12_qty: Optional[str] = None
    delivery_12_date: Optional[str] = None
    delivery_13_qty: Optional[str] = None
    delivery_13_date: Optional[str] = None
    delivery_14_qty: Optional[str] = None
    delivery_14_date: Optional[str] = None
    delivery_15_qty: Optional[str] = None
    delivery_15_date: Optional[str] = None
    delivery_16_qty: Optional[str] = None
    delivery_16_date: Optional[str] = None
    delivery_17_qty: Optional[str] = None
    delivery_17_date: Optional[str] = None
    delivery_18_qty: Optional[str] = None
    delivery_18_date: Optional[str] = None
    delivery_19_qty: Optional[str] = None
    delivery_19_date: Optional[str] = None
    delivery_20_qty: Optional[str] = None
    delivery_20_date: Optional[str] = None
    delivery_21_qty: Optional[str] = None
    delivery_21_date: Optional[str] = None
    delivery_1_number: Optional[str] = None
    delivery_1_id: Optional[int] = None
    delivery_2_number: Optional[str] = None
    delivery_2_id: Optional[int] = None
    delivery_3_number: Optional[str] = None
    delivery_3_id: Optional[int] = None
    latest_delivery_id: Optional[int] = None
    latest_delivery_number: Optional[str] = None
    latest_delivery_status: Optional[str] = None
    schedule_qty_total: Optional[str] = None
    schedule_unallocated_qty: Optional[str] = None
    actual_vs_schedule_qty: Optional[str] = None


class MarketingOutstandingPageOut(BaseModel):
    data: list[MarketingOutstandingLineOut] = Field(default_factory=list)
    items: list[MarketingOutstandingLineOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class MarketingDeliveryLineOut(BaseModel):
    surat_jalan_no: Optional[str] = None
    delivery_date: Optional[str] = None
    factory_name: Optional[str] = None
    system_no: Optional[str] = None
    po_date: Optional[str] = None
    po_number: Optional[str] = None
    lot_no: Optional[str] = None
    thickness: Optional[str] = None
    color: Optional[str] = None
    leather_color: Optional[str] = None
    leather_in_date: Optional[str] = None
    material_type: Optional[str] = None
    material_name: Optional[str] = None
    qty_po: Optional[str] = None
    unit_price: Optional[str] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    qty_sf: Optional[str] = None
    gross_weight: Optional[str] = None
    net_weight: Optional[str] = None
    amount: Optional[str] = None
    color_std: Optional[str] = None
    emboss: Optional[str] = None
    buyer: Optional[str] = None
    style_article: Optional[str] = None
    model: Optional[str] = None
    invoice_number: Optional[str] = None
    pi_no: Optional[str] = None
    remark: Optional[str] = None
    order_type: Optional[str] = None
    factory_code: Optional[str] = None
    destination: Optional[str] = None
    delivery_id: Optional[int] = None
    delivery_detail_id: Optional[int] = None
    delivery_status: Optional[str] = None
    packing_id: Optional[int] = None
    packing_status: Optional[str] = None
    invpl_printed: Optional[bool] = None
    delivery_zone: Optional[str] = None
    source_mrp: Optional[bool] = None


class MarketingDeliveryLinesPageOut(BaseModel):
    data: list[MarketingDeliveryLineOut] = Field(default_factory=list)
    items: list[MarketingDeliveryLineOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class MarketingDeliveryPlanningSlotOut(BaseModel):
    delivery_date: Optional[str] = None
    sequence_no: Optional[int] = None
    qty: Optional[str] = None
    po_id: Optional[int] = None
    po_number: Optional[str] = None
    po_customer_ref: Optional[str] = None
    customer_name: Optional[str] = None
    customer_id: Optional[int] = None
    brand: Optional[str] = None
    factory_code: Optional[str] = None
    material_name: Optional[str] = None
    thi_order: Optional[str] = None
    thi_line_ref: Optional[str] = None
    lot_no: Optional[str] = None
    po_detail_id: Optional[int] = None
    line_etd: Optional[str] = None
    mkt_stage: Optional[str] = None
    order_qty: Optional[str] = None
    delivered_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    ship_status: Optional[str] = None
    overdue: Optional[bool] = None
    mrp_qty_processed: Optional[str] = None
    mrp_qty_wip: Optional[str] = None


class MarketingDeliveryPlanningPageOut(BaseModel):
    date_from: str
    date_to: str
    data: list[MarketingDeliveryPlanningSlotOut] = Field(default_factory=list)
    items: list[MarketingDeliveryPlanningSlotOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class MarketingLineEtdTodayOut(BaseModel):
    line_etd: Optional[str] = None
    po_id: Optional[int] = None
    po_number: Optional[str] = None
    factory_code: Optional[str] = None
    customer_name: Optional[str] = None
    material_name: Optional[str] = None
    thi_order: Optional[str] = None
    po_detail_id: Optional[int] = None


class MarketingDeliveryTodayOut(BaseModel):
    as_of: str
    planned_delivery_slots: list[MarketingDeliveryPlanningSlotOut] = Field(default_factory=list)
    overdue_slots: list[MarketingDeliveryPlanningSlotOut] = Field(default_factory=list)
    lines_reply_etd_today: list[MarketingLineEtdTodayOut] = Field(default_factory=list)
    surat_jalan_lines: list[MarketingDeliveryLineOut] = Field(default_factory=list)


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
    color_standard: Optional[str] = None
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
    color_swatch_recipe_id: Optional[int] = None
    delivery_schedules: list[PoDetailDeliveryOut] = Field(default_factory=list)
    line_locked: bool = False
    line_lock_reason: Optional[str] = None


class LotGenerateIn(BaseModel):
    po_category: str
    factory_code: str
    master_item_id: Optional[int] = None
    material_name: Optional[str] = None
    vir_softness_type: Optional[str] = None


class LotGenerateOut(BaseModel):
    lot_number: str


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


class ProductionOrderOut(ORMBase):
    id: int
    production_number: Optional[str] = None
    po_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "planned"
    created_at: Optional[datetime] = None


class ProductionOrderPageOut(BaseModel):
    items: list[ProductionOrderOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class ProductionDetailOut(ORMBase):
    id: int
    production_id: Optional[int] = None
    po_detail_id: Optional[int] = None
    qty_planned: Optional[float] = None
    qty_actual: Optional[float] = None
    lot_number: Optional[str] = None
    batch_number: Optional[str] = None
    status: str = "pending"
    is_over_production: Optional[bool] = None


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


class QcHeaderOut(ORMBase):
    id: int
    qc_number: Optional[str] = None
    production_id: Optional[int] = None
    po_id: Optional[int] = None
    qc_date: Optional[date] = None
    operator_name: Optional[str] = None
    created_at: Optional[datetime] = None


class QcHeaderPageOut(BaseModel):
    items: list[QcHeaderOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class QcDetailOut(ORMBase):
    id: int
    qc_id: Optional[int] = None
    production_detail_id: Optional[int] = None
    roll_number: Optional[str] = None
    batch_number: Optional[str] = None
    thickness_actual: Optional[float] = None
    softness_actual: Optional[str] = None
    thickness_min: Optional[float] = None
    thickness_max: Optional[float] = None
    softness_standard: Optional[str] = None
    result: Optional[str] = None
    is_ok: Optional[bool] = None
    device_id: Optional[str] = None
    port: Optional[str] = None
    raw_value: Optional[str] = None
    remark: Optional[str] = None
    measured_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    qty_checked: Optional[float] = None
    qty_reject: Optional[float] = None
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
    delivery_zone: Optional[str] = None
    delivery_type: Optional[str] = None


class DeliveryCancelIn(BaseModel):
    reason: str = Field(..., min_length=1, max_length=2000)

    @field_validator("reason")
    @classmethod
    def reason_required(cls, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValueError("Alasan pembatalan wajib diisi")
        return text


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
    delivery_zone: Optional[str] = None
    delivery_type: Optional[str] = None


class DeliveryScanOutIn(BaseModel):
    delivery_number: Optional[str] = None
    packing_id: Optional[int] = None
    packing_number: Optional[str] = None


class DeliveryScanOutOut(BaseModel):
    ok: bool = True
    packing_id: Optional[int] = None
    delivery_id: Optional[int] = None
    delivery_number: Optional[str] = None
    marked_sent: list[int] = []
    already_sent: list[int] = []
    skipped: list[dict] = []
    message: str = ""


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


class DeliveryHeaderOut(ORMBase):
    id: int
    delivery_number: Optional[str] = None
    customer_id: Optional[int] = None
    delivery_date: Optional[date] = None
    driver_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    destination: Optional[str] = None
    bc_number: Optional[str] = None
    bc_date: Optional[date] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    packing_id: Optional[int] = None
    surat_jalan_printed_at: Optional[datetime] = None
    delivery_zone: Optional[str] = None
    delivery_type: Optional[str] = None
    customs_declaration_id: Optional[int] = None
    mrp_fg_id: Optional[int] = None
    cancel_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[str] = None


class DeliveryHeaderPageOut(BaseModel):
    items: list[DeliveryHeaderOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class DeliveryDetailOut(ORMBase):
    id: int
    delivery_id: Optional[int] = None
    production_detail_id: Optional[int] = None
    packing_detail_id: Optional[int] = None
    po_detail_id: Optional[int] = None
    qty: Optional[float] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight: Optional[float] = None
    returned_qty: Optional[float] = None


class DeliveryDetailReturnIn(BaseModel):
    qty: Decimal = Field(..., gt=0)
    remark: Optional[str] = None


class DeliveryDetailReturnOut(BaseModel):
    delivery_detail_id: int
    delivery_id: int
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    returned_qty: float
    return_qty_this: float
    unit_price: Optional[float] = None
    credit_amount: float
    credit_note_amount: Optional[float] = None
    remaining_returnable: float


class DeliveryDetailEnrichedOut(DeliveryDetailOut):
    po_id: Optional[int] = None
    po_number: str = ""
    po_customer_ref: str = ""
    po_detail_id: Optional[int] = None
    system_no: str = ""
    lot_number: str = ""
    material_name_line: str = ""
    thickness_display: str = ""
    color_line: str = ""
    leather_color: str = ""
    leather_in_date: str = ""
    order_type: str = ""


class MktWorkflowStagesOut(BaseModel):
    stages: list[str]


class MktWorkflowRollbackIn(BaseModel):
    reason: str


class StatusDeletedOut(BaseModel):
    status: str


class PackingHeaderOut(ORMBase):
    id: int
    packing_number: Optional[str] = None
    production_id: Optional[int] = None
    qc_header_id: Optional[int] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    invpl_printed_at: Optional[datetime] = None
    source: Optional[str] = None
    mrp_fg_id: Optional[int] = None
    mrp_packing_id: Optional[int] = None


class PackingHeaderPageOut(BaseModel):
    items: list[PackingHeaderOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class PackingDetailOut(ORMBase):
    id: int
    packing_id: Optional[int] = None
    production_detail_id: Optional[int] = None
    qty_packed: Optional[float] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight_net: Optional[float] = None


class PackingDetailEnrichedOut(PackingDetailOut):
    lot_no: str = ""
    so_number: str = ""
    material_name: str = ""
    qty_actual: Optional[float] = None


class PackingDetailUpdate(BaseModel):
    qty_packed: Optional[Decimal] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight_net: Optional[Decimal] = None


class PackingDetailBatchItem(BaseModel):
    production_detail_id: int
    qty_packed: Optional[Decimal] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight_net: Optional[Decimal] = None


class PackingDetailBatchIn(BaseModel):
    lines: list[PackingDetailBatchItem] = Field(default_factory=list)


class ReadyToShipLineOut(BaseModel):
    packing_id: int
    packing_number: str = ""
    packing_detail_id: Optional[int] = None
    production_detail_id: int
    lot_no: str = ""
    so_number: str = ""
    po_customer_ref: str = ""
    customer_id: Optional[int] = None
    customer_name: str = ""
    brand: str = ""
    material_name: str = ""
    qty_packed: float = 0
    qty_shipped: float = 0
    qty_available: float = 0
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight_net: Optional[float] = None


class DeliveryFromPackingLineIn(BaseModel):
    production_detail_id: int
    packing_id: Optional[int] = None
    packing_detail_id: Optional[int] = None
    qty: Optional[Decimal] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight: Optional[Decimal] = None


class DeliveryFromPackingLinesIn(BaseModel):
    packing_id: int
    customer_id: Optional[int] = None
    delivery_date: Optional[date] = None
    delivery_type: Optional[str] = "production"
    delivery_zone: Optional[str] = "outtown"
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    destination: Optional[str] = None
    lines: list[DeliveryFromPackingLineIn] = Field(default_factory=list)


class InvoiceOut(ORMBase):
    id: int
    delivery_id: Optional[int] = None
    customer_id: Optional[int] = None
    po_id: Optional[int] = None
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
    total_amount: Optional[float] = None
    total_in_words: Optional[str] = None
    due_date: Optional[date] = None
    tax_invoice_no: Optional[str] = None
    tax_invoice_date: Optional[date] = None
    receipt_no: Optional[str] = None
    received_by: Optional[str] = None
    received_date: Optional[date] = None
    nopen: Optional[str] = None
    nomor_aju: Optional[str] = None
    bc_date: Optional[date] = None
    bc_number: Optional[str] = None
    dokumen_bc: Optional[str] = None
    payment_date: Optional[date] = None
    payment_bank_account: Optional[str] = None
    payment_proof_url: Optional[str] = None
    payment_status: str = "unpaid"
    payment_amount: Optional[float] = None
    payment_remark: Optional[str] = None
    credit_note_no: Optional[str] = None
    credit_note_date: Optional[date] = None
    credit_note_amount: Optional[float] = None
    voided_at: Optional[datetime] = None
    void_reason: Optional[str] = None
    oia_export_usd: Optional[float] = None
    balance_after_deduct: Optional[float] = None
    deduction_amount: Optional[float] = None
    ar_status: Optional[str] = None
    remark: Optional[str] = None
    qty_total: Optional[float] = None
    payment_term_days: Optional[int] = None
    created_at: Optional[datetime] = None


class InvoicePageOut(BaseModel):
    items: list[InvoiceOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class InvoiceDetailOut(ORMBase):
    id: int
    invoice_id: Optional[int] = None
    item_description: Optional[str] = None
    color: Optional[str] = None
    qty: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    roll: Optional[int] = None
    pcs: Optional[int] = None
    net_weight: Optional[float] = None
    gross_weight: Optional[float] = None
    remark: Optional[str] = None


# --- Invoice ---
class InvoiceCreate(BaseModel):
    """delivery_id wajib — invoice hanya setelah delivery terkirim (status sent)."""

    delivery_id: int
    customer_id: Optional[int] = None
    po_id: Optional[int] = None
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
    bc_date: Optional[date] = None
    payment_date: Optional[date] = None
    payment_bank_account: Optional[str] = None
    payment_proof_url: Optional[str] = None
    payment_status: str = "unpaid"
    payment_amount: Optional[Decimal] = None
    payment_remark: Optional[str] = None
    credit_note_no: Optional[str] = None
    credit_note_date: Optional[date] = None
    credit_note_amount: Optional[Decimal] = None
    oia_export_usd: Optional[Decimal] = None


class InvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    po_id: Optional[int] = None
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
    bc_date: Optional[date] = None
    payment_date: Optional[date] = None
    payment_bank_account: Optional[str] = None
    payment_proof_url: Optional[str] = None
    payment_status: Optional[str] = None
    payment_amount: Optional[Decimal] = None
    payment_remark: Optional[str] = None
    credit_note_no: Optional[str] = None
    credit_note_date: Optional[date] = None
    credit_note_amount: Optional[Decimal] = None
    oia_export_usd: Optional[Decimal] = None


class TandaTerimaBatchIn(BaseModel):
    invoice_ids: list[int] = Field(..., min_length=1)
    received_by: Optional[str] = None
    received_date: Optional[date] = None
    receipt_no: Optional[str] = None
    stamp_invoices: bool = True


class AccountsReceivableReportOut(BaseModel):
    report_title: str
    year: int
    summary: dict
    rows: list[InvoiceOut]
    total: int
    limit: int
    offset: int


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
    category: str
    material_name: Optional[str] = None
    thickness_range: Optional[str] = None
    color: Optional[str] = None
    emboss: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_master_item_category(cls, v: str) -> str:
        raw = str(v or "").strip().lower()
        alias = {
            "pu": "PU",
            "suide": "Suede",
            "suede": "Suede",
            "subkon": "SubKon",
            "subcont": "SubKon",
            "subcontract": "SubKon",
        }
        out = alias.get(raw)
        if not out:
            raise ValueError("category harus salah satu: PU, Suede, SubKon")
        return out


class MasterItemOut(ORMBase):
    id: int
    item_code: str
    thickness_mm: Optional[Decimal] = None
    thickness_range: Optional[str] = None
    material_name: Optional[str] = None
    emboss: Optional[str] = None
    color: Optional[str] = None
    color_code: Optional[str] = None
    color_qualifier: Optional[str] = None
    in_csi: Optional[bool] = None
    in_swatch: Optional[bool] = None
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
    updated_at: Optional[datetime] = None


class MasterItemStatsOut(BaseModel):
    total: int
    pu: int
    suide: int
    subkon: int


class MasterItemPageOut(BaseModel):
    items: list[MasterItemOut]
    total: int
    limit: int
    offset: int
    page: int = 1
    page_size: int = 50
    stats: MasterItemStatsOut


class MasterItemDimensionValuesOut(BaseModel):
    """Nilai unik untuk cascade: material → ketebalan → warna → emboss → kode FG."""

    values: list[str] = Field(default_factory=list)


class MasterItemResolveByDimensionsOut(BaseModel):
    """Hasil resolve (material + ketebalan + warna + emboss) ke baris master_items."""

    status: Literal["single", "ambiguous", "none"]
    item: Optional[MasterItemOut] = None
    candidates: list[MasterItemOut] = Field(default_factory=list)


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



class BrandOut(ORMBase):
    id: int
    code: Optional[str] = None
    name: Optional[str] = None
    customer_id: Optional[int] = None
    customer_ids: Optional[list[int]] = None


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



class PpicsAssignmentCreate(BaseModel):
    po_id: int
    po_detail_id: Optional[int] = None
    # Opsional: kosong = serah terima otomatis ke tim PPIC (monitoring pool).
    ppic_user_id: Optional[int] = None
    notes: Optional[str] = None


class PpicsAssignmentUpdate(BaseModel):
    po_detail_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class PpicsAssignmentOut(ORMBase):
    id: int
    po_id: int
    po_detail_id: Optional[int] = None
    ppic_user_id: Optional[int] = None
    status: str
    notes: Optional[str] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    po_number: Optional[str] = None
    customer_name: Optional[str] = None
    ppic_username: Optional[str] = None
    item_revised_at: Optional[datetime] = None
    item_revised_has_update: bool = False
    item_revised_has_delete: bool = False
    assignment_mode: Optional[str] = None  # "auto" | "named"
class OutstandingScheduleLineIn(BaseModel):
    po_detail_id: int
    delivery_date: date
    qty: Optional[Decimal] = None
    sequence_no: Optional[int] = None


class OutstandingScheduleBatchIn(BaseModel):
    """Tambah slot jadwal kirim ke baris outstanding (boleh lintas SO)."""

    lines: list[OutstandingScheduleLineIn] = Field(default_factory=list)
    mode: Literal["append", "replace"] = "append"


class OutstandingScheduleBatchOut(BaseModel):
    ok: bool = True
    updated_count: int = 0
    po_detail_ids: list[int] = Field(default_factory=list)


class OutstandingPackingOptionOut(BaseModel):
    po_detail_id: int
    packing_id: int
    packing_number: str = ""
    packing_detail_id: Optional[int] = None
    production_detail_id: int
    lot_no: str = ""
    so_number: str = ""
    customer_id: Optional[int] = None
    customer_name: str = ""
    brand: str = ""
    material_name: str = ""
    qty_available: float = 0
    qty_packed: float = 0
    qty_shipped: float = 0
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None


class OutstandingPackingOptionsOut(BaseModel):
    data: list[OutstandingPackingOptionOut] = Field(default_factory=list)
    total: int = 0


class OutstandingShipLineIn(BaseModel):
    po_detail_id: int
    packing_id: int
    packing_detail_id: Optional[int] = None
    production_detail_id: int
    qty: Optional[Decimal] = None
    delivery_date: Optional[date] = None


class OutstandingShipBatchIn(BaseModel):
    """Susun delivery dari packing list terpilih per baris outstanding."""

    lines: list[OutstandingShipLineIn] = Field(default_factory=list)
    delivery_type: Optional[str] = "production"
    delivery_zone: Optional[str] = "outtown"
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    destination: Optional[str] = None


class OutstandingShipBatchOut(BaseModel):
    ok: bool = True
    delivery_ids: list[int] = Field(default_factory=list)
    delivery_numbers: list[str] = Field(default_factory=list)
    delivery_count: int = 0
    message: str = ""



class WarehouseCreate(BaseModel):
    code: str
    name: str
    location: Optional[str] = None
    is_active: bool = True


class WarehouseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseOut(ORMBase):
    id: int
    code: str
    name: str
    location: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


class InventoryUnitMasterCreate(BaseModel):
    material_type: str
    unit: str
    is_active: bool = True


class InventoryUnitMasterUpdate(BaseModel):
    material_type: Optional[str] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class InventoryUnitMasterOut(ORMBase):
    id: int
    material_type: str
    unit: str
    is_active: bool
    created_at: Optional[datetime] = None


class RawMaterialCreate(BaseModel):
    code: str
    name: str
    material_type: str
    unit: str
    default_warehouse_id: Optional[int] = None
    min_stock: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    thickness: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    leather_type: Optional[str] = None
    is_active: bool = True


class RawMaterialUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    material_type: Optional[str] = None
    unit: Optional[str] = None
    default_warehouse_id: Optional[int] = None
    min_stock: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    thickness: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    leather_type: Optional[str] = None
    is_active: Optional[bool] = None


class RawMaterialOut(ORMBase):
    id: int
    code: str
    name: str
    material_type: str
    unit: str
    default_warehouse_id: Optional[int] = None
    min_stock: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    thickness: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    leather_type: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


class MaterialStockOut(ORMBase):
    id: int
    material_id: int
    warehouse_id: int
    current_stock: Decimal
    reserved_stock: Decimal
    updated_at: Optional[datetime] = None
    material: Optional[RawMaterialOut] = None
    warehouse: Optional[WarehouseOut] = None

class QuotationLineCreate(BaseModel):
    master_item_id: Optional[int] = None
    item_code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    specification: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = "S/F"
    unit_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None


class QuotationLineUpdate(BaseModel):
    item_code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    specification: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None


class QuotationLineOut(ORMBase):
    id: int
    quotation_id: int
    line_no: int
    master_item_id: Optional[int] = None
    item_code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    specification: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    line_amount: Optional[Decimal] = None


class QuotationHeaderCreate(BaseModel):
    customer_id: Optional[int] = None
    quotation_date: Optional[date] = None
    currency: Optional[str] = "USD"
    payment_terms: Optional[str] = None
    valid_until: Optional[date] = None
    salesperson: Optional[str] = None
    remark: Optional[str] = None
    status: str = "draft"


class QuotationHeaderUpdate(BaseModel):
    customer_id: Optional[int] = None
    quotation_date: Optional[date] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    valid_until: Optional[date] = None
    salesperson: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[str] = None


class QuotationHeaderOut(ORMBase):
    id: int
    quotation_number: Optional[str] = None
    customer_id: Optional[int] = None
    quotation_date: Optional[date] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    valid_until: Optional[date] = None
    salesperson: Optional[str] = None
    remark: Optional[str] = None
    status: str = "draft"
    total_amount: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    lines: Optional[list[QuotationLineOut]] = None
    customer_name: Optional[str] = None

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


class OutstandingMaterialCreate(BaseModel):
    po_detail_id: int
    material_name: Optional[str] = None
    total_qty: Optional[Decimal] = None
    delivered_qty: Optional[Decimal] = None
    balance_qty: Optional[Decimal] = None
    status: str = "pending"


class OutstandingMaterialUpdate(BaseModel):
    material_name: Optional[str] = None
    total_qty: Optional[Decimal] = None
    delivered_qty: Optional[Decimal] = None
    balance_qty: Optional[Decimal] = None
    status: Optional[str] = None


class OutstandingMaterialOut(ORMBase):
    id: int
    po_detail_id: int
    material_name: Optional[str] = None
    total_qty: Optional[Decimal] = None
    delivered_qty: Optional[Decimal] = None
    balance_qty: Optional[Decimal] = None
    status: str
    updated_at: Optional[datetime] = None
    po_number: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None


class OutstandingMaterialPageOut(BaseModel):
    items: list[OutstandingMaterialOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    limit: int = 20
    offset: int = 0


class AccountingMappingCreate(BaseModel):
    transaction_type: str
    status: Optional[str] = None
    coa_code: str
    coa_name: str
    description: Optional[str] = None


class AccountingMappingUpdate(BaseModel):
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    coa_code: Optional[str] = None
    coa_name: Optional[str] = None
    description: Optional[str] = None


class AccountingMappingOut(ORMBase):
    id: int
    transaction_type: str
    status: Optional[str] = None
    coa_code: str
    coa_name: str
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


class AccountingMappingResolveOut(BaseModel):
    coa_code: Optional[str] = None
    coa_name: Optional[str] = None
    found: bool = False


class JournalEntryOut(ORMBase):
    id: int
    transaction_type: str
    transaction_id: int
    coa_code: str
    coa_name: str
    debit: Decimal
    credit: Decimal
    description: Optional[str] = None
    entry_date: date
    created_at: Optional[datetime] = None


class JournalEntryGenerate(BaseModel):
    transaction_type: str
    transaction_id: int


class TrialBalanceRow(BaseModel):
    coa_code: str
    coa_name: str

class TrialBalanceReport(BaseModel):
    as_of_date: date
    rows: list[TrialBalanceRow]
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool


class MaterialReceiptDetailCreate(BaseModel):
    material_id: int
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    remark: Optional[str] = None


class MaterialReceiptCreate(BaseModel):
    receipt_number: Optional[str] = None
    supplier_name: Optional[str] = None
    receipt_date: date
    warehouse_id: int
    total_amount: Optional[Decimal] = None
    remark: Optional[str] = None
    status: str = "draft"
    details: list[MaterialReceiptDetailCreate] = Field(default_factory=list)


class MaterialReceiptUpdate(BaseModel):
    supplier_name: Optional[str] = None
    receipt_date: Optional[date] = None
    warehouse_id: Optional[int] = None
    total_amount: Optional[Decimal] = None
    remark: Optional[str] = None
    status: Optional[str] = None


class MaterialReceiptDetailOut(ORMBase):
    id: int
    receipt_id: int
    material_id: int
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    remark: Optional[str] = None
    material: Optional[RawMaterialOut] = None


class MaterialReceiptOut(ORMBase):
    id: int
    receipt_number: str
    supplier_name: Optional[str] = None
    receipt_date: date
    warehouse_id: int
    total_amount: Optional[Decimal] = None
    remark: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    warehouse: Optional[WarehouseOut] = None
    details: list[MaterialReceiptDetailOut] = Field(default_factory=list)
