"""add_conversation_messages_table

Revision ID: 2025_12_14_0001
Revises: 8aee8d7a4035
Create Date: 2025-12-14 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '2025_12_14_0001'
down_revision: Union[str, None] = '8aee8d7a4035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_role')
    )

    # Create indexes for optimal query performance
    op.create_index(
        'idx_conversation_messages_conversation_id_created_at',
        'conversation_messages',
        ['conversation_id', sa.text('created_at DESC')]
    )
    op.create_index(
        'idx_conversation_messages_user_id_conversation_id',
        'conversation_messages',
        ['user_id', 'conversation_id']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_conversation_messages_user_id_conversation_id', table_name='conversation_messages')
    op.drop_index('idx_conversation_messages_conversation_id_created_at', table_name='conversation_messages')

    # Drop table
    op.drop_table('conversation_messages')
