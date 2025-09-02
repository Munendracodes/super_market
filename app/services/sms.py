# app/services/sms.py
import logging
import os
import requests  # type: ignore

logger = logging.getLogger(__name__)

FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"
FAST2SMS_API_KEY = os.getenv(
    "FAST2SMS_API_KEY",
    "yQ7XeDUIfOMnq0KAh3B4g2RvriW5bCs8wtJmEx1ZzNdoSkPFT6nCgxiqdOSFmwHKl94RA5JhzPvyu3GI"  # ✅ replace in prod
)


def send_sms(numbers: str, otp: str) -> bool:
    """
    Send OTP using Fast2SMS Quick SMS API.
    - numbers: comma separated mobile numbers
    - otp: the OTP value
    """
    if not FAST2SMS_API_KEY:
        logger.error("❌ FAST2SMS_API_KEY not configured")
        return False

    try:
        message = f"Your OTP is {otp}. Do not share it with anyone. - SuperMarket App"

        payload = {
            "route": "q",              # ✅ Quick Transactional SMS
            "message": message,
            "language": "english",
            "numbers": numbers,
        }
        headers = {
            "authorization": FAST2SMS_API_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(FAST2SMS_URL, data=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("return") is True:
            logger.info(f"📩 SMS sent successfully → {numbers}, otp={otp}")
            return True
        else:
            logger.error(f"⚠️ SMS failed → {numbers}, response={data}")
            return False

    except requests.RequestException as e:
        logger.error(f"🚨 HTTP error sending SMS → {numbers}: {e}")
        return False
    except Exception as e:
        logger.exception(f"🔥 Unexpected error sending SMS → {numbers}: {e}")
        return False
