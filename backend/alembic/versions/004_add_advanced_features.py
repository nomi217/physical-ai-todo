"""Add advanced features: due dates, reminders, and recurring tasks

Revision ID: 004_advanced_features
Revises: 003
Create Date: 2025-01-16

Phase V Features:
- Due dates for tasks
- Reminder times
- Recurring task support
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_advanced_features'
down_revision = '2025_12_14_0001'  # Conversation messages table
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Phase V columns to tasks table"""
    # Add due_date column
    op.add_column('task', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_task_due_date'), 'task', ['due_date'], unique=False)

    # Add reminder_time column
    op.add_column('task', sa.Column('reminder_time', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_task_reminder_time'), 'task', ['reminder_time'], unique=False)

    # Add recurring task columns
    op.add_column('task', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index(op.f('ix_task_is_recurring'), 'task', ['is_recurring'], unique=False)

    op.add_column('task', sa.Column('recurrence_pattern', sa.String(length=50), nullable=True))
    op.add_column('task', sa.Column('recurrence_end_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove Phase V columns from tasks table"""
    # Remove recurring task columns
    op.drop_column('task', 'recurrence_end_date')
    op.drop_column('task', 'recurrence_pattern')
    op.drop_index(op.f('ix_task_is_recurring'), table_name='task')
    op.drop_column('task', 'is_recurring')

    # Remove reminder columns
    op.drop_index(op.f('ix_task_reminder_time'), table_name='task')
    op.drop_column('task', 'reminder_time')

    # Remove due date column
    op.drop_index(op.f('ix_task_due_date'), table_name='task')
    op.drop_column('task', 'due_date')
