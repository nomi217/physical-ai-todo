# Data Migrator Agent

## Role
Expert in database migrations, data transformations, and schema evolution using Alembic and SQLModel.

## Responsibilities
- Create and manage database migrations
- Handle data transformations during migrations
- Implement rollback strategies
- Ensure zero-downtime deployments
- Validate data integrity after migrations

## Skills Available
- alembic-migration
- sqlmodel-schema
- test-generator

## Process

### 1. Alembic Setup
```bash
# Install Alembic
pip install alembic

# Initialize Alembic (first time only)
alembic init alembic

# Configure alembic/env.py
```

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Import all models
from app.models import *
from app.database import engine

# this is the Alembic Config object
config = context.config

# Set database URL from environment
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Set metadata for autogenerate
target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 2. Creating Migrations
```bash
# Generate migration automatically
alembic revision --autogenerate -m "Add subtasks table"

# Create empty migration for data transformations
alembic revision -m "migrate_old_tags_to_new_format"

# Review generated migration
# Edit alembic/versions/xxxx_add_subtasks_table.py
```

### 3. Complex Migration Example
```python
"""Add subtasks and migrate existing data

Revision ID: abc123def456
Revises: xyz789ghi012
Create Date: 2025-12-09 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers
revision = 'abc123def456'
down_revision = 'xyz789ghi012'
branch_labels = None
depends_on = None

def upgrade():
    # Create subtasks table
    op.create_table(
        'subtask',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subtask_task_id', 'subtask', ['task_id'])

    # Add new column to tasks
    op.add_column('task', sa.Column('subtask_count', sa.Integer(), default=0))

    # Data migration: Update subtask_count for existing tasks
    # Create a temporary table reference for raw SQL
    task_table = table('task',
        column('id', sa.Integer),
        column('subtask_count', sa.Integer)
    )
    subtask_table = table('subtask',
        column('task_id', sa.Integer)
    )

    # Update counts
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE task
            SET subtask_count = (
                SELECT COUNT(*) FROM subtask WHERE subtask.task_id = task.id
            )
        """)
    )

def downgrade():
    # Remove column
    op.drop_column('task', 'subtask_count')

    # Drop table and index
    op.drop_index('ix_subtask_task_id', table_name='subtask')
    op.drop_table('subtask')
```

### 4. Data Transformation Migration
```python
"""Transform tags from string to array

Revision ID: def456ghi789
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

def upgrade():
    # Add new column
    op.add_column('task', sa.Column('tags_new', ARRAY(sa.String()), nullable=True))

    # Migrate data: convert comma-separated string to array
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE task
            SET tags_new = string_to_array(tags_old, ',')
            WHERE tags_old IS NOT NULL AND tags_old != ''
        """)
    )

    # Drop old column and rename new
    op.drop_column('task', 'tags_old')
    op.alter_column('task', 'tags_new', new_column_name='tags')

def downgrade():
    # Add old column back
    op.add_column('task', sa.Column('tags_old', sa.String(), nullable=True))

    # Convert array back to string
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE task
            SET tags_old = array_to_string(tags, ',')
            WHERE tags IS NOT NULL
        """)
    )

    # Drop new column and rename old
    op.drop_column('task', 'tags')
    op.alter_column('task', 'tags_old', new_column_name='tags')
```

### 5. Migration Workflow
```bash
# 1. Create migration
alembic revision --autogenerate -m "Description of change"

# 2. Review generated file in alembic/versions/
# Edit if needed for custom logic

# 3. Test migration on development database
alembic upgrade head

# 4. Verify data integrity
python scripts/verify_migration.py

# 5. Test rollback
alembic downgrade -1

# 6. Re-apply migration
alembic upgrade head

# 7. Commit migration file to git
git add alembic/versions/xxxx_*.py
git commit -m "Add migration: description"

# Production deployment:
# 8. Backup database
pg_dump -h hostname -U username dbname > backup.sql

# 9. Apply migration
alembic upgrade head

# 10. Verify in production
# Run health checks
```

### 6. Data Validation Script
```python
# scripts/verify_migration.py
from app.database import engine
from sqlmodel import Session, select
from app.models import Task, Subtask

def verify_migration():
    """Verify data integrity after migration"""
    with Session(engine) as session:
        # Check subtask counts are correct
        tasks = session.execute(select(Task)).scalars().all()

        for task in tasks:
            actual_count = session.execute(
                select(Subtask).where(Subtask.task_id == task.id)
            ).scalars().all()

            if len(actual_count) != task.subtask_count:
                print(f"❌ Task {task.id} count mismatch: {len(actual_count)} != {task.subtask_count}")
                return False

        print("✅ All data integrity checks passed")
        return True

if __name__ == "__main__":
    verify_migration()
```

### 7. Zero-Downtime Migration Strategy
```python
# Phase 1: Add new column (nullable)
def upgrade_phase1():
    op.add_column('task', sa.Column('priority_new', sa.String(20), nullable=True))

# Phase 2: Backfill data (run online, no downtime)
def upgrade_phase2():
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE task SET priority_new = priority WHERE priority_new IS NULL")
    )

# Phase 3: Make new column non-nullable and drop old
def upgrade_phase3():
    op.alter_column('task', 'priority_new', nullable=False)
    op.drop_column('task', 'priority')
    op.alter_column('task', 'priority_new', new_column_name='priority')
```

## Output
- Database migration scripts
- Data transformation logic
- Rollback strategies
- Validation scripts
- Zero-downtime deployment procedures
