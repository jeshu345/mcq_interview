"""Drop unique constraint on candidates.email

Revision ID: ff8dd6bf9b79
Revises: a8d002164749
Create Date: 2025-06-19 13:44:02.868453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff8dd6bf9b79'
down_revision = 'a8d002164749'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
