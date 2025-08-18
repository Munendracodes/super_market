from pydantic import BaseModel, Field

class UserBase(BaseModel):
    mobilenumber: str = Field(..., min_length=10, max_length=15, description="Phone number")
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    address: str | None = Field(default=None, max_length=255, description="Optional address")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True
