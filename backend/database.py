from prisma import Prisma
from backend.models import UserInDB, TaskInDB # Keep these for type hinting and return types
from uuid import UUID

# Initialize Prisma client globally.
# The actual connection/disconnection will be handled by FastAPI startup/shutdown events.
prisma = Prisma()

async def create_user(user: UserInDB) -> UserInDB:
    """Creates a new user in the database."""
    created_user = await prisma.user.create(
        data={
            "email": user.email,
            "name": user.username,  # Map UserInDB.username to Prisma User.name
            "password": user.hashed_password,
        }
    )
    # Reconstruct UserInDB from Prisma model
    return UserInDB(
        id=UUID(created_user.id), # Attempt to convert Prisma string ID to UUID
        username=created_user.name, # Map Prisma User.name back to UserInDB.username
        email=created_user.email,
        hashed_password=created_user.password,
    )

async def get_user_by_email(email: str) -> UserInDB | None:
    """Retrieves a user by email from the database."""
    user = await prisma.user.find_first(where={"email": email})
    if user:
        return UserInDB(
            id=UUID(user.id), # Attempt to convert Prisma string ID to UUID
            username=user.name, # Map Prisma User.name back to UserInDB.username
            email=user.email,
            hashed_password=user.password,
        )
    return None

async def get_user_by_id(user_id: str) -> UserInDB | None:
    """Retrieves a user by ID from the database."""
    user = await prisma.user.find_unique(where={"id": user_id})
    if user:
        return UserInDB(
            id=UUID(user.id), # Attempt to convert Prisma string ID to UUID
            username=user.name, # Map Prisma User.name back to UserInDB.username
            email=user.email,
            hashed_password=user.password,
        )
    return None

async def create_task(task: TaskInDB) -> TaskInDB:
    """Creates a new task in the database."""
    created_task = await prisma.task.create(
        data={
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "userId": str(task.owner_id), # Prisma expects string for userId
        }
    )
    # Reconstruct TaskInDB from Prisma model
    return TaskInDB(
        id=UUID(created_task.id), # Attempt to convert Prisma string ID to UUID
        title=created_task.title,
        description=created_task.description,
        completed=created_task.completed,
        owner_id=UUID(created_task.userId), # Attempt to convert Prisma string userId to UUID
    )

async def get_tasks_by_user_id(user_id: str) -> list[TaskInDB]:
    """Retrieves tasks for a given user ID from the database."""
    tasks = await prisma.task.find_many(where={"userId": user_id})
    return [
        TaskInDB(
            id=UUID(task.id), # Attempt to convert Prisma string ID to UUID
            title=task.title,
            description=task.description,
            completed=task.completed,
            owner_id=UUID(task.userId), # Attempt to convert Prisma string userId to UUID
        )
        for task in tasks
    ]
