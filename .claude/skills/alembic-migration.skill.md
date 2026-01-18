# Alembic Migration Skill

## Purpose
Generate database migrations for schema changes.

## Process

```bash
# Install Alembic
pip install alembic

# Initialize (first time only)
alembic init alembic

# Configure env.py
from app.database import engine
from app.models import *
target_metadata = SQLModel.metadata

# Generate migration
alembic revision --autogenerate -m "Add subtasks table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Output
Database migration scripts.
