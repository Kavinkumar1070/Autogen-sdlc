from fastapi import FastAPI, HTTPException, status
from schemas import User, UserCreate
from database import create_user, get_user_by_email, get_all_users

app = FastAPI()

@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    db_user = get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    new_user = create_user(user)
    return new_user

@app.get("/users/", response_model=list[User])
async def get_users():
    return get_all_users()
