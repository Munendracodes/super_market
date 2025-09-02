import logging
import random
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.db import redis_client
from fastapi import BackgroundTasks
from app.services.sms import send_sms

# Configure logger
logger = logging.getLogger(__name__)


def create_user(db: Session, payload: UserCreate) -> User:
    print(f"🆕 Creating user with mobilenumber={payload}")

    user = User(
        mobilenumber=payload.mobilenumber,
        name=payload.name,
        address=payload.address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"✅ User created successfully: id={user.id}, mobilenumber={user.mobilenumber}")
    return user


def get_user_by_mobile(db: Session, mobilenumber: str) -> User | None:
    logger.debug(f"🔍 Looking up user by mobilenumber={mobilenumber}")
    user = db.query(User).filter(User.mobilenumber == mobilenumber).first()

    if user:
        logger.info(f"📲 User found: id={user.id}, mobilenumber={user.mobilenumber}")
    else:
        logger.warning(f"🚫 No user found with mobilenumber={mobilenumber}")

    return user


def get_users(db: Session, skip: int = 0, limit: int = 10):
    logger.debug(f"📋 Fetching users (skip={skip}, limit={limit})")
    users = db.query(User).offset(skip).limit(limit).all()
    logger.info(f"✅ Retrieved {len(users)} users")
    return users


def send_otp(mobilenumber: str, background_tasks: BackgroundTasks) -> bool:
    value = f"{random.randint(100000, 999999)}"
    key = f"OTP:{mobilenumber}"
    expiry_seconds = 5 * 60  # 5 minutes

    # Save OTP in Redis
    redis_client.setex(key, expiry_seconds, value)
    logger.info(f"📤 OTP generated: {value} → mobilenumber={mobilenumber} (expires in {expiry_seconds}s)")

    # Run SMS send in background
    background_tasks.add_task(send_sms, mobilenumber, f"Your OTP is {value}")

    return True


def verify_otp(mobilenumber: str, otp: str) -> bool:
    key = f"OTP:{mobilenumber}"
    stored_otp = redis_client.get(key)

    logger.debug(f"🔐 Verifying OTP for mobilenumber={mobilenumber}")

    if stored_otp:
        if stored_otp == otp:  # ensure bytes→str
            redis_client.delete(key)  # OTP is single-use
            logger.info(f"✅ OTP verified successfully for mobilenumber={mobilenumber}")
            return True
        else:
            logger.warning(f"❌ OTP mismatch for mobilenumber={mobilenumber} (expected={stored_otp}, got={otp})")
    else:
        logger.warning(f"⏳ OTP expired or not found for mobilenumber={mobilenumber}")

    return False
