from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.db import check_mysql, check_redis
from app.routers.user import router as user_router
from app.routers.redis import router as redis_router
from app.routers.authentication import router as authentication_router

app = FastAPI()

@app.get("/health")
def health_check():
    mysql_status = check_mysql()
    redis_status = check_redis()
    healthy = mysql_status.startswith("ok") and redis_status == "ok"
    status_code = status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "mysql": mysql_status,
            "redis": redis_status
        },
    )

# ✅ Correct way to include routers
app.include_router(authentication_router)
app.include_router(user_router)
app.include_router(redis_router)
