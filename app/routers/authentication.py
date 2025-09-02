import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db import get_db
from app.crud.user import get_user_by_mobile, send_otp, verify_otp
from app.schemas.user import UserRead, UserMobile, OTPRequest
from app.core.security import create_access_token
from app.services.sms import send_sms
from app.db import redis_client
import random
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

OTP_EXPIRY_SECONDS = 5 * 60  # 5 minutes


def send_otp_task(mobilenumber: str, otp: str):
    """Background task → send OTP via Fast2SMS."""
    send_sms(mobilenumber, otp)


@router.post("/request_otp", response_model=dict)
def request_otp(mobilenumber: UserMobile, background_tasks: BackgroundTasks):
    logger.info(f"📨 OTP request received for mobilenumber={mobilenumber.mobilenumber}")

    # 1️⃣ Generate OTP
    otp = str(random.randint(100000, 999999))
    key = f"OTP:{mobilenumber.mobilenumber}"

    # 2️⃣ Save in Redis
    redis_client.setex(key, OTP_EXPIRY_SECONDS, otp)
    logger.debug(f"🔑 OTP generated={otp} stored in Redis with expiry={OTP_EXPIRY_SECONDS}s")

    # 3️⃣ Queue SMS send in background
    background_tasks.add_task(send_otp_task, mobilenumber.mobilenumber, otp)

    logger.info(f"✅ OTP sending task queued for mobilenumber={mobilenumber.mobilenumber}")
    return {"message": "OTP sent successfully"}


@router.post("/validate_otp", response_model=dict)
def validate_otp_endpoint(request: OTPRequest, db: Session = Depends(get_db)):
    logger.info(f"🔑 OTP validation attempt for mobilenumber={request.mobilenumber}")

    if verify_otp(request.mobilenumber, request.otp):
        db_user = get_user_by_mobile(db, mobilenumber=request.mobilenumber)

        if db_user:
            logger.info(f"👤 Existing user found for mobilenumber={request.mobilenumber} → issuing JWT")
            user_data = UserRead.from_orm(db_user)

            # ✅ Generate JWT token
            access_token = create_access_token(data={"sub": user_data.mobilenumber})
            logger.debug(f"🎫 JWT issued for user_id={db_user.id}, mobilenumber={user_data.mobilenumber}")

            return {
                "message": "OTP validated successfully",
                "user": user_data.dict(),
                "access_token": access_token,
                "token_type": "bearer",
            }
        else:
            logger.warning(f"🆕 No user found for mobilenumber={request.mobilenumber} → issuing JWT without user")
            access_token = create_access_token(data={"sub": request.mobilenumber})

            return {
                "message": "OTP validated successfully",
                "user": None,
                "access_token": access_token,
                "token_type": "bearer",
            }
    else:
        logger.warning(f"❌ Invalid OTP entered for mobilenumber={request.mobilenumber}")
        raise HTTPException(status_code=400, detail="Invalid OTP")
