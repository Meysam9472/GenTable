"""credit not null and task charges

Revision ID: f3c8d1b7a926
Revises: e2b9c5a81f47
Create Date: 2026-11-09 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3c8d1b7a926'
down_revision: Union[str, Sequence[str], None] = 'e2b9c5a81f47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Old rows can have NULL credit (the column was added without a default),
    # and the old race condition could make credit negative. Set both to 0.
    op.execute("UPDATE users SET credit = 0 WHERE credit IS NULL OR credit < 0")
    op.alter_column('users', 'credit', existing_type=sa.Integer(),
                    nullable=False, server_default='0')
    op.create_check_constraint('ck_users_credit_non_negative', 'users', 'credit >= 0')

    # One row per started task. It records the charge and makes the refund happen only once.
    op.create_table(
        'task_charges',
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('refunded', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id'),
    )
    op.create_index(op.f('ix_task_charges_user_id'), 'task_charges', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_task_charges_user_id'), table_name='task_charges')
    op.drop_table('task_charges')
    op.drop_constraint('ck_users_credit_non_negative', 'users', type_='check')
    op.alter_column('users', 'credit', existing_type=sa.Integer(),
                    nullable=True, server_default=None)