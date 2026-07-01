"""Unique po_customer_ref per customer (kolom normalisasi + unique index)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "j1k2l3m4n5o6"
down_revision: Union[str, None] = "i5j6k7l8m9n0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "po_headers",
        sa.Column("po_customer_ref_norm", sa.String(length=255), nullable=True),
    )
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE po_headers
            SET po_customer_ref_norm = LOWER(TRIM(po_customer_ref))
            WHERE po_customer_ref IS NOT NULL AND TRIM(po_customer_ref) <> ''
            """
        )
    )
    dupes = conn.execute(
        sa.text(
            """
            SELECT customer_id, po_customer_ref_norm, COUNT(*) AS cnt
            FROM po_headers
            WHERE customer_id IS NOT NULL AND po_customer_ref_norm IS NOT NULL
            GROUP BY customer_id, po_customer_ref_norm
            HAVING cnt > 1
            """
        )
    ).fetchall()
    for customer_id, ref_norm, _cnt in dupes:
        headers = conn.execute(
            sa.text(
                """
                SELECT id FROM po_headers
                WHERE customer_id = :customer_id AND po_customer_ref_norm = :ref_norm
                ORDER BY id
                """
            ),
            {"customer_id": customer_id, "ref_norm": ref_norm},
        ).fetchall()
        for idx, (po_id,) in enumerate(headers[1:], start=2):
            conn.execute(
                sa.text(
                    """
                    UPDATE po_headers
                    SET po_customer_ref = CONCAT(TRIM(po_customer_ref), '-dup', :suffix),
                        po_customer_ref_norm = CONCAT(po_customer_ref_norm, '-dup', :suffix)
                    WHERE id = :po_id
                    """
                ),
                {"suffix": str(idx), "po_id": po_id},
            )

    op.create_index(
        "uq_po_headers_customer_ref_norm",
        "po_headers",
        ["customer_id", "po_customer_ref_norm"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_po_headers_customer_ref_norm", table_name="po_headers")
    op.drop_column("po_headers", "po_customer_ref_norm")
