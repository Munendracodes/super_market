from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.db import check_mysql, check_redis

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
