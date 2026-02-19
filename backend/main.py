import bcrypt
from fastapi import FastAPI, HTTPException, status
from uuid import uuid4

from . import database
from .models import UserRegister, UserInDB, UserOut, UserLogin

app = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}


@app.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    if database.get_user_by_email(user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user_in_db = UserInDB(
        id=uuid4(),
        email=user.email,
        hashed_password=hashed_password
    )
    database.create_user(new_user_in_db)
    return UserOut(id=new_user_in_db.id, email=new_user_in_db.email)


@app.post("/users/login", response_model=UserOut, status_code=status.HTTP_200_OK)
async def login_user(user_login: UserLogin):
    user_in_db = database.get_user_by_email(user_login.email)

    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    if not bcrypt.checkpw(user_login.password.encode('utf-8'), user_in_db.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    return UserOut(id=user_in_db.id, email=user_in_db.email)
