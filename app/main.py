from fastapi import FastAPI
from app.db import Base, engine
from app.routers import user
from app.routers.redis import router as redis_router

# Dev convenience only (prod uses Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Super Market API")
app.include_router(user.router)
app.include_router(redis_router)

@app.get("/health")
def health():
    return {"status": "ok"}
