from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str


class UserInDB(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    hashed_password: str
    username: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: str
