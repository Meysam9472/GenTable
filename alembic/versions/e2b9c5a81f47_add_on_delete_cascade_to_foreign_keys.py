"""add on delete cascade to foreign keys

Revision ID: e2b9c5a81f47
Revises: d7a41f3b9e20
Create Date: 2026-11-09 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e2b9c5a81f47'
down_revision: Union[str, Sequence[str], None] = 'd7a41f3b9e20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, column, referred table, constraint name)
# These are the default names that PostgreSQL gave to the constraints when they were created.
FOREIGN_KEYS = [
    ("teachers", "user_id", "users", "teachers_user_id_fkey"),
    ("courses", "user_id", "users", "courses_user_id_fkey"),
    ("user_teacher_course_relations", "user_id", "users",
     "user_teacher_course_relations_user_id_fkey"),
    ("user_teacher_course_relations", "teacher_id", "teachers",
     "user_teacher_course_relations_teacher_id_fkey"),
    ("user_teacher_course_relations", "course_id", "courses",
     "user_teacher_course_relations_course_id_fkey"),
]


def upgrade() -> None:
    """Upgrade schema."""
    for table, column, ref_table, name in FOREIGN_KEYS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, ref_table, [column], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    for table, column, ref_table, name in FOREIGN_KEYS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, ref_table, [column], ["id"])