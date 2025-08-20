from fastapi import APIRouter
from app.db import redis_client

router = APIRouter(prefix="/redis", tags=["Redis"])


@router.get("/ping")
def ping_redis():
    try:
        pong = redis_client.ping()
        return {"status": "ok", "message": "Redis is running"} if pong else {"status": "fail"}
    except Exception as e:
        return {"status": "fail", "error": str(e)}

# 1. Set a key
@router.post("/set/{key}/{value}")
def set_key(key: str, value: str):
    redis_client.set(key, value)
    return {"message": f"Key '{key}' set with value '{value}'"}

# 2. Set a key with expiry (minutes)
@router.post("/set_with_expiry/{key}/{value}/{minutes}")
def set_key_with_expiry(key: str, value: str, minutes: int):
    expiry_seconds = minutes * 60
    redis_client.setex(key, expiry_seconds, value)
    return {"message": f"Key '{key}' set for {minutes} minutes"}

# 3. Get a key
@router.get("/get/{key}")
def get_key(key: str):
    value = redis_client.get(key)
    if value is None:
        return {"error": f"Key '{key}' not found"}
    return {"key": key, "value": value}

# 4. Delete a key
@router.delete("/delete/{key}")
def delete_key(key: str):
    result = redis_client.delete(key)
    if result == 0:
        return {"error": f"Key '{key}' not found"}
    return {"message": f"Key '{key}' deleted"}

# 5. Get TTL (time to live)
@router.get("/ttl/{key}")
def get_ttl(key: str):
    ttl = redis_client.ttl(key)
    if ttl == -1:
        return {"key": key, "ttl": "No expiry"}
    elif ttl == -2:
        return {"key": key, "ttl": "Key does not exist"}
    return {"key": key, "ttl": f"{ttl} seconds remaining"}

# 6. Get all keys
@router.get("/all")
def get_all_keys():
    keys = redis_client.keys("*")
    return {"keys": keys}
