"""Add author_id to Story

Revision ID: add_author_id_001
Revises: bcfce47bbfb0
Create Date: 2026-02-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "add_author_id_001"
down_revision = "bcfce47bbfb0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("story", sa.Column("author_id", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("story", "author_id")
