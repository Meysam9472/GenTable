"""unique user teacher course relation

Revision ID: d7a41f3b9e20
Revises: c1092ce3fa72
Create Date: 2026-11-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd7a41f3b9e20'
down_revision: Union[str, Sequence[str], None] = 'c1092ce3fa72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The constraint cannot be created if duplicates already exist.
    # Keep the oldest row (lowest id) of each duplicate group and delete the rest.
    op.execute("""
        DELETE FROM user_teacher_course_relations a
        USING user_teacher_course_relations b
        WHERE a.id > b.id
          AND a.user_id = b.user_id
          AND a.teacher_id = b.teacher_id
          AND a.course_id = b.course_id
    """)
    op.create_unique_constraint(
        'uq_user_teacher_course',
        'user_teacher_course_relations',
        ['user_id', 'teacher_id', 'course_id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_user_teacher_course', 'user_teacher_course_relations', type_='unique')