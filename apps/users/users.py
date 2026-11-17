from fastapi import APIRouter, Depends, HTTPException, status, Body
from dependencies import get_postgres_db_connection as get_db

from schemas.users_schema import UserCreate, UserResponse, RefreshTokenRequest
from schemas.users_schema import AddCreditRequest, UserResetPassword, PromoteUserRequest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import AsyncSessionLocal
from models.users_models import User

from jose import JWTError, jwt
from .security import create_access_token, REFRESH_SECRET_KEY, ALGORITHM
from .security import verify_password, create_refresh_token, get_password_hash

from models.users_models import UserRole

from dependencies import require_admin_role, get_current_user_token_data, require_super_admin
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import delete, update
from dependencies import get_mongo_connection



router = APIRouter(prefix="/users", tags=["Users"])


def _delete_user_mongo_data(user_id: int) -> None:
    with get_mongo_connection() as client:
        db = client["university_scheduler"]
        db["schedules"].delete_many({"user_id": user_id})
        db["task_of_user"].delete_many({"user_id": user_id})


@router.post('/sing-up', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user.
    """
    try:
        # Check if username already exists
        result = await db.execute(select(User).where(User.username == user_in.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use."
            )

        # Hash the password and save the user
        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            username=user_in.username,
            hashed_password=hashed_password,
            phone_number=user_in.phone_number
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username or phone number is already in use."
        )


@router.post('/reset-user-password', status_code=status.HTTP_200_OK)
async def reset_user_password(req: UserResetPassword,
                              current_user: dict = Depends(get_current_user_token_data),
                              db: AsyncSession = Depends(get_db)):
    try:
        # 1. Fetch user
        user_data = await db.get(User, req.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        current_user_role = current_user.get("role")
        current_user_id = int(current_user.get("user_id"))
        
        # 2. Check Permissions
        is_admin = current_user_role in [UserRole.ADMIN.name, UserRole.SUPER_ADMIN.name]
        is_owner = user_data.id == current_user_id

        if not is_admin and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to change this password."
            )
        
        user_role_req = user_data.role
        # An Admin can't change the password of a SuperAdmin
        if user_role_req == UserRole.SUPER_ADMIN and current_user_role == UserRole.ADMIN.name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to change this password."
            )
        # A SuperAdmin can't change the password of another SuperAdmin.
        if user_role_req == UserRole.SUPER_ADMIN and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to change this password."
            )
        # An Admin can't change the password of another Admin.
        if user_role_req == UserRole.ADMIN and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to change this password."
            )
        # 3. Password Verification Logic
        if is_admin:
            # Admin can reset any password without verification
            pass 
        else:
            # Regular users MUST provide and verify current password
            if not req.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required for non-admin users."
                )
            
            if not verify_password(req.current_password, user_data.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect."
                )

        # 4. Check if new password is same as old one
        # Note: Admin might not care about this, but let's keep it for owners
        if req.current_password == req.new_password:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be the same as current password."
            )

        # 5. Update password
        user_data.hashed_password = get_password_hash(req.new_password)
        
        await db.commit()
        
        return {"status": "success", "message": f"Password updated by {'Admin' if is_admin else 'Owner'}."}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while resetting the password."
        )


@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                     current_admin: dict = Depends(require_admin_role)):
    """
    Get a list of users.
    """
    try:
        result = await db.execute(select(User).offset(skip).limit(limit))
        users = result.scalars().all()
        return users
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching data."
        )


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db), 
                    current_user: int=Depends(get_current_user_token_data)):
    """
    Get a specific user by ID.
    """
    try:
        current_user_role = current_user.get("role")
        current_user_id = int(current_user.get("user_id"))
        
        if current_user_role not in [UserRole.ADMIN.name, UserRole.SUPER_ADMIN.name]:
            if user_id != current_user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to perform this action.")
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching data."
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db),
                      current_admin: dict = Depends(require_admin_role)):
    """
    Delete a user by ID. The user's teachers, courses and relations are deleted too.
    """
    try:
        if user_id == current_admin["user_id"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You cannot delete your own account.")

        user_data = await db.get(User, user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        user_role_req = user_data.role
        # An Admin can't delete a SuperAdmin.
        if user_role_req == UserRole.SUPER_ADMIN and current_admin["role"] == UserRole.ADMIN.name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied."
            )
        if user_role_req == UserRole.SUPER_ADMIN and current_admin["role"] == UserRole.SUPER_ADMIN.name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied."
            )
        # An Admin can't delete another Admin.
        if user_role_req == UserRole.ADMIN and current_admin["role"] == UserRole.ADMIN.name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied."
            )
        # The database deletes the user's data itself (ON DELETE CASCADE).
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting user."
        )

    # The user is already deleted. If Mongo cleanup fails, log it but do not fail the request.
    try:
        await run_in_threadpool(_delete_user_mongo_data, user_id)
    except Exception:
        logger.exception("Could not delete Mongo data of user %s", user_id)
    return None


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return both access and refresh tokens.
    Uses OAuth2PasswordRequestForm which expects 'username' and 'password' in the form data.
    """
    
    # 1. Query the database to find the user by the provided username
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    # 2. Verify if the user exists and the provided password matches the hashed password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Generate both tokens
    # We cast user.id to string because the 'sub' (subject) claim in JWT is typically a string
    # user.role.name assumes your role is defined as an Enum in SQLAlchemy
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.name}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role.name}
    )
    
    # 4. Return the tokens to the client
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(request_data: RefreshTokenRequest):
    """
    Takes a valid refresh token and returns a new access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the refresh token using the REFRESH_SECRET_KEY
        payload = jwt.decode(request_data.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            raise credentials_exception
            
        # If valid, generate a NEW access token
        new_access_token = create_access_token(data={"sub": str(user_id), "role": role})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        # If the refresh token is expired or invalid, the user MUST log in again
        raise credentials_exception


@router.post("/change-user-credit", status_code=status.HTTP_200_OK)
async def change_user_credit(req: AddCreditRequest, db: AsyncSession = Depends(get_db),
                             current_admin: dict = Depends(require_admin_role)):
    """
    Add credit for a user. Amount can be negative to decrease the credit.
    """
    try:
        result = await db.execute(
            update(User)
            .where(User.id == req.user_id, User.credit + req.amount >= 0)
            .values(credit=User.credit + req.amount)
            .returning(User.credit)
        )
        row = result.first()

        if row is None:
            # Either the user does not exist, or the new credit would be below 0.
            exists = await db.execute(select(User.id).where(User.id == req.user_id))
            if exists.first() is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"User with id {req.user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credit amount must be at least 0. The new amount will make credit lower than 0."
            )

        await db.commit()
        return {"status": "success", "user_id": req.user_id, "new_credit": row.credit}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the user."
        )


@router.get("/get-user-credit/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_credit(user_id: int, db: AsyncSession = Depends(get_db),
                          current_admin: dict = Depends(require_admin_role)):
    """
    Get credit of a user by id.
    """
    try:
        user_data = await db.get(User, user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            ) 
        
        return {"message": f"Credit is {user_data.credit} for user with id={user_data.id}."}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting the user."
        )


@router.post("/promote-to-admin", status_code=status.HTTP_200_OK)
async def promote_to_admin(req: PromoteUserRequest,
                           db: AsyncSession = Depends(get_db),
                           current_super_admin: dict = Depends(require_super_admin)):
    """
    Change the role of a normal user to admin. Only a super admin can do this.
    """
    try:
        user_data = await db.get(User, req.user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found.")

        if user_data.role != UserRole.USER:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Only normal users can be promoted. This user is already {user_data.role.value}."
            )

        user_data.role = UserRole.ADMIN
        await db.commit()

        return {"status": "success", "user_id": user_data.id, "new_role": user_data.role.value}

    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        logger.exception("Unexpected error while promoting user %s", req.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while changing the user's role."
        )

