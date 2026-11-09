"""
Create the first SUPER_ADMIN account.

Run from the project root (not from inside scripts/):

    python -m scripts.make_super_admin

In Docker:

    docker compose exec gen_table python -m scripts.make_super_admin

Values come from environment variables. If one is missing, the script asks for it.
    SEED_ADMIN_USERNAME
    SEED_ADMIN_PASSWORD
    SEED_ADMIN_PHONE

The script is safe to run many times: if a super admin already exists, it does nothing.
"""
import os
import sys
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from apps.users.security import get_password_hash
from database import SyncSessionLocal
from models.users_models import User, UserRole

MIN_PASSWORD_LENGTH = 12


def _get_value(env_name: str, prompt: str, secret: bool = False) -> str:
    value = os.getenv(env_name)
    if value:
        return value.strip()
    return (getpass(prompt) if secret else input(prompt)).strip()


def main() -> int:
    with SyncSessionLocal() as session:
        existing = session.execute(
            select(User).where(User.role == UserRole.SUPER_ADMIN)
        ).scalars().first()
        if existing:
            print(f"A super admin already exists (username: {existing.username}). Nothing to do.")
            return 0

        username = _get_value("SEED_ADMIN_USERNAME", "Username: ")
        password = _get_value("SEED_ADMIN_PASSWORD", "Password: ", secret=True)
        phone = _get_value("SEED_ADMIN_PHONE", "Phone number: ")

        if not username or not phone:
            print("Username and phone number are required.")
            return 1
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            return 1

        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            role=UserRole.SUPER_ADMIN,
            phone_number=phone,
            credit=0,
        )
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print("This username or phone number is already used by another account.")
            return 1

        print(f"Super admin '{username}' created.")
        return 0


if __name__ == "__main__":
    sys.exit(main())