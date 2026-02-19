from typing import Dict, Optional
from uuid import UUID
from backend.models import UserInDB


# In-memory database simulation
_users_db: Dict[UUID, UserInDB] = {}

def create_user(user: UserInDB) -> UserInDB:
    """Adds a new user to the in-memory database."""
    _users_db[user.id] = user
    return user

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Retrieves a user by email from the in-memory database."""
    for user in _users_db.values():
        if user.email == email:
            return user
    return None

def get_user_by_id(user_id: UUID) -> Optional[UserInDB]:
    """Retrieves a user by ID from the in-memory database."""
    return _users_db.get(user_id)
