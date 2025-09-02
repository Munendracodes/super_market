from pydantic import BaseModel, Field, validator

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
        
class UserMobile(BaseModel):
    mobilenumber: str = Field(..., min_length=10, max_length=10, description="Phone number")
    
    @validator("mobilenumber")
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError("Mobile number must contain only digits")
        return v
    
class OTPRequest(BaseModel):
    mobilenumber: str = Field(..., min_length=10, max_length=10, description="Phone number")
    otp: str = Field(..., min_length=6, max_length=6, description="One Time Password")
    
    @validator("mobilenumber")
    def validate_mobile(cls, v):    
        if not v.isdigit():
            raise ValueError("Mobile number must contain only digits")
        return v
    @validator("otp")
    def validate_otp(cls, v):
        if not v.isdigit() and len(v) == 6:
            raise ValueError("OTP must contain only digits and be 6 characters long")
        return v    
    
class NewUserCreate(BaseModel):
    mobilenumber: str | None = Field(default=None, min_length=10, max_length=10, description="Phone number")
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    address: str | None = Field(default=None, max_length=255, description="Optional address")
    
    
