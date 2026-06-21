"""initial schema: classification, std_market_price, unit_alias

Revision ID: 0001
Revises:
Create Date: 2026-06-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "classification",
        sa.Column("item_code", sa.String(), primary_key=True),
        sa.Column("work_type_code", sa.String(), nullable=False),
        sa.Column("work_type_name", sa.String(), nullable=False),
        sa.Column("level1_code", sa.String()),
        sa.Column("level1_name", sa.String()),
        sa.Column("level1_description", sa.String()),
        sa.Column("level2_code", sa.String()),
        sa.Column("level2_name", sa.String()),
        sa.Column("level2_description", sa.String()),
        sa.Column("level3_code", sa.String()),
        sa.Column("level3_name", sa.String()),
        sa.Column("level3_description", sa.String()),
        sa.Column("level4_code", sa.String()),
        sa.Column("level4_name", sa.String()),
        sa.Column("level4_description", sa.String()),
        sa.Column("level5_code", sa.String()),
        sa.Column("level5_name", sa.String()),
        sa.Column("level5_description", sa.String()),
        sa.Column("item_name", sa.String(), nullable=False),
        sa.Column("spec", sa.String()),
        sa.Column("raw_unit", sa.String()),
        sa.Column("canonical_unit", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_classification_level_filter",
        "classification",
        ["work_type_code", "level1_code", "level2_code", "level3_code", "level4_code", "level5_code"],
    )
    op.create_index("ix_classification_item_name", "classification", ["item_name"])

    op.create_table(
        "unit_alias",
        sa.Column("raw_unit", sa.String(), primary_key=True),
        sa.Column("canonical_unit", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "std_market_price",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("item_code", sa.String()),
        sa.Column("work_type_code", sa.String()),
        sa.Column("work_type_name", sa.String()),
        sa.Column("product_name", sa.String()),
        sa.Column("spec", sa.String()),
        sa.Column("raw_unit", sa.String()),
        sa.Column("canonical_unit", sa.String()),
        sa.Column("material_cost", sa.Numeric()),
        sa.Column("labor_cost", sa.Numeric()),
        sa.Column("expense_cost", sa.Numeric()),
        sa.Column("published_date", sa.Date()),
        sa.Column("price_condition_note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("item_code", "published_date", name="uq_price_item_published_date"),
    )
    op.create_index("ix_price_item_code", "std_market_price", ["item_code"])


def downgrade() -> None:
    op.drop_table("std_market_price")
    op.drop_table("unit_alias")
    op.drop_table("classification")
