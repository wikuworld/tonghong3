"""Seed 5 correlated sample data for customer-brand-buyer-price-item.

Revision ID: d6e7f8a9b0c1
Revises: c4d5e6f7a8b9
Create Date: 2026-04-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d6e7f8a9b0c1"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEEDS = [
    {
        "customer_code": "CUST-SMP-001",
        "customer_name": "PT Sample Alpha",
        "brand_code": "BR-SMP-001",
        "brand_name": "Brand Alpha",
        "buyer_code": "BYSMP01",
        "item_code": "SMP-ITEM-001",
        "material_name": "PVC Synthetic Alpha",
        "thickness_range": "0.8-1.0",
        "color": "WHITE",
        "color_standard": "WHITE, BLACK, RED",
        "color_reference": "PANTONE WHITE, PANTONE BLACK, PANTONE RED",
        "price_base": 20000,
        "price_black": 1500,
        "price_fluor": 2000,
        "price_metalic": 2500,
        "price_emboss": 1000,
        "price_special_emboss": 1800,
    },
    {
        "customer_code": "CUST-SMP-002",
        "customer_name": "PT Sample Beta",
        "brand_code": "BR-SMP-002",
        "brand_name": "Brand Beta",
        "buyer_code": "BYSMP02",
        "item_code": "SMP-ITEM-002",
        "material_name": "PU Synthetic Beta",
        "thickness_range": "1.0-1.2",
        "color": "WHITE",
        "color_standard": "WHITE, BLACK, NAVY",
        "color_reference": "PANTONE WHITE, PANTONE BLACK, PANTONE NAVY",
        "price_base": 22500,
        "price_black": 1600,
        "price_fluor": 2100,
        "price_metalic": 2600,
        "price_emboss": 1200,
        "price_special_emboss": 2000,
    },
    {
        "customer_code": "CUST-SMP-003",
        "customer_name": "PT Sample Gamma",
        "brand_code": "BR-SMP-003",
        "brand_name": "Brand Gamma",
        "buyer_code": "BYSMP03",
        "item_code": "SMP-ITEM-003",
        "material_name": "Microfiber Gamma",
        "thickness_range": "1.2-1.4",
        "color": "WHITE",
        "color_standard": "WHITE, BLACK, GREY",
        "color_reference": "PANTONE WHITE, PANTONE BLACK, PANTONE GREY",
        "price_base": 24500,
        "price_black": 1700,
        "price_fluor": 2200,
        "price_metalic": 2800,
        "price_emboss": 1300,
        "price_special_emboss": 2100,
    },
    {
        "customer_code": "CUST-SMP-004",
        "customer_name": "PT Sample Delta",
        "brand_code": "BR-SMP-004",
        "brand_name": "Brand Delta",
        "buyer_code": "BYSMP04",
        "item_code": "SMP-ITEM-004",
        "material_name": "Synthetic Leather Delta",
        "thickness_range": "1.4-1.6",
        "color": "WHITE",
        "color_standard": "WHITE, BLACK, BROWN",
        "color_reference": "PANTONE WHITE, PANTONE BLACK, PANTONE BROWN",
        "price_base": 26500,
        "price_black": 1800,
        "price_fluor": 2300,
        "price_metalic": 3000,
        "price_emboss": 1400,
        "price_special_emboss": 2300,
    },
    {
        "customer_code": "CUST-SMP-005",
        "customer_name": "PT Sample Epsilon",
        "brand_code": "BR-SMP-005",
        "brand_name": "Brand Epsilon",
        "buyer_code": "BYSMP05",
        "item_code": "SMP-ITEM-005",
        "material_name": "Vegan Leather Epsilon",
        "thickness_range": "1.6-1.8",
        "color": "WHITE",
        "color_standard": "WHITE, BLACK, GREEN",
        "color_reference": "PANTONE WHITE, PANTONE BLACK, PANTONE GREEN",
        "price_base": 28500,
        "price_black": 1900,
        "price_fluor": 2400,
        "price_metalic": 3200,
        "price_emboss": 1500,
        "price_special_emboss": 2500,
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    for s in SEEDS:
        conn.execute(
            sa.text(
                """
                INSERT INTO customers (
                  code, name, contact_person, position, email, phone,
                  country, address, shipping_address, billing_address,
                  is_active, is_export_customer
                )
                SELECT
                  :customer_code, :customer_name, CONCAT('PIC ', :customer_name), 'Purchasing',
                  CONCAT(REPLACE(LOWER(:customer_code), '-', ''), '@example.com'),
                  CONCAT('08123', RIGHT(:customer_code, 3)),
                  'Indonesia', CONCAT('Alamat ', :customer_name), CONCAT('Gudang ', :customer_name),
                  CONCAT('Kantor ', :customer_name), 1, 0
                FROM dual
                WHERE NOT EXISTS (
                  SELECT 1 FROM customers WHERE code = :customer_code
                )
                """
            ),
            s,
        )

        conn.execute(
            sa.text(
                """
                INSERT INTO brands (code, name)
                SELECT :brand_code, :brand_name
                FROM dual
                WHERE NOT EXISTS (
                  SELECT 1 FROM brands WHERE code = :brand_code
                )
                """
            ),
            s,
        )

        conn.execute(
            sa.text(
                """
                INSERT INTO master_items (
                  item_code, thickness_range, material_name, color,
                  color_standard, color_reference, emboss, softness
                )
                SELECT
                  :item_code, :thickness_range, :material_name, :color,
                  :color_standard, :color_reference, 'STANDARD EMBOSS', 'MEDIUM'
                FROM dual
                WHERE NOT EXISTS (
                  SELECT 1 FROM master_items WHERE item_code = :item_code
                )
                """
            ),
            s,
        )

        conn.execute(
            sa.text(
                """
                INSERT INTO customer_brand_mappings (customer_id, brand_id, is_default)
                SELECT c.id, b.id, 1
                FROM customers c
                JOIN brands b ON b.code = :brand_code
                WHERE c.code = :customer_code
                  AND NOT EXISTS (
                    SELECT 1
                    FROM customer_brand_mappings cbm
                    WHERE cbm.customer_id = c.id AND cbm.brand_id = b.id
                  )
                """
            ),
            s,
        )

        conn.execute(
            sa.text(
                """
                INSERT INTO brand_buyer_maps (brand_id, buyer_code)
                SELECT b.id, :buyer_code
                FROM brands b
                WHERE b.code = :brand_code
                  AND NOT EXISTS (
                    SELECT 1
                    FROM brand_buyer_maps bbm
                    WHERE bbm.brand_id = b.id AND bbm.buyer_code = :buyer_code
                  )
                """
            ),
            s,
        )

        conn.execute(
            sa.text(
                """
                INSERT INTO buyer_price_lists (buyer_code, currency, title, period_label)
                SELECT
                  :buyer_code, 'USD',
                  CONCAT('Sample Price List ', :buyer_code),
                  'Sample 2026'
                FROM dual
                WHERE NOT EXISTS (
                  SELECT 1 FROM buyer_price_lists WHERE buyer_code = :buyer_code
                )
                """
            ),
            s,
        )

        conn.execute(
            sa.text(
                """
                INSERT INTO buyer_price_sheet_rows (list_id, `row_number`, cells)
                SELECT
                  bpl.id,
                  1,
                  JSON_OBJECT(
                    'ITEM', :item_code,
                    'THICKNESS', :thickness_range,
                    'COLOR', :color,
                    'COLOR WHITE', :price_base,
                    'COLOR BLACK', :price_black,
                    'FLOURASENT', :price_fluor,
                    'METALIC', :price_metalic,
                    'EMBOSS', :price_emboss,
                    'SPESIAL EMBOSS', :price_special_emboss
                  )
                FROM buyer_price_lists bpl
                WHERE bpl.buyer_code = :buyer_code
                  AND NOT EXISTS (
                    SELECT 1
                    FROM buyer_price_sheet_rows bpsr
                    WHERE bpsr.list_id = bpl.id
                  )
                """
            ),
            s,
        )

        conn.execute(
            sa.text(
                """
                UPDATE buyer_price_lists bpl
                SET bpl.meta_json = JSON_OBJECT(
                  'column_keys',
                  JSON_ARRAY(
                    'ITEM', 'THICKNESS', 'COLOR',
                    'COLOR WHITE', 'COLOR BLACK', 'FLOURASENT', 'METALIC', 'EMBOSS', 'SPESIAL EMBOSS'
                  )
                )
                WHERE bpl.buyer_code = :buyer_code
                """
            ),
            s,
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE bpsr
            FROM buyer_price_sheet_rows bpsr
            JOIN buyer_price_lists bpl ON bpl.id = bpsr.list_id
            WHERE bpl.buyer_code LIKE 'BYSMP%'
            """
        )
    )
    op.execute(sa.text("DELETE FROM buyer_price_lists WHERE buyer_code LIKE 'BYSMP%'"))
    op.execute(sa.text("DELETE FROM brand_buyer_maps WHERE buyer_code LIKE 'BYSMP%'"))
    op.execute(
        sa.text(
            """
            DELETE cbm
            FROM customer_brand_mappings cbm
            JOIN customers c ON c.id = cbm.customer_id
            WHERE c.code LIKE 'CUST-SMP-%'
            """
        )
    )
    op.execute(sa.text("DELETE FROM brands WHERE code LIKE 'BR-SMP-%'"))
    op.execute(sa.text("DELETE FROM customers WHERE code LIKE 'CUST-SMP-%'"))
    op.execute(sa.text("DELETE FROM master_items WHERE item_code LIKE 'SMP-ITEM-%'"))
