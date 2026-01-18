"""add_task_reminders_and_notifications

Revision ID: 2e937c606c38
Revises: 005_fix_tags_type
Create Date: 2025-12-30 16:40:27.759402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2e937c606c38'
down_revision: Union[str, None] = '005_fix_tags_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend tasks table with NEW reminder fields (due_date and reminder_time already exist from 004_advanced_features)
    op.add_column('task', sa.Column('reminder_offset', sa.String(length=10), nullable=True))
    op.add_column('task', sa.Column('last_reminder_sent', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('last_overdue_notification_sent', sa.DateTime(), nullable=True))

    # Note: Indexes for due_date and reminder_time already created in 004_advanced_features migration

    # Create notifications table
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes on notifications table
    op.create_index('idx_notifications_user_read', 'notification', ['user_id', 'is_read'])
    op.create_index('idx_notifications_task', 'notification', ['task_id'])
    op.create_index('idx_notifications_created', 'notification', ['created_at'])
    op.create_index('idx_notifications_read', 'notification', ['is_read'])


def downgrade() -> None:
    # Drop notifications table and indexes
    op.drop_index('idx_notifications_read', table_name='notification')
    op.drop_index('idx_notifications_created', table_name='notification')
    op.drop_index('idx_notifications_task', table_name='notification')
    op.drop_index('idx_notifications_user_read', table_name='notification')
    op.drop_table('notification')

    # Remove NEW task columns (do not remove due_date and reminder_time - they belong to 004_advanced_features)
    op.drop_column('task', 'last_overdue_notification_sent')
    op.drop_column('task', 'last_reminder_sent')
    op.drop_column('task', 'reminder_offset')
