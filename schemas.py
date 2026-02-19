from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    # In a real application, you would not return the password hash.
    # For this example, we include it to demonstrate data flow.
    password: str 

    class Config:
        from_attributes = True
