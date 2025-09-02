import logging
from datetime import datetime, timedelta
from typing import Optional
 
from jose import jwt, JWTError  # type: ignore
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.crud.user import get_user_by_mobile
from app.schemas.user import UserRead

# Configure logger
logger = logging.getLogger(__name__)

# JWT Config
SECRET_KEY = "9d0c3e5a5a2f47f99e3a18767d0b4a8d21b7d6d3f4b9c1f82d1c2b3f4e5f6a7b"   # 👉 move to env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 525600  # 1 year

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/validate_otp")  # token is returned here


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"🔑 Access token created for sub={data.get('sub')} exp={expire.isoformat()}")

    return token


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print("🕵️ Extracting current user from JWT token...")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mobilenumber: str = payload.get("sub")
        if mobilenumber is None:
            print("⚠️ Token payload missing 'sub' field")
            raise credentials_exception
        logger.info(f"📲 Token valid for mobilenumber={mobilenumber}")
    except JWTError as e:
        logger.error(f"❌ Invalid token: {e}")
        raise credentials_exception
    print(f"✅ Token valid for mobilenumber={mobilenumber}")
    return mobilenumber
