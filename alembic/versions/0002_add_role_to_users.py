"""add role to users

Revision ID: 0002_add_role_to_users
Revises: 0001_init
Create Date: 2026-05-10 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_role_to_users"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=50), nullable=False, server_default="user"),
    )


def downgrade():
    op.drop_column("users", "role")
