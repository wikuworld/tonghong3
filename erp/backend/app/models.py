"""Model SQLAlchemy; migrasi DB: Alembic (`alembic/versions/`)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    contact_person: Mapped[Optional[str]] = mapped_column(String(255))
    position: Mapped[Optional[str]] = mapped_column(String(120))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    city: Mapped[Optional[str]] = mapped_column(String(120))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    tax_id: Mapped[Optional[str]] = mapped_column(String(32))
    skep_kb_number: Mapped[Optional[str]] = mapped_column(String(80))
    customs_office_code: Mapped[Optional[str]] = mapped_column(String(32))
    address: Mapped[Optional[str]] = mapped_column(Text)
    billing_address: Mapped[Optional[str]] = mapped_column(Text)
    remark: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_export_customer: Mapped[bool] = mapped_column(Boolean, default=False)
    outside_banten: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    outside_price_adjust: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 4), nullable=True
    )
    outside_adjust_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    discount_modifier_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    discount_modifier: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 4), nullable=True
    )
    discount_modifier_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    default_currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    tax_mode: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    reference_quotation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    wilayah_province_code: Mapped[Optional[str]] = mapped_column(String(8))
    wilayah_regency_code: Mapped[Optional[str]] = mapped_column(String(16))
    wilayah_district_code: Mapped[Optional[str]] = mapped_column(String(24))
    wilayah_village_code: Mapped[Optional[str]] = mapped_column(String(32))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    brand_mappings: Mapped[list["CustomerBrandMapping"]] = relationship(
        "CustomerBrandMapping", back_populates="customer", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["CustomerPic"]] = relationship(
        "CustomerPic", cascade="all, delete-orphan"
    )
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", overlaps="customer")


class MasterItem(Base):
    """Master FG / barang jadi (sheet Master Item)."""

    __tablename__ = "master_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_code: Mapped[str] = mapped_column(String(50), unique=True)
    thickness_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    thickness_range: Mapped[Optional[str]] = mapped_column(String(80))
    material_name: Mapped[Optional[str]] = mapped_column(String(500))
    emboss: Mapped[Optional[str]] = mapped_column(String(500))
    color: Mapped[Optional[str]] = mapped_column(String(500))
    color_code: Mapped[Optional[str]] = mapped_column(String(64))
    color_qualifier: Mapped[Optional[str]] = mapped_column(String(64))
    softness: Mapped[Optional[str]] = mapped_column(String(100))
    color_reference: Mapped[Optional[str]] = mapped_column(String(255))
    color_standard: Mapped[Optional[str]] = mapped_column(String(255))
    model_takedown: Mapped[Optional[str]] = mapped_column(String(100))
    backing: Mapped[Optional[str]] = mapped_column(String(255))
    quantity_order_default: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    style_article: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    flag_color_black: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    flag_color: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    flag_flourasent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    flag_metalic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    flag_emboss: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    flag_special_emboss: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    exim_material_code: Mapped[Optional[str]] = mapped_column(String(80))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    po_details: Mapped[list["PoDetail"]] = relationship(
        "PoDetail", back_populates="master_item"
    )


class MasterPrice(Base):
    """Matrix harga material (sheet Master Harga)."""

    __tablename__ = "master_prices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    line_no: Mapped[Optional[int]] = mapped_column(Integer)
    material_category: Mapped[Optional[str]] = mapped_column(String(255))
    material_type: Mapped[Optional[str]] = mapped_column(String(255))
    material_name: Mapped[Optional[str]] = mapped_column(String(500))
    thickness_range: Mapped[Optional[str]] = mapped_column(String(80))
    price_white_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    price_black_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    price_color_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    price_metallic_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    remark: Mapped[Optional[str]] = mapped_column(String(255))
    price_tier: Mapped[Optional[str]] = mapped_column(String(32))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class CustomsDeclaration(Base):
    """Dokumen pabean (AJU) — snapshot lengkap per sheet sebagai baris JSON."""

    __tablename__ = "customs_declarations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nomor_aju: Mapped[str] = mapped_column(String(64), unique=True)
    kode_dokumen: Mapped[Optional[str]] = mapped_column(String(16))
    source_label: Mapped[Optional[str]] = mapped_column(String(255))
    versi_template: Mapped[Optional[str]] = mapped_column(String(32))
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    sheet_rows: Mapped[list["CustomsAjuSheetRow"]] = relationship(
        "CustomsAjuSheetRow",
        back_populates="declaration",
        cascade="all, delete-orphan",
    )


class CustomsAjuSheetRow(Base):
    __tablename__ = "customs_aju_sheet_rows"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    declaration_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("customs_declarations.id", ondelete="CASCADE")
    )
    sheet_code: Mapped[str] = mapped_column(String(64))
    row_number: Mapped[int] = mapped_column(Integer, default=0)
    cells: Mapped[dict] = mapped_column(JSON)

    declaration: Mapped["CustomsDeclaration"] = relationship(
        "CustomsDeclaration", back_populates="sheet_rows"
    )


class BuyerPriceList(Base):
    """List harga material per brand/buyer. Satu brand boleh punya banyak list selama periode tidak bertumpuk."""

    __tablename__ = "buyer_price_lists"
    __table_args__ = (Index("ix_buyer_price_lists_brand_id", "brand_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_code: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("buyer_codes.code", ondelete="RESTRICT"),
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("brands.id", ondelete="RESTRICT"), nullable=True
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    title: Mapped[Optional[str]] = mapped_column(Text)
    period_label: Mapped[Optional[str]] = mapped_column(Text)
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    period_end: Mapped[Optional[date]] = mapped_column(Date)
    meta_json: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    rows: Mapped[list["BuyerPriceSheetRow"]] = relationship(
        "BuyerPriceSheetRow",
        back_populates="price_list",
        cascade="all, delete-orphan",
    )
    brand: Mapped[Optional["Brand"]] = relationship("Brand")


class BuyerPriceSheetRow(Base):
    __tablename__ = "buyer_price_sheet_rows"
    __table_args__ = (
        UniqueConstraint("list_id", "row_number", name="uq_buyer_price_sheet_rows_list_row"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    list_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("buyer_price_lists.id", ondelete="CASCADE"))
    row_number: Mapped[int] = mapped_column(Integer, default=0)
    cells: Mapped[dict] = mapped_column(JSON)

    price_list: Mapped["BuyerPriceList"] = relationship("BuyerPriceList", back_populates="rows")


class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = (UniqueConstraint("code", name="uq_brands_code"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[Optional[str]] = mapped_column(String(50))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    customer_mappings: Mapped[list["CustomerBrandMapping"]] = relationship(
        "CustomerBrandMapping", back_populates="brand"
    )


class BuyerCode(Base):
    """Registry kode buyer resmi (master integrity)."""

    __tablename__ = "buyer_codes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class MaterialAlias(Base):
    """Alias material kotor → nama kanonik (resolve runtime)."""

    __tablename__ = "material_aliases"
    __table_args__ = (UniqueConstraint("alias_name", name="uq_material_aliases_alias"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    alias_name: Mapped[str] = mapped_column(String(500))
    canonical_name: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class CustomerBrandMapping(Base):
    __tablename__ = "customer_brand_mappings"
    __table_args__ = (
        UniqueConstraint("customer_id", "brand_id", name="uq_customer_brand"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="RESTRICT")
    )
    brand_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("brands.id", ondelete="RESTRICT")
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="brand_mappings")
    brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="customer_mappings")


class BrandConstraint(Base):
    __tablename__ = "brand_constraints"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    allowed_brand_ids: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)


class BrandBuyerMap(Base):
    __tablename__ = "brand_buyer_maps"
    __table_args__ = (
        UniqueConstraint("brand_id", "buyer_code", name="uq_brand_buyer_map"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("brands.id", ondelete="CASCADE")
    )
    buyer_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("buyer_codes.code", ondelete="RESTRICT")
    )


class ColorWindowMaster(Base):
    """Master Color Window — katalog color code per brand."""

    __tablename__ = "color_window_masters"
    __table_args__ = (
        Index("ix_color_window_masters_brand", "brand_code"),
        Index("ix_color_window_masters_code", "color_code"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    color_code: Mapped[str] = mapped_column(String(64))
    color_name: Mapped[str] = mapped_column(String(255))
    brand_code: Mapped[str] = mapped_column(String(50))
    remark: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CsiColorMaster(Base):
    """Katalog warna resmi per buyer (CSI ALL BUYER)."""

    __tablename__ = "csi_color_masters"
    __table_args__ = (
        UniqueConstraint("buyer_code", "color_code", name="uq_csi_color_master"),
        Index("ix_csi_color_masters_buyer", "buyer_code"),
        Index("ix_csi_color_masters_code", "color_code"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("buyer_codes.code", ondelete="RESTRICT")
    )
    color_code: Mapped[str] = mapped_column(String(64))
    color_name: Mapped[str] = mapped_column(String(255))
    source_file: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    aliases: Mapped[list["ColorCodeAlias"]] = relationship(
        "ColorCodeAlias", back_populates="csi_color"
    )
    swatch_recipes: Mapped[list["ColorSwatchRecipe"]] = relationship(
        "ColorSwatchRecipe", back_populates="csi_color"
    )


class ColorCodeAlias(Base):
    """XREF: alias sumber (COLORO/swatch/item) → CSI golden record."""

    __tablename__ = "color_code_aliases"
    __table_args__ = (
        UniqueConstraint(
            "buyer_code",
            "source_system",
            "alias_code",
            name="uq_color_code_alias_source",
        ),
        Index("ix_color_code_aliases_csi", "csi_color_master_id"),
        Index("ix_color_code_aliases_alias", "alias_code"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("buyer_codes.code", ondelete="RESTRICT")
    )
    source_system: Mapped[str] = mapped_column(String(32), default="SWATCH")
    alias_code: Mapped[str] = mapped_column(String(64))
    csi_color_master_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("csi_color_masters.id", ondelete="SET NULL")
    )
    match_method: Mapped[str] = mapped_column(String(32), default="dual_parse")
    steward_status: Mapped[str] = mapped_column(String(16), default="pending")
    source_file: Mapped[Optional[str]] = mapped_column(String(255))
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    csi_color: Mapped[Optional["CsiColorMaster"]] = relationship(
        "CsiColorMaster", back_populates="aliases"
    )


class ColorSwatchRecipe(Base):
    """Resep warna operasional (pabrik × buyer × material × emboss × kode warna)."""

    __tablename__ = "color_swatch_recipes"
    __table_args__ = (
        UniqueConstraint(
            "factory_key",
            "buyer_code",
            "color_code",
            "material_name",
            "emboss",
            "color_standard",
            name="uq_color_swatch_recipe_key",
        ),
        Index("ix_color_swatch_factory_key", "factory_key"),
        Index("ix_color_swatch_buyer_code", "buyer_code"),
        Index("ix_color_swatch_material_name", "material_name", mysql_length=191),
        Index("ix_color_swatch_color_code", "color_code"),
        Index("ix_color_swatch_csi_id", "csi_color_master_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    factory_key: Mapped[str] = mapped_column(String(80))
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="SET NULL")
    )
    buyer_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("buyer_codes.code", ondelete="RESTRICT")
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("brands.id", ondelete="SET NULL")
    )
    csi_color_master_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("csi_color_masters.id", ondelete="SET NULL")
    )
    color_code: Mapped[str] = mapped_column(String(64), default="")
    color_name: Mapped[str] = mapped_column(String(255), default="")
    emboss: Mapped[str] = mapped_column(String(255), default="")
    color_standard: Mapped[Optional[str]] = mapped_column(String(255))
    backing: Mapped[Optional[str]] = mapped_column(String(120))
    material_name: Mapped[str] = mapped_column(String(500), default="")
    legacy_urut: Mapped[Optional[str]] = mapped_column(String(32))
    entered_at: Mapped[Optional[date]] = mapped_column(Date)
    source_file: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    brand: Mapped[Optional["Brand"]] = relationship("Brand")
    csi_color: Mapped[Optional["CsiColorMaster"]] = relationship(
        "CsiColorMaster", back_populates="swatch_recipes"
    )
    po_details: Mapped[list["PoDetail"]] = relationship("PoDetail", back_populates="color_swatch_recipe")


class FluorescentColorMaster(Base):
    """Master warna fluorescent/metallic per buyer + season."""

    __tablename__ = "fluorescent_color_masters"
    __table_args__ = (
        UniqueConstraint(
            "buyer_code",
            "season_label",
            "color_code",
            "color_name",
            name="uq_fluorescent_color_master",
        ),
        Index("ix_fluorescent_color_masters_buyer", "buyer_code"),
        Index("ix_fluorescent_color_masters_season", "season_label"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_code: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("buyer_codes.code", ondelete="RESTRICT"),
        default="GLOBAL",
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("brands.id", ondelete="SET NULL")
    )
    season_label: Mapped[Optional[str]] = mapped_column(String(64))
    season_year: Mapped[Optional[int]] = mapped_column(Integer)
    season_type: Mapped[Optional[str]] = mapped_column(String(16))
    color_name: Mapped[str] = mapped_column(String(255))
    color_code: Mapped[Optional[str]] = mapped_column(String(64))
    color_class: Mapped[str] = mapped_column(String(32), default="fluorescent")
    source_file: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    brand: Mapped[Optional["Brand"]] = relationship("Brand")


class CustomerPic(Base):
    __tablename__ = "customer_pics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="CASCADE")
    )
    name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    title: Mapped[Optional[str]] = mapped_column(String(120))

    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="contacts")






class PoHeader(Base):
    __tablename__ = "po_headers"
    __table_args__ = (
        Index("ix_po_headers_customer_id", "customer_id"),
        Index("ix_po_headers_status", "status"),
        Index("ix_po_headers_mkt_workflow_stage", "mkt_workflow_stage"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    customer_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("customers.id"))
    customer_code: Mapped[Optional[str]] = mapped_column(String(50))
    po_category: Mapped[str] = mapped_column(String(32), default="production")
    # Kode pabrik/factory untuk kebutuhan nomor lot & filter outstanding
    factory_code: Mapped[Optional[str]] = mapped_column(String(32))
    buyer: Mapped[Optional[str]] = mapped_column(String(100))
    order_date: Mapped[Optional[date]] = mapped_column(Date)
    etd: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    billing_address: Mapped[Optional[str]] = mapped_column(Text)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)
    brand_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("brands.id"))
    marketing_excel_date_serial: Mapped[Optional[int]] = mapped_column(Integer)
    po_customer_ref: Mapped[Optional[str]] = mapped_column(Text)
    po_customer_ref_norm: Mapped[Optional[str]] = mapped_column(String(255))
    order_type_label: Mapped[Optional[str]] = mapped_column(String(50))
    brand_name_snapshot: Mapped[Optional[str]] = mapped_column(String(255))
    customer_name_snapshot: Mapped[Optional[str]] = mapped_column(String(255))
    customs_declaration_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("customs_declarations.id", ondelete="SET NULL")
    )
    # Alur MKT (flowchart: PO → rekap → PPIC → MKT → outstanding → material → delivery → SJ/INVPL → invoice)
    mkt_workflow_stage: Mapped[str] = mapped_column(String(48), default="input_system")
    mkt_workflow_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rekap_printed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Tanda untuk PPIC/marketing/admin: ada baris item yang diedit atau dihapus
    item_revised_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    item_revised_has_update: Mapped[bool] = mapped_column(Boolean, default=False)
    item_revised_has_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    material_followup_remark: Mapped[Optional[str]] = mapped_column(Text)
    material_followup_done: Mapped[bool] = mapped_column(Boolean, default=False)

    details: Mapped[list["PoDetail"]] = relationship(
        "PoDetail", back_populates="po", cascade="all, delete-orphan"
    )
    customs_declaration: Mapped[Optional["CustomsDeclaration"]] = relationship(
        "CustomsDeclaration",
        foreign_keys=[customs_declaration_id],
    )
    ppic_assignments: Mapped[list["PpicsAssignment"]] = relationship(
        "PpicsAssignment", back_populates="po", cascade="all, delete-orphan"
    )
    production_orders: Mapped[list["ProductionOrder"]] = relationship("ProductionOrder", back_populates="po")
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="po")


class PoDetail(Base):
    __tablename__ = "po_details"
    __table_args__ = (
        Index("ix_po_details_po_id", "po_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("po_headers.id", ondelete="CASCADE"))
    master_item_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("master_items.id", ondelete="SET NULL"))
    thi_line_ref: Mapped[Optional[str]] = mapped_column(String(100))
    material_name: Mapped[Optional[str]] = mapped_column(String(255))
    color: Mapped[Optional[str]] = mapped_column(String(100))
    color_family: Mapped[Optional[str]] = mapped_column(String(32))
    thickness_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    thickness_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    thickness_text: Mapped[Optional[str]] = mapped_column(String(80))
    emboss: Mapped[Optional[str]] = mapped_column(String(255))
    vir_softness_type: Mapped[Optional[str]] = mapped_column(String(100))
    softness: Mapped[Optional[str]] = mapped_column(String(100))
    color_reference: Mapped[Optional[str]] = mapped_column(String(255))
    color_standard: Mapped[Optional[str]] = mapped_column(String(255))
    backing: Mapped[Optional[str]] = mapped_column(String(255))
    quantity_order: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    style_article: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    line_etd: Mapped[Optional[date]] = mapped_column(Date)
    rtd_text: Mapped[Optional[str]] = mapped_column(String(80))
    etd_excel_serial: Mapped[Optional[int]] = mapped_column(Integer)
    stock_wh_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    balance_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    system_reference: Mapped[Optional[str]] = mapped_column(String(120))
    detail_remark: Mapped[Optional[str]] = mapped_column(Text)
    marketing_outstanding_remark: Mapped[Optional[str]] = mapped_column(Text)
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    is_special_price: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    discount_type: Mapped[Optional[str]] = mapped_column(String(20))
    discount_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    list_unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    copied_from_detail_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    color_swatch_recipe_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("color_swatch_recipes.id", ondelete="SET NULL")
    )

    po: Mapped[Optional[PoHeader]] = relationship("PoHeader", back_populates="details")
    master_item: Mapped[Optional["MasterItem"]] = relationship(
        "MasterItem", back_populates="po_details"
    )
    color_swatch_recipe: Mapped[Optional["ColorSwatchRecipe"]] = relationship(
        "ColorSwatchRecipe", back_populates="po_details"
    )
    delivery_schedules: Mapped[list["PoDetailDelivery"]] = relationship(
        "PoDetailDelivery",
        back_populates="po_detail",
        cascade="all, delete-orphan",
    )


class PoDetailDelivery(Base):
    """Jadwal pengiriman gelombang 1–8 per baris SO (sheet outstanding marketing)."""

    __tablename__ = "po_detail_deliveries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_detail_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_details.id", ondelete="CASCADE"))
    sequence_no: Mapped[int] = mapped_column(Integer)
    qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    delivery_date: Mapped[Optional[date]] = mapped_column(Date)

    po_detail: Mapped["PoDetail"] = relationship("PoDetail", back_populates="delivery_schedules")


class MarketingOutstandingSnapshot(Base):
    """Bekuan baris outstanding marketing (audit / bandingkan dengan data live)."""

    __tablename__ = "marketing_outstanding_snapshots"
    __table_args__ = (Index("ix_mkt_out_snap_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    label: Mapped[Optional[str]] = mapped_column(String(255))
    filter_params_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    rows_json: Mapped[list] = mapped_column(JSON, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    created_by_username: Mapped[Optional[str]] = mapped_column(String(100))


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    production_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    po_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("po_headers.id"))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="planned")
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    po: Mapped[Optional["PoHeader"]] = relationship("PoHeader", back_populates="production_orders")


class ProductionDetail(Base):
    __tablename__ = "production_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    production_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("production_orders.id", ondelete="CASCADE")
    )
    po_detail_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("po_details.id", ondelete="CASCADE")
    )
    qty_planned: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    qty_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    lot_number: Mapped[Optional[str]] = mapped_column(String(100))
    batch_number: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    is_over_production: Mapped[Optional[bool]] = mapped_column(Boolean)


class QcHeader(Base):
    __tablename__ = "qc_headers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    qc_number: Mapped[Optional[str]] = mapped_column(String(100))
    production_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("production_orders.id"))
    po_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("po_headers.id"))
    qc_date: Mapped[Optional[date]] = mapped_column(Date)
    operator_name: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class QcDetail(Base):
    __tablename__ = "qc_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    qc_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("qc_headers.id", ondelete="CASCADE"))
    production_detail_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("production_details.id")
    )
    roll_number: Mapped[Optional[str]] = mapped_column(String(50))
    batch_number: Mapped[Optional[str]] = mapped_column(String(100))
    thickness_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    softness_actual: Mapped[Optional[str]] = mapped_column(String(100))
    thickness_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    thickness_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    softness_standard: Mapped[Optional[str]] = mapped_column(String(100))
    result: Mapped[Optional[str]] = mapped_column(String(8))
    is_ok: Mapped[Optional[bool]] = mapped_column(Boolean)
    device_id: Mapped[Optional[str]] = mapped_column(String(50))
    port: Mapped[Optional[str]] = mapped_column(String(20))
    raw_value: Mapped[Optional[str]] = mapped_column(String(100))
    remark: Mapped[Optional[str]] = mapped_column(Text)
    measured_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    qty_checked: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    qty_reject: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    reject_reason: Mapped[Optional[str]] = mapped_column(Text)


class PackingHeader(Base):
    __tablename__ = "packing_headers"
    __table_args__ = (
        Index("ix_packing_headers_mrp_fg_id", "mrp_fg_id", unique=True),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    packing_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    production_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("production_orders.id"))
    qc_header_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("qc_headers.id"))
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    invpl_printed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # erp = alur Production/QC ERP; mrp = packing siap kirim dari packing finish MRP
    source: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, default="erp")
    mrp_packing_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mrp_fg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)


class PackingDetail(Base):
    __tablename__ = "packing_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    packing_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("packing_headers.id", ondelete="CASCADE")
    )
    production_detail_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("production_details.id")
    )
    qty_packed: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    qty_roll: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    qty_pcs: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_net: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3), nullable=True)


class DeliveryHeader(Base):
    __tablename__ = "delivery_headers"
    __table_args__ = (
        Index("ix_delivery_headers_customer_id", "customer_id"),
        Index("ix_delivery_headers_mrp_fg_id", "mrp_fg_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    delivery_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    customer_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("customers.id"))
    delivery_date: Mapped[Optional[date]] = mapped_column(Date)
    driver_name: Mapped[Optional[str]] = mapped_column(String(100))
    vehicle_number: Mapped[Optional[str]] = mapped_column(String(50))
    destination: Mapped[Optional[str]] = mapped_column(Text)
    bc_number: Mapped[Optional[str]] = mapped_column(String(80))
    bc_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    packing_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("packing_headers.id"))
    surat_jalan_printed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # local = dalam kota (commercial invoice H+1); outtown = luar kota (boleh hari pengiriman setelah INVPL)
    delivery_zone: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    # production / sample / return / subcont / claim — terpisah dari teks destination/remark
    delivery_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_foc: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    delete_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customs_declaration_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("customs_declarations.id", ondelete="SET NULL")
    )
    mrp_fg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="delivery")
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    customs_declaration: Mapped[Optional["CustomsDeclaration"]] = relationship(
        "CustomsDeclaration",
        foreign_keys=[customs_declaration_id],
    )


class DeliveryDetail(Base):
    __tablename__ = "delivery_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    delivery_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("delivery_headers.id", ondelete="CASCADE")
    )
    production_detail_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("production_details.id")
    )
    packing_detail_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("packing_details.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Jalur MRP FG OUT: taut langsung ke baris PO tanpa ProductionDetail
    po_detail_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("po_details.id", ondelete="SET NULL"), nullable=True, index=True
    )
    qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    qty_roll: Mapped[Optional[int]] = mapped_column(Integer)
    qty_pcs: Mapped[Optional[int]] = mapped_column(Integer)
    weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    # Akumulasi qty retur barang setelah SJ/invoice (ledger; tidak mengurangi qty kirim historis)
    returned_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)


class ProformaInvoiceRecord(Base):
    """Catatan PI yang sudah digenerate (nomor resmi + scope SO/baris)."""

    __tablename__ = "proforma_invoice_records"
    __table_args__ = (Index("ix_proforma_invoice_records_customer_id", "customer_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pi_number: Mapped[str] = mapped_column(String(120), unique=True)
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    customer_name: Mapped[Optional[str]] = mapped_column(String(255))
    po_ids_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    po_detail_ids_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    total_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("delivery_id", name="uq_invoices_delivery_id"),
        Index("ix_invoices_customer_id", "customer_id"),
        Index("ix_invoices_po_id", "po_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    delivery_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("delivery_headers.id", ondelete="RESTRICT"), nullable=True
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=True
    )
    po_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("po_headers.id", ondelete="RESTRICT"), nullable=True
    )
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))
    packing_list_number: Mapped[Optional[str]] = mapped_column(String(100))
    po_number: Mapped[Optional[str]] = mapped_column(String(100))
    customer_name: Mapped[Optional[str]] = mapped_column(String(255))
    customer_address: Mapped[Optional[str]] = mapped_column(Text)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(50))
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    term_of_payment: Mapped[Optional[str]] = mapped_column(String(100))
    bank_name: Mapped[Optional[str]] = mapped_column(String(255))
    account_number: Mapped[Optional[str]] = mapped_column(String(100))
    bank_address: Mapped[Optional[str]] = mapped_column(Text)
    bank_phone: Mapped[Optional[str]] = mapped_column(String(50))
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    total_in_words: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    tax_invoice_no: Mapped[Optional[str]] = mapped_column(String(80))
    tax_invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    receipt_no: Mapped[Optional[str]] = mapped_column(String(80))
    received_by: Mapped[Optional[str]] = mapped_column(String(120))
    received_date: Mapped[Optional[date]] = mapped_column(Date)
    nopen: Mapped[Optional[str]] = mapped_column(String(80))
    nomor_aju: Mapped[Optional[str]] = mapped_column(String(80))
    bc_date: Mapped[Optional[date]] = mapped_column(Date)
    payment_date: Mapped[Optional[date]] = mapped_column(Date)
    payment_bank_account: Mapped[Optional[str]] = mapped_column(String(100))
    payment_proof_url: Mapped[Optional[str]] = mapped_column(String(500))
    payment_status: Mapped[str] = mapped_column(String(20), default="unpaid")
    payment_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    payment_remark: Mapped[Optional[str]] = mapped_column(String(120))
    credit_note_no: Mapped[Optional[str]] = mapped_column(String(120))
    credit_note_date: Mapped[Optional[date]] = mapped_column(Date)
    credit_note_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    voided_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    void_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    oia_export_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    po: Mapped[Optional["PoHeader"]] = relationship("PoHeader")
    delivery: Mapped[Optional["DeliveryHeader"]] = relationship("DeliveryHeader", back_populates="invoices")


class InvoiceDetail(Base):
    __tablename__ = "invoice_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("invoices.id", ondelete="CASCADE")
    )
    item_description: Mapped[Optional[str]] = mapped_column(String(255))
    color: Mapped[Optional[str]] = mapped_column(String(100))
    qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    roll: Mapped[Optional[int]] = mapped_column("roll", Integer, nullable=True)
    pcs: Mapped[Optional[int]] = mapped_column(Integer)
    net_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    gross_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    remark: Mapped[Optional[str]] = mapped_column(Text)


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    idr_per_usd: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    effective_date: Mapped[date] = mapped_column(Date)
    valid_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valid_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(40))
    payload_before: Mapped[Optional[str]] = mapped_column(Text)
    payload_after: Mapped[Optional[str]] = mapped_column(Text)
    actor: Mapped[Optional[str]] = mapped_column(String(120))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class DocumentSequence(Base):
    __tablename__ = "document_sequences"
    __table_args__ = (
        UniqueConstraint("doc_type", "period", name="uq_document_sequences_doc_period"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    doc_type: Mapped[str] = mapped_column(String(20))
    period: Mapped[str] = mapped_column(String(10))
    last_value: Mapped[int] = mapped_column(Integer, default=0)


class LotSequence(Base):
    """Sequence harian per prefix+factory untuk nomor lot produksi/suede/PU."""

    __tablename__ = "lot_sequences"
    __table_args__ = (
        UniqueConstraint(
            "prefix",
            "factory_code",
            "date_ymd",
            name="uq_lot_sequences_prefix_factory_date",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # Contoh: MYC, SYC, BYC, QYC, KYC, PUM, PUS, PUC, PUR, PUK
    prefix: Mapped[str] = mapped_column(String(8))
    # Kode pabrik, mis. LR028 / SL043
    factory_code: Mapped[str] = mapped_column(String(32))
    # Tanggal input dalam format YYYYMMDD (string supaya sederhana di sequence)
    date_ymd: Mapped[str] = mapped_column(String(8))
    last_value: Mapped[int] = mapped_column(Integer, default=0)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    department: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role", "module_key", "action", name="uq_role_permissions_key"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(32))
    module_key: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(32))
    allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(180))
    message: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40), default="general")
    entity_type: Mapped[Optional[str]] = mapped_column(String(80))
    entity_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    route_path: Mapped[Optional[str]] = mapped_column(String(255))
    route_query: Mapped[Optional[dict]] = mapped_column(JSON)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)



class PpicsAssignment(Base):
    __tablename__ = "ppic_assignments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_headers.id"))
    po_detail_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("po_details.id"))
    ppic_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    po: Mapped[Optional["PoHeader"]] = relationship("PoHeader", back_populates="ppic_assignments")
    po_detail: Mapped[Optional["PoDetail"]] = relationship("PoDetail")
    ppic_user: Mapped[Optional["User"]] = relationship("User")





class Warehouse(Base):
    """Gudang penyimpanan material."""

    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)


class InventoryUnitMaster(Base):
    """Satuan per tipe material inventory (kulit, kimia, aksesoris, rp)."""

    __tablename__ = "inventory_unit_masters"
    __table_args__ = (
        UniqueConstraint("material_type", "unit", name="uq_inv_unit_type_unit"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    material_type: Mapped[str] = mapped_column(String(32))
    unit: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)


class RawMaterial(Base):
    """Master data bahan baku."""

    __tablename__ = "raw_materials"
    __table_args__ = (
        UniqueConstraint("code", name="uq_raw_material_code"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(255))
    material_type: Mapped[str] = mapped_column(String(50))
    unit: Mapped[str] = mapped_column(String(20))
    size: Mapped[Optional[str]] = mapped_column(String(80))
    default_warehouse_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("warehouses.id"))
    min_stock: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    thickness: Mapped[Optional[str]] = mapped_column(String(80))
    color: Mapped[Optional[str]] = mapped_column(String(100))
    leather_type: Mapped[Optional[str]] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    warehouse: Mapped[Optional["Warehouse"]] = relationship("Warehouse")


class MaterialStock(Base):
    """Stok material per gudang."""

    __tablename__ = "material_stocks"
    __table_args__ = (
        UniqueConstraint("material_id", "warehouse_id", name="uq_material_warehouse"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("raw_materials.id"))
    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("warehouses.id"))
    current_stock: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    reserved_stock: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    material: Mapped[Optional["RawMaterial"]] = relationship("RawMaterial")
    warehouse: Mapped[Optional["Warehouse"]] = relationship("Warehouse")


class SpecialPrice(Base):
    """Harga khusus/diskon per buyer untuk material tertentu."""

    __tablename__ = "special_prices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_code: Mapped[str] = mapped_column(String(32))
    material_pattern: Mapped[Optional[str]] = mapped_column(String(255))
    emboss_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    color_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    discount_type: Mapped[str] = mapped_column(String(20))
    discount_value: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)


class CustomerSpecialPrice(Base):
    """Harga khusus per customer dengan buyer_code dan material pattern."""

    __tablename__ = "customer_special_prices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    buyer_code: Mapped[str] = mapped_column(String(32))
    material_pattern: Mapped[Optional[str]] = mapped_column(String(255))
    price_override: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    discount_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    customer: Mapped[Optional["Customer"]] = relationship("Customer")


class QuotationHeader(Base):
    """Penawaran harga."""

    __tablename__ = "quotation_headers"
    __table_args__ = (
        Index("ix_quotation_headers_customer_id", "customer_id"),
        Index("ix_quotation_headers_status", "status"),
        Index("ix_quotation_headers_quotation_date", "quotation_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    quotation_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="SET NULL")
    )
    quotation_date: Mapped[Optional[date]] = mapped_column(Date)
    currency: Mapped[Optional[str]] = mapped_column(String(3), default="USD")
    payment_terms: Mapped[Optional[str]] = mapped_column(String(255))
    valid_until: Mapped[Optional[date]] = mapped_column(Date)
    salesperson: Mapped[Optional[str]] = mapped_column(String(100))
    remark: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    lines: Mapped[list["QuotationLine"]] = relationship(
        "QuotationLine",
        back_populates="quotation",
        cascade="all, delete-orphan",
        order_by="QuotationLine.line_no",
    )


class QuotationLine(Base):
    __tablename__ = "quotation_lines"
    __table_args__ = (Index("ix_quotation_lines_quotation_id", "quotation_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    quotation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("quotation_headers.id", ondelete="CASCADE"), nullable=False
    )
    line_no: Mapped[int] = mapped_column(Integer)
    master_item_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("master_items.id", ondelete="SET NULL")
    )
    item_code: Mapped[Optional[str]] = mapped_column(String(80))
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String(200))
    specification: Mapped[Optional[str]] = mapped_column(String(500))
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    unit: Mapped[Optional[str]] = mapped_column(String(20), default="S/F")
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), default=0)
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), default=0)
    line_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))

    quotation: Mapped["QuotationHeader"] = relationship("QuotationHeader", back_populates="lines")
    master_item: Mapped[Optional["MasterItem"]] = relationship("MasterItem")


class SubconInvoice(Base):
    """Invoice untuk PO Subcont — barang / jasa."""

    __tablename__ = "subcon_invoices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_headers.id"))
    invoice_type: Mapped[str] = mapped_column(String(20))
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    po: Mapped[Optional["PoHeader"]] = relationship("PoHeader")


class OutstandingMaterial(Base):
    """Track outstanding materials per PO detail."""

    __tablename__ = "outstanding_materials"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_detail_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_details.id"))
    material_name: Mapped[Optional[str]] = mapped_column(String(255))
    total_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    delivered_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    balance_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    po_detail: Mapped[Optional["PoDetail"]] = relationship("PoDetail")


class AccountingMapping(Base):
    """Mapping transaksi ke Chart of Accounts."""

    __tablename__ = "accounting_mappings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    coa_code: Mapped[str] = mapped_column(String(20))
    coa_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)


class JournalEntry(Base):
    """Auto-generated GL journal entries from transactions."""

    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_type: Mapped[str] = mapped_column(String(50))
    transaction_id: Mapped[int] = mapped_column(BigInteger)
    coa_code: Mapped[str] = mapped_column(String(20))
    coa_name: Mapped[str] = mapped_column(String(100))
    debit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    entry_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)


class MaterialReceipt(Base):
    """Penerimaan material dari supplier."""

    __tablename__ = "material_receipts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255))
    receipt_date: Mapped[date] = mapped_column(Date)
    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("warehouses.id"))
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    remark: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    warehouse: Mapped[Optional["Warehouse"]] = relationship("Warehouse")
    details: Mapped[list["MaterialReceiptDetail"]] = relationship(
        "MaterialReceiptDetail", back_populates="receipt", cascade="all, delete-orphan"
    )


class MaterialReceiptDetail(Base):
    """Detail penerimaan material."""

    __tablename__ = "material_receipt_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    receipt_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("material_receipts.id"))
    material_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("raw_materials.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    total_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    remark: Mapped[Optional[str]] = mapped_column(Text)

    receipt: Mapped[Optional["MaterialReceipt"]] = relationship(
        "MaterialReceipt", back_populates="details"
    )
    material: Mapped[Optional["RawMaterial"]] = relationship("RawMaterial")

