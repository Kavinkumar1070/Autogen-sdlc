from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from .models import UserInDB, TaskInDB

# In-memory database simulation
users_db: Dict[UUID, UserInDB] = {}
tasks_db: Dict[UUID, TaskInDB] = {}

def create_user(user: UserInDB) -> UserInDB:
    users_db[user.id] = user
    return user

def get_user_by_email(email: str) -> Optional[UserInDB]:
    for user in users_db.values():
        if user.email == email:
            return user
    return None

def get_user_by_id(user_id: UUID) -> Optional[UserInDB]:
    return users_db.get(user_id)

def create_task(task: TaskInDB) -> TaskInDB:
    tasks_db[task.id] = task
    return task

def get_tasks_by_user_id(user_id: UUID) -> List[TaskInDB]:
    return [task for task in tasks_db.values() if task.user_id == user_id]
