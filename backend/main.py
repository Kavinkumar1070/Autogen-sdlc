from fastapi import FastAPI, HTTPException, status
from passlib.context import CryptContext

from backend.models import UserRegister, UserInDB, UserOut
from backend import database

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}


@app.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    # Check if email already exists
    if database.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = pwd_context.hash(user_data.password)

    # Create a new UserInDB object
    new_user_in_db = UserInDB(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    # Store the user in the database
    created_user = database.create_user(new_user_in_db)

    # Return a UserOut object (without hashed password)
    return UserOut(
        id=created_user.id,
        email=created_user.email,
        username=created_user.username
    )
