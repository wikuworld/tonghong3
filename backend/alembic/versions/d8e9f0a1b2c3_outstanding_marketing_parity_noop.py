"""Paritas export outstanding marketing (tanpa DDL).

Kolom tambahan (PO CUST, STATUS MATERIAL, kirim 7–8) hanya di layer API;
`po_headers.po_customer_ref` dan `po_detail_deliveries.sequence_no` sudah ada.
"""

revision = "d8e9f0a1b2c3"
down_revision = "c7d8e9f0a1b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
