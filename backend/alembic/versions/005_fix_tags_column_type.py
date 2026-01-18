"""Fix tags column type from VARCHAR to JSON

Revision ID: 005_fix_tags_type
Revises: 004_advanced_features
Create Date: 2025-12-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_fix_tags_type'
down_revision = '004_advanced_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Change tags column from VARCHAR to JSON"""
    # PostgreSQL: convert VARCHAR to JSON using USING clause
    op.execute("ALTER TABLE task ALTER COLUMN tags TYPE JSON USING tags::json")


def downgrade() -> None:
    """Revert tags column from JSON to VARCHAR"""
    op.alter_column('task', 'tags',
                    type_=sa.VARCHAR(length=1000),
                    postgresql_using='tags::text')
