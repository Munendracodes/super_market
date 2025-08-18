from fastapi import FastAPI
from app.db import Base, engine
from app.routers import user

# Dev convenience only (prod uses Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Super Market API")
app.include_router(user.router)

@app.get("/health")
def health():
    return {"status": "ok"}
