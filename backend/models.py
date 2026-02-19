from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserInDB(BaseModel):
    id: UUID
    email: EmailStr
    hashed_password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str
