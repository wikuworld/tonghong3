"""Officialkan CSI, FK swatch, color_code item, XREF aliases.

Revision ID: a0b1c2d3e4f5
Revises: z0a1b2c3d4e5
Create Date: 2026-08-15
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text

revision: str = "a0b1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "z0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, column: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def _has_index(insp, table: str, name: str) -> bool:
    if not insp.has_table(table):
        return False
    return any(ix.get("name") == name for ix in insp.get_indexes(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa_inspect(bind)

    if not insp.has_table("csi_color_masters"):
        op.create_table(
            "csi_color_masters",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("buyer_code", sa.String(length=32), nullable=False),
            sa.Column("color_code", sa.String(length=64), nullable=False),
            sa.Column("color_name", sa.String(length=255), nullable=False),
            sa.Column("source_file", sa.String(length=255), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column(
                "created_at",
                sa.TIMESTAMP(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["buyer_code"],
                ["buyer_codes.code"],
                name="csi_color_masters_ibfk_1",
            ),
            sa.UniqueConstraint("buyer_code", "color_code", name="uq_csi_color_master"),
        )
        op.create_index("ix_csi_color_masters_buyer", "csi_color_masters", ["buyer_code"])
        op.create_index("ix_csi_color_masters_code", "csi_color_masters", ["color_code"])

    if not insp.has_table("color_code_aliases"):
        op.create_table(
            "color_code_aliases",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("buyer_code", sa.String(length=32), nullable=False),
            sa.Column("source_system", sa.String(length=32), nullable=False, server_default="SWATCH"),
            sa.Column("alias_code", sa.String(length=64), nullable=False),
            sa.Column("csi_color_master_id", sa.BigInteger(), nullable=True),
            sa.Column("match_method", sa.String(length=32), nullable=False, server_default="dual_parse"),
            sa.Column("steward_status", sa.String(length=16), nullable=False, server_default="pending"),
            sa.Column("source_file", sa.String(length=255), nullable=True),
            sa.Column("deactivated_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_at",
                sa.TIMESTAMP(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["buyer_code"],
                ["buyer_codes.code"],
                name="fk_color_code_aliases_buyer",
            ),
            sa.ForeignKeyConstraint(
                ["csi_color_master_id"],
                ["csi_color_masters.id"],
                name="fk_color_code_aliases_csi",
                ondelete="SET NULL",
            ),
            sa.UniqueConstraint(
                "buyer_code",
                "source_system",
                "alias_code",
                name="uq_color_code_alias_source",
            ),
        )
        op.create_index("ix_color_code_aliases_csi", "color_code_aliases", ["csi_color_master_id"])
        op.create_index("ix_color_code_aliases_alias", "color_code_aliases", ["alias_code"])

    insp = sa_inspect(bind)
    if not _has_column(insp, "color_swatch_recipes", "csi_color_master_id"):
        op.add_column(
            "color_swatch_recipes",
            sa.Column("csi_color_master_id", sa.BigInteger(), nullable=True),
        )
        op.create_index(
            "ix_color_swatch_csi_id",
            "color_swatch_recipes",
            ["csi_color_master_id"],
        )
        op.create_foreign_key(
            "fk_color_swatch_csi_color",
            "color_swatch_recipes",
            "csi_color_masters",
            ["csi_color_master_id"],
            ["id"],
            ondelete="SET NULL",
        )

    if not _has_column(insp, "master_items", "color_code"):
        op.add_column("master_items", sa.Column("color_code", sa.String(length=64), nullable=True))
        op.create_index("ix_master_items_color_code", "master_items", ["color_code"])
    if not _has_column(insp, "master_items", "color_qualifier"):
        op.add_column(
            "master_items",
            sa.Column("color_qualifier", sa.String(length=64), nullable=True),
        )

    bind.execute(
        text(
            """
            UPDATE color_swatch_recipes s
            JOIN csi_color_masters c
              ON c.buyer_code = s.buyer_code
             AND c.color_code = s.color_code
             AND c.is_active = 1
            SET s.csi_color_master_id = c.id
            WHERE s.csi_color_master_id IS NULL
            """
        )
    )
    bind.execute(
        text(
            """
            UPDATE master_items
            SET color_code = UPPER(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(color, ')', 1), '(', -1)))
            WHERE color LIKE '%(%' AND color LIKE '%)%'
              AND (color_code IS NULL OR color_code = '')
            """
        )
    )
    for word in ("FLUORESCENT", "PEARLIZED", "METALLIC", "TCX"):
        bind.execute(
            text(
                """
                UPDATE master_items
                SET color_qualifier = :word
                WHERE UPPER(color) LIKE :pat
                  AND (color_qualifier IS NULL OR color_qualifier = '')
                """
            ),
            {"word": word, "pat": f"%{word}%"},
        )

    linked = bind.execute(
        text("SELECT COUNT(*) FROM color_swatch_recipes WHERE csi_color_master_id IS NOT NULL")
    ).scalar()
    orphan = bind.execute(
        text(
            """
            SELECT COUNT(*) FROM color_swatch_recipes
            WHERE is_active = 1 AND csi_color_master_id IS NULL
            """
        )
    ).scalar()
    items_coded = bind.execute(
        text("SELECT COUNT(*) FROM master_items WHERE color_code IS NOT NULL AND TRIM(color_code) != ''")
    ).scalar()
    print(f"CSI cascade backfill: swatch_linked={linked} swatch_orphan={orphan} items_color_code={items_coded}")

    _seed_dual_aliases(bind)


def _seed_dual_aliases(bind) -> None:
    from app.services.color_code import parse_dual_color_code

    rows = bind.execute(
        text(
            """
            SELECT DISTINCT buyer_code, color_code, source_file
            FROM color_swatch_recipes
            WHERE is_active = 1 AND color_code LIKE '%(%'
            """
        )
    ).mappings().all()
    inserted = 0
    for row in rows:
        dual = parse_dual_color_code(row["color_code"])
        if not dual:
            continue
        csi_id = None
        status = "pending"
        if dual.csi_code:
            csi_id = bind.execute(
                text(
                    """
                    SELECT id FROM csi_color_masters
                    WHERE buyer_code = :b AND color_code = :c AND is_active = 1
                    LIMIT 1
                    """
                ),
                {"b": row["buyer_code"], "c": dual.csi_code},
            ).scalar()
            if csi_id:
                status = "active"
        exists = bind.execute(
            text(
                """
                SELECT id FROM color_code_aliases
                WHERE buyer_code = :b AND source_system = 'COLORO' AND alias_code = :a
                LIMIT 1
                """
            ),
            {"b": row["buyer_code"], "a": dual.alias_code},
        ).first()
        if exists:
            continue
        bind.execute(
            text(
                """
                INSERT INTO color_code_aliases
                  (buyer_code, source_system, alias_code, csi_color_master_id,
                   match_method, steward_status, source_file)
                VALUES
                  (:b, 'COLORO', :a, :cid, 'dual_parse', :st, :sf)
                """
            ),
            {
                "b": row["buyer_code"],
                "a": dual.alias_code,
                "cid": csi_id,
                "st": status,
                "sf": row["source_file"],
            },
        )
        inserted += 1
    print(f"CSI cascade aliases seeded: {inserted}")


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa_inspect(bind)
    if _has_column(insp, "color_swatch_recipes", "csi_color_master_id"):
        op.drop_constraint("fk_color_swatch_csi_color", "color_swatch_recipes", type_="foreignkey")
        if _has_index(insp, "color_swatch_recipes", "ix_color_swatch_csi_id"):
            op.drop_index("ix_color_swatch_csi_id", table_name="color_swatch_recipes")
        op.drop_column("color_swatch_recipes", "csi_color_master_id")
    if _has_column(insp, "master_items", "color_qualifier"):
        op.drop_column("master_items", "color_qualifier")
    if _has_column(insp, "master_items", "color_code"):
        if _has_index(insp, "master_items", "ix_master_items_color_code"):
            op.drop_index("ix_master_items_color_code", table_name="master_items")
        op.drop_column("master_items", "color_code")
    if insp.has_table("color_code_aliases"):
        op.drop_table("color_code_aliases")
    # Jangan drop csi_color_masters jika sudah berisi data impor live.
