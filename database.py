from typing import List, Dict, Optional
from schemas import User, UserCreate

# Simulate an in-memory database
database: List[User] = []
next_user_id = 1

def get_next_id() -> int:
    global next_user_id
    current_id = next_user_id
    next_user_id += 1
    return current_id

def get_user_by_email(email: str) -> Optional[User]:
    for user in database:
        if user.email == email:
            return user
    return None

def create_user(user: UserCreate) -> User:
    new_user_id = get_next_id()
    new_user = User(id=new_user_id, email=user.email, password=user.password) # Storing password directly for simplicity, not recommended for production
    database.append(new_user)
    return new_user

def get_all_users() -> List[User]:
    return database
