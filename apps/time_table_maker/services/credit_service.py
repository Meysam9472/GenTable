"""
Credit refund logic.

Used by the API (when starting a task fails) and by the Celery worker (when a task
does not produce a timetable).
"""
from sqlalchemy import update

from database import SyncSessionLocal
from models.time_table_models import TaskCharge
from models.users_models import User


def refund_credit_once(task_id: str) -> bool:
    """
    Give one credit back for a task.

    It is safe to call this many times for the same task: the credit is returned only once.
    Returns True if a credit was refunded, False if it was already refunded
    (or if the task has no charge, for example because the user was deleted).
    """
    with SyncSessionLocal() as session:
        # Flip the flag first. Only one caller can win this UPDATE.
        row = session.execute(
            update(TaskCharge)
            .where(TaskCharge.task_id == task_id, TaskCharge.refunded.is_(False))
            .values(refunded=True)
            .returning(TaskCharge.user_id)
        ).first()
        if row is None:
            return False

        session.execute(
            update(User).where(User.id == row.user_id).values(credit=User.credit + 1)
        )
        # The flag and the credit change are committed together,
        # so a refund can never be lost halfway or counted twice.
        session.commit()
        return True