from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import ValidationError

from . import database
from .models import (
    UserInDB, UserLogin, UserRegister, UserOut,
    Token, TokenData,
    TaskCreate, TaskInDB, TaskOut
)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# --- Utility Functions ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# In a real application, you'd use JWTs for stateless authentication.
# For this in-memory example, we'll simulate a very basic "token" system
# or rely on direct user lookup for simplicity, but the OAuth2PasswordBearer
# is still useful for FastAPI's documentation and flow.

# --- Authentication Dependency ---

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    # In a real app, 'token' would be a JWT that you decode and validate.
    # For this simple in-memory example, we'll just check if a user with
    # that token (which we'll treat as an email for simplicity in 'login') exists.
    # This is NOT a secure or proper token validation. It's illustrative.

    # HACK: For this in-memory example, we'll assume the 'token' here is actually the user's email.
    # In a real application, you would decode a JWT token to get the user ID.
    user = database.get_user_by_email(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserOut(**user.model_dump())

async def get_current_active_user(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    # In a real app, you might check if the user is active, not banned, etc.
    return current_user

# --- Health Endpoint ---

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- User Router ---

users_router = APIRouter()

@users_router.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_register: UserRegister):
    existing_user = database.get_user_by_email(user_register.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user_register.password)
    user_in_db = UserInDB(
        id=uuid4(),
        email=user_register.email,
        full_name=user_register.full_name,
        hashed_password=hashed_password
    )
    database.create_user(user_in_db)
    return UserOut(**user_in_db.model_dump())

@users_router.post("/users/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = database.get_user_by_email(form_data.username) # form_data.username is the email
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real application, you'd generate a JWT here.
    # For this example, we'll return the user's email as a simplistic "token".
    # This is INSECURE for production but demonstrates the flow.
    return {"access_token": user.email, "token_type": "bearer"}

app.include_router(users_router)

# --- Task Router ---

tasks_router = APIRouter()

@tasks_router.post("/tasks/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_create: TaskCreate,
    current_user: UserOut = Depends(get_current_active_user)
):
    task_id = uuid4()
    now = datetime.now(timezone.utc)
    task_in_db = TaskInDB(
        id=task_id,
        user_id=current_user.id,
        title=task_create.title,
        description=task_create.description,
        created_at=now,
        updated_at=now
    )
    database.create_task(task_in_db)
    return TaskOut(**task_in_db.model_dump())

@tasks_router.get("/tasks/", response_model=List[TaskOut])
async def read_tasks(
    current_user: UserOut = Depends(get_current_active_user)
):
    tasks = database.get_tasks_by_user_id(current_user.id)
    return [TaskOut(**task.model_dump()) for task in tasks]

app.include_router(tasks_router)
