from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.db import get_db
from app.crud.user import create_user, get_user_by_mobile, get_users
from app.schemas.user import UserRead, NewUserCreate
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)


@router.post("/", response_model=UserRead)
def create_user_ep(
    payload: NewUserCreate,
    db: Session = Depends(get_db),
    mobilenumber: str = Depends(get_current_user),  # 🔒 token required
):

    print(f"📲 Create User requested by mobilenumber={mobilenumber}")

    db_user = get_user_by_mobile(db, mobilenumber)
    if db_user:
        logger.warning(f"⚠️ User already exists with mobilenumber={mobilenumber}")
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    # Force mobilenumber from authenticated user
    print(f"🔒 Forcing mobilenumber from token: {mobilenumber}")
    payload.mobilenumber = mobilenumber #type: ignore
    print(f"✅ Final payload for user creation: {payload}")

    new_user = create_user(db, payload) #type: ignore
    print(f"✅ User created successfully: id={new_user.id}, mobilenumber={mobilenumber}")
    logger.info(f"✅ User created successfully: id={new_user.id}, mobilenumber={mobilenumber}")

    return new_user


# @router.get("/", response_model=list[UserRead])
# def list_users(
#     skip: int = 0,
#     limit: int = 10,
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),  # 🔒 token required
# ):
#     return get_users(db, skip=skip, limit=limit)


# @router.get("/me", response_model=UserRead)
# def get_me(current_user: UserRead = Depends(get_current_user)):
#     return current_user
