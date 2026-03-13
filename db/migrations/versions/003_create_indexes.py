"""create indexes

Revision ID: 003
Revises: 002
Create Date: 2025-03-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: Unique indexes on github_id and cache_key are already created
    # by the unique constraints in the table definitions.
    # We only need to create the non-unique sort index here.
    
    # Sort order for the projects grid: pinned first, then by last pushed
    op.create_index(
        'idx_repositories_sort',
        'repositories',
        ['is_pinned', 'github_pushed_at'],
        postgresql_ops={'is_pinned': 'DESC', 'github_pushed_at': 'DESC'},
    )


def downgrade() -> None:
    op.drop_index('idx_repositories_sort', table_name='repositories')
