from pydantic import BaseModel, ConfigDict
from typing import Optional
from models.users_models import UserRole


class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[UserRole] = UserRole.USER


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    # This allows Pydantic to read data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class UserResetPassword(BaseModel):
    user_id: int
    current_password: Optional[str] = None # For regular users it's required
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AddCreditRequest(BaseModel):
    user_id: int
    amount: int