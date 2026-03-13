"""create repositories table

Revision ID: 001
Revises: 
Create Date: 2025-03-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'repositories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('github_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('html_url', sa.Text(), nullable=False),
        sa.Column('homepage', sa.Text(), nullable=True),
        sa.Column('primary_language', sa.String(length=100), nullable=True),
        sa.Column('topics', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('stargazers_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('forks_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_fork', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('github_pushed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('github_updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('github_id', name='uq_repositories_github_id'),
        sa.UniqueConstraint('full_name', name='uq_repositories_full_name'),
    )


def downgrade() -> None:
    op.drop_table('repositories')
