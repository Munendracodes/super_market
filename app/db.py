from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import redis
from app.config import settings

DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_mysql():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            result = conn.execute(text("SHOW TABLES;")).fetchall()
            if result:
                return f"ok (tables: {[r[0] for r in result]})"
            else:
                return "ok (no tables yet)"
    except Exception as e:
        return f"error: {e}"

def check_redis():
    try:
        redis_client.set("health_check_key", "alive", ex=10)
        val = redis_client.get("health_check_key")
        if val == "alive":
            return "ok"
        return "error: unexpected value"
    except Exception as e:
        return f"error: {e}"
