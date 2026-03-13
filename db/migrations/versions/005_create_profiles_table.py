"""create profiles table

Revision ID: 005
Revises: 004
Create Date: 2025-03-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'profiles',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('login', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=False),
        sa.Column('html_url', sa.Text(), nullable=False),
        sa.Column('public_repos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('followers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('following', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('login', name='uq_profiles_login'),
    )


def downgrade() -> None:
    op.drop_table('profiles')
