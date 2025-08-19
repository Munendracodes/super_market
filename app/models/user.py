from sqlalchemy import Column, Integer, String
from app.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobilenumber = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(60), nullable=False)
    address = Column(String(200), nullable=True)
