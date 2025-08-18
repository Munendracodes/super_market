from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.crud.user import create_user, get_user_by_mobile, get_users
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserRead)
def create_user_ep(payload: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_mobile(db, payload.mobilenumber)
    if db_user:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    return create_user(db, payload)

@router.get("/", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)
