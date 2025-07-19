"""Drop unique constraint on candidates.email

Revision ID: ca317c931bdf
Revises: ff8dd6bf9b79
Create Date: 2025-06-19 15:09:15.204331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca317c931bdf'
down_revision = 'ff8dd6bf9b79'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
