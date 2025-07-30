from enum import Enum
from typing import Optional
from beanie import Document
from pydantic import BaseModel


class UserType(str, Enum):
    FIELD_CLINICIAN = "field_clinician"
    QUALITY_ADMINISTRATOR = "quality_administrator"


class User(Document):
    user_id: int
    username: str
    hashed_password: str
    user_type: UserType
    
    class Settings:
        name = "users"
        indexes = [
            "username",
            "user_id"
        ]


class UserCreate(BaseModel):
    username: str
    password: str
    user_type: UserType


class UserResponse(BaseModel):
    user_id: int
    username: str
    user_type: UserType


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None 