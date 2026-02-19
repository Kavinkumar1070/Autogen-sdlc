from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from dotenv import load_dotenv # Import load_dotenv
import os
from uuid import UUID # Import UUID for type hinting, especially for get_current_user return type

from backend.models import (
    UserBase, # Added to dependencies
    UserInDB,
    UserRegister,
    UserLogin,
    Token,
    TokenData,
    TaskBase,
    TaskCreate,
    TaskInDB,
    TaskOut,
    UserOut,
)
from backend.database import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    create_task,
    get_tasks_by_user_id,
    prisma,  # Import the prisma client
)

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key") # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

app = FastAPI(
    title="FastAPI Task Manager",
    description="A simple task management API built with FastAPI.",
    version="1.0.0",
)

# --- Helper Functions for Security ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# This function is not used for JWT generation in this simple example but conceptually for token data
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # This implementation is simplified and directly uses email as token content for in-memory example.
    # For a real application, you would encode a JWT here.
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # This is not a real JWT encoding for this simplified task.
    # We will simulate a token by returning the username/email.
    return to_encode["sub"] # For simplicity, returning the user identifier directly

# --- Dependencies ---

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    # In this simplified example, the 'token' is directly the user's email or identifier.
    # In a real app, you would decode the JWT here.
    user = await get_user_by_email(token) # Treat token directly as email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    # No specific "inactive" state in our models, so it just returns the user.
    return current_user

# --- Prisma Lifecycle Management ---
@app.on_event("startup")
async def startup():
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()

# --- API Endpoints ---

@app.get("/health", summary="Health check endpoint", tags=["Utility"])
async def health_check():
    """
    Checks the health of the API.
    """
    return {"status": "ok", "message": "API is running"}

@app.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def register_user(user: UserRegister):
    """
    Registers a new user in the system.
    """
    db_user = await get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    created_user = await create_user(user_in_db)
    # The `id` field is set by the database, so we don't need to generate it here.
    return UserOut(id=created_user.id, username=created_user.username, email=created_user.email)


@app.post("/users/login", response_model=Token, tags=["Users"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns an access token.
    """
    user = await get_user_by_email(form_data.username)  # Using username field for email
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks/", response_model=TaskOut, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_new_task(
    task: TaskCreate, current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Creates a new task for the authenticated user.
    """
    task_in_db = TaskInDB(
        title=task.title,
        description=task.description,
        owner_id=current_user.id, # current_user.id is a UUID
        completed=False,
    )
    created_task = await create_task(task_in_db)
    return TaskOut(
        id=created_task.id,
        title=created_task.title,
        description=created_task.description,
        completed=created_task.completed,
        owner_id=created_task.owner_id,
    )


@app.get("/tasks/", response_model=List[TaskOut], tags=["Tasks"])
async def read_tasks(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Retrieves all tasks for the authenticated user.
    """
    tasks = await get_tasks_by_user_id(str(current_user.id)) # Prisma expects string ID for filtering
    return [
        TaskOut(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            owner_id=task.owner_id,
        )
        for task in tasks
    ]
