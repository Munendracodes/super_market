from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        mobilenumber=payload.mobilenumber,
        name=payload.name,
        address=payload.address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_mobile(db: Session, mobilenumber: str) -> User | None:
    return db.query(User).filter(User.mobilenumber == mobilenumber).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()
